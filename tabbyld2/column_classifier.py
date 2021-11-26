import re
import stanza
import operator
import collections
from math import sqrt
from collections import defaultdict

# Named Entities from OntoNotes package:
PERSON = "PERSON"  # People, including fictional
NORP = "NORP"  # Nationalities or religious or political groups
FACILITY = "FACILITY"  # Buildings, airports, highways, bridges, etc.
ORGANIZATION = "ORG"  # Companies, agencies, institutions, etc.
GPE = "GPE"  # Countries, cities, states
LOCATION = "LOC"  # Non-GPE locations, mountain ranges, bodies of water
PRODUCT = "PRODUCT"  # Vehicles, weapons, foods, etc. (Not services)
EVENT = "EVENT"  # Named hurricanes, battles, wars, sports events, etc.
ART_WORK = "WORK OF ART"  # Titles of books, songs, etc.
LAW = "LAW"  # Named documents made into laws
NONE = "NONE"  # NER result is empty

# All named Entity tag list
NAMED_ENTITY_TAGS = [PERSON, NORP, FACILITY, ORGANIZATION, GPE, LOCATION, PRODUCT, EVENT, ART_WORK, LAW, NONE]

# Literal types from OntoNotes package:
DATE = "DATE"  # Absolute or relative dates or periods
TIME = "TIME"  # Times smaller than a day
PERCENT = "PERCENT"  # Percentage (including "%")
MONEY = "MONEY"  # Monetary values, including unit
QUANTITY = "QUANTITY"  # Measurements, as of weight or distance
ORDINAL = "ORDINAL"  # "first", "second", etc.
CARDINAL = "CARDINAL"  # Numerals that do not fall under another type
# Another literal types:
POSITIVE_INTEGER = "POSITIVE INTEGER"  # Positive integer
NEGATIVE_INTEGER = "NEGATIVE INTEGER"  # Negative integer
FLOAT = "FLOAT"  # Float
BOOLEAN = "BOOLEAN"  # true or false
MAIL = "MAIL"  # Mail address
EMAIL = "EMAIL"  # Email address
ISSN = "ISSN"  # ISSN
ISBN = "ISBN"  # ISBN
IP_ADDRESS_V4 = "IP V4"  # IP address for 4 version
BANK_CARD = "BANK CARD"  # Bank card number
COORDINATES = "COORDINATES"  # Latitude and longitude coordinates
PHONE = "PHONE"  # Phone number
COLOR = "COLOR"  # Color number
TEMPERATURE = "TEMPERATURE"  # Temperature degrees (celcius or fahrenheit)
URL = "URL"  # URL address for site
EMPTY = "EMPTY"  # Empty value

# Column types
CATEGORICAL_COLUMN = "CATEGORICAL"  # Categorical column type
LITERAL_COLUMN = "LITERAL"  # Literal column type
SUBJECT_COLUMN = "SUBJECT"  # Subject column type

