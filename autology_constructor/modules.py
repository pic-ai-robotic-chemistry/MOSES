from numpy import mean

import dspy


from autology_constructor.base_data_structures import OntologyElements, OntologyDataProperties, OntologyObjectProperties, OntologyEntities
from autology_constructor.signatures import ExtractOntologyElements, ExtractOntologyDataProperties, ExtractOntologyObjectProperties, ExtractOntologyEntities, Assess
from autology_constructor.utils import ontology_entities_to_string, ontology_elements_to_string, ontology_data_properties_to_string, ontology_object_properties_to_string

from config.settings import ASSESSMENT_CRITERIA_CONFIG

max_backtracks = 3

entity = ASSESSMENT_CRITERIA_CONFIG["entity"]
entity_score = ASSESSMENT_CRITERIA_CONFIG["entity_score"]
hierachy = ASSESSMENT_CRITERIA_CONFIG["hierachy"]
hierachy_score = ASSESSMENT_CRITERIA_CONFIG["hierachy_score"]
disjointness = ASSESSMENT_CRITERIA_CONFIG["disjointness"]
disjointness_score = ASSESSMENT_CRITERIA_CONFIG["disjointness_score"]
data_property = ASSESSMENT_CRITERIA_CONFIG["data_property"]
data_property_score = ASSESSMENT_CRITERIA_CONFIG["data_property_score"]
object_property = ASSESSMENT_CRITERIA_CONFIG["object_property"]
object_property_score = ASSESSMENT_CRITERIA_CONFIG["object_property_score"]
ontology_structure = ASSESSMENT_CRITERIA_CONFIG["ontology_structure"]
ontology_structure_score = ASSESSMENT_CRITERIA_CONFIG["ontology_structure_score"]
overall_content = ASSESSMENT_CRITERIA_CONFIG["overall_content"]
overall_content_score = ASSESSMENT_CRITERIA_CONFIG["overall_content_score"]
full_score = ASSESSMENT_CRITERIA_CONFIG["full_score"]

class BaseEntityExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.entities_extractor = dspy.ChainOfThought(ExtractOntologyEntities)
    
    def forward(self, context):
        return self.entities_extractor(text=context)

class BaseElementExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.elements_extractor = dspy.ChainOfThought(ExtractOntologyElements)
    
    def forward(self, context, ontology_entities):
        # Ensure ontology_entities is passed as a string if the signature expects it
        # Or, ensure the signature and subsequent processing can handle the OntologyEntities object directly
        return self.elements_extractor(text=context, ontology_entities=ontology_entities)

class BaseDataPropertyExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.data_properties_extractor = dspy.ChainOfThought(ExtractOntologyDataProperties)
    
    def forward(self, context, ontology_entities):
        return self.data_properties_extractor(text=context, ontology_entities=ontology_entities)

class BaseObjectPropertyExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.object_properties_extractor = dspy.ChainOfThought(ExtractOntologyObjectProperties)
    
    def forward(self, context, ontology_entities):
        return self.object_properties_extractor(text=context, ontology_entities=ontology_entities)

class ChemOntology(dspy.Module):
    def __init__(self):
        super().__init__()
        self.entities_extractor = BaseEntityExtractor()
        self.elements_extractor = BaseElementExtractor()
        self.data_properties_extractor = BaseDataPropertyExtractor()
        self.object_properties_extractor = BaseObjectPropertyExtractor()
    
    def forward(self, context):
        entities_pred = self.entities_extractor(context=context)
        entities_output = entities_pred.ontology_entities

        elements_pred = self.elements_extractor(context=context, ontology_entities=entities_output)
        elements_output = elements_pred.ontology_elements

        data_properties_pred = self.data_properties_extractor(context=context, ontology_entities=entities_output)
        data_properties_output = data_properties_pred.ontology_data_properties

        object_properties_pred = self.object_properties_extractor(context=context, ontology_entities=entities_output)
        object_properties_output = object_properties_pred.ontology_object_properties

        return dspy.Prediction(
            context=context, 
            ontology_entities=entities_output,
            ontology_elements=elements_output,
            ontology_data_properties=data_properties_output,
            ontology_object_properties=object_properties_output
        )

