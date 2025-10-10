import argparse
from config.settings import ONTOLOGY_SETTINGS, LLM_CONFIG
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_ollama import ChatOllama

import sys
import os
import json
import time
import datetime
from typing import Dict, Any, List

base_folder_path = r"test_results/workflow_runs/"
MAX_WORKERS = 10


# Parse command line arguments
parser = argparse.ArgumentParser(description='Run workflow test with optional LLM override')
parser.add_argument('--query-llm', default=LLM_CONFIG.get('model', 'gpt-4.1-nano'), help='Query LLM model name (default: from settings.yaml)')
parser.add_argument('--answer-llm', default='gpt-4.1-nano', help='Answer LLM model name (default: gpt-4.1-nano)')
parser.add_argument('--runs', type=int, default=1, help='Number of times to run the test (default: 1)')
args = parser.parse_args()

# Override LLM configuration if provided
if args.query_llm:
    import config.settings as settings
    settings.LLM_CONFIG['model'] = args.query_llm
    print(f"Query LLM overridden to: {args.query_llm}")

# Configure answer LLM
answer_llm = ChatOpenAI(
            model_name=args.answer_llm,
            temperature=0,
            max_tokens=10000,
        )

print(f"Using Query LLM: {args.query_llm}, Answer LLM: {args.answer_llm}")
print(f"Will run {args.runs} time(s)")

# 控制台输出重定向类
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# 记录整体开始时间
overall_start_time = time.time()
print(f"\n{'='*60}")
print(f"开始执行测试 - 总共 {args.runs} 次运行")
print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_start_time))}")
print(f"{'='*60}")

