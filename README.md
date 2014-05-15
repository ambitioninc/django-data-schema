[![Build Status](https://travis-ci.org/ambitioninc/django-data-schema.png)](https://travis-ci.org/ambitioninc/django-data-schema)

Django Data Schema
==================
Django data schema is a lightweight Django app for defining the schema for a model, dictionary, or list.
By describing a schema on a piece of data, this allows other applications to easily reference
fields of models or fields in dictionaries (or their related json fields).

# Basic Usage
Django data schema defines three models for building schemas on data. These models are ``DataSchema`` and
``FieldSchema``.

The ``DataSchema`` model provides a ``model_content_type`` field that points to a Django ``ContentType`` model.
This field represents which object this schema is modeling. If the field is left Null, it is assumed that
this schema models a dictionary.

After the enclosing ``DataSchema`` has been defined, various ``FieldSchema`` models can reference the main
data schema. ``FieldSchema`` models provide the ability to define the name of the field (the ``field_key`` attribute)
and if the field is part of the uniqueness constraint of the data schema. If the field is part of the
uniqueness constraint of the data, the user must provide an integrer in the ``uniqueness_order`` field that indicates
what order this field is in the uniqueness constraint. If the user wishes to parse fields of a python ``list``, a
``field_position`` attribute must also be provided in the ``FieldSchema`` model.

Along with these options, a ``FieldSchema`` object must specify its data type, which can be any of the types in the
``FieldSchemaType`` class. These types are as follows:

- FieldSchemaType.DATE: A python ``date`` object from the ``datetime`` module.
- FieldSchemaType.DATETIME: A python ``datetime`` object from the ``datetime`` module.
- FieldSchemaType.INT: A python ``int``.
- FieldSchemaType.FLOAT: A python ``float``.
- FieldSchemaType.STRING: A python ``str``.

Note that these fields provide the necessary conversion mechanisms when accessing data via ``FieldSchema.get_value``.
Along with providing the type of field being accessed, a ``field_format`` parameter can be specified as a format
string for parsing string values into their associated types. Datetime objects, for example, will pass this
format string to the ``strptime`` function automatically.

# Examples

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
constraint of the data. The uniquess constraint can then easily be accessed by simply doing the following.

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


Note that ``FieldSchema`` objects have an analogous ``set_value`` function for setting the value of a field.
