from cla_public.apps.checker.constants import PASSPORTED_BENEFITS, NASS_BENEFITS, MONEY_INTERVALS, CATEGORIES
from flask import session
from datetime import datetime


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


def set_session_data(category, question_answer_map):
    """Sets the users session data based on the answers they provided on the new frontend.

    We do not clear their session, as if they have already answered means questions these should be remembered.

    Args:
        category: str - A category key string, this should match one of legalaid_category.code
        question_answer_map: dict[str, str] - Mapping of the users questions and answers in the form of
        { "English Question Label": "English Answer Label"}

    Raises:
        ValueError - If the category is invalid
    """

    # Domestic Abuse has a category value of violence in cla_pubic, it is classed as domestic abuse on the new frontend
    # we will set it to violence for consistency.
    if category == "domestic-abuse":
        category = "violence"

    valid_categories = [category_set[0] for category_set in CATEGORIES]
    if category not in valid_categories:
        raise ValueError("Invalid Category Code")

    user_answer_as_text = u""

    session.checker["started"] = datetime.now()
    session.checker["scope_answers"] = []

    for question, answer in question_answer_map.items():
        user_answer_as_text += u"{question}: {answer}\n\n".format(question=question, answer=answer)
        session.checker["scope_answers"].append({"answer": answer, "question": question})

    session.checker["category"] = category

    if category == "violence":
        # This ensured 'Exit this page' and safe content appears on the /contact page.
        session.checker["diagnosis_previous_choices"] = ["n18"]

    session.checker["notes"] = {"user_selected": user_answer_as_text}
    return
