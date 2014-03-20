from core.testing.testcases import CLATestCase

from ...forms import YourProblemForm

from ..fixtures import mocked_api


class YourProblemFormTestCase(CLATestCase):
    def setUp(self):
        super(YourProblemFormTestCase, self).setUp()

        self.mocked_connection.category.get.return_value = mocked_api.CATEGORY_LIST

    def test_get(self):
        form = YourProblemForm()

        choices = form.fields['category'].choices
        self.assertEqual(len(choices), 4)
        self.assertEqual([c[0] for c in choices], ['immigration','abuse','consumer','debt'])
        self.assertEqual(list(choices)[0][1], 'Immigration')  # checking only the first one

    def _get_default_post_data(self):
        return {
            'category': 'debt',
            'your_problem_notes': 'lorem'
        }

    def test_post_success_first_time(self):
        """
        The first time we save the form without passing the eligibility reference,
        we call POST to create an object
        """
        data = self._get_default_post_data()
        form = YourProblemForm(data=data)
        self.assertTrue(form.is_valid())

        form.save()
        self.mocked_connection.eligibility_check.post.assert_called_with(data)

    def test_post_success_second_time(self):
        """
        The second time we save the form passing the eligibility reference,
        we call PATCH to update an object
        """
        reference = '1234567890'
        data = self._get_default_post_data()
        form = YourProblemForm(reference=reference, data=data)
        self.assertTrue(form.is_valid())

        form.save()
        self.mocked_connection.eligibility_check(reference).patch.assert_called_with(data)

    def test_post_validation_errors(self):
        default_data = self._get_default_post_data()

        ERRORS_DATA = [
            # category mandatory
            {
                'error': {'category': [u'This field is required.']},
                'data': { 'category': None }
            },
            # invalid category
            {
                'error': {'category': [u'Select a valid choice. 3333 is not one of the available choices.']},
                'data': { 'category': 3333 }
            },
            # notes too long
            {
                'error': {'your_problem_notes': [u'Ensure this value has at most 500 characters (it has 501).']},
                'data': { 'your_problem_notes': 's'*501 }
            },
        ]

        for error_data in ERRORS_DATA:
            data = dict(default_data)
            data.update(error_data['data'])

            form = YourProblemForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors, error_data['error'])
