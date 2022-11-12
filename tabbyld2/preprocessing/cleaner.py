import ftfy
from typing import Any


def remove_multiple_spaces(text: str) -> str:
    """
    Remove multiple spaces in a source text.
    :param text: a source text
    :return: text with multiple spaces removed
    """
    return " ".join(text.split())


def check_letter_and_digit_existence(text: Any) -> bool:
    """
    Check existence of letters and (or) numbers in a source text.
    :param text: a source text
    :return: flag to indicate letters and numbers existence in a source text
    """
    exist_letter = True if any(map(str.isalpha, text)) else False
    exist_digit = True if any(map(str.isdigit, text)) else False
    return True if exist_letter or exist_digit else False


def remove_garbage_characters(text: Any) -> str:
    """
    Remove "garbage" characters in a source text.
    :param text: a source text
    :return: text with garbage characters removed
    """
    new_text = ""
    if check_letter_and_digit_existence(text):
        for word in text.split():
            if check_letter_and_digit_existence(word) and word:
                new_text += " " + word if new_text else word
    return new_text


def fix_text(text: Any) -> str:
    """
    Fix broken Unicode characters and HTML tags in a source text.
    :param text: a source text
    :return: corrected text
    """
    return ftfy.fix_text(ftfy.fix_encoding(str(text)))
