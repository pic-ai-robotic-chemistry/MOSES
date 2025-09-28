"""
顶级模型雷达图可视化脚本
创建顶级AI模型的多维度雷达图比较
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os
from math import pi

# 添加配置和数据处理模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_processing'))

from vis_config import (
    COLOR_SCHEME,
    MODEL_INFO,
    DIMENSION_INFO,
    PLOT_STYLE,
    setup_plot_style,
)
from data_processor import DataProcessor


class TopModelRadarVisualizer:
    """顶级模型雷达图可视化器"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/radar_charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        setup_plot_style()
    
    def create_single_radar_chart(self, save_format=['png', 'pdf', 'svg']):
        """
        创建包含顶级模型的单个雷达图
        """
        # 获取数据
        radar_data = self.processor.create_top_model_radar_data()
        
        # 计算角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]  # 完成圆圈
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])
        
        # 为每个模型绘制雷达图
        for i, model_data in enumerate(radar_data):
            model = model_data['model']
            scores = model_data['scores'] + [model_data['scores'][0]]  # 闭合图形
            
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            # 绘制线条（无点）和填充
            ax.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'], label=display_name, color=color)
            ax.fill(angles, scores, alpha=0.18, color=color)
        
        # 设置维度标签
        dimension_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimension_labels, fontsize=12)
        
        # 设置径向标签
        # 中心点从0调整为3分：显示范围 3–10
        ax.set_ylim(3, 10)
        ax.set_yticks([3, 5, 7, 9, 10])
        ax.set_yticklabels(['3', '5', '7', '9', '10'], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        
        # 设置标题
        ax.set_title('Top AI Models Performance Comparison\n(4 Dimensions, Doubao Judge)', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # 添加图例（统一位置与样式）
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), fontsize=12, frameon=False)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"top_models_radar.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"顶级模型雷达图已保存: {filepath}")
        
        return fig, ax
    
    def create_individual_radar_charts(self, save_format=['png', 'pdf']):
        """
        为每个顶级模型创建独立的雷达图
        """
        # 获取数据
        radar_data = self.processor.create_top_model_radar_data()
        
        # 计算角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        
        # 创建子图
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw=dict(projection='polar'))
        
        for i, (ax, model_data) in enumerate(zip(axes, radar_data)):
            ax.set_facecolor(COLOR_SCHEME['radar']['background'])
            model = model_data['model']
            scores = model_data['scores'] + [model_data['scores'][0]]
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            # 绘制雷达图（无点）
            ax.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'] + 1, color=color)
            ax.fill(angles, scores, alpha=0.2, color=color)
            
            # 设置维度标签
            dimension_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimension_labels, fontsize=11)
            
            # 设置径向标签
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9)
            ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
            
            # 设置标题
            ax.set_title(f'{display_name}\n(Avg: {np.mean(model_data["scores"]):.2f})', 
                        fontsize=14, fontweight='bold', pad=20)
            
            # 在雷达图上标注具体数值
            for angle, score, label in zip(angles[:-1], model_data['scores'], dimension_labels):
                ax.text(angle, score + 0.3, f'{score:.1f}', 
                       ha='center', va='center', fontsize=10, fontweight='bold')
        
        # 设置总标题
        fig.suptitle('Individual Model Performance Analysis\n(Performance Scores by Dimension)', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"individual_model_radars.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"独立模型雷达图已保存: {filepath}")
        
        return fig, axes
    
    def create_comparative_radar_chart(self, save_format=['png', 'pdf']):
        """
        创建比较型雷达图，突出显示模型差异
        """
        # 获取数据
        radar_data = self.processor.create_top_model_radar_data()
        
        # 计算角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), 
                                      subplot_kw=dict(projection='polar'))
        ax1.set_facecolor(COLOR_SCHEME['radar']['background'])
        ax2.set_facecolor(COLOR_SCHEME['radar']['background'])
        
        # 左侧：原始性能对比
        for model_data in radar_data:
            model = model_data['model']
            scores = model_data['scores'] + [model_data['scores'][0]]
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            ax1.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'], label=display_name, color=color, alpha=0.9)
            ax1.fill(angles, scores, alpha=0.15, color=color)
        
        # 设置左侧图表
        dimension_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(dimension_labels, fontsize=11)
        ax1.set_ylim(0, 10)
        ax1.set_yticks([2, 4, 6, 8, 10])
        ax1.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9)
        ax1.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax1.set_title('Absolute Performance\n(Original Scores)', fontsize=12, fontweight='bold')
        
        # 右侧：标准化性能对比（相对于最大值）
        # 计算每个维度的最大值
        all_scores = np.array([data['scores'] for data in radar_data])
        max_scores = np.max(all_scores, axis=0)
        
        for model_data in radar_data:
            model = model_data['model']
            # 标准化到最大值
            normalized_scores = [score / max_val for score, max_val in 
                               zip(model_data['scores'], max_scores)]
            normalized_scores += [normalized_scores[0]]
            
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            ax2.plot(angles, normalized_scores, '-', linewidth=PLOT_STYLE['line_width'], label=display_name, color=color, alpha=0.9)
            ax2.fill(angles, normalized_scores, alpha=0.15, color=color)
        
        # 设置右侧图表
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(dimension_labels, fontsize=11)
        ax2.set_ylim(0, 1.0)
        ax2.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax2.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
        ax2.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax2.set_title('Relative Performance\n(% of Dimension Maximum)', fontsize=12, fontweight='bold')
        
        # 添加图例
        plt.legend(loc='center', bbox_to_anchor=(-0.1, -0.1), ncol=3, fontsize=11, frameon=False)
        
        # 设置总标题
        fig.suptitle('Top Models Performance Analysis: Absolute vs. Relative Comparison', 
                    fontsize=14, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"comparative_radar_analysis.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"比较雷达图已保存: {filepath}")
        
        return fig, (ax1, ax2)

    def create_selected_models_radar(self, models=None, save_format=['png', 'pdf', 'svg']):
        """为指定模型列表创建分数雷达图（四维）。
        默认: ['MOSES','o3','gpt-4.1','lightrag-4.1']
        """
        if models is None:
            models = ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1']

        radar_data = self.processor.create_models_radar_data(models)
        # 角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])

        for model_info in radar_data:
            model = model_info['model']
            scores = model_info['scores'] + [model_info['scores'][0]]
            color = COLOR_SCHEME['models'][model]
            label = model_info['display_name']
            # 主图样式：无点，仅折线
            ax.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=label)
            ax.fill(angles, scores, alpha=0.18, color=color)

        # 轴标签
        dim_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dim_labels, fontsize=12)
        # 将中心半径设为3分
        try:
            ax.set_rlim(3, 10)  # Matplotlib >= 3.5
        except Exception:
            ax.set_ylim(3, 10)
        ax.set_yticks([3, 5, 7, 9, 10])
        ax.set_yticklabels(['3', '5', '7', '9', '10'], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax.set_title('Selected Models Performance (4 Dimensions)', fontsize=16, fontweight='bold', pad=28)

        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), frameon=False)
        plt.tight_layout()

        # 保存
        tag = '_'.join([m.replace('.', '').replace('-', '') for m in models])
        for fmt in save_format:
            path = self.output_dir / f"selected_models_radar_{tag}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"选定模型雷达图已保存: {path}")

        return fig, ax

    def create_selected_models_radar_relative(self, models=None, save_format=['png', 'pdf', 'svg']):
        """为指定模型创建相对雷达图（各维度相对于所选模型中的最大值进行归一化）。"""
        if models is None:
            models = ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1']

        radar_data = self.processor.create_models_radar_data(models)
        # 计算各维度最大值（在所选模型范围内）
        all_scores = np.array([d['scores'] for d in radar_data])
        max_scores = np.maximum(all_scores.max(axis=0), 1e-9)

        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])

        for model_info in radar_data:
            model = model_info['model']
            rel = [s/m for s, m in zip(model_info['scores'], max_scores)]
            rel += [rel[0]]
            color = COLOR_SCHEME['models'][model]
            label = model_info['display_name']
            # 主图样式：无点，仅折线
            ax.plot(angles, rel, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=label)
            ax.fill(angles, rel, alpha=0.18, color=color)

        dim_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dim_labels, fontsize=12)
        # 中心点从0调整为40%：显示范围 40%–100%
        try:
            ax.set_rlim(0.4, 1.0)
        except Exception:
            ax.set_ylim(0.4, 1.0)
        ax.set_yticks([0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['40%', '60%', '80%', '100%'], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax.set_title('Selected Models Relative Performance (per-dimension max = 100%)', fontsize=16, fontweight='bold', pad=28)

        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), frameon=False)
        plt.tight_layout()

        tag = '_'.join([m.replace('.', '').replace('-', '') for m in models])
        for fmt in save_format:
            path = self.output_dir / f"selected_models_radar_relative_{tag}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"选定模型相对雷达图已保存: {path}")

        return fig, ax

    def create_selected_models_elo_radar(self, models=None, save_format=['png', 'pdf', 'svg']):
        """为指定模型创建 ELO 绝对雷达图（四维）。"""
        if models is None:
            models = ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1']

        radar_data = self.processor.create_models_elo_radar_data(models)
        if not radar_data:
            print('未从 ELO 维度数据找到指定模型，检查模型名称。')
            return None, None

        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])

        # 画线
        for model_info in radar_data:
            model = model_info['model']
            vals = model_info['scores'] + [model_info['scores'][0]]
            color = COLOR_SCHEME['models'][model]
            label = model_info['display_name']
            ax.plot(angles, vals, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=label)
            ax.fill(angles, vals, alpha=0.18, color=color)

        # 轴与范围（根据数据动态设置）
        dim_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dim_labels, fontsize=12)

        all_vals = np.array([d['scores'] for d in radar_data])
        vmin = float(np.min(all_vals))
        vmax = float(np.max(all_vals))
        # 稍微留边，刻度选择4个等距刻度
        lower = np.floor((vmin - 0.5) / 1.0) * 1.0
        upper = np.ceil((vmax + 0.5) / 1.0) * 1.0
        try:
            ax.set_rlim(lower, upper)
        except Exception:
            ax.set_ylim(lower, upper)
        ticks = np.linspace(lower, upper, 5)
        ax.set_yticks(ticks)
        ax.set_yticklabels([f'{t:.0f}' if upper - lower > 6 else f'{t:.1f}' for t in ticks], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax.set_title('Selected Models ELO Rating (4 Dimensions)', fontsize=16, fontweight='bold', pad=28)

        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), frameon=False)
        plt.tight_layout()

        tag = '_'.join([m.replace('.', '').replace('-', '') for m in models])
        for fmt in save_format:
            path = self.output_dir / f"selected_models_elo_radar_{tag}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"选定模型ELO雷达图已保存: {path}")

        return fig, ax

    def create_selected_models_elo_radar_relative(self, models=None, save_format=['png', 'pdf', 'svg']):
        """为指定模型创建 ELO 相对雷达图（各维度相对于所选模型中的最大值归一化）。"""
        if models is None:
            models = ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1']

        radar_data = self.processor.create_models_elo_radar_data(models)
        if not radar_data:
            print('未从 ELO 维度数据找到指定模型，检查模型名称。')
            return None, None

        all_scores = np.array([d['scores'] for d in radar_data])
        max_scores = np.maximum(all_scores.max(axis=0), 1e-9)

        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])

        for model_info in radar_data:
            model = model_info['model']
            rel = [s/m for s, m in zip(model_info['scores'], max_scores)]
            rel += [rel[0]]
            color = COLOR_SCHEME['models'][model]
            label = model_info['display_name']
            ax.plot(angles, rel, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=label)
            ax.fill(angles, rel, alpha=0.18, color=color)

        dim_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dim_labels, fontsize=12)
        # 相对图中心 40%
        try:
            ax.set_rlim(0.4, 1.0)
        except Exception:
            ax.set_ylim(0.4, 1.0)
        ax.set_yticks([0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['40%', '60%', '80%', '100%'], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax.set_title('Selected Models ELO Rating (Relative, per-dimension max = 100%)', fontsize=16, fontweight='bold', pad=28)

        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), frameon=False)
        plt.tight_layout()

        tag = '_'.join([m.replace('.', '').replace('-', '') for m in models])
        for fmt in save_format:
            path = self.output_dir / f"selected_models_elo_radar_relative_{tag}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"选定模型ELO相对雷达图已保存: {path}")

        return fig, ax

    def create_selected_models_score_elo_combined(self, models=None, normalization_scope='all', save_format=['png', 'pdf']):
        """在同一Figure中并排绘制：左=绝对分数雷达(0–10, 中心3)，右=ELO相对雷达(40–100%)。
        normalization_scope: 'all' 使用全体模型的维度最大值归一化ELO；'selected' 使用所选模型组内最大值。
        """
        if models is None:
            models = ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1']

        # 分数数据（绝对）
        score_data = self.processor.create_models_radar_data(models)

        # ELO 数据（相对）
        elo_data = self.processor.create_models_elo_radar_data(models)
        if normalization_scope == 'all':
            # 用全体模型的维度最大值进行归一化，增强可复现性
            all_elo = self.processor.create_models_elo_radar_data(MODEL_INFO['order'])
            all_scores = np.array([d['scores'] for d in all_elo]) if all_elo else np.array([d['scores'] for d in elo_data])
        else:
            all_scores = np.array([d['scores'] for d in elo_data])
        elo_max = np.maximum(all_scores.max(axis=0), 1e-9)

        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(projection='polar'))
        for ax in (ax1, ax2):
            ax.set_facecolor(COLOR_SCHEME['radar']['background'])

        # 左：分数绝对值（0–10，中心3）
        for item in score_data:
            vals = item['scores'] + [item['scores'][0]]
            color = COLOR_SCHEME['models'][item['model']]
            ax1.plot(angles, vals, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=item['display_name'])
            ax1.fill(angles, vals, alpha=0.18, color=color)
        dim_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(dim_labels, fontsize=11)
        try:
            ax1.set_rlim(3, 10)
        except Exception:
            ax1.set_ylim(3, 10)
        ax1.set_yticks([3, 5, 7, 9, 10])
        ax1.set_yticklabels(['3', '5', '7', '9', '10'], fontsize=9)
        ax1.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax1.set_title('LLM-Judge Score (0–10)', fontsize=12, fontweight='bold')

        # 右：ELO 相对（40–100%）
        for item in elo_data:
            rel = [s/m for s, m in zip(item['scores'], elo_max)]
            rel += [rel[0]]
            color = COLOR_SCHEME['models'][item['model']]
            ax2.plot(angles, rel, '-', linewidth=PLOT_STYLE['line_width'], color=color, label=item['display_name'])
            ax2.fill(angles, rel, alpha=0.18, color=color)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(dim_labels, fontsize=11)
        try:
            ax2.set_rlim(0.4, 1.0)
        except Exception:
            ax2.set_ylim(0.4, 1.0)
        ax2.set_yticks([0.4, 0.6, 0.8, 1.0])
        ax2.set_yticklabels(['40%', '60%', '80%', '100%'], fontsize=9)
        ax2.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        ax2.set_title('ELO Rating (Relative to cohort max)', fontsize=12, fontweight='bold')

        # 统一图例
        handles, labels = ax1.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=min(4, len(labels)), frameon=False)
        fig.suptitle('Selected Models: Score vs. ELO (Unified Style)', fontsize=14, fontweight='bold')
        plt.tight_layout()

        tag = '_'.join([m.replace('.', '').replace('-', '') for m in models])
        for fmt in save_format:
            path = self.output_dir / f"selected_models_score_elo_combined_{tag}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"选定模型 分数+ELO 组合雷达图已保存: {path}")

        return fig, (ax1, ax2)


