import ftfy


def remove_multiple_spaces(text):
    """
    Удаление множественных пробелов в строке.
    :param text: исходный текст
    :return: текст с удаленными множественными пробелами
    """
    new_text = " ".join(text.split())

    return new_text


def remove_garbage_characters(text):
    """
    Удаление "мусорных" символов в строке, которая не содержит буквы или цифры.
    :param text: исходный текст
    :return: текст с удаленными "мусорными" символами
    """
    letter_exist = False
    if any(map(str.isalpha, text)):
        letter_exist = True
    digit_exist = False
    if any(map(str.isdigit, text)):
        digit_exist = True
    if letter_exist is False and digit_exist is False:
        text = ""
    # if text != "":
    #     symbols = ["?", "!", "@", "#", "$", "%", "^", "&", "*", "+", "=", "{", "}", "[", "]", ":", ";" "<", ">"]
    #     new_text = text
    #     for symbol in symbols:
    #         new_text = new_text.replace(symbol, "")

    return text


def fix_text(value):
    """
    Исправления битых символов Юникода и тегов HTML в исходном значении (строке).
    :param value: исходное значение (строка)
    :return: исправленное текстовое значение (строка)
    """
    text = str(value)
    cleared_text = ftfy.fix_encoding(text)
    cleared_text = ftfy.fix_text(cleared_text)

    return cleared_text
