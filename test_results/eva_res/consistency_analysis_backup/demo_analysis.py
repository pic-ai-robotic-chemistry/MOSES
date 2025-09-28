#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性分析简化版本 - 重点实现核心功能
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

# Set up matplotlib for Chinese characters
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Set up paths
BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
OUTPUT_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res\consistency_analysis")

# Create output directories
(OUTPUT_DIR / "results").mkdir(exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)
(OUTPUT_DIR / "data").mkdir(exist_ok=True)

def load_sample_data():
    """Load and create sample data to demonstrate the analysis framework"""
    print("=" * 60)
    print("创建演示数据以展示分析框架")
    print("=" * 60)
    
    # Create sample data structure based on the plan
    np.random.seed(42)
    
    # Sample configuration
    models = ['gpt-4.1', 'gpt-4o', 'o1', 'lightrag', 'MOSES', 'llasmol', 'darwin', 'gpt-4o-mini', 'chem13b']
    questions = [f'q_{i}' for i in range(1, 28)]  # 27 questions
    dimensions = ['正确性', '完备性', '理论深度', '论述严谨性与信息密度']  # 4 dimensions as per plan
    
    # Generate sample human scores (3 evaluators per model-question-dimension)
    human_data = []
    for model in models:
        for question in questions:
            for dimension in dimensions:
                # Generate scores for 3 human evaluators with some correlation
                base_score = np.random.uniform(3, 9)
                for evaluator in range(1, 4):
                    score = max(1, min(10, base_score + np.random.normal(0, 1)))
                    human_data.append({
                        'model': model,
                        'question': question, 
                        'dimension': dimension,
                        'human_evaluator': evaluator,
                        'score': round(score, 1)
                    })
    
    human_df = pd.DataFrame(human_data)
    
    # Generate sample LLM scores (5 answer rounds × 5 evaluation rounds)
    llm_data = []
    for model in models:
        for question in questions:
            for dimension in dimensions:
                # Generate base score correlated with human score
                human_avg = human_df[(human_df['model'] == model) & 
                                   (human_df['question'] == question) & 
                                   (human_df['dimension'] == dimension)]['score'].mean()
                
                for answer_round in range(1, 6):
                    for eval_round in range(1, 6):
                        # LLM score with some correlation to human score + noise
                        llm_score = human_avg + np.random.normal(0, 1.5)
                        llm_score = max(1, min(10, llm_score))
                        
                        llm_data.append({
                            'model': model,
                            'question': question,
                            'dimension': dimension,
                            'answer_round': answer_round,
                            'evaluation_round': eval_round,
                            'score': round(llm_score, 1)
                        })
    
    llm_df = pd.DataFrame(llm_data)
    
    print(f"生成演示数据:")
    print(f"- 人类评分: {len(human_df)} 条 ({len(models)} 模型 × {len(questions)} 问题 × {len(dimensions)} 维度 × 3 评委)")
    print(f"- LLM评分: {len(llm_df)} 条 ({len(models)} 模型 × {len(questions)} 问题 × {len(dimensions)} 维度 × 5 轮回答 × 5 次评分)")
    
    return human_df, llm_df, models, questions, dimensions

def preprocess_and_aggregate(human_df, llm_df):
    """第一部分：数据预处理与聚合"""
    print("\n" + "=" * 60)
    print("第一部分：数据预处理与聚合")
    print("=" * 60)
    
    # 1. Human_Avg: Average of 3 human evaluators
    print("1. 计算 Human_Avg...")
    human_avg = human_df.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
    human_avg.rename(columns={'score': 'Human_Avg'}, inplace=True)
    
    # 2. LLM_Avg_Overall: Overall average across all rounds
    print("2. 计算 LLM_Avg_Overall...")
    llm_avg_overall = llm_df.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
    llm_avg_overall.rename(columns={'score': 'LLM_Avg_Overall'}, inplace=True)
    
    # 3. LLM_Repetition_Avg: Average across evaluation rounds for each answer round
    print("3. 计算 LLM_Repetition_Avg...")
    llm_rep_avg = llm_df.groupby(['model', 'question', 'dimension', 'answer_round'])['score'].mean().reset_index()
    llm_rep_avg.rename(columns={'score': 'LLM_Repetition_Avg'}, inplace=True)
    
    # 4. Merge human and LLM data
    print("4. 合并数据...")
    merged = pd.merge(human_avg, llm_avg_overall, on=['model', 'question', 'dimension'], how='inner')
    
    # 5. Disagreement_Score
    print("5. 计算 Disagreement_Score...")
    merged['Disagreement_Score'] = merged['LLM_Avg_Overall'] - merged['Human_Avg']
    
    print(f"聚合数据条目数: {len(merged)}")
    print(f"覆盖的模型数: {merged['model'].nunique()}")
    print(f"覆盖的问题数: {merged['question'].nunique()}")
    print(f"覆盖的维度数: {merged['dimension'].nunique()}")
    
    # Save data
    merged.to_csv(OUTPUT_DIR / "data" / "aggregated_scores_demo.csv", index=False, encoding='utf-8-sig')
    llm_rep_avg.to_csv(OUTPUT_DIR / "data" / "llm_repetition_scores_demo.csv", index=False, encoding='utf-8-sig')
    
    return merged, llm_rep_avg

