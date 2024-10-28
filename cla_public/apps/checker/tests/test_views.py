from collections import OrderedDict
from mock import patch
import jwt
from flask import url_for
from cla_public.apps.base.tests import FlaskAppTestCase
from urllib import urlencode


class TestReceiveUserAnswers(FlaskAppTestCase):
    def setUp(self):
        super(TestReceiveUserAnswers, self).setUp()
        self.app.config["JWT_SECRET"] = "test-secret"
        self.app.config["DEBUG"] = True
        self.client = self.app.test_client()
        self.valid_payload = {
            "category": "debt",
            "answers": OrderedDict([("Question 1", "Yes"), ("Question 2", "No")]),
            "destination": "means-test",
        }
        self.landing_url = url_for("checker.receive_user_answers")

    def create_token(self, payload):
        return jwt.encode(payload, self.app.config["JWT_SECRET"], algorithm="HS256")

    def get_url_with_token(self, token):
        """Helper method to create URL with token parameter"""
        params = urlencode({"token": token})
        return "{0}?{1}".format(self.landing_url, params)

    def test_malformed_token(self):
        with self.client as client:
            response = client.get(self.get_url_with_token("invalid token"))
            self.assertEqual(response.status_code, 403)

    def test_empty_token(self):
        with self.client as client:
            response = client.get(self.landing_url)
            self.assertEqual(response.status_code, 404)

    def test_missing_jwt_secret(self):
        self.app.config["JWT_SECRET"] = ""
        token = self.create_token(self.valid_payload)
        with self.client as client:
            response = client.get(self.get_url_with_token(token))
            self.assertEqual(response.status_code, 500)

    @patch("cla_public.apps.checker.views.set_session_data")
    def test_set_session_data_called(self, mock_set_session):
        token = self.create_token(self.valid_payload)

        self.client.get(self.get_url_with_token(token))

        # Check set_session_data was called with correct args
        mock_set_session.assert_called_once_with("debt", OrderedDict([("Question 1", "Yes"), ("Question 2", "No")]))

    def test_valid_token_means_test(self,):
        """Test successful means test flow with valid token"""
        token = self.create_token(self.valid_payload)

        response = self.client.get(self.get_url_with_token(token))

        # Should redirect to interstitial
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/legal-aid-available"))

    def test_valid_token_contact(self):
        """Test successful contact flow with valid token"""
        payload = {
            "category": "domestic-abuse",
            "answers": OrderedDict([("Question 1", "Yes"), ("Question 2", "No")]),
            "destination": "contact",
        }
        token = self.create_token(payload)

        response = self.client.get(self.get_url_with_token(token))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/contact"))

    def test_valid_token_fala(self):
        """Test successful fala flow with valid token"""
        payload = {"category": "clinneg", "destination": "fala", "answers": {}}
        token = self.create_token(payload)

        response = self.client.get(self.get_url_with_token(token))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("scope/refer/legal-adviser?category=clinneg"))
