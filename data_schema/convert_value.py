"""
Functions for handling conversions of values from one type to another.
"""
from datetime import datetime
import re

from dateutil.parser import parse
import fleming
import pytz

from data_schema.field_schema_type import FieldSchemaType


class ValueConverter(object):
    """
    A generic value converter.
    """
    def __init__(self, field_schema_type, python_type):
        # Set the FieldSchemaType value
        self._field_schema_type = field_schema_type

        # Set the python type to convert the value to
        self._python_type = python_type

    def is_string(self, value):
        """
        Returns True if the value is a string.
        """
        return isinstance(value, (str, unicode))

    def is_numeric(self, value):
        """
        Returns True if the value is numeric.
        """
        return isinstance(value, (int, float, long, complex))

    def _preprocess_value(self, value, format_str):
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
        return self._python_type(value)

    def __call__(self, value, format_str, default_value):
        """
        Converts a provided value to the configured python type.
        """
        value = self._preprocess_value(value, format_str)

        # Set the value to the default if it is None and there is a default
        value = default_value if value is None and default_value is not None else value

        # Convert the value if it isn't None
        return self._convert_value(value, format_str) if value is not None else None


class NumericConverter(ValueConverter):
    """
    Converts numeric values (floats and ints).
    """
    # A compiled regex for extracting non-numeric characters
    NON_NUMERIC_REGEX = re.compile(r'[^\d\.\-]+')

    def _preprocess_value(self, value, format_str):
        """
        Strips out any non-numeric characters for numeric values if they are a string.
        """
        value = super(NumericConverter, self)._preprocess_value(value, format_str)
        if self.is_string(value):
            value = self.NON_NUMERIC_REGEX.sub('', value) or None

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
        if self.is_numeric(value):
            value = datetime.utcfromtimestamp(value)
        elif self.is_string(value):
            value = datetime.strptime(value, format_str) if format_str else parse(value)

        # Convert any aware datetime objects to naive utc
        return value if value.tzinfo is None else fleming.convert_to_tz(value, pytz.utc, return_naive=True)


class StringConverter(ValueConverter):
    """
    Converts string values.
    """
    def _preprocess_value(self, value, format_str):
        """
        Performs additional regex matching for any provided format string. If the value
        does not match the format string, None is returned.
        """
        value = super(StringConverter, self)._preprocess_value(value, format_str)
        if self.is_string(value) and format_str:
            value = value if re.match(format_str, value) else None

        return value


# Create a mapping of the field schema types to their associated converters
FIELD_SCHEMA_CONVERTERS = {
    FieldSchemaType.DATE: DatetimeConverter(FieldSchemaType.DATE, datetime),
    FieldSchemaType.DATETIME: DatetimeConverter(FieldSchemaType.DATETIME, datetime),
    FieldSchemaType.INT: NumericConverter(FieldSchemaType.INT, int),
    FieldSchemaType.FLOAT: NumericConverter(FieldSchemaType.FLOAT, float),
    FieldSchemaType.STRING: StringConverter(FieldSchemaType.STRING, str),
    FieldSchemaType.BOOLEAN: ValueConverter(FieldSchemaType.BOOLEAN, bool),
}


def convert_value(field_schema_type, value, format_str=None, default_value=None):
    """
    Converts a value to a type with an optional format string.
    """
    return FIELD_SCHEMA_CONVERTERS[field_schema_type](value, format_str, default_value)