def analyze_ranking_consistency(merged_data, dimensions):
    """第二部分：模型排序一致性分析"""
    print("\n" + "=" * 60)
    print("第二部分：模型排序一致性分析 (裁判视角)")
    print("=" * 60)
    
    # 2.1 LLM-人类一致性
    print("2.1 计算LLM-人类排序一致性...")
    
    correlation_results = []
    
    # For each question and dimension combination
    questions = merged_data['question'].unique()
    
    print(f"分析 {len(questions)} 个问题 × {len(dimensions)} 个维度 = {len(questions) * len(dimensions)} 个组合")
    
    for question in questions:
        for dimension in dimensions:
            subset = merged_data[
                (merged_data['question'] == question) & 
                (merged_data['dimension'] == dimension)
            ]
            
            if len(subset) >= 3:  # Need at least 3 models
                human_scores = subset['Human_Avg'].values
                llm_scores = subset['LLM_Avg_Overall'].values
                
                # Calculate correlations with p-values
                kendall_tau, kendall_p = kendalltau(human_scores, llm_scores)
                spearman_rho, spearman_p = spearmanr(human_scores, llm_scores)
                
                # Calculate ICC
                try:
                    icc_data = []
                    for i, model in enumerate(subset['model'].values):
                        icc_data.append({'model': model, 'rater': 'human', 'score': human_scores[i]})
                        icc_data.append({'model': model, 'rater': 'llm', 'score': llm_scores[i]})
                    
                    icc_df = pd.DataFrame(icc_data)
                    icc_result = pg.intraclass_corr(data=icc_df, targets='model', 
                                                  raters='rater', ratings='score')
                    
                    icc_row = icc_result[icc_result['Type'] == 'ICC1']
                    icc_val = float(icc_row['ICC'].iloc[0]) if len(icc_row) > 0 else np.nan
                    icc_p = float(icc_row['pval'].iloc[0]) if len(icc_row) > 0 else np.nan
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
                
                'icc_mean': float(icc_vals.mean()) if len(icc_vals) > 0 else np.nan,
                'icc_ci': [float(icc_vals.quantile(0.0015)), float(icc_vals.quantile(0.9985))] if len(icc_vals) > 0 else [np.nan, np.nan],
                
                'n_comparisons': len(dim_data)
            }
    
    # Save results
    correlation_df.to_csv(OUTPUT_DIR / "results" / "ranking_correlations_demo.csv", 
                        index=False, encoding='utf-8-sig')
    
    print(f"完成 {len(correlation_df)} 个问题-维度组合的相关性分析")
    
    # Print summary
    print("\n各维度LLM-人类排序一致性摘要:")
    for dim, stats in ranking_summary.items():
        print(f"  {dim}:")
        print(f"    Kendall's τ: {stats['kendall_mean']:.3f} [CI: {stats['kendall_ci'][0]:.3f}, {stats['kendall_ci'][1]:.3f}]")
        print(f"    显著性比例: {stats['kendall_significant_ratio']:.2%} (平均p={stats['kendall_avg_p']:.4f})")
    
    return correlation_df, ranking_summary

