import collections
import operator
import re
from abc import ABC, abstractmethod
from math import sqrt

from atomic_column_classifier import ColumnType
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.utility import is_int


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
    # List of simple prepositions
    SIMPLE_PREPOSITIONS = [ABOARD, ABOUT, ABOVE, ABSENT, ACROSS, AFORE, AFTER, AGAINST, ALONG, AMID, AMIDST, AMONG, AMONGST, AROUND, AS,
                           ASIDE, ASLANT, ASTRIDE, AT, ATHWART, ATOP, BAR, BEFORE, BEHIND, BELOW, BENEATH, BESIDE, BESIDES, BETWEEN,
                           BETWIXT, BEYOND, BUT, BY, CIRCA, DESPITE, DOWN, EXCEPT, FOR, FROM, GIVEN, IN, INSIDE, INTO, LIKE, MID, MINUS,
                           NEAR, NEATH, NEXT, NOTWITHSTANDING, OF, OFF, ON, OPPOSITE, OUT, OUTSIDE, OVER, PACE, PER, PLUS, POST, PRO, QUA,
                           ROUND, SAVE, SINCE, THAN, THROUGH]


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
    # List of derivative prepositions
    DERIVATIVE_PREPOSITIONS = [BARRING, CONCERNING, CONSIDERING, DEPENDING, DURING, GRANTED, EXCEPTING, EXCLUDING, FAILING, FOLLOWING,
                               INCLUDING, PAST, PENDING, REGARDING]


class ComplexPreposition:
    ALONGSIDE = "alongside"  # около, рядом, у
    WITHIN = "within"  # внутри, внутрь, в пределах, не далее, не позднее чем
    UPON = "upon"  # на, у, после, в
    ONTO = "onto"  # на, в
    THROUGHOUT = "throughout"  # через, по всей площади, длине, на всем протяжении
    WHEREWITH = "wherewith"  # чем, посредством которого
    # List of complex prepositions
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
    # List of compound prepositions
    COMPOUND_PREPOSITIONS = [ACCORDING_TO, AHEAD_OF, APART_FROM, AS_FAR_AS, AS_FOR, AS_OF, AS_PER, AS_REGARDS, ASIDE_FROM, AS_WELL_AS,
                             AWAY_FROM, BECAUSE, BY_FORCE_OF, BY_MEANS_OF, BY_VIRTUE_OF, CLOSE_TO, CONTRARY, DUE_TO, EXCEPT_FOR, FAR_FROM,
                             FOR_THE_SAKE_OF, IN_ACCORDANCE_WITH, IN_ADDITION_TO, IN_CASE_OF, IN_CONNECTION_WITH, IN_CONSEQUENCE,
                             IN_FRONT_OF, IN_SPITE_OF, IN_THE_BACK_OF, IN_THE_COURSE_OF, IN_THE_EVENT_OF, IN_THE_MIDDLE_OF, IN_TO,
                             INSIDE_OF, INSTEAD_OF, IN_VIEW_OF, NEAR_TO, NEXT_TO, ON_ACCOUNT_OF, ON_TO, ON_TOP_OF, OPPOSITE_TO, OUT_OF,
                             OUTSIDE_OF, OWING_TO, THANKS_TO, UP_TO, WITH_REGARD_TO, WITH_RESPECT_TO]


class WeightingFactor:
    UCF = 2
    AWN = 1
    ECF = 1
    CFA = 1
    HPN = 1


class AbstractSubjectColumnIdentifier(ABC):
    __slots__ = ()

    @abstractmethod
    def get_empty_cell_fraction(self, column_index: int = None) -> float:
        """
        Get a proportion of empty cells for current column from table.
        :param column_index: index of current column
        :return: proportion of blank cells for current column
        """
        pass

    @abstractmethod
    def get_cell_fraction_with_acronyms(self, column_index: int = None) -> float:
        """
        Get a proportion of cells with acronyms for current column from table.
        :param column_index: index of current column
        :return: proportion of cells with acronyms for current column
        """
        pass

    @abstractmethod
    def get_unique_content_cell_fraction(self, column_index: int = None) -> float:
        """
        Get a proportion of cells with unique content for current column from table.
        :param column_index: index of current column
        :return: proportion of cells with unique content for current column
        """
        pass

    @abstractmethod
    def get_distance_from_first_ne_column(self, column_index: int = None) -> int:
        """
        Get a distance from the first categorical column to current column.
        :param column_index: index of current column
        :return: distance from the first categorical column
        """
        pass

    @abstractmethod
    def get_average_word_number(self, column_index: int = None, threshold_factor: int = 0) -> float:
        """
        Get average number of words for current column.
        :param column_index: index of current column
        :param threshold_factor: threshold factor for cells that contains long text
        :return: average number of words
        """
        pass

    @abstractmethod
    def determine_prepositions_in_column_header_name(self, column_index: int = None) -> int:
        """
        Define preposition names in current column heading.
        :param column_index: index of current column
        :return: 1 if heading is a preposition, otherwise 0
        """
        pass


