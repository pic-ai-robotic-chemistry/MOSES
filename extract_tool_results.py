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

def extract_tool_calls_from_file(iteration_file):
    """从迭代历史文件中提取get_information_by_source工具调用结果"""
    try:
        with open(iteration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找最后一个tried_tool_calls
        pattern = r"'tried_tool_calls': ({.*?})}(?=, 'retry_count':|$)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            return []
        
        last_match = matches[-1]
        
        # 尝试解析tried_tool_calls字典
        try:
            # 使用正则表达式提取get_information_by_source调用
            get_info_pattern = r"'(get_information_by_source_[^']+)': ({.*?})}(?=(?:, 'get_|$))"
            get_info_matches = re.findall(get_info_pattern, last_match, re.DOTALL)
            
            results = []
            for call_id, call_data_str in get_info_matches:
                try:
                    # 手动解析调用数据
                    # 提取参数
                    params_match = re.search(r"'params': ({.*?})", call_data_str, re.DOTALL)
                    if params_match:
                        params_str = params_match.group(1)
                        # 简化参数提取
                        class_names_match = re.search(r"'class_names': (\[.*?\])", params_str)
                        source_match = re.search(r"'source': '([^']+)'", params_str)
                        
                        class_names = []
                        source = ""
                        
                        if class_names_match:
                            class_names_str = class_names_match.group(1)
                            class_names = re.findall(r"'([^']+)'", class_names_str)
                        
                        if source_match:
                            source = source_match.group(1)
                    
                    # 提取结果
                    result_match = re.search(r"'result': ({.*?})", call_data_str, re.DOTALL)
                    result_summary = {}
                    
                    if result_match:
                        result_str = result_match.group(1)
                        # 为每个类名查找结果
                        for class_name in class_names:
                            class_pattern = rf"'{re.escape(class_name)}': (\[.*?\])"
                            class_match = re.search(class_pattern, result_str, re.DOTALL)
                            if class_match:
                                list_content = class_match.group(1)
                                # 简单计算列表中的元素数量
                                if list_content.strip() == '[]':
                                    result_summary[class_name] = 0
                                else:
                                    # 粗略统计信息条数
                                    info_count = list_content.count("'information':")
                                    if info_count == 0:
                                        info_count = list_content.count('{')  # 备用方法
                                    result_summary[class_name] = info_count
                    
                    results.append({
                        'call_id': call_id,
                        'params': {'class_names': class_names, 'source': source},
                        'result_summary': result_summary
                    })
                    
                except Exception as e:
                    print(f"  Error parsing call {call_id}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"  Error parsing tried_tool_calls: {e}")
            return []
            
    except Exception as e:
        print(f"Error processing {iteration_file}: {e}")
        return []

def get_query_number_from_filename(filename):
    """从文件名提取query编号"""
    match = re.search(r'query_(\d+)_iteration_history\.txt', filename)
    return int(match.group(1)) if match else None

# 主要分析逻辑
print("提取前7次测试运行中的get_information_by_source工具调用结果")
print("=" * 80)

all_results = {}

for test_run in test_runs:
    print(f"\n正在分析: {test_run}")
    print("-" * 50)
    
    test_run_path = base_path / test_run
    if not test_run_path.exists():
        print(f"路径不存在: {test_run_path}")
        continue
    
    # 找到所有iteration_history文件
    iteration_files = list(test_run_path.glob("*iteration_history.txt"))
    
    run_results = {}
    
    for iteration_file in sorted(iteration_files):
        query_num = get_query_number_from_filename(iteration_file.name)
        if query_num is None:
            continue
        
        # 提取工具调用结果
        tool_calls = extract_tool_calls_from_file(iteration_file)
        
        if tool_calls:
            run_results[query_num] = tool_calls
            print(f"  Query {query_num}: 找到 {len(tool_calls)} 个get_information_by_source调用")
            
            # 显示一个简要的结果摘要
            for call in tool_calls[:2]:  # 只显示前2个
                params = call['params']
                summary = call['result_summary']
                print(f"    - 类别: {params['class_names'][:3]}...")  # 只显示前3个类别
                print(f"    - 源: {params['source']}")
                total_info = sum(summary.values())
                print(f"    - 总信息条数: {total_info}")
    
    all_results[test_run] = run_results

print("\n" + "=" * 80)
print("汇总结果")
print("=" * 80)

# 统计每个query的使用情况
query_stats = {}
for test_run, run_data in all_results.items():
    for query_num, calls in run_data.items():
        if query_num not in query_stats:
            query_stats[query_num] = []
        
        for call in calls:
            total_info = sum(call['result_summary'].values())
            query_stats[query_num].append({
                'test_run': test_run,
                'class_names': call['params']['class_names'],
                'source': call['params']['source'],
                'total_info_found': total_info,
                'class_results': call['result_summary']
            })

# 按query编号排序输出
for query_num in sorted(query_stats.keys()):
    print(f"\n### Query {query_num} ###")
    calls_data = query_stats[query_num]
    print(f"在 {len(set(call['test_run'] for call in calls_data))} 个测试运行中使用")
    
    total_info_all = sum(call['total_info_found'] for call in calls_data)
    print(f"总共找到信息: {total_info_all} 条")
    
    # 显示一个代表性的调用
    if calls_data:
        sample = calls_data[0]
        print(f"查询类别: {sample['class_names']}")
        print(f"查询源: {sample['source']}")
        print(f"各类别结果: {sample['class_results']}")

print("\n" + "=" * 80)
print("现在需要将这些结果与PDF参考答案进行对比分析")