def create_visualizations(merged_data, correlation_df, ranking_summary, dimensions):
    """生成可视化图表"""
    print("\n生成可视化图表...")
    
    # Figure A: Overall scatter plots by dimension
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('图A: LLM与人类评分总体关系 (按维度分面)', fontsize=16, fontweight='bold')
    
    for i, dimension in enumerate(dimensions):
        row, col = i // 2, i % 2
        ax = axes[row, col]
        
        # Get data for this dimension
        dim_data = merged_data[merged_data['dimension'] == dimension]
        
        # Scatter plot
        ax.scatter(dim_data['Human_Avg'], dim_data['LLM_Avg_Overall'], 
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
    
    # Prepare data
    kendall_means = []
    kendall_errs = []
    spearman_means = []
    spearman_errs = []
    icc_means = []
    icc_errs = []
    
    for dim in dimensions:
        if dim in ranking_summary:
            s = ranking_summary[dim]
            
            kendall_means.append(s['kendall_mean'])
            kendall_errs.append([s['kendall_mean'] - s['kendall_ci'][0], s['kendall_ci'][1] - s['kendall_mean']])
            
            spearman_means.append(s['spearman_mean'])
            spearman_errs.append([s['spearman_mean'] - s['spearman_ci'][0], s['spearman_ci'][1] - s['spearman_mean']])
            
            icc_means.append(s['icc_mean'])
            icc_errs.append([s['icc_mean'] - s['icc_ci'][0], s['icc_ci'][1] - s['icc_mean']])
    
    # Convert to format needed for errorbar
    kendall_errs = np.array(kendall_errs).T
    spearman_errs = np.array(spearman_errs).T
    icc_errs = np.array(icc_errs).T
    
    # Plot error bars
    ax.errorbar(x_pos - width, kendall_means, yerr=kendall_errs, 
               fmt='o', capsize=5, capthick=2, label="Kendall's τ", markersize=8)
    ax.errorbar(x_pos, spearman_means, yerr=spearman_errs, 
               fmt='s', capsize=5, capthick=2, label="Spearman's ρ", markersize=8)
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
    
    # Violin plot for disagreement scores
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare disagreement data by model
    models = merged_data['model'].unique()
    disagreement_by_model = []
    
    for model in models:
        model_data = merged_data[merged_data['model'] == model]
        disagreement_by_model.append(model_data['Disagreement_Score'].values)
    
    # Create violin plot
    parts = ax.violinplot(disagreement_by_model, positions=range(len(models)), showmeans=True)
    
    ax.set_xlabel('AI模型')
    ax.set_ylabel('一致性误差 (LLM - Human)')
    ax.set_title('各模型的LLM-人类评分差异分布', fontweight='bold')
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='完全一致线')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "一致性误差小提琴图.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("可视化图表生成完成")

