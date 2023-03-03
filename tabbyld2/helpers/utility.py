def is_float(string: str) -> bool:
    """
    Check a string for a real number
    :param string: a source string
    :return: True if a source string is a float, False otherwise
    """
    try:
        float(string.replace(",", "."))
        return True
    except ValueError:
        return False


def is_int(string: str) -> bool:
    """
    Check a string for an integer numeric value
    :param string: a source string
    :return: True if a source string is an integer numeric value, False otherwise
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_number(string: str) -> bool:
    """
    Check a string for a numeric value (float or integer)
    :param string: a source string
    :return: True if a source string is a numeric value, False otherwise
    """
    return True if is_int(string) or is_float(string) else False


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Combine contents of two dictionaries
    :param dict1: a first dict
    :param dict2: a second dict
    :return: third resulting dict
    """
    dict3 = {**dict1, **dict2}
    for key in dict3.keys():
        if key in dict1 and key in dict2 and isinstance(dict3[key], list):
            dict3[key].append(dict1[key])
    return dict3
