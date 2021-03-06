import re
from abc import ABC
import stanza
import operator
import collections
from math import sqrt
from collections import defaultdict
from tabbyld2.utility import is_float
from tabbyld2.tabular_data_model import TableModel


class NamedEntityLabel:
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
    # Named entities from OntoNotes package
    NAMED_ENTITY_TAGS = [PERSON, NORP, FACILITY, ORGANIZATION, GPE, LOCATION, PRODUCT, EVENT, ART_WORK, LAW, NONE]


class LiteralLabel:
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
    # Literal labels list
    LITERAL_TAGS = [DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL, POSITIVE_INTEGER, NEGATIVE_INTEGER,
                    FLOAT, BOOLEAN, MAIL, EMAIL, ISSN, ISBN, IP_ADDRESS_V4, BANK_CARD, COORDINATES, PHONE, COLOR,
                    TEMPERATURE, URL, EMPTY]


class ColumnType:
    CATEGORICAL_COLUMN = "CATEGORICAL"  # Categorical column type
    LITERAL_COLUMN = "LITERAL"  # Literal column type
    SUBJECT_COLUMN = "SUBJECT"  # Subject column type


class SimplePreposition:
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
    SIMPLE_PREPOSITIONS = [ABOARD, ABOUT, ABOVE, ABSENT, ACROSS, AFORE, AFTER, AGAINST, ALONG, AMID, AMIDST, AMONG,
                           AMONGST, AROUND, AS, ASIDE, ASLANT, ASTRIDE, AT, ATHWART, ATOP, BAR, BEFORE, BEHIND, BELOW,
                           BENEATH, BESIDE, BESIDES, BETWEEN, BETWIXT, BEYOND, BUT, BY, CIRCA, DESPITE, DOWN, EXCEPT,
                           FOR, FROM, GIVEN, IN, INSIDE, INTO, LIKE, MID, MINUS, NEAR, NEATH, NEXT, NOTWITHSTANDING, OF,
                           OFF, ON, OPPOSITE, OUT, OUTSIDE, OVER, PACE, PER, PLUS, POST, PRO, QUA, ROUND, SAVE, SINCE,
                           THAN, THROUGH]


class DerivedPreposition:
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
    DERIVATIVE_PREPOSITIONS = [BARRING, CONCERNING, CONSIDERING, DEPENDING, DURING, GRANTED, EXCEPTING, EXCLUDING,
                               FAILING, FOLLOWING, INCLUDING, PAST, PENDING, REGARDING]


class ComplexPreposition:
    ALONGSIDE = "alongside"  # около, рядом, у
    WITHIN = "within"  # внутри, внутрь, в пределах, не далее, не позднее чем
    UPON = "upon"  # на, у, после, в
    ONTO = "onto"  # на, в
    THROUGHOUT = "throughout"  # через, по всей площади, длине, на всем протяжении
    WHEREWITH = "wherewith"  # чем, посредством которого
    # Список сложных предлогов
    COMPLEX_PREPOSITIONS = [ALONGSIDE, WITHIN, UPON, ONTO, THROUGHOUT, WHEREWITH]


class CompoundPreposition:
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
    COMPOUND_PREPOSITIONS = [ACCORDING_TO, AHEAD_OF, APART_FROM, AS_FAR_AS, AS_FOR, AS_OF, AS_PER, AS_REGARDS,
                             ASIDE_FROM, AS_WELL_AS, AWAY_FROM, BECAUSE, BY_FORCE_OF, BY_MEANS_OF, BY_VIRTUE_OF,
                             CLOSE_TO, CONTRARY, DUE_TO, EXCEPT_FOR, FAR_FROM, FOR_THE_SAKE_OF, IN_ACCORDANCE_WITH,
                             IN_ADDITION_TO, IN_CASE_OF, IN_CONNECTION_WITH, IN_CONSEQUENCE, IN_FRONT_OF, IN_SPITE_OF,
                             IN_THE_BACK_OF, IN_THE_COURSE_OF, IN_THE_EVENT_OF, IN_THE_MIDDLE_OF, IN_TO, INSIDE_OF,
                             INSTEAD_OF, IN_VIEW_OF, NEAR_TO, NEXT_TO, ON_ACCOUNT_OF, ON_TO, ON_TOP_OF, OPPOSITE_TO,
                             OUT_OF, OUTSIDE_OF, OWING_TO, THANKS_TO, UP_TO, WITH_REGARD_TO, WITH_RESPECT_TO]


