def check_categories(session, categories_list):
    if "diagnosis_previous_choices" in session.checker:
        for category in categories_list:
            if category in session.checker["diagnosis_previous_choices"]:
                return True
    return False
