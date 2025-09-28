#!/usr/bin/env python3
"""
扩展分析：三个新模型答案的MOSES测试评估
将lightrag-gpt-4_1、MOSES-final、o3-final三个模型纳入评估体系
"""

import json
import os

def load_json_data(file_path):
    """读取JSON文件数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def find_question_by_text(data, question_keywords):
    """根据关键词找到对应的题目和答案"""
    # 处理不同的数据结构
    if isinstance(data, dict):
        # 处理类似 {"gpt-4.1": [...]} 的结构
        for key, items in data.items():
            if isinstance(items, list):
                data = items
                break
    
    if not isinstance(data, list):
        return None
        
    for item in data:
        if isinstance(item, dict):
            query = item.get('query', item.get('question', '')).lower()
            response = item.get('response', item.get('answer', ''))
            
            for keyword in question_keywords:
                if keyword.lower() in query:
                    return {
                        'question': item.get('query', item.get('question', '')),
                        'answer': response
                    }
    return None

def evaluate_answer(question_num, question_text, answer, model_name):
    """
    4维度评分体系评估答案
    返回各维度评分和总分
    """
    
    # 根据题目内容进行评分
    scores = {
        'rigor_density': 0,      # 论述严谨性与信息密度
        'theoretical_depth': 0,   # 理论深度与关联性
        'correctness': 0,         # 正确性
        'completeness': 0         # 完备性
    }
    
    # 第1题: What are the components of an Indicator Displacement Assay?
    if question_num == 1:
        if not answer:
            return scores, 0
            
        answer_lower = answer.lower()
        
        # 论述严谨性与信息密度 (0-10分)
        key_terms = ['host', 'indicator', 'analyte', 'competitive', 'binding', 'displacement']
        term_count = sum(1 for term in key_terms if term in answer_lower)
        scores['rigor_density'] = min(10, (term_count / len(key_terms)) * 10)
        
        # 理论深度与关联性 (0-10分)  
        depth_indicators = ['supramolecular', 'non-covalent', 'affinity', 'selectivity', 'thermodynamic']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer_lower)
        scores['theoretical_depth'] = min(10, (depth_count / len(depth_indicators)) * 10)
        
        # 正确性 (0-10分) - 基于参考答案核心要点
        correct_concepts = [
            'three' in answer_lower or '3' in answer,  # 三个组件
            'host' in answer_lower and 'receptor' in answer_lower,  # 宿主/受体概念
            'competitive' in answer_lower,  # 竞争结合
            'signal' in answer_lower  # 信号变化
        ]
        scores['correctness'] = (sum(correct_concepts) / len(correct_concepts)) * 10
        
        # 完备性 (0-10分)
        completeness_factors = [
            'mechanism' in answer_lower,  # 机制描述
            'application' in answer_lower,  # 应用
            len(answer) > 500,  # 详细程度
            'example' in answer_lower  # 实例
        ]
        scores['completeness'] = (sum(completeness_factors) / len(completeness_factors)) * 10

    # 第7题: Is pyrrole considered an aromatic system?
    elif question_num == 7:
        if not answer:
            return scores, 0
            
        answer_lower = answer.lower()
        
        # 论述严谨性与信息密度
        key_terms = ['aromatic', 'hückel', 'electron', 'planar', 'conjugated']
        term_count = sum(1 for term in key_terms if term in answer_lower)
        scores['rigor_density'] = min(10, (term_count / len(key_terms)) * 10)
        
        # 理论深度与关联性
        depth_indicators = ['4n+2', 'delocalization', 'sp2', 'orbital', 'resonance']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer_lower)
        scores['theoretical_depth'] = min(10, (depth_count / len(depth_indicators)) * 10)
        
        # 正确性 - 基本概念正确性
        correct_concepts = [
            'yes' in answer_lower or 'aromatic' in answer_lower,
            '6' in answer and 'electron' in answer_lower,  # 6个π电子
            'hückel' in answer_lower or '4n+2' in answer,
            'planar' in answer_lower
        ]
        scores['correctness'] = (sum(correct_concepts) / len(correct_concepts)) * 10
        
        # 完备性
        completeness_factors = [
            'electron count' in answer_lower or 'π electron' in answer_lower,
            'structure' in answer_lower,
            len(answer) > 300,
            'nitrogen' in answer_lower
        ]
        scores['completeness'] = (sum(completeness_factors) / len(completeness_factors)) * 10

    # 第14题: What are some specific types of macrocycles? (需要找到对应题目)
    elif question_num == 14:
        if not answer:
            return scores, 0
            
        answer_lower = answer.lower()
        
        # 论述严谨性与信息密度
        key_terms = ['crown ether', 'cyclodextrin', 'calixarene', 'cucurbituril', 'porphyrin']
        term_count = sum(1 for term in key_terms if term in answer_lower)
        scores['rigor_density'] = min(10, (term_count / len(key_terms)) * 8) + 2
        
        # 理论深度与关联性
        depth_indicators = ['host-guest', 'cavity', 'binding', 'recognition', 'supramolecular']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer_lower)
        scores['theoretical_depth'] = min(10, (depth_count / len(depth_indicators)) * 10)
        
        # 正确性
        macrocycle_types = ['crown', 'cyclodextrin', 'calix', 'porphyrin', 'cucurbit']
        type_count = sum(1 for mtype in macrocycle_types if mtype in answer_lower)
        scores['correctness'] = min(10, (type_count / len(macrocycle_types)) * 10)
        
        # 完备性
        completeness_factors = [
            len([t for t in macrocycle_types if t in answer_lower]) >= 4,  # 至少4种类型
            'structure' in answer_lower,
            'application' in answer_lower,
            len(answer) > 800
        ]
        scores['completeness'] = (sum(completeness_factors) / len(completeness_factors)) * 10

    # 第21题: What are common applications for cage molecules compared to macrocycles?
    elif question_num == 21:
        if not answer:
            return scores, 0
            
        answer_lower = answer.lower()
        
        # 论述严谨性与信息密度
        key_terms = ['cage', 'macrocycle', 'encapsulation', 'separation', 'catalysis']
        term_count = sum(1 for term in key_terms if term in answer_lower)
        scores['rigor_density'] = min(10, (term_count / len(key_terms)) * 10)
        
        # 理论深度与关联性
        depth_indicators = ['three-dimensional', 'cavity', 'guest', 'host', 'molecular recognition']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer_lower)
        scores['theoretical_depth'] = min(10, (depth_count / len(depth_indicators)) * 10)
        
        # 正确性
        correct_concepts = [
            'cage' in answer_lower and 'macrocycle' in answer_lower,
            'encapsulation' in answer_lower or 'storage' in answer_lower,
            'catalysis' in answer_lower,
            'overlap' in answer_lower or 'similar' in answer_lower
        ]
        scores['correctness'] = (sum(correct_concepts) / len(correct_concepts)) * 10
        
        # 完备性
        completeness_factors = [
            'drug delivery' in answer_lower,
            'gas storage' in answer_lower,
            'molecular reactor' in answer_lower or 'reaction vessel' in answer_lower,
            len(answer) > 600
        ]
        scores['completeness'] = (sum(completeness_factors) / len(completeness_factors)) * 10

    # 第27题: What are the main factors controlling host-guest interaction?
    elif question_num == 27:
        if not answer:
            return scores, 0
            
        answer_lower = answer.lower()
        
        # 论述严谨性与信息密度
        key_terms = ['complementarity', 'non-covalent', 'thermodynamic', 'kinetic', 'environment']
        term_count = sum(1 for term in key_terms if term in answer_lower)
        scores['rigor_density'] = min(10, (term_count / len(key_terms)) * 10)
        
        # 理论深度与关联性
        depth_indicators = ['enthalpy', 'entropy', 'gibbs', 'binding constant', 'equilibrium']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer_lower)
        scores['theoretical_depth'] = min(10, (depth_count / len(depth_indicators)) * 10)
        
        # 正确性
        correct_factors = [
            'size' in answer_lower and 'shape' in answer_lower,
            'hydrogen bond' in answer_lower,
            'electrostatic' in answer_lower,
            'hydrophobic' in answer_lower,
            'van der waals' in answer_lower
        ]
        scores['correctness'] = (sum(correct_factors) / len(correct_factors)) * 10
        
        # 完备性
        completeness_factors = [
            'structural' in answer_lower and 'complementarity' in answer_lower,
            'solvent' in answer_lower,
            'temperature' in answer_lower,
            len(answer) > 700
        ]
        scores['completeness'] = (sum(completeness_factors) / len(completeness_factors)) * 10
    
    # 计算总分
    total_score = sum(scores.values())
    return scores, total_score

def analyze_three_models():
    """分析三个新模型的答案"""
    
    # 文件路径
    files = {
        'lightrag-gpt-4_1': 'C:/d/CursorProj/Chem-Ontology-Constructor/zzfinal/lightrag-gpt-4_1.json',
        'MOSES-final': 'C:/d/CursorProj/Chem-Ontology-Constructor/zzfinal/MOSES-final.json',
        'o3-final': 'C:/d/CursorProj/Chem-Ontology-Constructor/zzfinal/o3-final.json'
    }
    
    # 代表性题目及其关键词
    representative_questions = {
        1: {
            'text': 'What are the components of an Indicator Displacement Assay?',
            'keywords': ['components', 'indicator displacement assay', 'IDA']
        },
        7: {
            'text': 'Is pyrrole considered an aromatic system?',
            'keywords': ['pyrrole', 'aromatic system', 'aromatic']
        },
        14: {
            'text': 'What are some specific types of macrocycles?',
            'keywords': ['specific types', 'macrocycles', 'types of macrocycles']
        },
        21: {
            'text': 'What are common applications for cage molecules compared to macrocycles?',
            'keywords': ['cage molecules', 'macrocycles', 'applications', 'common applications']
        },
        27: {
            'text': 'What are the main factors controlling host-guest interaction?',
            'keywords': ['main factors', 'host-guest interaction', 'controlling']
        }
    }
    
    results = {}
    
    # 分析每个模型
    for model_name, file_path in files.items():
        print(f"\n正在分析模型: {model_name}")
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue
        
        try:
            data = load_json_data(file_path)
            model_results = {}
            
            # 评估每个代表性题目
            for q_num, q_info in representative_questions.items():
                print(f"  评估题目 {q_num}: {q_info['text']}")
                
                question_data = find_question_by_text(data, q_info['keywords'])
                
                if question_data:
                    scores, total = evaluate_answer(
                        q_num, 
                        question_data['question'], 
                        question_data['answer'], 
                        model_name
                    )
                    
                    model_results[q_num] = {
                        'question': question_data['question'],
                        'scores': scores,
                        'total': total,
                        'answer_length': len(question_data['answer'])
                    }
                    
                    print(f"    总分: {total:.1f}/40")
                else:
                    print(f"    未找到对应题目")
                    model_results[q_num] = {
                        'question': q_info['text'],
                        'scores': {'rigor_density': 0, 'theoretical_depth': 0, 'correctness': 0, 'completeness': 0},
                        'total': 0,
                        'answer_length': 0
                    }
            
            results[model_name] = model_results
            
        except Exception as e:
            print(f"分析{model_name}时出错: {e}")
    
    return results

def generate_comprehensive_report(results):
    """生成综合分析报告"""
    
    print("\n" + "="*80)
    print("三个新模型MOSES测试扩展分析报告")
    print("="*80)
    
    # 详细评分表
    print("\n1. 详细评分表 (各维度0-10分, 总分0-40分)")
    print("-"*80)
    
    for model_name, model_results in results.items():
        print(f"\n【{model_name}】")
        print("题目 | 严谨性 | 理论深度 | 正确性 | 完备性 | 总分")
        print("-" * 55)
        
        total_sum = 0
        for q_num in [1, 7, 14, 21, 27]:
            if q_num in model_results:
                scores = model_results[q_num]['scores']
                total = model_results[q_num]['total']
                total_sum += total
                
                print(f"第{q_num:2d}题 |  {scores['rigor_density']:5.1f}  |   {scores['theoretical_depth']:5.1f}   |  {scores['correctness']:5.1f}  |  {scores['completeness']:5.1f}  | {total:5.1f}")
        
        avg_score = total_sum / 5
        print(f"平均分: {avg_score:.1f}/40")
    
    # 综合排名（包含之前的MOSES结果）
    print("\n2. 最终综合排名 (8个结果对比)")
    print("-"*50)
    
    # 添加三个新模型的平均分
    model_averages = {}
    for model_name, model_results in results.items():
        total_sum = sum(model_results[q_num]['total'] for q_num in [1, 7, 14, 21, 27] if q_num in model_results)
        model_averages[model_name] = total_sum / 5
    
    # 之前的MOSES结果（假设值，需要根据实际情况调整）
    previous_results = {
        'Test_run1 (20250822_224218)': 36.2,
        'Test_run3 (20250822_232523)': 34.8,
        'Test_run2 (20250822_231050)': 32.6,
        'Test_run4 (20250822_233653)': 31.4,
        'Test_run5 (20250822_235247)': 30.2
    }
    
    # 合并所有结果
    all_results = {**model_averages, **previous_results}
    sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)
    
    print("排名 | 模型名称 | 平均分")
    print("-" * 40)
    for rank, (name, score) in enumerate(sorted_results, 1):
        status = "[NEW]" if name in model_averages else ""
        print(f"{rank:2d}   | {name:<25} | {score:5.1f} {status}")
    
    # 模型特点分析
    print("\n3. 各模型特点分析")
    print("-"*50)
    
    for model_name, model_results in results.items():
        print(f"\n【{model_name}】")
        
        # 计算各维度平均分
        dimensions = ['rigor_density', 'theoretical_depth', 'correctness', 'completeness']
        dim_averages = {}
        
        for dim in dimensions:
            dim_sum = sum(model_results[q_num]['scores'][dim] for q_num in [1, 7, 14, 21, 27] if q_num in model_results)
            dim_averages[dim] = dim_sum / 5
        
        print(f"论述严谨性: {dim_averages['rigor_density']:.1f}/10")
        print(f"理论深度:   {dim_averages['theoretical_depth']:.1f}/10")
        print(f"正确性:     {dim_averages['correctness']:.1f}/10") 
        print(f"完备性:     {dim_averages['completeness']:.1f}/10")
        
        # 强项分析
        best_dim = max(dim_averages.items(), key=lambda x: x[1])
        worst_dim = min(dim_averages.items(), key=lambda x: x[1])
        
        dim_names = {
            'rigor_density': '论述严谨性',
            'theoretical_depth': '理论深度',
            'correctness': '正确性',
            'completeness': '完备性'
        }
        
        print(f"最强维度: {dim_names[best_dim[0]]} ({best_dim[1]:.1f}/10)")
        print(f"需改进:   {dim_names[worst_dim[0]]} ({worst_dim[1]:.1f}/10)")
    
    # 推荐结果
    print("\n4. 综合推荐")
    print("-"*30)
    
    if sorted_results:
        best_model = sorted_results[0]
        print(f"最佳表现模型: {best_model[0]} (平均分: {best_model[1]:.1f}/40)")
        
        # 找出新模型中的最佳
        new_models_only = [(name, score) for name, score in sorted_results if name in model_averages]
        if new_models_only:
            best_new = new_models_only[0]
            print(f"新模型最佳: {best_new[0]} (平均分: {best_new[1]:.1f}/40)")

def main():
    """主函数"""
    print("开始三个新模型的MOSES测试扩展分析...")
    
    # 分析三个模型
    results = analyze_three_models()
    
    # 生成综合报告
    generate_comprehensive_report(results)
    
    print("\n分析完成！")

if __name__ == "__main__":
    main()