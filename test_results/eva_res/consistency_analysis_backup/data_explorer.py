#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据结构探查工具
用于理解人类评分数据的真实结构
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
HUMAN_DATA_PATH = BASE_DIR / "human" / "副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv"

def explore_human_data_structure():
    """深度探查人类评分数据结构"""
    print("=" * 60)
    print("人类评分数据结构深度分析")
    print("=" * 60)
    
    # Load raw data
    df = pd.read_csv(HUMAN_DATA_PATH, encoding='utf-8-sig')
    print(f"数据形状: {df.shape}")
    
    # Show first few rows and columns
    print("\n前5行, 前10列:")
    print(df.iloc[:5, :10])
    
    print("\n所有列名:")
    for i, col in enumerate(df.columns):
        print(f"  {i:2d}: {col}")
    
    # Look at specific rows that might contain headers
    print("\n第1行 (可能的模型名):")
    print(df.iloc[0].fillna('').tolist()[:10])
    
    print("\n第2行:")
    print(df.iloc[1].fillna('').tolist()[:10])
    
    print("\n第3行 (第一个问题):")
    print(df.iloc[2].fillna('').tolist()[:10])
    
    # Check for patterns in the data
    print("\n检查数值列:")
    numeric_cols = []
    for col in df.columns:
        try:
            # Try to convert column to numeric (excluding first 2 rows which might be headers)
            numeric_data = pd.to_numeric(df.iloc[2:][col], errors='coerce')
            if not numeric_data.isna().all():
                numeric_cols.append(col)
        except:
            pass
    
    print(f"发现 {len(numeric_cols)} 个可能包含评分的列")
    print("数值列示例:", numeric_cols[:10])
    
    # Try to identify the structure
    print("\n尝试识别结构模式...")
    
    # Look for repeating patterns in column names
    dimensions = ['正确性', '逻辑性', '清晰度', '完备性', '理论深度', '论述严谨性与信息密度']
    
    pattern_info = {}
    for i, col in enumerate(df.columns):
        if isinstance(col, str):
            for dim in dimensions:
                if dim in col:
                    if dim not in pattern_info:
                        pattern_info[dim] = []
                    pattern_info[dim].append((i, col))
    
    print("维度出现模式:")
    for dim, occurrences in pattern_info.items():
        print(f"  {dim}: {len(occurrences)} 次")
        for i, (col_idx, col_name) in enumerate(occurrences[:3]):  # Show first 3
            print(f"    列{col_idx}: {col_name}")
        if len(occurrences) > 3:
            print(f"    ... 还有 {len(occurrences) - 3} 个")
    
    # Try to extract a sample evaluation matrix
    print("\n尝试提取样本评分矩阵...")
    
    # Look for the first occurrence of each dimension
    first_dim_cols = {}
    for dim in dimensions:
        if dim in pattern_info:
            first_dim_cols[dim] = pattern_info[dim][0][0]  # Column index
    
    if first_dim_cols:
        print("第一组维度列索引:", first_dim_cols)
        
        # Extract scores for first few questions
        sample_data = []
        for q_idx in range(2, min(7, len(df))):  # Questions 1-5
            row_data = {'question': f"q_{q_idx-1}"}
            for dim, col_idx in first_dim_cols.items():
                try:
                    score = df.iloc[q_idx, col_idx]
                    if pd.notna(score):
                        row_data[dim] = score
                except:
                    pass
            sample_data.append(row_data)
        
        sample_df = pd.DataFrame(sample_data)
        print("\n样本评分数据:")
        print(sample_df)
    
    return df

def explore_llm_data_structure():
    """探查LLM数据结构"""
    print("\n" + "=" * 60)
    print("LLM评分数据结构分析")
    print("=" * 60)
    
    import json
    
    LLM_DATA_PATH = BASE_DIR / "individual" / "安全前瞻-化学_82_doubao-seed-1.6_安全与前瞻_1755917139543_individual_evaluation_prompts_5x_18900_v1.json"
    
    # Load first few entries
    entries = []
    with open(LLM_DATA_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:  # Just first 5 entries
                break
            if line.strip():
                entries.append(json.loads(line))
    
    print(f"加载了 {len(entries)} 个样本条目")
    
    if entries:
        entry = entries[0]
        print("\n第一个条目的键:")
        for key, value in entry.items():
            print(f"  {key}: {type(value)} - {str(value)[:100]}...")
        
        # Check the answer field structure
        print("\n回答字段分析:")
        for i, entry in enumerate(entries):
            answer = entry.get('answer', '')
            print(f"  条目 {i+1}: {answer[:150]}...")
        
        # Try to parse answer format
        print("\n尝试解析回答格式:")
        for i, entry in enumerate(entries):
            try:
                answer_str = entry.get('answer', '{}')
                if answer_str.startswith('{') and answer_str.endswith('}'):
                    parsed = json.loads(answer_str)
                    print(f"  条目 {i+1} 解析成功: {parsed}")
                else:
                    print(f"  条目 {i+1} 非标准JSON格式")
            except Exception as e:
                print(f"  条目 {i+1} 解析失败: {e}")
        
        # Check model and question distribution
        models = set()
        questions = set()
        dimensions_found = set()
        
        with open(LLM_DATA_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    models.add(entry.get('model_name', 'unknown'))
                    questions.add(entry.get('question_id', 'unknown'))
                    
                    # Check dimensions in the 'dimensions' field
                    dims = entry.get('dimensions', [])
                    if isinstance(dims, list):
                        dimensions_found.update(dims)
        
        print(f"\n总体统计:")
        print(f"  模型数量: {len(models)}")
        print(f"  问题数量: {len(questions)}")
        print(f"  发现的维度: {sorted(dimensions_found)}")
        print(f"  模型列表: {sorted(list(models))[:10]}...")

def main():
    """主探查函数"""
    human_df = explore_human_data_structure()
    explore_llm_data_structure()
    
    # Save the DataFrame for further inspection
    OUTPUT_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res\consistency_analysis")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Save a subset for manual inspection
    human_df.iloc[:10, :20].to_csv(OUTPUT_DIR / "human_data_sample.csv", 
                                  index=False, encoding='utf-8-sig')
    
    print(f"\n样本数据已保存到: {OUTPUT_DIR / 'human_data_sample.csv'}")

if __name__ == "__main__":
    main()