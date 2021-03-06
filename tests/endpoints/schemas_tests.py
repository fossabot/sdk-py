# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import unittest

import pytz
from datetime import datetime, date

from predicthq.endpoints import decorators, schemas
from predicthq.endpoints.base import BaseEndpoint


class SchemasTest(unittest.TestCase):

    def test_datetime_type(self):

        class SchemaExample(schemas.Model):

            my_datetime = schemas.DateTimeType()

        test_date = datetime(2016, 1, 1, tzinfo=pytz.UTC)
        self.assertEqual(SchemaExample({"my_datetime": "2016-01-01T00:00:00+00:00"}).my_datetime, test_date)
        self.assertEqual(SchemaExample({"my_datetime": "2016-01-01T00:00:00+0000"}).my_datetime, test_date)
        self.assertEqual(SchemaExample({"my_datetime": "2016-01-01T00:00:00Z"}).my_datetime, test_date)
        self.assertEqual(SchemaExample({"my_datetime": test_date}).my_datetime, test_date)

    def test_date_type(self):

        class SchemaExample(schemas.Model):

            my_date = schemas.DateType()

        test_date = date(2016, 1, 1)
        self.assertEqual(SchemaExample({"my_date": "2016-01-01"}).my_date, test_date)
        self.assertEqual(SchemaExample({"my_date": "2016-01-01T00:00:00+0000"}).my_date, test_date)
        self.assertEqual(SchemaExample({"my_date": "2016-01-01T00:00:00Z"}).my_date, test_date)
        self.assertEqual(SchemaExample({"my_date": test_date}).my_date, test_date)


    def test_string_model_and_string_model_type(self):

        class MyModel(schemas.StringModel):

            import_format = r"(?P<left>.*)==(?P<right>\d*)"
            export_format = "{left}=={right}"

            left = schemas.StringType()
            right = schemas.IntType()

        class SchemaExample(schemas.Model):

            my_model = schemas.StringModelType(MyModel)

        short_data = {"my_model": "ten==10"}
        long_data = {"my_model": {"left": "ten", "right": 10}}
        model_data = {"my_model": MyModel("ten==10")}
        invalid_data = {"my_model": "10==ten"}

        expected_data = {"my_model": "ten==10"}

        m = SchemaExample()

        self.assertDictEqual(m.import_data(short_data).to_primitive(), expected_data)
        self.assertDictEqual(m.import_data(long_data).to_primitive(), expected_data)
        self.assertDictEqual(m.import_data(model_data).to_primitive(), expected_data)

        self.assertDictEqual(m.import_data(short_data).to_dict(), expected_data)
        self.assertDictEqual(m.import_data(long_data).to_dict(), expected_data)
        self.assertDictEqual(m.import_data(model_data).to_dict(), expected_data)

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data(invalid_data)

    def test_string_list_type(self):

        class SchemaExample(schemas.Model):

            area_list = schemas.StringListType(schemas.StringModelType(schemas.Area), separator="+")
            string_list = schemas.StringListType(schemas.StringType, separator="+")

        string_data = {"string_list": "a+b+c", "area_list": "10km@-36.847585,174.765742+10km@-41.288058,174.778265"}
        list_data = {"string_list": ["a", "b", "c"], "area_list": ["10km@-36.847585,174.765742", "10km@-41.288058,174.778265"]}
        dict_data = {"string_list": ["a", "b", "c"], "area_list": [{"radius": "10km", "latitude": -36.847585, "longitude": 174.765742}, {"radius": "10km", "latitude": -41.288058, "longitude": 174.778265}]}

        expected_data = {"string_list": "a+b+c", "area_list": "10km@-36.847585,174.765742+10km@-41.288058,174.778265"}

        m = SchemaExample()
        self.assertDictEqual(m.import_data(string_data).to_primitive(), expected_data)
        self.assertDictEqual(m.import_data(list_data).to_primitive(), expected_data)
        self.assertDictEqual(m.import_data(dict_data).to_primitive(), expected_data)

        unique_item_data = {"string_list": "a", "area_list": "10km@-36.847585,174.765742"}
        unique_item_dict_data = {"string_list": "a", "area_list": {"radius": "10km", "latitude": -36.847585, "longitude": 174.765742}}
        self.assertDictEqual(m.import_data(unique_item_data).to_primitive(), unique_item_data)
        self.assertDictEqual(m.import_data(unique_item_dict_data).to_primitive(), unique_item_data)

    def test_list_type(self):

        class SchemaExample(schemas.Model):

            string_list = schemas.ListType(schemas.StringType)

        m = SchemaExample()
        self.assertDictEqual(m.import_data({"string_list": "string"}).to_primitive(), {"string_list": ["string"]})
        self.assertDictEqual(m.import_data({"string_list": ["string1", "string2"]}).to_primitive(), {"string_list": ["string1", "string2"]})

    def test_geo_json_point_type(self):

        class SchemaExample(schemas.Model):

            point = schemas.GeoJSONPointType()

        m = SchemaExample()
        self.assertDictEqual(m.import_data({"point": [174.765742, -36.847585]}).to_primitive(), {"point": [174.765742, -36.847585]})

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data({"point": [-36.847585, 174.765742]}, validate=True)

    def test_date_around_type(self):

        class SchemaExample(schemas.Model):
            around = schemas.ModelType(schemas.DateAround)

        m = SchemaExample()

        self.assertDictEqual(m.import_data({"around": {"origin": '2020-01-01', "offset": "1d", "scale": "0d", "decay": "0.1"}}).to_primitive(),
                             {'around': {'origin': '2020-01-01', 'decay': 0.1, 'scale': u'0d', 'offset': u'1d'}})

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data({"around": "2020-01-01"}, validate=True)

    def test_location_around_type(self):
        class SchemaExample(schemas.Model):
            around = schemas.ModelType(schemas.LocationAround)

        m = SchemaExample()

        self.assertDictEqual(m.import_data(
            {"around": {"origin": '40.730610,-73.935242', "offset": "1km", "scale": "2km", "decay": "0.1"}}).to_primitive(),
                             {'around': {'origin': u'40.730610,-73.935242', 'decay': 0.1, 'scale': u'2km', 'offset': u'1km'}})

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data({"around": "40.730610,-73.935242"}, validate=True)

    def test_area_model(self):

        class SchemaExample(schemas.Model):

            area = schemas.StringModelType(schemas.Area)

        short_data = {"area": "10km@-36.847585,174.765742"}
        long_data = {"area": {"radius": "10km", "latitude": -36.847585, "longitude": 174.765742}}
        model_data = {"area": schemas.Area("10km@-36.847585,174.765742")}
        invalid_data = {"area": "10k@-36.847585,174.765742"}

        expected_expected = {"area": "10km@-36.847585,174.765742"}

        m = SchemaExample()
        self.assertDictEqual(m.import_data(short_data).to_primitive(), expected_expected)
        self.assertDictEqual(m.import_data(long_data).to_primitive(), expected_expected)
        self.assertDictEqual(m.import_data(model_data).to_primitive(), expected_expected)

        self.assertDictEqual(m.import_data(short_data).to_dict(), expected_expected)
        self.assertDictEqual(m.import_data(long_data).to_dict(), expected_expected)
        self.assertDictEqual(m.import_data(model_data).to_dict(), expected_expected)

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data(invalid_data)

    def test_location_model(self):

        class SchemaExample(schemas.Model):

            location = schemas.StringModelType(schemas.Location)

        short_data = {"location": "@-36.847585,174.765742"}
        long_data = {"location": {"latitude": -36.847585, "longitude": 174.765742}}
        model_data = {"location": schemas.Location("@-36.847585,174.765742")}
        invalid_data = {"location": "-36.847585,174.765742"}

        expected_expected = {"location": "@-36.847585,174.765742"}

        m = SchemaExample()
        self.assertDictEqual(m.import_data(short_data).to_primitive(), expected_expected)
        self.assertDictEqual(m.import_data(long_data).to_primitive(), expected_expected)
        self.assertDictEqual(m.import_data(model_data).to_primitive(), expected_expected)

        self.assertDictEqual(m.import_data(short_data).to_dict(), expected_expected)
        self.assertDictEqual(m.import_data(long_data).to_dict(), expected_expected)
        self.assertDictEqual(m.import_data(model_data).to_dict(), expected_expected)

        with self.assertRaises(schemas.SchematicsDataError):
            m.import_data(invalid_data)

    def test_resultset(self):

        class ResultExample(schemas.Model):

            value = schemas.IntType()

        class ResultSetExample(schemas.ResultSet):

            results = schemas.ResultType(ResultExample)

        class EndpointExample(BaseEndpoint):

            @decorators.returns(ResultSetExample)
            def load_page(self, page):
                page = int(page)
                return {
                    "count": 9,
                    "next": "http://example.org/?page={}".format(page + 1) if page < 3 else None,
                    "previous": "http://example.org/?page={}".format(page - 1) if page > 1 else None,
                    "results": [{"value": 1 + (3 * (page - 1))}, {"value": 2 + (3 * (page - 1))}, {"value": 3 + (3 * (page - 1))}]
                }

        endpoint = EndpointExample(None)

        p1 = endpoint.load_page(page=1)
        self.assertEqual(p1.count, 9)
        self.assertListEqual(list(p1), [ResultExample({"value": 1}), ResultExample({"value": 2}), ResultExample({"value": 3})])
        self.assertFalse(p1.has_previous())
        self.assertTrue(p1.has_next())
        self.assertIsNone(p1.get_previous())

        p2 = p1.get_next()

        self.assertListEqual(list(p2), [ResultExample({"value": 4}), ResultExample({"value": 5}), ResultExample({"value": 6})])
        self.assertTrue(p2.has_previous())
        self.assertTrue(p2.has_next())

        p3 = p2.get_next()
        self.assertListEqual(list(p3), [ResultExample({"value": 7}), ResultExample({"value": 8}), ResultExample({"value": 9})])
        self.assertTrue(p3.has_previous())
        self.assertFalse(p3.has_next())

        self.assertIsNone(p3.get_next())
        self.assertListEqual(list(p3.get_previous()), list(p2))

        self.assertListEqual(list(p1.iter_pages()), [endpoint.load_page(page=2), endpoint.load_page(page=3)])
        self.assertListEqual(list(p1.iter_all()), list(p1) + list(p2) + list(p3))

        for item in p1.iter_all():
            self.assertEqual(item._endpoint, endpoint)
