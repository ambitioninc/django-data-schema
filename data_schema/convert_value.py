"""
Functions for handling conversions of values from one type to another.
"""
from datetime import datetime
import re

from data_schema.field_schema_type import FieldSchemaType


# Create a mapping of the field schema types to their associated python types
FIELD_SCHEMA_PYTHON_TYPES = {
    FieldSchemaType.DATE: datetime,
    FieldSchemaType.DATETIME: datetime,
    FieldSchemaType.INT: int,
    FieldSchemaType.FLOAT: float,
    FieldSchemaType.STRING: str,
}

# A compiled regex for extracting numeric characters
NUMERIC_REGEX = re.compile(r'[^\d.]+')


def convert_value_python_type(field_schema_type, value, format=None):
    """
    A generic function for converting the value into a python type.

    For example:
        val = convert_value_generic(int, "0", None)
        print val
        0
    """
    python_type = FIELD_SCHEMA_PYTHON_TYPES[field_schema_type]

    if not format:
        return python_type(value)
    else:
        # TODO support format strings for integers and other types using the parse library
        # (https://github.com/r1chardj0n3s/parse)
        raise NotImplementedError('Format string not applicable to field schema type')


def convert_value_numeric(field_schema_type, value):
    """
    Converts a numeric value into its python type.
    """
    if isinstance(value, str):
        # Strip out any non-numeric characters if it is a string.
        value = NUMERIC_REGEX.sub('', value)

    return convert_value_python_type(field_schema_type, value)


def convert_value_datetime_type(field_schema_type, value, format=None):
    """
    Converts a value into a date or datetime object. The format parameter is passed to strptime if provided.
    If the value is an integer or float, it assumes it is a UTC timestamp
    """
    datetime_type = FIELD_SCHEMA_PYTHON_TYPES[field_schema_type]

    if isinstance(value, datetime_type):
        # The value is already the appropriate type
        return value

    if isinstance(value, int) or isinstance(value, float):
        # Return a timestamp if the value is an integer or float
        return datetime.utcfromtimestamp(value)
    elif format:
        # If there is a format specified, assume the value is a string
        return datetime.strptime(value, format)
    else:
        # If there is no format specifi
        raise NotImplementedError('Unsupported input value for datetime conversion: {0}'.format(value))


def convert_value(field_schema_type, value, format=None):
    """
    Converts a value to a type with an optional format string.
    """
    if field_schema_type in (FieldSchemaType.DATETIME, FieldSchemaType.DATE):
        return convert_value_datetime_type(field_schema_type, value, format)
    elif field_schema_type in (FieldSchemaType.INT, FieldSchemaType.FLOAT):
        return convert_value_numeric(field_schema_type, value)
    else:
        return convert_value_python_type(field_schema_type, value, format)
