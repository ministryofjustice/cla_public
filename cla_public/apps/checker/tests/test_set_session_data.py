# coding: utf-8
from cla_common.constants import DIAGNOSIS_SCOPE

from cla_public.apps.base.tests import FlaskAppTestCase
from flask import session
from cla_public.apps.checker.utils import set_session_data


class TestSetSessionData(FlaskAppTestCase):
    def test_valid_category_simple_data(self):
        """Test setting session data with valid category and simple question-answer map"""
        category = "debt"
        question_answer_map = [{"question": "Question 1", "answer": "Yes"}, {"question": "Question 2", "answer": "No"}]

        set_session_data(category, question_answer_map)

        # Check session was updated correctly
        self.assertEqual(session.checker["category"], "debt")
        self.assertEqual(len(session.checker["scope_answers"]), 2)

        # Check scope answers were added correctly
        expected_scope_answers = [
            {"answer": "Yes", "question": "Question 1"},
            {"answer": "No", "question": "Question 2"},
        ]
        self.assertEqual(session.checker["scope_answers"], expected_scope_answers)

        # Check notes were formatted correctly
        expected_notes = "Question 1: Yes\n\nQuestion 2: No\n\nOutcome: Unknown (Diagnosis not complete)"
        self.assertEqual(session.checker["notes"][u"User selected"], expected_notes)

    def test_invalid_category(self):
        """Test that invalid category raises ValueError"""
        category = "invalid-category"
        question_answer_map = {"Question": "Answer"}

        with self.assertRaises(ValueError) as context:
            set_session_data(category, question_answer_map)

        self.assertEqual(str(context.exception), "Invalid Category Code")

    def test_domestic_abuse_category(self):
        """Test special handling for domestic-abuse category"""
        category = "domestic-abuse"
        question_answer_map = {}

        set_session_data(category, question_answer_map)

        # Check domestic abuse specific session data
        self.assertEqual(session.checker["diagnosis_previous_choices"], ["n18"])
        self.assertEqual(session.checker["category"], "violence")

    def test_empty_question_answer_map(self):
        """Test handling of empty question-answer map"""
        category = "debt"
        question_answer_map = {}

        set_session_data(category, question_answer_map)

        # Check basic session data was set
        self.assertEqual(session.checker["category"], "debt")
        self.assertEqual(session.checker["scope_answers"], [])
        self.assertEqual(session.checker["notes"][u"User selected"], "Outcome: Unknown (Diagnosis not complete)")

    def test_unicode_handling(self):
        """Test handling of unicode characters in questions and answers"""
        category = "family"
        question_answer_map = [{"question": "Answer with a non-ascii character", "answer": u"München"}]

        set_session_data(category, question_answer_map)

        expected_notes = u"Answer with a non-ascii character: München\n\nOutcome: Unknown (Diagnosis not complete)"
        self.assertEqual(session.checker["notes"][u"User selected"], expected_notes)

    def test_session_preservation(self):
        """Test that existing session data is preserved when setting new data"""
        session.checker = {"existing_key": "should_remain"}

        category = "debt"
        question_answer_map = [{"question": "Question 1", "answer": "Yes"}, {"question": "Question 2", "answer": "No"}]

        set_session_data(category, question_answer_map)

        # Check that new data was added and old data preserved
        self.assertEqual(session.checker["existing_key"], "should_remain")
        self.assertEqual(session.checker["category"], "debt")

    def test_inscope_outcome(self):
        category = "debt"
        question_answer_map = {}

        set_session_data(category, question_answer_map, outcome=DIAGNOSIS_SCOPE.INSCOPE)

        self.assertEqual(session.checker["notes"][u"User selected"], "Outcome: In Scope")

    def test_contact_outcome(self):
        category = "debt"
        question_answer_map = {}

        set_session_data(category, question_answer_map, outcome=DIAGNOSIS_SCOPE.CONTACT)

        self.assertEqual(session.checker["notes"][u"User selected"], "Outcome: In Scope - skip means test")

    def test_harm_flag(self):
        """Test that the correct content is added to the notes when a harm_flag is used"""
        category = "debt"
        question_answer_map = {}

        set_session_data(category, question_answer_map, harm_flag=True)

        self.assertEqual(session.checker["notes"][u"Public Diagnosis note"], "User is at immediate risk of harm")
