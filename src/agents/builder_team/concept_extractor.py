from __future__ import annotations  
from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Type, Union
import json
import os
import warnings


from owlready2 import get_ontology, types, Thing
from owlready2.namespace import Ontology

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate


from config import settings
 
llm = ChatOpenAI(
    model=settings.LLM_CONFIG["model"],
    temperature=settings.LLM_CONFIG["temperature"],
    api_key=settings.OPENAI_API_KEY,
    streaming=settings.LLM_CONFIG["streaming"]
)

class Example(BaseModel):
    context: str
    concepts: List[Concept]

class Concept(BaseModel):
    name: str
    is_data_property: bool
    information: str

class DataPropertyMetaData(BaseModel):
    name: str
    embedding: List[float] = Field(default_factory=list)
    location: Tuple[str, str] = Field(default_factory=lambda: ("", ""))
    information: str = ""
    
    def __eq__(self, other):
        if not isinstance(other, DataPropertyMetaData):
            return False
        return self.name == other.name

class IndividualMetaData(BaseModel):
    name: str
    embedding: List[float] = Field(default_factory=list)
    data_properties: Dict[str, str] = Field(default_factory=dict)
    location: Tuple[str, str] = Field(default_factory=lambda: ("", ""))
    information: str = ""
    
    def __eq__(self, other):
        if not isinstance(other, IndividualMetaData):
            return False
        return self.name == other.name

class ClassMetaData(BaseModel):
    name: str
    embedding: List[float] = Field(default_factory=list)
    location: Tuple[str, str] = Field(default_factory=lambda: ("", ""))
    information: str = ""
    
    def __eq__(self, other):
        if not isinstance(other, ClassMetaData):
            return False
        return self.name == other.name

def save_examples_to_json(examples: List[Example], filepath: str = None):
    if not examples:
        raise ValueError("示例列表不能为空。")

    # 检查所有实例是否都是Example类型
    if not all(isinstance(example, Example) for example in examples):
        raise TypeError("列表中所有实例必须是Example类型。")

    # 使用传入的文件路径或默认路径
    filename = filepath or settings.EXTRACTOR_EXAMPLES_CONFIG["concept_file_path"]

    # 读取已有数据(如果文件存在)
    existing_examples = []
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_examples = [Example(**data) for data in existing_data]

    # 合并示例,检测重复
    all_examples = existing_examples.copy()
    for new_example in examples:
        is_duplicate = False
        for existing in existing_examples:
            # 比较context和concepts内容是否完全相同
            if (existing.context == new_example.context and
                len(existing.concepts) == len(new_example.concepts) and
                all(ec.model_dump() == nc.model_dump() 
                    for ec, nc in zip(existing.concepts, new_example.concepts))):
                is_duplicate = True
                break
        
        if not is_duplicate:
            all_examples.append(new_example)

    # 保存合并后的数据
    json_data = json.dumps([example.model_dump() for example in all_examples], 
                          ensure_ascii=False, indent=4)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json_data)

def _load_examples_from_json(filepath: str = None) -> List[Example]:
    filename = filepath or settings.EXTRACTOR_EXAMPLES_CONFIG["concept_file_path"]
    
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return []
        
    with open(filename, 'r', encoding='utf-8') as f:
        examples_data = json.load(f)
        
    examples = [Example(**data) for data in examples_data]
    
    return examples


def generate_prompt() -> str:
    examples = _load_examples_from_json()

    task_prompt = PromptTemplate(
        template = """# Ontology Entities Extraction in Chemistry

## Task Overview
In the field of chemistry, we aim to find all concepts and entities including classes, individuals and data properties within an ontological framework. 

## Definitions

- **Class:** A class represents a broad category or group that can include multiple entities or concepts. If a concept A can be linked to a set of other concepts or entities {{B}}, and it can be stated that {{B}} are examples of A or belong to A, then A is a class.

- **Individual:** An individual is a distinct, singular entity or concept that does not include other entities. It is unique and cannot be subdivided into further examples or categories.

- **Data Property:** A data property is a concept that describes the characteristics of an entity. It is a property describing an entity itself by a value which means ONLY ONE ENTITY exclude itself appears. Also, a property describing the relationship between two entities is not data property.

## Task Instructions

1. **Analyze the Text:** Thoroughly read the provided text to understand the context.
2. **Extract Entities:** Identify and extract all relevant entities and concepts from the text.
3. **Find Data Properties:**
   - If the concept describes an attribute of an entity or a concept, classify it as a **"data property"**.
4. **Extract Information about the Entity:** Extract information in one sentence about the entity or concept in the text."""
    )
    
    examples_prompt = ""
    if examples:
        examples_prompt = "\n\n## Examples\n\n"
        for example in examples:
            examples_prompt += f"**Text:**\n    {example.context}\n\nOutput:\n"
            for concept in example.concepts:
                examples_prompt += f"Name: {concept.name}\n"
                examples_prompt += f"Is data property: {concept.is_data_property}\n"
                examples_prompt += f"Information: {concept.information}\n\n"
    
    output_format_prompt = PromptTemplate(
        template="""For each identified entity, output only:
Name: [Specific entity name/identifier]
Is data property: [True or False]
Information: [Information about the entity in one sentence]

If the entity has abbreviations, format its Name [Full name]([Abbreviation]).

Apply this structured approach to analyze the text I offer later and accurately extract the entities.
"""
    )

    final_prompt_template = PromptTemplate.from_template(
        "{task}\n{examples}\n{format}"
    )
    
    prompt_pipeline = PipelinePromptTemplate(
        final_prompt=final_prompt_template,
        pipeline_prompts=[
            ("task", task_prompt),
            ("examples", PromptTemplate.from_template(examples_prompt)),
            ("format", output_format_prompt)
        ]
    )
    
    return prompt_pipeline.format()


