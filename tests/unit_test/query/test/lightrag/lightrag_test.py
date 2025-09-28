import os
import asyncio
import json
from glob import glob
import numpy as np
import logging

# 假设您已通过 pypi 安装 lightrag
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed

# --------------------------------------------------------------------------- #
# ---                           CONFIGURATION                             --- #
# ---             在这里修改所有的变量，无需改动下方代码                     --- #
# --------------------------------------------------------------------------- #

# 1. 文件和路径配置
# -------------------
# 基础工作目录，用于存放不同模型的独立知识库
WORKING_DIR_BASE = r".\temp_rag_storage"
# 存放数据切片（JSON文件）的文件夹路径
CHUNKS_DIR = r"tests\unit_test\query\test\lightrag\test_chunks"
# 最终输出的 JSON 文件名
JSON_OUTPUT_FILENAME = "lightrag_results.json"


# 2. 模型配置
# -------------------
# 需要运行和对比的模型列表
MODELS_TO_RUN = ["gpt-4.1-nano", "gpt-4.1"]
# Embedding 模型
EMBEDDING_MODEL = "text-embedding-3-large"

# 3. LightRAG 配置
# -------------------
# 并行插入文档的最大数量
MAX_PARALLEL_INSERT = 10

# 4. 提示词模板
# -------------------
# 这是用于指导模型回答问题的系统提示词
USER_PROMPT_TEMPLATE = f"""
**Role:** You are an expert Chemistry Researcher.
**Task:** Provide a clear, accurate, and comprehensive answer to the user's question. You should leverage your own expert knowledge, **judiciously enhancing and verifying** it with **relevant and applicable information** selected from the 'query results'.
**Response Guidelines:**
* **Knowledge Integration:** Synthesize your broad chemical knowledge with pertinent details from the 'Information Source'.
* **Selective Use of Source:** Critically evaluate the 'Information Source'. **Incorporate specific details** (e.g., data points like pKa values, reaction types, precise definitions, specific examples) **only when they directly enhance the accuracy, specificity, or completeness of the answer to the user's question.** Do not feel obligated to include all provided information; prioritize relevance to the query.
* **Verification and Conflict:** Use the source to verify facts where appropriate. If there's a conflict between your general knowledge and the source, prioritize the source's specific data **if it is relevant to the question and appears accurate**, but use your expert judgment to omit information that seems erroneous or irrelevant to the user's query.
* **Synthesis:** Weave together your general knowledge and the selected source information into a coherent, well-structured response.
* **Clarity & Tone:** Use precise, professional chemical language. Aim for accessibility by briefly explaining potentially niche terms if needed.
* **Directness & Comprehensiveness:** Address all parts of the user's question directly and thoroughly, enriched by the appropriately selected information.
* **Source Attribution:** Do **not** mention "ontology" or refer to the 'Information Source' explicitly (e.g., avoid "according to the provided data..."). Present the integrated information as established chemical facts.
* **Knowledge Expansion:** Feel free to supplement the response with your own expert knowledge on topics that may be absent from the 'Query Results' but are relevant to providing a complete answer to the user's question.
* **Supramolecular Chemistry Style:** Tailor your response to appeal to supramolecular chemists by emphasizing host-guest interactions, non-covalent binding phenomena, molecular recognition principles, and structure-property relationships. Include relevant thermodynamic parameters, binding constants, and mechanistic insights where appropriate.
**Answer:**
"""

# 5. 问题数据
# -------------------
# 所有需要提问的问题列表
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
# ---                      END OF CONFIGURATION                           --- #
# --------------------------------------------------------------------------- #


# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def create_llm_model_func(model_name: str):
    """为指定的模型名称创建一个 LLM 调用函数"""
    async def llm_model_func(prompt: str, **kwargs) -> str:
        return await openai_complete_if_cache(
            model=model_name,
            prompt=prompt,
            api_key=os.getenv("OPENAI_API_KEY"),
            **kwargs
        )
    return llm_model_func

