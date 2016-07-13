from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from manager_utils import ManagerUtilsManager, sync

from data_schema.convert_value import convert_value
from data_schema.field_schema_type import FieldSchemaType


class DataSchemaManager(ManagerUtilsManager):
    """
    A model manager for data schemas. Caches related attributes of data schemas.
    """
    def get_queryset(self):
        return super(DataSchemaManager, self).get_queryset().select_related(
            'model_content_type').prefetch_related('fieldschema_set')


class DataSchema(models.Model):
    """Define a schema information about a unit of data, such as a
    dictionary, list or model.

    ``FieldSchema`` objects are created referencing a ``DataSchema``
    to describe individual fields within the unit of data.
    """
    # The content type of the django model for which this schema is related. If None, this schema is
    # for a dictionary of data.
    model_content_type = models.ForeignKey(ContentType, null=True, default=None)

    # A custom model manager that caches objects
    objects = DataSchemaManager()

    @transaction.atomic
    def update(self, **updates):
        """
        Takes a template of updates and updates the data schema. The following are possible keyword
        arguments.

        'model_content_type': The string path of a model that this schema represents (or None),
        'fieldschema_set': [{
            'field_key': The field key of the field,
            'display_name': The display name for the field (or the 'field_key' by default),
            'field_type': The FieldSchemaType type of the field,
            'uniqueness_order': The order this field is in the uniquessness constraint (or None by default),
            'field_position': The position of this field if it can be parsed by an array (or None by default),
            'field_format': The format of this field (or None by default),
            'default_value': The default value of this field (or None by default),
            'fieldoption_set': The set of options for the field schema (optional),
        }, {
            Additional field schemas...
        }]
        """
        if 'model_content_type' in updates:
            self.model_content_type = updates['model_content_type']

        self.save()

        if 'fieldschema_set' in updates:
            # Sync the field schema models
            sync(self.fieldschema_set.all(), [
                FieldSchema(
                    data_schema=self,
                    field_key=fs_values['field_key'],
                    display_name=fs_values.get('display_name', ''),
                    field_type=fs_values['field_type'],
                    uniqueness_order=fs_values.get('uniqueness_order', None),
                    field_position=fs_values.get('field_position', None),
                    field_format=fs_values.get('field_format', None),
                    default_value=fs_values.get('default_value', None),
                    has_options='fieldoption_set' in fs_values and fs_values['fieldoption_set'],
                    transform_case=fs_values.get('transform_case', None),
                )
                for fs_values in updates['fieldschema_set']
            ], ['field_key'], [
                'display_name', 'field_key', 'field_type', 'uniqueness_order', 'field_position',
                'field_format', 'default_value', 'has_options', 'transform_case'
            ])

            # Sync the options of the field schema models if they are present
            for fs_values in updates['fieldschema_set']:
                if 'fieldoption_set' in fs_values:
                    fs = self.fieldschema_set.get(field_key=fs_values['field_key'])
                    sync(fs.fieldoption_set.all(), [
                        FieldOption(
                            field_schema=fs,
                            value=f_option,
                        )
                        for f_option in fs_values['fieldoption_set']
                    ], ['value'], ['value'])

    def get_unique_fields(self):
        """
        Gets all of the fields that create the uniqueness constraint for a metric record.
        """
        if not hasattr(self, '_unique_fields'):
            # Instead of querying the reverse relationship directly, assume that it has been cached
            # with prefetch_related and go through all fields.
            setattr(self, '_unique_fields', [
                field for field in self.fieldschema_set.all() if field.uniqueness_order is not None
            ])
            self._unique_fields.sort(key=lambda k: k.uniqueness_order or 0)
        return self._unique_fields

    def get_fields(self):
        """
        Gets all fields in the schema. Note - dont use django's order_by since we are caching the fieldschema_set
        beforehand.
        """
        return sorted(self.fieldschema_set.all(), key=lambda k: k.field_position or 0)

    def _get_field_map(self):
        """
        Returns a cached mapping of field keys to their field schemas.
        """
        if not hasattr(self, '_field_map'):
            self._field_map = {
                field.field_key: field for field in self.get_fields()
            }
        return self._field_map

    def get_value(self, obj, field_key):
        """
        Given an object and a field key, return the value of the field in the object.
        """
        try:
            return self._get_field_map()[field_key].get_value(obj)
        except Exception as e:
            # Attach additional information to the exception to make higher level error handling easier
            e.field_key = field_key
            raise e

    def set_value(self, obj, field_key, value):
        """
        Given an object and a field key, set the value of the field in the object.
        """
        return self._get_field_map()[field_key].set_value(obj, value)


class FieldSchema(models.Model):
    """
    Specifies the schema for a field in a piece of data.
    """
    class Meta:
        unique_together = ('data_schema', 'field_key')

    # The data schema to which this field belongs
    data_schema = models.ForeignKey(DataSchema)

    # The key for the field in the data
    field_key = models.CharField(max_length=64)

    # Optional way to display the field. defaults to the field_key
    display_name = models.CharField(max_length=64, blank=True, default='')

    # The order in which this field appears in the UID for the record. It is null if it does
    # not appear in the uniqueness constraint
    uniqueness_order = models.IntegerField(null=True)

    # The position of the field. This ordering is relevant when parsing a list of fields into
    # a dictionary with the field names as keys
    field_position = models.IntegerField(null=True)

    # The type of field. The available choices are present in the FieldSchemaType class
    field_type = models.CharField(max_length=32, choices=FieldSchemaType.choices())

    # If the field is a string and needs to be converted to another type, this string specifies
    # the format for a field
    field_format = models.CharField(null=True, blank=True, default=None, max_length=64)

    # This field provides a default value to be used for the field in the case that it is None.
    default_value = models.CharField(null=True, blank=True, default=None, max_length=128)

    # Flag to indicate if setting values should be validated against an option list
    has_options = models.BooleanField(default=False)

    # Only applies to string data types. Valid options are upper and lower
    transform_case = models.CharField(null=True, default=None, blank=True, max_length=5)

    # Use django manager utils to manage FieldSchema objects
    objects = ManagerUtilsManager()

    def set_value(self, obj, value):
        """
        Given an object, set the value of the field in that object.
        """
        if self.has_options:
            # Build a set of possible values by calling self.get_value on the stored value options. This will
            # make sure they are the right data type because they are stored as strings
            values = set(
                self.get_value({
                    self.field_key: field_option.value
                })
                for field_option in self.fieldoption_set.all()
            )
            if value not in values:
                raise Exception('Invalid option for {0}'.format(self.field_key))

        if isinstance(obj, list):
            obj[self.field_position] = value
        elif isinstance(obj, dict):
            obj[self.field_key] = value
        else:
            setattr(obj, self.field_key, value)

    def get_value(self, obj):
        """
        Given an object, return the value of the field in that object.
        """
        if isinstance(obj, list):
            value = obj[self.field_position] if 0 <= self.field_position < len(obj) else None
        elif isinstance(obj, dict):
            value = obj[self.field_key] if self.field_key in obj else None
        else:
            value = getattr(obj, self.field_key) if hasattr(obj, self.field_key) else None

        return convert_value(self.field_type, value, self.field_format, self.default_value, self.transform_case)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.field_key
        super(FieldSchema, self).save(*args, **kwargs)


class FieldOption(models.Model):
    """
    Specifies a set of possible values that a field schema can have
    """
    field_schema = models.ForeignKey(FieldSchema)
    value = models.CharField(max_length=1024)

    class Meta:
        unique_together = ('field_schema', 'value')
