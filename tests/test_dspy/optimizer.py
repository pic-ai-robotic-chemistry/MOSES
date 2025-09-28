from pydantic import BaseModel, Field
from typing import List, Tuple
import dspy

lm = dspy.LM('openai/gpt-4o', temperature=1)
dspy.configure(lm=lm)

class DataProperty(BaseModel):
    """Extracted data properties from text for ontology creation. These should be value-based properties, not entities."""
    name: str = Field(description="Provide a clear and concise name for the data property.")
    information: str = Field(description="Offer a complete and comprehensive sentence detailing the data property from the text.")

class Entity(BaseModel):
    """Extracted entities from text for ontology creation, including classes and individuals, excluding data properties."""
    name: str = Field(description="Provide a clear and concise name for the entity. Use the format [Full name]([Abbreviation]) if applicable.")
    information: str = Field(description="Offer a complete and comprehensive sentence detailing the entity from the text.")

class ObjectProperty(BaseModel):
    """Extracted object properties from text for ontology creation."""
    name: str = Field(description="Provide a clear and concise name for the object property. It should be separated by underscores between words.")
    domain: str = Field(
        description="Domain entity name of the object property, it should be an existing entity in the Entity list"
    )
    range: str = Field(
        description="Range entity name of the object property, it should be an existing entity in the Entity list"
    )
    restriction: str = Field(
        description="Use 'only' if the domain MUST have exactly and exclusively this range for the property. Use 'some' if the domain MUST have at least this range among possible values."
    )
    information: str = Field(
        description="Offer a complete and comprehensive sentence detailing the object property from the text."
    )

class Ontology(BaseModel):
    """Graph representation of the ontology for text."""

    entities: List[Entity] = Field(
        description="List of entities in the knowledge graph"
    )
    data_properties: List[DataProperty] = Field(
        description="List of data properties in the ontology"
    )
    object_properties: List[ObjectProperty] = Field(
        description="List of object properties in the ontology"
    )

def ontology_to_string(ontology: Ontology) -> str:
    result = []
    
    result.append("Entities:")
    for entity in ontology.entities:
        result.append(f"  - Name: {entity.name}")
        result.append(f"    Information: {entity.information}")
    
    result.append("\nData Properties:")
    for prop in ontology.data_properties:
        result.append(f"  - Name: {prop.name}")
        result.append(f"    Information: {prop.information}")
        
    result.append("\nObject Properties:")
    for prop in ontology.object_properties:
        result.append(f"  - Name: {prop.name}")
        result.append(f"    Domain: {prop.domain}")
        result.append(f"    Range: {prop.range}")
        result.append(f"    Restriction: {prop.restriction}")
        result.append(f"    Information: {prop.information}")
        
    return "\n".join(result)


class ExtractOntologyElements(dspy.Signature):
    """Analyze the provided text from research papers in the field of chemistry to identify all chemistry-related entities, data properties, and object properties within an ontological framework.

    Follow these Step-by-Step Analysis:

    1. Extract Chemistry-Related Entities:
      - Identify all significant nouns, proper nouns, and technical terminologies that represent chemistry-related concepts, such as molecules, reactions, compounds, processes, or any substantial entities.
      - Ensure that you capture entities across different levels of detail, from broad chemical categories to specific molecular structures, to create a comprehensive representation of the subject matter.
      - Choose names for entities that are specific enough to indicate their meaning without additional context, avoiding overly generic terms.
      - Consolidate similar entities to avoid redundancy, ensuring each represents a distinct concept at appropriate granularity levels.

    2. Identify Data Properties:
      - Extract attributes or characteristics of the identified entities that can be classified as data properties, ensuring they are value-based and not entities themselves.
      - Clearly define each data property, ensuring it accurately describes an attribute of an entity.

    3. Establish Object Properties:
      - Carefully examine the text to identify all relationships between entities, ensuring each relationship is correctly captured with accurate details about the interactions.
      - Analyze the context and interactions between the identified entities to determine how they are interconnected, focusing on actions, associations, dependencies, or similarities.
      - Clearly define the relationships, ensuring accurate directionality that reflects the logical or functional dependencies among entities.

    Objective: Produce a detailed and comprehensive ontology that captures the full spectrum of chemistry-related entities, data properties, and object properties mentioned in the text, along with their interrelations, reflecting both broad concepts and intricate details specific to the chemistry domain.

    """

    text: str = dspy.InputField(
        desc="a paragraph of text to extract entities, data properties, and object properties to form an ontology"
    )
    ontology: Ontology = dspy.OutputField(
        desc="List representation of the ontology extracted from the text."
    )


