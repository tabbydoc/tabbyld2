import ftfy


def remove_multiple_spaces(text):
    """
    Remove multiple spaces in a source text.
    :param text: a source text
    :return: text with multiple spaces removed
    """
    return " ".join(text.split())


def check_letter_and_digit_existence(text):
    """
    Check existence of letters and (or) numbers in a source text.
    :param text: a source text
    :return: flag to indicate letters and numbers absence in a source text
    """
    exist_letter = True if any(map(str.isalpha, text)) else False
    exist_digit = True if any(map(str.isdigit, text)) else False
    return True if not exist_letter and not exist_digit else False


def remove_garbage_characters(text):
    """
    Remove "garbage" characters in a source text.
    :param text: a source text
    :return: text with garbage characters removed
    """
    if check_letter_and_digit_existence(text):
        text = ""
    new_text = text
    if text:
        # for symbol in symbols:
        #     new_text = new_text.replace(symbol, "")
        word_list = text.split()
        new_text = ""
        for word in word_list:
            if not check_letter_and_digit_existence(word) and word:
                new_text += " " + word if new_text else word
    return new_text


def fix_text(text):
    """
    Fix broken Unicode characters and HTML tags in a source text.
    :param text: a source text
    :return: corrected text
    """
    return ftfy.fix_text(ftfy.fix_encoding(str(text)))
