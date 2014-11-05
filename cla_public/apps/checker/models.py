from cla_public.apps.checker.constants import F2F_CATEGORIES, NO, \
    PASSPORTED_BENEFITS, YES


class UserStatus(dict):
    "Store the results of each form submission, namespaced by form class name"

    def update(self, form):
        ns = lambda key: '{namespace}.{key}'.format(
            namespace=form.__class__.__name__,
            key=key)
        for (key, val) in form.data.iteritems():
            self[ns(key)] = val

    @property
    def needs_face_to_face(self):
        return self.get('ProblemForm.categories') in F2F_CATEGORIES

    @property
    def has_savings(self):
        return self.get('AboutYouForm.have_savings', NO) == YES

    @property
    def owns_property(self):
        return self.get('AboutYouForm.own_property', NO) == YES

    @property
    def is_on_benefits(self):
        return self.get('AboutYouForm.on_benefits', NO) == YES

    @property
    def is_on_passported_benefits(self):
        benefits = set(self.get('YourBenefitsForm.benefits', []))
        return bool(benefits.intersection(PASSPORTED_BENEFITS))

    @property
    def has_tax_credits(self):
        has_children = self.get('AboutYouForm.have_children', NO) == YES
        is_carer = self.get('AboutYouForm.have_dependants', NO) == YES
        benefits = set(self.get('YourBenefitsForm.benefits', []))
        other_benefits = bool(benefits.difference(PASSPORTED_BENEFITS))
        return has_children or is_carer or other_benefits
