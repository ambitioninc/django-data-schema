# flake8: noqa
from .version import __version__
from .models import DataSchema, FieldSchema, FieldSchemaType

django_app_config = 'data_schema.apps.DataSchemaConfig'