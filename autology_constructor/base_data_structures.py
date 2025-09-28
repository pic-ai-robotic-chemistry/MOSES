from pydantic import BaseModel, Field
from typing import List, Literal, Union

class DataProperty(BaseModel):
    """Extract data properties from text for ontology creation. These should be value-based properties, not entities. Do not miss any fields. If a data property has no value in context, ignore this property."""
    name: str = Field(description="Provide a clear and concise name for the data property. It should be in lowercase and separate words with underscores. Don't use plural form. ")
    values: Union[dict, None] = Field(
        default=None,
        description="A dictionary of values as values and their owner classes for the data property as keys. Owner classes should be existing entities in the Entity list. Entity names should be the totally same as the names in the Entity list. If the data property has no value in context, specify 'None'."
    )
    information: Union[str, None] = Field(
        default=None,
        description="Offer a complete and comprehensive sentence detailing the data property from the text."
    )

class Entity(BaseModel):
    """Extract entities from text for ontology creation, including classes and individuals, excluding data properties. Then regard all entities as classes. Do not miss any fields. Use '(' and ')' to replace square brackets '[' and ']' in both full name and abbreviations."""
    name: str = Field(description="Provide a clear and concise name for the entity. Use the format [Full Name]([Abbreviation]) if abbreviation is available, where [Full Name] should be in lowercase and separate words with underscores, and [Abbreviation] should keep its original format. Don't use plural form. Do not use quotes to wrap the name. Use underscores to replace space in full name. Use '(' and ')' to replace square brackets '[' and ']' in both full name and abbreviations. **SQAURE BRACKETS ARE NOT ALLOWED IN FULL NAMES AND ABBREVIATIONS IN ANY CASE**.")
    information: Union[str, None] = Field(
        default=None,
        description="Offer a complete and comprehensive sentence detailing the entity from the text."
    )

class Domain(BaseModel):
    """Describe the domain of an instance of an object property. The domain specifies the source class or classes that can have this property. It defines the valid types that can be the subject of the property."""
    entity: Union[str, None] = Field(
        default=None,
        description="Domain entity name of the object property meaning the owner class of the property. It should be an existing entity in the Entity list with type field as 'single'. If one entity cannot describe the domain, use multiple entities formatted as 'entity1, entity2, ...' combined with type field to specify their relationship. Entity names should be the totally same as the names in the Entity list."
    )
    type: Union[Literal['union', 'intersection', 'single'], None] = Field(
        default=None,
        description="Specify the domain type. 'union' means union of multiple domain entities, 'intersection' means intersection of multiple domain entities, and 'single' means single domain entity."
    )

class Range(BaseModel):
    """Describe the range of an instance of an object property. The range specifies the target class or classes that can be values for this property. It defines the valid types that the property value must belong to."""
    entity: Union[str, None] = Field(
        default=None,
        description="Range entity name of the object property meaning the value class of the property. It should be an existing entity in the Entity list with type field as 'single'. If one entity cannot describe the range, use multiple entities formatted as 'entity1, entity2, ...' combined with type field to specify their relationship. Entity names should be the totally same as the names in the Entity list."
    )
    type: Union[Literal['union', 'intersection', 'single'], None] = Field(
        default=None,
        description="Specify the range type. 'union' means union of multiple range entities, 'intersection' means intersection of multiple range entities, and 'single' means single range entity."
    )

class ObjectPropertyInstance(BaseModel):
    """Describe the domain and range of an object property. Use the exact entity sets from the original text without summarizing or inferring. Do not miss any fields."""
    domain: Union[Domain, None] = Field(
        default=None,
        description="Describe the domain of the instance of the object property.It should be an existing entity in the Entity list"
    )
    range: Union[Range, None] = Field(
        default=None,
        description="Describe the range of the instance of the object property. It should be an existing entity in the Entity list"
    )
    restriction: Literal['only', 'some', ""] = Field(
        default='some',
        description="Specify 'only' to indicate a universal restriction (owl:allValuesFrom), meaning all possible values of the domain class must belong to the specified range. Specify 'some' to indicate an existential restriction (owl:someValuesFrom), meaning at least one value of the domain class must belong to the specified range."
    )

class ObjectProperty(BaseModel):
    """Extract object properties and their instances from text for ontology creation. Do not miss any fields."""
    name: str = Field(description="Provide a clear and concise name for the object property. It should be in lowercase and separate words with underscores. It should start with is_ or has_ to indicate the property expresses a complex subclass-superclass relationship or a property. Don't use plural form. The name should not contain any entity name to avoid redundancy and improve the reusability in the ontology.")
    instances: Union[List[ObjectPropertyInstance], None] = Field(
        default=None,
        description="List of object property instances."
    )
    information: Union[str, None] = Field(
        default=None,
        description="Offer a complete and comprehensive sentence detailing the object property from the text."
    )

class Hierarchy(BaseModel):
    """Extract subclass-superclass relationship of entities in the ontology. Do not miss any fields."""
    subclass: str = Field(
        default='',
        description="Subclass name, it should be an existing entity in the Entity list. Its name should be the totally same as the name in the Entity list."
    )
    superclass: List[str] = Field(
        default=[],
        description="Superclass names, it should be one or more existing entities in the Entity list. Its name should be the totally same as the name in the Entity list."
    )
    information: Union[str, None] = Field(
        default=None,
        description="Offer a complete and comprehensive sentence detailing the subclass-superclass relationship from the text."
    )

class Disjointness(BaseModel):
    """Extract disjoint class relationships in the ontology. Disjoint classes means nothing belongs to both classes. Only extract disjoint class relationships when the text explicitly mentions that the two classes are disjoint, which means something cannot be both classes at the same time. Do not miss any fields."""
    class1: str = Field(
        default='',
        description="First class name, it should be an existing entity in the Entity list. Its name should be the totally same as the name in the Entity list."
    )
    class2: str = Field(
        default='',
        description="Second class name, it should be an existing entity in the Entity list. Its name should be the totally same as the name in the Entity list."
    )

class OntologyEntities(BaseModel):
    """List representation of the ontology entities extracted from the text."""
    entities: List[Entity] = Field(
        description="List of entities in the ontology"
    )

class OntologyElements(BaseModel):
    """List representation of the hierarchy and disjointness in the text about the ontology_entities. In this context, entity means same as class."""

    hierarchy: Union[List[Hierarchy], None] = Field(
        default=None,
        description="List of subclass-superclass relationships in the ontology. If there is no subclass-superclass relationship, specify 'None'."
    )
    disjointness: Union[List[Disjointness], None] = Field(
        default=None,
        description="List of disjoint class relationships in the ontology. If there is no disjoint class relationship, specify 'None'."
    )

class OntologyDataProperties(BaseModel):
    """List representation of the data properties in ontology for text. In this context, entity means same as class."""
    data_properties: Union[List[DataProperty], None] = Field(
        default=None,
        description="List of data properties in the ontology. If there is no data property, specify 'None'."
    )

class OntologyObjectProperties(BaseModel):
    """List representation of the object properties in ontology for text. In this context, entity means same as class."""
    object_properties: List[ObjectProperty] = Field(
        description="List of object properties in the ontology"
    )