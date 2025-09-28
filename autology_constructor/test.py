# from owlready2 import *
# import owlready2.base
# import owlready2.class_construct
# import pytest
# # Removed tempfile, os, shutil as they are no longer needed for temp ontology

# from config.settings import OntologySettings
# # Keep OntologyTools import
# from autology_constructor.idea.query_team.ontology_tools import OntologyTools



# ontology_settings = OntologySettings(
#     base_iri="http://www.test.org/chem_ontologies/",
#     ontology_file_name="backup-2.owl",
#     directory_path="data/ontology/",
#     closed_ontology_file_name=None
# )

# ontology_tools = OntologyTools(ontology_settings)

# # print(ontology_tools.get_class_info("bis-formamides"))

# props = ontology_tools._get_single_class_properties("bis-formamides")

# print("props: ", props)
# props_filtered = set(props) - {'has_information'}
# print("props_filtered: ", props_filtered)

# prop = ontology_settings.object_properties["is_stable_as"]
# print("prop: ", prop)
# print("type(prop): ", type(prop))
# print("prop.name: ", prop.name)
# print("prop.domain", prop.domain)
# print("prop.range", prop.range)

# ops = list(ontology_settings.ontology.object_properties())
# for op in ops:
#     if len(op.range) > 0 and len(op.domain) > 0:
#         print("op: ", op)
#         print("type(op): ", type(op))
#         print("op.name: ", op.name)
#         print("op.domain", op.domain)
#         print("op.range", op.range)
#         print("-"*100) 

# onto = get_ontology("http://www.test.org/chem_ontologies/backup-2.owl").load(only_local=True)

# res_list = onto.search(iri = f"*/anion_antiport_mechanism", type = owlready2.owl_class)

# print("res_list: ", res_list)
# print(isinstance(res_list[0], ThingClass))


# import random
# cls = random.choice(list(onto.classes()))
# print(cls)

# super_classes = cls.is_a

# for res in super_classes:
#     print(res)
#     is_res = isinstance(res,owlready2.Restriction)
#     print(is_res)
#     if is_res:
#         print(res.property)
#         print(type(res.property))
#         print(res.property.name)
#         print(res.property.name == "has_information")
#         print(isinstance(res.property, (ObjectPropertyClass, DataPropertyClass)))
#         print("-"*100)
#         print(type(res.subclasses))
#         print(res.__dict__["type"])
#         print(res.type)
#         print(getattr(res,"type", -1))


#     print("-"*200)



import litellm
import os

# 设置您的 OpenAI API 密钥环境变量，如果尚未设置
# os.environ["OPENAI_API_KEY"] = "sk-your_api_key"
# os.environ["LITELLM_STEP_VERBOSE_LOGS"] = "True" # 尝试启用更详细的 litellm 日志

print("Attempting to configure litellm caching and make a call...")

try:
    # 尝试模拟可能在 dspy 内部发生的 litellm 用法
    # 显式启用缓存，因为原始堆栈跟踪涉及缓存
    litellm.cache = litellm.Cache() # 尝试初始化缓存系统
    # 或者根据 litellm 文档，有时是 litellm.caching = True

    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test call for annotations error."}],
        caching=True # 确保启用缓存以触发相关代码路径
    )
    print("LiteLLM call with caching attempted.")
    # print(response)
except AttributeError as ae:
    if "__annotations__" in str(ae):
        print(f"POTENTIAL ORIGINAL ERROR REPRODUCED: AttributeError: {ae}")
    else:
        print(f"Other AttributeError during LiteLLM test: {ae}")
except ImportError as ie:
    print(f"ImportError during LiteLLM test: {ie}")
except Exception as e:
    print(f"An error occurred during LiteLLM test: {e}")
    import traceback
    traceback.print_exc()

print("Test script for annotations finished.")