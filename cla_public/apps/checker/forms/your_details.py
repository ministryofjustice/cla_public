from django import forms
from django.utils.translation import ugettext as _

from ..fields import RadioBooleanField

from .base import CheckerWizardMixin


class YourDetailsForm(CheckerWizardMixin, forms.Form):
    form_tag = 'your_details'

    has_partner = RadioBooleanField(
        required=True, label=_(u'Do you have a partner?')
    )

    has_benefits = RadioBooleanField(
        required=True, label=_(u''.join([
            u"Are you or your partner on Income Support, "
            u"Income Based Jobseeker's Allowance, Income Based Employment"
            u" and Support Allowance or Guarantee Credit?"
        ]))
    )

    has_children = RadioBooleanField(
        required=True, label=_(u'Do you have children?')
    )

    caring_responsibilities = RadioBooleanField(
        required=True, label=_(u'Do you any other caring responsibilities?')
    )

    own_property = RadioBooleanField(
        required=True, label=_(u'Do you or your partner own a property?')
    )

    risk_homeless = RadioBooleanField(
        required=True, label=_(u'Are you are risk of becoming homeless?')
    )

    older_than_sixty = RadioBooleanField(
        required=True, label=_(u'Are you or your partner aged 60 or over?')
    )

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        post_data = {
            'is_you_or_your_partner_over_60': data['older_than_sixty'],
            'on_passported_benefits': data['has_benefits'],
            'has_partner': data['has_partner'],
        }
        if not self.reference:
            response = self.connection.eligibility_check.post(post_data)
        else:
            response = self.connection.eligibility_check(self.reference).patch(post_data)

        return {
            'eligibility_check': response
        }
