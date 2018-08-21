import unittest
import mock

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
