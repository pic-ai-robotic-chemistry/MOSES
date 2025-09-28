#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性散点图可视化脚本
基于原始评分数据生成真正的一致性散点图，而非相关系数的散点图
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from pathlib import Path
import sys
import json

# 添加路径以导入配置和数据加载器
vis_root = Path(__file__).parent.parent  # vis目录
eva_res_root = vis_root.parent  # eva_res目录
consistency_root = eva_res_root / "consistency_analysis"  # consistency_analysis目录

sys.path.append(str(vis_root))
sys.path.append(str(consistency_root))

from config.vis_config import COLOR_SCHEME, DIMENSION_INFO, setup_plot_style
from data_loader import ConsistencyDataLoader
from analysis_config import AnalysisConfig

class ConsistencyScatterPlotter:
    """一致性散点图生成器"""
    
    def __init__(self):
        self.color_scheme = COLOR_SCHEME
        self.dimension_info = DIMENSION_INFO
        self.fig_size = (20, 6)  # 宽图用于多子图
        self.setup_style()
        
        # 创建分析配置（与现有报告一致）
        self.analysis_config = AnalysisConfig(
            name="Reduced Analysis (4 Dimensions, Selected Models Only)",
            description="Analysis with reduced dimensions for only GPT-4 family models",
            dimensions=["正确性", "完备性", "理论深度", "论述严谨性与信息密度"],
            llm_strategy='average',
            output_suffix="reduced_selected_models",
            selected_models=[
                "gpt-4.1-final", "gpt-4.1-nano-final-815-1", 
                "lightrag-gpt-4_1", "lightrag-gpt-4_1-nano", 
                "o1-final", "o3-final", 
                "gpt-4o-final-815-1", "gpt-4o-mini-final-815-1", 
                "reordered_MOSES-final", "reordered_MOSES-nano-final"
            ]
        )
        
        # 数据加载器
        self.data_loader = ConsistencyDataLoader(config=self.analysis_config)
        
        # 维度颜色映射
        self.dimension_colors = COLOR_SCHEME['dimensions']
        
        # 存储处理后的数据
        self.processed_data = None
        
    def setup_style(self):
        """设置matplotlib样式"""
        setup_plot_style()
    
    def load_and_process_data(self):
        """加载并处理数据"""
        print("Loading consistency data...")
        
        # 加载人工和LLM评分
        self.data_loader.load_human_scores()
        self.data_loader.load_llm_scores()
        
        # 获取处理后的数据
        human_scores = self.data_loader.processed_data['human_scores']
        llm_scores = self.data_loader.processed_data['llm_scores']
        
        print(f"Loaded {len(human_scores)} human systems, {len(llm_scores)} LLM systems")
        
        # 处理数据为散点图格式
        self.processed_data = self._organize_data_for_scatter(human_scores, llm_scores)
        
        return self.processed_data
    
    def _organize_data_for_scatter(self, human_scores, llm_scores):
        """将原始评分数据组织为散点图所需格式"""
        
        # 存储所有数据点
        scatter_data = {
            'human_internal': {'data_points': []},
            'llm_internal': {'data_points': []},
            'human_llm_agreement': {'data_points': []}
        }
        
        # 筛选指定的系统
        selected_systems = set(self.analysis_config.selected_models) if self.analysis_config.selected_models else None
        
        # 处理人工内部一致性数据
        for system_name, system_data in human_scores.items():
            # 只处理指定的系统
            if selected_systems and system_name not in selected_systems:
                continue
                
            for question_id, question_data in system_data.items():
                for dimension, scores in question_data.items():
                    # 只处理指定的维度
                    if dimension not in self.analysis_config.dimensions:
                        continue
                        
                    if len(scores) >= 3:  # 确保有3个评分者
                        # 为每个评分者创建数据点（与其他评分者平均的对比）
                        for rater_idx in range(3):
                            others_avg = np.mean([scores[i] for i in range(3) if i != rater_idx])
                            rater_score = scores[rater_idx]
                            
                            scatter_data['human_internal']['data_points'].append({
                                'system': system_name,
                                'question': question_id,
                                'dimension': dimension,
                                'rater': f'rater_{rater_idx + 1}',
                                'x': others_avg,  # 其他评分者平均
                                'y': rater_score  # 该评分者评分
                            })
        
        # 处理LLM内部一致性数据
        # 需要映射系统名称
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
        
        for system_name, system_data in llm_scores.items():
            # 找到对应的人工系统名
            mapped_system = None
            for human_sys, llm_sys in llm_system_mapping.items():
                if llm_sys == system_name:
                    mapped_system = human_sys
                    break
            
            # 只处理指定的系统
            if selected_systems and mapped_system not in selected_systems:
                continue
                
            for question_id, question_data in system_data.items():
                for dimension, scores in question_data.items():
                    # 只处理指定的维度
                    if dimension not in self.analysis_config.dimensions:
                        continue
                        
                    if len(scores) >= 5:  # 确保有5次评分
                        # 为每次评分创建数据点
                        for round_idx in range(5):
                            others_avg = np.mean([scores[i] for i in range(5) if i != round_idx])
                            round_score = scores[round_idx]
                            
                            scatter_data['llm_internal']['data_points'].append({
                                'system': mapped_system,  # 使用映射后的系统名
                                'question': question_id,
                                'dimension': dimension,
                                'round': f'round_{round_idx + 1}',
                                'x': others_avg,
                                'y': round_score
                            })
        
        # 处理人工-LLM一致性数据
        for human_sys, llm_sys in llm_system_mapping.items():
            if selected_systems and human_sys not in selected_systems:
                continue
                
            if human_sys in human_scores and llm_sys in llm_scores:
                human_system = human_scores[human_sys]
                llm_system = llm_scores[llm_sys]
                
                # 找到共同的问题和维度
                for question_id in human_system.keys():
                    if question_id in llm_system:
                        human_question = human_system[question_id]
                        llm_question = llm_system[question_id]
                        
                        for dimension in human_question.keys():
                            if dimension in llm_question and dimension in self.analysis_config.dimensions:
                                human_scores_dim = human_question[dimension]
                                llm_scores_dim = llm_question[dimension]
                                
                                if len(human_scores_dim) >= 2 and len(llm_scores_dim) >= 2:
                                    human_avg = np.mean(human_scores_dim)
                                    llm_avg = np.mean(llm_scores_dim)
                                    
                                    scatter_data['human_llm_agreement']['data_points'].append({
                                        'system': human_sys,
                                        'question': question_id,
                                        'dimension': dimension,
                                        'x': human_avg,  # 人工平均
                                        'y': llm_avg     # LLM平均
                                    })
        
        print(f"Processed data points (filtered):")
        print(f"  Human internal: {len(scatter_data['human_internal']['data_points'])}")
        print(f"  LLM internal: {len(scatter_data['llm_internal']['data_points'])}")
        print(f"  Human-LLM agreement: {len(scatter_data['human_llm_agreement']['data_points'])}")
        
        return scatter_data
    
    def create_human_internal_consistency_plot(self):
        """创建人工内部一致性散点图"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Human Internal Consistency', fontsize=16, fontweight='bold')
        
        data_points = self.processed_data['human_internal']['data_points']
        df = pd.DataFrame(data_points)
        
        # 为每个评分者创建子图
        for rater_idx, rater_name in enumerate(['rater_1', 'rater_2', 'rater_3']):
            ax = axes[rater_idx]
            rater_data = df[df['rater'] == rater_name]
            
            # 英文维度标签映射
            dimension_en_labels = {
                "正确性": "Correctness",
                "完备性": "Completeness", 
                "理论深度": "Theoretical Depth",
                "论述严谨性与信息密度": "Rigor & Info Density"
            }
            
            # 按维度绘制散点图
            for dimension in self.analysis_config.dimensions:
                dim_data = rater_data[rater_data['dimension'] == dimension]
                if len(dim_data) > 0:
                    ax.scatter(dim_data['x'], dim_data['y'], 
                             color=self.dimension_colors[dimension],
                             alpha=0.6, s=20, label=dimension_en_labels.get(dimension, dimension))
            
            # 添加y=x参考线
            lims = [
                np.min([ax.get_xlim(), ax.get_ylim()]),
                np.max([ax.get_xlim(), ax.get_ylim()])
            ]
            ax.plot(lims, lims, 'k--', alpha=0.5, linewidth=1, label='Perfect Agreement (y=x)')
            
            # 计算并添加回归线
            if len(rater_data) > 5:
                from sklearn.linear_model import LinearRegression
                reg = LinearRegression()
                reg.fit(rater_data[['x']], rater_data['y'])
                x_line = np.linspace(rater_data['x'].min(), rater_data['x'].max(), 100)
                y_line = reg.predict(x_line.reshape(-1, 1))
                ax.plot(x_line, y_line, 'r-', alpha=0.7, linewidth=2, label='Fit Line')
                
                # 计算相关系数
                r, p = pearsonr(rater_data['x'], rater_data['y'])
                
                # 格式化P值显示
                if p < 0.001:
                    p_text = "p < 0.001"
                else:
                    p_text = f"p = {p:.3f}"
                
                ax.text(0.05, 0.95, f'r = {r:.3f}, {p_text}', 
                       transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            
            # 设置标签和标题
            ax.set_xlabel('Other Raters Average')
            ax.set_ylabel(f'Rater {rater_idx + 1} Score')
            ax.set_title(f'Rater {rater_idx + 1} vs Others')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            
            if rater_idx == 2:  # 只在最后一个子图显示图例
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        return fig
    
    def create_llm_internal_consistency_plot(self):
        """创建LLM内部一致性散点图"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # 只选择3个代表性的轮次
        fig.suptitle('LLM Internal Consistency', fontsize=16, fontweight='bold')
        
        data_points = self.processed_data['llm_internal']['data_points']
        df = pd.DataFrame(data_points)
        
        # 选择代表性的轮次 (round 1, 3, 5)
        selected_rounds = ['round_1', 'round_3', 'round_5']
        
        for plot_idx, round_name in enumerate(selected_rounds):
            ax = axes[plot_idx]
            round_data = df[df['round'] == round_name]
            
            # 英文维度标签映射
            dimension_en_labels = {
                "正确性": "Correctness",
                "完备性": "Completeness", 
                "理论深度": "Theoretical Depth",
                "论述严谨性与信息密度": "Rigor & Info Density"
            }
            
            # 按维度绘制散点图
            for dimension in self.analysis_config.dimensions:
                dim_data = round_data[round_data['dimension'] == dimension]
                if len(dim_data) > 0:
                    ax.scatter(dim_data['x'], dim_data['y'], 
                             color=self.dimension_colors[dimension],
                             alpha=0.6, s=20, label=dimension_en_labels.get(dimension, dimension))
            
            # 添加y=x参考线
            lims = [
                np.min([ax.get_xlim(), ax.get_ylim()]),
                np.max([ax.get_xlim(), ax.get_ylim()])
            ]
            ax.plot(lims, lims, 'k--', alpha=0.5, linewidth=1, label='Perfect Agreement (y=x)')
            
            # 计算并添加回归线
            if len(round_data) > 5:
                from sklearn.linear_model import LinearRegression
                reg = LinearRegression()
                reg.fit(round_data[['x']], round_data['y'])
                x_line = np.linspace(round_data['x'].min(), round_data['x'].max(), 100)
                y_line = reg.predict(x_line.reshape(-1, 1))
                ax.plot(x_line, y_line, 'r-', alpha=0.7, linewidth=2, label='Fit Line')
                
                # 计算相关系数
                r, p = pearsonr(round_data['x'], round_data['y'])
                
                # 格式化P值显示
                if p < 0.001:
                    p_text = "p < 0.001"
                else:
                    p_text = f"p = {p:.3f}"
                
                ax.text(0.05, 0.95, f'r = {r:.3f}, {p_text}', 
                       transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            
            # 设置标签和标题
            ax.set_xlabel('Other Rounds Average')
            ax.set_ylabel(f'{round_name.replace("_", " ").title()} Score')
            ax.set_title(f'{round_name.replace("_", " ").title()} vs Others')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            
            if plot_idx == 2:  # 只在最后一个子图显示图例
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        return fig
    
    def create_human_llm_agreement_plot(self):
        """创建人工-LLM一致性散点图"""
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        fig.suptitle('Human-LLM Agreement', fontsize=16, fontweight='bold')
        
        data_points = self.processed_data['human_llm_agreement']['data_points']
        df = pd.DataFrame(data_points)
        
        # 英文维度标签映射
        dimension_en_labels = {
            "正确性": "Correctness",
            "完备性": "Completeness", 
            "理论深度": "Theoretical Depth",
            "论述严谨性与信息密度": "Rigor & Info Density"
        }
        
        # 按维度绘制散点图
        for dimension in self.analysis_config.dimensions:
            dim_data = df[df['dimension'] == dimension]
            if len(dim_data) > 0:
                ax.scatter(dim_data['x'], dim_data['y'], 
                         color=self.dimension_colors[dimension],
                         alpha=0.6, s=30, label=dimension_en_labels.get(dimension, dimension))
        
        # 添加y=x参考线
        lims = [
            np.min([ax.get_xlim(), ax.get_ylim()]),
            np.max([ax.get_xlim(), ax.get_ylim()])
        ]
        ax.plot(lims, lims, 'k--', alpha=0.5, linewidth=1, label='Perfect Agreement (y=x)')
        
        # 计算并添加回归线
        if len(df) > 5:
            from sklearn.linear_model import LinearRegression
            reg = LinearRegression()
            reg.fit(df[['x']], df['y'])
            x_line = np.linspace(df['x'].min(), df['x'].max(), 100)
            y_line = reg.predict(x_line.reshape(-1, 1))
            ax.plot(x_line, y_line, 'r-', alpha=0.7, linewidth=2, label='Fit Line')
            
            # 计算相关系数
            r, p = pearsonr(df['x'], df['y'])
            
            # 格式化P值显示
            if p < 0.001:
                p_text = "p < 0.001"
            else:
                p_text = f"p = {p:.3f}"
            
            ax.text(0.05, 0.95, f'r = {r:.3f}, {p_text}', 
                   transform=ax.transAxes, fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 设置标签和标题
        ax.set_xlabel('Human Raters Average')
        ax.set_ylabel('LLM Average Score')
        ax.set_title('Human vs LLM Scoring Agreement')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def generate_all_plots(self, output_dir):
        """生成所有一致性散点图"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print("Generating consistency scatter plots...")
        
        # 加载数据
        self.load_and_process_data()
        
        # 生成图表
        plots = [
            ("human_internal_consistency", self.create_human_internal_consistency_plot()),
            ("llm_internal_consistency", self.create_llm_internal_consistency_plot()),
            ("human_llm_agreement", self.create_human_llm_agreement_plot())
        ]
        
        # 保存图表
        for plot_name, fig in plots:
            # 保存PNG
            png_path = output_dir / f"{plot_name}_scatter.png"
            fig.savefig(png_path, dpi=300, bbox_inches='tight')
            print(f"Saved: {png_path}")
            
            # 保存PDF
            pdf_path = output_dir / f"{plot_name}_scatter.pdf"
            fig.savefig(pdf_path, bbox_inches='tight')
            print(f"Saved: {pdf_path}")
            
            plt.close(fig)
        
        print("All consistency scatter plots generated successfully!")

if __name__ == "__main__":
    plotter = ConsistencyScatterPlotter()
    
    output_dir = Path(__file__).parent.parent / "plots"
    plotter.generate_all_plots(output_dir)