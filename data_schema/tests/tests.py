from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import G

from data_schema.models import DataSchema, FieldSchema, TimeFieldSchema


class DataSchemaTest(TestCase):
    """
    Tests the DataSchema model.
    """
    def test_get_unique_fields_no_fields(self):
        """
        Tests the get_unique_fields function when there are no fields defined.
        """
        data_schema = G(DataSchema)
        self.assertEquals(data_schema.get_unique_fields(), [])

    def test_get_unique_fields_no_unique_fields(self):
        """
        Tests the get_unique_fields function when there are fields defined, but
        none of them have a unique constraint.
        """
        data_schema = G(DataSchema)
        G(FieldSchema, data_schema=data_schema)
        G(FieldSchema, data_schema=data_schema)

        self.assertEquals(data_schema.get_unique_fields(), [])

    def test_get_unique_fields_one(self):
        """
        Tests retrieving one unique field.
        """
        data_schema = G(DataSchema)
        field = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        G(FieldSchema, data_schema=data_schema)

        self.assertEquals(data_schema.get_unique_fields(), [field])

    def test_get_unique_fields_three(self):
        """
        Tests retrieving three unique fields.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        field2 = G(FieldSchema, data_schema=data_schema, uniqueness_order=3)
        field3 = G(FieldSchema, data_schema=data_schema, uniqueness_order=2)
        G(FieldSchema, data_schema=data_schema)

        self.assertEquals(data_schema.get_unique_fields(), [field1, field3, field2])

    def test_optimal_queries_get_unique_fields(self):
        """
        Tests that get_unique_fields incurs no additional queries when caching the
        schema with the model manager.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        field2 = G(FieldSchema, data_schema=data_schema, uniqueness_order=3)
        field3 = G(FieldSchema, data_schema=data_schema, uniqueness_order=2)
        G(FieldSchema, data_schema=data_schema)

        data_schema = DataSchema.objects.get(id=data_schema.id)

        with self.assertNumQueries(0):
            self.assertEquals(data_schema.get_unique_fields(), [field1, field3, field2])

    def test_cached_unique_fields(self):
        """
        Tests that get_unique_fields function caches the unique fields.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        field2 = G(FieldSchema, data_schema=data_schema, uniqueness_order=3)
        field3 = G(FieldSchema, data_schema=data_schema, uniqueness_order=2)
        G(FieldSchema, data_schema=data_schema)

        data_schema = DataSchema.objects.get(id=data_schema.id)

        self.assertFalse(hasattr(data_schema, '_unique_fields'))
        self.assertEquals(data_schema.get_unique_fields(), [field1, field3, field2])
        self.assertTrue(hasattr(data_schema, '_unique_fields'))
        self.assertEquals(data_schema.get_unique_fields(), [field1, field3, field2])

    def test_get_fields_no_fields(self):
        """
        Tests the get_fields function when there are no fields defined.
        """
        data_schema = G(DataSchema)
        self.assertEquals(data_schema.get_fields(), [])

    def test_get_fields_one(self):
        """
        Tests retrieving one field.
        """
        data_schema = G(DataSchema)
        field = G(FieldSchema, data_schema=data_schema)
        G(FieldSchema)

        self.assertEquals(data_schema.get_fields(), [field])

    def test_get_fields_three(self):
        """
        Tests retrieving three fields.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema)
        field2 = G(FieldSchema, data_schema=data_schema)
        field3 = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        G(FieldSchema)

        self.assertEquals(set(data_schema.get_fields()), set([field1, field2, field3]))

    def test_optimal_queries_get_fields(self):
        """
        Tests that get_fields incurs no additional queries when caching the
        schema with the model manager.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema, uniqueness_order=1)
        field2 = G(FieldSchema, data_schema=data_schema, uniqueness_order=3)
        field3 = G(FieldSchema, data_schema=data_schema, uniqueness_order=2)
        G(FieldSchema)

        data_schema = DataSchema.objects.get(id=data_schema.id)

        with self.assertNumQueries(0):
            self.assertEquals(set(data_schema.get_fields()), set([field1, field3, field2]))


class FieldSchemaTest(TestCase):
    """
    Tests functionality in the FieldSchema model.
    """
    def test_set_value_dict(self):
        """
        Tests setting the value of a field when the object is a dictionary.
        """
        field_schema = G(FieldSchema, field_key='field_key')
        obj = {
            'field_key': 'none',
        }
        field_schema.set_value(obj, 'value')
        self.assertEquals(obj, {'field_key': 'value'})

    def test_set_value_obj(self):
        """
        Tests setting the value of an object.
        """
        class Input:
            field_key = 'none'
        field_schema = G(FieldSchema, field_key='field_key')
        obj = Input()
        field_schema.set_value(obj, 'value')
        self.assertEquals(obj.field_key, 'value')

    def test_get_value_dict(self):
        """
        Tests the get_value function with a dictionary as input.
        """
        field_schema = G(FieldSchema, field_key='field_key')
        self.assertEquals(field_schema.get_value({
            'field_key': 'value'
        }), 'value')

    def test_get_value_obj(self):
        """
        Tests the get_value function with an object as input.
        """
        class Input:
            field_key = 'value'

        field_schema = G(FieldSchema, field_key='field_key')
        self.assertEquals(field_schema.get_value(Input()), 'value')


class TimeFieldSchemaTest(TestCase):
    """
    Tests functionality in the TimeFieldSchema model.
    """
    def test_get_value_non_int(self):
        """
        Tests the get_value function with a non integer input.
        """
        field_schema = G(TimeFieldSchema, field_key='field_key')
        value = datetime(2013, 12, 4)
        self.assertEquals(field_schema.get_value({
            'field_key': value
        }), value)

    def test_get_value_int(self):
        """
        Tests the get_value function with a utc timestamp.
        """
        field_schema = G(TimeFieldSchema, field_key='field_key')
        self.assertEquals(field_schema.get_value({
            'field_key': 1396396800
        }), datetime(2014, 4, 2))