class SubjectColumnIdentifier(AbstractSubjectColumnIdentifier):

    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    def get_empty_cell_fraction(self, column_index: int = None) -> float:
        return sum(1 if not cell else 0 for cell in self.table_model.column(column_index)) / self.table_model.rows_number

    def get_cell_fraction_with_acronyms(self, column_index: int = None) -> float:
        cn = sum(1 if cell is not None and re.search(r"\b[A-ZА-Я.]{2,}\b", cell) else 0 for cell in self.table_model.column(column_index))
        return cn / self.table_model.rows_number

    def get_unique_content_cell_fraction(self, column_index: int = None) -> float:
        col = collections.Counter()
        for cell in self.table_model.column(column_index):
            col[cell] += 1
        return len(col) / self.table_model.rows_number

    def get_distance_from_first_ne_column(self, column_index: int = None) -> int:
        categorical_column_index = 0
        for column in self.table_model.columns:
            if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                break
            categorical_column_index += 1
        return sum(1 if i < column_index else 0 for i in range(categorical_column_index, self.table_model.columns_number))

    def get_average_word_number(self, column_index: int = None, threshold_factor: int = 0) -> float:
        score = sum(len(cell.split()) if cell else 0 for cell in self.table_model.column(column_index)) / self.table_model.rows_number
        return score / threshold_factor if score <= threshold_factor else 0

    def determine_prepositions_in_column_header_name(self, column_index: int = None) -> int:
        result, column_number = 0, 0
        for column in self.table_model.columns:
            if column_number == column_index:
                if column.header_name.lower() in SimplePreposition.SIMPLE_PREPOSITIONS or \
                        column.header_name.lower() in DerivedPreposition.DERIVATIVE_PREPOSITIONS or \
                        column.header_name.lower() in ComplexPreposition.COMPLEX_PREPOSITIONS or \
                        column.header_name.lower() in CompoundPreposition.COMPOUND_PREPOSITIONS:
                    result = 1
            column_number += 1
        return result

    def define_subject_column(self, column_index: int = None):
        """
        Определение сущностного (тематического) столбца на основе эвристических оценок.
        :param column_index: явное указание на номер сущностного (тематического) столбца
        """
        # If column index is explicitly specified, then this column is assigned to a subject column
        if is_int(str(column_index)) and 0 <= column_index < self.table_model.columns_number:
            i = 0
            for column in self.table_model.columns:
                if column_index == i:
                    column._column_type = ColumnType.SUBJECT_COLUMN
                i += 1
        else:
            column_index, sub_col = 0, {}
            for column in self.table_model.columns:
                if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                    # Calculate heuristics
                    ucf = self.get_unique_content_cell_fraction(column_index)
                    awn = self.get_average_word_number(column_index, 10)
                    ecf = self.get_empty_cell_fraction(column_index)
                    cfa = self.get_cell_fraction_with_acronyms(column_index)
                    hpn = self.determine_prepositions_in_column_header_name(column_index)
                    dfc = self.get_distance_from_first_ne_column(column_index)
                    # Get penalty score
                    penalty_score = WeightingFactor.ECF * ecf + WeightingFactor.CFA * cfa + WeightingFactor.HPN * hpn
                    # Get total score
                    sub_col[column.header_name] = ((WeightingFactor.UCF * ucf + WeightingFactor.AWN * awn) - penalty_score) / sqrt(dfc + 1)
                    print("Total score for '" + str(column.header_name) + "' (candidate subject column) = " +
                          str(sub_col[column.header_name]))
                column_index += 1
            # Define current column with highest score as subject column
            for column in self.table_model.columns:
                if column.header_name == max(sub_col.items(), key=operator.itemgetter(1))[0]:
                    column._column_type = ColumnType.SUBJECT_COLUMN
