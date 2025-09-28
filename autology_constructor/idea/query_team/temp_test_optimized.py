import inspect
from autology_constructor.idea.query_team.ontology_tools import OntologyTools
from config.settings import ONTOLOGY_SETTINGS

def _get_tool_descriptions_optimized(tool_instance: OntologyTools) -> str:
    """Generates formatted descriptions of OntologyTools methods with priority ordering."""
    
    # Define priority order - most important tools first
    priority_methods = [
        "get_class_properties",      # 最详细的属性信息
        "parse_class_definition",     # 综合定义
        "get_class_info",            # 基本信息
        "get_related_classes",       # 相关类
        "get_parents",               # 直接父类
        "get_children",              # 直接子类
        "get_ancestors",             # 所有祖先
        "get_descendants",           # 所有后代
        "parse_hierarchy_structure", # 层次结构
        "get_disjoint_classes",      # 不相交类
        "get_information_sources",   # 信息源
        "get_information_by_source", # 按源获取信息
    ]
    
    descriptions = []
    processed_methods = set()
    
    if tool_instance is None:
        return "No tool instance provided."
    
    # Get all methods
    all_methods = dict(inspect.getmembers(tool_instance, predicate=inspect.ismethod))
    
    # Process methods in priority order first
    for method_name in priority_methods:
        if method_name in all_methods:
            method = all_methods[method_name]
            if not method_name.startswith("_") and method_name not in ["__init__", "execute_sparql", "get_class_richness_info"]:
                try:
                    sig = inspect.signature(method)
                    doc = inspect.getdoc(method)
                    desc = f"- {method_name}{sig}: {doc if doc else 'No description available.'}"
                    descriptions.append(desc)
                    processed_methods.add(method_name)
                except ValueError:
                    descriptions.append(f"- {method_name}(...): No signature/description available.")
                    processed_methods.add(method_name)
    
    # Process any remaining methods not in priority list (alphabetically)
    for name, method in sorted(all_methods.items()):
        if name not in processed_methods:
            if not name.startswith("_") and name not in ["__init__", "execute_sparql", "get_class_richness_info"]:
                try:
                    sig = inspect.signature(method)
                    doc = inspect.getdoc(method)
                    desc = f"- {name}{sig}: {doc if doc else 'No description available.'}"
                    descriptions.append(desc)
                except ValueError:
                    descriptions.append(f"- {name}(...): No signature/description available.")
    
    # Add a header to indicate the ordering
    header = "=== ONTOLOGY TOOLS (ordered by importance/frequency of use) ===\n"
    header += "Priority tools (most commonly used):\n"
    header += "1. get_class_properties - For detailed property information\n"
    header += "2. parse_class_definition - For comprehensive class definitions\n"
    header += "3. get_class_info - For basic class information\n"
    header += "\nComplete tool list:\n"
    
    return header + "\n".join(descriptions) if descriptions else "No tools available"

def _get_tool_descriptions_grouped(tool_instance: OntologyTools) -> str:
    """Generates formatted descriptions grouped by functionality."""
    
    # Group methods by functionality
    groups = {
        "Core Information Retrieval (Most Important)": [
            "get_class_properties",
            "parse_class_definition", 
            "get_class_info"
        ],
        "Hierarchy Navigation": [
            "get_parents",
            "get_children",
            "get_ancestors",
            "get_descendants",
            "parse_hierarchy_structure"
        ],
        "Relationships and Connections": [
            "get_related_classes",
            "get_disjoint_classes"
        ],
        "Source and Documentation": [
            "get_information_sources",
            "get_information_by_source"
        ]
    }
    
    if tool_instance is None:
        return "No tool instance provided."
    
    all_methods = dict(inspect.getmembers(tool_instance, predicate=inspect.ismethod))
    output = []
    
    for group_name, method_names in groups.items():
        group_descriptions = []
        output.append(f"\n### {group_name}")
        
        for method_name in method_names:
            if method_name in all_methods:
                method = all_methods[method_name]
                try:
                    sig = inspect.signature(method)
                    doc = inspect.getdoc(method)
                    # Get just the first paragraph of the docstring for brevity
                    if doc:
                        doc_lines = doc.split('\n\n')[0]
                    else:
                        doc_lines = 'No description available.'
                    desc = f"- **{method_name}**{sig}: {doc_lines}"
                    group_descriptions.append(desc)
                except ValueError:
                    group_descriptions.append(f"- **{method_name}**(...): No signature/description available.")
        
        output.extend(group_descriptions)
    
    return "\n".join(output) if output else "No tools available"

if __name__ == "__main__":
    ot = OntologyTools(ONTOLOGY_SETTINGS)
    
    print("=" * 80)
    print("OPTIMIZED VERSION (Priority Ordering):")
    print("=" * 80)
    print(_get_tool_descriptions_optimized(ot))
    
    print("\n" + "=" * 80)
    print("GROUPED VERSION (By Functionality):")
    print("=" * 80)
    print(_get_tool_descriptions_grouped(ot))