async def embedding_func(texts: list[str]) -> np.ndarray:
    """Embedding 函数，将文本转换为向量"""
    return await openai_embed(
        texts,
        model=EMBEDDING_MODEL,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

async def run_rag_workflow_for_model(model_name: str, questions: list[dict]):
    """为单个指定模型运行完整的 LightRAG 工作流"""
    log.info(f"--- 开始为模型: {model_name} 执行工作流 ---")

    model_working_dir = os.path.join(WORKING_DIR_BASE, model_name.replace(".", "_"))
    if not os.path.exists(model_working_dir):
        os.makedirs(model_working_dir)
        log.info(f"已创建独立目录: {model_working_dir}")

    rag = LightRAG(
        working_dir=model_working_dir,
        llm_model_func=create_llm_model_func(model_name),
        embedding_func=openai_embed,
        max_parallel_insert=MAX_PARALLEL_INSERT,
    )

    log.info(f"[{model_name}] 正在初始化存储...")
    await rag.initialize_storages()
    log.info(f"[{model_name}] 存储初始化完成。")

    chunk_storage = rag.get_storage("chunk_storage")
    vector_store_size = chunk_storage.size()
    if vector_store_size == 0:
        log.info(f"[{model_name}] 向量数据库为空，正在从 '{CHUNKS_DIR}' 加载文档...")
        all_contents = []
        if os.path.exists(CHUNKS_DIR):
            for file_path in glob(os.path.join(CHUNKS_DIR, "*.json")):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        if "content" in item:
                            all_contents.append(item["content"])
            
            if all_contents:
                log.info(f"[{model_name}] 找到 {len(all_contents)} 个内容块待插入。")
                await rag.ainsert(all_contents)
                log.info(f"[{model_name}] 文档插入完成。")
            else:
                log.warning(f"[{model_name}] 在 '{CHUNKS_DIR}' 中未找到任何内容。")
        else:
             log.warning(f"[{model_name}] 目录 '{CHUNKS_DIR}' 不存在，跳过文档插入。")
    else:
        log.info(f"[{model_name}] 向量数据库中已有 {vector_store_size} 个项目，跳过插入。")

    query_param = QueryParam(mode="mix", user_prompt=USER_PROMPT_TEMPLATE)

    results = []
    log.info(f"[{model_name}] 开始处理 {len(questions)} 个问题...")
    for i, qa in enumerate(questions):
        question_text = qa["question"]
        log.info(f"[{model_name}] 正在查询 ({i+1}/{len(questions)}): \"{question_text}\"")
        
        response = await rag.aquery(
            user_query=f"**User Question:** {question_text}",
            param=query_param
        )
        
        results.append({
            "question": question_text,
            "answer": str(response.response) if response else "未能生成回答。"
        })
    
    log.info(f"--- 模型: {model_name} 的工作流已完成 ---")
    return results

async def main():
    """主函数，负责调度所有模型的执行并保存最终的输出文件"""
    if not os.getenv("OPENAI_API_KEY"):
        log.error("致命错误: 环境变量 OPENAI_API_KEY 未设置。")
        return

    final_results = {}
    for model in MODELS_TO_RUN:
        model_answers = await run_rag_workflow_for_model(model, TOTAL_QAS)
        final_results[model] = model_answers

    # --- 文件写入逻辑 ---

    # 1. 保存完整的 JSON 文件
    with open(JSON_OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)
    log.info(f"所有模型的完整结果已保存至: '{JSON_OUTPUT_FILENAME}'")

    # 2. 为每个模型分别保存独立的 Markdown 文件
    for model_name, results in final_results.items():
        # 创建一个对文件名安全的名字
        safe_model_name = model_name.replace(".", "_")
        md_filename = f"{safe_model_name}_results.md"
        
        markdown_output = f"# 模型: {model_name}\n\n"
        for result in results:
            markdown_output += f"## {result['question']}\n\n"
            markdown_output += f"{result['answer']}\n\n"
        
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        log.info(f"模型 {model_name} 的结果已保存至: '{md_filename}'")
    
    log.info(f"\n✅ 所有工作流已完成。")

if __name__ == "__main__":
    # 在 Windows 上运行 asyncio 需要这一行来避免事件循环策略的错误
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())