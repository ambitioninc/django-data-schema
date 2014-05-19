"""
Functions for handling conversions of values from one type to another.
"""
from datetime import datetime
import re

from dateutil.parser import parse
import fleming
import pytz

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


def is_string(value):
    """
    Returns True if the value is a string.
    """
    return isinstance(value, (str, unicode))


def is_numeric(value):
    """
    Returns True if the value is numeric.
    """
    return isinstance(value, (int, float, long, complex))


def convert_value_numeric(field_schema_type, value):
    """
    Converts a numeric value into its python type.
    """
    if is_string(value):
        # Strip out any non-numeric characters if it is a string.
        value = NON_NUMERIC_REGEX.sub('', value) or None

    return FIELD_SCHEMA_PYTHON_TYPES[field_schema_type](value) if value is not None else None


def convert_value_datetime_type(field_schema_type, value, format_str=None):
    """
    Converts a value into a date or datetime object. The format parameter is passed to strptime if provided.
    If the value is an integer or float, it assumes it is a UTC timestamp
    """
    dt = None

    if is_numeric(value):
        dt = datetime.utcfromtimestamp(value)
    elif is_string(value):
        if value:
            if format_str:
                dt = datetime.strptime(value, format_str)
            else:
                dt = parse(value)
    else:
        dt = value

    # Convert any aware datetime objects to naive utc
    if dt is not None and dt.tzinfo is not None:
        return fleming.convert_to_tz(dt, pytz.utc, return_naive=True)
    else:
        return dt


def convert_value_string_type(field_schema_type, value, format_str=None):
    """
    Converts a value to a string object.
    """
    if is_string(value):
        if format_str:
            value = value if re.match(format_str, value) else None

    return str(value) if value is not None else None


def convert_value(field_schema_type, value, format_str=None):
    """
    Converts a value to a type with an optional format string.
    """
    if is_string(value):
        # Strip any strings
        value = value.strip()

    if field_schema_type in (FieldSchemaType.DATETIME, FieldSchemaType.DATE):
        return convert_value_datetime_type(field_schema_type, value, format_str)
    elif field_schema_type in (FieldSchemaType.INT, FieldSchemaType.FLOAT):
        return convert_value_numeric(field_schema_type, value)
    else:
        return convert_value_string_type(field_schema_type, value, format_str)
