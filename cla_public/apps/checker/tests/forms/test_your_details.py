from core.testing.testcases import CLATestCase

from ...forms import YourDetailsForm


class YourDetailsFormTestCase(CLATestCase):
    def setUp(self):
        super(YourDetailsFormTestCase, self).setUp()

    def test_get(self):
        form = YourDetailsForm()
        self.assertFalse(form.is_valid())

    def _get_default_post_data(self):
        return {
            'older_than_sixty': 0,
            'has_partner': 0,
            'has_benefits': 0,
            'has_children': 0,
            'caring_responsibilities': 0,
            'own_property': 0,
            'risk_homeless': 0,
        }

    def _get_default_post_data_response(self):
        return {
            'reference': '123456789',
            "category": 'null',
            "your_problem_notes": "",
            "notes": "",
            "property_set": [],
            "your_finances": 'null',
            "partner_finances": 'null',
            "dependants_young": 0,
            "dependants_old": 0,
            "is_you_or_your_partner_over_60": True,
            "has_partner": True,
            "on_passported_benefits": True
        }

    def test_basic_post(self):
        data = self._get_default_post_data()
        form = YourDetailsForm(data=data)
        self.assertTrue(form.is_valid())

        self.mocked_connection.eligibility_check.post.return_value = self._get_default_post_data_response()
        response = form.save()
        self.mocked_connection.eligibility_check.post.assert_called_with({
            'on_passported_benefits': data['has_benefits'],
            'is_you_or_your_partner_over_60': data['older_than_sixty'],
            'has_partner': data['has_partner']
        })
        self.assertTrue('reference' in response['eligibility_check'])
        self.assertDictContainsSubset(
            {
                'is_you_or_your_partner_over_60': True,
                'has_partner': True,
                'on_passported_benefits': True
            },
            response['eligibility_check'])

    def test_form_validation_error(self):
        default_data = self._get_default_post_data()
        ERRORS_DATA = [
            # just testing a few
            # has_partner req'd
            {
                'error': {'has_partner': [u'This field is required.']},
                'data': {'has_partner': None}
            },
            # is_you_or_your_partner_over_60 req'd
            {
                'error': {'older_than_sixty': [u'This field is required.']},
                'data': {'older_than_sixty': None}
            }
        ]
        for error_data in ERRORS_DATA:
            data = dict(default_data)
            data.update(error_data['data'])

            form = YourDetailsForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors, error_data['error'])

    def test_patch_success(self):
        reference = '123456789'
        data = self._get_default_post_data()
        form = YourDetailsForm(reference=reference, data=data)
        self.assertTrue(form.is_valid())
        self.mocked_connection.eligibility_check.patch.return_value = self._get_default_post_data_response()
        form.save()
        self.mocked_connection.eligibility_check(reference).patch.assert_called_with(
            {
                'on_passported_benefits': data['has_benefits'],
                'is_you_or_your_partner_over_60': data['older_than_sixty'],
                'has_partner': data['has_partner']
            }
        )
        self.mocked_connection.eligibility_check.assert_called_with(reference)
