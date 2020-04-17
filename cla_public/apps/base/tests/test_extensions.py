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
