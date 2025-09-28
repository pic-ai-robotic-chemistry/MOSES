"""
ELO森林图可视化脚本
创建TrueSkill ELO评分的森林图展示
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

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
)
from data_processor import DataProcessor
try:
    from scipy.cluster.hierarchy import linkage, fcluster
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False
import numpy as np


class ELOForestPlotVisualizer:
    """ELO森林图可视化器"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/forest_plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        setup_plot_style()
    
    def create_overall_elo_forest_plot(self, save_format=['png', 'pdf', 'svg'], orientation: str = 'both'):
        """
        创建整体ELO评分的森林图
        orientation: 'horizontal'（默认）或 'vertical'（与示例图一致）
        """
        # 获取数据
        forest_data = self.processor.create_forest_plot_data()
        
        def _plot_vertical():
            fig, ax = plt.subplots(figsize=(12, 8))
            # 垂直式：x为模型类别，y为评分，竖向误差条
            x_pos = np.arange(len(forest_data))
            for i, (_, row) in enumerate(forest_data.iterrows()):
                color = COLOR_SCHEME['models'][row['model']]
                ax.errorbar(
                    x_pos[i],
                    row['elo_rating'],
                    yerr=[[row['elo_rating'] - row['elo_lower']], [row['elo_upper'] - row['elo_rating']]],
                    fmt='o',
                    color='#4D4D4D',
                    ecolor='#4D4D4D',
                    elinewidth=1.8,
                    capsize=4,
                    capthick=1.8,
                    markersize=PLOT_STYLE['marker_size'] + 2,
                    markerfacecolor=color,
                    markeredgecolor='white',
                    markeredgewidth=1.0,
                    alpha=0.95,
                )
                # 顶部标注
                ax.text(
                    x_pos[i],
                    row['elo_upper'] + 0.6,
                    f"{row['elo_rating']:.1f}",
                    ha='center',
                    va='bottom',
                    fontsize=10,
                    fontweight='bold',
                )

            ax.set_xticks(x_pos)
            ax.set_xticklabels(forest_data['display_name'], rotation=30, ha='right', fontsize=12)
            ax.set_ylabel('TrueSkill ELO (μ ± 3σ)', fontsize=12, fontweight='bold')
            ymin = max(0, forest_data['elo_lower'].min() - 1)
            ax.set_ylim(ymin, forest_data['elo_upper'].max() + 4)
            ax.set_title(
                'AI Model TrueSkill ELO Rankings\n(99.7% CI, Vertical Forest Plot)',
                fontsize=14,
                fontweight='bold',
                pad=20,
            )
            # 水平参考线（均值）
            mean_elo = forest_data['elo_rating'].mean()
            ax.axhline(mean_elo, color='#9E9E9E', linestyle=(0, (3, 3)), alpha=0.8, linewidth=1.2)
            ax.text(
                len(forest_data) - 0.5,
                mean_elo,
                f'Mean: {mean_elo:.1f}',
                ha='right',
                va='bottom',
                fontsize=10,
                style='italic',
            )
            style_axes(ax)
            ax.grid(axis='y', alpha=0.35)
            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_forest_plot_vertical.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"ELO森林图已保存: {filepath}")
            return fig, ax

        def _plot_horizontal():
            fig, ax = plt.subplots(figsize=(12, 8))
            # 水平式（原有逻辑）
            y_pos = np.arange(len(forest_data))
            for i, (_, row) in enumerate(forest_data.iterrows()):
                model = row['model']
                color = COLOR_SCHEME['models'][model]
                ax.errorbar(
                    row['elo_rating'],
                    y_pos[i],
                    xerr=[[row['elo_rating'] - row['elo_lower']], [row['elo_upper'] - row['elo_rating']]],
                    fmt='o',
                    color='#4D4D4D',  # 误差线统一深灰
                    ecolor='#4D4D4D',
                    elinewidth=1.8,
                    capsize=4,
                    capthick=1.8,
                    markersize=PLOT_STYLE['marker_size'] + 2,
                    markerfacecolor=color,
                    markeredgecolor='white',
                    markeredgewidth=1.0,
                    alpha=0.9,
                )
                ax.text(
                    row['elo_upper'] + 1.0,
                    y_pos[i],
                    f"{row['elo_rating']:.1f} [{row['elo_lower']:.1f}, {row['elo_upper']:.1f}]",
                    va='center',
                    fontsize=10,
                    fontweight='bold',
                )

            ax.set_yticks(y_pos)
            ax.set_yticklabels(forest_data['display_name'], fontsize=12)
            ax.set_xlabel('TrueSkill ELO (μ ± 3σ)', fontsize=12, fontweight='bold')
            ax.set_xlim(forest_data['elo_lower'].min() - 2, forest_data['elo_upper'].max() + 10)
            ax.set_title(
                'AI Model TrueSkill ELO Rankings\n(4 Dimensions, Forest Plot with 99.7% Confidence Intervals)',
                fontsize=14,
                fontweight='bold',
                pad=20,
            )
            mean_elo = forest_data['elo_rating'].mean()
            ax.axvline(mean_elo, color='#9E9E9E', linestyle=(0, (3, 3)), alpha=0.8, linewidth=1.2)
            ax.text(mean_elo, len(forest_data), f'Mean: {mean_elo:.1f}', ha='center', va='bottom', fontsize=10, style='italic')
            style_axes(ax)
            ax.grid(axis='x', alpha=0.35)
            ax.set_axisbelow(True)
            ax.invert_yaxis()

            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_forest_plot_horizontal.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"ELO森林图已保存: {filepath}")
            return fig, ax

        if orientation == 'vertical':
            return _plot_vertical()
        elif orientation == 'horizontal':
            return _plot_horizontal()
        else:
            _plot_horizontal()
            return _plot_vertical()
    
    def create_tiered_elo_forest_plot(self, save_format=['png', 'pdf'], orientation: str = 'both', style: str = 'band'):
        """
        创建分层的ELO森林图，按性能梯队分组。
        style: 'band' 使用淡色背景带表示梯队，点颜色保持模型色；
               'point_by_tier' 使用梯队颜色绘制点（旧样式）。
        """
        # 获取数据
        forest_data = self.processor.create_forest_plot_data()
        
        # 定义性能梯队
        def get_tier(elo_rating):
            if elo_rating >= 30:
                return "Elite (ELO ≥ 30)"
            elif elo_rating >= 25:
                return "Advanced (25 ≤ ELO < 30)"
            elif elo_rating >= 20:
                return "Intermediate (20 ≤ ELO < 25)"
            else:
                return "Basic (ELO < 20)"
        
        forest_data['tier'] = forest_data['elo_rating'].apply(get_tier)
        
        # 为不同梯队定义背景色（淡色）与边框色
        tier_colors = {
            "Elite (ELO ≥ 30)": '#FDEDEC',
            "Advanced (25 ≤ ELO < 30)": '#E8F4FD',
            "Intermediate (20 ≤ ELO < 25)": '#EEF7EE',
            "Basic (ELO < 20)": '#FFF6D9'
        }
        
        def _plot_horizontal():
            fig, ax = plt.subplots(figsize=(14, 10))
            y_position = 0
            for tier in ["Elite (ELO ≥ 30)", "Advanced (25 ≤ ELO < 30)", 
                        "Intermediate (20 ≤ ELO < 25)", "Basic (ELO < 20)"]:
                tier_data = forest_data[forest_data['tier'] == tier].sort_values('elo_rating', ascending=False)
                if len(tier_data) > 0:
                    # 背景带（横向）
                    if style == 'band':
                        ax.axhspan(y_position - 0.5, y_position + len(tier_data) - 0.5, color=tier_colors[tier], alpha=0.5, zorder=0)
                    ax.text(-2, y_position - 0.3, tier, fontweight='bold', fontsize=12, color='#555555')
                    for _, row in tier_data.iterrows():
                        ax.errorbar(
                            row['elo_rating'],
                            y_position,
                            xerr=[[row['elo_rating'] - row['elo_lower']], [row['elo_upper'] - row['elo_rating']]],
                            fmt='o', color='#4D4D4D', markersize=10, capsize=5, capthick=2, linewidth=2, alpha=0.9,
                            ecolor='#4D4D4D',
                            markerfacecolor=(COLOR_SCHEME['models'][row['model']] if style == 'band' else '#888888'),
                            markeredgecolor='white', markeredgewidth=1.0,
                        )
                        ax.text(-1, y_position, row['display_name'], ha='right', va='center', fontsize=11, fontweight='bold')
                        ax.text(row['elo_upper'] + 0.5, y_position, f"{row['elo_rating']:.1f}", va='center', fontsize=10, fontweight='bold')
                        y_position += 1
                    y_position += 0.5
            ax.set_xlim(-3, forest_data['elo_upper'].max() + 5)
            ax.set_ylim(-1, y_position)
            ax.set_xlabel('TrueSkill ELO Rating (μ - 3σ)', fontsize=12, fontweight='bold')
            ax.set_yticks([])
            ax.set_title('AI Model Performance Tiers\n(TrueSkill ELO Forest Plot by Performance Level)', fontsize=14, fontweight='bold', pad=20)
            for threshold in [20, 25, 30]:
                ax.axvline(threshold, color='#BDBDBD', linestyle=(0, (2, 2)), alpha=0.7, linewidth=1)
                ax.text(threshold, y_position - 0.5, f'{threshold}', ha='center', va='top', fontsize=9, style='italic')
            style_axes(ax)
            ax.grid(axis='x', alpha=0.35)
            ax.set_axisbelow(True)
            ax.invert_yaxis()
            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_tiered_forest_plot_horizontal.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"分层ELO森林图已保存: {filepath}")
            return fig, ax

        def _plot_vertical():
            ordered = []
            for tier in ["Elite (ELO ≥ 30)", "Advanced (25 ≤ ELO < 30)", 
                        "Intermediate (20 ≤ ELO < 25)", "Basic (ELO < 20)"]:
                tdf = forest_data[forest_data['tier'] == tier].sort_values('elo_rating', ascending=False)
                if len(tdf) > 0:
                    for _, r in tdf.iterrows():
                        ordered.append((tier, r))
            fig, ax = plt.subplots(figsize=(14, 10))
            for i, (tier, row) in enumerate(ordered):
                # 背景带（纵向，按x分类位置画竖带）
                if style == 'band':
                    ax.axvspan(i - 0.5, i + 0.5, color=tier_colors[tier], alpha=0.5, zorder=0)
                ax.errorbar(
                    i, row['elo_rating'],
                    yerr=[[row['elo_rating'] - row['elo_lower']], [row['elo_upper'] - row['elo_rating']]],
                    fmt='o', color='#4D4D4D', ecolor='#4D4D4D', elinewidth=1.8, capsize=4, capthick=1.8,
                    markersize=PLOT_STYLE['marker_size'] + 2,
                    markerfacecolor=(COLOR_SCHEME['models'][row['model']] if style == 'band' else '#888888'),
                    markeredgecolor='white', markeredgewidth=1.0,
                )
                ax.text(i, row['elo_upper'] + 0.6, f"{row['elo_rating']:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.set_xticks(range(len(ordered)))
            ax.set_xticklabels([r['display_name'] for _, r in ordered], rotation=30, ha='right', fontsize=11)
            ax.set_ylabel('TrueSkill ELO (μ ± 3σ)', fontsize=12, fontweight='bold')
            ax.set_title('AI Model Performance Tiers\n(Vertical Forest Plot by Level)', fontsize=14, fontweight='bold', pad=20)
            mean_elo = forest_data['elo_rating'].mean()
            ax.axhline(mean_elo, color='#9E9E9E', linestyle=(0, (3, 3)), alpha=0.8, linewidth=1.2)
            style_axes(ax)
            ax.grid(axis='y', alpha=0.35)
            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_tiered_forest_plot_vertical.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"分层ELO森林图已保存: {filepath}")
            return fig, ax

    def create_clustered_elo_forest_plot(self, save_format=['png', 'pdf'], n_clusters: int | None = None, orientation: str = 'vertical'):
        """基于分维度 ELO 的分层聚类对模型分组，并在森林图中用淡色背景带和分割线表示分组。
        - 点颜色保持模型配色
        - linkage: Ward（若无 SciPy，回退到 PC1 分位数分组）
        - n_clusters=None 时自动从2..min(10,n)中选择 silhouette 最优的K
        """
        # 准备数据：使用分维度ELO
        dim_data = self.processor.create_dimension_elo_radar_data()
        models = [d['model'] for d in dim_data]
        X = np.array([d['scores'] for d in dim_data], dtype=float)
        # 标准化
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

        # 计算 silhouette 辅助函数
        def _silhouette_score(data, labs):
            n = data.shape[0]
            if n <= 2 or len(set(labs)) < 2:
                return 0.0
            D = np.sqrt(((data[:, None, :] - data[None, :, :]) ** 2).sum(axis=2))
            scores = []
            for i in range(n):
                same = (labs == labs[i])
                same_idx = np.where(same)[0]
                if len(same_idx) <= 1:
                    a = 0.0
                else:
                    a = D[i, same_idx[same_idx != i]].mean()
                b = np.inf
                for c in set(labs[~same]):
                    c_idx = np.where(labs == c)[0]
                    b = min(b, D[i, c_idx].mean())
                s = 0.0 if (a == 0 and b == 0) else (b - a) / max(a, b)
                scores.append(s)
            return float(np.mean(scores))

        # 选择聚类方法与K
        method_used = 'PC1-quantile'
        Z = None
        if _HAVE_SCIPY and len(models) >= 2:
            Z = linkage(X, method='ward')
            method_used = 'WARD'

        if n_clusters is None:
            candidate_ks = [k for k in range(2, min(10, len(models)) + 1)]
            best_score, best_k, best_labels = -1, None, None
            for k in candidate_ks:
                if Z is not None:
                    labs = fcluster(Z, k, criterion='maxclust')
                else:
                    pc1 = X @ np.linalg.svd(X, full_matrices=False)[2][0]
                    qs = np.quantile(pc1, np.linspace(0, 1, k + 1))
                    labs = np.digitize(pc1, qs[1:-1]) + 1
                score = _silhouette_score(X, labs)
                if score > best_score:
                    best_score, best_k, best_labels = score, k, labs
            n_clusters = best_k
            labels = best_labels
            print(f"[Cluster] method={method_used}, auto_k={n_clusters}, silhouette={best_score:.3f}")
        else:
            if Z is not None and len(models) >= n_clusters:
                labels = fcluster(Z, n_clusters, criterion='maxclust')
            else:
                pc1 = X @ np.linalg.svd(X, full_matrices=False)[2][0]
                qs = np.quantile(pc1, np.linspace(0, 1, n_clusters + 1))
                labels = np.digitize(pc1, qs[1:-1]) + 1
            score = _silhouette_score(X, labels)
            print(f"[Cluster] method={method_used}, k={n_clusters}, silhouette={score:.3f}")

        # 计算整体ELO排序（固定为整体 ELO 从高到低）
        overall = self.processor.create_forest_plot_data()
        overall = overall.set_index('model')
        order = sorted(models, key=lambda m: overall.loc[m, 'elo_rating'] if m in overall.index else -1, reverse=True)

        # 记录每个模型的簇标签（绘制背景带时用）
        label_map = {m: int(l) for m, l in zip(models, labels)}

        # 绘制（仅实现纵向，保证简洁）
        fig, ax = plt.subplots(figsize=(14, 10))
        # 背景带 + 分割线（沿着 ELO 降序顺序迭代，簇变化处画带和分隔线）
        x_idx = np.arange(len(order))
        if order:
            current = label_map.get(order[0], None)
            start = 0
            for i in range(1, len(order) + 1):
                lab = label_map.get(order[i], None) if i < len(order) else None
                if lab != current:
                    if current is not None:
                        ax.axvspan(start - 0.5, i - 0.5, color=f"C{(current-1)%10}", alpha=0.08, zorder=0)
                        ax.axvline(i - 0.5, color='#BBBBBB', linestyle=':', linewidth=1)
                    start = i
                    current = lab

        # 点与误差
        for i, m in enumerate(order):
            if m not in overall.index:
                continue
            row = overall.loc[m]
            color = COLOR_SCHEME['models'].get(m, '#4D4D4D')
            ax.errorbar(i, row['elo_rating'],
                        yerr=[[row['elo_rating'] - row['elo_lower']], [row['elo_upper'] - row['elo_rating']]],
                        fmt='o', color='#4D4D4D', ecolor='#4D4D4D', elinewidth=1.6, capsize=4, capthick=1.6,
                        markersize=PLOT_STYLE['marker_size'] + 2, markerfacecolor=color, markeredgecolor='white', markeredgewidth=1.0)
            # 标注 mu [lower, upper]
            ax.text(i, row['elo_upper'] + 0.6, f"{row['elo_mu']:.2f} [{row['elo_lower']:.2f}, {row['elo_upper']:.2f}]",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_xticks(x_idx)
        ax.set_xticklabels([MODEL_INFO['display_names'][m] for m in order], rotation=30, ha='right', fontsize=11)
        ax.set_ylabel('TrueSkill ELO (μ ± 3σ)', fontsize=12, fontweight='bold')
        ax.set_title('AI Model ELO (Clustered by dimension ratings)\n(Bands denote clusters; point colors=model palette)', fontsize=14, fontweight='bold', pad=20)
        style_axes(ax)
        ax.grid(axis='y', alpha=0.35)
        plt.tight_layout()
        for fmt in save_format:
            path = self.output_dir / f"elo_clustered_forest_plot_vertical.{fmt}"
            fig.savefig(path, dpi=300, bbox_inches='tight')
            print(f"聚类ELO森林图已保存: {path}")
        return fig, ax

        if orientation == 'vertical':
            return _plot_vertical()
        elif orientation == 'horizontal':
            return _plot_horizontal()
        else:
            _plot_horizontal()
            return _plot_vertical()
    
    def create_elo_uncertainty_analysis(self, save_format=['png', 'pdf'], orientation: str = 'both'):
        """
        创建ELO不确定性分析图
        """
        # 获取数据
        forest_data = self.processor.create_forest_plot_data()
        
        # 计算不确定性指标
        forest_data['uncertainty'] = forest_data['elo_upper'] - forest_data['elo_lower']
        forest_data['relative_uncertainty'] = forest_data['uncertainty'] / forest_data['elo_rating']
        
        def _plot_horizontal():
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 左侧：ELO评分 vs 不确定性
            for _, row in forest_data.iterrows():
                model = row['model']
                color = COLOR_SCHEME['models'][model]
                ax1.scatter(
                    row['elo_rating'],
                    row['uncertainty'],
                    color=color,
                    s=90,
                    alpha=0.9,
                    edgecolors='white',
                    linewidth=1.0,
                )
                ax1.text(
                    row['elo_rating'],
                    row['uncertainty'] + 0.1,
                    row['display_name'],
                    ha='center',
                    va='bottom',
                    fontsize=9,
                )
            ax1.set_xlabel('ELO Rating', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Uncertainty (CI Width)', fontsize=12, fontweight='bold')
            ax1.set_title('ELO Rating vs. Uncertainty', fontsize=12, fontweight='bold')
            style_axes(ax1)

            # 右侧：森林图风格的不确定性展示
            y_pos = np.arange(len(forest_data))
            forest_sorted = forest_data.sort_values('uncertainty', ascending=True)
            for i, (_, row) in enumerate(forest_sorted.iterrows()):
                model = row['model']
                color = COLOR_SCHEME['models'][model]
                ax2.barh(i, row['uncertainty'], color=color, alpha=0.6, height=0.6, edgecolor='white')
                ax2.text(
                    row['uncertainty'] + 0.1,
                    i,
                    f"{row['uncertainty']:.1f}",
                    va='center',
                    fontsize=10,
                    fontweight='bold',
                )
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(forest_sorted['display_name'], fontsize=11)
            ax2.set_xlabel('Uncertainty (99.7% CI Width)', fontsize=12, fontweight='bold')
            ax2.set_title('Model Ranking Uncertainty', fontsize=12, fontweight='bold')
            style_axes(ax2)
            ax2.grid(axis='x', alpha=0.35)

            # 设置总标题
            fig.suptitle('TrueSkill ELO Uncertainty Analysis\n(Model Performance Confidence Assessment)', fontsize=14, fontweight='bold')
            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_uncertainty_analysis_horizontal.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"ELO不确定性分析图已保存: {filepath}")
            return fig, (ax1, ax2)

        def _plot_vertical():
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            for _, row in forest_data.iterrows():
                color = COLOR_SCHEME['models'][row['model']]
                ax1.scatter(row['elo_rating'], row['uncertainty'], color=color, s=90, alpha=0.9, edgecolors='white', linewidth=1.0)
                ax1.text(row['elo_rating'], row['uncertainty'] + 0.1, row['display_name'], ha='center', va='bottom', fontsize=9)
            ax1.set_xlabel('ELO Rating', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Uncertainty (CI Width)', fontsize=12, fontweight='bold')
            ax1.set_title('ELO Rating vs. Uncertainty', fontsize=12, fontweight='bold')
            style_axes(ax1)
            forest_sorted_v = forest_data.sort_values('uncertainty', ascending=False)
            x_pos = np.arange(len(forest_sorted_v))
            ax2.bar(x_pos, forest_sorted_v['uncertainty'], color=[COLOR_SCHEME['models'][m] for m in forest_sorted_v['model']], alpha=0.7, edgecolor='white')
            for i, (_, row) in enumerate(forest_sorted_v.iterrows()):
                ax2.text(i, row['uncertainty'] + 0.1, f"{row['uncertainty']:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(forest_sorted_v['display_name'], rotation=30, ha='right', fontsize=10)
            ax2.set_ylabel('Uncertainty (99.7% CI Width)', fontsize=12, fontweight='bold')
            ax2.set_title('Model Ranking Uncertainty', fontsize=12, fontweight='bold')
            style_axes(ax2)
            fig.suptitle('TrueSkill ELO Uncertainty Analysis\n(Model Performance Confidence Assessment)', fontsize=14, fontweight='bold')
            plt.tight_layout()
            for fmt in save_format:
                filepath = self.output_dir / f"elo_uncertainty_analysis_vertical.{fmt}"
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"ELO不确定性分析图已保存: {filepath}")
            return fig, (ax1, ax2)

        if orientation == 'vertical':
            return _plot_vertical()
        elif orientation == 'horizontal':
            return _plot_horizontal()
        else:
            _plot_horizontal()
            return _plot_vertical()


def main():
    """主函数，生成所有森林图"""
    visualizer = ELOForestPlotVisualizer()
    
    try:
        print("=== 生成ELO森林图 ===")
        
        # 基础森林图
        print("1. 创建整体ELO森林图 (水平+垂直)...")
        visualizer.create_overall_elo_forest_plot(orientation='both')
        
        # 分层森林图
        print("2. 创建分层ELO森林图 (水平+垂直)...")
        visualizer.create_tiered_elo_forest_plot(orientation='both')
        
        # 不确定性分析
        print("3. 创建ELO不确定性分析图 (水平+垂直)...")
        visualizer.create_elo_uncertainty_analysis(orientation='both')
        
        # 聚类ELO森林图
        print("4. 创建聚类ELO森林图 (Ward聚类/回退PC1分组)...")
        visualizer.create_clustered_elo_forest_plot()
        
        print("\n所有ELO森林图生成完成！")
        
        # 显示图形
        plt.show()
        
    except Exception as e:
        print(f"ELO森林图生成出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