# Простые предлоги
ABOARD = "aboard"  # на борту
ABOUT = "about"  # кругом, вокруг, в, где-то на, в пределах, относительно, о
ABOVE = "above"  # над, до, более, свыше, выше
ABSENT = "absent"  # (амер.) без, в отсутствие
ACROSS = "across"  # через, сквозь, по ту сторону
AFORE = "afore"  # вперед, перед
AFTER = "after"  # за, после, по, позади
AGAINST = "against"  # против, в, о, обо, на, к
ALONG = "along"  # вдоль, по
AMID = "amid"  # среди, посреди, между
AMIDST = "amidst"  # среди, посреди, между
AMONG = "among"  # между, посреди
AMONGST = "amongst"  # между, посреди
AROUND = "around"  # вокруг, по, за, около
AS = "as"  # в качестве, как
ASIDE = "aside"  # в стороне, поодаль
ASLANT = "aslant"  # поперек
ASTRIDE = "astride"  # верхом на, по обе стороны, на пути
AT = "at"  # у, около, в, на
ATHWART = "athwart"  # поперек, через, вопреки, против
ATOP = "atop"  # на, поверх, над
BAR = "bar"  # исключая, за исключением, кроме
BEFORE = "before"  # перед, до, в
BEHIND = "behind"  # позади, за, после
BELOW = "below"  # ниже, под
BENEATH = "beneath"  # под, ниже
BESIDE = "beside"  # рядом, близ, около, ниже
BESIDES = "besides"  # кроме
BETWEEN = "between"  # между
BETWIXT = "betwixt"  # между
BEYOND = "beyond"  # по ту сторону, за, вне, позже, сверх, выше
BUT = "but"  # кроме, за исключением
BY = "by"  # у, около, мимо, вдоль, через, к, на
CIRCA = "circa"  # приблизительно, примерно, около
DESPITE = "despite"  # несмотря на
DOWN = "down"  # вниз, с, по течению, вниз по, вдоль по, по, ниже, через, сквозь
EXCEPT = "except"  # исключая, кроме
FOR = "for"  # на, в, в течение дня, за, ради, к, от, по отношению, в отношении, вместо
FROM = "from"  # от, из, с, по, из-за, у
GIVEN = "given"  # при условии
IN = "in"  # в, во, на, в течение, за, через, у, к, из
INSIDE = "inside"  # внутри, внутрь, с внутренней стороны, на внутренней стороне
INTO = "into"  # в, на
LIKE = "like"  # так; как что-л.; подобно чему-л.
MID = "mid"  # (от "amid") между, посреди, среди
MINUS = "minus"  # без, минус
NEAR = "near"  # около, возле, к
NEATH = "neath"  # под, ниже
NEXT = "next"  # рядом, около
NOTWITHSTANDING = "notwithstanding"  # не смотря на, вопреки
OF = "of"  # о, у, из, от
OFF = "off"  # с, со, от
ON = "on"  # на, у, после, в
OPPOSITE = "opposite"  # против, напротив
OUT = "out"  # вне, из
OUTSIDE = "outside"  # вне, за пределами
OVER = "over"  # над, через, за, по, свыше, больше, у
PACE = "pace"  # с позволения
PER = "per"  # по, посредством, через, согласно, из расчёта на, за, в, с
PLUS = "plus"  # плюс, с
POST = "post"  # после
PRO = "pro"  # для, ради, за
QUA = "qua"  # как, в качестве
ROUND = "round"  # вокруг, по
SAVE = "save"  # кроме, исключая
SINCE = "since"  # с (некоторого времени), после
THAN = "than"  # нежели, чем
THROUGH = "through"  # через, сквозь, по, в, через посредство, из, от, в продолжение, в течение, включительно
# Список простых предлогов
SIMPLE_PREPOSITIONS = [ABOARD, ABOUT, ABOVE, ABSENT, ACROSS, AFORE, AFTER, AGAINST, ALONG, AMID, AMIDST, AMONG, AMONGST,
                       AROUND, AS, ASIDE, ASLANT, ASTRIDE, AT, ATHWART, ATOP, BAR, BEFORE, BEHIND, BELOW, BENEATH,
                       BESIDE, BESIDES, BETWEEN, BETWIXT, BEYOND, BUT, BY, CIRCA, DESPITE, DOWN, EXCEPT, FOR, FROM,
                       GIVEN, IN, INSIDE, INTO, LIKE, MID, MINUS, NEAR, NEATH, NEXT, NOTWITHSTANDING, OF, OFF, ON,
                       OPPOSITE, OUT, OUTSIDE, OVER, PACE, PER, PLUS, POST, PRO, QUA, ROUND, SAVE, SINCE, THAN, THROUGH]
# Производные предлоги
BARRING = "barring"  # исключая, за исключением, кроме
CONCERNING = "concerning"  # относительно
CONSIDERING = "considering"  # учитывая, принимая во внимание
DEPENDING = "depending"  # в зависимости
DURING = "during"  # в течение, в продолжение, во время
GRANTED = "granted"  # при условии
EXCEPTING = "excepting"  # за исключением, исключая
EXCLUDING = "excluding"  # за исключением
FAILING = "failing"  # за неимением, в случае отсутствия
FOLLOWING = "following"  # после, вслед за
INCLUDING = "including"  # включая, в том числе
PAST = "past"  # за, после, мимо, сверх, выше
PENDING = "pending"  # в продолжение, в течение, до, вплоть
REGARDING = "regarding"  # относительно, касательно
# Список производных предлогов
DERIVATIVE_PREPOSITIONS = [BARRING, CONCERNING, CONSIDERING, DEPENDING, DURING, GRANTED, EXCEPTING, EXCLUDING, FAILING,
                           FOLLOWING, INCLUDING, PAST, PENDING, REGARDING]
