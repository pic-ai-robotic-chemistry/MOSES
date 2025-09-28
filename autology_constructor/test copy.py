from owlready2 import *
import owlready2.base
import owlready2.class_construct
import pytest
# Removed tempfile, os, shutil as they are no longer needed for temp ontology

from config.settings import OntologySettings # Keep this
# Keep OntologyTools import
from autology_constructor.idea.query_team.ontology_tools import OntologyTools

ontology_settings = OntologySettings(
    base_iri="http://www.test.org/chem_ontologies/",
    ontology_file_name="backup-2.owl",
    directory_path="data/ontology/",
    closed_ontology_file_name=None
)

ontology_tools = OntologyTools(ontology_settings)

print(ontology_tools.get_class_info("bis-formamides"))

# --- Additions for Testing OntologyTools ---
print("\n" + "="*20 + " Starting OntologyTools Test Suite " + "="*20)


class_name_1 = "super_aryl_extended_calix(4)pyrroles(SAE-C(4)Ps)"
# Replace with another valid class name from backup-2.owl
class_name_2 = "ae-c(4)ps"
# Replace with a valid object property name from backup-2.owl
source_name = "https://doi.org/10.1021/acs.accounts.2c00839"
# Replace with a valid class name to use as root for hierarchy parsing
root_class_name = "c(4)ps"

# List of classes for testing list inputs
class_list = [class_name_1, class_name_2]

def run_test(func_name: str, func_call):
    """Helper function to run and print test results."""
    print(f"\n--- Testing: {func_name} ---")
    try:
        result = func_call()
        print(f"Result: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        # Optional: print full traceback for debugging
        # import traceback
        # traceback.print_exc()

# --- Test Cases ---

# 2. get_class_info (list input)
run_test("get_class_info (list)", lambda: ontology_tools.get_class_info(class_list))

# 3. get_information_sources (single & list)
run_test("get_information_sources (single)", lambda: ontology_tools.get_information_sources(class_name_1))
run_test("get_information_sources (list)", lambda: ontology_tools.get_information_sources(class_list))

# 4. get_information_by_source
run_test(f"get_information_by_source ({class_name_1}, {source_name})", lambda: ontology_tools.get_information_by_source(class_name_1, source_name))
run_test(f"get_information_by_source (list, {source_name})", lambda: ontology_tools.get_information_by_source(class_list, source_name))

# 5. get_class_properties (single & list)
run_test("get_class_properties (single)", lambda: ontology_tools.get_class_properties(class_name_1))
run_test("get_class_properties (list)", lambda: ontology_tools.get_class_properties(class_list))

# 6. get_parents (single & list)
run_test("get_parents (single)", lambda: ontology_tools.get_parents(class_name_1))
run_test("get_parents (list)", lambda: ontology_tools.get_parents(class_list))

# 7. get_children (single & list)
run_test("get_children (single)", lambda: ontology_tools.get_children(class_name_1))
run_test("get_children (list)", lambda: ontology_tools.get_children(class_list))

# 8. get_ancestors (single & list)
run_test("get_ancestors (single)", lambda: ontology_tools.get_ancestors(class_name_1))
run_test("get_ancestors (list)", lambda: ontology_tools.get_ancestors(class_list))

# 9. get_descendants (single & list)
run_test("get_descendants (single)", lambda: ontology_tools.get_descendants(class_name_1))
run_test("get_descendants (list)", lambda: ontology_tools.get_descendants(class_list))

# 10. get_related_classes (single & list)
run_test("get_related_classes (single)", lambda: ontology_tools.get_related_classes(class_name_1))
run_test("get_related_classes (list)", lambda: ontology_tools.get_related_classes(class_list))

# 11. get_disjoint_classes (single & list)
run_test("get_disjoint_classes (single)", lambda: ontology_tools.get_disjoint_classes(class_name_1))
run_test("get_disjoint_classes (list)", lambda: ontology_tools.get_disjoint_classes(class_list))

# 12. parse_class_definition (single & list)
run_test("parse_class_definition (single)", lambda: ontology_tools.parse_class_definition(class_name_1))
run_test("parse_class_definition (list)", lambda: ontology_tools.parse_class_definition(class_list))

# 13. get_property_restrictions
# run_test(f"get_property_restrictions ({class_name_1}, {prop_name_obj})", lambda: ontology_tools.get_property_restrictions(class_name_1, prop_name_obj))
# run_test(f"get_property_restrictions ({class_name_1}, {prop_name_data})", lambda: ontology_tools.get_property_restrictions(class_name_1, prop_name_data))

# 14. get_property_values
# run_test(f"get_property_values ({class_name_1}, {prop_name_obj})", lambda: ontology_tools.get_property_values(class_name_1, prop_name_obj))

# 15. get_property_path
# run_test(f"get_property_path ({class_name_1} -> {class_name_2})", lambda: ontology_tools.get_property_path(class_name_1, class_name_2))

# 16. get_semantic_similarity
# run_test(f"get_semantic_similarity ({class_name_1}, {class_name_2})", lambda: ontology_tools.get_semantic_similarity(class_name_1, class_name_2))

# 17. get_inconsistent_classes
# print("\n--- Testing: get_inconsistent_classes (Ensure Java/Pellet is configured) ---")
# try:
#     result = ontology_tools.get_inconsistent_classes()
#     print(f"Result: {result}")
# except Exception as e:
#     print(f"ERROR: {e}")

# 18. parse_property_definition
# run_test(f"parse_property_definition ({prop_name_obj})", lambda: ontology_tools.parse_property_definition(prop_name_obj))
# run_test(f"parse_property_definition ({prop_name_data})", lambda: ontology_tools.parse_property_definition(prop_name_data))

# 19. parse_hierarchy_structure
# run_test("parse_hierarchy_structure (full)", lambda: ontology_tools.parse_hierarchy_structure())
run_test(f"parse_hierarchy_structure (root={root_class_name})", lambda: ontology_tools.parse_hierarchy_structure(root_class_name))


print("\n" + "="*20 + " OntologyTools Test Suite Finished " + "="*20)