class ChemOntologyWithRefinement(dspy.Module):
    def __init__(self):
        super().__init__()
        self.entity_extractor = RefinedEntityExtractor()
        self.element_extractor = RefinedElementExtractor()
        self.data_property_extractor = RefinedDataPropertyExtractor()
        self.object_property_extractor = RefinedObjectPropertyExtractor()

    def forward(self, context):
        # Step 1: Extract and refine entities
        entities_prediction = self.entity_extractor(context=context)
        # The output of Refine is the student's last successful (or max_iters) prediction.
        # This Prediction object should contain .ontology_entities
        refined_entities = entities_prediction.ontology_entities 

        # Step 2: Extract and refine elements using refined entities
        elements_prediction = self.element_extractor(context=context, ontology_entities=refined_entities)
        refined_elements = elements_prediction.ontology_elements

        # Step 3: Extract and refine data properties using refined entities
        data_properties_prediction = self.data_property_extractor(context=context, ontology_entities=refined_entities)
        refined_data_properties = data_properties_prediction.ontology_data_properties

        # Step 4: Extract and refine object properties using refined entities
        object_properties_prediction = self.object_property_extractor(context=context, ontology_entities=refined_entities)
        refined_object_properties = object_properties_prediction.ontology_object_properties

        return dspy.Prediction(
            context=context, 
            ontology_entities=refined_entities,
            ontology_elements=refined_elements,
            ontology_data_properties=refined_data_properties,
            ontology_object_properties=refined_object_properties
        )

class Assessment(dspy.Module):
    def __init__(self, verbose=False, assertions=False):
        super().__init__()
        self.assessor = dspy.ChainOfThought(Assess)
        self.verbose = verbose
        self.assertions = assertions
    
    def forward(self, assessed_text, assessment_ontology):
        verbose = self.verbose
        assertions = self.assertions
        if isinstance(assessment_ontology, OntologyEntities):
            print("entities")
            assessment_ontology = ontology_entities_to_string(assessment_ontology)
            print(assessment_ontology)
            criteria_list = [entity]
            score_list = [
                self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_score for criteria in criteria_list
            ]
            score_denominators = [entity_score]
            normalized_score_list = [score/denom for score, denom in zip(score_list, score_denominators)]
            if verbose or assertions:
                reason_list = [
                    self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_reason for criteria in criteria_list
                ]
        elif isinstance(assessment_ontology, OntologyElements):
            print("elements")
            assessment_ontology = ontology_elements_to_string(assessment_ontology)
            print(assessment_ontology)
            criteria_list = [hierachy, disjointness]
            score_list = [
                self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_score for criteria in criteria_list
            ]
            score_denominators = [hierachy_score, disjointness_score]
            normalized_score_list = [score/denom for score, denom in zip(score_list, score_denominators)]
            if verbose or assertions:
                reason_list = [
                    self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_reason for criteria in criteria_list
                ]
        elif isinstance(assessment_ontology, (OntologyDataProperties, OntologyObjectProperties)):
            print("properties")
            if isinstance(assessment_ontology, OntologyDataProperties):
                assessment_ontology = ontology_data_properties_to_string(assessment_ontology)
                criteria_list = [data_property]
                score_denominators = [data_property_score]
            else:
                assessment_ontology = ontology_object_properties_to_string(assessment_ontology)
                criteria_list = [object_property]
                score_denominators = [object_property_score]
            print(assessment_ontology)
            score_list = [
                self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_score for criteria in criteria_list
            ]
            normalized_score_list = [score/denom for score, denom in zip(score_list, score_denominators)]
            if verbose or assertions:
                reason_list = [
                    self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_reason for criteria in criteria_list
                ]
        elif isinstance(assessment_ontology, tuple) and len(assessment_ontology) == 4:
            if isinstance(assessment_ontology[0], OntologyEntities) and isinstance(assessment_ontology[1], OntologyElements) and isinstance(assessment_ontology[2], OntologyDataProperties) and isinstance(assessment_ontology[3], OntologyObjectProperties):
                print("entities, elements and properties")
                assessment_ontology = ontology_entities_to_string(assessment_ontology[0]) + "\n" + ontology_elements_to_string(assessment_ontology[1]) + "\n" + ontology_data_properties_to_string(assessment_ontology[2]) + "\n" + ontology_object_properties_to_string(assessment_ontology[3])
                criteria_list = [ontology_structure, overall_content]
                score_list = [
                    self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_score for criteria in criteria_list
                ]
                score_denominators = [ontology_structure_score, overall_content_score]
                normalized_score_list = [score/denom for score, denom in zip(score_list, score_denominators)]
                if verbose or assertions:
                    reason_list = [
                        self.assessor(assessed_text=assessed_text, assessment_ontology=assessment_ontology, assessment_criteria=criteria).assessment_reason for criteria in criteria_list
                    ]
        else:
            raise ValueError("assessment_ontology 必须是 OntologyEntities、OntologyElements、OntologyDataProperties、OntologyObjectProperties 或者它们的元组类型")
        if assertions:
            result_dict = {}
            for i, criteria_name in enumerate(criteria_list):
                name = criteria_name.split('\n')[0].split('(')[0].strip().lower().replace(' ', '_')
                threshold = score_denominators[i] - (4 if name == 'overall_content' else 0.5)
                result_dict[name] = (score_list[i] >= threshold, reason_list[i])

            score_text = '\n'.join([f"{criteria.split('(')[0].strip()} Score: {score}" for criteria, score in zip(criteria_list, normalized_score_list)])
            reason_text = '\n'.join([f"{criteria.split('(')[0].strip()}: {reason}" for criteria, reason in zip(criteria_list, reason_list)])

            return (
                result_dict,
                f"""
{score_text}

Total Score: {sum(score_list)}/{sum(score_denominators)}
Percentage Score: {mean(normalized_score_list)*100:.2f}%

Reason:
{reason_text}
"""
            )

        if verbose:
            score_text = '\n'.join([f"{criteria.split('(')[0].strip()} Score: {score}" for criteria, score in zip(criteria_list, normalized_score_list)])
            reason_text = '\n'.join([f"{criteria.split('(')[0].strip()}: {reason}" for criteria, reason in zip(criteria_list, reason_list)])

            return f"""
{score_text}

Total Score: {sum(score_list)}/{sum(score_denominators)}
Percentage Score: {mean(normalized_score_list)*100:.2f}%

Reason:
{reason_text}
"""

        return mean(normalized_score_list)

