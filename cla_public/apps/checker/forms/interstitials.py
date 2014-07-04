from django import forms

from .base import CheckerWizardMixin


class NullForm(CheckerWizardMixin, forms.Form):
    def save(self):
        if not self.reference:
            response = self.connection.eligibility_check.post()
        else:
            response = self.connection.eligibility_check(self.reference).get()

        return {
            'eligibility_check': response
        }


class YourFinancesNullForm(NullForm):
    form_tag = 'your_finances_interstitial'
