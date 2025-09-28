import os
import sys
import argparse
import asyncio
import json
import logging

# 假设您已通过 pypi 安装 lightrag
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status


# --------------------------------------------------------------------------- #
# ---                           CONFIGURATION                             --- #
# --------------------------------------------------------------------------- #

# 1. 文件和路径配置
WORKING_DIR_BASE = r"tests\unit_test\query\test\lightrag\temp_rag_storage"
JSON_OUTPUT_FILENAME = "all_model_results.json"

# 2. 模型配置
# MODELS_TO_RUN = ["gpt-4.1-nano", "gpt-4.1"]

MODELS_TO_RUN = ["gpt-4.1-nano"]

# MODELS_TO_RUN = ["gpt-4.1"]

# 3. 提示词和问题数据
USER_PROMPT_TEMPLATE = f"""
**Role:** You are an expert Chemistry Researcher.
**Task:** Provide a clear, accurate, and comprehensive answer to the user's question. You should leverage your own expert knowledge, judiciously enhancing and verifying it with relevant and applicable information selected from the 'query results'.
**Response Guidelines:**
* **Knowledge Integration:** Synthesize your broad chemical knowledge with pertinent details from the 'Information Source'.
* **Selective Use of Source:** Critically evaluate the 'Information Source'. Incorporate specific details (e.g., data points like pKa values, reaction types, precise definitions, specific examples) only when they directly enhance the accuracy, specificity, or completeness of the answer to the user's question. Do not feel obligated to include all provided information; prioritize relevance to the query.
* **Verification and Conflict:** Use the source to verify facts where appropriate. If there's a conflict between your general knowledge and the source, prioritize the source's specific data if it is relevant to the question and appears accurate, but use your expert judgment to omit information that seems erroneous or irrelevant to the user's query.
* **Synthesis:** Weave together your general knowledge and the selected source information into a coherent, well-structured response.
* **Clarity & Tone:** Use precise, professional chemical language. Aim for accessibility by briefly explaining potentially niche terms if needed.
* **Directness & Comprehensiveness:** Address all parts of the user's question directly and thoroughly, enriched by the appropriately selected information.
* **Source Attribution:** Do not mention "ontology" or refer to the 'Information Source' explicitly (e.g., avoid "according to the provided data..."). Present the integrated information as established chemical facts.
* **Knowledge Expansion:** Feel free to supplement the response with your own expert knowledge on topics that may be absent from the 'Query Results' but are relevant to providing a complete answer to the user's question.
* **Supramolecular Chemistry Style:** Tailor your response to appeal to supramolecular chemists by emphasizing host-guest interactions, non-covalent binding phenomena, molecular recognition principles, and structure-property relationships. Include relevant thermodynamic parameters, binding constants, and mechanistic insights where appropriate.
**Answer:**
"""
TOTAL_QAS = [
    {
      "difficulty_level": 1,
      "question": "Tell me about Quinine.",
      "answer": "Quinine is an alkaloid derived from cinchona tree bark, used historically for malaria and now as a bittering agent, but associated with adverse health effects like thrombocytopenia."
    },
    {
      "difficulty_level": 1,
      "question": "What is an Indicator Displacement Assay?",
      "answer": "An IDA is a sensing strategy based on host-guest recognition, often utilizing non-covalent interactions where an analyte displaces an indicator from a receptor, causing a detectable signal change (e.g., fluorescence or absorbance)."
    },
    {
      "difficulty_level": 2,
      "question": "What techniques are used to analyze Quinine?",
      "answer": "Quinine is analyzed by techniques including Electrochemical Technique, High Performance Liquid Chromatography (HPLC), Colorimetric Assay, Fluorescence Assay, and High Resolution Mass Spectrometry (HRMS)."
    },
    {
      "difficulty_level": 2,
      "question": "What are the components of an Indicator Displacement Assay?",
      "answer": "Components include beta-Cyclodextrin (beta-CD), Poly(N-acetylaniline), and Graphene."
    },
    {
      "difficulty_level": 3,
      "question": "Are there electrochemical sensors using Indicator Displacement Assay (IDA) to detect Quinine?",
      "answer": "The Electrochemical Sensor constructed via IDA (Indicator Displacement Assay) has the detection target Quinine."
    },
    {
      "difficulty_level": 3,
      "question": "Which host molecules use host-guest recognition in electrochemical assays?",
      "answer": "Host-Guest Recognition is integrated with an Electrochemical Sensor. Beta-Cyclodextrin (β-CD) is a host involved in Host-Guest Recognition."
    },
    {
      "difficulty_level": 4,
      "question": "How stable and reproducible is the electrochemical sensor that uses an Indicator Displacement Assay (IDA) for detecting Quinine?",
      "answer": "The Electrochemical Sensor has high stability (acceptable peak current decrease within 21 days, 86.47% retained) and good reproducibility (RSD of 2.06% across seven electrodes)."
    },
    {
      "difficulty_level": 4,
      "question": "How is the electrochemical sensor that uses an Indicator Displacement Assay (IDA) for detecting Quinine verified?",
      "answer": "The Electrochemical Sensor is verified by Differential Pulse Voltammetry (DPV), Cyclic Voltammetry (CV), Proton Nuclear Magnetic Resonance (H_NMR), Scanning Electron Microscopy (SEM), Electrochemical Impedance Analysis (EIS), and Fourier Transform Infrared (FTIR)."
    },
    {
      "difficulty_level": 5,
      "question": "In the electrochemical sensor that uses an Indicator Displacement Assay (IDA) for detecting Quinine, how does Quinine displace Methylene Blue from beta-Cyclodextrin?",
      "answer": "Methylene Blue (MB) forms an inclusion complex with beta-Cyclodextrin (beta-CD). Quinine, having a higher binding affinity, competitively displaces MB from the beta-CD cavity. This displacement causes a change in the electrochemical signal (e.g., DPV peak current) which is used for Quinine detection. Poly(N-acetylaniline) inhibits non-specific adsorption of MB, contributing to the assay's selectivity."
    },
    {
      "difficulty_level": 5,
      "question": "What does Graphene do in the electrochemical sensor that uses an Indicator Displacement Assay (IDA) for detecting Quinine?",
      "answer": "Graphene (specifically reduced graphene oxide, rGO) is used as an electrode material in the sensor. It enhances electron transfer properties due to its superior electrical conductivity and large specific surface area, improving the sensor's performance. It serves as a platform onto which other components like Poly(N-acetylaniline) and beta-Cyclodextrin are deposited."
    },
    {
    "question": "What is a cryptand?",
    "query": "Retrieve the definition or description associated with the chemical class 'Cryptand'. Look for annotations like rdfs:comment, skos:definition, or specific meta-properties on the 'Cryptand' class definition.",
    "answer": "A cryptand is a type of macrocyclic ligand, specifically a supramolecular host, featuring a three-dimensional cavity that allows it to form stable complexes by encapsulating guest ions or molecules.",
    "difficulty_level": 1
  },
  {
    "question": "Is pyrrole considered an aromatic system?",
    "query": "Verify if an `rdfs:subClassOf` axiom exists where 'Pyrrole' is declared as a subclass of the 'AromaticSystem' class within the ontology.",
    "answer": "Yes, pyrrole is classified as an aromatic system.",
    "difficulty_level": 1
  },
  {
    "question": "What types of molecules typically act as guests for supramolecular hosts?",
    "query": "Identify the `rdfs:range` axiom defined for the object property 'binds_guest'. This indicates the general class of entities that can be bound by entities that are in the domain of 'binds_guest' (typically 'SupramolecularHost').",
    "answer": "Typically, molecules classified as 'GuestMolecule' (which can include anions, cations, or neutral molecules) act as guests for supramolecular hosts.",
    "difficulty_level": 2
  },
  {
    "question": "What are some specific types of macrocycles?",
    "query": "List all `owl:Class` entities for which an `rdfs:subClassOf` axiom exists, explicitly stating 'Macrocycle' as the direct parent class.",
    "answer": "Specific types of macrocycles include cryptands, calixarenes, pillararenes, and cyclodextrins.",
    "difficulty_level": 2
  },
  {
    "question": "When a calixarene containing pyrrole groups binds an anion, what specific non-covalent interactions are typically involved?",
    "query": "Analyze OWL axioms or property restrictions associated with the 'Calixarene' class, particularly when it 'has_functional_group' 'Pyrrole' and 'binds_guest' an 'Anion'. Identify the specific subclasses of 'InteractionType' (e.g., 'HydrogenBond', 'AnionPiInteraction') that are linked via 'interacts_via' in these defined scenarios.",
    "answer": "When a calixarene containing pyrrole groups binds an anion, non-covalent interactions such as HydrogenBond (often from the pyrrole NH) and AnionPiInteraction (between the anion and the pyrrole ring) are typically involved.",
    "difficulty_level": 3
  },
  {
    "question": "Are there known supramolecular hosts that are derivatives of calixarenes and also feature pyrrole functional groups?",
    "query": "Search for 'SupramolecularHost' classes or typical instances that are described as being 'is_derivative_of' the 'Calixarene' class AND are also associated with the 'Pyrrole' class via the 'has_functional_group' property.",
    "answer": "Yes, supramolecular hosts that are derivatives of calixarenes and feature pyrrole functional groups are known, a prominent example being calix[n]pyrroles.",
    "difficulty_level": 3
  },
  {
    "question": "What are common applications for cage molecules compared to macrocycles, and do they have any overlapping uses?",
    "query": "1. Identify 'Application' subclasses (e.g., 'Sensing', 'Catalysis', 'DrugDelivery', 'Separation') linked to the 'CageMolecule' class via the 'has_application' property (possibly through class axioms or restrictions). 2. Perform the same analysis for the 'Macrocycle' class. 3. Compare these sets of 'Application' subclasses to identify distinct and common areas.",
    "answer": "Cage molecules are commonly utilized in applications like catalysis and chemical separation. Macrocycles frequently find use in areas such as molecular sensing and drug delivery. An example of an overlapping application could be sensing, where both classes of compounds might be employed.",
    "difficulty_level": 4
  },
  {
    "question": "What types of supramolecular hosts are known to bind anions primarily through anion-π interactions?",
    "query": "Find 'SupramolecularHost' subclasses or characteristic descriptions where OWL axioms (e.g., `owl:equivalentClass` or `rdfs:subClassOf` involving restrictions on 'binds_guest' with 'Anion', and 'interacts_via' with 'AnionPiInteraction') define this specific binding mode.",
    "answer": "Supramolecular hosts that possess electron-deficient aromatic systems, such as certain calixarene derivatives (like calix[n]pyrroles) or other specifically designed π-acidic macrocycles, are known to bind anions primarily through AnionPiInteraction.",
    "difficulty_level": 4
  },
  {
    "question": "Why are supramolecular hosts containing pyrrole units generally effective at binding anions?",
    "query": "Analyze the defined properties of the 'Pyrrole' class (e.g., its classification as an 'AromaticSystem', its NH group) and its typical involvement in 'InteractionType' classes like 'HydrogenBond' and 'AnionPiInteraction' when 'Pyrrole' is a 'FunctionalGroup' of a 'SupramolecularHost' binding an 'Anion'. Synthesize an explanation for this effectiveness based on these defined chemical characteristics and interaction capabilities.",
    "answer": "Supramolecular hosts with pyrrole units are effective for anion binding due to two main features of pyrrole: its NH group can act as a hydrogen bond donor, forming HydrogenBond interactions with anions, and its electron-deficient aromatic π-system can engage in favorable AnionPiInteractions with anions. This combination enhances binding affinity and selectivity.",
    "difficulty_level": 5
  },
  {
    "question": "What is the role of non-covalent interactions like hydrogen bonds and anion-π interactions in the formation of supramolecular host-guest complexes?",
    "query": "Examine how 'InteractionType' subclasses (e.g., 'HydrogenBond', 'AnionPiInteraction') are axiomatically linked via the 'interacts_via' property in scenarios where 'SupramolecularHost' classes bind 'GuestMolecule' classes (often described by 'binds_guest' relationships). Summarize their function based on these defined ontological roles.",
    "answer": "Non-covalent interactions, such as hydrogen bonds and anion-π interactions, are crucial for molecular recognition between hosts and guests. They act as the primary driving forces that determine the stability, selectivity, and overall formation of supramolecular host-guest complexes.",
    "difficulty_level": 5
  },
  {
        "question": "What types of molecules can be detected by IDA?"
    },
    {
        "question": "What types of host-guest interaction can be used to design IDA-based electrochemical sensors?"
    },
    {
        "question": "What types of host-guest interaction can be used to design IDA using optical detection?"
    },
    {
        "question": "What types of host-guest interaction can induce changes in optical signals?"
    },
    {
        "question": "What types of host-guest interaction can induce changes in electrochemical signals?"
    },
    {
        "question": "What types of supramolecular hosts are known to bind to their guests primarily through cation-π interactions?"
    },
    {
        "question": "What are the main factors controlling host-guest interaction?"
    }
]


