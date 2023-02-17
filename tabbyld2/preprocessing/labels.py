from enum import Enum


class NamedEntityLabel(str, Enum):
    PERSON = "PERSON"  # People, including fictional
    NORP = "NORP"  # Nationalities or religious or political groups
    FACILITY = "FAC"  # Buildings, airports, highways, bridges, etc.
    ORGANIZATION = "ORG"  # Companies, agencies, institutions, etc.
    GPE = "GPE"  # Countries, cities, states
    LOCATION = "LOC"  # Non-GPE locations, mountain ranges, bodies of water
    PRODUCT = "PRODUCT"  # Vehicles, weapons, foods, etc. (Not services)
    EVENT = "EVENT"  # Named hurricanes, battles, wars, sports events, etc.
    ART_WORK = "WORK_OF_ART"  # Titles of books, songs, etc.
    LAW = "LAW"  # Named documents made into laws
    NONE = "NONE"  # NER result is empty

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class LiteralLabel(str, Enum):
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
    HEXADECIMAL = "HEXADECIMAL"  # Hexadecimal
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
    SYMBOL = "SYMBOL"  # Some symbol
    ID = "ID"  # Some identifier (ID)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
