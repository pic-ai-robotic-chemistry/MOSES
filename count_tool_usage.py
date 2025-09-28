#!/usr/bin/env python3
import os
import glob
import re

# 定义路径
base_path = r"C:\d\CursorProj\Chem-Ontology-Constructor\test_results\final-2\MOSES"

# 找到所有在22点前的测试运行文件夹
test_runs = []
for folder in os.listdir(base_path):
    if folder.startswith("20250822_1") and not folder.startswith("20250822_22"):
        test_runs.append(folder)

test_runs.sort()

print("Test Run Analysis: get_information_by_source Usage")
print("=" * 60)

total_usage = {}
run_summaries = {}

for test_run in test_runs:
    print(f"\n{test_run}:")
    print("-" * 40)
    
    run_path = os.path.join(base_path, test_run)
    iteration_files = glob.glob(os.path.join(run_path, "*iteration_history.txt"))
    
    run_total = 0
    query_counts = {}
    
    for file_path in sorted(iteration_files):
        query_name = os.path.basename(file_path).replace("_iteration_history.txt", "")
        
        # 读取文件并统计get_information_by_source的使用次数
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                count = content.count("get_information_by_source")
                
                if count > 0:
                    print(f"  {query_name}: {count}")
                    query_counts[query_name] = count
                    run_total += count
                    
                    if query_name not in total_usage:
                        total_usage[query_name] = []
                    total_usage[query_name].append(count)
                    
        except Exception as e:
            print(f"  Error reading {query_name}: {e}")
    
    run_summaries[test_run] = {
        'total': run_total, 
        'query_counts': query_counts,
        'queries_with_usage': len(query_counts)
    }
    
    if run_total == 0:
        print("  No usage found")
    else:
        print(f"  Total: {run_total} usages across {len(query_counts)} queries")

print("\n" + "=" * 60)
print("SUMMARY ACROSS ALL 7 TEST RUNS")
print("=" * 60)

# 汇总统计
all_runs_total = sum(summary['total'] for summary in run_summaries.values())
queries_with_any_usage = set()
for summary in run_summaries.values():
    queries_with_any_usage.update(summary['query_counts'].keys())

print(f"Total get_information_by_source calls: {all_runs_total}")
print(f"Unique queries that used the tool: {len(queries_with_any_usage)}")

# 按测试运行统计
print(f"\nUsage by test run:")
for test_run, summary in run_summaries.items():
    print(f"  {test_run}: {summary['total']} calls, {summary['queries_with_usage']} queries")

# 按query统计
if total_usage:
    print(f"\nUsage by query (across all runs):")
    for query, counts in sorted(total_usage.items()):
        total_for_query = sum(counts)
        avg_for_query = total_for_query / len(counts)
        print(f"  {query}: {total_for_query} total ({avg_for_query:.1f} avg per run)")

print(f"\nQueries that used get_information_by_source:")
print(f"{sorted(queries_with_any_usage)}")