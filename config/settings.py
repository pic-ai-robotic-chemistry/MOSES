import os
import re
import yaml
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

import owlready2
from owlready2 import onto_path, get_ontology, Ontology, Namespace

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default_api_key")


path_matcher = re.compile(r'\$\{([^}^{]+)\}')
key_matcher = re.compile(r'\{\{([^}^{]+)\}\}')

def path_constructor(loader, node):
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    project_root = os.environ.get(env_var, '')
    return os.path.join(project_root, value[match.end():])

def resolve_key_references(yaml_dict):
    def _resolve_value(value, current_level_dict):
        if isinstance(value, str):
            match = key_matcher.search(value)
            if match:
                key = match.group(1).strip()
                if key in current_level_dict:
                    return value.replace(match.group(0), str(current_level_dict[key]))
                elif key in yaml_dict:
                    return value.replace(match.group(0), str(yaml_dict[key]))
        return value

    resolved_dict = {}
    for key, value in yaml_dict.items():
        if isinstance(value, dict):
            resolved_dict[key] = resolve_key_references(value)
        else:
            resolved_dict[key] = _resolve_value(value, yaml_dict)
    return resolved_dict

yaml.SafeLoader.add_implicit_resolver('!path', path_matcher, None)
yaml.SafeLoader.add_constructor('!path', path_constructor)

config_path = Path(__file__).parent / "settings.yaml"
with open(config_path, "r", encoding='utf-8') as f:
    yaml_settings = yaml.safe_load(f)
    if 'PROJECT_ROOT' in os.environ:
        yaml_settings['PROJECT_ROOT'] = os.environ['PROJECT_ROOT']
    yaml_settings = resolve_key_references(yaml_settings)

# --- Set Java Path Globally (Step 1 - Added) ---
_ontology_yaml_config = yaml_settings.get("ontology", {}) # Get ontology section safely

java_path_from_yaml = _ontology_yaml_config.get("java_exe")
if java_path_from_yaml:
    java_path_obj = Path(java_path_from_yaml) 
    if not java_path_obj.exists() or not java_path_obj.is_file():
         print(f"Warning: Specified JAVA_EXE path from YAML ('{java_path_from_yaml}') does not exist or is not a file.")
    # Set the global variable for owlready2
    owlready2.JAVA_EXE = str(java_path_obj) 
    print(f"Setting owlready2.JAVA_EXE globally from settings.yaml: {owlready2.JAVA_EXE}")
else:
     print("Warning: 'java_exe' not found in settings.yaml ontology section. Owlready2 reasoning might fail if Java is required.")

# --- Define OntologySettings Class ---
@dataclass
class OntologySettings:
    base_iri: str
    ontology_file_name: str
    directory_path: str
    # closed_ontology_file_name: str

    _ontology: Optional[Ontology] = field(init=False, repr=False, default=None)
    _world: Optional[Any] = field(init=False, repr=False, default=None)  # 独立的owlready2 World
    _namespaces: Dict[str, Namespace] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        onto_path.append(self.directory_path)
        try:
            # 为每个OntologySettings实例创建独立的owlready2 World
            # 这样避免多个实例共享同一个本体对象
            from owlready2 import World
            self._world = World()
            self._ontology = self._world.get_ontology(self.ontology_iri).load(only_local=True)
        except Exception as e:
            print(f"Error loading ontology {self.ontology_iri}: {e}")
            raise RuntimeError(f"Failed to load ontology: {self.ontology_iri}") from e

    @property
    def ontology_iri(self) -> str:
        return self.base_iri.rstrip('/') + '/' + self.ontology_file_name.lstrip('/')

    # @property
    # def closed_ontology_iri(self) -> str:
    #     return self.base_iri.rstrip('/') + '/' + self.closed_ontology_file_name.lstrip('/')

    @property
    def ontology(self) -> Ontology:
        if self._ontology is None:
            raise RuntimeError("Ontology has not been loaded successfully.")
        return self._ontology

    def get_namespace(self, suffix: str) -> Namespace:
        full_iri = self.base_iri.rstrip('/') + '/' + suffix.lstrip('/')
        print(full_iri)
        if full_iri not in self._namespaces:
            if self._ontology is None:
                raise RuntimeError("Cannot get namespace because ontology is not loaded.")
            self._namespaces[full_iri] = self.ontology.get_namespace(full_iri)
        return self._namespaces[full_iri]

    @property
    def meta(self) -> Namespace:
        return self.get_namespace("meta/")

    @property
    def classes(self) -> Namespace:
        return self.get_namespace("classes/")

    @property
    def individuals(self) -> Namespace:
        return self.get_namespace("individuals/")

    @property
    def data_properties(self) -> Namespace:
        return self.get_namespace("data_properties/")

    @property
    def object_properties(self) -> Namespace:
        return self.get_namespace("object_properties/")

    @property
    def axioms(self) -> Namespace:
        return self.get_namespace("axioms/")

