from django import forms
from django.utils.translation import ugettext as _

from .base import CheckerWizardMixin

class YourBenefitsForm(CheckerWizardMixin, forms.Form):

    form_tag = 'your_benefits'

    income_support = forms.BooleanField(
           label=_(u'Income Support'), required=False
    )

    job_seekers = forms.BooleanField(
           label=_(u'Income-Based Job Seeker\'s Allowance'), required=False
    )

    employment_allowance = forms.BooleanField(
           label=_(u'Income-Related Employment and Support Allowance'), required=False
    )

    universal_credit = forms.BooleanField(
           label=_(u'Guarantee Credit or Universal Credit'), required=False
    )

    nass_benefit = forms.BooleanField(
           label=_(u'immigration/asylum'), required=False
    )

    none_of_above = forms.BooleanField(
           label=_(u'None of the above'), required=False
    )

    @staticmethod
    def ask_about_benefits(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step('your_details') or {}
        return cleaned_data.get('has_benefits', True)

    def clean(self):
        cleaned_data = super(YourBenefitsForm, self).clean()
        none_of_above = cleaned_data.get("none_of_above")
        income_support = cleaned_data.get("income_support")
        job_seekers = cleaned_data.get("job_seekers")
        employment_allowance = cleaned_data.get("employment_allowance")
        universal_credit = cleaned_data.get("universal_credit")
        nass_benefit = cleaned_data.get("nass_benefit")
        
        cleaned_data['passport_benefit'] = income_support or job_seekers \
                                or employment_allowance or universal_credit

        if none_of_above and (nass_benefit or cleaned_data['passport_benefit']):
            raise forms.ValidationError(_('None and something selected'))

        return cleaned_data

    def save(self, *args, **kwargs):

        post_data = {
            'on_passported_benefits': self.cleaned_data['passport_benefit'],
            'on_nass_benefits' : self.cleaned_data['nass_benefit'],
        }
        if not self.reference:
            response = self.connection.eligibility_check.post(post_data)
        else:
            response = self.connection.eligibility_check(self.reference).patch(post_data)

        return {
            'eligibility_check': response
        }
