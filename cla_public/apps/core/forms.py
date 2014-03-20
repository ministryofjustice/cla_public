import itertools
from django import forms
from django.forms import models
from django.forms.fields import ChoiceField
from django.utils.encoding import force_text


class CollectionChoiceIterator(object):
    def __init__(self, collection=None, pk_attr=None, label_attr=None):
        self.collection = collection
        self.pk_attr= pk_attr
        self.label_attr = label_attr

    def __iter__(self):
        for obj in self.collection:
            yield self.choice(obj)

    def __len__(self):
        return len(self.collection)

    def choice(self, obj):
        return (obj.get(self.pk_attr), obj.get(self.label_attr), obj)

class AdvancedCollectionChoiceField(ChoiceField):
    pk_attr = None
    label_attr = None
    collection = None

    def __init__(self, *args, **kwargs):
        self.collection = kwargs.pop('collection', [])
        self.pk_attr = kwargs.pop('pk_attr')
        self.label_attr = kwargs.pop('label_attr')
        super(AdvancedCollectionChoiceField, self).__init__(*args, **kwargs)

    def _get_choices(self):
        return CollectionChoiceIterator(collection=self.collection,  pk_attr=self.pk_attr, label_attr=self.label_attr)

    def valid_value(self, value):
        text_value = force_text(value)
        for k, v, d in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == force_text(k2):
                        return True
            else:
                if value == k or text_value == force_text(k):
                    return True
        return False

    choices = property(_get_choices, ChoiceField._set_choices)


class MultipleFormsForm(forms.Form):
    forms_list = ()
    formset_list = ()

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        self.forms = []
        self.formsets = []

        for prefix, form_class in self.forms_list:
            form_kwargs = dict(kwargs)
            form_kwargs.update({
                'prefix': prefix,
                'initial': initial.get(prefix, {})
            })
            form_kwargs = self.get_form_kwargs(**form_kwargs)

            form = form_class(*args, **form_kwargs)
            self.forms.append((prefix, form))

        for prefix, formset_class in self.formset_list:
            formset_kwargs = dict(kwargs)
            formset_kwargs.update({
                'prefix': prefix,
                'initial': initial.get(prefix, {})
            })

            formset = formset_class(**formset_kwargs)

            self.formsets.append((prefix, formset))


        super(MultipleFormsForm, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        return kwargs

    def is_valid(self, *args, **kwargs):
        return all(
            [form.is_valid(*args, **kwargs) for
             prefix, form in
             itertools.chain(self.forms, self.formsets)]
        )

    def get_form_by_prefix(self, prefix):
        for _prefix, form in itertools.chain(self.forms, self.formsets):
            if _prefix == prefix:
                return form
        return None

    @property
    def cleaned_data(self):
        cleaned_data = {}
        for prefix, form in self.forms:
            cleaned_data[prefix] = form.cleaned_data
        for prefix, formset in self.formsets:
            formset_cleaned_data = []
            for form in formset:
                formset_cleaned_data.append(form.cleaned_data)
            cleaned_data[prefix] = formset_cleaned_data

        return cleaned_data

    @property
    def errors(self):
        errors = {}

        for prefix, form in itertools.chain(self.forms, self.formsets):
            if form.errors:
                errors[prefix] = form.errors
        return errors

    def form_dict(self):
        form_dict = {}
        form_dict.update({k: v for k,v in self.forms})
        form_dict.update({k: v for k,v in self.formsets})
        return form_dict

