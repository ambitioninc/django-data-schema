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


def convert_value_python_type(field_schema_type, value):
    """
    A generic function for converting the value into a python type.

    For example:
        val = convert_value_generic(int, "0", None)
        print val
        0
    """
    python_type = FIELD_SCHEMA_PYTHON_TYPES[field_schema_type]

    return python_type(value)


def convert_value_numeric(field_schema_type, value):
    """
    Converts a numeric value into its python type.
    """
    if isinstance(value, str):
        # Strip out any non-numeric characters if it is a string.
        value = NUMERIC_REGEX.sub('', value)

        # Return None if its an empty string
        if not value:
            return None

    return convert_value_python_type(field_schema_type, value)


def convert_value_datetime_type(field_schema_type, value, format_str=None):
    """
    Converts a value into a date or datetime object. The format parameter is passed to strptime if provided.
    If the value is an integer or float, it assumes it is a UTC timestamp
    """
    if isinstance(value, (int, float)):
        # Return a timestamp if the value is an integer or float
        return datetime.utcfromtimestamp(value)
    elif isinstance(value, str):
        # Return None for empty values, or format the time string
        return datetime.strptime(value, format_str or '%s') if value else None
    else:
        # The value can't be converted or it's in its proper datetime type already
        return value


def convert_value(field_schema_type, value, format_str=None):
    """
    Converts a value to a type with an optional format string.
    """
    if isinstance(value, str):
        # Strip all strings of traling and leading whitespace
        value = value.strip()
    elif value is None:
        # Return None if the value is None
        return None

    if field_schema_type in (FieldSchemaType.DATETIME, FieldSchemaType.DATE):
        return convert_value_datetime_type(field_schema_type, value, format_str)
    elif field_schema_type in (FieldSchemaType.INT, FieldSchemaType.FLOAT):
        return convert_value_numeric(field_schema_type, value)
    else:
        return convert_value_python_type(field_schema_type, value)
