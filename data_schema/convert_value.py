"""
Functions for handling conversions of values from one type to another.
"""
from datetime import datetime
import re
import six

from dateutil.parser import parse
import fleming
import pytz

from data_schema.field_schema_type import FieldSchemaType, FieldSchemaCase


class ValueConverter(object):
    """
    A generic value converter.
    """
    NUMBER_TYPES = (float, complex) + six.integer_types

    def __init__(self, field_schema_type, python_type):
        # Set the FieldSchemaType value
        self._field_schema_type = field_schema_type

        # Set the python type to convert the value to
        self._python_type = python_type

    def is_string(self, value):
        """
        Returns True if the value is a string.
        """
        return isinstance(value, six.string_types)

    def is_numeric(self, value):
        """
        Returns True if the value is numeric.
        """
        return isinstance(value, self.NUMBER_TYPES)

    def _preprocess_value(self, value, format_str, transform_case=None):
        """
        Preprocesses the value depending on the field schema type.
        """
        # Strip all strings by default
        if self.is_string(value):
            value = value.strip()

            # Convert blank strings to None if the schema type isn't a string
            if self._field_schema_type != FieldSchemaType.STRING and not value:
                value = None

        return value

    def _convert_value(self, value, format_str):
        """
        Converts the value into the format of the field schema type.
        """
        try:
            return self._python_type(value)
        except Exception as e:
            # Attach additional information to the exception to make higher level error handling easier
            e.bad_value = value
            e.expected_type = self._field_schema_type
            raise e

    def __call__(self, value, format_str, default_value, transform_case=None):
        """
        Converts a provided value to the configured python type.
        """
        value = self._preprocess_value(value, format_str, transform_case=transform_case)

        # Set the value to the default if it is None and there is a default
        value = default_value if value is None and default_value is not None else value

        # Convert the value if it isn't None
        return self._convert_value(value, format_str) if value is not None else None


class BooleanConverter(ValueConverter):
    """
    Converts strings to a boolean value or None
    """
    TRUE_VALUES = frozenset(('t', 'T', 'true', 'True', 'TRUE', True, 1, '1',))
    FALSE_VALUES = frozenset(('f', 'F', 'false', 'False', 'FALSE', False, 0, '0',))

    def _convert_value(self, value, format_str):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        return None


class NumericConverter(ValueConverter):
    """
    Converts numeric values (floats and ints).
    """
    # A compiled regex for extracting non-numeric characters
    NON_NUMERIC_REGEX = re.compile(r'[^\d\.\-\e\E]+')

    def _preprocess_value(self, value, format_str, transform_case=None):
        """
        Strips out any non-numeric characters for numeric values if they are a string.
        """
        value = super(NumericConverter, self)._preprocess_value(value, format_str, transform_case=transform_case)
        if self.is_string(value):
            value = self.NON_NUMERIC_REGEX.sub('', value) or None

        return value


class DurationConverter(ValueConverter):
    """
    Converts durations from [hh]:mm:ss format to integer number of seconds
    """
    TIME_FORMAT_DURATION_REGEXP = re.compile(r'^\d{1,2}:\d{1,2}(:\d{1,2})?$')

    def __call__(self, value, format_str, default_value, transform_case=None):
        if self.is_string(value) and self.TIME_FORMAT_DURATION_REGEXP.match(value) is not None:
            return super(DurationConverter, self).__call__(value, format_str, default_value, transform_case)
        return NumericConverter(FieldSchemaType.INT, int)(value, format_str, default_value, transform_case)

    def _convert_value(self, value, format_str):
        duration_constituents = value.split(':')
        value = int(duration_constituents[-2]) * 60 + int(duration_constituents[-1])
        if len(duration_constituents) == 3:
            value += int(duration_constituents[0]) * 3600
        return value


class DatetimeConverter(ValueConverter):
    """
    Converts datetime values (date and datetime).
    """
    def _convert_value(self, value, format_str):
        """
        Formats datetimes based on the input type. If the input is a string, uses strptime and the
        format string specified or dateutil.parse if no format is specified. If the input is numeric,
        it assumes it is a unix timestamp. This function also takes care of converting any
        aware datetimes to naive UTC.
        """
        try:
            value = datetime.utcfromtimestamp(float(value))
        except Exception:
            pass
        if self.is_string(value):
            value = datetime.strptime(value, format_str) if format_str else parse(value)

        # Convert any aware datetime objects to naive utc
        return value if value.tzinfo is None else fleming.convert_to_tz(value, pytz.utc, return_naive=True)


class StringConverter(ValueConverter):
    """
    Converts string values.
    """
    def _preprocess_value(self, value, format_str, transform_case=None):
        """
        Performs additional regex matching for any provided format string. If the value
        does not match the format string, None is returned.
        """
        value = super(StringConverter, self)._preprocess_value(value, format_str, transform_case=transform_case)
        if self.is_string(value) and format_str:
            value = value if re.match(format_str, value) else None

        if value and transform_case:
            if transform_case == FieldSchemaCase.LOWER:
                value = value.lower()
            else:
                value = value.upper()

        return value


# Create a mapping of the field schema types to their associated converters
FIELD_SCHEMA_CONVERTERS = {
    FieldSchemaType.DATE: DatetimeConverter(FieldSchemaType.DATE, datetime),
    FieldSchemaType.DATETIME: DatetimeConverter(FieldSchemaType.DATETIME, datetime),
    FieldSchemaType.INT: NumericConverter(FieldSchemaType.INT, int),
    FieldSchemaType.FLOAT: NumericConverter(FieldSchemaType.FLOAT, float),
    FieldSchemaType.STRING: StringConverter(FieldSchemaType.STRING, six.text_type),
    FieldSchemaType.BOOLEAN: BooleanConverter(FieldSchemaType.BOOLEAN, bool),
    FieldSchemaType.DURATION: DurationConverter(FieldSchemaType.DURATION, int),
}


def convert_value(field_schema_type, value, format_str=None, default_value=None, transform_case=None):
    """
    Converts a value to a type with an optional format string.
    """
    return FIELD_SCHEMA_CONVERTERS[field_schema_type](value, format_str, default_value, transform_case)
