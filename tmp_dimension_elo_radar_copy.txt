"""
分维度ELO雷达图可视化脚本
创建基于TrueSkill ELO评分的分维度雷达图比较
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import sqrt
try:
    from scipy import stats as spstats
except Exception:
    spstats = None
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
    style_axes,
    get_heatmap_cmap,
)
from data_processor import DataProcessor


class DimensionELORadarVisualizer:
    """分维度ELO雷达图可视化器"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/radar_charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        setup_plot_style()
    
    def create_all_models_elo_radar(self, save_format=['png', 'pdf', 'svg']):
        """
        创建包含所有模型的ELO雷达图
        """
        # 获取数据
        radar_data = self.processor.create_dimension_elo_radar_data()
        
        # 计算角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]  # 完成圆圈
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])
        
        # 为每个模型绘制雷达图
        for model_data in radar_data:
            model = model_data['model']
            scores = model_data['scores'] + [model_data['scores'][0]]  # 闭合图形
            
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            # 绘制线条和填充（统一风格）
            ax.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'] - 0.2,
                    label=display_name, color=color, alpha=0.9)
            ax.fill(angles, scores, alpha=0.15, color=color)
        
        # 设置维度标签
        dimension_labels = [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimension_labels, fontsize=12, fontweight='bold')
        
        # 动态设置径向范围
        all_scores = [data['scores'] for data in radar_data]
        flat_scores = [score for scores in all_scores for score in scores]
        min_score = min(flat_scores)
        max_score = max(flat_scores)
        
        # 设置径向标签
        ax.set_ylim(0, max_score * 1.1)
        n_ticks = 5
        tick_values = np.linspace(0, max_score, n_ticks)
        ax.set_yticks(tick_values)
        ax.set_yticklabels([f'{val:.0f}' for val in tick_values], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        
        # 设置标题
        ax.set_title('AI Models TrueSkill ELO Comparison\n(4 Dimensions Radar Chart)', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # 添加图例
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), fontsize=11, frameon=False)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"all_models_elo_radar.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"所有模型ELO雷达图已保存: {filepath}")
        
        return fig, ax
    
    def create_top_models_elo_radar(self, save_format=['png', 'pdf', 'svg']):
        """
        创建顶级模型的ELO雷达图（更清晰的版本）
        """
        # 获取数据
        radar_data = self.processor.create_dimension_elo_radar_data()
        
        # 只保留顶级模型
        top_models_data = [data for data in radar_data if data['model'] in MODEL_INFO['top_models']]
        
        # 计算角度
        N = len(DIMENSION_INFO['order'])
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.set_facecolor(COLOR_SCHEME['radar']['background'])
        
        # 为每个顶级模型绘制雷达图
        for model_data in top_models_data:
            model = model_data['model']
            scores = model_data['scores'] + [model_data['scores'][0]]
            
            color = COLOR_SCHEME['models'][model]
            display_name = model_data['display_name']
            
            # 绘制线条和填充（统一风格）
            ax.plot(angles, scores, '-', linewidth=PLOT_STYLE['line_width'] + 1,
                    label=display_name, color=color, alpha=0.95)
            ax.fill(angles, scores, alpha=0.2, color=color)
        
        # 设置维度标签
        dimension_labels = [DIMENSION_INFO['display_names'][d] for d in DIMENSION_INFO['order']]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimension_labels, fontsize=12, fontweight='bold')
        
        # 动态设置径向范围
        all_scores = [data['scores'] for data in top_models_data]
        flat_scores = [score for scores in all_scores for score in scores]
        max_score = max(flat_scores)
        
        ax.set_ylim(0, max_score * 1.1)
        n_ticks = 5
        tick_values = np.linspace(0, max_score, n_ticks)
        ax.set_yticks(tick_values)
        ax.set_yticklabels([f'{val:.0f}' for val in tick_values], fontsize=10)
        ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.5)
        
        # 设置标题
        ax.set_title('Top AI Models TrueSkill ELO Analysis\n(Multi-Dimensional Performance Comparison)', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # 添加图例
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05), fontsize=12, frameon=False)
        
        # 在雷达图上标注数值
        for model_data in top_models_data:
            for angle, score, dim in zip(angles[:-1], model_data['scores'], 
                                       [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]):
                ax.text(angle, score + max_score * 0.05, f'{score:.0f}', 
                       ha='center', va='center', fontsize=9, fontweight='bold',
                       color=COLOR_SCHEME['models'][model_data['model']])
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"top_models_elo_radar.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"顶级模型ELO雷达图已保存: {filepath}")
        
        return fig, ax
    
    def create_comparative_elo_analysis(self, save_format=['png', 'pdf']):
        """
        创建比较性ELO分析：性能分数 vs ELO评分
        """
        # 获取两种数据
        performance_data = self.processor.load_performance_scores()
        elo_radar_data = self.processor.create_dimension_elo_radar_data()
        
        # 创建图形：2x2子图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 为每个维度创建一个子图
        dimensions = DIMENSION_INFO['order']
        
        for i, dim in enumerate(dimensions):
            ax = axes[i//2, i%2]
            
            # 提取该维度的数据
            perf_scores = []
            elo_scores = []
            model_names = []
            colors = []
            
            for model in MODEL_INFO['order']:
                # 性能分数
                perf_score = performance_data[performance_data['model'] == model][dim].iloc[0]
                
                # ELO分数
                elo_data = next((data for data in elo_radar_data if data['model'] == model), None)
                if elo_data:
                    dim_idx = DIMENSION_INFO['order'].index(dim)
                    elo_score = elo_data['scores'][dim_idx]
                    
                    perf_scores.append(perf_score)
                    elo_scores.append(elo_score)
                    model_names.append(MODEL_INFO['display_names'][model])
                    colors.append(COLOR_SCHEME['models'][model])
            
            # 绘制散点图
            ax.scatter(
                perf_scores,
                elo_scores,
                c=colors,
                s=90,
                alpha=0.9,
                edgecolors='white',
                linewidth=1.0,
            )
            
            # 添加模型标签
            for j, (perf, elo, name) in enumerate(zip(perf_scores, elo_scores, model_names)):
                ax.annotate(name, (perf, elo), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8, alpha=0.8)
            
            # 添加趋势线（线性拟合）
            if len(perf_scores) >= 2:
                z = np.polyfit(perf_scores, elo_scores, 1)
                pl = np.poly1d(z)
                xs = np.linspace(min(perf_scores), max(perf_scores), 100)
                ax.plot(xs, pl(xs), "r--", alpha=0.5, linewidth=1)

            # 计算相关性（Pearson 与 Spearman）
            def safe_corrs(x, y):
                if spstats is None or len(x) < 3:
                    r = float(np.corrcoef(x, y)[0, 1]) if len(x) >= 2 else np.nan
                    return r, np.nan, np.nan, np.nan
                pr, p_pr = spstats.pearsonr(x, y)
                srho, p_srho = spstats.spearmanr(x, y)
                return float(pr), float(p_pr), float(srho), float(p_srho)

            pr, p_pr, srho, p_srho = safe_corrs(perf_scores, elo_scores)

            # 设置标签和标题（同时标注 Pearson 与 Spearman）
            ax.set_xlabel('LLM-Judge Score (0-10)', fontsize=10)
            ax.set_ylabel('TrueSkill ELO Rating', fontsize=10)
            ax.set_title(
                f"{DIMENSION_INFO['short_names'][dim]}\nPearson r={pr:.3f} (p={p_pr:.3g}) | Spearman ρ={srho:.3f} (p={p_srho:.3g})",
                fontsize=10, fontweight='bold'
            )
            style_axes(ax)
        
        # 设置总标题
        fig.suptitle('LLM-Judge Score vs TrueSkill ELO\n(Dimension-wise Correlations: Pearson + Spearman)',
                     fontsize=14, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"performance_elo_correlation.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"性能-ELO相关性分析图已保存: {filepath}")

        return fig, axes

    def create_comparative_elo_analysis_with_kendall(self, save_format=['png', 'pdf']):
        """补充版：在相关性图上同时标注 Kendall τ（与 Pearson、Spearman 一起）。"""
        if spstats is None:
            print('SciPy 未安装，无法计算 Kendall τ；请先安装 scipy。')
            return self.create_comparative_elo_analysis(save_format=save_format)

        performance_data = self.processor.load_performance_scores()
        elo_radar_data = self.processor.create_dimension_elo_radar_data()

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        dimensions = DIMENSION_INFO['order']

        for i, dim in enumerate(dimensions):
            ax = axes[i//2, i%2]
            perf_scores, elo_scores, model_names, colors = [], [], [], []
            for model in MODEL_INFO['order']:
                if model in performance_data['model'].values:
                    perf_score = performance_data[performance_data['model'] == model][dim].iloc[0]
                    elo_data = next((d for d in elo_radar_data if d['model'] == model), None)
                    if elo_data:
                        dim_idx = DIMENSION_INFO['order'].index(dim)
                        elo_score = elo_data['scores'][dim_idx]
                        perf_scores.append(perf_score)
                        elo_scores.append(elo_score)
                        model_names.append(MODEL_INFO['display_names'][model])
                        colors.append(COLOR_SCHEME['models'][model])

            ax.scatter(perf_scores, elo_scores, c=colors, s=100, alpha=0.85, edgecolors='white', linewidth=1)
            if len(perf_scores) >= 2:
                z = np.polyfit(perf_scores, elo_scores, 1)
                pl = np.poly1d(z)
                xs = np.linspace(min(perf_scores), max(perf_scores), 100)
                ax.plot(xs, pl(xs), 'r--', alpha=0.5, linewidth=1)

            pr, p_pr = spstats.pearsonr(perf_scores, elo_scores)
            srho, p_srho = spstats.spearmanr(perf_scores, elo_scores)
            ktau, p_tau = spstats.kendalltau(perf_scores, elo_scores)

            ax.set_xlabel('LLM-Judge Score (0-10)', fontsize=10)
            ax.set_ylabel('TrueSkill ELO Rating', fontsize=10)
            ax.set_title(
                f"{DIMENSION_INFO['short_names'][dim]}\nPearson r={pr:.3f} (p={p_pr:.3g}) | Spearman ρ={srho:.3f} (p={p_srho:.3g}) | Kendall τ={ktau:.3f} (p={p_tau:.3g})",
                fontsize=9, fontweight='bold'
            )

        fig.suptitle('LLM-Judge Score vs TrueSkill ELO\n(Pearson + Spearman + Kendall τ, per Dimension)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        for fmt in save_format:
            filepath = self.output_dir / f"performance_elo_correlation_kendall.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"性能-ELO相关性分析图（含 Kendall τ）已保存: {filepath}")

        return fig, axes
    
    def create_dimension_ranking_comparison(self, save_format=['png', 'pdf']):
        """
        创建各维度排名比较图
        """
        # 获取数据
        radar_data = self.processor.create_dimension_elo_radar_data()
        
        # 为每个维度创建排名
        rankings_by_dimension = {}
        for i, dim in enumerate(DIMENSION_INFO['order']):
            scores = [(data['model'], data['scores'][i], data['display_name']) 
                     for data in radar_data]
            scores.sort(key=lambda x: x[1], reverse=True)
            rankings_by_dimension[dim] = scores
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # 创建排名矩阵
        models = MODEL_INFO['order']
        dimensions = DIMENSION_INFO['order']
        ranking_matrix = np.zeros((len(models), len(dimensions)))
        
        for j, dim in enumerate(dimensions):
            for rank, (model, score, _) in enumerate(rankings_by_dimension[dim]):
                model_idx = models.index(model)
                ranking_matrix[model_idx, j] = rank + 1  # 排名从1开始
        
        # 创建热图
        # 排名数值小更好，因此使用反向色图：rank=1 为深色
        im = ax.imshow(ranking_matrix, cmap=get_heatmap_cmap(reverse=True), aspect='auto', vmin=1, vmax=len(models))
        
        # 设置刻度标签
        ax.set_xticks(range(len(dimensions)))
        ax.set_xticklabels([DIMENSION_INFO['short_names'][d] for d in dimensions], 
                          fontsize=12)
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels([MODEL_INFO['display_names'][m] for m in models], 
                          fontsize=11)
        
        # 添加数值标注
        for i in range(len(models)):
            for j in range(len(dimensions)):
                rank = int(ranking_matrix[i, j])
                ax.text(j, i, str(rank), ha='center', va='center', 
                       fontsize=12, fontweight='bold', 
                       color='white' if rank <= 5 else 'black')
        
        # 设置标题
        ax.set_title('AI Model Rankings by Dimension\n(TrueSkill ELO Rankings, 1=Best)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # 添加颜色条
        cbar = fig.colorbar(im, ax=ax, shrink=0.6)
        cbar.set_label('Ranking Position', rotation=270, labelpad=20)
        style_axes(ax)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"dimension_ranking_heatmap.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"维度排名比较图已保存: {filepath}")
        
        return fig, ax


def main():
    """主函数，生成所有维度ELO雷达图"""
    visualizer = DimensionELORadarVisualizer()
    
    try:
        print("=== 生成分维度ELO雷达图 ===")
        
        # 所有模型ELO雷达图
        print("1. 创建所有模型ELO雷达图...")
        visualizer.create_all_models_elo_radar()
        
        # 顶级模型ELO雷达图
        print("2. 创建顶级模型ELO雷达图...")
        visualizer.create_top_models_elo_radar()
        
        # 比较分析
        print("3. 创建性能-ELO相关性分析...")
        visualizer.create_comparative_elo_analysis()
        
        # 排名比较
        print("4. 创建维度排名比较图...")
        visualizer.create_dimension_ranking_comparison()
        
        print("\n所有分维度ELO雷达图生成完成！")
        
        # 显示图形
        plt.show()
        
    except Exception as e:
        print(f"分维度ELO雷达图生成出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
