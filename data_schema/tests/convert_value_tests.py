from django.test import SimpleTestCase

from data_schema import FieldSchemaType
from data_schema.convert_value import BooleanConverter


class BooleanConverterTest(SimpleTestCase):

    def test_convert_value_true(self):
        """
        Verifies true string values are True
        """
        converter = BooleanConverter(FieldSchemaType.BOOLEAN, bool)
        self.assertTrue(converter._convert_value('t', None))
        self.assertTrue(converter._convert_value('T', None))
        self.assertTrue(converter._convert_value('true', None))
        self.assertTrue(converter._convert_value('True', None))
        self.assertTrue(converter._convert_value('TRUE', None))
        self.assertTrue(converter._convert_value(True, None))

    def test_convert_value_false(self):
        """
        Verifies false string values are False
        """
        converter = BooleanConverter(FieldSchemaType.BOOLEAN, bool)
        self.assertFalse(converter._convert_value('f', None))
        self.assertFalse(converter._convert_value('F', None))
        self.assertFalse(converter._convert_value('false', None))
        self.assertFalse(converter._convert_value('False', None))
        self.assertFalse(converter._convert_value('FALSE', None))
        self.assertFalse(converter._convert_value(False, None))

    def test_convert_value_empty(self):
        """
        Verifies that any other value returns None
        """
        converter = BooleanConverter(FieldSchemaType.BOOLEAN, bool)
        self.assertIsNone(converter._convert_value(None, None))
        self.assertIsNone(converter._convert_value('', None))
        self.assertIsNone(converter._convert_value('string', None))
        self.assertIsNone(converter._convert_value(5, None))
