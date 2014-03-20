class InconsistentStateException(Exception):
    """
    Raised when an unexpected internal state is found (e.g. contacting the API
    without an eligibility check reference)
    """
    pass
