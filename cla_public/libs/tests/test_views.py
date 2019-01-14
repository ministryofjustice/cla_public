import unittest

from flask import session, Flask
from wtforms import Form, StringField
from wtforms.validators import InputRequired
from cla_public.apps.checker.session import CheckerSessionInterface, CustomJSONEncoder

from cla_public.libs.views import FormWizard, FormWizardStep, SessionBackedFormView


class TestForm(Form):
    name = StringField(validators=[InputRequired()])


class FormView(SessionBackedFormView):
    def __init__(self):
        super(FormView, self).__init__()
        self.form_class = TestForm
        self.template = "form_test.html"

    def on_valid_submit(self):
        return "Foo"


class TestSessionBackedFormView(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.session_interface = CheckerSessionInterface()
        app.json_encoder = CustomJSONEncoder
        app.config["SECRET_KEY"] = "test"
        app.add_url_rule("/", view_func=FormView.as_view("form"))
        app.add_url_rule(
            "/session-expired", endpoint="base.session_expired", view_func=lambda request: "Session expired"
        )
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess.checker["foo"] = "bar"

    def test_get_form(self):
        self.assertEqual('<input id="name" name="name" type="text" value="">', self.client.get("/").data)

    def test_post_form_invalid(self):
        with self.client as client:
            form_data = {}
            self.assertEqual(
                '<input id="name" name="name" type="text" value=""> ' "This field is required.",
                client.post("/", data=form_data).data,
            )
            self.assertFalse("TestForm" in session.checker)

    def test_post_form_valid(self):
        with self.client as client:
            form_data = {"name": "Test"}
            self.assertEqual("Foo", client.post("/", data=form_data).data)
            self.assertTrue("TestForm" in session.checker)
            self.assertTrue("name" in session.checker["TestForm"])
            self.assertEqual("Test", session.checker["TestForm"]["name"])

    def test_form_data_from_session(self):
        with self.client.session_transaction() as sess:
            sess.checker["TestForm"] = {"name": "Test"}

        self.assertEqual('<input id="name" name="name" type="text" value="Test">', self.client.get("/").data)

    def test_redirect_if_no_session(self):
        with self.client.session_transaction() as sess:
            sess.clear_checker()

        response = self.client.get("/")
        self.assertEqual("http://localhost/session-expired", response.headers["Location"])


class TestForm2(Form):
    nick = StringField()


class TestForm3(Form):
    email = StringField()


class TestForm4(Form):
    city = StringField()


class TestWizard(FormWizard):

    steps = [
        ("one", FormWizardStep(TestForm, "form_test.html")),
        ("two", FormWizardStep(TestForm2, "form_test.html")),
        ("three", FormWizardStep(TestForm3, "form_test.html")),
        ("four", FormWizardStep(TestForm4, "form_test.html")),
    ]

    def skip(self, step):
        return step.name == "three"


class TestFormWizard(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.session_interface = CheckerSessionInterface()
        app.json_encoder = CustomJSONEncoder
        app.config["SECRET_KEY"] = "test"
        app.add_url_rule("/<step>", view_func=TestWizard.as_view("wizard"))
        app.add_url_rule(
            "/session-expired", endpoint="base.session_expired", view_func=lambda request: "Session expired"
        )
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess.checker["foo"] = "bar"

    def test_wizard_start(self):
        self.assertEqual('<input id="name" name="name" type="text" value="">', self.client.get("/one").data)

    def test_wizard_redirect_to_next_step(self):
        with self.client as client:
            form_data = {"name": "Test"}
            response = client.post("/one", data=form_data)
            self.assertEqual("http://localhost/two", response.headers["Location"])

    def test_wizard_skip_step(self):
        with self.client as client:
            form_data = {"nick": "Test"}
            response = client.post("/two", data=form_data)
            self.assertEqual("http://localhost/four", response.headers["Location"])
