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

base_folder_path = r"test_results/IDA/"
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
            # closed_ontology_file_name="IDA-closed.owl" 
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

    import json

    def generate_questions_from_config(config_file_name='IDA.json'):
        """
        从JSON配置文件加载所有数据并生成多选题。
        """
        # 1. 读取并解析JSON配置文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_file_name)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"错误：配置文件 '{config_path}' 未找到。")
            return
        except json.JSONDecodeError as e:
            print(f"错误：配置文件 '{config_path}' 格式不正确，请检查JSON语法。\n{e}")
            return

        # 2. 从配置中提取数据
        # 直接使用模板字符串，不再需要join
        question_template = config.get('template')
        descriptions = config.get('descriptions', {})
        combinations = config.get('combinations', [])

        if not all([question_template, descriptions, combinations]):
            print("错误：配置文件中缺少 'template', 'descriptions', 或 'combinations' 的数据。")
            return

        # 3. 循环并生成题目
        generated_questions = []
        for i, combo in enumerate(combinations):
            question_number = i + 1
            
            # 从描述字典中获取全名和描述
            def get_desc(key):
                return descriptions.get(key, f"【描述未找到: {key}】")

            host_name = get_desc(combo['host'])
            indicator_name = get_desc(combo['indicator'])
            analyte_name = get_desc(combo['analyte'])

            unknown_role = combo['unknown'].capitalize() # e.g., "Analyte"
            
            # 动态确定已知和未知组件
            components = {
                "Host": f"{host_name} (Host A)",
                "Indicator": f"{indicator_name} (Indicator B)",
                "Analyte": f"{analyte_name} (Analyte C)"
            }
            
            # 移除未知的那个，剩下就是已知的
            known_components = [v for k, v in components.items() if k != unknown_role]
            
            # 生成选项列表
            option_texts = []
            for opt_key in combo['options']:
                option_texts.append(f"* {get_desc(opt_key)}")
            options_str = "\n".join(option_texts)

            # 填充模板
            full_question = question_template.format(
                question_number=f" #{question_number}",
                known_comp1_name_and_role=known_components[0],
                known_comp2_name_and_role=known_components[1],
                unknown_comp_role=f"{unknown_role} ({components[unknown_role][-2]})", # e.g., "Analyte (C)"
                options=options_str
            )
            generated_questions.append(full_question)

        # 4. 保存结果到文件
        output_filename = os.path.join(script_dir, 'generated_ida_questions.md') # 保存为.md文件，格式更美观
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                for i, question in enumerate(generated_questions):
                    f.write(question)
                    # 在每个问题后添加分页符，以便打印或分隔
                    if i < len(generated_questions) - 1:
                        f.write("\n\n---\n\n")
            
            print(f"任务完成！成功生成 {len(generated_questions)} 道题目。")
            print(f"结果已保存到文件: '{output_filename}'")
        # 将 generated_questions 序列化为文件，便于后续加载和使用
            serialized_filename = os.path.join(script_dir, 'generated_ida_questions.json')
            try:
                with open(serialized_filename, 'w', encoding='utf-8') as f_json:
                    json.dump(generated_questions, f_json, ensure_ascii=False, indent=2)
                print(f"已将 generated_questions 序列化保存到: '{serialized_filename}'")
            except Exception as e:
                print(f"序列化 generated_questions 时出错: {e}")
        except IOError as e:
            print(f"错误：无法写入输出文件。原因: {e}")

        return generated_questions


    ida_choice = generate_questions_from_config()

    queries = ida_choice
    revised_queries = ida_choice
    query_context = {
        "ontology": test_ontology_settings,
        "originating_team": "test_notebook",
        "originating_stage": "manual_test",
        "query_type": "analytical_reasoning"
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
