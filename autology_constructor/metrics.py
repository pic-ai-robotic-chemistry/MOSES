from autology_constructor.modules import Assessment
from config.settings import ASSESSMENT_CRITERIA_CONFIG

def assessor_metric(gold, pred, trace=None):
    standard_score = gold['score']
    assessor_score = pred['assessment_score']
    return standard_score == assessor_score

def metric(gold, pred, trace=None, verbose=False):
    weights = ASSESSMENT_CRITERIA_CONFIG["weights"]
    assessment = Assessment()
    entities_score = assessment(assessed_text=gold['context'], assessment_ontology=pred['ontology_entities'])
    elements_score = assessment(assessed_text=gold['context'], assessment_ontology=pred['ontology_elements']) 
    data_properties_score = assessment(assessed_text=gold['context'], assessment_ontology=pred['ontology_data_properties'])
    object_properties_score = assessment(assessed_text=gold['context'], assessment_ontology=pred['ontology_object_properties'])
    overall_score = assessment(assessed_text=gold['context'], assessment_ontology=(pred['ontology_entities'], pred['ontology_elements'], pred['ontology_data_properties'], pred['ontology_object_properties']))
    res = (entities_score * weights["entities"] + 
           elements_score * weights["elements"] + 
           data_properties_score * weights["data_properties"] + 
           object_properties_score * weights["object_properties"] + 
           overall_score * weights["overall"])
    if verbose:
        print(f"Entities Score: {entities_score}")
        print(f"Elements Score: {elements_score}")
        print(f"Data Properties Score: {data_properties_score}")
        print(f"Object Properties Score: {object_properties_score}")
        print(f"Overall Score: {overall_score}")
        print(f"Final Score: {res}")
    return res