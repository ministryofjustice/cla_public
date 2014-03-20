# # -*- coding: utf-8 -*-
# from cla_frontend.apps.api import client as c
# from django.conf import settings
# import os
# import slumber.exceptions as sx

# from unittest import TestCase
# from betamax import Betamax
# from requests import Session

# with Betamax.configure() as config:
#     config.cassette_library_dir = \
#         os.path.join(
#             settings.PROJECT_ROOT, 'apps/api/tests/fixtures/cassettes')


# class ApiClient(TestCase):

#     def setUp(self):
#         self.session = Session()
#         self.api_connection = c.get_connection(self.session)

#     def test_category_list(self):
#         """
#         TEST: that category list returns some results
#         """
#         with Betamax(self.session) as vcr:
#             vcr.use_cassette('category')
#             category_list = c.Category(self.api_connection).list()
#             self.assertTrue(len(category_list))

#     def test_eligibility_check_create_not_allowed(self):
#         """
#         TEST: that creating an eligibility_check works
#         """
#         with Betamax(self.session) as vcr:
#             vcr.use_cassette('eligibility_check')
#             category_list = c.Category(self.api_connection).list()
#             el_check = c.EligibilityCheck(self.api_connection).create()
#             self.assertRaises(sx.HttpClientError)
