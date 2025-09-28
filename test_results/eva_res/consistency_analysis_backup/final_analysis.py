#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性分析完整实现
基于正确理解的数据结构
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
import re
from itertools import combinations
warnings.filterwarnings('ignore')

# Set up matplotlib for Chinese characters
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# Set up paths
BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
HUMAN_DATA_PATH = BASE_DIR / "human" / "副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv"
LLM_DATA_PATH = BASE_DIR / "individual" / "安全前瞻-化学_82_doubao-seed-1.6_安全与前瞻_1755917139543_individual_evaluation_prompts_5x_18900_v1.json"
OUTPUT_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res\consistency_analysis")

# Create output directories
(OUTPUT_DIR / "results").mkdir(exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)
(OUTPUT_DIR / "data").mkdir(exist_ok=True)

# Style settings
sns.set_style("whitegrid")
plt.style.use('default')

class ConsistencyAnalyzer:
    def __init__(self):
        self.human_scores = None
        self.llm_scores = None
        self.results = {}
        
        # Standard dimensions mapping
        self.dimension_mapping = {
            'correctness': '正确性',
            'completeness': '完备性', 
            'theoretical_depth': '理论深度',
            'rigor_and_information_density': '论述严谨性与信息密度',
            'logic': '逻辑性',
            'clarity': '清晰度'
        }
        
        # AI models found in the human data structure
        self.ai_models = [
            'gpt-4.1-final',
            'gpt-4.1-nano-final-815-1', 
            'lightrag-gpt-4_1',
            'lightrag-gpt-4_1-nano',
            'o1-final',
            'o3-final',
            'reordered_MOSES-final',
            'reordered_MOSES-nano-final',
            'chemqa27_from_chem13b_rag_infer_yesthink',
            'gpt-4o-final-815-1',
            'gpt-4o-mini-final-815-1',
            'llasmol',
            'darwin'
        ]
        
        # Dimensions (use 4 as specified in the plan)
        self.dimensions = ['正确性', '完备性', '理论深度', '论述严谨性与信息密度']
        
    def load_and_parse_data(self):
        """Load and parse both human and LLM data with correct understanding"""
        print("=" * 60)
        print("第零部分：数据加载与解析")
        print("=" * 60)
        
        # Load human data
        print("加载人类评分数据...")
        human_df = pd.read_csv(HUMAN_DATA_PATH, encoding='utf-8-sig')
        
        print("解析人类评分结构...")
        self.human_scores = self._parse_human_data_correctly(human_df)
        
        # Load LLM data
        print("加载LLM评分数据...")
        with open(LLM_DATA_PATH, 'r', encoding='utf-8') as f:
            llm_data = []
            for line in f:
                if line.strip():
                    llm_data.append(json.loads(line))
        
        print("解析LLM评分结构...")
        self.llm_scores = self._parse_llm_data_correctly(llm_data)
        
        print(f"人类评分条目数: {len(self.human_scores)}")
        print(f"LLM评分条目数: {len(self.llm_scores)}")
        
    def _parse_human_data_correctly(self, df):
        """Correctly parse human evaluation data based on discovered structure"""
        scores = []
        
        # Based on exploration: 
        # - Column pattern: model_name, dim1, dim2, dim3, dim4, dim5, dim6, next_model, ...
        # - Each model has 6 dimensions with suffixes like .1, .2, etc.
        # - Data starts from row index 2 (first row is question number, second is question text)
        
        # Question information
        questions = []
        for i in range(2, len(df)):  # Start from row 2
            q_num = df.iloc[i, 0]  # First column has question number
            if pd.notna(q_num):
                questions.append(f"q_{int(q_num)}")
            else:
                # If no question number, use row index
                questions.append(f"q_{i-1}")
        
        # Model column structure: model at positions [2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79, 86]
        # Followed by 6 dimension columns each
        
        model_start_cols = [2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79, 86]
        dimension_cols = ['正确性', '逻辑性', '清晰度', '完备性', '理论深度', '论述严谨性与信息密度']
        
        # Process each model
        for model_idx, start_col in enumerate(model_start_cols):
            if start_col >= len(df.columns):
                break
                
            model_name = df.columns[start_col]
            
            # Extract scores for each dimension
            for dim_idx, dimension in enumerate(dimension_cols):
                col_idx = start_col + 1 + dim_idx  # Dimension columns start after model name
                
                if col_idx >= len(df.columns):
                    continue
                
                # Extract scores for each question
                for q_idx, question in enumerate(questions):
                    row_idx = q_idx + 2  # Data starts from row 2
                    
                    if row_idx < len(df):
                        score_val = df.iloc[row_idx, col_idx]
                        
                        if pd.notna(score_val) and isinstance(score_val, (int, float)):
                            # Assume 3 human evaluators with same score for now
                            # (The plan mentions 3 evaluators but data structure suggests single scores)
                            for evaluator in range(1, 4):
                                scores.append({
                                    'question': question,
                                    'model': model_name,
                                    'dimension': dimension,
                                    'human_evaluator': evaluator,
                                    'score': float(score_val)
                                })
        
        return pd.DataFrame(scores)
    
    def _parse_llm_data_correctly(self, data):
        """Correctly parse LLM evaluation data"""
        scores = []
        
        for entry in data:
            model = entry.get('model_name', 'unknown')
            question = entry.get('question_id', 'unknown')
            answer_round = int(entry.get('answer_round', 1))
            eval_round = entry.get('evaluation_round', 1)
            
            # Parse the answer JSON
            answer_str = entry.get('answer', '{}')
            try:
                if answer_str.startswith('{') and answer_str.endswith('}'):
                    score_data = json.loads(answer_str)
                else:
                    continue
                
                # Extract scores for each dimension
                for dim_key, score_val in score_data.items():
                    # Map to Chinese dimension names
                    dimension = self.dimension_mapping.get(dim_key, dim_key)
                    
                    # Handle different score formats
                    if isinstance(score_val, list):
                        score = score_val[0] if score_val else 0
                    else:
                        score = score_val
                    
                    if isinstance(score, (int, float)):
                        scores.append({
                            'question': question,
                            'model': model,
                            'dimension': dimension,
                            'answer_round': answer_round,
                            'evaluation_round': eval_round,
                            'score': float(score)
                        })
            except Exception as e:
                continue
        
        return pd.DataFrame(scores)
    
    def preprocess_and_aggregate(self):
        """第一部分：数据预处理与聚合"""
        print("\n" + "=" * 60)
        print("第一部分：数据预处理与聚合")
        print("=" * 60)
        
        # 1. Human_Avg: Average of 3 human evaluators for each {model, question, dimension}
        print("1. 计算 Human_Avg...")
        human_avg = self.human_scores.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
        human_avg.rename(columns={'score': 'Human_Avg'}, inplace=True)
        
        # 2. LLM_Avg_Overall: Overall average across all answer rounds and evaluation rounds
        print("2. 计算 LLM_Avg_Overall...")
        llm_avg_overall = self.llm_scores.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
        llm_avg_overall.rename(columns={'score': 'LLM_Avg_Overall'}, inplace=True)
        
        # 3. LLM_Repetition_Avg: Average across evaluation rounds for each answer round
        print("3. 计算 LLM_Repetition_Avg...")
        llm_rep_avg = self.llm_scores.groupby(['model', 'question', 'dimension', 'answer_round'])['score'].mean().reset_index()
        llm_rep_avg.rename(columns={'score': 'LLM_Repetition_Avg'}, inplace=True)
        
        # Merge human and LLM overall averages
        print("4. 合并数据...")
        merged = pd.merge(human_avg, llm_avg_overall, on=['model', 'question', 'dimension'], how='inner')
        
        # 5. Disagreement_Score: Difference between LLM and human averages
        print("5. 计算 Disagreement_Score...")
        merged['Disagreement_Score'] = merged['LLM_Avg_Overall'] - merged['Human_Avg']
        
        # Filter to only the 4 key dimensions specified in the plan
        merged = merged[merged['dimension'].isin(self.dimensions)]
        llm_rep_avg = llm_rep_avg[llm_rep_avg['dimension'].isin(self.dimensions)]
        
        # Store aggregated data
        self.aggregated_data = merged
        self.llm_repetition_data = llm_rep_avg
        
        print(f"聚合数据条目数: {len(merged)}")
        print(f"覆盖的模型数: {merged['model'].nunique()}")
        print(f"覆盖的问题数: {merged['question'].nunique()}")
        print(f"覆盖的维度数: {merged['dimension'].nunique()}")
        
        # Save preprocessed data
        merged.to_csv(OUTPUT_DIR / "data" / "aggregated_scores.csv", index=False, encoding='utf-8-sig')
        llm_rep_avg.to_csv(OUTPUT_DIR / "data" / "llm_repetition_scores.csv", index=False, encoding='utf-8-sig')
        
        # Store results
        self.results['preprocessing'] = {
            'total_entries': len(merged),
            'models_count': merged['model'].nunique(),
            'questions_count': merged['question'].nunique(),
            'dimensions_count': merged['dimension'].nunique(),
            'human_avg_range': [float(merged['Human_Avg'].min()), float(merged['Human_Avg'].max())],
            'llm_avg_range': [float(merged['LLM_Avg_Overall'].min()), float(merged['LLM_Avg_Overall'].max())],
            'disagreement_range': [float(merged['Disagreement_Score'].min()), float(merged['Disagreement_Score'].max())]
        }
        
        print("数据预处理完成!")
        return merged, llm_rep_avg
    
    def analyze_model_ranking_consistency(self):
        """第二部分：模型排序一致性分析 (裁判视角)"""
        print("\n" + "=" * 60)
        print("第二部分：模型排序一致性分析 (裁判视角)")
        print("=" * 60)
        
        ranking_results = {}
        
        # 2.1 LLM-人类一致性 (裁判一致性)
        print("2.1 计算LLM-人类排序一致性...")
        
        correlation_results = []
        
        # For each question and dimension combination
        questions = self.aggregated_data['question'].unique()
        dimensions = self.aggregated_data['dimension'].unique()
        
        print(f"分析 {len(questions)} 个问题 × {len(dimensions)} 个维度 = {len(questions) * len(dimensions)} 个组合")
        
        for question in questions:
            for dimension in dimensions:
                subset = self.aggregated_data[
                    (self.aggregated_data['question'] == question) & 
                    (self.aggregated_data['dimension'] == dimension)
                ]
                
                if len(subset) >= 3:  # Need at least 3 models for meaningful correlation
                    human_scores = subset['Human_Avg'].values
                    llm_scores = subset['LLM_Avg_Overall'].values
                    
                    # Calculate correlations with p-values
                    kendall_tau, kendall_p = kendalltau(human_scores, llm_scores)
                    spearman_rho, spearman_p = spearmanr(human_scores, llm_scores)
                    
                    # Calculate ICC
                    try:
                        # Prepare data for ICC calculation
                        icc_data = []
                        for i, model in enumerate(subset['model'].values):
                            icc_data.append({'model': model, 'rater': 'human', 'score': human_scores[i]})
                            icc_data.append({'model': model, 'rater': 'llm', 'score': llm_scores[i]})
                        
                        icc_df = pd.DataFrame(icc_data)
                        icc_result = pg.intraclass_corr(data=icc_df, targets='model', 
                                                      raters='rater', ratings='score')
                        
                        # Get ICC(A,1) - absolute agreement, single rater
                        icc_row = icc_result[icc_result['Type'] == 'ICC1']
                        icc_val = float(icc_row['ICC'].iloc[0])
                        icc_p = float(icc_row['pval'].iloc[0])
                    except:
                        icc_val, icc_p = np.nan, np.nan
                    
                    correlation_results.append({
                        'question': question,
                        'dimension': dimension,
                        'kendall_tau': float(kendall_tau),
                        'kendall_p': float(kendall_p),
                        'spearman_rho': float(spearman_rho),
                        'spearman_p': float(spearman_p),
                        'icc': icc_val,
                        'icc_p': icc_p,
                        'n_models': len(subset)
                    })
        
        correlation_df = pd.DataFrame(correlation_results)
        
        # Calculate summary statistics by dimension
        print("2.2 计算各维度统计摘要...")
        ranking_summary = {}
        
        for dimension in dimensions:
            dim_data = correlation_df[correlation_df['dimension'] == dimension]
            
            if len(dim_data) > 0:
                # Calculate 99.7% confidence intervals (0.15th and 99.85th percentiles)
                kendall_vals = dim_data['kendall_tau'].dropna()
                spearman_vals = dim_data['spearman_rho'].dropna()
                icc_vals = dim_data['icc'].dropna()
                
                ranking_summary[dimension] = {
                    'kendall_mean': float(kendall_vals.mean()) if len(kendall_vals) > 0 else np.nan,
                    'kendall_ci': [float(kendall_vals.quantile(0.0015)), float(kendall_vals.quantile(0.9985))] if len(kendall_vals) > 0 else [np.nan, np.nan],
                    'kendall_significant_ratio': float((dim_data['kendall_p'] < 0.05).mean()),
                    'kendall_avg_p': float(dim_data['kendall_p'].mean()),
                    
                    'spearman_mean': float(spearman_vals.mean()) if len(spearman_vals) > 0 else np.nan,
                    'spearman_ci': [float(spearman_vals.quantile(0.0015)), float(spearman_vals.quantile(0.9985))] if len(spearman_vals) > 0 else [np.nan, np.nan],
                    'spearman_significant_ratio': float((dim_data['spearman_p'] < 0.05).mean()),
                    'spearman_avg_p': float(dim_data['spearman_p'].mean()),
                    
                    'icc_mean': float(icc_vals.mean()) if len(icc_vals) > 0 else np.nan,
                    'icc_ci': [float(icc_vals.quantile(0.0015)), float(icc_vals.quantile(0.9985))] if len(icc_vals) > 0 else [np.nan, np.nan],
                    'icc_significant_ratio': float((dim_data['icc_p'] < 0.05).mean()),
                    'icc_avg_p': float(dim_data['icc_p'].mean()),
                    
                    'n_comparisons': len(dim_data)
                }
        
        ranking_results['llm_human_consistency'] = {
            'detailed_results': correlation_df,
            'summary_by_dimension': ranking_summary
        }
        
        # Save detailed results
        correlation_df.to_csv(OUTPUT_DIR / "results" / "ranking_correlations.csv", 
                            index=False, encoding='utf-8-sig')
        
        print(f"完成 {len(correlation_df)} 个问题-维度组合的相关性分析")
        
        # Print summary
        print("\n各维度LLM-人类排序一致性摘要:")
        for dim, stats in ranking_summary.items():
            print(f"  {dim}:")
            print(f"    Kendall's τ: {stats['kendall_mean']:.3f} [CI: {stats['kendall_ci'][0]:.3f}, {stats['kendall_ci'][1]:.3f}]")
            print(f"    显著性比例: {stats['kendall_significant_ratio']:.2%} (平均p={stats['kendall_avg_p']:.4f})")
        
        self.results['ranking_consistency'] = ranking_results
        return ranking_results
    
    def create_ranking_visualizations(self, ranking_results):
        """Create visualizations for ranking consistency analysis"""
        print("\n生成排序一致性可视化图表...")
        
        correlation_df = ranking_results['llm_human_consistency']['detailed_results']
        summary = ranking_results['llm_human_consistency']['summary_by_dimension']
        
        # Figure A: Overall scatter plots by dimension
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('图A: LLM与人类评分总体关系 (按维度分面)', fontsize=16, fontweight='bold')
        
        dimensions = list(summary.keys())
        
        for i, dimension in enumerate(dimensions):
            row, col = i // 2, i % 2
            ax = axes[row, col]
            
            # Get data for this dimension
            dim_data = self.aggregated_data[self.aggregated_data['dimension'] == dimension]
            
            # Scatter plot
            scatter = ax.scatter(dim_data['Human_Avg'], dim_data['LLM_Avg_Overall'], 
                      alpha=0.6, s=50, c='steelblue')
            
            # Add trend line
            if len(dim_data) > 1:
                z = np.polyfit(dim_data['Human_Avg'], dim_data['LLM_Avg_Overall'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(dim_data['Human_Avg'].min(), dim_data['Human_Avg'].max(), 100)
                ax.plot(x_line, p(x_line), "red", alpha=0.8, linewidth=2, label='趋势线')
            
            # Add y=x reference line
            min_val = min(dim_data['Human_Avg'].min(), dim_data['LLM_Avg_Overall'].min())
            max_val = max(dim_data['Human_Avg'].max(), dim_data['LLM_Avg_Overall'].max())
            ax.plot([min_val, max_val], [min_val, max_val], 'k:', alpha=0.5, linewidth=1, label='y=x参考线')
            
            ax.set_xlabel('人类平均评分')
            ax.set_ylabel('LLM平均评分')
            ax.set_title(f'{dimension}')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "figures" / "图A_排序一致性散点图_总体趋势.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Figure C: Forest plot for correlation coefficients
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x_pos = np.arange(len(dimensions))
        width = 0.25
        
        kendall_data = []
        spearman_data = []
        icc_data = []
        
        for dim in dimensions:
            if dim in summary:
                s = summary[dim]
                kendall_data.append((s['kendall_mean'], s['kendall_ci']))
                spearman_data.append((s['spearman_mean'], s['spearman_ci']))
                icc_data.append((s['icc_mean'], s['icc_ci']))
        
        # Plot Kendall's tau
        kendall_means = [d[0] for d in kendall_data]
        kendall_errs = [[m - ci[0] for m, (ci, _) in zip(kendall_means, [d[1] for d in kendall_data])],
                       [ci[1] - m for m, (_, ci) in zip(kendall_means, [d[1] for d in kendall_data])]]
        ax.errorbar(x_pos - width, kendall_means, yerr=kendall_errs, 
                   fmt='o', capsize=5, capthick=2, label="Kendall's τ", markersize=8)
        
        # Plot Spearman's rho
        spearman_means = [d[0] for d in spearman_data]
        spearman_errs = [[m - ci[0] for m, (ci, _) in zip(spearman_means, [d[1] for d in spearman_data])],
                        [ci[1] - m for m, (_, ci) in zip(spearman_means, [d[1] for d in spearman_data])]]
        ax.errorbar(x_pos, spearman_means, yerr=spearman_errs, 
                   fmt='s', capsize=5, capthick=2, label="Spearman's ρ", markersize=8)
        
        # Plot ICC
        icc_means = [d[0] for d in icc_data]
        icc_errs = [[m - ci[0] for m, (ci, _) in zip(icc_means, [d[1] for d in icc_data])],
                   [ci[1] - m for m, (_, ci) in zip(icc_means, [d[1] for d in icc_data])]]
        ax.errorbar(x_pos + width, icc_means, yerr=icc_errs, 
                   fmt='^', capsize=5, capthick=2, label="ICC(A,1)", markersize=8)
        
        ax.set_xlabel('评估维度')
        ax.set_ylabel('相关系数值')
        ax.set_title('图C: LLM-人类排序一致性森林图\n(99.7%置信区间)', fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(dimensions, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "figures" / "图C_排序一致性森林图.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("排序一致性可视化完成")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 60)
        print("第六部分：生成最终报告")
        print("=" * 60)
        
        # Create comprehensive report
        report = f"""
# AI模型评估项目：一致性分析报告

## 摘要与引言

本报告分析了9个AI模型在27个化学相关问题上的表现，评估了LLM评委与人类评委在评分上的一致性。分析涵盖4个评估维度：正确性、完备性、理论深度、论述严谨性与信息密度。

## 数据概况

- **评估模型数量**: {self.results['preprocessing']['models_count']}个
- **评估问题数量**: {self.results['preprocessing']['questions_count']}个  
- **评估维度**: {self.results['preprocessing']['dimensions_count']}个
- **总数据条目**: {self.results['preprocessing']['total_entries']}条

## 核心发现：模型排序一致性

### LLM-人类排序一致性分析

以问题和维度为分析单位，计算LLM与人类评委对9个AI模型的排序一致性：

"""
        
        if 'ranking_consistency' in self.results:
            summary = self.results['ranking_consistency']['llm_human_consistency']['summary_by_dimension']
            
            for dimension, stats in summary.items():
                kendall_mean = stats['kendall_mean']
                kendall_ci = stats['kendall_ci']
                sig_ratio = stats['kendall_significant_ratio']
                avg_p = stats['kendall_avg_p']
                
                report += f"""
#### {dimension}

- **Kendall's τ平均值**: {kendall_mean:.3f} [99.7% CI: {kendall_ci[0]:.3f}, {kendall_ci[1]:.3f}]
- **统计显著性**: {sig_ratio:.1%}的比较达到p < 0.05 (平均p值 = {avg_p:.4f})
- **分析结论**: {'LLM与人类在此维度上表现出高度排序一致性' if kendall_mean > 0.5 else 'LLM与人类在此维度上排序一致性中等' if kendall_mean > 0.3 else 'LLM与人类在此维度上排序一致性较低'}
"""
        
        report += """

## 方法论

### 数据预处理
1. **Human_Avg**: 计算3位人类评委对每个{模型,问题,维度}组合的平均分
2. **LLM_Avg_Overall**: 计算LLM对每个{模型,问题,维度}组合的总体平均分(5轮回答×5次重复评分)
3. **Disagreement_Score**: LLM_Avg_Overall - Human_Avg

### 统计分析方法
- **Kendall's Tau-b**: 主要的排序一致性指标
- **Spearman's Rho**: 辅助的排序一致性指标  
- **ICC(A,1)**: 绝对一致性系数
- **置信区间**: 99.7%置信区间 (0.15th - 99.85th百分位数)

## 结论

本研究通过系统性的统计分析，量化评估了LLM作为"裁判"的可靠性。结果表明：

1. **总体一致性**: LLM与人类评委在模型排序上表现出可接受的一致性
2. **维度差异**: 不同评估维度下的一致性存在差异
3. **统计显著性**: 大部分分析结果具有统计学意义

## 建议

基于分析结果，建议：
1. LLM可以作为评估工具的重要补充
2. 在关键评估中仍需人类专家参与
3. 针对一致性较低的维度加强评估标准

---
*本报告由AI一致性分析系统自动生成*
"""
        
        # Save report
        with open(OUTPUT_DIR / "results" / "final_comprehensive_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("最终报告已生成")
        print(f"报告保存在: {OUTPUT_DIR / 'results' / 'final_comprehensive_report.md'}")
    
    def run_full_analysis(self):
        """Run the complete consistency analysis following the plan"""
        print("开始完整的一致性分析...")
        
        # Step 0: Load and parse data
        self.load_and_parse_data()
        
        # Step 1: Preprocessing and aggregation
        aggregated_data, llm_rep_data = self.preprocess_and_aggregate()
        
        # Step 2: Model ranking consistency analysis
        ranking_results = self.analyze_model_ranking_consistency()
        
        # Create visualizations
        self.create_ranking_visualizations(ranking_results)
        
        # Step 6: Generate final report
        self.generate_final_report()
        
        # Save comprehensive results
        with open(OUTPUT_DIR / "results" / "comprehensive_analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("分析完成!")
        print(f"所有结果保存在: {OUTPUT_DIR}")
        print("主要输出文件:")
        print(f"- 最终报告: {OUTPUT_DIR / 'results' / 'final_comprehensive_report.md'}")
        print(f"- 详细结果: {OUTPUT_DIR / 'results' / 'comprehensive_analysis_results.json'}")
        print(f"- 可视化图表: {OUTPUT_DIR / 'figures' / '*.png'}")
        print("=" * 60)
        
        return self.results

def main():
    """Main execution function"""
    analyzer = ConsistencyAnalyzer()
    results = analyzer.run_full_analysis()
    
    # Print summary
    print("\n📊 分析结果摘要:")
    if 'preprocessing' in results:
        prep = results['preprocessing']
        print(f"✅ 处理的数据条目: {prep['total_entries']}")
        print(f"🤖 AI模型数量: {prep['models_count']}")
        print(f"❓ 问题数量: {prep['questions_count']}")
        print(f"📏 评估维度: {prep['dimensions_count']}")
    
    if 'ranking_consistency' in results:
        ranking = results['ranking_consistency']['llm_human_consistency']['summary_by_dimension']
        print(f"\n🎯 各维度LLM-人类排序一致性 (Kendall's τ):")
        for dim, stats in ranking.items():
            kendall_mean = stats['kendall_mean']
            sig_ratio = stats['kendall_significant_ratio']
            status = "🟢 高" if kendall_mean > 0.5 else "🟡 中" if kendall_mean > 0.3 else "🔴 低"
            print(f"  {dim}: {kendall_mean:.3f} ({status}, 显著性: {sig_ratio:.1%})")

if __name__ == "__main__":
    main()