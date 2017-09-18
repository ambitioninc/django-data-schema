from django.test import TestCase

from data_schema.models import FieldSchema


class FieldSchemaTest(TestCase):

    def test_unicode(self):
        field = FieldSchema(field_key='key', display_name='Field', id=10)

        self.assertEqual(str(field), u'10 - key - Field')
