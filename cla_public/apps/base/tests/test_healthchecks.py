import unittest
import mock
import requests

from cla_public import app
from cla_public.apps.base import healthchecks


class DiskSpaceHealthcheckTest(unittest.TestCase):
    @mock.patch('os.statvfs')
    def test_disk_space_check_reports_on_available_and_total_space(self, stat_mock):
        stat_mock.return_value.f_bavail = 50 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset(
            {'available_percent': 50.0, 'available_mb': 50.0, 'total_mb': 100.0}, result)

    @mock.patch('os.statvfs')
    def test_disk_space_check_passes_when_more_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 3 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset(
            {'status': True, 'available_percent': 3.0}, result)

    @mock.patch('os.statvfs')
    def test_disk_space_check_fails_when_less_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 2 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset(
            {'status': False, 'available_percent': 2.0}, result)


class BackendAPIHealthcheckTest(unittest.TestCase):
    def setUp(self):
        self.app = app.create_app('config/testing.py')
        self.app.test_request_context().push()

    @mock.patch('requests.get')
    def test_backend_check_fails_if_request_fails(self, request_mock):
        request_mock.side_effect = requests.exceptions.ConnectionError()

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset(
            {'status': False, 'response': 'ConnectionError'}, result)

    @mock.patch('requests.get')
    def test_backend_check_fails_if_backend_is_unhealthy(self, request_mock):
        request_mock.return_value.ok = False
        request_mock.return_value.json.return_value = {'status': 'DOWN'}

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset(
            {'status': False, 'response': {'status': 'DOWN'}}, result)

    @mock.patch('requests.get')
    def test_backend_check_passes_if_backend_is_healthy(self, request_mock):
        request_mock.return_value.ok = True
        request_mock.return_value.json.return_value = {'status': 'UP'}

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset(
            {'status': True, 'response': {'status': 'UP'}}, result)


class HealthcheckEndpointTest(unittest.TestCase):
    check_disk = 'cla_public.apps.base.healthchecks.check_disk'
    check_backend_api = 'cla_public.apps.base.healthchecks.check_backend_api'

    def setUp(self):
        self.app = app.create_app('config/testing.py')
        self.app.test_request_context().push()
        self.client = self.app.test_client()

    def assert_response_is_service_unavailable(self):
        result = self.client.get('/healthcheck.json')
        self.assertEquals(requests.codes.service_unavailable,
                          result.status_code)

    def test_healthcheck_returns_service_unavailable_if_any_or_all_checks_fail(self):
        with mock.patch(self.check_disk, return_value={'status': False}), mock.patch(self.check_backend_api, return_value={'status': True}):
            self.assert_response_is_service_unavailable()

        with mock.patch(self.check_disk, return_value={'status': True}), mock.patch(self.check_backend_api, return_value={'status': False}):
            self.assert_response_is_service_unavailable()

        with mock.patch(self.check_disk, return_value={'status': False}), mock.patch(self.check_backend_api, return_value={'status': False}):
            self.assert_response_is_service_unavailable()

    def test_healthcheck_returns_ok_if_all_checks_pass(self):
        with mock.patch(self.check_disk, return_value={'status': True}), mock.patch(self.check_backend_api, return_value={'status': True}):
            result = self.client.get('/healthcheck.json')
            self.assertEquals(requests.codes.ok, result.status_code)