# Сложные предлоги
ALONGSIDE = "alongside"  # около, рядом, у
WITHIN = "within"  # внутри, внутрь, в пределах, не далее, не позднее чем
UPON = "upon"  # на, у, после, в
ONTO = "onto"  # на, в
THROUGHOUT = "throughout"  # через, по всей площади, длине, на всем протяжении
WHEREWITH = "wherewith"  # чем, посредством которого
# Список сложных предлогов
COMPLEX_PREPOSITIONS = [ALONGSIDE, WITHIN, UPON, ONTO, THROUGHOUT, WHEREWITH]
# Составные предлоги
ACCORDING_TO = "according to"  # согласно
AHEAD_OF = "ahead of"  # до, в преддверии
APART_FROM = "apart from"  # несмотря на, невзирая на
AS_FAR_AS = "as far as"  # до
AS_FOR = "as for"  # что касается
AS_OF = "as of"  # с, начиная с; на день, на дату; на момент, от (такого-то числа)
AS_PER = "as per"  # согласно
AS_REGARDS = "as regards"  # что касается, в отношении
ASIDE_FROM = "aside from"  # помимо, за исключением
AS_WELL_AS = "as well as"  # кроме, наряду
AWAY_FROM = "away from"  # от, в отсутствие
BECAUSE = "because of"  # из-за
BY_FORCE_OF = "by force of"  # в силу
BY_MEANS_OF = "by means of"  # посредством
BY_VIRTUE_OF = "by virtue of"  # в силу, на основании
CLOSE_TO = "close to"  # рядом с
CONTRARY = "contrary to"  # против, вопреки
DUE_TO = "due to"  # благодаря, в силу, из-за
EXCEPT_FOR = "except for"  # кроме
FAR_FROM = "far from"  # далеко не
FOR_THE_SAKE_OF = "for the sake of"  # ради
IN_ACCORDANCE_WITH = "in accordance with"  # в соответствии с
IN_ADDITION_TO = "in addition to"  # в дополнение, кроме
IN_CASE_OF = "in case of"  # в случае
IN_CONNECTION_WITH = "in connection with"  # в связи с
IN_CONSEQUENCE = "in consequence of"  # вследствие, в результате
IN_FRONT_OF = "in front of"  # впереди
IN_SPITE_OF = "in spite of"  # несмотря на
IN_THE_BACK_OF = "in the back of"  # сзади, позади
IN_THE_COURSE_OF = "in the course of"  # в течение
IN_THE_EVENT_OF = "in the event of"  # в случае, если
IN_THE_MIDDLE_OF = "in the middle of"  # посередине
IN_TO = "in to" # в, на
INSIDE_OF = "inside of"  # за (какое-л время), в течение
INSTEAD_OF = "instead of"  # вместо
IN_VIEW_OF = "in view of"  # ввиду
NEAR_TO = "near to"  # рядом, поблизости
NEXT_TO = "next to"  # рядом, поблизости
ON_ACCOUNT_OF = "on account of"  # по причине, из-за, вследствие
ON_TO = "on to"  # на
ON_TOP_OF = "on top of"  # на вершине, наверху
OPPOSITE_TO = "opposite to"  # против
OUT_OF = "out of"  # из, изнутри, снаружи, за пределами
OUTSIDE_OF = "outside of"  # вне, помимо
OWING_TO = "owing to"  # из-за, благодаря
THANKS_TO = "thanks to"  # благодаря
UP_TO = "up to"  # вплоть до, на уровне
WITH_REGARD_TO = "with regard to"  # относительно, по отношению
WITH_RESPECT_TO = "with respect to"  # относительно, по отношению
# Список сложных предлогов
COMPOUND_PREPOSITIONS = [ACCORDING_TO, AHEAD_OF, APART_FROM, AS_FAR_AS, AS_FOR, AS_OF, AS_PER, AS_REGARDS, ASIDE_FROM,
                         AS_WELL_AS, AWAY_FROM, BECAUSE, BY_FORCE_OF, BY_MEANS_OF, BY_VIRTUE_OF, CLOSE_TO, CONTRARY,
                         DUE_TO, EXCEPT_FOR, FAR_FROM, FOR_THE_SAKE_OF, IN_ACCORDANCE_WITH, IN_ADDITION_TO, IN_CASE_OF,
                         IN_CONNECTION_WITH, IN_CONSEQUENCE, IN_FRONT_OF, IN_SPITE_OF, IN_THE_BACK_OF, IN_THE_COURSE_OF,
                         IN_THE_EVENT_OF, IN_THE_MIDDLE_OF, IN_TO, INSIDE_OF, INSTEAD_OF, IN_VIEW_OF, NEAR_TO, NEXT_TO,
                         ON_ACCOUNT_OF, ON_TO, ON_TOP_OF, OPPOSITE_TO, OUT_OF, OUTSIDE_OF, OWING_TO, THANKS_TO, UP_TO,
                         WITH_REGARD_TO, WITH_RESPECT_TO]


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


