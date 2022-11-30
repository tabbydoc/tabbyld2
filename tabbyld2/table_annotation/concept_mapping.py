from enum import Enum

from atomic_column_classifier import LiteralLabel, NamedEntityLabel


class OntologyClass(str, Enum):
    PARK = "dbo:Park"
    MINE = "dbo:Mine"
    GARDEN = "dbo:Garden"
    CEMETERY = "dbo:Cemetery"
    WINE_REGION = "dbo:WineRegion"
    NATURAL_PLACE = "dbo:NaturalPlace"
    PROTECTED_AREA = "dbo:ProtectedArea"
    WORLD_HERITAGE_SITE = "dbo:WorldHeritageSite"
    SITE_OF_SPECIAL_SCIENTIFIC_INTEREST = "dbo:SiteOfSpecialScientificInterest"
    POPULATED_PLACE = "dbo:PopulatedPlace"
    ETHNIC_GROUP = "dbo:EthnicGroup"
    PERSON = "dbo:Person"
    DEVICE = "dbo:Device"
    FOOD = "dbo:Food"
    MEAN_OF_TRANSPORTATION = "dbo:MeanOfTransportation"
    ARCHITECTURAL_STRUCTURE = "dbo:ArchitecturalStructure"
    ORGANISATION = "dbo:Organisation"
    EVENT = "dbo:Event"
    WORK = "dbo:Work"
    LAW = "dbo:Law"
    LEGAL_CASE = "dbo:LegalCase"


CLASS_MAPPING = {
    NamedEntityLabel.LOCATION: [OntologyClass.PARK, OntologyClass.MINE, OntologyClass.GARDEN, OntologyClass.WINE_REGION,
                                OntologyClass.NATURAL_PLACE, OntologyClass.PROTECTED_AREA, OntologyClass.WORLD_HERITAGE_SITE,
                                OntologyClass.SITE_OF_SPECIAL_SCIENTIFIC_INTEREST],
    NamedEntityLabel.GPE: OntologyClass.POPULATED_PLACE,
    NamedEntityLabel.NORP: OntologyClass.ETHNIC_GROUP,
    NamedEntityLabel.PERSON: OntologyClass.PERSON,
    NamedEntityLabel.PRODUCT: [OntologyClass.DEVICE, OntologyClass.FOOD, OntologyClass.MEAN_OF_TRANSPORTATION],
    NamedEntityLabel.FACILITY: OntologyClass.ARCHITECTURAL_STRUCTURE,
    NamedEntityLabel.ORGANIZATION: OntologyClass.ORGANISATION,
    NamedEntityLabel.EVENT: OntologyClass.EVENT,
    NamedEntityLabel.ART_WORK: OntologyClass.WORK,
    NamedEntityLabel.LAW: [OntologyClass.LAW, OntologyClass.LEGAL_CASE]
}


class XMLSchemaDataType(str, Enum):
    DATE = "xsd:date"
    TIME = "xsd:time"
    NON_NEGATIVE_INTEGER = "xsd:nonNegativeInteger"
    POSITIVE_INTEGER = "xsd:positiveInteger"
    NEGATIVE_INTEGER = "xsd:negativeInteger"
    DECIMAL = "xsd:decimal"
    FLOAT = "xsd:float"
    BOOLEAN = "xsd:boolean"
    STRING = "xsd:string"
    URL = "xsd:anyURI"


DATATYPE_MAPPING = {
    LiteralLabel.DATE: XMLSchemaDataType.DATE,
    LiteralLabel.TIME: XMLSchemaDataType.TIME,
    LiteralLabel.PERCENT: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.MONEY: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.QUANTITY: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.POSITIVE_INTEGER: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.ORDINAL: XMLSchemaDataType.POSITIVE_INTEGER,
    LiteralLabel.CARDINAL: XMLSchemaDataType.DECIMAL,
    LiteralLabel.MAIL: XMLSchemaDataType.DECIMAL,
    LiteralLabel.BANK_CARD: XMLSchemaDataType.DECIMAL,
    LiteralLabel.PHONE: XMLSchemaDataType.DECIMAL,
    LiteralLabel.NEGATIVE_INTEGER: XMLSchemaDataType.NEGATIVE_INTEGER,
    LiteralLabel.FLOAT: XMLSchemaDataType.FLOAT,
    LiteralLabel.BOOLEAN: XMLSchemaDataType.BOOLEAN,
    LiteralLabel.URL: XMLSchemaDataType.URL
}
