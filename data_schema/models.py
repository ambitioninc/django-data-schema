from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import models
from manager_utils import ManagerUtilsManager


class DataSchemaManager(ManagerUtilsManager):
    """
    A model manager for data schemas. Caches related attributes of data schemas.
    """
    def get_queryset(self):
        return super(DataSchemaManager, self).get_queryset().select_related(
            'model_content_type').prefetch_related('fieldschema_set')


class DataSchema(models.Model):
    """
    A configuration for a metric record that is tracked by animal. Specifies the main options and
    allows MetricRecordFieldConfigs to be attached to it, which specify the schema of the metric
    record. Also defines a unique name for the metric record and a display name.
    """
    # The content type of the django model for which this schema is related. If None, this schema is
    # for a dictionary of data.
    model_content_type = models.ForeignKey(ContentType, null=True, default=None)

    # A custom model manager that caches objects
    objects = DataSchemaManager()

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
            self._unique_fields.sort(key=lambda k: k.uniqueness_order)
        return self._unique_fields

    def get_fields(self):
        """
        Gets all fields in the schema.
        """
        return list(self.fieldschema_set.all())


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

    # The order in which this field appears in the UID for the record. It is null if it does
    # not appear in the uniqueness constraint
    uniqueness_order = models.PositiveIntegerField(null=True)

    # Use django manager utils to manage FieldSchema objects
    objects = ManagerUtilsManager()

    def get_value(self, obj):
        """
        Given an object, return the value of the field in that object.
        """
        if type(obj) is dict:
            return obj[self.field_key]
        else:
            return getattr(obj, self.field_key)


class TimeFieldSchema(FieldSchema):
    """
    A model that performs additional datetime parsing when obtaining the value of a time field.
    """
    # Use django manager utils to manage TimeFieldSchema objects
    objects = ManagerUtilsManager()

    def get_value(self, obj):
        """
        If an integer time stamp is stored in the time field, convert it into a datetime object.
        NOTE - we can add time formatting strings here later when supporing parsing of string times.
        """
        value = super(TimeFieldSchema, self).get_value(obj)

        if type(value) is int:
            # Convert a time stamp to a datetime object.
            value = datetime.utcfromtimestamp(value)

        return value
