from enum import Enum


class Preposition(str, Enum):
    # Simple prepositions
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
    # Derived prepositions
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
    # Complex prepositions
    ALONGSIDE = "alongside"  # около, рядом, у
    WITHIN = "within"  # внутри, внутрь, в пределах, не далее, не позднее чем
    UPON = "upon"  # на, у, после, в
    ONTO = "onto"  # на, в
    THROUGHOUT = "throughout"  # через, по всей площади, длине, на всем протяжении
    WHEREWITH = "wherewith"  # чем, посредством которого
    # Compound prepositions
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
    IN_TO = "in to"  # в, на
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

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
