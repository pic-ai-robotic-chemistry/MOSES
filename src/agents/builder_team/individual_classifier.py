from typing import List
from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate
from concept_extractor import IndividualMetaData, ClassMetaData


def generate_relationship_prompt(subject: str, object: str, text_content: str) -> str:
    return f"""# Relationship Analysis Task

## Task Overview
Please give a property to describe the relationship based on the text below between {subject} and {object}.

## Text
{text_content}

## Task Instructions
1. Text Analysis: Read throughoutly and make sure you comprehensively understand the provided Text.
2. BASED ON THE TEXT, offer a property to describe the relationship between {subject} and {object}:
   - property should begin with "has_" or "is_"
   - If the relationship is not meaningful from the text, output 'None'
   - If the relationship contains other entities except {subject} and {object}, only output a sentence that clearly describe the relationship.
3. Add a restriction:
   - If the relationship implies that the subject MUST have the object as its ONLY value for this property, add "only" as restriction
   - If the relationship implies that the subject MUST have AT LEAST the object as a value for this property, add "some" as restriction
   - If no clear restriction is implied, omit the restriction

## Output Format
{subject} [property_name] {object} [restriction]"""


def generate_relationship_prompt_all(subject: str, object: List[ClassMetaData], text_content: str) -> str:
    objects_str = "\n".join([obj.name for obj in object])
    return f"""# Relationship Analysis Task

## Task Overview
Please give properties to describe the relationship based on the text below between {subject} and [objects].

## Objects
{objects_str}

## Text
{text_content}

## Task Instructions
1. Text Analysis: Thoroughly read and comprehensively understand the provided Text.
2. BASED ON THE TEXT AND YOUR KNOWLEDGE, identify and describe relationships between {subject} and each [object]:
   - Property names must:
     * Start with "has" or "is" 
     * Use underscores between words
     * Be descriptive and meaningful both in and out of context
     * Support multiple words if needed
     * Prioritize reusing existing property names when applicable
     * Follow similar naming patterns as related properties
     * **MUST NOT** contain the [object] name
   - The relationship should be:
     * Logically valid when expressed as "{subject} [property_name] [object]"
     * Clear and understandable when stated as "{subject} [property_name], that is [object]"
     * Semantically accurate as a standalone statement without requiring the source text
   - If no valid relationship exists in the text, output 'None'

3. Specify relationship restrictions:
   - Use "only" if the subject MUST have exactly and exclusively this object for the property
   - Use "some" if the subject MUST have at least this object among possible values
   - Omit restriction if no clear cardinality is implied by the relationship

## Output Format
{subject} [property_name] [object] [restriction]"""