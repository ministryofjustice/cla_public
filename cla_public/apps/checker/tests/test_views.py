import pickle

from django.core.urlresolvers import reverse

from core.testing.testcases import CLATestCase

from ..exceptions import InconsistentStateException
from ..views import CheckerWizard

from .fixtures import mocked_api


class CheckerWizardTestCase(CLATestCase):
    def setUp(self):
        super(CheckerWizardTestCase, self).setUp()

        self.reference = '123456789'

        self.mocked_connection.category.get.return_value = mocked_api.CATEGORY_LIST

        # shortcuts
        self.mocked_eligibility_check_create = self.mocked_connection.eligibility_check.post
        self.mocked_eligibility_check_patch = self.mocked_connection.eligibility_check(self.reference).patch
        self.mocked_is_eligible_post = self.mocked_connection.eligibility_check(self.reference).is_eligible().post

        self.your_problem_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_problem'}
        )
        self.your_details_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_details'}
        )
        self.your_benefits_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_benefits'}
        )
        self.your_capital_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_capital'}
        )
        self.your_income_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_income'}
        )
        self.your_allowances_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'your_allowances'}
        )
        self.result_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'result'}
        )
        self.done_url = reverse('checker:confirmation', args=(), kwargs={})

    def _get_your_problem_post_data(self):
        return {
            'your_problem-category': ['debt'],
            'your_problem-notes': u'lorem',
            'checker_wizard-current_step': 'your_problem',
        }

    def _get_your_details_post_data(self):
        return {
            'your_details-has_partner': [1],
            'your_details-has_children': [1],
            'your_details-has_benefits': [1],
            'your_details-risk_homeless': [1],
            'your_details-older_than_sixty': [1],
            'your_details-caring_responsibilities': [1],
            'your_details-own_property': [1],
            'checker_wizard-current_step': 'your_details',
        }

    def _get_your_benefits_post_data(self):
        return {
            "checker_wizard-current_step": "your_benefits",
            'your_benefits-income_support': [1],
            "your_benefits-job_seekers": [1],
            "your_benefits-employment_allowance": [1],
            "your_benefits-universal_credit": [1],
            "your_benefits-nass_benefit": [1],
            "your_benefits-none_of_above": [1],
        }

    def _get_your_capital_post_data(self):
        return {
            "checker_wizard-current_step": "your_capital",
            "property-TOTAL_FORMS": [1],
            "property-INITIAL_FORMS": [0],
            "property-MAX_NUM_FORMS": [20],
            "property-0-worth": [100000],
            "property-0-mortgage_left": [50000],
            "property-0-owner": [1],
            "property-0-share": [100],
            "property-0-disputed": [u"1"],
            "your_other_properties-other_properties": [u"0"],
            "your_savings-bank": [100],
            "your_savings-investments": [100],
            "your_savings-valuable_items": [100],
            "your_savings-money_owed": [100],
            "partners_savings-bank": [100],
            "partners_savings-investments": [100],
            "partners_savings-valuable_items": [100],
            "partners_savings-money_owed": [100],
        }

    def _get_your_income_post_data(self):
        return {
            "checker_wizard-current_step": "your_income",
            "your_income-earnings": [100],
            "your_income-other_income": [100],
            "your_income-self_employed": [0],
            "partners_income-earnings": [100],
            "partners_income-other_income": [100],
            "partners_income-self_employed": [0],
            "dependants-dependants_old": [0],
            "dependants-dependants_young": [0],
        }

    def _get_your_allowances_post_data(self):
        return {
            'your_allowances-mortgage': [700],
            'your_allowances-rent': [700],
            'your_allowances-tax': [700],
            'your_allowances-ni': [700],
            'your_allowances-maintenance': [700],
            'your_allowances-childcare': [700],
            'your_allowances-criminal_legalaid_contributions': [700],

            'partners_allowances-mortgage': [701],
            'partners_allowances-rent': [701],
            'partners_allowances-tax': [701],
            'partners_allowances-ni': [701],
            'partners_allowances-maintenance': [701],
            'partners_allowances-childcare': [701],
            'partners_allowances-criminal_legalaid_contributions': [701],

            'checker_wizard-current_step': 'your_allowances',
        }

    def _fill_in_prev_steps(self, current_step, without_reference=False):
        self.client.get(self.your_problem_url)
        s = self.client.session

        if not without_reference:
            s['wizard_checker_wizard']['_check_reference'] = self.reference

        step_data = {}
        fillers = {
            'your_problem': self._get_your_problem_post_data,
            'your_details': self._get_your_details_post_data,
            'your_benefits': self._get_your_benefits_post_data,
            'your_capital': self._get_your_capital_post_data,
            'your_income': self._get_your_income_post_data,
            'your_allowances': self._get_your_allowances_post_data,
            'result': lambda : {}
        }
        for step in [x[0] for x in CheckerWizard.form_list]:
            if step == current_step:
                break
            step_data[step] = fillers[step]()
        s['wizard_checker_wizard'][u'step_data'] = step_data
        s.save()

    def assertStepEqual(self, response, step):
        self.assertEqual(response.context_data['wizard']['steps'].current, step)

    def test_get_start_page(self):
        """
        Redirects to the first step of the wizard.
        """
        response = self.client.get(reverse('checker:checker'))
        self.assertRedirects(response, self.your_problem_url)