class Coefficient:
    # Весовые коэффициенты для балансировки эвристик
    WEIGHTING_FACTOR_1 = 2
    WEIGHTING_FACTOR_2 = 1
    WEIGHTING_FACTOR_3 = 1
    WEIGHTING_FACTOR_4 = 1
    WEIGHTING_FACTOR_5 = 1
    # Пороговый коэффициент, определяющий, что в ячейке представлен длинный текст
    THRESHOLD_COEFFICIENT = 10


class AbstractTableColumnClassifier(ABC):
    __slots__ = ()


class TableColumnClassifier(AbstractTableColumnClassifier):
    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    @staticmethod
    def determine_number(value, label):
        """
        Определение типа числа на основе исходного входного значения.
        :param value: исходное входное значение
        :param label: текущая метка
        :return: определенная метка числа
        """
        # Если число с плавающей точкой
        if is_float(value):
            label = LiteralLabel.FLOAT
        # Если целое положительное число
        if re.search(r"^[1-9]\d*$", value):
            label = LiteralLabel.POSITIVE_INTEGER
        # Если целое отрицательное число
        if re.search(r"^[-][1-9]\d*$", value):
            label = LiteralLabel.NEGATIVE_INTEGER

        return label

    @staticmethod
    def determine_entity_mention(entity_mention):
        """
        Корректировка упоминания сущности (строки) с присвоением определенной метки.
        :param entity_mention: текстовое упоминание сущности (исходная строка)
        :return: определенная метка
        """
        # Если упоминание сущности является пустой строкой
        if entity_mention == "":
            label = LiteralLabel.EMPTY
        else:
            label = NamedEntityLabel.NONE
            # Если упоминание сущности является логическим значением
            if re.search(r"^'true|false|True|False|TRUE|FALSE'&", entity_mention):
                label = LiteralLabel.BOOLEAN
            # Если упоминание сущности является почтовым адресом (индексом)
            if re.search(r"^\d{6}$", entity_mention) or re.search(r"^\d{5}(?:[-\s]\d{4})?$", entity_mention):
                label = LiteralLabel.MAIL
            # Если упоминание сущности является ISSN-номером
            if re.search(r"^[0-9]{4}-[0-9]{3}[0-9xX]$", entity_mention):
                label = LiteralLabel.ISSN
            # Если упоминание сущности является ISBN-номером
            if re.search(r"^(?:ISBN(?:: ?| ))?((?:97[89])?\d{9}[\dx])+$", entity_mention):
                label = LiteralLabel.ISBN
            # Если упоминание сущности является IP-адресом
            if re.search(r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)", entity_mention):
                label = LiteralLabel.IP_ADDRESS_V4
            # Если упоминание сущности является номером банковской карты
            if re.search(r"^([456][0-9]{3})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})$", entity_mention):
                label = LiteralLabel.BANK_CARD
            # Если упоминание сущности является цветом в 16 бит
            if re.search(r"#[0-9A-Fa-f]{6}", entity_mention):
                label = LiteralLabel.COLOR
            # Если упоминание сущности является адресом электронной почты
            if re.search(r"[\w.-]+@[\w.-]+\.?[\w]+?", entity_mention):
                label = LiteralLabel.EMAIL
            # Если упоминание сущности является координатами широты и долготы
            if re.search(r"^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$", entity_mention):
                label = LiteralLabel.COORDINATES
            # Если упоминание сущности является номером сотового телефона
            if re.search(r"^((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{"
                         r"3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))$", entity_mention):
                label = LiteralLabel.PHONE
            # Если упоминание сущности является значением температуры
            if re.search(r"([+-]?\d+(\.\d+)*)\s?°([CcFf])", entity_mention):
                label = LiteralLabel.TEMPERATURE
            # Если упоминание сущности является URL-адресом
            if re.search(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,"
                         r"6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", entity_mention):
                label = LiteralLabel.URL

        return label

    def recognize_named_entities(self):
        """
        Распознавание именованных сущностей в ячейках таблицы.
        """
        # Подготовка нейронного конвейера
        stanza.download("en")
        nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
        # Обход столбцов в таблице
        for column in self.table_model.columns:
            for cell in column.cells:
                # Распознавание именованной сущности
                doc = nlp(cell.cleared_value + ".")
                # Формирование словаря с рузультатом распознавания именованных сущностей
                recognized_named_entities = []
                if len(doc.ents) > 1:
                    for ent in doc.ents:
                        recognized_named_entities.append(ent.type)
                if len(doc.ents) == 1:
                    recognized_named_entities = doc.ents[0].type
                if len(doc.ents) == 0:
                    recognized_named_entities = NamedEntityLabel.NONE
                # Если упоминанию сущности присвоена неопределенная метка NONE
                if not isinstance(recognized_named_entities, list):
                    # Корректировка значения NONE на основе регулярных выражений
                    if recognized_named_entities == NamedEntityLabel.NONE:
                        recognized_named_entities = self.determine_entity_mention(cell.cleared_value)
                    # Уточнение типа числа на основе регулярных выражений
                    if recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self.determine_number(cell.cleared_value, LiteralLabel.CARDINAL)
                    if recognized_named_entities == NamedEntityLabel.NONE:
                        recognized_named_entities = self.determine_number(cell.cleared_value, NamedEntityLabel.NONE)
                # Присваивание метки
                cell._label = recognized_named_entities

    def classify_columns(self):
        """
        Определение типов столбцов на основе распознанных именованных сущностей в ячейках таблицы.
        """
        # Подсчет категориальных и литеральных ячеек
        categorical_number = defaultdict(int)
        literal_number = defaultdict(int)
        for column in self.table_model.columns:
            for cell in column.cells:
                if categorical_number[column.header_name] == 0:
                    categorical_number[column.header_name] = 0
                if literal_number[column.header_name] == 0:
                    literal_number[column.header_name] = 0
                if cell.label in NamedEntityLabel.NAMED_ENTITY_TAGS:
                    categorical_number[column.header_name] += 1
                if cell.label in LiteralLabel.LITERAL_TAGS:
                    literal_number[column.header_name] += 1
        # Определение типов столбцов на основе классифицированных ячейках
        for key_c, value_c in categorical_number.items():
            for key_l, value_l in literal_number.items():
                if key_c == key_l:
                    for column in self.table_model.columns:
                        if column.header_name == key_c:
                            if value_c >= value_l:
                                column._column_type = ColumnType.CATEGORICAL_COLUMN
                            else:
                                column._column_type = ColumnType.LITERAL_COLUMN

    def get_empty_cell_fraction(self, column_index: int = None):
        """
        Получение доли пустых ячеек для указанного столбца.
        :param column_index: индекс столбца
        :return: доля пустых ячеек для указанного столбца
        """
        # Получение столбца по его индексу
        column = self.table_model.column(column_index)
        # Вычисление количества пустых ячеек в столбце
        empty_cell_number = 0
        for cell in column:
            if not cell:
                empty_cell_number += 1
        # Вычисление доли пустых ячеек в столбце
        empty_cell_fraction = empty_cell_number / self.table_model.rows_number

        return empty_cell_fraction

    def get_cell_fraction_with_acronyms(self, column_index: int = None):
        """
        Получение доли ячеек для указанного столбца, содержащих акронимы.
        :param column_index: индекс столбца
        :return: доля ячеек для указанного столбца, содержащих акронимы
        """
        # Получение столбца по его индексу
        column = self.table_model.column(column_index)
        # Вычисление количества ячеек с акронимами в столбце
        cell_number_with_acronyms = 0
        for cell in column:
            if re.search(r"\b[A-ZА-Я.]{2,}\b", cell):
                cell_number_with_acronyms += 1
        # Вычисление доли ячеек, содержащих акронимы
        cell_fraction_with_acronyms = cell_number_with_acronyms / self.table_model.rows_number

        return cell_fraction_with_acronyms

    @staticmethod
    def determine_prepositions_in_column_header_name(header_name: str = None):
        """
        Определение названий предлогов в заголовке столбца.
        :param header_name: название заголовка столбца
        :return: если название есть, то 1, иначе 0
        """
        result = 0
        # Проверка названия заголовка столбца в нижнем регистре на предлоги
        if header_name.lower() in SimplePreposition.SIMPLE_PREPOSITIONS or \
                header_name.lower() in DerivedPreposition.DERIVATIVE_PREPOSITIONS or \
                header_name.lower() in ComplexPreposition.COMPLEX_PREPOSITIONS or \
                header_name.lower() in CompoundPreposition.COMPOUND_PREPOSITIONS:
            result = 1

        return result

    def get_unique_content_cell_fraction(self, column_index: int = None):
        """
        Получение доли ячеек с уникальным содержимым для указанного столбца.
        :param column_index: индекс столбца
        :return: доля ячеек с уникальным содержимым для указанного столбца
        """
        # Получение столбца по его индексу
        column = self.table_model.column(column_index)
        # Вычисление количества ячеек с уникальным содержимым
        col = collections.Counter()
        for cell in column:
            col[cell] += 1
        # Вычисление доли ячеек с уникальным содержимым в столбце
        unique_content_cell_fraction = len(col) / self.table_model.rows_number

        return unique_content_cell_fraction

    @staticmethod
    def get_distance_from_first_ne_column(column_index: int = None):
        """
        Получение расстояния от первого категориального столбца до текущего указанного столбца.
        :param column_index: индекс столбца
        :return: расстояние от первого категориального столбца
        """
        distance_from_first_ne_column = column_index

        return distance_from_first_ne_column

    def get_average_word_number(self, column_index: int = None):
        """
        Получение среднего количества слов для указанного столбца.
        :param column_index: индекс столбца
        :return: среднее количество слов для указанного столбца
        """
        # Получение столбца по его индексу
        column = self.table_model.column(column_index)
        # Подсчет количества слов в ячейках
        total_word_number = 0
        for cell in column:
            if cell:
                total_word_number += len(cell.split())
        # Вычисление среднего количества слов в ячейках столбца
        average_word_number = total_word_number / self.table_model.rows_number

        return average_word_number

    def define_subject_column(self, column_index: int = None):
        """
        Определение сущностного (тематического) столбца на основе эвристических оценок.
        :param column_index: явное указание на номер сущностного (тематического) столбца
        """
        # Если явно указан номер столбца, то данный столбец назначается сущностным (тематическим)
        if is_float(str(column_index)) and 0 <= column_index < self.table_model.columns_number:
            i = 0
            for column in self.table_model.columns:
                if column_index == i:
                    column._column_type = ColumnType.SUBJECT_COLUMN
                i += 1
        else:
            index = 0
            sub_col = dict()
            for column in self.table_model.columns:
                if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                    # Получение доли пустых ячеек
                    empty_cell_fraction = self.get_empty_cell_fraction(index)
                    # Получение доли ячеек с акронимами
                    cell_fraction_with_acronyms = self.get_cell_fraction_with_acronyms(index)
                    # Определение предлогов в названии заголовка столбца
                    hpn = self.determine_prepositions_in_column_header_name(column.header_name)
                    # Получение доли ячеек с уникальным содержимым
                    unique_content_cell_fraction = self.get_unique_content_cell_fraction(index)
                    # Получение расстояния от первого сущностного столбца
                    distance_from_first_ne_column = self.get_distance_from_first_ne_column(index)
                    # Получение среднего количества слов
                    average_word_number = self.get_average_word_number(index)
                    # Нормализация ранга, полученного путем подсчета среднего количества слов
                    awn = 0
                    if average_word_number <= Coefficient.THRESHOLD_COEFFICIENT:
                        awn = average_word_number / Coefficient.THRESHOLD_COEFFICIENT
                    # Вычисление штрафной оценки
                    penalty_rank = Coefficient.WEIGHTING_FACTOR_3 * empty_cell_fraction + \
                                   Coefficient.WEIGHTING_FACTOR_4 * cell_fraction_with_acronyms + \
                                   Coefficient.WEIGHTING_FACTOR_5 * hpn
                    # Вычисление итогового ранга (оценки)
                    sub_col[column.header_name] = (Coefficient.WEIGHTING_FACTOR_1 * unique_content_cell_fraction +
                                                   Coefficient.WEIGHTING_FACTOR_2 * awn - penalty_rank) / sqrt(
                                                    distance_from_first_ne_column + 1)
                    print("Final score for '" + str(column.header_name) + "' (subject column) = " +
                          str(sub_col[column.header_name]))
                index += 1
            # Определение столбца с максимальной оценкой в качестве сущностного
            subject_key = max(sub_col.items(), key=operator.itemgetter(1))[0]
            for column in self.table_model.columns:
                if column.header_name == subject_key:
                    column._column_type = ColumnType.SUBJECT_COLUMN


def test_ner(text):
    """
    Функция для тестирвоания распознавания именованных сущностей в тексте.
    :param text: исходный текст
    """
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    doc = nlp(text)
    print(*[f"entity: {ent.text}\ttype: {ent.type}" for ent in doc.ents], sep="\n")
