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

# A compiled regex for extracting non-numeric characters
NON_NUMERIC_REGEX = re.compile(r'[^\d\.]+')


def convert_value_numeric(field_schema_type, value):
    """
    Converts a numeric value into its python type.
    """
    if isinstance(value, str):
        # Strip out any non-numeric characters if it is a string.
        value = NON_NUMERIC_REGEX.sub('', value) or None

    return FIELD_SCHEMA_PYTHON_TYPES[field_schema_type](value) if value is not None else None


def convert_value_datetime_type(field_schema_type, value, format_str=None):
    """
    Converts a value into a date or datetime object. The format parameter is passed to strptime if provided.
    If the value is an integer or float, it assumes it is a UTC timestamp
    """
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    elif isinstance(value, str):
        value = value.strip()
        return datetime.strptime(value, format_str or '%s') if value else None
    else:
        return value


def convert_value_string_type(field_schema_type, value, format_str=None):
    """
    Converts a value to a string object.
    """
    if isinstance(value, str):
        value = value.strip()
        if format_str:
            print format_str, value, re.match(format_str, value)
            value = value if re.match(format_str, value) else None

    return FIELD_SCHEMA_PYTHON_TYPES[field_schema_type](value) if value is not None else None


def convert_value(field_schema_type, value, format_str=None):
    """
    Converts a value to a type with an optional format string.
    """
    if field_schema_type in (FieldSchemaType.DATETIME, FieldSchemaType.DATE):
        return convert_value_datetime_type(field_schema_type, value, format_str)
    elif field_schema_type in (FieldSchemaType.INT, FieldSchemaType.FLOAT):
        return convert_value_numeric(field_schema_type, value)
    else:
        return convert_value_string_type(field_schema_type, value, format_str)
