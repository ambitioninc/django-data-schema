from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import G
from mock import patch
import pytz

from data_schema.models import DataSchema, FieldSchema, FieldSchemaType


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

    def test_get_fields_with_field_ordering(self):
        """
        Tests that obtaining fields with a field position returns them in the proper
        order.
        """
        data_schema = G(DataSchema)
        field1 = G(FieldSchema, data_schema=data_schema, field_position=2)
        field2 = G(FieldSchema, data_schema=data_schema, field_position=3)
        field3 = G(FieldSchema, data_schema=data_schema, field_position=1)
        G(FieldSchema)

        self.assertEquals(data_schema.get_fields(), [field3, field1, field2])

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

    def test_set_value_list(self):
        """
        Tests setting the value of a list.
        """
        data_schema = G(DataSchema)
        G(FieldSchema, data_schema=data_schema, field_key='field_key', field_position=1)
        val = ['hello', 'worlds']
        data_schema.set_value(val, 'field_key', 'world')
        self.assertEquals(val, ['hello', 'world'])

    def test_set_value_obj(self):
        """
        Tests setting the value of an object.
        """
        class Input:
            field_key = 'none'
        data_schema = G(DataSchema)
        G(FieldSchema, data_schema=data_schema, field_key='field_key')
        obj = Input()
        data_schema.set_value(obj, 'field_key', 'value')
        self.assertEquals(obj.field_key, 'value')

    def test_set_value_dict(self):
        """
        Tests setting the value of a dict.
        """
        data_schema = G(DataSchema)
        G(FieldSchema, data_schema=data_schema, field_key='field_key')
        val = {'field_key': 'value1'}
        data_schema.set_value(val, 'field_key', 'value')
        self.assertEquals(val['field_key'], 'value')

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_dict(self, convert_value_mock):
        """
        Tests getting the value of a field when the object is a dictionary.
        """
        data_schema = G(DataSchema)
        G(FieldSchema, field_key='field_key', field_type=FieldSchemaType.STRING, data_schema=data_schema)
        obj = {
            'field_key': 'value',
        }
        data_schema.get_value(obj, 'field_key')
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'value', None, None)

    def test_get_value_dict_cached(self):
        """
        Tests getting the value of a field twice (i.e. the cache gets used)
        """
        data_schema = G(DataSchema)
        G(FieldSchema, field_key='field_key', data_schema=data_schema, field_type=FieldSchemaType.STRING)
        obj = {
            'field_key': 'none',
        }
        value = data_schema.get_value(obj, 'field_key')
        self.assertEquals(value, 'none')
        value = data_schema.get_value(obj, 'field_key')
        self.assertEquals(value, 'none')

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_obj(self, convert_value_mock):
        """
        Tests the get_value function with an object as input.
        """
        class Input:
            field_key = 'value'

        data_schema = G(DataSchema)
        G(
            FieldSchema, field_key='field_key', field_type=FieldSchemaType.STRING, field_format='format',
            data_schema=data_schema)
        data_schema.get_value(Input(), 'field_key')
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'value', 'format', None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_list(self, convert_value_mock):
        """
        Tests the get_value function with a list as input.
        """
        data_schema = G(DataSchema)
        G(
            FieldSchema, field_key='field_key', field_position=1, field_type=FieldSchemaType.STRING,
            data_schema=data_schema)
        data_schema.get_value(['hello', 'world'], 'field_key')
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'world', None, None)


