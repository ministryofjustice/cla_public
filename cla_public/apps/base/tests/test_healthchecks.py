import unittest
import mock
import requests

from cla_public.apps.base import healthchecks
from cla_public.apps.base.tests import FlaskAppTestCase


class DiskSpaceHealthcheckTest(unittest.TestCase):
    @mock.patch("os.statvfs")
    def test_disk_space_check_reports_on_available_and_total_space(self, stat_mock):
        stat_mock.return_value.f_bavail = 50 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset({"available_percent": 50.0, "available_mb": 50.0, "total_mb": 100.0}, result)

    @mock.patch("os.statvfs")
    def test_disk_space_check_passes_when_more_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 3 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset({"status": "healthy", "available_percent": 3.0}, result)

    @mock.patch("os.statvfs")
    def test_disk_space_check_fails_when_less_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 2 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertDictContainsSubset({"status": "unhealthy", "available_percent": 2.0}, result)


class BackendAPIHealthcheckTest(FlaskAppTestCase):
    @mock.patch("requests.get")
    def test_backend_check_fails_if_request_fails(self, request_mock):
        request_mock.side_effect = requests.exceptions.ConnectionError()

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset({"status": "unhealthy", "response": "ConnectionError"}, result)

    @mock.patch("requests.get")
    def test_backend_check_fails_if_backend_is_unhealthy(self, request_mock):
        request_mock.return_value.ok = False
        request_mock.return_value.json.return_value = {"status": "DOWN"}

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset({"status": "unhealthy", "response": {"status": "DOWN"}}, result)

    @mock.patch("requests.get")
    def test_backend_check_passes_if_backend_is_healthy(self, request_mock):
        request_mock.return_value.ok = True
        request_mock.return_value.json.return_value = {"status": "UP"}

        result = healthchecks.check_backend_api()
        self.assertDictContainsSubset({"status": "healthy", "response": {"status": "UP"}}, result)


class HealthcheckEndpointTest(FlaskAppTestCase):
    check_disk = "cla_public.apps.base.healthchecks.check_disk"
    check_backend_api = "cla_public.apps.base.healthchecks.check_backend_api"

    def setUp(self):
        super(HealthcheckEndpointTest, self).setUp()
        self.client = self.app.test_client()

    def assert_response_is_service_unavailable(self):
        result = self.client.get("/healthcheck.json")
        self.assertEquals(requests.codes.service_unavailable, result.status_code)

    def test_healthcheck_returns_service_unavailable_if_any_or_all_checks_fail(self):
        with mock.patch(self.check_disk, return_value={"status": "unhealthy"}), mock.patch(
            self.check_backend_api, return_value={"status": "healthy"}
        ):
            self.assert_response_is_service_unavailable()

        with mock.patch(self.check_disk, return_value={"status": "healthy"}), mock.patch(
            self.check_backend_api, return_value={"status": "unhealthy"}
        ):
            self.assert_response_is_service_unavailable()

        with mock.patch(self.check_disk, return_value={"status": "unhealthy"}), mock.patch(
            self.check_backend_api, return_value={"status": "unhealthy"}
        ):
            self.assert_response_is_service_unavailable()

    def test_healthcheck_returns_ok_if_all_checks_pass(self):
        with mock.patch(self.check_disk, return_value={"status": "healthy"}), mock.patch(
            self.check_backend_api, return_value={"status": "healthy"}
        ):
            result = self.client.get("/healthcheck.json")
            self.assertEquals(requests.codes.ok, result.status_code)
