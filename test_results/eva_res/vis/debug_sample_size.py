#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析样本量和数据结构问题
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# 添加路径
current_dir = Path(__file__).parent  # vis目录
eva_res_root = current_dir.parent  # eva_res目录  
consistency_root = eva_res_root / "consistency_analysis"  # consistency_analysis目录

sys.path.append(str(current_dir))
sys.path.append(str(consistency_root))

from data_loader import ConsistencyDataLoader
from analysis_config import AnalysisConfig
from scipy.stats import pearsonr

def debug_sample_size():
    """详细调试样本量问题"""
    
    print("=== 样本量和数据结构调试 ===\n")
    
    # 创建与报告一致的配置
    config = AnalysisConfig(
        name="Debug Analysis",
        description="Debug sample size",
        dimensions=["正确性", "完备性", "理论深度", "论述严谨性与信息密度"],
        llm_strategy='average',
        output_suffix="debug",
        selected_models=[
            "gpt-4.1-final", "gpt-4.1-nano-final-815-1", 
            "lightrag-gpt-4_1", "lightrag-gpt-4_1-nano", 
            "o1-final", "o3-final", 
            "gpt-4o-final-815-1", "gpt-4o-mini-final-815-1", 
            "reordered_MOSES-final", "reordered_MOSES-nano-final"
        ]
    )
    
    # 加载数据
    data_loader = ConsistencyDataLoader(config=config)
    data_loader.load_human_scores()
    data_loader.load_llm_scores()
    
    human_scores = data_loader.processed_data['human_scores']
    llm_scores = data_loader.processed_data['llm_scores']
    
    print("1. 原始数据概况:")
    print(f"   人工评分系统数: {len(human_scores)}")
    print(f"   LLM评分系统数: {len(llm_scores)}")
    
    # 检查人工评分数据结构
    print("\n2. 人工评分详细结构:")
    total_human_subjects = 0
    
    for system_name in config.selected_models:
        if system_name in human_scores:
            system_data = human_scores[system_name]
            n_questions = len(system_data)
            
            # 统计每个维度的有效数据
            dimension_counts = {}
            for question_id, question_data in system_data.items():
                for dimension in config.dimensions:
                    if dimension in question_data:
                        scores = question_data[dimension]
                        if len(scores) >= 3:  # 有效的评分（至少3个评分者）
                            dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
            
            print(f"   {system_name}: {n_questions}个问题")
            for dim, count in dimension_counts.items():
                print(f"     {dim}: {count}个有效评分")
                total_human_subjects += count
    
    print(f"   总计人工评分subjects: {total_human_subjects}")
    print(f"   期望subjects: {len(config.selected_models)} × 27 × 4 = {len(config.selected_models) * 27 * 4}")
    
    # 检查LLM评分数据结构
    print("\n3. LLM评分详细结构:")
    llm_system_mapping = {
        "gpt-4.1-final": "gpt-4.1",
        "gpt-4.1-nano-final-815-1": "gpt-4.1-nano", 
        "lightrag-gpt-4_1": "lightrag-4.1",
        "lightrag-gpt-4_1-nano": "lightrag-4.1-nano",
        "o1-final": "o1",
        "o3-final": "o3",
        "gpt-4o-final-815-1": "gpt-4o",
        "gpt-4o-mini-final-815-1": "gpt-4o-mini",
        "reordered_MOSES-final": "MOSES",
        "reordered_MOSES-nano-final": "MOSES-nano"
    }
    
    total_llm_subjects = 0
    
    for human_sys, llm_sys in llm_system_mapping.items():
        if llm_sys in llm_scores:
            system_data = llm_scores[llm_sys]
            n_questions = len(system_data)
            
            # 统计每个维度的有效数据
            dimension_counts = {}
            for question_id, question_data in system_data.items():
                for dimension in config.dimensions:
                    if dimension in question_data:
                        scores = question_data[dimension]
                        if len(scores) >= 5:  # 有效的评分（至少5次评分）
                            dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
            
            print(f"   {llm_sys} (→{human_sys}): {n_questions}个问题")
            for dim, count in dimension_counts.items():
                print(f"     {dim}: {count}个有效评分")
                total_llm_subjects += count
    
    print(f"   总计LLM评分subjects: {total_llm_subjects}")
    
    # 分析Leave-One-Out方法的数据点数量
    print("\n4. Leave-One-Out方法数据点分析:")
    print("   人工内部一致性 (每个rater vs 其他rater平均):")
    print(f"     每个subject: 3个数据点 (3个rater)")
    print(f"     总数据点: {total_human_subjects} × 3 = {total_human_subjects * 3}")
    
    print("   LLM内部一致性 (每轮 vs 其他轮平均):")
    print(f"     每个subject: 5个数据点 (5轮评分)")
    print(f"     总数据点: {total_llm_subjects} × 5 = {total_llm_subjects * 5}")
    
    # 计算实际的相关系数来验证
    print("\n5. 验证相关系数计算:")
    
    # 人工内部一致性 - 正确性维度
    dimension = "正确性"
    rater_pairs_data = []
    
    for system_name in config.selected_models:
        if system_name in human_scores:
            system_data = human_scores[system_name]
            for question_id, question_data in system_data.items():
                if dimension in question_data:
                    scores = question_data[dimension]
                    if len(scores) >= 3:
                        # Leave-one-out: 每个rater vs 其他rater平均
                        for rater_idx in range(3):
                            others_avg = np.mean([scores[i] for i in range(3) if i != rater_idx])
                            rater_score = scores[rater_idx]
                            rater_pairs_data.append((others_avg, rater_score))
    
    if rater_pairs_data:
        x_vals = [pair[0] for pair in rater_pairs_data]
        y_vals = [pair[1] for pair in rater_pairs_data]
        
        r, p = pearsonr(x_vals, y_vals)
        print(f"   {dimension}维度人工内部一致性:")
        print(f"     数据点数: {len(rater_pairs_data)}")
        print(f"     Pearson r: {r:.6f}")
        print(f"     P值: {p:.2e}")
        print(f"     报告中的期望值: 0.6612 (配对方法的平均)")
        
        # 分析为什么我的相关系数这么高
        print(f"\n   相关系数分析:")
        print(f"     我的方法: Leave-one-out (1 vs 其他平均)")
        print(f"     报告方法: 配对比较 (1 vs 1)")
        print(f"     区别: Leave-one-out会产生更高的相关性，因为减少了噪声")
    
    # 对比报告中的配对方法
    print("\n6. 报告中配对方法的理论分析:")
    print("   报告中 '正确性' 维度的配对相关系数:")
    print("     rater_1 vs rater_2: 0.5597")
    print("     rater_1 vs rater_3: 0.7532") 
    print("     rater_2 vs rater_3: 0.6708")
    print("     平均: 0.6612")
    print(f"     我的Leave-one-out结果: {r:.4f}")
    print("   差异原因: Leave-one-out方法减少了随机噪声，产生更高相关性")

if __name__ == "__main__":
    debug_sample_size()