class FieldSchemaTest(TestCase):
    """
    Tests functionality in the FieldSchema model.
    """
    def test_set_value_list(self):
        """
        Tests setting the value of a list.
        """
        field_schema = G(FieldSchema, field_key='field_key', field_position=1)
        val = ['hello', 'worlds']
        field_schema.set_value(val, 'world')
        self.assertEquals(val, ['hello', 'world'])

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

    def test_set_value_dict(self):
        """
        Tests setting the value of a dict.
        """
        field_schema = G(FieldSchema, field_key='field_key')
        val = {'field_key': 'value1'}
        field_schema.set_value(val, 'value')
        self.assertEquals(val['field_key'], 'value')

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_dict(self, convert_value_mock):
        """
        Tests getting the value of a field when the object is a dictionary.
        """
        field_schema = G(FieldSchema, field_key='field_key', field_type=FieldSchemaType.STRING)
        field_schema.get_value({'field_key': 'hello'})
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'hello', None, None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_obj(self, convert_value_mock):
        """
        Tests the get_value function with an object as input.
        """
        class Input:
            field_key = 'value'

        field_schema = G(FieldSchema, field_key='field_key', field_type=FieldSchemaType.STRING, field_format='format')
        field_schema.get_value(Input())
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'value', 'format', None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_list(self, convert_value_mock):
        """
        Tests the get_value function with a list as input.
        """
        field_schema = G(FieldSchema, field_key='field_key', field_position=1, field_type=FieldSchemaType.STRING)
        field_schema.get_value(['hello', 'world'])
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, 'world', None, None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_dict_non_extant(self, convert_value_mock):
        """
        Tests getting the value of a field when the object is a dictionary and it doesn't exist in the dict.
        """
        field_schema = G(FieldSchema, field_key='field_key_bad', field_type=FieldSchemaType.STRING)
        field_schema.get_value({'field_key': 'hello'})
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, None, None, None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_obj_non_extant(self, convert_value_mock):
        """
        Tests the get_value function with an object as input and the field key is not in the object.
        """
        class Input:
            field_key = 'value'

        field_schema = G(
            FieldSchema, field_key='field_key_bad', field_type=FieldSchemaType.STRING, field_format='format')
        field_schema.get_value(Input())
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, None, 'format', None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_list_non_extant_negative(self, convert_value_mock):
        """
        Tests the get_value function with a list as input and the input position is negative.
        """
        field_schema = G(FieldSchema, field_key='field_key', field_position=-1, field_type=FieldSchemaType.STRING)
        field_schema.get_value(['hello', 'world'])
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, None, None, None)

    @patch('data_schema.models.convert_value', set_spec=True)
    def test_get_value_list_non_extant_out_of_range(self, convert_value_mock):
        """
        Tests the get_value function with a list as input and the input position is greater than the
        length of the list.
        """
        field_schema = G(FieldSchema, field_key='field_key', field_position=2, field_type=FieldSchemaType.STRING)
        field_schema.get_value(['hello', 'world'])
        convert_value_mock.assert_called_once_with(FieldSchemaType.STRING, None, None, None)


class DateFieldSchemaTest(TestCase):
    """
    Tests the DATE type for field schemas.
    """
    def test_no_format_string(self):
        """
        Tests when there is a string input with no format string.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE)
        val = field_schema.get_value({'time': '2013/04/02 9:25 PM'})
        self.assertEquals(val, datetime(2013, 4, 2, 21, 25))

    def test_none(self):
        """
        Tests getting a value of None.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': None})
        self.assertEquals(val, None)

    def test_blank(self):
        """
        Tests blank strings of input.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': '   '})
        self.assertEquals(val, None)

    def test_padded_date_with_format(self):
        """
        Tests a date that is padded and has a format string.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': '    2013-04-05     '})
        self.assertEquals(val, datetime(2013, 4, 5))

    def test_get_value_date(self):
        """
        Tests getting the value when the input is already a date object.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE)
        val = field_schema.get_value({'time': datetime(2013, 4, 4)})
        self.assertEquals(val, datetime(2013, 4, 4))

    def test_get_value_int(self):
        """
        Tests getting the date value of an int. Assumed to be a utc timestamp.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE)
        val = field_schema.get_value({'time': 1399486805})
        self.assertEquals(val, datetime(2014, 5, 7, 18, 20, 5))

    def test_get_value_float(self):
        """
        Tests getting the date value of an float. Assumed to be a utc timestamp.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE)
        val = field_schema.get_value({'time': 1399486805.0})
        self.assertEquals(val, datetime(2014, 5, 7, 18, 20, 5))

    def test_get_value_formatted(self):
        """
        Tests getting a formatted date value.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATE, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': '2013-04-05'})
        self.assertEquals(val, datetime(2013, 4, 5))


