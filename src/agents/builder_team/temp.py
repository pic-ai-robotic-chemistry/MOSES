from owlready2 import *
from config import settings

ontology = settings.ONTOLOGY_CONFIG["ontology"]

results = default_world.sparql_query("""
    SELECT ?class
    WHERE {
      ?class a owl:Class .
      FILTER NOT EXISTS { ?subclass rdfs:subClassOf ?class }
    }
""")

list_results = list(results)

print(list_results)

# print(type(list_results[0][0]))