#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Model Evaluation Project: Consistency Analysis
一致性分析总方案的实现

This script implements the comprehensive consistency analysis plan for evaluating
the agreement between LLM and human evaluators across multiple dimensions.
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import pingouin as pg
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up paths
BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
HUMAN_DATA_PATH = BASE_DIR / "human" / "副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv"
LLM_DATA_PATH = BASE_DIR / "individual" / "安全前瞻-化学_82_doubao-seed-1.6_安全与前瞻_1755917139543_individual_evaluation_prompts_5x_18900_v1.json"
OUTPUT_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res\consistency_analysis")

# Create output directories
(OUTPUT_DIR / "results").mkdir(exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)

# Set style for visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_human_data():
    """Load and parse human evaluation data"""
    print("Loading human evaluation data...")
    
    # Read the CSV file with proper encoding
    df = pd.read_csv(HUMAN_DATA_PATH, encoding='utf-8-sig')
    
    # Print basic info about the structure
    print(f"Human data shape: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
    
    return df

def load_llm_data():
    """Load and parse LLM evaluation data"""
    print("Loading LLM evaluation data...")
    
    with open(LLM_DATA_PATH, 'r', encoding='utf-8') as f:
        data = []
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    print(f"LLM data entries: {len(data)}")
    
    # Print structure of first entry
    if data:
        first_entry = data[0]
        print("LLM data structure:")
        for key in first_entry.keys():
            print(f"  {key}: {type(first_entry[key])}")
    
    return data

def analyze_data_structure():
    """Analyze the structure of both datasets"""
    print("=" * 60)
    print("数据结构分析 (Data Structure Analysis)")
    print("=" * 60)
    
    # Load data
    human_df = load_human_data()
    llm_data = load_llm_data()
    
    # Analyze human data structure
    print("\n1. 人类评分数据结构分析:")
    print(f"   - 数据维度: {human_df.shape}")
    print(f"   - 列数: {len(human_df.columns)}")
    
    # Try to identify the structure
    if len(human_df.columns) > 50:
        print("   - 检测到多列结构，可能包含多个模型和评分维度")
        
        # Show a sample of column names to understand structure
        cols = list(human_df.columns)
        print(f"   - 前10列: {cols[:10]}")
        print(f"   - 中间10列: {cols[len(cols)//2:len(cols)//2+10]}")
    
    # Analyze LLM data structure
    print("\n2. LLM评分数据结构分析:")
    print(f"   - 数据条目数: {len(llm_data)}")
    
    if llm_data:
        sample = llm_data[0]
        if 'model_name' in sample:
            models = set(item.get('model_name', 'unknown') for item in llm_data)
            print(f"   - 模型数量: {len(models)}")
            print(f"   - 模型列表: {list(models)[:5]}...")
        
        if 'question_id' in sample:
            questions = set(item.get('question_id', 'unknown') for item in llm_data)
            print(f"   - 问题数量: {len(questions)}")
        
        if 'evaluation_round' in sample:
            rounds = set(item.get('evaluation_round', 0) for item in llm_data)
            print(f"   - 评估轮次: {sorted(rounds)}")
        
        if 'answer_round' in sample:
            answer_rounds = set(item.get('answer_round', 0) for item in llm_data)
            print(f"   - 回答轮次: {sorted(answer_rounds)}")
    
    return human_df, llm_data

def extract_human_scores(human_df):
    """Extract and organize human scores by model, question, and dimension"""
    print("\n提取人类评分数据...")
    
    # First, let's examine the column structure more carefully
    print("分析列结构...")
    columns = list(human_df.columns)
    print(f"总列数: {len(columns)}")
    
    # Look for patterns in column names
    model_columns = []
    dimension_columns = []
    
    # Common dimensions we expect
    expected_dimensions = ['正确性', '逻辑性', '清晰度', '完备性', '理论深度', '论述严谨性与信息密度']
    
    for i, col in enumerate(columns):
        if isinstance(col, str):
            # Check if this looks like a model name (contains letters, not just dimension names)
            if col not in expected_dimensions and col not in ['Unnamed: 0', 'Unnamed: 1'] and not col.startswith('Unnamed'):
                # This might be a model column
                if any(dim in col for dim in expected_dimensions):
                    # This is a dimension column with suffix
                    dimension_columns.append((i, col))
                else:
                    # This is likely a model name
                    model_columns.append((i, col))
            elif col in expected_dimensions:
                dimension_columns.append((i, col))
    
    print(f"发现潜在模型列: {len(model_columns)}")
    print(f"发现维度列: {len(dimension_columns)}")
    
    # Show some examples
    if model_columns:
        print("模型列示例:", [col for _, col in model_columns[:5]])
    if dimension_columns:
        print("维度列示例:", [col for _, col in dimension_columns[:10]])
    
    # Create a simplified mapping for now
    column_mapping = {}
    
    # Skip the first two columns (question info)
    for i in range(2, len(columns)):
        col_name = columns[i]
        if isinstance(col_name, str):
            # Try to extract model and dimension
            if any(dim in col_name for dim in expected_dimensions):
                # This is a dimension column
                for dim in expected_dimensions:
                    if dim in col_name:
                        # Extract model name (everything before the dimension)
                        model_part = col_name.replace(dim, '').strip('.')
                        if not model_part:
                            model_part = "unknown"
                        column_mapping[i] = (model_part, dim)
                        break
            else:
                # This might be a model name column, assume first dimension
                column_mapping[i] = (col_name, expected_dimensions[0])
    
    # Extract unique models and dimensions
    unique_models = set()
    unique_dimensions = set()
    for model, dim in column_mapping.values():
        unique_models.add(model)
        unique_dimensions.add(dim)
    
    print(f"提取的模型数: {len(unique_models)}")
    print(f"提取的维度数: {len(unique_dimensions)}")
    print(f"模型: {sorted(list(unique_models))[:5]}...")
    print(f"维度: {sorted(list(unique_dimensions))}")
    
    return column_mapping, human_df

def extract_llm_scores(llm_data):
    """Extract and organize LLM scores"""
    print("\n提取LLM评分数据...")
    
    # Organize LLM data
    llm_scores = {}
    
    for entry in llm_data:
        model = entry.get('model_name', 'unknown')
        question = entry.get('question_id', 'unknown')
        answer_round = entry.get('answer_round', 1)
        eval_round = entry.get('evaluation_round', 1)
        
        # Parse the answer JSON
        answer_str = entry.get('answer', '{}')
        try:
            if answer_str.startswith('{') and answer_str.endswith('}'):
                scores = json.loads(answer_str)
            else:
                # Try to extract JSON from the string
                import re
                json_match = re.search(r'\{[^{}]*\}', answer_str)
                if json_match:
                    scores = json.loads(json_match.group())
                else:
                    continue
        except:
            continue
        
        # Store scores
        for dimension, score_list in scores.items():
            if isinstance(score_list, list) and score_list:
                score = score_list[0] if len(score_list) == 1 else score_list
                
                key = (model, question, dimension, answer_round, eval_round)
                llm_scores[key] = score
    
    print(f"提取了 {len(llm_scores)} 个LLM评分条目")
    
    return llm_scores

def main():
    """Main analysis function"""
    print("开始一致性分析...")
    
    # Step 0: Analyze data structure
    human_df, llm_data = analyze_data_structure()
    
    # Step 1: Extract scores
    human_column_mapping, human_df_clean = extract_human_scores(human_df)
    llm_scores = extract_llm_scores(llm_data)
    
    print("\n数据提取完成!")
    print(f"人类评分列映射: {len(human_column_mapping)} 列")
    print(f"LLM评分条目: {len(llm_scores)} 个")
    
    # Save preliminary results
    results = {
        'human_column_mapping': {str(k): v for k, v in human_column_mapping.items()},
        'llm_scores_count': len(llm_scores),
        'status': 'data_extracted'
    }
    
    with open(OUTPUT_DIR / "results" / "data_extraction_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n初步结果已保存到: {OUTPUT_DIR / 'results' / 'data_extraction_results.json'}")

if __name__ == "__main__":
    main()