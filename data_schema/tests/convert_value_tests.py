from django.test import SimpleTestCase

from data_schema import FieldSchemaType
from data_schema.convert_value import convert_value


class BooleanConverterTest(SimpleTestCase):

    def test_convert_value_true(self):
        """
        Verifies true string values are True
        """
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 't'))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 'T'))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 'true'))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 'True'))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 'TRUE'))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, True))

    def test_convert_value_false(self):
        """
        Verifies false string values are False
        """
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 'f'))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 'F'))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 'false'))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 'False'))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 'FALSE'))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, False))

    def test_convert_value_empty(self):
        """
        Verifies that any other value returns None
        """
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, None))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, ''))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 'string'))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 5))

    def test_convert_value_default(self):
        """
        Verifies that the default value will be used if the passed value is null
        """
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, None, default_value=True))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 'invalid', default_value=True))
