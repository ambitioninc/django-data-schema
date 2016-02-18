from datetime import datetime

from django.test import SimpleTestCase

from data_schema.models import FieldSchemaType
from data_schema.convert_value import convert_value


class ConvertValueExceptionTest(SimpleTestCase):
    def test_get_value_exception(self):
        """
        Tests that when we fail to parse a value, we get a ValueError with additional information attached.
        """
        bad_value = '-'

        with self.assertRaises(ValueError) as ctx:
            convert_value(FieldSchemaType.INT, bad_value)

        self.assertEquals(bad_value, ctx.exception.bad_value)
        self.assertEquals(FieldSchemaType.INT, ctx.exception.expected_type)


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
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, 1))
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, '1'))

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
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, 0))
        self.assertFalse(convert_value(FieldSchemaType.BOOLEAN, '0'))

    def test_convert_value_empty(self):
        """
        Verifies that any other value returns None
        """
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, None))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, ''))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 'string'))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 5))

    def test_convert_datetime(self):
        """
        Verifies that datetime field type attempts to coerce to timestamp before
        attempting to parse the string as a date string
        """
        # still
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, 1447251508), datetime)
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, 1447251508.1234), datetime)
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, 1.447251508e9), datetime)
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, '1447251508'), datetime)
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, '1447251508.1234'), datetime)
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, '1.447251508e9'), datetime)
        # parses date strings
        self.assertIsInstance(convert_value(FieldSchemaType.DATETIME, '2015-11-09 15:30:00'), datetime)

    def test_convert_value_default(self):
        """
        Verifies that the default value will be used if the passed value is null
        """
        self.assertTrue(convert_value(FieldSchemaType.BOOLEAN, None, default_value=True))
        self.assertIsNone(convert_value(FieldSchemaType.BOOLEAN, 'invalid', default_value=True))
