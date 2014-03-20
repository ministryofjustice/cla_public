from ..exceptions import InconsistentStateException

from api.client import connection


class CheckerWizardMixin(object):
    form_tag = ''

    def _prepare_for_init(self, kwargs):
        # pop these from kwargs
        self.reference = kwargs.pop('reference', None)

    def __init__(self, *args, **kwargs):
        self._prepare_for_init(kwargs)
        self.connection = connection
        super(CheckerWizardMixin, self).__init__(*args, **kwargs)

    def save(self):
        raise NotImplementedError()

    def get_context_data(self):
        return {}

    def check_that_reference_exists(self):
        if not self.reference:
            raise InconsistentStateException(
                'Eligibility Reference cannot be None'
            )


class EligibilityMixin(object):
    ELIGIBILITY_YES = 'yes'
    ELIGIBILITY_NO = 'no'
    ELIGIBILITY_UNKNOWN = 'unknown'

    @property
    def eligibility(self):
        if not hasattr(self, '_eligibility'):
            response = connection.eligibility_check(self.reference).is_eligible().post()
            self._eligibility = response['is_eligible']
        return self._eligibility

    def is_eligible(self):
        if self.is_eligibility_unknown():
            raise InconsistentStateException(u'Eligibility unknown')
        return self.eligibility == self.ELIGIBILITY_YES

    def is_eligibility_unknown(self):
        return self.eligibility == self.ELIGIBILITY_UNKNOWN
