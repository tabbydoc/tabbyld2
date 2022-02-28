import ftfy


def remove_multiple_spaces(text):
    """
    Удаление множественных пробелов в строке.
    :param text: исходный текст
    :return: текст с удаленными множественными пробелами
    """
    new_text = " ".join(text.split())

    return new_text


def check_letter_and_digit_existence(text):
    """
    Проверка существования в исходном тексте (строке) букв и(или) цифр.
    :param text: исходный текст
    :return: флаг, показывающий отсутствие букв и цифр в строке
    """
    exist_letter = True if any(map(str.isalpha, text)) else False
    exist_digit = True if any(map(str.isdigit, text)) else False

    return True if not exist_letter and not exist_digit else False


def remove_garbage_characters(text):
    """
    Удаление "мусорных" символов в строке.
    :param text: исходный текст
    :return: текст с удаленными "мусорными" символами
    """
    # Удаление "мусорных" символов в строке, которая не содержит буквы или цифры
    if check_letter_and_digit_existence(text):
        text = ""

    new_text = text
    if text:
        # Удаление "мусорных" символов в строке
        # for symbol in symbols:
        #     new_text = new_text.replace(symbol, "")
        # Удаление "мусорных" символов в строке, которые отделены пробелами
        word_list = text.split()
        new_text = ""
        for word in word_list:
            if not check_letter_and_digit_existence(word) and word:
                if new_text:
                    new_text += " " + word
                else:
                    new_text = word

    return new_text


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