##############
#
# TODO: I guess that for now we can just ignore the check in dispatch, not a
#       really deal
#
##############

    # def _test_cant_skip_steps_redirect_to_step(self, requested_step, expected_redirect_to_step):
    #     STEP_URL_MAPPER = {
    #         'your_problem': self.your_problem_url,
    #         'your_details': self.your_details_url,
    #         'your_finances': self.your_finances_url,
    #         'your_disposable_income': self.your_disposable_income_url,
    #         'result': self.result_url,
    #         'apply': self.result_url
    #     }

    #     requested_url = STEP_URL_MAPPER[requested_step]
    #     expected_redirect_to_step_url = STEP_URL_MAPPER[expected_redirect_to_step]

    #     response_get = self.client.get(requested_url)
    #     self.assertRedirects(response_get, expected_redirect_to_step_url)

    #     response_post = self.client.post(requested_url, data={})
    #     self.assertRedirects(response_post, expected_redirect_to_step_url)

    # def test_cant_skip_steps(self):
    #     """
    #     Tests that you can't get or post directly a future step
    #     """
    #     # TODO: makes tests run slow, change?
    #     steps = [x[0] for x in CheckerWizard.form_list]
    #     for index, step in enumerate(steps):
    #         self._fill_in_prev_steps(current_step=step)

    #         # test that can't get or post future steps
    #         for future_step in steps[index+1:]:
    #             self._test_cant_skip_steps_redirect_to_step(future_step, step)

    ## YOUR PROBLEM

    def test_get_your_problem(self):
        """
        TEST get your problem - context variables and step
        """
        response = self.client.get(self.your_problem_url)
        context_data = response.context_data

        choices = context_data['form'].fields['category'].choices
        self.assertTrue(len(choices), 4)
        self.assertItemsEqual([c[0] for c in choices], ['immigration','abuse','consumer','debt'])
        self.assertStepEqual(response, 'your_problem')

    def test_post_your_problem(self):
        """
        TEST post your problem - without reference
        """
        data = self._get_your_problem_post_data()

        self.mocked_eligibility_check_create.return_value = mocked_api.ELIGIBILITY_CHECK_CREATE

        response = self.client.post(self.your_problem_url, data=data)
        self.assertRedirects(response, self.your_details_url)

        self.assertEqual(self.mocked_eligibility_check_create.called, True)

    def test_update_your_problem(self):
        """
        TEST post your problem - with reference - should call patch instead of post
        """
        self._fill_in_prev_steps(current_step='your_problem')
        data = self._get_your_problem_post_data()

        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE

        response = self.client.post(self.your_problem_url, data=data)
        self.assertRedirects(response, self.your_details_url)

        self.assertEqual(self.mocked_eligibility_check_patch.called, True)

    ## YOUR DETAILS

    def test_get_your_details(self):
        self._fill_in_prev_steps(current_step='your_details')

        response = self.client.get(self.your_details_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)

        self.assertStepEqual(response, 'your_details')

    def test_post_your_details(self):
        """
        TEST post your details - without reference
        """
        self._fill_in_prev_steps(current_step='your_details', without_reference=True)

        data = self._get_your_details_post_data()

        r1 = self.client.get(self.your_details_url)

        self.mocked_eligibility_check_create.return_value = mocked_api.ELIGIBILITY_CHECK_CREATE

        response = self.client.post(self.your_details_url, data=data)
        self.assertRedirects(response, self.your_benefits_url)

        self.assertEqual(self.mocked_eligibility_check_create.called, True)

    def test_update_your_details(self):
        """
        TEST post your details - with reference
        """
        self._fill_in_prev_steps(current_step='your_details')

        data = self._get_your_details_post_data()

        r1 = self.client.get(self.your_details_url)

        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE

        response = self.client.post(self.your_details_url, data=data)
        self.assertRedirects(response, self.your_benefits_url)

        self.assertEqual(self.mocked_eligibility_check_patch.called, True)

    ## YOUR CAPITAL

    def test_get_your_capital(self):
        self._fill_in_prev_steps(current_step='your_capital')

        response = self.client.get(self.your_capital_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)
        self.assertStepEqual(response, 'your_capital')

    def test_post_your_capital_unknown_eligibility(self):
        """
        TEST post your capital - should redirect to next step because of
            the unknown eligibility
        """
        self._fill_in_prev_steps(current_step='your_capital')

        post_data = self._get_your_capital_post_data()

        r1 = self.client.get(self.your_capital_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_UNKNOWN

        response = self.client.post(self.your_capital_url, data=post_data)
        self.assertRedirects(response, self.your_income_url)

        # api called?
        self.assertEqual(self.mocked_eligibility_check_patch.called, True)
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_post_your_capital_is_eligible(self):
        """
        TEST post your capital - is_eligible returns True so redirect straight to
            result page.
        """
        self._fill_in_prev_steps(current_step='your_capital')

        post_data = self._get_your_capital_post_data()

        r1 = self.client.get(self.your_capital_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_YES

        response = self.client.post(self.your_capital_url, data=post_data)
        self.assertRedirects(response, self.result_url)

    def test_post_your_capital_is_not_eligible(self):
        """
        TEST post your capital - is_eligible returns False so redirect straight to
            result page.
        """
        self._fill_in_prev_steps(current_step='your_capital')

        post_data = self._get_your_capital_post_data()

        r1 = self.client.get(self.your_capital_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_NO

        response = self.client.post(self.your_capital_url, data=post_data)
        self.assertRedirects(response, self.result_url)

    def test_post_your_capital_with_extra_property(self):
        """
        Test that ticking yes for 'I own other properties' returns you to the same page
        with an additional property
        """
        post_data = {
            "checker_wizard-current_step": "your_capital",
            "property-TOTAL_FORMS": [1],
            "property-INITIAL_FORMS": [0],
            "property-MAX_NUM_FORMS": [20],
            "property-0-worth": [100000],
            "property-0-mortgage_left": [50000],
            "property-0-owner": [1],
            "property-0-share": [100],
            "property-0-disputed": [u"1"],
            "your_other_properties-other_properties": [u"1"],
            "your_savings-bank": [100],
            "your_savings-investments": [100],
            "your_savings-valuable_items": [100],
            "your_savings-money_owed": [100],
            "partners_savings-bank": [100],
            "partners_savings-investments": [100],
            "partners_savings-valuable_items": [100],
            "partners_savings-money_owed": [100],
        }

        self._fill_in_prev_steps(current_step='your_capital')

        r1 = self.client.get(self.your_capital_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS

        response = self.client.post(self.your_capital_url, data=post_data, follow=True)
        self.assertRedirects(response, self.your_capital_url)
        self.assertGreater(
            len(response.context_data['form'].get_form_by_prefix('property')),
            len(r1.context_data['form'].get_form_by_prefix('property'))
        )

        # api called?
        self.assertEqual(self.mocked_eligibility_check_patch.called, True)
        # shouldn't call is_eligible because the user has to add another property
        self.assertEqual(self.mocked_is_eligible_post.called, False)

    def test_post_your_capital_fails_without_reference(self):
        self._fill_in_prev_steps(current_step='your_capital', without_reference=True)

        post_data = self._get_your_capital_post_data()

        r1 = self.client.get(self.your_capital_url)
        self.assertRaises(InconsistentStateException,
            self.client.post, self.your_capital_url, data=post_data
        )

    ## YOUR INCOME

    def test_get_your_income(self):
        self._fill_in_prev_steps(current_step='your_income')

        response = self.client.get(self.your_income_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)

        self.assertStepEqual(response, 'your_income')

    def test_post_your_income_unknown_eligibility(self):
        """
        TEST post your income - should redirect to next step because of
            the unknown eligibility
        """
        self._fill_in_prev_steps(current_step='your_income')

        post_data = self._get_your_income_post_data()

        r1 = self.client.get(self.your_income_url)

        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_UNKNOWN
        response = self.client.post(self.your_income_url, data=post_data)
        self.assertRedirects(response, self.your_allowances_url)

        # api called?
        self.assertEqual(self.mocked_eligibility_check_patch.called, True)
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_post_your_income_is_eligible(self):
        """
        TEST post your income - is_eligible returns True so redirect straight to
            result page.
        """
        self._fill_in_prev_steps(current_step='your_income')

        post_data = self._get_your_income_post_data()

        r1 = self.client.get(self.your_income_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_YES

        response = self.client.post(self.your_income_url, data=post_data)
        self.assertRedirects(response, self.result_url)

    def test_post_your_income_is_not_eligible(self):
        """
        TEST post your income - is_eligible returns False so redirect straight to
            result page.
        """
        self._fill_in_prev_steps(current_step='your_income')

        post_data = self._get_your_income_post_data()

        r1 = self.client.get(self.your_income_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_NO

        response = self.client.post(self.your_income_url, data=post_data)
        self.assertRedirects(response, self.result_url)

    def test_post_your_income_fails_without_reference(self):
        self._fill_in_prev_steps(current_step='your_income', without_reference=True)

        post_data = self._get_your_income_post_data()

        r1 = self.client.get(self.your_income_url)
        self.assertRaises(InconsistentStateException,
            self.client.post, self.your_income_url, data=post_data
        )

    ## YOUR ALLOWANCES

    def test_get_your_allowances(self):
        self._fill_in_prev_steps(current_step='your_allowances')

        response = self.client.get(self.your_allowances_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)
        self.assertStepEqual(response, 'your_allowances')

    def test_post_your_allowances(self):
        self._fill_in_prev_steps(current_step='your_allowances')

        post_data = self._get_your_allowances_post_data()

        r1 = self.client.get(self.your_allowances_url)

        # mock api responses
        self.mocked_eligibility_check_patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_ALLOWANCES
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_YES

        response = self.client.post(self.your_allowances_url, data=post_data)
        self.assertRedirects(response, self.result_url)

        # api called?
        self.assertEqual(self.mocked_eligibility_check_patch.called, True)
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    ## YOUR RESULT

    def test_get_result_is_eligible(self):
        self._fill_in_prev_steps(current_step='result')

        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_YES

        response = self.client.get(self.result_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)

        self.assertStepEqual(response, 'result')
        self.assertEqual(response.context_data['is_eligible'], True)

        # api called?
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_get_result_is_not_eligible(self):
        self._fill_in_prev_steps(current_step='result')

        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_NO

        response = self.client.get(self.result_url)
        self.assertTrue('sessionid' in response.cookies)
        self.assertEqual(response.status_code, 200)

        self.assertStepEqual(response, 'result')
        self.assertEqual(response.context_data['is_eligible'], False)

        # api called?
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_get_result_unknown_eligibility(self):
        """
        TEST unknown eligibility => error
        """
        self._fill_in_prev_steps(current_step='result')

        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_UNKNOWN

        response = self.client.get(self.result_url, follow=True)
        self.assertRedirects(response, self.your_problem_url)


        # api called?
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_post_result_fails_without_reference(self):
        self._fill_in_prev_steps(current_step='result', without_reference=True)

        data = {
            "checker_wizard-current_step": "result",
            "contact_details-title": 'mr',
            "contact_details-full_name": 'John Doe',
            "contact_details-postcode": 'SW1H 9AJ',
            "contact_details-street": '102 Petty France',
            "contact_details-town": 'London',
            "contact_details-mobile_phone": '0123456789',
            "contact_details-home_phone": '9876543210',
        }

        response = self.client.get(self.result_url, follow=True)
        self.assertRedirects(response, self.your_problem_url)


    def test_post_result_fails_if_not_eligible(self):
        """
        TEST cannot apply if not eligible
        """
        self._fill_in_prev_steps(current_step='result')

        data = {
            "checker_wizard-current_step": "result",
            "contact_details-title": 'mr',
            "contact_details-full_name": 'John Doe',
            "contact_details-postcode": 'SW1H 9AJ',
            "contact_details-street": '102 Petty France',
            "contact_details-town": 'London',
            "contact_details-mobile_phone": '0123456789',
            "contact_details-home_phone": '9876543210',
        }
        r1 = self.client.get(self.result_url)

        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_NO
        self.assertRaises(
            InconsistentStateException, self.client.post,
            self.result_url, data=data
        )

        # api called?
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_post_apply_fails_if_unknown_eligibility(self):
        """
        TEST cannot apply if unknown eligibility
        """
        self._fill_in_prev_steps(current_step='result')

        data = {
            "checker_wizard-current_step": "result",
            "contact_details-title": 'mr',
            "contact_details-full_name": 'John Doe',
            "contact_details-postcode": 'SW1H 9AJ',
            "contact_details-street": '102 Petty France',
            "contact_details-town": 'London',
            "contact_details-mobile_phone": '0123456789',
            "contact_details-home_phone": '9876543210',
        }
        r1 = self.client.get(self.result_url)

        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_UNKNOWN
        self.assertRaises(
            InconsistentStateException, self.client.post,
            self.result_url, data=data
        )

        # api called?
        self.assertEqual(self.mocked_is_eligible_post.called, True)

    def test_post_apply_success(self):
        self._fill_in_prev_steps(current_step='result')

        data = {
            "checker_wizard-current_step": "result",
            "contact_details-title": 'mr',
            "contact_details-full_name": 'John Doe',
            "contact_details-postcode": 'SW1H 9AJ',
            "contact_details-street": '102 Petty France',
            "contact_details-town": 'London',
            "contact_details-mobile_phone": '0123456789',
            "contact_details-home_phone": '9876543210',
        }
        r1 = self.client.get(self.result_url)

        self.mocked_connection.case.post.return_value = mocked_api.ELIGIBILITY_CHECK_CREATE_CASE
        self.mocked_is_eligible_post.return_value = mocked_api.IS_ELIGIBLE_YES

        response = self.client.post(self.result_url, data=data, follow=True)
        self.assertRedirects(response, self.done_url)

        # check that case and eligibility check references are in the session
        s = self.client.session
        self.assertItemsEqual(s['checker_confirmation'].keys(), ['forms_data', 'metadata'])
        self.assertDictEqual(
            s['checker_confirmation']['metadata'],
            {u'case_reference': u'LA-2954-3453', u'eligibility_check_reference': self.reference}
        )

        # api called?
        self.assertEqual(self.mocked_connection.case.post.called, True)
        self.assertEqual(self.mocked_is_eligible_post.called, True)


class ConfirmationViewTestCase(CLATestCase):
    def setUp(self):
        super(ConfirmationViewTestCase, self).setUp()

        self.url = reverse('checker:confirmation', args=(), kwargs={})

    def test_get_success(self):
        response = self.client.get(reverse('checker:checker', args=(), kwargs={}))

        # mock session data
        s = self.client.session
        mocked_data = {
            'forms_data': {
                'forms_data': pickle.dumps({
                    'category': 1
                })
            },
            'metadata': {
                'eligibility_check_reference': 123456789,
                'case_reference': 'LA-2954-3453'
            }
        }
        s['checker_confirmation'] = mocked_data
        s.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.context_data['history_data'], {
            'category': 1
        })
        self.assertEqual(
            response.context_data['case_reference'],
            mocked_data['metadata']['case_reference']
        )

    def test_get_success_then_back_button(self):
        """
        If the user pressed the back button after the confirmation page
        a redirect should take them back to the first form.
        """

        response = self.client.get(reverse('checker:checker', args=(), kwargs={}))

        # mock session data
        s = self.client.session
        mocked_data = {
            'forms_data': {
                'forms_data': pickle.dumps({
                    'category': 1
                })
            },
            'metadata': {
                'eligibility_check_reference': 123456789,
                'case_reference': 'LA-2954-3453'
            }
        }
        s['checker_confirmation'] = mocked_data
        s.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        result_url = reverse(
            'checker:checker_step', args=(), kwargs={'step': 'result'}
        )

        response = self.client.get(result_url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_404_session_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
