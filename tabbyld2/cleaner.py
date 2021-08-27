import ftfy
import json


def remove_multiple_spaces(text):
    """
    Удаление множественных пробелов в строке.
    :param text: исходный текст
    :return: текст с удаленными множественными пробелами
    """
    new_text = ' '.join(text.split())

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


def clean(file_path):
    """
    Очистка данных в json-файле исходной таблицы. Очищаются ключи и их значения.
    :param file_path: полный путь к json-файлу исходной таблицы
    :return: очищенные данные в виде словаря
    """
    result_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            source_json_data = json.load(fp)
            for item in source_json_data:
                result_item = {}
                for key, mention in item.items():
                    if not isinstance(mention, str):
                        mention = str(mention)
                    # Исправления битых символов Юникода и тегов HTML
                    clean_key = ftfy.fix_encoding(key)
                    clean_key = ftfy.fix_text(clean_key)
                    clean_mention = ftfy.fix_encoding(mention)
                    clean_mention = ftfy.fix_text(clean_mention)
                    # Удаление "мусорных" символов
                    # clean_key = remove_garbage_characters(clean_key)
                    clean_mention = remove_garbage_characters(clean_mention)
                    # Удаление множественных пробелов
                    clean_key = remove_multiple_spaces(clean_key)
                    clean_mention = remove_multiple_spaces(clean_mention)
                    # Сохранение результата очистки
                    result_item[clean_key] = clean_mention
                result_list.append(result_item)
    except json.decoder.JSONDecodeError:
        print("Ошибка декодирования исходного json-файла!")

    return result_list
