from werkzeug.http import parse_cookie

from cla_public.apps.base.tests import FlaskAppTestCase


class LocaleTest(FlaskAppTestCase):
    def setUp(self):
        super(LocaleTest, self).setUp()
        self.client = self.app.test_client()

    def test_locale_cookie_is_set(self):
        with self.app.test_client() as client:
            response = client.get("/?locale=en_GB")
            self.check_cookie(response, "locale", "en_GB")

    def check_cookie(self, response, name, value):
        # Checks for existence of a cookie and verifies the value of it.

        cookies = response.headers.getlist("Set-Cookie")
        for cookie in cookies:
            c_key, c_value = parse_cookie(cookie).items()[0]
            if c_key == name:
                assert c_value == value
                return
        # Cookie not found
        assert False