class DatetimeFieldSchemaTest(TestCase):
    """
    Tests the DATETIME type for field schemas.
    """
    def test_default_value_blank(self):
        """
        Tests when a default value is used and there is a blank string.
        """
        field_schema = G(
            FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, default_value='2013/04/02 9:25 PM')
        val = field_schema.get_value({'time': ' '})
        self.assertEquals(val, datetime(2013, 4, 2, 21, 25))

    def test_default_value_null(self):
        """
        Tests when a default value is used and there is a null object.
        """
        field_schema = G(
            FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, default_value='2013/04/02 9:25 PM')
        val = field_schema.get_value({'time': None})
        self.assertEquals(val, datetime(2013, 4, 2, 21, 25))

    def test_no_format_string(self):
        """
        Tests when there is a string input with no format string.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': '2013/04/02 9:25 PM'})
        self.assertEquals(val, datetime(2013, 4, 2, 21, 25))

    def test_datetime_with_tz_dateutil(self):
        """
        Tests that a datetime with a tz is converted back to naive UTC after using dateutil for parsing.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': '2013/04/02 09:25:00+0400'})
        self.assertEquals(val, datetime(2013, 4, 2, 5, 25))

    def test_datetime_with_tz(self):
        """
        Tests that a datetime with a tz is converted back to naive UTC.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': datetime(2013, 4, 2, 9, 25, tzinfo=pytz.utc)})
        self.assertEquals(val, datetime(2013, 4, 2, 9, 25))

    def test_none(self):
        """
        Tests getting a value of None.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': None})
        self.assertEquals(val, None)

    def test_blank(self):
        """
        Tests blank strings of input.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, field_format='%Y-%m-%d')
        val = field_schema.get_value({'time': '   '})
        self.assertEquals(val, None)

    def test_get_value_date(self):
        """
        Tests getting the value when the input is already a date object.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': datetime(2013, 4, 4)})
        self.assertEquals(val, datetime(2013, 4, 4))

    def test_get_value_int(self):
        """
        Tests getting the date value of an int. Assumed to be a utc timestamp.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': 1399486805})
        self.assertEquals(val, datetime(2014, 5, 7, 18, 20, 5))

    def test_get_value_float(self):
        """
        Tests getting the date value of an float. Assumed to be a utc timestamp.
        """
        field_schema = G(FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME)
        val = field_schema.get_value({'time': 1399486805.0})
        self.assertEquals(val, datetime(2014, 5, 7, 18, 20, 5))

    def test_get_value_formatted(self):
        """
        Tests getting a formatted date value.
        """
        field_schema = G(
            FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, field_format='%Y-%m-%d %H:%M:%S')
        val = field_schema.get_value({'time': '2013-04-05 12:12:12'})
        self.assertEquals(val, datetime(2013, 4, 5, 12, 12, 12))

    def test_get_value_formatted_unicode(self):
        """
        Tests getting a formatted date in unicode.
        """
        field_schema = G(
            FieldSchema, field_key='time', field_type=FieldSchemaType.DATETIME, field_format='%Y-%m-%d %H:%M:%S')
        val = field_schema.get_value({'time': u'2013-04-05 12:12:12'})
        self.assertEquals(val, datetime(2013, 4, 5, 12, 12, 12))


class IntFieldSchemaTest(TestCase):
    """
    Tests the INT type for field schemas.
    """
    def test_negative_string(self):
        """
        Tests parsing a negative string number.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': '-1'})
        self.assertEquals(val, -1)

    def test_none(self):
        """
        Tests getting a value of None.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': None})
        self.assertEquals(val, None)

    def test_blank(self):
        """
        Tests blank strings of input.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': '   '})
        self.assertEquals(val, None)

    def test_get_value_non_numeric_str(self):
        """
        Tests getting the value of a string that has currency information.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': ' $15,000,456 Dollars '})
        self.assertAlmostEquals(val, 15000456)

    def test_get_value_str(self):
        """
        Tests getting the value when the input is a string.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': '1'})
        self.assertEquals(val, 1)

    def test_get_value_int(self):
        """
        Tests getting the value when it is an int.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': 5})
        self.assertEquals(val, 5)

    def test_get_value_float(self):
        """
        Tests getting the date value of a float.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.INT)
        val = field_schema.get_value({'val': 5.2})
        self.assertEquals(val, 5)


