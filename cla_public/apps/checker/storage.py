from django.contrib.formtools.wizard.storage.session import SessionStorage


class CheckerSessionStorage(SessionStorage):
    def init_data(self):
        super(CheckerSessionStorage, self).init_data()
        self.data['_check_reference'] = None
        self.data['_case_reference'] = None

    def set_eligibility_check_reference(self, reference):
        if not self.data.get('_check_reference'):
            self.data['_check_reference'] = reference

    def set_case_reference(self, reference):
        if not self.data.get('_case_reference'):
            self.data['_case_reference'] = reference

    def get_eligibility_check_reference(self):
        return self.data.get('_check_reference')

    def get_case_reference(self):
        return self.data.get('_case_reference')
