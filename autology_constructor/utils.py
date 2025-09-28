from autology_constructor.base_data_structures import OntologyElements, OntologyEntities, OntologyDataProperties, OntologyObjectProperties

def flatten_dict(d, parent_key=''):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key} with {k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

def ontology_entities_to_string(ontology_entities: OntologyEntities) -> str:
    result = []
    
    result.append("Entities:")
    for entity in ontology_entities.entities:
        result.append(f"  - Name: {entity.name}")
        result.append(f"    Information: {entity.information}")
            
    return "\n".join(result)

def ontology_elements_to_string(ontology_elements: OntologyElements) -> str:
    result = []
    
    result.append("Entity Hierarchy:")
    if ontology_elements.hierarchy is not None:
        for hierarchy in ontology_elements.hierarchy:
            result.append(f"  - Subclass: {hierarchy.subclass}")
            result.append(f"    Superclass: {hierarchy.superclass}")
            result.append(f"    Information: {hierarchy.information}")
    
    result.append("\nDisjoint Classes:")
    if ontology_elements.disjointness is not None:
        for disjoint in ontology_elements.disjointness:
            result.append(f"  - Class 1: {disjoint.class1}")
            result.append(f"    Class 2: {disjoint.class2}")
            
    return "\n".join(result)

def ontology_data_properties_to_string(ontology_data_properties: OntologyDataProperties) -> str:
    result = []
    
    result.append("Data Properties:")
    if ontology_data_properties.data_properties is not None:
        for prop in ontology_data_properties.data_properties:
            result.append(f"  - Name: {prop.name}")
            if prop.values is not None:
                values_str = "\n            ".join(f"{k}: {v}" for k, v in flatten_dict(prop.values).items())
                result.append(f"    Values: {values_str}")
            result.append(f"    Information: {prop.information}")
            
    return "\n".join(result)

def ontology_object_properties_to_string(ontology_object_properties: OntologyObjectProperties) -> str:
    result = []
    
    result.append("Object Properties:")
    for prop in ontology_object_properties.object_properties:
        result.append(f"  - Name: {prop.name}")
        if prop.instances is not None:
            for instance in prop.instances:
                result.append("    Instance:")
                if instance.domain is not None:
                    result.append("      Domain:")
                    if instance.domain.entity is not None:
                        result.append(f"        Entity: {instance.domain.entity}")
                    if instance.domain.type is not None:
                        result.append(f"        Type: {instance.domain.type}")
                if instance.range is not None:
                    result.append("      Range:")
                    if instance.range.entity is not None:
                        result.append(f"        Entity: {instance.range.entity}")
                    if instance.range.type is not None:
                        result.append(f"        Type: {instance.range.type}")
                result.append(f"      Restriction: {instance.restriction}")
        result.append(f"    Information: {prop.information}")
        
    return "\n".join(result)