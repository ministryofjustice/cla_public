import unittest

from cla_public.apps.base import filters


class QueryToDictTest(unittest.TestCase):
    def test_returns_the_parsed_query_parameters_when_no_prop_is_given(self):
        result = filters.query_to_dict("http://localhost:8000/?postcode=SW1A&page=3")
        self.assertEqual({"postcode": ["SW1A"], "page": ["3"]}, result)

    def test_returns_the_value_of_a_query_parameter_when_a_prop_is_given(self):
        result = filters.query_to_dict("http://localhost:8000/?postcode=SW1A&page=3", "page")
        self.assertEqual(["3"], result)

    def test_returns_an_empty_list_when_a_prop_is_given_but_does_not_exist(self):
        result = filters.query_to_dict("http://localhost:8000/?postcode=SW1A&page=3", "potato")
        self.assertEqual([], result)
