#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# 定义需要分析的测试运行文件夹（8月22日22点前的前7个）
test_runs = [
    "20250822_104514_test_run1",
    "20250822_110220_test_run2", 
    "20250822_114039_test_run",
    "20250822_122445_test_run1",
    "20250822_132829_test_run2",
    "20250822_133739_test_run_run1", 
    "20250822_134803_test_run"
]

base_path = Path(r"C:\d\CursorProj\Chem-Ontology-Constructor\test_results\final-2\MOSES")

def extract_last_tried_tool_calls(iteration_file):
    """从迭代历史文件中提取最后一个tried_tool_calls"""
    try:
        with open(iteration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式查找所有包含tried_tool_calls的部分
        pattern = r"'tried_tool_calls': ({[^}]+(?:{[^}]*}[^}]*)*})"
        matches = re.findall(pattern, content)
        
        if not matches:
            # 如果没有找到，尝试更简单的模式
            if 'tried_tool_calls' in content:
                # 查找最后一个tried_tool_calls出现的位置
                last_pos = content.rfind('tried_tool_calls')
                if last_pos != -1:
                    # 提取从该位置开始的一段文本进行处理
                    excerpt = content[last_pos-100:last_pos+2000]
                    try:
                        # 尝试解析为JSON
                        import ast
                        start_brace = excerpt.find('{', excerpt.find('tried_tool_calls'))
                        if start_brace != -1:
                            brace_count = 0
                            end_pos = start_brace
                            for i, char in enumerate(excerpt[start_brace:]):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_pos = start_brace + i + 1
                                        break
                            
                            json_str = excerpt[start_brace:end_pos]
                            # 尝试使用ast.literal_eval解析
                            return ast.literal_eval(json_str)
                    except:
                        pass
            return None
        
        # 返回最后一个匹配项并尝试解析
        try:
            import ast
            return ast.literal_eval(matches[-1])
        except:
            try:
                return json.loads(matches[-1])
            except:
                return None
                
    except Exception as e:
        print(f"Error processing {iteration_file}: {e}")
        return None

def extract_get_information_by_source_results(tried_tool_calls):
    """从tried_tool_calls中提取get_information_by_source的结果"""
    if not tried_tool_calls:
        return []
    
    results = []
    for call_id, call_data in tried_tool_calls.items():
        if call_data.get('tool') == 'get_information_by_source':
            result = call_data.get('result', {})
            params = call_data.get('params', {})
            results.append({
                'call_id': call_id,
                'params': params,
                'result': result
            })
    
    return results

def get_query_number_from_filename(filename):
    """从文件名提取query编号"""
    match = re.search(r'query_(\d+)_iteration_history\.txt', filename)
    return int(match.group(1)) if match else None

# 主要分析逻辑
print("分析前7次测试运行中的get_information_by_source工具调用结果")
print("=" * 80)

all_analysis = {}

for test_run in test_runs:
    print(f"\n正在分析: {test_run}")
    print("-" * 50)
    
    test_run_path = base_path / test_run
    if not test_run_path.exists():
        print(f"路径不存在: {test_run_path}")
        continue
    
    # 找到所有iteration_history文件
    iteration_files = list(test_run_path.glob("*iteration_history.txt"))
    
    run_analysis = {}
    
    for iteration_file in sorted(iteration_files):
        query_num = get_query_number_from_filename(iteration_file.name)
        if query_num is None:
            continue
        
        print(f"  处理 Query {query_num}...")
        
        # 提取最后一个tried_tool_calls
        last_tried_calls = extract_last_tried_tool_calls(iteration_file)
        
        # 提取get_information_by_source结果
        get_info_results = extract_get_information_by_source_results(last_tried_calls)
        
        if get_info_results:
            run_analysis[query_num] = {
                'file': str(iteration_file),
                'get_information_by_source_calls': len(get_info_results),
                'results': get_info_results[:3]  # 只保留前3个结果用于展示
            }
            print(f"    找到 {len(get_info_results)} 个get_information_by_source调用")
    
    all_analysis[test_run] = run_analysis

print("\n" + "=" * 80)
print("详细分析结果")
print("=" * 80)

# 统计每个query在所有测试运行中的使用情况
query_usage = {}
for test_run, run_data in all_analysis.items():
    for query_num, query_data in run_data.items():
        if query_num not in query_usage:
            query_usage[query_num] = []
        query_usage[query_num].append({
            'test_run': test_run,
            'calls': query_data['get_information_by_source_calls'],
            'sample_results': query_data['results']
        })

# 按query编号排序输出
for query_num in sorted(query_usage.keys()):
    print(f"\n### Query {query_num} ###")
    print(f"在 {len(query_usage[query_num])} 个测试运行中使用了get_information_by_source")
    
    total_calls = sum(usage['calls'] for usage in query_usage[query_num])
    print(f"总调用次数: {total_calls}")
    
    # 显示一个样本结果
    if query_usage[query_num][0]['sample_results']:
        sample = query_usage[query_num][0]['sample_results'][0]
        print(f"样本调用参数: {sample.get('params', {})}")
        
        # 显示结果中的关键信息
        result = sample.get('result', {})
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict) and 'information' in value:
                    info_count = len(value['information']) if isinstance(value['information'], list) else 0
                    print(f"  {key}: 找到 {info_count} 条信息")
    
    print()

print("=" * 80)
print("现在需要对比参考答案，请查看PDF文件中对应的题目答案")
print("PDF文件包含了Question 1-27的标准答案")
print("每个query号对应PDF中的相应问题编号")