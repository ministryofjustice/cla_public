from django import forms
from django.utils.translation import ugettext as _

from ..fields import RadioBooleanField

from .base import CheckerWizardMixin


class YourDetailsForm(CheckerWizardMixin, forms.Form):
    form_tag = 'your_details'

    has_partner = RadioBooleanField(
        required=True, label=_(u'Do you have a partner?'), help_text=_(u'<p>Legal aid is calculated on both you and your partner\'s money. A \'partner\' is a person you\'re married to or a person you live with as if you\'re married</p>')
    )

    has_benefits = RadioBooleanField(
        required=True, label=_(u'Are you or your partner on any benefits?'), help_text=_(u'<p>Legal aid is based on how much money you have so any benefits you get must be taken into account</p>')
    )

    has_children = RadioBooleanField(
        required=True, label=_(u'Do you have children?'), help_text=_(u'<p>Your childcare costs will be taken into account provided you can give the right evidence</p>')
    )

    caring_responsibilities = RadioBooleanField(
        required=True, label=_(u'Do you any other caring responsibilities?'), help_text=_(u'<p>Other care costs will be taken into account provided you can give the right evidence</p>')
    )

    own_property = RadioBooleanField(
        required=True, label=_(u'Do you or your partner own a property?'), help_text=_(u'<p>Legal aid is based on how much money you have. That means any property you own must be considered, even if you don\'t live in it. Your \'home\' is where you live as your only or main residence and includes caravans, houseboats or other vehicles</p>')
    )

    risk_homeless = RadioBooleanField(
        required=True, label=_(u'Are you at immediate risk of losing your home or becoming homeless?'), help_text=_(u'<p>Legal aid is generally available if you are at immediate risk of becoming homeless. Your \'home\' is where you live as your only or main residence and includes caravans, houseboats or other vehicles</p>')
    )

    older_than_sixty = RadioBooleanField(
        required=True, label=_(u'Are you or your partner aged 60 or over?')
    )

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        post_data = {
            'is_you_or_your_partner_over_60': data['older_than_sixty'],
            'has_partner': data['has_partner'],
        }
        if not self.reference:
            response = self.connection.eligibility_check.post(post_data)
        else:
            response = self.connection.eligibility_check(self.reference).patch(post_data)

        return {
            'eligibility_check': response
        }
