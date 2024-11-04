from cla_public.apps.checker.constants import PASSPORTED_BENEFITS, NASS_BENEFITS, MONEY_INTERVALS, CATEGORIES
from flask import session
from datetime import datetime
from cla_common.constants import DIAGNOSIS_SCOPE


def passported(benefits):
    return bool(set(benefits).intersection(PASSPORTED_BENEFITS))


def nass(benefits):
    if benefits:
        return bool(set(benefits).intersection(NASS_BENEFITS))
    return False


def money_intervals_except(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key not in fields]


def money_intervals(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key in fields]


def category_option_from_name(category_name):
    def requested(category_tuple):
        return category_tuple[1] == category_name

    return next(iter(filter(requested, CATEGORIES)), (None, None, None))


def set_session_data(category, question_answer_map, outcome=DIAGNOSIS_SCOPE.UNKNOWN, harm_flag=False):
    """Sets the users session data based on the answers they provided on the new frontend.

    We do not clear their session, as if they have already answered means questions these should be remembered.

    Args:
        category: str - A category key string, this should match one of legalaid_category.code
        question_answer_map: List[dict[str, str]] - Mapping of the users questions and answers in the form of
        [{ "question": "English Question Label", "answer", English Answer Label"}]
        outcome: str (DIAGNOSIS_SCOPE) - The outcome of the users scope diagnosis, E.g. DIAGNOSIS_SCOPE.INSCOPE
        harm_flag: bool - If the user is at immediate risk of harm

    Raises:
        ValueError - If the category is invalid
    """

    # Domestic Abuse has a category value of violence in cla_public, it is classed as domestic abuse on the new frontend
    # we will set it to violence for consistency.
    if category == "domestic-abuse":
        category = "violence"

    valid_categories = [category_set[0] for category_set in CATEGORIES]
    if category not in valid_categories:
        raise ValueError("Invalid Category Code")

    user_answer_as_text = u""

    session.checker["started"] = datetime.now()
    session.checker["scope_answers"] = []
    session.checker["notes"] = {}

    if harm_flag:
        session.checker["notes"][u"Public Diagnosis note"] = u"User is at immediate risk of harm"

    for question_answer_pair in question_answer_map:
        question = question_answer_pair["question"]
        answer = question_answer_pair["answer"]
        user_answer_as_text += u"{question}: {answer}\n\n".format(question=question, answer=answer)
        session.checker["scope_answers"].append({"answer": answer, "question": question})

    user_answer_as_text += u"Outcome: {outcome}".format(outcome=DIAGNOSIS_SCOPE.CHOICES_DICT[outcome])

    session.checker["category"] = category

    if category == "violence":
        # This ensured 'Exit this page' and safe content appears on the /contact page.
        session.checker["diagnosis_previous_choices"] = ["n18"]

    session.checker["notes"][u"User selected"] = user_answer_as_text
    return