def main():
    """主函数，生成所有雷达图"""
    visualizer = TopModelRadarVisualizer()
    
    try:
        print("=== 生成顶级模型雷达图 ===")
        
        # 单个综合雷达图
        print("1. 创建综合雷达图...")
        visualizer.create_single_radar_chart()
        
        # 独立雷达图
        print("2. 创建独立模型雷达图...")
        visualizer.create_individual_radar_charts()
        
        # 比较雷达图
        print("3. 创建比较雷达图...")
        visualizer.create_comparative_radar_chart()

        # 选定模型雷达图（MOSES, O3, GPT-4.1, LightRAG）
        print("4. 创建选定模型雷达图 (MOSES/O3/GPT-4.1/LightRAG)...")
        visualizer.create_selected_models_radar()
        print("5. 创建选定模型相对雷达图 (相对维度最大值=100%) ...")
        visualizer.create_selected_models_radar_relative()
        print("6. 创建选定模型ELO雷达图 (绝对/相对)...")
        visualizer.create_selected_models_elo_radar()
        visualizer.create_selected_models_elo_radar_relative()
        print("7. 创建选定模型 分数+ELO 组合雷达图...")
        visualizer.create_selected_models_score_elo_combined()
        
        print("\n所有雷达图生成完成！")
        
        # 显示图形
        plt.show()
        
    except Exception as e:
        print(f"雷达图生成出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
