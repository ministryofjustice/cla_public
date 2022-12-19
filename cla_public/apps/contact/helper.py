def append_default_option_to_list(append_list, list_options):
    """Append a default non selectable message to a HTML select option"""
    # append to index 0
    return append_list.insert(0, list_options[0])