# --------------------------------------------------------------------------- #

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        "gpt-4.1",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

async def query_model_workflow(model_name: str, questions: list[dict], graph_dir_name: str = None):
    """为单个模型加载知识库并执行查询

    参数:
        model_name: 模型名（如 gpt-4.1）
        questions: 问答列表
        graph_dir_name: 指定知识库目录名（如 gpt-4_1），如果为None则自动用模型名.replace('.', '_')
    """
    log.info(f"--- 开始为模型: {model_name} 执行查询工作流 ---")

    if graph_dir_name is not None:
        model_working_dir = os.path.join(WORKING_DIR_BASE, graph_dir_name)
    else:
        model_working_dir = os.path.join(WORKING_DIR_BASE, model_name.replace(".", "_"))
    
    if not os.path.exists(model_working_dir):
        log.error(f"错误: 模型 '{model_name}' 的知识库目录不存在: {model_working_dir}")
        log.error("请先成功运行 'build_knowledge_base.py' 脚本。")
        return None

    # 初始化LightRAG，这次它会从指定目录加载已有的知识库
    rag = LightRAG(
        working_dir=model_working_dir,
        llm_model_func=llm_model_func,
        embedding_func=openai_embed,
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    log.info(f"[{model_name}] 已成功加载预构建的知识库。")

    query_param = QueryParam(mode="mix", user_prompt=USER_PROMPT_TEMPLATE,enable_rerank=False)

    results = []
    log.info(f"[{model_name}] 开始处理 {len(questions)} 个问题...")
    for i, qa in enumerate(questions):
        question_text = qa["question"]
        log.info(f"[{model_name}] 正在查询 ({i+1}/{len(questions)}): \"{question_text}\"")
        
        response = await rag.aquery(
            f"**User Question:** {question_text}",
            param=query_param
        )
        
        results.append({
            "question": question_text,
            "answer": response if response else "未能生成回答。"
        })
    
    log.info(f"--- 模型: {model_name} 的查询工作流已完成 ---")
    return results

async def main():
    """主函数，负责调度所有模型的查询并保存输出

    支持命令行参数:
        --graph-dir-name <目录名>   # 指定知识库目录名（如 gpt-4_1），否则自动用模型名.replace('.', '_')
    """
    parser = argparse.ArgumentParser(description="Run LightRAG queries for multiple models with optional graph dir override.")
    parser.add_argument("--graph-dir-name", type=str, default=None, help="指定知识库目录名（如 gpt-4_1），否则自动用模型名.replace('.', '_')")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        log.error("致命错误: 环境变量 OPENAI_API_KEY 未设置。")
        return

    final_results = {}
    for model in MODELS_TO_RUN:
        model_answers = await query_model_workflow(model, TOTAL_QAS, graph_dir_name=args.graph_dir_name)
        if model_answers:
            final_results[model] = model_answers

    if not final_results:
        log.error("所有模型的查询均未成功，无法生成输出文件。")
        return
        
    # --- 文件写入逻辑 ---
    with open(JSON_OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)
    log.info(f"所有模型的完整结果已保存至: '{JSON_OUTPUT_FILENAME}'")

    for model_name, results in final_results.items():
        safe_model_name = model_name.replace(".", "_")
        md_filename = f"{safe_model_name}_results.md"
        
        markdown_output = f"# 模型: {model_name}\n\n"
        for result in results:
            markdown_output += f"## {result['question']}\n\n"
            markdown_output += f"{result['answer']}\n\n"
        
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        log.info(f"模型 {model_name} 的结果已保存至: '{md_filename}'")
    
    log.info("\n✅ 所有查询工作流已完成。")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())