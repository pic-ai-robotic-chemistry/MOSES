import dspy

from autology_constructor.signatures import ExtractOntologyEntities, ExtractOntologyElements, ExtractOntologyDataProperties, ExtractOntologyObjectProperties
from autology_constructor.modules import Assessment

max_backtracks = 3

class ChemOntologyWithEntitiesAssertions(dspy.Module):
    def __init__(self):
        super().__init__()

        self.entities_extractor = dspy.ChainOfThought(ExtractOntologyEntities)
        self.assessor = Assessment(assertions=True)
    
    def forward(self, context):
        entities = self.entities_extractor(text=context)
        assertions, score_info = self.assessor(assessed_text=context, assessment_ontology=entities.ontology_entities)
        qualified = [x[0] for x in assertions.values()]
        suggestion = [x[1] for x in assertions.values()]
        dspy.Suggest(all(qualified),"".join(suggestion),target_module=self.entities_extractor)
        return dspy.Prediction(context=context, ontology_entities=entities.ontology_entities, score_info=score_info)

class ChemOntologyWithElementsAssertions(dspy.Module):
    def __init__(self):
        super().__init__()

        self.elements_extractor = dspy.ChainOfThought(ExtractOntologyElements)
        self.assessor = Assessment(assertions=True)
    
    def forward(self, context, entities):
        elements = self.elements_extractor(text=context, ontology_entities=entities.ontology_entities)
        assertions, score_info = self.assessor(assessed_text=context, assessment_ontology=elements.ontology_elements)
        qualified = [x[0] for x in assertions.values()]
        suggestion = [x[1] for x in assertions.values()]
        dspy.Suggest(all(qualified),"".join(suggestion),target_module=self.elements_extractor)

        return dspy.Prediction(context=context, ontology_elements=elements.ontology_elements, score_info=score_info)

class ChemOntologyWithDataPropertiesAssertions(dspy.Module):
    def __init__(self):
        super().__init__()

        self.data_properties_extractor = dspy.ChainOfThought(ExtractOntologyDataProperties)
        self.assessor = Assessment(assertions=True)

    def forward(self, context, entities):
        data_properties = self.data_properties_extractor(text=context, ontology_entities=entities.ontology_entities)
        assertions, score_info = self.assessor(assessed_text=context, assessment_ontology=data_properties.ontology_data_properties)
        qualified = [x[0] for x in assertions.values()]
        suggestion = [x[1] for x in assertions.values()]
        dspy.Suggest(all(qualified),"".join(suggestion),target_module=self.data_properties_extractor)
        return dspy.Prediction(context=context, ontology_entities=entities.ontology_entities, ontology_data_properties=data_properties.ontology_data_properties, score_info=score_info)

class ChemOntologyWithObjectPropertiesAssertions(dspy.Module):
    def __init__(self):
        super().__init__()

        self.object_properties_extractor = dspy.ChainOfThought(ExtractOntologyObjectProperties)
        self.assessor = Assessment(assertions=True)

    def forward(self, context, entities):
        object_properties = self.object_properties_extractor(text=context, ontology_entities=entities.ontology_entities)
        assertions, score_info = self.assessor(assessed_text=context, assessment_ontology=object_properties.ontology_object_properties)
        qualified = [x[0] for x in assertions.values()]
        suggestion = [x[1] for x in assertions.values()]
        dspy.Suggest(all(qualified),"".join(suggestion),target_module=self.object_properties_extractor)
        return dspy.Prediction(context=context, ontology_entities=entities.ontology_entities, ontology_object_properties=object_properties.ontology_object_properties, score_info=score_info)

chemonto_with_entities_assertions = ChemOntologyWithEntitiesAssertions().activate_assertions(max_backtracks=max_backtracks)
chemonto_with_elements_assertions = ChemOntologyWithElementsAssertions().activate_assertions(max_backtracks=max_backtracks)
chemonto_with_data_properties_assertions = ChemOntologyWithDataPropertiesAssertions().activate_assertions(max_backtracks=max_backtracks)
chemonto_with_object_properties_assertions = ChemOntologyWithObjectPropertiesAssertions().activate_assertions(max_backtracks=max_backtracks) 