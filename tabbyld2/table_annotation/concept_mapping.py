from enum import Enum

from atomic_column_classifier import LiteralLabel, NamedEntityLabel


class OntologyClass(str, Enum):
    THING = "https://www.w3.org/2002/07/owl#Thing"
    PARK = "http://dbpedia.org/ontology/Park"
    MINE = "http://dbpedia.org/ontology/Mine"
    GARDEN = "http://dbpedia.org/ontology/Garden"
    CEMETERY = "http://dbpedia.org/ontology/Cemetery"
    WINE_REGION = "http://dbpedia.org/ontology/WineRegion"
    NATURAL_PLACE = "http://dbpedia.org/ontology/NaturalPlace"
    PROTECTED_AREA = "http://dbpedia.org/ontology/ProtectedArea"
    WORLD_HERITAGE_SITE = "http://dbpedia.org/ontology/WorldHeritageSite"
    SITE_OF_SPECIAL_SCIENTIFIC_INTEREST = "http://dbpedia.org/ontology/SiteOfSpecialScientificInterest"
    POPULATED_PLACE = "http://dbpedia.org/ontology/PopulatedPlace"
    ETHNIC_GROUP = "http://dbpedia.org/ontology/EthnicGroup"
    PERSON = "http://dbpedia.org/ontology/Person"
    DEVICE = "http://dbpedia.org/ontology/Device"
    FOOD = "http://dbpedia.org/ontology/Food"
    MEAN_OF_TRANSPORTATION = "http://dbpedia.org/ontology/MeanOfTransportation"
    ARCHITECTURAL_STRUCTURE = "http://dbpedia.org/ontology/ArchitecturalStructure"
    ORGANISATION = "http://dbpedia.org/ontology/Organisation"
    EVENT = "http://dbpedia.org/ontology/Event"
    WORK = "http://dbpedia.org/ontology/Work"
    LAW = "http://dbpedia.org/ontology/Law"
    LEGAL_CASE = "http://dbpedia.org/ontology/LegalCase"


CLASS_MAPPING = {
    NamedEntityLabel.NONE: OntologyClass.THING,
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