extractor = dspy.ChainOfThought(ExtractOntologyElements)

context = """
###### How electron donation and withdrawal change chemical shifts  \nWe can get an idea of the effect of electron distribution by looking at a series of benzene rings\nwith the same substituent in the 1 and 4 positions. This pattern makes all four hydrogens on\nthe ring identical. Here are a few compounds listed in order of chemical shift: largest shift\n(lowest fi eld; most deshielded) fi rst. Conjugation is shown by the usual curly arrows, and\ninductive effects by a straight arrow by the side of the group. Only one hydrogen atom and\none set of arrows are shown.  \nConjugation, as discussed in\nChapter 7, is felt through π bonds,\nwhile inductive effects are the\nresult of electron withdrawal or\ndonation felt simply by polarization\nof the σ bonds of the molecule.\nSee p. 135.  \nthe effect of electron-withdrawing groups\nby conjugation  \nby inductive effects  \n**H**  \n**O**  \n**O**  \n**HO**  \n**N**  \nδH 8.48 δH 8.10 **C** δH 8.10 δH 8.07 δH 7.78  \n**N**  \n**O**  \n**O**  \n**OH**  \n**C**  \n**N**  \n**O**  \n**H**  \n**F** **F**  \n**F**  \nThe largest shifts come from groups that withdraw electrons by conjugation. Nitro is the\nmost powerful—this should not surprise you as we saw the same in non-aromatic compounds\nin both [13]C and [1]H NMR spectra. Then come the carbonyl and nitrile group followed by groups\nshowing simple inductive withdrawal. CF3 is an important example of this kind of group—\nthree fl uorine atoms combine to exert a powerful effect.  \n-----  \nIn the middle of our sequence, around the position of benzene itself at 7.27 ppm, come\nthe halogens, whose inductive electron withdrawal and lone pair donation are nearly\nbalanced.  \nbalance between withdrawal by inductive effect and donation of lone pairs by conjugation  \n**I** δH 7.40 **Br** δH 7.32 δH 7.27 **Cl** δH 7.24 **F** δH 7.00  \n**I**  \n**Br**  \n**Cl**  \n**F**  \nAlkyl groups are weak inductive donators, but the groups which give the most shielding—\nperhaps surprisingly—are those containing the electronegative atoms O and N. Despite being\ninductively electron withdrawing (the C–O and C–N σ bonds are polarized with δ + C), on\nbalance conjugation of their lone pairs with the ring (as you saw on p. 278) makes them net\nelectron donors. They increase the shielding at the ring hydrogens. Amino groups are the best.\nNote that one nitrogen-based functional group (NO2) is the best electron withdrawer while\nanother (NH2) is the best electron donor.  \nthe effect of electron-donating groups  \nby inductive effect  \nbalance between withdrawal by inductive effect and donation\nof lone pairs by conjugation—electron donation wins  \n**H**  \nδH 7.03  \n**H**  \n**H**  \n**CH3**  \nδH 6.80 **O**  \n**H** **H**  \nδH 6.59 **N**  \n**H**  \nδH 6.35  \n**H**  \n**H**  \n**CH3**  \n**O**  \n**CH3**  \n**H**  \n**H**  \n**N**  \n**O**  \nδH 7.27  \n**H**  \n**H**  \nδH 7.27  \nδH 5.68  \n**H**  \n**H**  \nδH 5.68  \n**O**  \nδH 6.0  \n**H**  \n**H**  \nδH 7.0  \nδH 4.65  \n**H**  \n**H**  \nδH 6.35  \nAs far as the donors with lone pairs are concerned (the halogens plus O and N), two factors\nare important—the size of the lone pairs and the electronegativity of the element. If we look\nat the four halides at the top of this page the lone pairs are in 2p (F), 3p (Cl), 4p (Br), and 5p (I)\norbitals. In all cases the orbitals on the benzene ring are 2p so the fl uorine orbital is of the\nright size to interact well and the others too large. Even though fl uorine is the most electronegative, it is still the best donor. The others don’t pull so much electron density away, but\nthey can’t give so much back either.\nIf we compare the fi rst row of the p block elements—F, OH, and NH2—all have lone pairs\nin 2p orbitals so now electronegativity is the only variable. As you would expect, the most\nelectronegative element, F, is now the weakest donor.
"""

