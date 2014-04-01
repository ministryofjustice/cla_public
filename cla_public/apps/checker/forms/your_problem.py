from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from core.forms import AdvancedCollectionChoiceField
from .base import CheckerWizardMixin


class YourProblemForm(CheckerWizardMixin, forms.Form):
    """
    Gets the problem choices from the backend API.
    """
    form_tag = 'your_problem'

    your_problem_notes = forms.CharField(
        required=False, max_length=500,
        label=_(u'Please give us any additional details about your problem that may be relevant'),
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 80})
    )

    category = AdvancedCollectionChoiceField(
        collection=[],
        pk_attr=u'code',
        label_attr=u'name',
        label=_(u'Is your problem about?'),
        widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        super(YourProblemForm, self).__init__(*args, **kwargs)

        self._categories = self.connection.category.get()

        def get_category_choice(category):
            code = category['code']
            label = category['name']
            if category['description']:
                label = mark_safe(u'%s <br> <p class="bs-callout bs-callout-warning">%s</p>' % (label, category['description']))
            return (code, label)
        self.fields['category'].choices = [get_category_choice(cat) for cat in self._categories]


        self.fields['category'].collection = self._categories

    def _get_category_by_code(self, code):
        for cat in self._categories:
            if code == str(cat['code']):
                return cat
        return None

    def clean(self, *args, **kwargs):
        cleaned_data = super(YourProblemForm, self).clean(*args, **kwargs)

        if self._errors: # skip immediately
            return cleaned_data

        category = cleaned_data.get('category')
        if category:
            categoryData = self._get_category_by_code(category)
            cleaned_data['category_name'] = categoryData['name']

        return cleaned_data

    def save(self):
        data = {
            'category': self.cleaned_data.get('category'),
            'your_problem_notes': self.cleaned_data.get('your_problem_notes', '')
        }

        if not self.reference:
            response = self.connection.eligibility_check.post(data)
        else:
            response = self.connection.eligibility_check(self.reference).patch(data)

        return {
            'eligibility_check': response
        }