def determine_number(value, label):
    """
    Определение типа числа на основе исходного входного значения.
    :param value: исходное входное значение
    :param label: текущая метка
    :return: определенная метка числа
    """
    # Если число с плавающей точкой
    if is_float(value):
        label = FLOAT
    # Если целое положительное число
    if re.search(r"^[1-9]\d*$", value):
        label = POSITIVE_INTEGER
    # Если целое отрицательное число
    if re.search(r"^[-][1-9]\d*$", value):
        label = NEGATIVE_INTEGER

    return label


def determine_mention_entity(entity_mention):
    """
    Корректировка упоминания сущности (строки) с присвоением определенной метки.
    :param entity_mention: текстовое упоминание сущности (исходная строка)
    :return: определенная метка
    """
    # Если упоминание сущности является пустой строкой
    if entity_mention == "":
        label = EMPTY
    else:
        # Определение типа числового значения
        label = determine_number(entity_mention, NONE)
        # Если упоминание сущности является логическим значением
        if re.search(r"^'true|false|True|False|TRUE|FALSE'&", entity_mention):
            label = BOOLEAN
        # Если упоминание сущности является почтовым адресом (индексом)
        if re.search(r"^\d{6}$", entity_mention) or re.search(r"^\d{5}(?:[-\s]\d{4})?$", entity_mention):
            label = MAIL
        # Если упоминание сущности является ISSN-номером
        if re.search(r"^[0-9]{4}-[0-9]{3}[0-9xX]$", entity_mention):
            label = ISSN
        # Если упоминание сущности является ISBN-номером
        if re.search(r"^(?:ISBN(?:: ?| ))?((?:97[89])?\d{9}[\dx])+$", entity_mention):
            label = ISBN
        # Если упоминание сущности является IP-адресом
        if re.search(r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)", entity_mention):
            label = IP_ADDRESS_V4
        # Если упоминание сущности является номером банковской карты
        if re.search(r"^([456][0-9]{3})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})$", entity_mention):
            label = BANK_CARD
        # Если упоминание сущности является цветом в 16 бит
        if re.search(r"#[0-9A-Fa-f]{6}", entity_mention):
            label = COLOR
        # Если упоминание сущности является адресом электронной почты
        if re.search(r"[\w.-]+@[\w.-]+\.?[\w]+?", entity_mention):
            label = EMAIL
        # Если упоминание сущности является координатами широты и долготы
        if re.search(r"^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$", entity_mention):
            label = COORDINATES
        # Если упоминание сущности является номером сотового телефона
        if re.search(r"^((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))$", entity_mention):
            label = PHONE
        # Если упоминание сущности является значением температуры
        if re.search(r"([+-]?\d+(\.\d+)*)\s?°([CcFf])", entity_mention):
            label = TEMPERATURE
        # Если упоминание сущности является URL-адресом
        if re.search(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", entity_mention):
            label = URL

    return label


def test_ner(text):
    """
    Функция для тестирвоания распознавания именованных сущностей в тексте.
    :param text: исходный текст
    """
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    doc = nlp(text)
    print(*[f"entity: {ent.text}\ttype: {ent.type}" for ent in doc.ents], sep="\n")


def recognize_named_entities(source_table):
    """
    Распознавание именованных сущностей в исходном словаре (таблице)
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :return: словарь распознанных именнованых сущностей в таблице
    """
    result_list = []
    # Подготовка нейронного конвейера
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    # Обход строк в исходной таблице
    for row in source_table:
        result_item = dict()
        for key, entity_mention in row.items():
            # Распознавание именованной сущности
            doc = nlp(entity_mention + ".")
            # Формирование словаря с рузультатом распознавания именованных сущностей
            recognized_named_entities = []
            if len(doc.ents) > 1:
                for ent in doc.ents:
                    recognized_named_entities.append(ent.type)
            if len(doc.ents) == 1:
                recognized_named_entities = doc.ents[0].type
            if len(doc.ents) == 0:
                recognized_named_entities = NONE
            # Если упоминанию сущности присвоена неопределенная метка NONE
            if not isinstance(recognized_named_entities, list):
                # Корректировка значения NONE на основе регулярных выражений
                if recognized_named_entities == NONE:
                    recognized_named_entities = determine_mention_entity(entity_mention)
                # Уточнение типа числа на основе регулярных выражений
                if recognized_named_entities == CARDINAL:
                    recognized_named_entities = determine_number(entity_mention, CARDINAL)
            result_item[key] = recognized_named_entities
        result_list.append(result_item)

    return result_list


def classify_recognized_named_entities(recognized_table):
    """
    Определение типа значений в ячейке на основе распознанных именованных сущностей.
    :param recognized_table: словарь (таблица) с распознанными именованными сущностями: ключ и NER-тег
    :return: словарь классифицированных по типам значений ячеек в таблице
    """
    result_list = []
    for recognized_row in recognized_table:
        result_item = dict()
        for key, recognized_named_entities in recognized_row.items():
            typed_value = LITERAL_COLUMN
            if isinstance(recognized_named_entities, list):
                for recognized_named_entity in recognized_named_entities:
                    if recognized_named_entity in NAMED_ENTITY_TAGS:
                        typed_value = CATEGORICAL_COLUMN
            else:
                if recognized_named_entities in NAMED_ENTITY_TAGS:
                    typed_value = CATEGORICAL_COLUMN
            result_item[key] = typed_value
        result_list.append(result_item)

    return result_list


def classify_columns(typed_table):
    """
    Определение типов столбцов на основе классифицированных значений ячеек.
    :param typed_table: словарь (таблица) с квалифицированными значениями ячеек: ключ и тип ячейки
    :return: словарь с типами столбцов
    """
    # Подсчет количества категориальных и литеральных значений ячеек
    categorical_number = defaultdict(int)
    literal_number = defaultdict(int)
    for typed_row in typed_table:
        for key, value in typed_row.items():
            if categorical_number[key] == 0:
                categorical_number[key] = 0
            if literal_number[key] == 0:
                literal_number[key] = 0
            if value == CATEGORICAL_COLUMN:
                categorical_number[key] += 1
            if value == LITERAL_COLUMN:
                literal_number[key] += 1
    # Определение типов для столбцов
    result_list = dict()
    for key_c, value_c in categorical_number.items():
        for key_l, value_l in literal_number.items():
            if key_c == key_l:
                if value_c >= value_l:
                    result_list[key_c] = CATEGORICAL_COLUMN
                else:
                    result_list[key_c] = LITERAL_COLUMN

    return result_list


def get_empty_cell_fraction(source_table, classified_table):
    """
    Получение доли пустых ячеек для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Вычисление количества пустых ячеек в столбце
            empty_cell_number = 0
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key and not mention_entity:
                        empty_cell_number += 1
            # Вычисление доли пустых ячеек в столбце
            result_list[column_key] = empty_cell_number / cell_number

    return result_list


def get_cell_fraction_with_acronyms(source_table, classified_table):
    """
    Получение доли ячеек, содержащих акронимы, для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Вычисление количества ячеек с акронимами в столбце
            cell_number_with_acronyms = 0
            for row in source_table:
                for key, mention_entity in row.items():
                    # Поиск акронимов по регулярному выражению
                    if column_key == key and re.search(r"\b[A-ZА-Я.]{2,}\b", mention_entity):
                        cell_number_with_acronyms += 1
            # Вычисление доли ячеек, содержащих акронимы
            result_list[column_key] = cell_number_with_acronyms / cell_number

    return result_list


def determine_prepositions_in_column_header_name(classified_table):
    """
    Определение названий предлогов в заголовке столбца
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: оценка поиска предлогов (0 - предлогов нет, 1 - предлоги есть)
    """
    result = 0
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Проверка названия заголовка столбца в нижнем регистре на предлоги
            if column_key.lower() in SIMPLE_PREPOSITIONS or column_key.lower() in DERIVATIVE_PREPOSITIONS or \
                    column_key.lower() in COMPLEX_PREPOSITIONS or column_key.lower() in COMPOUND_PREPOSITIONS:
                result = 1

    return result


def get_unique_content_cell_fraction(source_table, classified_table):
    """
    Получение доли ячеек с уникальным содержимым для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Вычисление количества ячеек с уникальным содержимым
            col = collections.Counter()
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key:
                        col[mention_entity] += 1
            # Вычисление доли ячеек с уникальным содержимым в столбце
            result_list[column_key] = len(col) / cell_number

    return result_list


def get_distance_from_first_ne_column(classified_table):
    """
    Получение расстояния от первого сущностного столбца для категориальных столбцов.
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    column_number = 0
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            result_list[column_key] = column_number
        column_number += 1

    return result_list


def get_average_word_number(source_table, classified_table):
    """
    Получение среднего количества слов для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Подсчет количества слов в ячейках
            total_word_number = 0
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key and mention_entity:
                        total_word_number += len(mention_entity.split())
            # Вычисление среднего количества слов в ячейках столбца
            result_list[column_key] = total_word_number / cell_number

    return result_list


def define_subject_column(source_table, classified_table, index=None):
    """
    Определение сущностного (тематического) столбца на основе эвристических оценок.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :param index: явное указание на номер сущностного (тематического) столбца
    :return: словарь (таблица) с отмеченным сущностным (тематическим) столбцом
    """
    result_list = dict()
    # Если явно указан номер столбца, то данный столбец назначается сущностным (тематическим)
    if is_float(str(index)) and 0 <= index <= len(classified_table):
        i = 0
        for key, type_column in classified_table.items():
            if i == index:
                result_list[key] = SUBJECT_COLUMN
            else:
                result_list[key] = type_column
            i += 1
    else:
        sub_col = dict()
        # Весовые коэффициенты для балансировки эвристик
        weighting_factor_1 = 2
        weighting_factor_2 = 1
        weighting_factor_3 = 1
        weighting_factor_4 = 1
        weighting_factor_5 = 1
        # Пороговый коэффициент, определяющий, что в ячейке представлен длинный текст
        threshold_coefficient = 10
        # Получение доли пустых ячеек
        empty_cell_fraction = get_empty_cell_fraction(source_table, classified_table)
        # Получение доли ячеек с акронимами
        cell_fraction_with_acronyms = get_cell_fraction_with_acronyms(source_table, classified_table)
        # Определение предлогов в названии заголовка столбца
        hpn = determine_prepositions_in_column_header_name(classified_table)
        # Получение доли ячеек с уникальным содержимым
        unique_content_cell_fraction = get_unique_content_cell_fraction(source_table, classified_table)
        # Получение расстояния от первого сущностного столбца
        distance_from_first_ne_column = get_distance_from_first_ne_column(classified_table)
        # Получение среднего количества слов
        average_word_number = get_average_word_number(source_table, classified_table)
        # Агрегация оценки
        for key, type_column in classified_table.items():
            if type_column == CATEGORICAL_COLUMN:
                # Нормализация ранга, полученного путем подсчета среднего количества слов
                awn = 0
                if average_word_number[key] <= threshold_coefficient:
                    awn = average_word_number[key] / threshold_coefficient
                # Вычисление штрафной оценки
                penalty_rank = weighting_factor_3 * empty_cell_fraction[key] + \
                               weighting_factor_4 * cell_fraction_with_acronyms[key] + \
                               weighting_factor_5 * hpn
                # Вычисление итогового ранга (оценки)
                sub_col[key] = (weighting_factor_1 * unique_content_cell_fraction[key] + weighting_factor_2 * awn -
                                penalty_rank) / sqrt(distance_from_first_ne_column[key] + 1)
                print("TOTAL = " + str(sub_col[key]))
        # Определение ключа столбца с максимальной оценкой
        subject_key = max(sub_col.items(), key=operator.itemgetter(1))[0]
        # Формирование словаря с определенным сущностным (тематическим) столбцом
        for key, type_column in classified_table.items():
            if key == subject_key:
                result_list[key] = SUBJECT_COLUMN
            else:
                result_list[key] = type_column

    return result_list
