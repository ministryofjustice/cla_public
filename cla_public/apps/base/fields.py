# -*- coding: utf-8 -*-
"Custom form fields"

from wtforms import widgets, SelectMultipleField

class MultiRadioField(SelectMultipleField):
    """
    A multiple-select, except displays a list of radio buttons.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()
