"""
Functions for handling conversions of values from one type to another.
"""
from datetime import datetime, date


def convert_value_python_type(python_type, value, format=None):
    """
    A generic function for converting the value into a python type.

    For example:
        val = convert_value_generic(int, "0", None)
        print val
        0
    """
    if not format:
        return python_type(value)
    else:
        # TODO support format strings for integers and other types using the parse library
        # (https://github.com/r1chardj0n3s/parse)
        raise NotImplementedError('Format string not applicable to field schema type')


def convert_value_datetime_type(datetime_type, value, format=None):
    """
    Converts a value into a date or datetime object. The format parameter is passed to strptime if provided.
    If the value is an integer or float, it assumes it is a UTC timestamp
    """
    if isinstance(value, datetime_type):
        # The value is already the appropriate type
        return value

    if isinstance(value, int) or isinstance(value, float):
        # Return a timestamp if the value is an integer or float
        value = datetime.utcfromtimestamp(value)
    elif format:
        # If there is a format specified, assume the value is a string
        value = datetime.strptime(value, format)
    else:
        # If there is no format specifi
        raise NotImplementedError('Unsupported input value for datetime conversion: {0}'.format(value))

    # Convert it to a date object if necessary. Otherwise it should already be a datetime object
    return value.date() if datetime_type is date else value


def convert_value(value_type, value, format=None):
    """
    Converts a value to a type with an optional format string.
    """
    if value_type in (datetime, date):
        return convert_value_datetime_type(value_type, value, format)
    else:
        return convert_value_python_type(value_type, value, format)