class StringFieldSchemaTest(TestCase):
    """
    Tests the STRING type for field schemas.
    """
    def test_unicode_input(self):
        """
        Unicode should be handled properly.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': u'    '})
        self.assertEquals(val, '')

    def test_matching_format(self):
        """
        Tests returning a string that matches a format.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING, field_format='^[\d\.]+$')
        val = field_schema.get_value({'val': '23.45'})
        self.assertEquals(val, '23.45')

    def test_non_matching_format(self):
        """
        Tests returning a string that matches a format.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING, field_format='^[\d\.]+$')
        val = field_schema.get_value({'val': '23,45'})
        self.assertEquals(val, None)

    def test_matching_format_limit_length(self):
        """
        Tests returning a string that matches a format of a limited length number.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING, field_format='^[\d]{1,5}$')
        val = field_schema.get_value({'val': '2345'})
        self.assertEquals(val, '2345')
        val = field_schema.get_value({'val': '23456'})
        self.assertEquals(val, '23456')

    def test_non_matching_format_limit_length(self):
        """
        Tests returning a string that matches a format of a limited length number.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING, field_format='^[\d]{1,5}$')
        val = field_schema.get_value({'val': '234567'})
        self.assertEquals(val, None)

    def test_none(self):
        """
        Tests getting a value of None.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': None})
        self.assertEquals(val, None)

    def test_blank(self):
        """
        Tests blank strings of input. Contrary to other formats, the string field schema
        returns a blank string instead of None (since blank strings are valid strings).
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': '    '})
        self.assertEquals(val, '')

    def test_strip_whitespaces(self):
        """
        Tests that getting a string results in its leading and trailing whitespace being
        stripped.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': '   1 2  3    '})
        self.assertEquals(val, '1 2  3')

    def test_get_value_str(self):
        """
        Tests getting the value when the input is a string.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': '1'})
        self.assertEquals(val, '1')

    def test_get_value_int(self):
        """
        Tests getting the value when it is an int.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': 5})
        self.assertEquals(val, '5')

    def test_get_value_float(self):
        """
        Tests getting the date value of a float.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.STRING)
        val = field_schema.get_value({'val': 5.2})
        self.assertEquals(val, '5.2')


class FloatFieldSchemaTest(TestCase):
    """
    Tests the FLOAT type for field schemas.
    """
    def test_negative_string(self):
        """
        Tests parsing a negative string number.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': '-1.1'})
        self.assertEquals(val, -1.1)

    def test_none(self):
        """
        Tests getting a value of None.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': None})
        self.assertEquals(val, None)

    def test_blank(self):
        """
        Tests blank strings of input.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': '   '})
        self.assertEquals(val, None)

    def test_get_value_non_numeric_str(self):
        """
        Tests getting the value of a string that has currency information.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': ' $15,000,456.34 Dollars '})
        self.assertAlmostEquals(val, 15000456.34)

    def test_get_value_non_numeric_unicode(self):
        """
        Tests getting the value of a unicode object that has currency information.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': u' $15,000,456.34 Dollars '})
        self.assertAlmostEquals(val, 15000456.34)

    def test_get_value_str(self):
        """
        Tests getting the value when the input is a string.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': '1'})
        self.assertAlmostEquals(val, 1.0)

    def test_get_value_int(self):
        """
        Tests getting the value when it is an int.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': 5})
        self.assertAlmostEquals(val, 5.0)

    def test_get_value_float(self):
        """
        Tests getting the date value of a float.
        """
        field_schema = G(FieldSchema, field_key='val', field_type=FieldSchemaType.FLOAT)
        val = field_schema.get_value({'val': 5.2})
        self.assertAlmostEquals(val, 5.2)