# 主循环：重复运行测试
for run_num in range(1, args.runs + 1):
    run_start_time = time.time()
    
    # 设置控制台输出重定向 - 在每次测试开始前设置
    import logging
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 为每次运行创建带次数的文件夹
    if args.runs > 1:
        results_dir = f"{base_folder_path}{timestamp}_test_run_run{run_num}"
    else:
        results_dir = f"{base_folder_path}{timestamp}_test_run"
    
    os.makedirs(results_dir, exist_ok=True)

    # 重定向标准输出和标准错误到同一个文件
    log_file = open(f"{results_dir}/console_output.log", 'w', encoding='utf-8')
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    # 配置logging只输出到stderr（这样会通过上面的Tee保存到同一个文件）
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr,  # 输出到stderr，会被Tee捕获
        force=True  # 强制重新配置，覆盖之前的配置
    )

    print(f"所有输出（包括print和logger）将按时间顺序保存到: {results_dir}/console_output.log")
    print(f"\n{'='*60}")
    print(f"开始第 {run_num}/{args.runs} 次运行")
    print(f"运行开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_start_time))}")
    print(f"{'='*60}")
    
    from owlready2 import *
    import asyncio # Needed for owlready2 async operations in some envs
    
    # Import the OntologySettings class
    from config.settings import OntologySettings # Keep ONTOLOGY_SETTINGS import for potential base_iri access
    
    # Import necessary LLM and Query Team components
    try:
        from autology_constructor.idea.query_team import QueryManager, Query, QueryStatus, create_query_graph
        from autology_constructor.idea.query_team.ontology_tools import OntologyTools
        from autology_constructor.idea.common.llm_provider import get_cached_default_llm
        print("Modules imported successfully.")
    except ModuleNotFoundError as e:
        print(f"Error importing modules: {e}")
        print(f"Current sys.path: {sys.path}")
    
    # Ensure LLM Provider is configured
    try:
        llm = get_cached_default_llm()
        def get_model_name(obj):
            return getattr(obj, "model_name", getattr(obj, "model", None))
        print(f"LLM: {get_model_name(llm)}. \nAnsewr LLM: {get_model_name(answer_llm)}")
        print("LLM Provider initialized successfully.")
    except Exception as e:
        print(f"Error initializing LLM Provider: {e}\nPlease ensure API keys or necessary configurations are set.")
        llm = None

    # --- Ontology Setup ---
    print("Setting up test ontology using a new OntologySettings instance...")

    # Define parameters for the new OntologySettings instance
    # Assuming 'backup-2.owl' and 'backup-2-closed.owl' exist in 'data/ontology'
    # Use the project root defined in the previous cell
    project_root_path = os.environ.get("PROJECT_ROOT", ".")
    ontology_dir = os.path.join(project_root_path, "data", "ontology")
    # You might want to use the base_iri from the default settings or define a specific one for testing
    test_base_iri = ONTOLOGY_SETTINGS.base_iri if 'ONTOLOGY_SETTINGS' in locals() else "http://www.test.org/chem_ontologies/backup-2"

    try:
        # Instantiate OntologySettings directly
        # test_ontology_settings = ONTOLOGY_SETTINGS
        test_ontology_settings = OntologySettings(
            base_iri=test_base_iri,
            ontology_file_name="final.owl",  # Use the desired ontology file
            directory_path=ontology_dir,
            # closed_ontology_file_name="final-closed.owl" 
        )
        # Access the loaded ontology via the instance's property
        test_onto = test_ontology_settings.ontology
        print(f"Successfully loaded ontology: {test_onto.base_iri}")
        print(f"From file: {test_ontology_settings.ontology_file_name} in {test_ontology_settings.directory_path}")

        # Optional: Print some details about the loaded ontology
        # print(f"Test Ontology '{test_onto.base_iri}' loaded with:")
        # print(f"- Classes ({len(list(test_onto.classes()))}): {[c.name for c in list(test_onto.classes())[:5]]}...") # Print first 5
        # print(f"- Individuals ({len(list(test_onto.individuals()))}): {[i.name for i in list(test_onto.individuals())[:5]]}...")
        # print(f"- Object Properties ({len(list(test_onto.object_properties()))}): {[p.name for p in list(test_onto.object_properties())[:5]]}...")
        # print(f"- Data Properties ({len(list(test_onto.data_properties()))}): {[p.name for p in list(test_onto.data_properties())[:5]]}...")

    except Exception as e:
        print(f"Error creating OntologySettings or loading ontology 'backup-2.owl': {e}")
        print(f"Please ensure 'backup-2.owl' exists in '{ontology_dir}' and settings are correct.")
        test_onto = None 


    total_qas = [
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



    temp_qas = total_qas

    num = len(temp_qas)

    queries = [item["question"] for item in temp_qas[:num]]

    revised_queries = [item["question"] for item in temp_qas[:num]]

    query_context = {
        # "ontology": ONTOLOGY_SETTINGS,
        "originating_team": "test_notebook",
        "originating_stage": "manual_test",
        "query_type": "information_retrieval" # 对所有查询使用信息检索类型
    }

    print(len(queries),len(revised_queries))

    # queries = [queries[4], queries[6], queries[20]]
    # revised_queries =  [revised_queries[4],  revised_queries[6],  revised_queries[20]]

    # queries = [queries[14]]
    # revised_queries =  [revised_queries[14]]

    # print(len(queries),len(revised_queries))

    # 定义回调函数处理Future结果并使用agent生成回答

    def process_result_with_agent(result_dict, query_text):
        """
        Use an agent to process query results and generate a natural language response
        
        Args:
            result_dict: Query result dictionary
            query_text: Original query text
        
        Returns:
            str: Natural language response generated by the agent
        """
        # Extract query results information from the result
        if "formatted_results" in result_dict:
            query_results = result_dict["formatted_results"]
            print("-"*100)
            print(f"formatted_results found")
        elif "query_results" in result_dict:
            query_results = result_dict["query_results"]
            print("-"*100)
            print(f"query_results found")
        else:
            return f"I'm sorry, I couldn't find valid information about '{query_text}'."
        
        # Construct the prompt in English
        prompt = f"""
    **Role:** You are an expert Chemistry Researcher.

    **Task:** Provide a clear, accurate, and comprehensive answer to the user's question. You should leverage your own expert knowledge, **judiciously enhancing and verifying** it with **relevant and applicable information** selected from the 'Ontology query results'.

    **User Question:**
    {query_text}

    **Information Source (Ontology Query Results for Enhancement & Verification):**
    {query_results}

    **Response Guidelines:**
    * **Knowledge Integration:** Synthesize your broad chemical knowledge with **pertinent details** from the 'Information Source'.
    * **Selective Use of Source:** Critically evaluate the 'Information Source'. **Incorporate specific details** (e.g., data points like pKa values, reaction types, precise definitions, specific examples) **only when they directly enhance the accuracy, specificity, or completeness of the answer to the user's question.** Do not feel obligated to include all provided information; prioritize relevance to the query.
    * **Verification and Conflict:** Use the source to verify facts where appropriate. If there's a conflict between your general knowledge and the source, prioritize the source's specific data **if it is relevant to the question and appears accurate**, but use your expert judgment to omit information that seems erroneous or irrelevant to the user's query.
    * **Synthesis:** Weave together your general knowledge and the selected source information into a coherent, well-structured response.
    * **Clarity & Tone:** Use precise, professional chemical language. Aim for accessibility by briefly explaining potentially niche terms if needed.
    * **Directness & Comprehensiveness:** Address all parts of the user's question directly and thoroughly, enriched by the appropriately selected information.
    * **Source Attribution:** Do **not** mention "ontology" or refer to the 'Information Source' explicitly (e.g., avoid "according to the provided data..."). Present the integrated information as established chemical facts.
    * **Knowledge Expansion:** Feel free to supplement the response with your own expert knowledge on topics that may be absent from the 'Ontology Query Results' but are relevant to providing a complete answer to the user's question.
    * **Supramolecular Chemistry Style:** Tailor your response to appeal to supramolecular chemists by emphasizing host-guest interactions, non-covalent binding phenomena, molecular recognition principles, and structure-property relationships. Include relevant thermodynamic parameters, binding constants, and mechanistic insights where appropriate.

    **Answer:**
    """
        
        # Generate response using LLM
        try:
            response = answer_llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error generating response: {e}"

    def query_result_callback(future, query_idx, query_text):
        """Callback function to process Future results"""
        try:
            print(f"\nProcessing callback for query {query_idx}: '{query_text}'")
            
            # Get the future result
            result_dict = future.result(timeout=5)  # Small timeout to avoid indefinite waiting
            
            # Process the result using the agent
            answer = process_result_with_agent(result_dict, query_text)
            
            # Print the agent-generated answer
            print(f"\n--- Agent Answer for Query {query_idx} ---")
            print(answer)
            print("------------------------------")
            print(answer.content)
            
            return answer
        except Exception as e:
            print(f"Error processing result in callback: {e}")
            if future.exception():
                print(f"Future exception details: {future.exception()}")
            return None

    query_manager = QueryManager(max_workers=MAX_WORKERS, ontology_settings=test_ontology_settings)

    # Test code using callback functions to process query results

    if not llm:
        print("Skipping callback test due to LLM initialization failure.")
    else:
        print("\n--- Starting Callback Function Test ---")
        
        # Re-create query manager if needed
        if 'query_manager' not in locals() or not hasattr(query_manager, 'is_running') or not query_manager.is_running():
            query_manager = QueryManager(max_workers=MAX_WORKERS, ontology_settings=test_ontology_settings)
            query_manager.update_all_caches(test_onto)
            query_manager.start()
        
        # 创建一个闭包函数来捕获回调返回的answer
        def create_answer_collector():
            # 在闭包中创建一个存储结果的字典
            answers = {}
            
            # 创建一个能捕获answer的回调函数
            def answer_collector(future, query_idx, query_text):
                try:
                    result_dict = future.result(timeout=5)
                    # 处理结果并获取answer
                    answer = process_result_with_agent(result_dict, query_text)
                    # 将answer存储在闭包的answers字典中
                    answers[query_idx] = answer
                    print(f"查询 {query_idx} 的答案已保存")
                    return answer
                except Exception as e:
                    print(f"处理结果时出错: {e}")
                    return None
            
            # 返回回调函数和结果字典
            return answer_collector, answers

        # 创建回调函数和结果存储字典
        callback_collector, answers = create_answer_collector()

        # 提交查询并注册回调
        callback_futures = []
        for i, query_text in enumerate(queries):
            question = revised_queries[i]
            print(f"提交查询 {i+1}: '{query_text}'")
            future = query_manager.submit_query(query_text=query_text, query_context=query_context)
            
            # 使用functools.partial创建带参数的回调函数
            from functools import partial
            callback_func = partial(callback_collector, query_idx=i+1, query_text=question)
            
            # 注册回调函数
            future.add_done_callback(callback_func)
            callback_futures.append((i+1, query_text, future))
        
        # Wait for all Futures to complete (optional but ensures all callbacks execute)
        import concurrent.futures
        import time
        
        # Non-blocking check
        all_done = False
        wait_time = 0
        max_wait_time = 1200  # Maximum wait time
        check_interval = 5  # Check interval
        
        print("\nWaiting for callbacks to execute...")
        while not all_done and wait_time < max_wait_time:
            all_done = all(future[2].done() for future in callback_futures)
            if not all_done:
                print(f"Waited {wait_time} seconds, continuing to wait for callbacks...")
                time.sleep(check_interval)
                wait_time += check_interval
        
        if all_done:
            print("\nAll callbacks have completed!")
        else:
            print(f"\nTimeout waiting, some queries may not have completed. Waited {wait_time} seconds.")
        
        # Stop query manager
        print("\nStopping QueryManager...")
        query_manager.stop()
        print("QueryManager stopped.")
        
        print("--- Callback Function Test Finished ---")

    future_list = [future[2].result() for future in callback_futures]

    # 自动保存future_list中每个future的iteration_history和formatted_results
    # 使用之前已经创建的results_dir和timestamp

    from langchain_core.messages import AIMessage

    results = []
    for idx, answer in answers.items():
        if isinstance(answer, AIMessage):
            q = queries[idx-1]
            print(f"{idx}.查询的最终答案: {answer.content}\n")
            results.append({"query": q, "response": answer.content})
        else:
            print("error")

    print(f"\n保存测试结果到: {results_dir}")

    # 保存每个future的结果
    for i, result in enumerate(future_list):
        query_num = i + 1
        
        # 保存iteration_history
        if "iteration_history" in result:
            history_file = f"{results_dir}/query_{query_num}_iteration_history.txt"
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write(f"Query {query_num} - Iteration History\n")
                f.write("=" * 50 + "\n")
                f.write(f"Time: {datetime.datetime.now()}\n\n")
                if isinstance(result["iteration_history"], str):
                    f.write(result["iteration_history"])
                else:
                    f.write(str(result["iteration_history"]))
            print(f"已保存 Query {query_num} iteration_history")
        
        # 保存formatted_results  
        if "formatted_results" in result:
            results_file = f"{results_dir}/query_{query_num}_formatted_results.txt"
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write(f"Query {query_num} - Formatted Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"Time: {datetime.datetime.now()}\n\n")
                if isinstance(result["formatted_results"], str):
                    f.write(result["formatted_results"])
                else:
                    f.write(str(result["formatted_results"]))
            print(f"已保存 Query {query_num} formatted_results")

    print(f"\n所有结果已保存到文件夹: {results_dir}")

    # 保存最终结果为JSON和Markdown文件
    model_name = f"{args.query_llm}-query_{args.answer_llm}-answer"
    if args.runs > 1:
        model_name += f"_run{run_num}"
    
    json_filename = f"{results_dir}/{model_name}.json"
    md_filename = f"{results_dir}/{model_name}.md"
    
    # 将结果保存为JSON文件
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"已保存 JSON 结果文件: {json_filename}")
    
    # 生成Markdown内容，二级标题（query）带序号
    markdown_output = f"# {model_name}\n\n"
    for idx, result in enumerate(results, 1):
        markdown_output += f"## {idx}. {result['query']}\n\n"
        markdown_output += f"{result['response']}\n\n"
    
    # 保存为Markdown文件
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(markdown_output)
    print(f"已保存 Markdown 结果文件: {md_filename}")
    
    # 计算运行用时
    run_end_time = time.time()
    run_duration = run_end_time - run_start_time
    print(f"\n第 {run_num}/{args.runs} 次运行结束")
    print(f"运行结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_end_time))}")
    print(f"本次运行用时: {run_duration:.2f} 秒 ({run_duration/60:.2f} 分钟)")
    
    # 恢复标准输出
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    log_file.close()
    
    print(f"第 {run_num}/{args.runs} 次运行完成")

print(f"\n{'='*60}")
print(f"所有 {args.runs} 次运行已完成")
# 计算总用时
overall_end_time = time.time()
total_duration = overall_end_time - overall_start_time
print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_end_time))}")
print(f"总用时: {total_duration:.2f} 秒 ({total_duration/60:.2f} 分钟)")
if args.runs > 1:
    avg_time = total_duration / args.runs
    print(f"平均每次运行用时: {avg_time:.2f} 秒 ({avg_time/60:.2f} 分钟)")
print(f"{'='*60}")
