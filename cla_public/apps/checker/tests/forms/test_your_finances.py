import mock

from core.testing.testcases import CLATestCase
from django.forms.formsets import formset_factory

from ...forms.your_finances import YourCapitalPropertyForm, \
    OnlyAllowExtraIfNoInitialFormSet, YourAllowancesForm, YourCapitalForm, \
    YourIncomeForm
from ...exceptions import InconsistentStateException

from ..fixtures import mocked_api


class YourCapitalFormTestCase(CLATestCase):

    all_forms = {
        'your_savings',
        'partners_savings',
    }

    partner_forms = {
        'partners_savings',
    }

    property_forms = {'your_other_properties'}

    def setUp(self):
        self.reference = '123456789'
        super(YourCapitalFormTestCase, self).setUp()
        self.mocked_connection.eligibility_check(self.reference).patch.\
            return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS

    def test_get(self):
        """
        TEST: a blank GET to the this form - all subforms should be visible
        """

        form = YourCapitalForm()
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms
        )

        self.assertSetEqual(
            set(dict(form.formset_list).keys()),
            {'property'}
        )

    def test_get_no_partner(self):
        """
        TEST: no questions about partner should be visible
        if the form was created with a has_partner=False kwarg
        """

        form = YourCapitalForm(has_partner=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms - self.partner_forms
        )

        self.assertSetEqual(
            set(dict(form.formset_list).keys()),
            {'property'}
        )

    def test_get_no_property(self):
        """
        TEST: no questions about property should be visible
        if the form was created with a has_property=False kwarg
        """

        form = YourCapitalForm(has_property=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms-self.property_forms
        )

        self.assertSetEqual(
            set(dict(form.formset_list).keys()),
            set()
        )

    def test_get_no_property_no_partner(self):
        form = YourCapitalForm(has_property=False, has_partner=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms-self.property_forms-self.partner_forms
        )

        self.assertSetEqual(
            set(dict(form.formset_list).keys()),
            set()
        )

    def test_get_has_single_new_property(self):
        form = YourCapitalForm()
        self.assertTrue(len(form.get_form_by_prefix('property').forms), 1)

    def _get_default_post_data(self):
        return {
            u'partners_savings-bank': u'100.01',
            u'partners_savings-investments': u'100.02',
            u'partners_savings-money_owed': u'100.03',
            u'partners_savings-valuable_items': u'100.04',
            u'property-0-mortgage_left': u'50000',
            u'property-0-owner': u'1',
            u'property-0-share': u'100',
            u'property-0-worth': u'100000',
            u'property-0-disputed': u'1',
            u'property-INITIAL_FORMS': u'0',
            u'property-MAX_NUM_FORMS': u'20',
            u'property-TOTAL_FORMS': u'1',
            u'your_savings-bank': u'100',
            u'your_savings-investments': u'100',
            u'your_savings-money_owed': u'100',
            u'your_savings-valuable_items': u'100'}

    def _get_default_api_post_data(self):
        return {
            "you": {
                "savings": {
                    "bank_balance": 10000,
                    "investment_balance": 10000,
                    "asset_balance": 10000,
                    "credit_balance": 10000,
                }
            },
            "property_set": [
                {
                    "share": 100, "value": 10000000, "mortgage_left": 5000000,
                    "disputed": True
                }
            ],
            "partner": {
                "savings": {
                    "bank_balance": 10001,
                    "investment_balance": 10002,
                    "asset_balance": 10004,
                    "credit_balance": 10003,
                }
            }
        }

    def test_fail_save_without_eligibility_check_reference(self):
        """
        The form should raise an Exception if eligibility check is not present
        when saving
        """
        data = self._get_default_post_data()
        form = YourCapitalForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertRaises(InconsistentStateException, form.save)

    def test_post_update(self):
        """
        TEST post update with full data, simple case
        """
        form = YourCapitalForm(reference=self.reference, data=self._get_default_post_data())

        self.assertTrue(form.get_form_by_prefix('your_savings').is_valid())
        self.assertTrue(form.get_form_by_prefix('partners_savings').is_valid())

        for f in form.get_form_by_prefix('property'):
            self.assertTrue(f.is_valid())

        response_data = form.save()
        self.assertDictEqual(response_data, {
            'eligibility_check': mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS
        })
        self.mocked_connection.eligibility_check(self.reference).patch.assert_called_with(
            self._get_default_api_post_data()
        )

    def test_fails_if_first_properties_not_filled_in(self):
        # 'property-TOTAL_FORMS' == 1 but the property #1 is not filled in
        data = {k: v for k,v in self._get_default_post_data().items() if not k.startswith('property-0') }
        data['property-TOTAL_FORMS'] = 1
        form = YourCapitalForm(reference=self.reference, data=data)

        self.assertFalse(form.is_valid())
        property_form = form.get_form_by_prefix('property')
        self.assertFalse(property_form.is_valid())
        self.assertEqual(property_form.non_form_errors(), [u'Fill in all your property details'])

    def test_fails_if_second_properties_not_filled_in(self):
        # 'property-TOTAL_FORMS' == 2 but the property #2 is not filled in
        data = dict(self._get_default_post_data())
        data['property-TOTAL_FORMS'] = 2
        form = YourCapitalForm(reference=self.reference, data=data)

        self.assertFalse(form.is_valid())
        property_form = form.get_form_by_prefix('property')
        self.assertFalse(property_form.is_valid())
        self.assertEqual(property_form.non_form_errors(), [u'Fill in all your property details'])

    def test_post_update_cleaned_data_your_savings(self):
        """
        TEST cleaned_data for your savings
        """
        form = YourCapitalForm(reference=self.reference, data=self._get_default_post_data())
        self.assertTrue(form.get_form_by_prefix('your_savings').is_valid())
        self.assertEqual(form.get_form_by_prefix('your_savings').cleaned_data['bank'], 10000)
        self.assertEqual(form.get_form_by_prefix('your_savings').cleaned_data['investments'], 10000)
        self.assertEqual(form.get_form_by_prefix('your_savings').cleaned_data['money_owed'], 10000)
        self.assertEqual(form.get_form_by_prefix('your_savings').cleaned_data['valuable_items'], 10000)

    def test_post_update_cleaned_data_partner_savings(self):
        """
        TEST cleaned_data for partner savings
        """
        form = YourCapitalForm(reference=self.reference, data=self._get_default_post_data())
        self.assertTrue(form.get_form_by_prefix('partners_savings').is_valid())
        self.assertEqual(form.get_form_by_prefix('partners_savings').cleaned_data['bank'], 10001)
        self.assertEqual(form.get_form_by_prefix('partners_savings').cleaned_data['investments'], 10002)
        self.assertEqual(form.get_form_by_prefix('partners_savings').cleaned_data['money_owed'], 10003)
        self.assertEqual(form.get_form_by_prefix('partners_savings').cleaned_data['valuable_items'], 10004)

    def test_form_validation(self):
        default_data = self._get_default_post_data()

        # only checking one, not partners_savings
        ERRORS_DATA =  [
            # your savings is mandatory
            {
                'data': {
                    'your_savings-bank': None,
                    'your_savings-investments': None,
                    'your_savings-valuable_items': None,
                    'your_savings-money_owed': None
                },
                'error': {
                    'bank': [u'This field is required.'],
                    'investments': [u'This field is required.'],
                    'valuable_items': [u'This field is required.'],
                    'money_owed': [u'This field is required.']
                }
            },
            # negative values
            {
                'data': {
                    'your_savings-bank': -1,
                    'your_savings-investments': -1,
                    'your_savings-valuable_items': -1,
                    'your_savings-money_owed': -1
                },
                'error': {
                    'bank': [u'Ensure this value is greater than or equal to 0.'],
                    'valuable_items': [u'Ensure this value is greater than or equal to 0.'],
                    'investments': [u'Ensure this value is greater than or equal to 0.'],
                    'money_owed': [u'Ensure this value is greater than or equal to 0.']
                }
            },
        ]

        for error_data in ERRORS_DATA:
            data = dict(default_data)
            data.update(error_data['data'])

            form = YourCapitalForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors['your_savings'], error_data['error'])

    def test_add_new_property(self):
        data = self._get_default_post_data()
        data['submit'] = 'add-property'
        form = YourCapitalForm(data=data)
        property_forms_before_process_action = form.form_dict()['property'].total_form_count()
        form.process_actions()
        property_forms_after_process_actions = form.form_dict()['property'].total_form_count()
        self.assertFalse(form.is_valid())
        self.assertGreater(property_forms_after_process_actions, property_forms_before_process_action)

    def test_remove_property_last(self):
        data = self._get_default_post_data()
        more_data = {
            u'property-1-mortgage_left': u'20000',
            u'property-1-owner': u'1',
            u'property-1-share': u'100',
            u'property-1-worth': u'200000',
            u'property-1-disputed': u'1',
            u'property-INITIAL_FORMS': u'0',
            u'property-MAX_NUM_FORMS': u'20',
            u'property-TOTAL_FORMS': u'2',
            u'submit': u'remove-property-1',

        }
        data.update(more_data)
        form = YourCapitalForm(data=data)
        property_forms_before_process_action = form.form_dict()['property'].total_form_count()
        form.process_actions()
        property_forms_after_process_actions = form.form_dict()['property'].total_form_count()
        self.assertTrue(form.is_valid())
        self.assertLess(property_forms_after_process_actions, property_forms_before_process_action)

    def test_remove_property_middle(self):
        data = self._get_default_post_data()
        more_data = {
            u'property-1-mortgage_left': u'20000',
            u'property-1-owner': u'1',
            u'property-1-share': u'100',
            u'property-1-worth': u'100000',
            u'property-1-disputed': u'1',
            u'property-2-mortgage_left': u'10000',
            u'property-2-owner': u'1',
            u'property-2-share': u'100',
            u'property-2-worth': u'200000',
            u'property-2-disputed': u'0',
            u'property-INITIAL_FORMS': u'0',
            u'property-MAX_NUM_FORMS': u'20',
            u'property-TOTAL_FORMS': u'3',
            u'submit': u'remove-property-1',

            }
        data.update(more_data)
        form = YourCapitalForm(data=data)
        property_forms_before_process_action = form.form_dict()['property'].total_form_count()
        form.process_actions()
        property_forms_after_process_actions = form.form_dict()['property'].total_form_count()
        self.assertTrue(form.is_valid())
        self.assertLess(property_forms_after_process_actions, property_forms_before_process_action)
        self.assertEqual(form.cleaned_data['property'][1]['worth'], int(more_data[u'property-2-worth']) * 100)

    # TEST Calculated fields

    def test_get_savings_doesnt_raise_error_if_no_partner(self):
        data = {k:v for k,v in self._get_default_post_data().items() if not k.startswith('partners')}
        form = YourCapitalForm(reference=self.reference, data=data, has_partner=False)
        self.assertTrue(form.is_valid(), form.errors)

        your_savings, partner_savings = form.get_savings(form.cleaned_data)
        self.assertDictEqual(partner_savings, {})

    def test_get_properties_doesnt_error_if_no_properties(self):
        data = {k: v for k,v in self._get_default_post_data().items() if not k.startswith('property') }
        form = YourCapitalForm(reference=self.reference, data=data, has_property=False)
        self.assertTrue(form.is_valid(), msg=form.errors)

        properties = form.get_properties(form.cleaned_data)
        self.assertListEqual(properties, [])


 # CALCULATED TESTS REDUNDANT AND TO BE REMOVED
    def test_calculated_capital_assets(self):
        form = YourCapitalForm(data=self._get_default_post_data())
        self.assertTrue(form.is_valid())
        # this should be their share of any properties
        # plus any savings
        properties_value = sum([(int(max(x['value'], 0) - x['mortgage_left'])*(x['share'] / 100.0)) for x in form.get_properties(form.cleaned_data)])
        self.assertEqual(properties_value, 5000000)
        self.assertEqual(form.total_capital_assets, 80010 + 5000000)

    def test_calculated_capital_assets_no_property(self):
        data = {k: v for k,v in self._get_default_post_data().items() if not k.startswith('property-0')}
        data['property-TOTAL_FORMS'] = 0
        form = YourCapitalForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.total_capital_assets, 80010)

    def test_calculated_capital_assets_two_property(self):
        default_data = self._get_default_post_data()
        default_data['property-TOTAL_FORMS'] = u'2'
        new_data = {k.replace('0','1'): v for k,v in default_data.items() if  k.startswith('property-0')}
        default_data.update(new_data)
        form = YourCapitalForm(data=default_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.total_capital_assets, 80010 + (5000000 * 2))