def validate_entities_reward(args: dict, pred: dspy.Prediction) -> float:
    assessed_text = args['context']
    assessment_ontology_object = pred.ontology_entities

    assessor_module = Assessment(assertions=False, verbose=False) 
    score = assessor_module(assessed_text=assessed_text, assessment_ontology=assessment_ontology_object)
    
    return score

def validate_elements_reward(args: dict, pred: dspy.Prediction) -> float:
    assessed_text = args['context']
    assessment_ontology_object = pred.ontology_elements
    # ontology_entities_input = args['ontology_entities'] # This might be needed if Assessment for elements requires it

    assessor_module = Assessment(assertions=False, verbose=False)
    score = assessor_module(assessed_text=assessed_text, assessment_ontology=assessment_ontology_object)
    return score

def validate_data_properties_reward(args: dict, pred: dspy.Prediction) -> float:
    assessed_text = args['context']
    assessment_ontology_object = pred.ontology_data_properties
    # ontology_entities_input = args['ontology_entities']

    assessor_module = Assessment(assertions=False, verbose=False)
    score = assessor_module(assessed_text=assessed_text, assessment_ontology=assessment_ontology_object)
    return score

def validate_object_properties_reward(args: dict, pred: dspy.Prediction) -> float:
    assessed_text = args['context']
    assessment_ontology_object = pred.ontology_object_properties
    # ontology_entities_input = args['ontology_entities']

    assessor_module = Assessment(assertions=False, verbose=False)
    score = assessor_module(assessed_text=assessed_text, assessment_ontology=assessment_ontology_object)
    return score

class RefinedEntityExtractor(dspy.Module):
    def __init__(self, threshold=0.95):
        super().__init__()
        self.base_extractor = BaseEntityExtractor()
        self.refined_extractor = dspy.Refine(
            module=self.base_extractor, 
            reward_fn=validate_entities_reward, 
            N=max_backtracks,
            threshold=threshold
        )

    def forward(self, context):
        return self.refined_extractor(context=context)

class RefinedElementExtractor(dspy.Module):
    def __init__(self, threshold=0.95):
        super().__init__()
        self.base_extractor = BaseElementExtractor()
        self.refined_extractor = dspy.Refine(
            module=self.base_extractor, 
            reward_fn=validate_elements_reward, 
            N=max_backtracks,
            threshold=threshold
        )

    def forward(self, context, ontology_entities):
        return self.refined_extractor(context=context, ontology_entities=ontology_entities)

class RefinedDataPropertyExtractor(dspy.Module):
    def __init__(self, threshold=0.95):
        super().__init__()
        self.base_extractor = BaseDataPropertyExtractor()
        self.refined_extractor = dspy.Refine(
            module=self.base_extractor, 
            reward_fn=validate_data_properties_reward, 
            N=max_backtracks,
            threshold=threshold
        )

    def forward(self, context, ontology_entities):
        return self.refined_extractor(context=context, ontology_entities=ontology_entities)

class RefinedObjectPropertyExtractor(dspy.Module):
    def __init__(self, threshold=0.95):
        super().__init__()
        self.base_extractor = BaseObjectPropertyExtractor()
        self.refined_extractor = dspy.Refine(
            module=self.base_extractor, 
            reward_fn=validate_object_properties_reward, 
            N=max_backtracks,
            threshold=threshold
        )

    def forward(self, context, ontology_entities):
        return self.refined_extractor(context=context, ontology_entities=ontology_entities)


# chemonto_with_entities_assertions = ChemOntologyWithEntitiesAssertions().activate_assertions(max_backtracks=max_backtracks)

# Instantiate the new main orchestrator module
chemonto_refined = ChemOntologyWithRefinement()

# Instantiate the base orchestrator module (without refinement)
chemonto_base = ChemOntology()
