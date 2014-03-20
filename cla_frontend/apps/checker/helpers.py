import pickle

from core.session.utils import BaseSessionData


class SessionCheckerHelper(BaseSessionData):
    SESSION_KEY = 'checker_confirmation'

    # FORMS DATA

    def store_forms_data(self, data):
        self._set('forms_data', 'forms_data', pickle.dumps(data))

    def get_forms_data(self):
        data = self._get('forms_data', 'forms_data')
        if data:
            data = pickle.loads(data)
        return data

    # ELIGIBILITY CHECK

    def store_eligibility_check_reference(self, reference):
        self._set('metadata', 'eligibility_check_reference', reference)

    def get_eligibility_check_reference(self):
        return self._get('metadata', 'eligibility_check_reference')

    # CASE

    def store_case_reference(self, reference):
        self._set('metadata', 'case_reference', reference)

    def get_case_reference(self):
        return self._get('metadata', 'case_reference')