class YourCapitalPropertyFormSetSetTeseCase(CLATestCase):

    def test_no_extra_allowed_if_initial_data_supplied(self):
        YourCapitalPropertyFormSet = formset_factory(
            YourCapitalPropertyForm,
            extra=1,
            max_num=20,
            validate_max=True,
            formset=OnlyAllowExtraIfNoInitialFormSet
        )
        formset = YourCapitalPropertyFormSet(
            initial=[
                {"share": 100, "value": 100000, "mortgage_left": 50000},
                {"share": 100, "value": 100000, "mortgage_left": 50000}
            ]
        )
        self.assertEqual(formset.extra, 0)

    def test_one_extra_allowed_if_no_initial_data_supplied(self):
        YourCapitalPropertyFormSet = formset_factory(
            YourCapitalPropertyForm,
            extra=1,
            max_num=20,
            validate_max=True,
            formset=OnlyAllowExtraIfNoInitialFormSet
        )
        formset = YourCapitalPropertyFormSet()
        self.assertEqual(formset.extra, 1)


class YourIncomeFormTestCase(CLATestCase):
    all_forms = {
        'your_income',
        'partners_income',
        'dependants'
    }

    partner_forms = {
        'partners_income',
    }

    children_forms = {'dependants'}

    def setUp(self):
        super(YourIncomeFormTestCase, self).setUp()

        self.reference = '123456789'
        self.mocked_connection.eligibility_check(self.reference).\
            patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME

    def _get_default_post_data(self):
        return {
            u'your_income-earnings_0': u'222',
            u'your_income-earnings_1': u'per_month',
            u'your_income-other_income': u'333',
            u'your_income-self_employed': u'0',

            u'partners_income-earnings_0': u'444',
            u'partners_income-earnings_1': u'per_month',
            u'partners_income-other_income': u'555',
            u'partners_income-self_employed': u'1',

            u'dependants-dependants_young': u'3',
            u'dependants-dependants_old': u'2',
        }

    def _get_default_api_post_data(self):
        return {
            "you": {
                "income": {
                    "earnings":  {'interval_period': u'per_month',
                                  'per_interval_value': 22200,
                                  'per_month': 22200
                                 },
                    "other_income": 33300,
                    "self_employed": False,
                }
            },
            "partner": {
                "income": {
                    "earnings":  {'interval_period': u'per_month',
                                  'per_interval_value': 44400,
                                  'per_month': 44400
                                 },
                    "other_income": 55500,
                    "self_employed": True,
                }
            },
            "dependants_young": 3,
            "dependants_old": 2,
        }

    def test_get(self):
        """
        TEST: a blank GET to the this form - all subforms should be visible
        """

        form = YourIncomeForm()
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms
        )

    def test_get_no_partner(self):
        """
        TEST: no questions about partner should be visible
        if the form was created with a has_partner=False kwarg
        """

        form = YourIncomeForm(has_partner=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms - self.partner_forms
        )

    def test_get_no_children(self):
        """
        TEST: no questions about children should be visible
        if the form was created with a has_children=False kwarg
        """

        form = YourIncomeForm(has_children=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms - self.children_forms
        )

    def test_get_no_children_no_partner(self):
        form = YourIncomeForm(has_children=False, has_partner=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms-self.children_forms-self.partner_forms
        )

    def test_fail_save_without_eligibility_check_reference(self):
        """
        The form should raise an Exception if eligibility check is not present
        when saving
        """
        data = self._get_default_post_data()
        form = YourIncomeForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertRaises(InconsistentStateException, form.save)

    def test_post_update(self):
        """
        TEST post update with full data, simple case
        """
        form = YourIncomeForm(reference=self.reference, data=self._get_default_post_data())

        self.assertTrue(form.get_form_by_prefix('your_income').is_valid())
        self.assertTrue(form.get_form_by_prefix('partners_income').is_valid())
        self.assertTrue(form.get_form_by_prefix('dependants').is_valid())

        response_data = form.save()
        self.assertDictEqual(response_data, {
            'eligibility_check': mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME
        })
        self.mocked_connection.eligibility_check(self.reference).patch.assert_called_with(
            self._get_default_api_post_data()
        )

    def test_post_update_cleaned_data_dependants(self):
        """
        TEST cleaned_data for dependants
        """
        form = YourIncomeForm(reference=self.reference, data=self._get_default_post_data())

        self.assertTrue(form.get_form_by_prefix('dependants').is_valid())
        self.assertEqual(form.get_form_by_prefix('dependants').cleaned_data['dependants_young'], 3)
        self.assertEqual(form.get_form_by_prefix('dependants').cleaned_data['dependants_old'], 2)

    def test_post_update_cleaned_data_your_income(self):
        """
        TEST cleaned_data for your savings
        """
        form = YourIncomeForm(reference=self.reference, data=self._get_default_post_data())
        self.assertTrue(form.get_form_by_prefix('your_income').is_valid())
        earnings_dict = {'interval_period': u'per_month', 'per_interval_value': 22200, 'per_month': 22200}
        self.assertEqual(form.get_form_by_prefix('your_income').cleaned_data['earnings'], earnings_dict)
        self.assertEqual(form.get_form_by_prefix('your_income').cleaned_data['other_income'], 33300)
        self.assertEqual(form.get_form_by_prefix('your_income').cleaned_data['self_employed'], False)

    def test_post_update_cleaned_data_partner_income(self):
        """
        TEST cleaned_data for partner savings
        """
        form = YourIncomeForm(reference=self.reference, data=self._get_default_post_data())
        self.assertTrue(form.get_form_by_prefix('partners_income').is_valid())
        earnings_dict = {'interval_period': u'per_month', 'per_interval_value': 44400, 'per_month': 44400}
        self.assertEqual(form.get_form_by_prefix('partners_income').cleaned_data['earnings'], earnings_dict)
        self.assertEqual(form.get_form_by_prefix('partners_income').cleaned_data['other_income'], 55500)
        self.assertEqual(form.get_form_by_prefix('partners_income').cleaned_data['self_employed'], True)

    def test_form_validation(self):
        default_data = self._get_default_post_data()

        ERRORS_DATA =  {
            'your_income': # only checking one, not partners_income
                [
                    # your savings is mandatory
                    {
                        'data': {
                            'your_income-earnings_0': None,
                            'your_income-other_income': None,
                            'your_income-self_employed': None
                        },
                        'error': {
                            'earnings': [u'This field is required.'],
                            'other_income': [u'This field is required.'],
                            'self_employed': [u'This field is required.']
                        }
                    },
                    {
                        'data': {
                            'your_income-earnings_0': -1,
                            'your_income-other_income': -1,
                        },
                        'error': {
                            'earnings': [u'Ensure this value is greater than or equal to 0.'],
                            'other_income': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    },
                ],
        }

        for error_section_name, error_section_vals in ERRORS_DATA.items():
            for error_data in error_section_vals:
                data = dict(default_data)
                data.update(error_data['data'])

                form = YourIncomeForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertEqual(
                    form.errors[error_section_name], error_data['error']
                )


class YourAllowancesFormTestCase(CLATestCase):
    all_forms = {
        'your_allowances',
        'partners_allowances',
    }

    partner_forms = {
        'partners_allowances',
    }

    def setUp(self):
        super(YourAllowancesFormTestCase, self).setUp()

        self.reference = '123456789'
        self.mocked_connection.eligibility_check(self.reference).\
            patch.return_value = mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_ALLOWANCES

    def _get_default_post_data(self):
        return {
            u'your_allowances-mortgage': u'351',
            u'your_allowances-rent': u'352',
            u'your_allowances-tax': u'353',
            u'your_allowances-ni': u'354',
            u'your_allowances-maintenance': u'355',
            u'your_allowances-childcare': u'355.50',
            u'your_allowances-criminal_legalaid_contributions': u'356',

            u'partners_allowances-mortgage': u'451',
            u'partners_allowances-rent': u'452',
            u'partners_allowances-tax': u'453',
            u'partners_allowances-ni': u'454',
            u'partners_allowances-maintenance': u'455',
            u'partners_allowances-childcare': u'455.50',
            u'partners_allowances-criminal_legalaid_contributions': u'456',
        }

    def _get_default_api_post_data(self):
        return {
            "you": {
                "deductions": {
                    "mortgage_or_rent": 70300,
                    "income_tax_and_ni": 70700,
                    "maintenance": 35500,
                    "childcare": 35550,
                    "criminal_legalaid_contributions": 35600
                }
            },
            "partner": {
                "deductions": {
                    "mortgage_or_rent": 90300,
                    "income_tax_and_ni": 90700,
                    "maintenance": 45500,
                    "childcare": 45550,
                    "criminal_legalaid_contributions": 45600
                }
            }
        }

    def test_get(self):
        """
        TEST: a blank GET to the this form - all subforms should be visible
        """

        form = YourAllowancesForm()
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms
        )

    def test_get_no_partner(self):
        """
        TEST: no questions about partner should be visible
        if the form was created with a has_partner=False kwarg
        """

        form = YourAllowancesForm(has_partner=False)
        self.assertSetEqual(
            set(dict(form.forms_list).keys()),
            self.all_forms - self.partner_forms
        )

    def test_fail_save_without_eligibility_check_reference(self):
        """
        The form should raise an Exception if eligibility check is not present
        when saving
        """
        data = self._get_default_post_data()
        form = YourAllowancesForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertRaises(InconsistentStateException, form.save)

    def test_post_update(self):
        """
        PATCH to eligibility_check with a reference already set
        """
        post_data = self._get_default_post_data()
        form = YourAllowancesForm(reference=self.reference, data=post_data)

        self.assertTrue(form.is_valid())

        response_data = form.save()
        self.assertDictEqual(response_data, {
            'eligibility_check': mocked_api.ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_ALLOWANCES
        })

        self.mocked_connection.eligibility_check(self.reference).patch.assert_called_with(
            self._get_default_api_post_data()
        )

    def test_form_validation(self):
        default_data = self._get_default_post_data()

        ERRORS_DATA = [
            # mandatory fields
            {
                'error': {
                    u'income_tax_and_ni': [u'This field is required.'],
                    u'maintenance': [u'This field is required.'],
                    u'childcare': [u'This field is required.'],
                    u'mortgage_or_rent': [u'This field is required.'],
                    u'criminal_legalaid_contributions': [u'This field is required.'],
                },
                'data': {
                    u'income_tax_and_ni': None,
                    u'maintenance': None,
                    u'childcare': None,
                    u'mortgage_or_rent': None,
                    u'criminal_legalaid_contributions': None,
                }
            },
            # negative values
            {
                'error': {
                    u'income_tax_and_ni': [u'Ensure this value is greater than or equal to 0.'],
                    u'maintenance': [u'Ensure this value is greater than or equal to 0.'],
                    u'childcare': [u'Ensure this value is greater than or equal to 0.'],
                    u'mortgage_or_rent': [u'Ensure this value is greater than or equal to 0.'],
                    u'criminal_legalaid_contributions': [u'Ensure this value is greater than or equal to 0.'],
                },
                'data': {
                    u'income_tax_and_ni': u'-1',
                    u'maintenance': u'-1',
                    u'childcare': u'-1',
                    u'mortgage_or_rent': u'-1',
                    u'criminal_legalaid_contributions': u'-1',
                }
            },
        ]

        ERRORS_DATA =  {
            'your_allowances': # only checking one, not partners_allowances
                [
                    # your allowances is mandatory
                    {
                        'data': {
                            'your_allowances-mortgage': None,
                            'your_allowances-rent': None,
                            'your_allowances-tax': None,
                            'your_allowances-ni': None,
                            'your_allowances-maintenance': None,
                            'your_allowances-childcare': None,
                            'your_allowances-criminal_legalaid_contributions': None,
                        },
                        'error': {
                            'mortgage': [u'This field is required.'],
                            'rent': [u'This field is required.'],
                            'tax': [u'This field is required.'],
                            'ni': [u'This field is required.'],
                            'maintenance': [u'This field is required.'],
                            'childcare': [u'This field is required.'],
                            'criminal_legalaid_contributions': [u'This field is required.'],
                        }
                    },
                    {
                        'data': {
                            'your_allowances-mortgage': -1,
                            'your_allowances-rent': -1,
                            'your_allowances-tax': -1,
                            'your_allowances-ni': -1,
                            'your_allowances-maintenance': -1,
                            'your_allowances-childcare': -1,
                            'your_allowances-criminal_legalaid_contributions': -1,
                        },
                        'error': {
                            'mortgage': [u'Ensure this value is greater than or equal to 0.'],
                            'rent': [u'Ensure this value is greater than or equal to 0.'],
                            'tax': [u'Ensure this value is greater than or equal to 0.'],
                            'ni': [u'Ensure this value is greater than or equal to 0.'],
                            'maintenance': [u'Ensure this value is greater than or equal to 0.'],
                            'childcare': [u'Ensure this value is greater than or equal to 0.'],
                            'criminal_legalaid_contributions': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    },
                ],
        }

        for error_section_name, error_section_vals in ERRORS_DATA.items():
            for error_data in error_section_vals:
                data = dict(default_data)
                data.update(error_data['data'])

                form = YourAllowancesForm(reference=self.reference, data=data)
                self.assertFalse(form.is_valid())
                self.assertEqual(
                    form.errors[error_section_name], error_data['error']
                )
