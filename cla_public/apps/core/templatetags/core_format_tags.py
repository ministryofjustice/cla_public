from django import template
from num2words import num2words

register = template.Library()

@register.filter()
def ordinal_from_count(count, total):
    if total == 1:
        return ""
    # hard coded to English for now, not sure how we'd handle Welsh
    return num2words(count, ordinal=True, lang='en_GB')