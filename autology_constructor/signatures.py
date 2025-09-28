import dspy

from autology_constructor.base_data_structures import OntologyElements, OntologyDataProperties, OntologyObjectProperties, OntologyEntities

class ExtractOntologyEntities(dspy.Signature):
    """Analyze the provided text from research papers in the field of chemistry to identify all chemistry-related entities for the subsequent parts to construct an ontological framework together. And all the entities are regarded as classes in the ontology.

    You are an expert ontology engineer. Your task is to carefully analyze the text and extract key ontological entities following these steps:

    1. Extract Chemistry-Related Entities:
      - Identify all significant chemistry concepts that should be represented as entities
      - Look for nouns, proper nouns, and technical terms representing:
        * Chemical compounds, molecules, and substances
        * Reaction types and processes
        * Chemical properties and characteristics
        * Laboratory equipment and procedures
      - Ensure each entity name is specific and meaningful
      - Avoid redundancy by consolidating similar concepts
      - Avoid concepts describing data properties
      - Use '(' and ')' to **replace square brackets** '[' and ']' in entity names and abbreviations. **SQAURE BRACKETS ARE NOT ALLOWED IN ENTITY NAMES AND ABBREVIATIONS IN ANY CASE**. Especially, replace square brackets in case of ions.
      - Avoid '/' and '#' in entity names and abbreviations. Replace them with text to claim the meaning of the entity
      - Entity representing the union or intersection of multiple entities should be split into multiple entities

    2. Document Entity Information:
      s- For each entity, extract a complete and comprehensive sentence from the text that best describes the entity
      - The sentence should capture the essential characteristics or role of the entity
      - Ensure the information is factual and directly supported by the text
      - Avoid making inferences or combining information from different contexts
      - Focus on clear, unambiguous descriptions

    Remember: The final goal is to create a precise and well-structured ontological framework that accurately represents the chemistry domain knowledge in the text. In this part, the goal is to extract all the entities to be the ontology classes to be used in the subsequent parts and ontology."""
    
    text: str = dspy.InputField(
        desc="a paragraph of text to extract entities to form an ontology"
    )
    ontology_entities: OntologyEntities = dspy.OutputField(
        desc="List representation of the ontology entities extracted from the text"
    )

class ExtractOntologyElements(dspy.Signature):
    """Analyze the provided text from research papers in the field of chemistry to identify all hierarchical relationships and disjoint relationships about the ontology_entities to construct an ontological framework together with the subsequent parts. 

    You are an expert chemist. Your task is to carefully analyze the text and extract key relationships between the ontology_entities following these steps:

    1. Identify Superclass-Subclass Relationships:
      - If a class is another class with more specific meaning or modifiers, it should be classified as a subclass of the other class even if the text does not explicitly mention their relationships.
      - Carefully analyze the text for "is-a" relationships between entities
      - Look for phrases indicating classification or categorization
      - Carefully analyze the text for multiple inheritance relationships
      - Ensure the hierarchy is logically consistent
      - Document the evidence supporting each relationship
      - Verify that subclass-superclass relationship remains valid after removing modifiers and context
      - Avoid misclassification due to other entities appearing in modifiers of parent/child classes
      - Avoid circular or contradictory hierarchical relationships
      - **Most importantly**, an entity A consists of an entity B, and this entity A is **not** a subclass of entity B. The composition, component, construction and part of relationship is **not** a Superclass-Subclass relationship.

    2. Determine Disjoint Relationships:
      - Identify mutually exclusive classes that cannot share instances
      - Look for explicit statements of incompatibility
      - Verify each disjoint relationship is properly justified
      - Only extract disjoint class relationships when the text explicitly mentions that the two classes are disjoint, which means something cannot be both classes at the same time.

    Remember: The final goal is to create a precise and well-structured ontological framework that accurately represents the chemistry domain knowledge in the text. In this part, the goal is to extract all the hierarchy and disjointness of the ontology classes to abound ontology."""

    text: str = dspy.InputField(
        desc="a paragraph of text to extract entities and their relationships to form an ontology"
    )
    ontology_entities: OntologyEntities = dspy.InputField(
        desc="List representation of entities extracted from the text. The entities in your extracted hierarchical and disjoint relationships should be in this list."
    )
    ontology_elements: OntologyElements = dspy.OutputField(
        desc="List representation of the hierarchy and disjointness of entities extracted from the text."
    )

