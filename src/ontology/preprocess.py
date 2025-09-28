from owlready2 import *
import numpy as np
import datetime

from config.settings import ONTOLOGY_SETTINGS


def create_metadata_properties():
    """Create necessary metadata classes and properties in the ontology"""
    ontology = ONTOLOGY_SETTINGS.ontology
    meta = ONTOLOGY_SETTINGS.meta
    
    with ontology:
        # 创建SourcedInformation类
        if not meta.SourcedInformation in ontology.classes():
            print("Creating SourcedInformation class...")
            class SourcedInformation(Thing):
                namespace = meta
        si = meta.SourcedInformation
        # 创建content和source属性
        if not meta.content in ontology.data_properties():
            print("Creating content property...")
            class content(DataProperty):
                namespace = meta
                domain = [si]
                range = [str]
                
        if not meta.source in ontology.data_properties():
            print("Creating source property...")
            class source(DataProperty):
                namespace = meta
                domain = [si]
                range = [str]

        if not meta.file_path in ontology.data_properties():
            print("Creating file_path property...")
            class file_path(DataProperty):
                namespace = meta
                domain = [si]
                range = [str]

        # 创建type属性
        if not meta.type in ontology.data_properties():
            print("Creating type property...")
            class type(DataProperty):
                namespace = meta
                domain = [si]
                range = [str]
        
        # 创建property属性
        if not meta.property in ontology.data_properties():
            print("Creating property property...")
            class property(DataProperty):
                namespace = meta
                domain = [si]
                range = [str]

        # 创建has_information对象属性
        if not meta.has_information in ontology.object_properties():
            print("Creating has_information property...")
            class has_information(ObjectProperty):
                namespace = meta
                # domain = [Thing]
                range = [si]
    
    ontology.save()