def parse_llm_output(response_content: str) -> Tuple[List[ClassMetaData], List[DataPropertyMetaData]]:
    class_concepts = []
    data_properties = []
    
    # 按空行分割每个概念块
    concept_blocks = [block.strip() for block in response_content.split('\n\n') if block.strip()]
    
    for block in concept_blocks:
        # 解析每个概念的属性
        properties = {}
        for line in block.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                properties[key.strip().lower()] = value.strip()
                
        # 提取关键信息
        name = properties.get('name', '')
        is_data_property_str = properties.get('is data property', '').lower()
        if is_data_property_str == 'true':
            is_data_property = True
        elif is_data_property_str == 'false':
            is_data_property = False
        else:
            raise ValueError(f"'Is data property' must be 'true' or 'false', got '{is_data_property_str}'")
            
        information = properties.get('information', '')
        
        # 根据is_data_property创建对应的元数据对象
        if is_data_property:
            data_property = DataPropertyMetaData(
                name=name,
                information=information
            )
            data_properties.append(data_property)
        else:
            class_concept = ClassMetaData(
                name=name,
                information=information
            )
            class_concepts.append(class_concept)
            
    return class_concepts, data_properties

def create_classes(ontology: Ontology, classes: List[ClassMetaData]):
    class_namespace = settings.ONTOLOGY_CONFIG["classes"]

    for class_meta in classes:
        # Check if class already exists
        name = class_meta.name.replace(" ", "_").lower()
        if not class_namespace[name] in ontology.classes():
            print(f"Class: {name} does not exist, creating...")
            # Create new class in ontology
            with class_namespace:
                new_class = types.new_class(name, (Thing,))
                
                new_class.embedding = class_meta.embedding
                
                new_class.location = [f"doi: {class_meta.location[0]} - page: {class_meta.location[1]}"]
                
                new_class.information = [class_meta.information]
        else:
            print(f"Class: {name} already exists")
            with class_namespace:
                class_to_update = class_namespace[name]
                print(class_to_update)
                class_to_update.location.append(f"doi: {class_meta.location[0]} - page: {class_meta.location[1]}")
                class_to_update.information.append(class_meta.information)

def create_individuals(ontology: Ontology, individuals: List[IndividualMetaData]):
    individual_namespace = settings.ONTOLOGY_CONFIG["individuals"]
    for individual_meta in individuals:
        name = individual_meta.name.replace(" ", "_").lower()
        if not individual_namespace[name] in ontology.individuals():
            print(f"Individual: {name} does not exist, creating...")
            with individual_namespace:
                new_individual = Thing(name)
                
                # Create embedding annotation property
                new_individual.embedding = individual_meta.embedding
                
                # Create location annotation property
                new_individual.location = [f"doi: {individual_meta.location[0]} - page: {individual_meta.location[1]}"]
                
                # Create information annotation property
                new_individual.information = [individual_meta.information]
        else:
            print(f"Individual: {name} already exists")
            with individual_namespace:
                individual_to_update = individual_namespace[name]
                individual_to_update.location.append(f"doi: {individual_meta.location[0]} - page: {individual_meta.location[1]}")
                individual_to_update.information.append(individual_meta.information)

def create_data_properties(ontology: Ontology, data_properties: List[DataPropertyMetaData]):
    data_property_namespace = settings.ONTOLOGY_CONFIG["data_properties"]
    for data_property_meta in data_properties:
        name = data_property_meta.name.replace(" ", "_").lower()
        if not data_property_namespace[name] in ontology.data_properties():
            print(f"Data property: {name} does not exist, creating...")
            with data_property_namespace:
                new_data_property = types.new_data_property(name)
                
                new_data_property.embedding = data_property_meta.embedding
                
                new_data_property.location = [f"doi: {data_property_meta.location[0]} - page: {data_property_meta.location[1]}"]
                
                new_data_property.information = [data_property_meta.information]
        else:
            print(f"Data property: {name} already exists")
            with data_property_namespace:
                data_property_to_update = data_property_namespace[name]
                print(data_property_to_update)
                data_property_to_update.location.append(f"doi: {data_property_meta.location[0]} - page: {data_property_meta.location[1]}")
                data_property_to_update.information.append(data_property_meta.information)



