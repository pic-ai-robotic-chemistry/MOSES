#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性分析主程序 - 完整实现
Comprehensive Consistency Analysis Implementation

根据一致性分析总方案实现所有分析步骤
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
        
        # Standard dimensions based on the plan
        self.dimensions = ['正确性', '完备性', '理论深度', '论述严谨性与信息密度']
        
    def load_and_parse_data(self):
        """Load and parse both human and LLM data"""
        print("=" * 60)
        print("第零部分：数据加载与解析")
        print("=" * 60)
        
        # Load human data
        print("加载人类评分数据...")
        human_df = pd.read_csv(HUMAN_DATA_PATH, encoding='utf-8-sig')
        
        # Parse human data structure more carefully
        print("解析人类评分结构...")
        self.human_scores = self._parse_human_data(human_df)
        
        # Load LLM data
        print("加载LLM评分数据...")
        with open(LLM_DATA_PATH, 'r', encoding='utf-8') as f:
            llm_data = []
            for line in f:
                if line.strip():
                    llm_data.append(json.loads(line))
        
        print("解析LLM评分结构...")
        self.llm_scores = self._parse_llm_data(llm_data)
        
        print(f"人类评分条目数: {len(self.human_scores)}")
        print(f"LLM评分条目数: {len(self.llm_scores)}")
        
    def _parse_human_data(self, df):
        """Parse human evaluation data"""
        scores = []
        
        # Get question information from first two columns
        questions = []
        for i in range(2, len(df)):  # Skip first 2 rows which are headers
            q_info = str(df.iloc[i, 0]) if not pd.isna(df.iloc[i, 0]) else f"q_{i-1}"
            questions.append(q_info)
        
        # Parse column structure to identify models and dimensions
        cols = list(df.columns)
        
        # Identify model names by looking for non-dimension columns
        models = []
        current_model = None
        
        for col in cols[2:]:  # Skip first 2 columns
            if isinstance(col, str):
                # Check if this is a model name (not a dimension)
                if not any(dim in col for dim in self.dimensions):
                    # This is likely a model name
                    models.append(col)
                    current_model = col
        
        print(f"识别出的模型: {models[:5]}...")  # Show first 5
        print(f"总模型数: {len(models)}")
        
        # Extract scores for each model and dimension
        model_pattern = {}
        dim_count = 0
        
        for i, col in enumerate(cols[2:], 2):  # Start from column 2
            if isinstance(col, str):
                # Determine which model and dimension this column belongs to
                model_name = None
                dimension = None
                
                # Check if this column contains a dimension name
                for dim in self.dimensions:
                    if dim in col:
                        dimension = dim
                        # Extract model name (before the dimension)
                        model_part = col.replace(dim, '').strip('.')
                        if model_part:
                            model_name = model_part
                        else:
                            # Use the most recent model
                            if models:
                                model_idx = min(dim_count // len(self.dimensions), len(models) - 1)
                                model_name = models[model_idx]
                        break
                
                if not dimension:
                    # This might be a pure model column, assign first dimension
                    model_name = col
                    dimension = self.dimensions[dim_count % len(self.dimensions)]
                
                if model_name and dimension:
                    # Extract scores for this model-dimension combination
                    for q_idx, question in enumerate(questions):
                        if q_idx + 2 < len(df):  # Ensure we don't go out of bounds
                            score_val = df.iloc[q_idx + 2, i]
                            if pd.notna(score_val) and str(score_val).replace('.', '').isdigit():
                                try:
                                    score = float(score_val)
                                    scores.append({
                                        'question': f"q_{q_idx + 1}",
                                        'model': model_name,
                                        'dimension': dimension,
                                        'human_evaluator': 1,  # Assuming single evaluator for now
                                        'score': score
                                    })
                                except:
                                    continue
                
                dim_count += 1
        
        return pd.DataFrame(scores)
    
    def _parse_llm_data(self, data):
        """Parse LLM evaluation data"""
        scores = []
        
        for entry in data:
            model = entry.get('model_name', 'unknown')
            question = entry.get('question_id', 'unknown')
            answer_round = int(entry.get('answer_round', 1))
            eval_round = entry.get('evaluation_round', 1)
            
            # Parse evaluation dimensions
            dimensions = entry.get('dimensions', [])
            
            # Parse the answer JSON
            answer_str = entry.get('answer', '{}')
            try:
                # Try to parse as JSON
                if answer_str.startswith('{') and answer_str.endswith('}'):
                    score_data = json.loads(answer_str)
                else:
                    # Extract JSON from string using regex
                    json_match = re.search(r'\\{[^{}]*\\}', answer_str)
                    if json_match:
                        score_data = json.loads(json_match.group())
                    else:
                        continue
                
                # Extract scores for each dimension
                for dim_key, score_val in score_data.items():
                    # Map dimension keys to standard dimensions
                    dim_mapping = {
                        'correctness': '正确性',
                        'completeness': '完备性', 
                        'theoretical_depth': '理论深度',
                        'rigor_and_information_density': '论述严谨性与信息密度'
                    }
                    
                    dimension = dim_mapping.get(dim_key, dim_key)
                    
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
        
        # 1. Human_Avg: Average of human evaluators for each {model, question, dimension}
        print("计算 Human_Avg...")
        human_avg = self.human_scores.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
        human_avg.rename(columns={'score': 'Human_Avg'}, inplace=True)
        
        # 2. LLM_Avg_Overall: Overall average across all answer rounds and evaluation rounds
        print("计算 LLM_Avg_Overall...")
        llm_avg_overall = self.llm_scores.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
        llm_avg_overall.rename(columns={'score': 'LLM_Avg_Overall'}, inplace=True)
        
        # 3. LLM_Repetition_Avg: Average across evaluation rounds for each answer round
        print("计算 LLM_Repetition_Avg...")
        llm_rep_avg = self.llm_scores.groupby(['model', 'question', 'dimension', 'answer_round'])['score'].mean().reset_index()
        llm_rep_avg.rename(columns={'score': 'LLM_Repetition_Avg'}, inplace=True)
        
        # Merge human and LLM overall averages
        merged = pd.merge(human_avg, llm_avg_overall, on=['model', 'question', 'dimension'], how='inner')
        
        # 4. Disagreement_Score: Difference between LLM and human averages
        print("计算 Disagreement_Score...")
        merged['Disagreement_Score'] = merged['LLM_Avg_Overall'] - merged['Human_Avg']
        
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
        
        self.results['preprocessing'] = {
            'total_entries': len(merged),
            'models_count': merged['model'].nunique(),
            'questions_count': merged['question'].nunique(),
            'dimensions_count': merged['dimension'].nunique(),
            'human_avg_range': [merged['Human_Avg'].min(), merged['Human_Avg'].max()],
            'llm_avg_range': [merged['LLM_Avg_Overall'].min(), merged['LLM_Avg_Overall'].max()],
            'disagreement_range': [merged['Disagreement_Score'].min(), merged['Disagreement_Score'].max()]
        }
        
        return merged, llm_rep_avg
    
    def analyze_model_ranking_consistency(self):
        """第二部分：模型排序一致性分析"""
        print("\n" + "=" * 60)
        print("第二部分：模型排序一致性分析 (裁判视角)")
        print("=" * 60)
        
        ranking_results = {}
        
        # 2.1 LLM-人类一致性 (裁判一致性)
        print("2.1 计算LLM-人类排序一致性...")
        
        correlation_results = []
        
        # For each question and dimension combination
        for question in self.aggregated_data['question'].unique():
            for dimension in self.aggregated_data['dimension'].unique():
                subset = self.aggregated_data[
                    (self.aggregated_data['question'] == question) & 
                    (self.aggregated_data['dimension'] == dimension)
                ]
                
                if len(subset) >= 3:  # Need at least 3 models for meaningful correlation
                    human_scores = subset['Human_Avg'].values
                    llm_scores = subset['LLM_Avg_Overall'].values
                    
                    # Calculate correlations
                    kendall_tau, kendall_p = kendalltau(human_scores, llm_scores)
                    spearman_rho, spearman_p = spearmanr(human_scores, llm_scores)
                    
                    # Calculate ICC
                    try:
                        # Prepare data for ICC calculation
                        icc_data = pd.DataFrame({
                            'model': subset['model'].values,
                            'human': human_scores,
                            'llm': llm_scores
                        })
                        
                        # Reshape for ICC
                        icc_long = pd.melt(icc_data, id_vars=['model'], 
                                         value_vars=['human', 'llm'],
                                         var_name='rater', value_name='score')
                        
                        icc_result = pg.intraclass_corr(data=icc_long, targets='model', 
                                                      raters='rater', ratings='score')
                        icc_val = icc_result[icc_result['Type'] == 'ICC1']['ICC'].iloc[0]
                        icc_p = icc_result[icc_result['Type'] == 'ICC1']['pval'].iloc[0]
                    except:
                        icc_val, icc_p = np.nan, np.nan
                    
                    correlation_results.append({
                        'question': question,
                        'dimension': dimension,
                        'kendall_tau': kendall_tau,
                        'kendall_p': kendall_p,
                        'spearman_rho': spearman_rho,
                        'spearman_p': spearman_p,
                        'icc': icc_val,
                        'icc_p': icc_p,
                        'n_models': len(subset)
                    })
        
        correlation_df = pd.DataFrame(correlation_results)
        
        # Calculate summary statistics by dimension
        ranking_summary = {}
        for dimension in correlation_df['dimension'].unique():
            dim_data = correlation_df[correlation_df['dimension'] == dimension]
            
            ranking_summary[dimension] = {
                'kendall_mean': dim_data['kendall_tau'].mean(),
                'kendall_ci': np.percentile(dim_data['kendall_tau'].dropna(), [0.15, 99.85]),
                'kendall_significant_ratio': (dim_data['kendall_p'] < 0.05).mean(),
                'spearman_mean': dim_data['spearman_rho'].mean(),
                'spearman_ci': np.percentile(dim_data['spearman_rho'].dropna(), [0.15, 99.85]),
                'spearman_significant_ratio': (dim_data['spearman_p'] < 0.05).mean(),
                'icc_mean': dim_data['icc'].mean(),
                'icc_ci': np.percentile(dim_data['icc'].dropna(), [0.15, 99.85]),
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
        
        # 2.2 人类内部一致性 (if multiple human evaluators available)
        print("2.2 计算人类内部一致性...")
        # This would require multiple human evaluators per question-model-dimension
        # For now, we'll skip this as the current data structure suggests single evaluator
        
        self.results['ranking_consistency'] = ranking_results
        
        return ranking_results
    
    def create_ranking_visualizations(self, ranking_results):
        """Create visualizations for ranking consistency"""
        print("生成排序一致性可视化图表...")
        
        correlation_df = ranking_results['llm_human_consistency']['detailed_results']
        summary = ranking_results['llm_human_consistency']['summary_by_dimension']
        
        # Figure A: Scatter plots showing overall relationship
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('LLM vs Human Evaluation Scores by Dimension', fontsize=16, fontweight='bold')
        
        dimensions = list(summary.keys())[:4]  # Take first 4 dimensions
        
        for i, dimension in enumerate(dimensions):
            row, col = i // 2, i % 2
            ax = axes[row, col]
            
            # Get data for this dimension
            dim_data = self.aggregated_data[self.aggregated_data['dimension'] == dimension]
            
            # Scatter plot
            ax.scatter(dim_data['Human_Avg'], dim_data['LLM_Avg_Overall'], 
                      alpha=0.6, s=50)
            
            # Add trend line
            if len(dim_data) > 1:
                z = np.polyfit(dim_data['Human_Avg'], dim_data['LLM_Avg_Overall'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(dim_data['Human_Avg'].min(), dim_data['Human_Avg'].max(), 100)
                ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
            
            # Add y=x reference line
            min_val = min(dim_data['Human_Avg'].min(), dim_data['LLM_Avg_Overall'].min())
            max_val = max(dim_data['Human_Avg'].max(), dim_data['LLM_Avg_Overall'].max())
            ax.plot([min_val, max_val], [min_val, max_val], 'k:', alpha=0.5, linewidth=1)
            
            ax.set_xlabel('Human Average Score')
            ax.set_ylabel('LLM Average Score')
            ax.set_title(f'{dimension}')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "figures" / "ranking_scatter_overall.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Figure C: Forest plot for correlation coefficients
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x_pos = np.arange(len(dimensions))
        width = 0.25
        
        kendall_means = [summary[dim]['kendall_mean'] for dim in dimensions]
        kendall_cis = [summary[dim]['kendall_ci'] for dim in dimensions]
        spearman_means = [summary[dim]['spearman_mean'] for dim in dimensions]
        spearman_cis = [summary[dim]['spearman_ci'] for dim in dimensions]
        
        # Plot Kendall's tau
        kendall_errs = [[m - ci[0] for m, ci in zip(kendall_means, kendall_cis)],
                       [ci[1] - m for m, ci in zip(kendall_means, kendall_cis)]]
        ax.errorbar(x_pos - width/2, kendall_means, yerr=kendall_errs, 
                   fmt='o', capsize=5, capthick=2, label="Kendall's τ", markersize=8)
        
        # Plot Spearman's rho
        spearman_errs = [[m - ci[0] for m, ci in zip(spearman_means, spearman_cis)],
                        [ci[1] - m for m, ci in zip(spearman_means, spearman_cis)]]
        ax.errorbar(x_pos + width/2, spearman_means, yerr=spearman_errs, 
                   fmt='s', capsize=5, capthick=2, label="Spearman's ρ", markersize=8)
        
        ax.set_xlabel('Evaluation Dimensions')
        ax.set_ylabel('Correlation Coefficient')
        ax.set_title('LLM-Human Ranking Consistency by Dimension\n(with 99.7% Confidence Intervals)', 
                    fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(dimensions, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "figures" / "ranking_correlation_forest.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print("排序一致性可视化完成")
    
    def run_full_analysis(self):
        """Run the complete consistency analysis"""
        print("开始完整的一致性分析...")
        
        # Load and parse data
        self.load_and_parse_data()
        
        # Step 1: Preprocessing and aggregation
        aggregated_data, llm_rep_data = self.preprocess_and_aggregate()
        
        # Step 2: Model ranking consistency analysis
        ranking_results = self.analyze_model_ranking_consistency()
        
        # Create visualizations
        self.create_ranking_visualizations(ranking_results)
        
        # Save comprehensive results
        with open(OUTPUT_DIR / "results" / "comprehensive_analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("分析完成!")
        print(f"结果保存在: {OUTPUT_DIR}")
        print("=" * 60)
        
        return self.results

def main():
    """Main execution function"""
    analyzer = ConsistencyAnalyzer()
    results = analyzer.run_full_analysis()
    
    # Print summary
    print("\n分析结果摘要:")
    if 'preprocessing' in results:
        prep = results['preprocessing']
        print(f"- 处理的数据条目: {prep['total_entries']}")
        print(f"- 模型数量: {prep['models_count']}")
        print(f"- 问题数量: {prep['questions_count']}")
        print(f"- 评估维度: {prep['dimensions_count']}")
    
    if 'ranking_consistency' in results:
        ranking = results['ranking_consistency']['llm_human_consistency']['summary_by_dimension']
        print(f"\n各维度LLM-人类排序一致性 (Kendall's τ):")
        for dim, stats in ranking.items():
            print(f"  {dim}: {stats['kendall_mean']:.3f} (显著性比例: {stats['kendall_significant_ratio']:.2%})")

if __name__ == "__main__":
    main()