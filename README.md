[![Build Status](https://travis-ci.org/ambitioninc/django-data-schema.png)](https://travis-ci.org/ambitioninc/django-data-schema)

# Django Data Schema
Django data schema is a lightweight Django app for defining the schema for a model, dictionary, or list.
By describing a schema on a piece of data, this allows other applications to easily reference
fields of models or fields in dictionaries (or their related json fields).

Django data schema also takes care of all conversions under the hood, such as parsing datetime strings, converting strings to numeric values, using default values when values don't exist, and so on.

1. [Installation](#installation)
2. [Model Overview](#model-overview)
3. [Examples](#examples)

## Installation

```python
pip install django-data-schema
```

## Model Overview
Django data schema defines three models for building schemas on data. These models are ``DataSchema``,
``FieldSchema``, and ``FieldOptional``.

The ``DataSchema`` model provides a ``model_content_type`` field that points to a Django ``ContentType`` model.
This field represents which object this schema is modeling. If the field is None, it is assumed that
this schema models an object such as a dictionary or list.

After the enclosing ``DataSchema`` has been defined, various ``FieldSchema`` models can reference the main
data schema. ``FieldSchema`` models provide the following attributes:

- ``field_key``: The name of the field. Used to identify a field in a dictionary or model.
- ``field_position``: The position of the field. Used to identify a field in a list.
- ``uniqueness_order``: The order of this field in the uniqueness constraint of the schema. Defaults to None.
- ``field_type``: The type of field. More on the field types below.
- ``field_format``: An optional formatting string for the field. Used differently depending on the field type and documented more below.
- ``default_value``: If the field returns None, this default value will be returned instead.

A ``FieldSchema`` object must specify its data type. While data of a given type can be stored in different formats,
django-data-schema normalizes the data when accessing it through ``get_value``, described below. The available
types are listed in the ``FieldSchemaType`` class. These types are listed here, with the type they normalize to:

- ``FieldSchemaType.DATE``: A python ``date`` object from the ``datetime`` module. Currently returned as a ``datetime`` object.
- ``FieldSchemaType.DATETIME``: A python ``datetime`` object from the ``datetime`` module.
- ``FieldSchemaType.INT``: A python ``int``.
- ``FieldSchemaType.FLOAT``: A python ``float``.
- ``FieldSchemaType.STRING``: A python ``str``.
- ``FieldSchemaType.BOOLEAN``: A python ``bool``.

These fields provide the necessary conversion mechanisms when accessing data via ``FieldSchema.get_value``. Differences in how the ``get_value`` function operates are detailed below.

### Using get_value on DATE or DATETIME fields
The ``get_value`` function has the following behavior on DATE and DATETIME fields:

- If called on a Python ``int`` or ``float`` value, the numeric value will be passed to the ``datetime.utcfromtimestamp`` function.
- If called on a ``string`` or ``unicode`` value, the string will be stripped of all trailing and leading whitespace. If the string is empty, the default value (or None) will be used. If the string is not empty, it will be passed to dateutil's ``parse`` function. If the ``field_format`` field is specified on the ``FieldSchema`` object, it will be passed to the ``strptime`` function instead. 
- If called on an aware datetime object (or a string with a timezone), it will be converted to naive UTC time.
- If called on None, the default value (or None) is returned.

### Using get_value on INT or FLOAT fields
The ``get_value`` function has the following behavior on INT and FLOAT fields:

- If called on a ``string`` or ``unicode`` value, the string will be stripped of all non-numeric numbers except for periods. If the string is blank, the default value (or None) will be returned. If not, the string will then be passed to ``int()`` or ``float()``.
- If called on an ``int`` or ``float``, the value will be passed to the ``int()`` or ``float()`` function.
- No other values can be converted. The ``field_format`` parameter is ignored.
- If called on None, the default value (or None) is returned.

### Using get_value on a STRING field
The ``get_value`` function has the following behavior on a STRING field:

- If called on a ``string`` or ``unicode`` value, the string will be stripped of all trailing and leading whitespace. If a ``field_format`` is specified, the string is then be matched to the regex. If it passes, the string is returned. If not, None is returned and the default value is used (or None).
- All other types are passed to the ``str()`` function.
- If called on None, the default value (or None) is returned.

### Using get_value on a BOOLEAN field
The ``get_value`` function has the following behavior on a BOOLEAN field:

- Bool data types will return True or False
- Truthy looking string values return True ('t', 'T', 'true', 'True', 'TRUE', 1, '1')
- Falsy looking string values return False ('f', 'F', 'false', 'False', 'FALSE', 0, '0')
- If called on None, the default value (or None) is returned.

## Examples

A data schema can be created like the following:

```python
from data_schema import DataSchema, FieldSchema, FieldSchemaType

user_login_schema = DataSchema.objects.create()
user_id_field = FieldSchema.objects.create(
    data_schema=user_login_schema, field_key='user_id', uniqueness_order=1, field_type=FieldSchemaType.STRING)
login_time_field = FieldSchema.objects.create(
    data_schema=user_login_schema, field_key='login_time', field_type=FieldSchemaType.DATETIME)
```

The above example represents the schema of a user login. In this schema, the user id field provides the uniqueness
constraint of the data. The uniqueness constraint can then easily be accessed by simply doing the following.

```python
unique_fields = user_login_schema.get_unique_fields()
```

The above function returns the unique fields in the order in which they were specified, allowing the user to
generate a unique ID for the data.

To obtain values of data using the schema, one can use the ``get_value`` function as follows:

```python
data = {
    'user_id': 'my_user_id',
    'login_time': 1396396800,
}

print login_time_field.get_value(data)
2014-04-02 00:00:00
```

Note that the ``get_value`` function looks at the type of data object and uses the proper access method. If the
data object is a ``dict``, it accesses it using ``data[field_key]``. If it is an object, it accesses it with
``getattr(data, field_key)``. An array is accessed as ``data[field_position]``.

Here's another example of parsing datetime objects in an array with a format string.

```python
string_time_field_schema = FieldSchema.objects.create(
    data_schema=data_schema, field_key='time', field_position=1, field_type=FieldSchemaType.DATETIME, field_format='%Y-%m-%d %H:%M:%S')

print string_time_field_schema.get_value(['value', '2013-04-12 12:12:12'])
2013-04-12 12:12:12
```

Note that if you are parsing numerical fields, Django data schema will strip out any non-numerical values, allowing the user to get values of currency-based numbers and other formats.

```python
revenue_field_schema = FieldSchema.objects.create(
    data_schema=data_schema, field_key='revenue', field_type=FieldSchemaType.FLOAT)

print revenue_field_schema.get_value({'revenue': '$15,000,456.23'})
15000456.23
```

Note that ``FieldSchema`` objects have an analogous ``set_value`` method for setting the value of a field.
The ``set_value`` method does not do any data conversions, so when calling this method, be sure to use a value
that is in the correct format.