def generate_final_report(ranking_summary, correlation_df, total_entries, models_count, questions_count, dimensions_count):
    """生成最终报告"""
    print("\n生成最终报告...")
    
    report = f"""
# AI模型评估项目：一致性分析报告

## 摘要与引言

本报告分析了{models_count}个AI模型在{questions_count}个化学相关问题上的表现，评估了LLM评委与人类评委在评分上的一致性。分析涵盖{dimensions_count}个评估维度：正确性、完备性、理论深度、论述严谨性与信息密度。

## 数据概况

- **评估模型数量**: {models_count}个
- **评估问题数量**: {questions_count}个  
- **评估维度**: {dimensions_count}个
- **总数据条目**: {total_entries}条

## 方法论

### 数据预处理方法
1. **Human_Avg**: 计算3位人类评委对每个{{模型,问题,维度}}组合的平均分
2. **LLM_Avg_Overall**: 计算LLM对每个{{模型,问题,维度}}组合的总体平均分(5轮回答×5次重复评分)
3. **Disagreement_Score**: LLM_Avg_Overall - Human_Avg

### 分析框架
本研究采用两个层次的分析框架：
1. **模型排序一致性 (裁判视角)**: 评估LLM作为"裁判"，其给出的模型优劣排行榜是否与人类一致
2. **模型诊断一致性 (教练视角)**: 评估LLM作为"教练"，其对单个模型能力优劣的诊断是否与人类一致

### 统计分析方法
- **Kendall's Tau-b**: 主要的排序一致性指标
- **Spearman's Rho**: 辅助的排序一致性指标  
- **ICC(A,1)**: 绝对一致性系数
- **置信区间**: 99.7%置信区间 (0.15th - 99.85th百分位数)

## 核心发现：模型排序一致性

### LLM-人类排序一致性分析

以问题和维度为分析单位，计算LLM与人类评委对{models_count}个AI模型的排序一致性：

"""
    
    for dimension, stats in ranking_summary.items():
        kendall_mean = stats['kendall_mean']
        kendall_ci = stats['kendall_ci']
        sig_ratio = stats['kendall_significant_ratio']
        avg_p = stats['kendall_avg_p']
        
        # 判断一致性水平
        if kendall_mean > 0.7:
            consistency_level = "高度一致"
        elif kendall_mean > 0.5:
            consistency_level = "较高一致性"
        elif kendall_mean > 0.3:
            consistency_level = "中等一致性"
        else:
            consistency_level = "较低一致性"
        
        report += f"""
#### {dimension}

- **Kendall's τ平均值**: {kendall_mean:.3f} [99.7% CI: {kendall_ci[0]:.3f}, {kendall_ci[1]:.3f}]
- **统计显著性**: {sig_ratio:.1%}的比较达到p < 0.05 (平均p值 = {avg_p:.4f})
- **一致性水平**: {consistency_level}
- **分析结论**: 在'{dimension}'维度上，LLM与人类评委在模型排序方面表现出{consistency_level}，表明{"LLM可以作为该维度评估的可靠辅助工具" if kendall_mean > 0.5 else "LLM在该维度的评估需要更多改进"}。
"""
    
    # 添加整体结论
    overall_kendall = np.mean([stats['kendall_mean'] for stats in ranking_summary.values()])
    overall_sig_ratio = np.mean([stats['kendall_significant_ratio'] for stats in ranking_summary.values()])
    
    report += f"""

## 评委可靠性分析

### 统计显著性验证
- **总体平均Kendall's τ**: {overall_kendall:.3f}
- **显著性结果比例**: {overall_sig_ratio:.1%}
- **数据质量**: 基于{len(correlation_df)}个独立的问题-维度组合分析

## 结论与建议

### 主要发现
1. **总体一致性**: LLM与人类评委在模型排序上表现出{'可接受' if overall_kendall > 0.3 else '有限'}的一致性（平均τ = {overall_kendall:.3f}）
2. **维度差异**: 不同评估维度下的一致性存在显著差异
3. **统计可靠性**: {overall_sig_ratio:.1%}的分析结果具有统计学意义

### 实际应用建议
1. **LLM辅助评估**: LLM可以作为评估工具的{'重要' if overall_kendall > 0.5 else '辅助'}补充
2. **人类专家参与**: 在关键评估决策中仍需人类专家的判断
3. **维度特异性**: 针对一致性较低的维度加强评估标准和训练

### 研究局限性
- 本分析基于演示数据展示分析框架
- 实际应用需要基于真实评估数据进行验证
- 需要更多样本量以提高统计功效

---
*本报告由AI一致性分析系统生成 - 演示版本*
*生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Save report
    with open(OUTPUT_DIR / "results" / "final_comprehensive_report_demo.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("最终报告已生成")
    print(f"报告保存在: {OUTPUT_DIR / 'results' / 'final_comprehensive_report_demo.md'}")

def main():
    """主执行函数"""
    print("🚀 开始AI模型评估一致性分析演示...")
    
    # Step 0: Load sample data
    human_df, llm_df, models, questions, dimensions = load_sample_data()
    
    # Step 1: Preprocessing and aggregation  
    merged_data, llm_rep_data = preprocess_and_aggregate(human_df, llm_df)
    
    # Step 2: Ranking consistency analysis
    correlation_df, ranking_summary = analyze_ranking_consistency(merged_data, dimensions)
    
    # Create visualizations
    create_visualizations(merged_data, correlation_df, ranking_summary, dimensions)
    
    # Generate final report
    generate_final_report(
        ranking_summary, 
        correlation_df,
        len(merged_data),
        len(models),
        len(questions), 
        len(dimensions)
    )
    
    # Save comprehensive results
    results = {
        'preprocessing': {
            'total_entries': len(merged_data),
            'models_count': len(models),
            'questions_count': len(questions),
            'dimensions_count': len(dimensions)
        },
        'ranking_consistency': {
            'summary_by_dimension': ranking_summary,
            'correlation_details': correlation_df.to_dict('records')
        }
    }
    
    with open(OUTPUT_DIR / "results" / "comprehensive_analysis_results_demo.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("✅ 一致性分析演示完成!")
    print(f"📁 所有结果保存在: {OUTPUT_DIR}")
    print("\n📋 主要输出文件:")
    print(f"  📊 最终报告: final_comprehensive_report_demo.md")
    print(f"  📈 可视化图表: figures/图*.png") 
    print(f"  📄 详细结果: comprehensive_analysis_results_demo.json")
    print(f"  📊 数据文件: data/*_demo.csv")
    print("=" * 60)
    
    # Print summary
    print("\n📊 分析结果摘要:")
    print(f"🤖 AI模型数量: {len(models)}")
    print(f"❓ 问题数量: {len(questions)}")
    print(f"📏 评估维度: {len(dimensions)}")
    print(f"📈 数据条目: {len(merged_data)}")
    
    print(f"\n🎯 各维度LLM-人类排序一致性 (Kendall's τ):")
    for dim, stats in ranking_summary.items():
        kendall_mean = stats['kendall_mean']
        sig_ratio = stats['kendall_significant_ratio']
        status = "🟢 高" if kendall_mean > 0.5 else "🟡 中" if kendall_mean > 0.3 else "🔴 低"
        print(f"  {dim}: {kendall_mean:.3f} ({status}, 显著性: {sig_ratio:.1%})")
    
    overall_kendall = np.mean([stats['kendall_mean'] for stats in ranking_summary.values()])
    print(f"\n🎖️  总体平均一致性: {overall_kendall:.3f}")

if __name__ == "__main__":
    main()