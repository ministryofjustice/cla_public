from core.testing.testcases import CLATestCase

from ...forms import ApplyForm

from ...exceptions import InconsistentStateException

from ..fixtures import mocked_api


class ApplyFormTestCase(CLATestCase):
    # def setUp(self):
    #     super(ApplyFormTestCase, self).setUp()

    CONTACT_DETAILS_DEFAULT_DATA = {
        'title': 'mr',
        'full_name': 'John Doe',
        'postcode': 'SW1H 9AJ',
        'street': '102 Petty France',
        'mobile_phone': '0123456789',
        'home_phone': '9876543210'
    }

    EXTRA_DEFAULT_DATA = {
        'notes': 'lorem ipsum'
    }

    DEFAULT_CHECK_REFERENCE = 1234567890

    def _get_default_post_data(self):
        cd_data = dict(('contact_details-'+key, val) for key, val in self.CONTACT_DETAILS_DEFAULT_DATA.items())
        extra_data = dict(('extra-'+key, val) for key, val in self.EXTRA_DEFAULT_DATA.items())

        data = {}
        data.update(cd_data)
        data.update(extra_data)
        return data

    def test_form_validation(self):
        default_data = self._get_default_post_data()

        ERRORS_DATA = [
            # mandatory fields (notes is not mandatory)
            {
                'error': {
                    'contact_details': {
                        'title': [u'This field is required.'],
                        'full_name': [u'This field is required.'],
                        'postcode': [u'This field is required.'],
                        'street': [u'This field is required.'],
                    }
                },
                'data': {
                    'contact_details-title': None,
                    'contact_details-full_name': None,
                    'contact_details-postcode': None,
                    'contact_details-street': None,
                    'contact_details-mobile_phone': None,
                    'contact_details-home_phone': None,
                    'extra-notes': None
                }
            },
            # must be mobile phone or home phone
            {
                'error': {
                    'contact_details': {
                        'mobile_phone': [u'You must specify at least one contact number.'],
                    }
                },
                'data': {
                    'contact_details-mobile_phone': None,
                    'contact_details-home_phone': None,
                }
            },
            # notes too long
            {
                'error': {
                    'contact_details': {
                        'full_name': [u'Ensure this value has at most 300 characters (it has 301).'],
                        'postcode': [u'Ensure this value has at most 10 characters (it has 11).'],
                        'street': [u'Ensure this value has at most 250 characters (it has 251).'],
                        'mobile_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                        'home_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                    },
                    'extra': {
                        'notes': [u'Ensure this value has at most 500 characters (it has 501).']
                    }
                },
                'data': {
                    'contact_details-full_name': u'a'*301,
                    'contact_details-postcode': u'a'*11,
                    'contact_details-street': u'a'*251,
                    'contact_details-mobile_phone': u'a'*21,
                    'contact_details-home_phone': u'a'*21,
                    'extra-notes': u'a'*501
                }
            },
            # invalid title
            {
                'error': {
                    'contact_details': {
                        'title': [u'Select a valid choice. invalid is not one of the available choices.'],
                    }
                },
                'data': {
                    'contact_details-title': u'invalid',
                }
            },
        ]

        for error_data in ERRORS_DATA:
            data = dict(default_data)
            data.update(error_data['data'])

            form = ApplyForm(reference=self.DEFAULT_CHECK_REFERENCE, data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors, error_data['error'])

    def test_post_success(self):
        # mocking API response
        self.maxDiff = 0
        mocked_save_response = {
            'reference': 'abcdefg',
            'personal_details': self.CONTACT_DETAILS_DEFAULT_DATA
        }
        self.mocked_connection.case.post.return_value = mocked_save_response
        self.mocked_connection.eligibility_check(self.DEFAULT_CHECK_REFERENCE).\
            is_eligible().post.return_value = mocked_api.IS_ELIGIBLE_YES

        data = self._get_default_post_data()
        form = ApplyForm(reference=self.DEFAULT_CHECK_REFERENCE, data=data)
        self.assertTrue(form.is_valid())

        response = form.save()
        self.mocked_connection.case.post.assert_called_with({
            'personal_details': self.CONTACT_DETAILS_DEFAULT_DATA,
            'eligibility_check': self.DEFAULT_CHECK_REFERENCE
        })
        self.mocked_connection.eligibility_check(
            self.DEFAULT_CHECK_REFERENCE
        ).patch.assert_called_with(self.EXTRA_DEFAULT_DATA)

        self.assertDictEqual(response, {
            'case': mocked_save_response
        })

    def test_fail_save_without_eligibility_check_reference(self):
        """
        The form should raise an Exception if eligibility check is not present
        when saving
        """
        data = self._get_default_post_data()
        form = ApplyForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertRaises(InconsistentStateException, form.save)

    def test_fail_save_when_not_eligible(self):
        data = self._get_default_post_data()
        form = ApplyForm(reference=self.DEFAULT_CHECK_REFERENCE, data=data)
        self.mocked_connection.eligibility_check(self.DEFAULT_CHECK_REFERENCE).\
            is_eligible().post.return_value = mocked_api.IS_ELIGIBLE_NO

        self.assertTrue(form.is_valid())
        self.assertRaises(InconsistentStateException, form.save)

    def test_fail_save_when_eligibility_unknown(self):
        data = self._get_default_post_data()
        form = ApplyForm(reference=self.DEFAULT_CHECK_REFERENCE, data=data)
        self.mocked_connection.eligibility_check(self.DEFAULT_CHECK_REFERENCE).\
            is_eligible().post.return_value = mocked_api.IS_ELIGIBLE_UNKNOWN

        self.assertTrue(form.is_valid())
        self.assertRaises(InconsistentStateException, form.save)