class ExtractOntologyDataProperties(dspy.Signature):
    """Analyze the provided text from research papers in the field of chemistry to identify data properties about the ontology_entities to construct an ontological framework.

    You are an expert ontology engineer. Your task is to carefully analyze the text and extract data properties following these steps:

    1. Identify Data Properties:
      - Look for value-based attributes that describe entities:
        * Numerical measurements and quantities 
        * Descriptive characteristics
        * Physical or chemical properties
      - More importantly, the value of a data property of an entity should be a state, and this value points the owner entity itself.
      - For each property:
        * Determine the owner entity from existing_ontology_elements
        * Identify specific values if present
        * Document the context and meaning
        * Validate owner entity exists in the ontology
      - Ensure properties are attributes, not entities themselves

    Remember: The goal is to create a comprehensive property structure that captures all meaningful characteristics in the chemistry domain while maintaining consistency with existing entities.
    """

    text: str = dspy.InputField(
        desc="a paragraph of text to extract data properties for the ontology"
    )
    ontology_entities: OntologyEntities = dspy.InputField(
        desc="List representation of the ontology entities extracted from the text. The entities in your extracted data properties should be in this list."
    )
    ontology_data_properties: OntologyDataProperties = dspy.OutputField(
        desc="List representation of the data properties extracted from the text"
    )

class ExtractOntologyObjectProperties(dspy.Signature):
    """Analyze the provided text from research papers in the field of chemistry to identify object properties about the ontology_entities to construct an ontological framework.

    You are an expert ontology engineer. Your task is to carefully analyze the text and extract object properties following these steps:

    1. Establish Object Properties:
      - Identify relationships between entities by looking for:
        * Verbs and action phrases
        * Structural relationships
        * Functional dependencies
        * Composition and construction relationships
      - More importantly, the value of an object property of an entity should be another entity, and this value points the value entity.
      - For each relationship:
        * Define clear domain (source) entities from existing_ontology_elements
        * Specify range (target) entities from existing_ontology_elements
        * Determine if it's a universal or existential restriction
        * Verify domain and range entities exist in the ontology
        * Validate the relationship direction and semantics
        * Consider complex domain/range expressions using union/intersection

    Remember: The goal is to create a comprehensive property structure that captures all meaningful relationships in the chemistry domain while maintaining consistency with existing entities.
    """

    text: str = dspy.InputField(
        desc="a paragraph of text to extract object properties for the ontology"
    )
    ontology_entities: OntologyEntities = dspy.InputField(
        desc="List representation of the ontology entities extracted from the text. The entities in your extracted object properties should be in this list."
    )
    ontology_object_properties: OntologyObjectProperties = dspy.OutputField(
        desc="List representation of the object properties extracted from the text"
    )

class Assess(dspy.Signature):
    """Assess the quality of an ontology or a part of an ontology along the specified dimension."""

    assessed_text: str = dspy.InputField(
        desc="The text that is used to construct ontology"
    )
    assessment_ontology: str = dspy.InputField(
        desc="Structured text representation of the ontology extracted from the text"
    )
    assessment_criteria: str = dspy.InputField(
        desc="The criteria of dimension of ontology quality to be assessed"
    )
    assessment_score: int = dspy.OutputField(
        desc="Score with extreme rigor - only award full points when the ontology achieves perfect alignment with assessment criteria and would be deemed flawless by expert chemists"
    )
    assessment_reason: str = dspy.OutputField(
        desc="Leave this field empty if the ontology receives the full score for this criterion. Otherwise, explain what criteria are not met and propose improvements."
    )



