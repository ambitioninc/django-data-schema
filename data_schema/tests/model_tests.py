from django.test import TestCase
from django_dynamic_fixture import G

from data_schema.models import FieldSchema, DataSchema


class FieldSchemaTest(TestCase):

    def test_unicode(self):
        field = FieldSchema(field_key='key', display_name='Field', id=10)

        self.assertEqual(str(field), u'10 - key - Field')

    def test_display_name_no_character_limit(self):
        data_schema = G(DataSchema)
        field_schema = FieldSchema(
            data_schema=data_schema,
            field_key='testing_id',
            display_name='Testing this is longer than 64 characters and we are no longer failing')

        field_schema.save()

        self.assertEqual(
            field_schema.display_name,
            'Testing this is longer than 64 characters and we are no longer failing'
        )