response = extractor(text=context)

print(ontology_to_string(response.ontology))

class Assess(dspy.Signature):
    """Assess the quality of a tweet along the specified dimension."""

    assessed_text = dspy.InputField()
    assessment_ontology = dspy.InputField()
    assessment_criteria = dspy.InputField()
    assessment_score: int = dspy.OutputField()

def metric(context, response, trace=None):
    entity_accuracy = """Entity Accuracy Score (0-5 points):
Award 1 point for each criterion met:
- Entity names are specific and meaningful without being overly generic (1 point)
- Entity definitions align with established chemical concepts (1 point) 
- Entity relationships reflect valid chemical principles (1 point)
- Entities are properly consolidated without redundancy (1 point)
- Entity hierarchy captures appropriate chemical classification (1 point)"""

    data_property_correctness = """Data Property Correctness Score (0-5 points):
Award 1 point for each criterion met:
- Data properties are truly value-based attributes (1 point)
- Each data property describes a single measurable characteristic (1 point)
- Data property units and ranges are chemically valid (1 point)
- Data property dependencies are accurately captured (1 point)
- Data properties maintain consistency across the ontology (1 point)"""

    object_property_completeness = """Object Property Completeness Score (0-5 points):
Award 1 point for each criterion met:
- Object properties capture all key chemical interactions (1 point)
- Domain and range specifications reflect valid chemical relationships (1 point)
- Relationship restrictions ('only'/'some') are properly applied (1 point)
- Object property chains represent complex chemical processes (1 point)
- Inverse relationships are correctly identified where applicable (1 point)"""

    ontology_structure = """Ontology Structure Score (0-4 points):
Award 1 point for each criterion met:
- Entities span appropriate levels of chemical granularity (1 point)
- Properties and relationships form a coherent chemical knowledge graph (1 point)
- The ontology maintains semantic clarity independent of source text (1 point)
- Cross-references between concepts are meaningful and accurate (1 point)"""

    overall_score = """Overall Score (0-8 points):
Each criterion is evaluated on three levels - excellent (2 points), adequate (1 point), or poor (0 points):

- Extraction Accuracy (2 points):
  * Excellent: No errors in entity and property extraction
  * Adequate: Minor non-critical errors present 
  * Poor: Some extraction errors exist

- Professional Validity (2 points):
  * Excellent: Extractions fully align with chemical expertise
  * Adequate: Most extractions align with chemical knowledge
  * Poor: Some deviations from chemical principles

- Comprehensiveness (2 points):
  * Excellent: Complete extraction of all relevant information
  * Adequate: Most key information captured
  * Poor: Some key information missing

- Knowledge Independence (2 points):
  * Excellent: Entities and properties can be accurately understood without source text context
  * Adequate: Most entities and properties are clear without background text
  * Poor: Some understanding requires source text context"""

    score = sum(
        [
            dspy.ChainOfThought(Assess)(assessed_text=context, assessment_ontology=ontology_to_string(response.ontology), assessment_criteria=criteria).assessment_score for criteria in [entity_accuracy, data_property_correctness, object_property_completeness, ontology_structure, overall_score]
        ]
    )

    return score / 27.0