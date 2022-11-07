def is_float(string):
    """
    Определение является ли строка числовым значением с плавающей точкой.
    :param string: исходная строка
    :return: True - если строка является числом с плавающей точкой, False - в противном случае
    """
    try:
        float(string.replace(",", "."))
        return True
    except ValueError:
        return False


def is_int(string):
    """
    Определение является ли строка целым числовым значением.
    :param string: исходная строка
    :return: True - если строка является целым числом, False - в противном случае
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_number(string):
    """
    Определение является ли строка каким-либо числовым занчением.
    :param string: исходная строка
    :return: True - если строка является числом, False - в противном случае
    """
    if is_int(string) or is_float(string):
        return True
    return False


def merge_dicts(dict1, dict2):
    """
    Объединение содержимого двух словарей.
    :param dict1: первый словарь
    :param dict2: второй словарь
    :return: результирующий (третий) словарь
    """
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            if isinstance(dict3[key], list):
                dict3[key].append(dict1[key])
    return dict3
