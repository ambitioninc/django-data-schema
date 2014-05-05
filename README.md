[![Build Status](https://travis-ci.org/ambitioninc/django-data-schema.png)](https://travis-ci.org/ambitioninc/django-data-schema)

Django Data Schema
==================
Django data schema is a lightweight Django app for defining the schema for a model or dictionary.
By describing a schema on a piece of data, this allows other applications to easily reference
fields of models or fields in dictionaries (or their related json fields).

# Basic Usage
Django data schema defines three models for building schemas on data. These models are ``DataSchema``,
``FieldSchema``, and ``TimeFieldSchema``.

The ``DataSchema`` model provides a ``model_content_type`` field that points to a Django ``ContentType`` model.
This field represents which object this schema is modeling. If the field is left Null, it is assumed that
this schema models a dictionary.

After the enclosing ``DataSchema`` has been defined, various ``FieldSchema`` models can reference the main
data schema. ``FieldSchema`` models provide the ability to define the name of the field (the ``field_key`` attribute)
and if the field is part of the uniqueness constraint of the data schema. If the field is part of the
uniqueness constraint of the data, the user must provide an integrer in the ``uniqueness_order`` field that indicates
what order this field is in the uniqueness constraint.

A data schema can be created like the following:

```python
from data_schema import DataSchema, FieldSchema

user_login_schema = DataSchema.objects.create()
user_id_field = FieldSchema.objects.create(data_schema=user_login_schema, field_key='user_id', uniqueness_order=1)
login_time_field = FieldSchema.objects.create(data_schema=user_login_schema, field_key='login_time')
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
1396396800
```

Django data schema defines a special field for time variables, called ``TimeFieldSchema``. This model overrides the
``get_value`` function and will parse integer time stamps into Python datetime objects. For example.

```python
from data_schema import TimeFieldSchema

data = {
    'user_id': 'my_user_id',
    'login_time': 1396396800,
}

new_login_time_field = TimeFieldSchema.objects.create(data_schema=user_login_schema, field_key='login_time')
print new_login_time_field.get_value(data)
2014-04-02 00:00:00
```

Note that ``FieldSchema`` and ``TimeFieldSchema`` objects have an analogous ``set_value`` function for setting the value of a field.