# --- Instantiate Settings Objects ---
# _ontology_settings_data already has java_exe popped in previous step
# Ensure it's still the case or adjust if the dict is re-read
_ontology_settings_data = yaml_settings.get("ontology", {})
_ontology_settings_data.pop('java_exe', None) # Pop again to be safe
ONTOLOGY_SETTINGS = OntologySettings(**_ontology_settings_data)


LLM_CONFIG = yaml_settings["LLM"]
EXTRACTOR_EXAMPLES_CONFIG = yaml_settings["extractor_examples"]
DATASET_CONSTRUCTION_CONFIG = yaml_settings["dataset_construction"]
ENTITY_RETRIEVAL_CONFIG = yaml_settings.get("entity_retrieval", {
    "top_k": 15,
    "bm25_weight": 0.5,
    "jaccard_weight": 0.5,
    "trigram_size": 3,
    "min_score_threshold": 0.1
})

_ASSESSMENT_CRITERIA_SCORE_CONFIG = {
    "entity_score": 9,
    "hierachy_score": 7,
    "disjointness_score": 6,
    "data_property_score": 4,
    "object_property_score": 8,
    "ontology_structure_score": 4,
    "overall_content_score": 24,
    "weights": {
        "entities": 0.3,
        "elements": 0.15,
        "data_properties": 0.15,
        "object_properties": 0.25,
        "overall": 0.15
    }
}
ASSESSMENT_CRITERIA_CONFIG = {
    "element_property_split": 3,
    "entity_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["entity_score"],
    "entity": f"""You are an expert chemist. Based on text, Entity Accuracy Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["entity_score"]} points):
Award 1 point for each criterion met:
- Classes cover all granularity levels (1 point)
- Entities capture concepts across all levels of abstraction, from highly abstract to highly specific mentioned in the text (1 point)
- Entity names are specific and meaningful without being overly generic (1 point)
- Entity definitions align with established chemical concepts (1 point)
- Entities are properly consolidated without redundancy (1 point)
- Entity design supports future expansion and integration with other ontologies (1 point)
- Entities can be effectively applied across different chemical subdomains (1 point)
- Entities have chemical meaning and accuracy even without the context of text and information fields (1 point)
- Entity full names and abbreviations do not contain square brackets (1 point)""",
    "hierachy_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["hierachy_score"],
    "hierachy": f"""You are an expert chemist. Based on text, Class Hierarchy Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["hierachy_score"]} points):
Award 1 point for each criterion met:
- Class hierarchies align with valid chemical taxonomies (1 point)
- Subclass relationships are logically sound, chemically meaningful and accurate even without the context of text and information fields (1 point)
- Multiple inheritance is used appropriately when context explicitly mentions a class is a subclass of multiple classes (1 point)
- Hierarchical relationships are stated or implied in the text (1 point)
- Superclass-subclass pairs maintain consistent semantic meaning (1 point)
- No circular or contradictory hierarchical relationships (1 point)
If the ontology has no subclass-superclass relationships, check if the text contains any hierarchical relationships. If there are no hierarchical relationships mentioned in the text, award full points. If hierarchical relationships exist in the text but are missing from the ontology, award 0 points.""",
    "disjointness_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["disjointness_score"],
    "disjointness": f"""You are an expert chemist. Based on text, Disjoint Classes Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["disjointness_score"]} points):
Award 1 point for each criterion met:
- Disjoint class relationships are explicitly stated in the text (1 point)
- Correctly identifies mutually exclusive class relationships in chemical concepts (1 point)
- Disjoint classes are comprehensive without missing key exclusions (1 point)
- Disjoint classes reflect real chemical incompatibilities (1 point)
- Disjoint class assertions do not create logical contradictions (1 point)
- Disjoint relationships support chemical reasoning and inference (1 point)
If the ontology has no disjoint class relationships, check if the text contains any disjoint class relationships. If there are no disjoint class relationships mentioned in the text, award full points. If disjoint class relationships exist in the text but are missing from the ontology, award 0 points.""",
    "data_property_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["data_property_score"],
    "data_property": f"""You are an expert chemist. Based on text, Data Property Correctness Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["data_property_score"]} points):
Award 1 point for each criterion met:
- Data properties are truly value-based attributes (1 point)
- Each data property describes a single measurable characteristic (1 point)
- Values of each data property are explicitly stated in the text (1 point)
- Data properties are chemically meaningful and accurate even without the context of text and information fields (1 point)
If the ontology has no data properties, check if the text contains any data properties. If there are no data properties mentioned in the text, award full points. If data properties exist in the text but are missing from the ontology, award 0 points.""",
    "object_property_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["object_property_score"],
    "object_property": f"""You are an expert chemist. Based on text, Object Property Completeness Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["object_property_score"]} points):
Award 1 point for each criterion met:
- Object properties capture all key chemical knowledges and reflect valid chemical principles (1 point)
- The words used in object property names are accurate, specific, and academic (1 point)
- Object property names and instances are meaningful, specific and accurate even without the context of text and information fields (1 point)
- Object property instances are aligned with the context of text (1 point)
- Domain and range specifications are precise and accurate without loss of specificity from using overly broad classes (1 point)
- Relationship restrictions ('only'/'some') are properly applied (1 point)
- If multiple object properties describe symmetric aspects of the same chemical scope, their instances should be aligned in granularity (1 point)
- Object properties names start with is_ or has_ to indicate the property expresses a complex subclass-superclass relationship or a property (1 point)
""",
    "ontology_structure_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["ontology_structure_score"],
    "ontology_structure": f"""You are an expert chemist. Based on text, Ontology Structure Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["ontology_structure_score"]} points):
Award 1 point for each criterion met:
- Entities span all levels of chemical granularity mentioned in the text (1 point)
- Properties and relationships form a coherent chemical knowledge graph (1 point)
- The ontology maintains semantic clarity independent of source text (1 point)
- Cross-references between concepts are meaningful and accurate (1 point)
- Definitions and usage of entities are consistent throughout the ontology (1 point)""",
    "overall_content_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["overall_content_score"],
    "overall_content": f"""You are an expert chemist. Based on text, Overall Score (0-{_ASSESSMENT_CRITERIA_SCORE_CONFIG["overall_content_score"]} points):
Each criterion is evaluated based on three levels - excellent (6 points), adequate (3 points), or medium (0 points). If you think the ontology is between levels, you can give it a intermediate score. 0 points means the ontology has medium quality rather than low quality in this criterion. More detailed criteria are as follows:

- Extraction Accuracy (6 points):
  * Excellent: No errors in entity and property extraction
  * Adequate: Minor non-critical errors present 
  * Medium: Some extraction errors exist

- Professional Validity (6 points):
  * Excellent: Extractions fully align with chemical expertise
  * Adequate: Most extractions align with chemical knowledge
  * Medium: Some deviations from chemical principles

- Comprehensiveness (6 points):
  * Excellent: Complete extraction of all relevant information
  * Adequate: Most key information captured
  * Medium: Some key information missing

- Knowledge Independence (6 points):
  * Excellent: Entities and properties can be accurately understood without source text context
  * Adequate: Most entities and properties are clear without background text
  * Medium: Some understanding requires source text context""",
    "full_score": _ASSESSMENT_CRITERIA_SCORE_CONFIG["entity_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["hierachy_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["disjointness_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["data_property_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["object_property_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["ontology_structure_score"] + _ASSESSMENT_CRITERIA_SCORE_CONFIG["overall_content_score"]
}