from cla_public.apps.base.tests import FlaskAppTestCase
from cla_public.apps.base.extensions import is_quick_exit_enabled


class SessionLikeObject(object):
    checker = {}

    def set_history(self, choices):
        self.checker.update(diagnosis_previous_choices=choices)


class TestIsQuickExitEnabled(FlaskAppTestCase):
    def setUp(self):
        super(TestIsQuickExitEnabled, self).setUp()
        self.session = SessionLikeObject()

    def test_no_diagnosis_choices(self):
        self.assertFalse(is_quick_exit_enabled(self.session))

    def test_empty_diagnosis_choices(self):
        self.session.set_history([])
        self.assertFalse(is_quick_exit_enabled(self.session))

    def test_no_quick_exit_route(self):
        self.session.set_history(["n43n14"])
        self.assertFalse(is_quick_exit_enabled(self.session))
        self.session.set_history(["n43n14", "n56"])
        self.assertFalse(is_quick_exit_enabled(self.session))

    def test_quick_exit_top_level_route(self):
        self.session.set_history(["n43n3"])
        self.assertTrue(is_quick_exit_enabled(self.session))
        self.session.set_history(["n43n3", "n45"])
        self.assertTrue(is_quick_exit_enabled(self.session))

    def test_quick_exit_deeper_route(self):
        self.session.set_history(["n43n14"])
        self.assertFalse(is_quick_exit_enabled(self.session))
        self.session.set_history(["n43n14", "n97"])
        self.assertTrue(is_quick_exit_enabled(self.session))

    def test_partial_code_match(self):
        self.session.set_history(["n1", "n1490"])
        self.assertFalse(is_quick_exit_enabled(self.session))


class TestMaintenanceModeEnabled(FlaskAppTestCase):
    def test_maintenance_mode_enabled_start_page(self):
        self.app.config["MAINTENANCE_MODE"] = True
        client = self.app.test_client()
        response = client.get("/start")
        self.assertEqual(302, response.status_code)
        headers = dict(response.headers)
        self.assertEqual(headers.get("Location"), "http://localhost/maintenance")

    def test_maintenance_mode_disabled_start_page(self):
        self.app.config["MAINTENANCE_MODE"] = False
        client = self.app.test_client()
        response = client.get("/start")
        self.assertEqual(302, response.status_code)
        headers = dict(response.headers)
        self.assertEqual(headers.get("Location"), "http://localhost/scope/diagnosis/")

    def test_maintenance_mode_enabled_maintenance_page(self):
        self.app.config["MAINTENANCE_MODE"] = True
        client = self.app.test_client()
        response = client.get("/maintenance")
        self.assertEqual(200, response.status_code)
        self.assertIn("This service is currently down for maintenance", response.data)

    def test_maintenance_mode_disabled_maintenance_page(self):
        self.app.config["MAINTENANCE_MODE"] = False
        client = self.app.test_client()
        response = client.get("/maintenance")
        self.assertEqual(302, response.status_code)
        headers = dict(response.headers)
        self.assertEqual(headers.get("Location"), "http://localhost/")
