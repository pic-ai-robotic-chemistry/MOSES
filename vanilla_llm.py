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

base_folder_path = r"test_results/vanilla_llm/"

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run vanilla LLM test with specified model(s) and repeat runs')
parser.add_argument('--models', nargs='+', default=['gpt-4.1-nano'], help='LLM model name(s) - can specify multiple models (default: gpt-4.1-nano)')
parser.add_argument('--runs', type=int, default=1, help='Number of times to run each model (default: 1)')
args = parser.parse_args()

print(f"Using models: {args.models}")
print(f"Will run each model {args.runs} time(s)")
print(f"Total runs: {len(args.models) * args.runs}")


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



print(len(queries),len(revised_queries))

# queries = [queries[4], queries[6], queries[20]]
# revised_queries =  [revised_queries[4],  revised_queries[6],  revised_queries[20]]

# queries = [queries[4]]
# revised_queries =  [revised_queries[4]]

print(len(queries),len(revised_queries))


# 记录整体开始时间
overall_start_time = time.time()
print(f"\n{'='*60}")
print(f"开始执行测试 - 总共 {len(args.models)} 个模型，每个模型 {args.runs} 次运行")
print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_start_time))}")
print(f"{'='*60}")

# 外层循环：遍历所有模型
for model_idx, model_name in enumerate(args.models, 1):
    print(f"\n{'*'*50}")
    print(f"开始处理模型 {model_idx}/{len(args.models)}: {model_name}")
    print(f"{'*'*50}")
    
    # 内层循环：每个模型重复运行指定次数
    for run_num in range(1, args.runs + 1):
        run_start_time = time.time()
        
        # 为每个模型创建专属文件夹
        results_dir = f"{base_folder_path}{model_name}"
        os.makedirs(results_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"模型 {model_name} - 第 {run_num}/{args.runs} 次运行")
        print(f"运行开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_start_time))}")
        print(f"结果保存目录: {results_dir}")
        print(f"{'='*60}")

        # o1 和 o3 模型不支持 temperature=0，只支持默认值 1
        if model_name.startswith('o'):
            answer_llm = ChatOpenAI(
                        model_name=model_name,
                        max_tokens=5000,
                        temperature=1,
                    )
        else:
            answer_llm = ChatOpenAI(
                        model_name=model_name,
                        temperature=0,
                        max_tokens=5000,
                    )

        res_list = []
        for i, ques in enumerate(revised_queries):
            response = answer_llm.invoke(ques)
            res_list.append(response)
            print(f"完成 {i+1} 个回答")

        # 生成文件名（带时间戳和运行次数）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.runs > 1:
            model_filename = f"{timestamp}_{model_name}_run{run_num}"
        else:
            model_filename = f"{timestamp}_{model_name}"
            
        md_filename = f"{results_dir}/{model_filename}.md"
        json_filename = f"{results_dir}/{model_filename}.json"

        results = []
        for i, res in enumerate(res_list):
            q = queries[i]
            print(f"{i+1}.查询 {q} 的答案是：{res.content}\n")
            results.append({"query": q, "response": res.content})

        # 将结果保存为JSON文件
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        # 生成Markdown内容，二级标题（query）带序号
        markdown_output = f"# {model_filename}\n\n"
        for idx, result in enumerate(results, 1):
            markdown_output += f"## {idx}. {result['query']}\n\n"
            markdown_output += f"{result['response']}\n\n"

        # 保存为Markdown文件
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_output)
            
        # 计算运行用时
        run_end_time = time.time()
        run_duration = run_end_time - run_start_time
        print(f"\n模型 {model_name} - 第 {run_num}/{args.runs} 次运行结束")
        print(f"运行结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_end_time))}")
        print(f"本次运行用时: {run_duration:.2f} 秒 ({run_duration/60:.2f} 分钟)")
        print(f"已保存 JSON 结果文件: {json_filename}")
        print(f"已保存 Markdown 结果文件: {md_filename}")
        
        print(f"模型 {model_name} - 第 {run_num}/{args.runs} 次运行完成")

    print(f"\n{'*'*50}")
    print(f"模型 {model_name} 的所有 {args.runs} 次运行已完成")
    print(f"{'*'*50}")

print(f"\n{'='*60}")
print(f"所有 {len(args.models)} 个模型的测试已完成")
# 计算总用时
overall_end_time = time.time()
total_duration = overall_end_time - overall_start_time
print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_end_time))}")
print(f"总用时: {total_duration:.2f} 秒 ({total_duration/60:.2f} 分钟)")
total_runs = len(args.models) * args.runs
if total_runs > 1:
    avg_time = total_duration / total_runs
    print(f"平均每次运行用时: {avg_time:.2f} 秒 ({avg_time/60:.2f} 分钟)")
print(f"{'='*60}")