"""
评分分布小提琴图与评分森林图
数据来源: analysis_results.json -> question_volatility/Doubao-Seed-1.6-combined
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys
import os

# 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_processing'))

from vis_config import COLOR_SCHEME, MODEL_INFO, PLOT_STYLE, setup_plot_style, style_axes

# 全局缓存，避免重复解析巨大的 individual JSON
_GLOBAL_SCORE_DF = None
_GLOBAL_SCORE_STATS = None
from data_processor import DataProcessor


class ScoreViolinAndForestVisualizer:
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/score_plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        setup_plot_style()
        # 只加载一次原始数据，避免重复解析大JSON
        global _GLOBAL_SCORE_DF, _GLOBAL_SCORE_STATS
        try:
            if _GLOBAL_SCORE_DF is None:
                _GLOBAL_SCORE_DF = self.processor.create_score_distribution_df()
            self.df = _GLOBAL_SCORE_DF
        except Exception:
            self.df = None
        try:
            if _GLOBAL_SCORE_STATS is None:
                _GLOBAL_SCORE_STATS = self.processor.create_score_forest_data(ci_mult=3.0)
            self.stats = _GLOBAL_SCORE_STATS
        except Exception:
            self.stats = None

    def create_violin_plot(self, judge: str = 'Doubao-Seed-1.6-combined', save_format=['png', 'pdf', 'svg']):
        """按模型的题目评分分布小提琴图（与参考图风格一致）。"""
        df = self.df if self.df is not None else self.processor.create_score_distribution_df(judge)
        # 按预设模型顺序排序显示名
        df['display_name'] = df['model'].map(MODEL_INFO['display_names'])
        order = [MODEL_INFO['display_names'][m] for m in MODEL_INFO['order'] if m in df['model'].unique()]
        # 颜色映射基于显示名，避免 seaborn palette 警告
        display_palette = {MODEL_INFO['display_names'][m]: COLOR_SCHEME['models'][m] for m in MODEL_INFO['order'] if m in df['model'].unique()}

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.violinplot(
            data=df,
            x='display_name', y='score',
            order=order,
            hue='display_name',  # 为了使用调色板映射颜色
            palette=display_palette,
            dodge=False, legend=False,
            cut=0, inner='quartile', linewidth=1.2, ax=ax
        )
        # 参考图风格：上方轻微虚线网格、x标签倾斜
        ax.set_xlabel('AI Models', fontsize=12, fontweight='bold')
        ax.set_ylabel('LLM-Judge Score (0–10)', fontsize=12, fontweight='bold')
        ax.set_ylim(0, 10)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha='right')
        ax.set_title('LLM-Judge Scores by Model\n(Doubao-Seed-1.6, Distribution across Questions)', fontsize=14, fontweight='bold')
        style_axes(ax)
        ax.grid(axis='y', alpha=0.35)

        for fmt in save_format:
            path = self.output_dir / f"score_violin.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"评分小提琴图已保存: {path}")
        return fig, ax

    def create_score_forest(self, judge: str = 'Doubao-Seed-1.6-combined', save_format=['png', 'pdf', 'svg'], orientation='vertical'):
        """评分均值+95%CI 的森林图（非ELO）。默认纵向。"""
        stats = self.stats if self.stats is not None else self.processor.create_score_forest_data(judge, ci_mult=3.0)
        if orientation == 'vertical':
            fig, ax = plt.subplots(figsize=(12, 7))
            x = np.arange(len(stats))
            for i, row in enumerate(stats.itertuples(index=False)):
                color = COLOR_SCHEME['models'][row.model]
                ax.errorbar(
                    i, row.mean,
                    yerr=[[row.mean - row.lower], [row.upper - row.mean]],
                    fmt='o', color='#4D4D4D', ecolor='#4D4D4D', elinewidth=1.8, capsize=4, capthick=1.8,
                    markersize=PLOT_STYLE['marker_size'] + 2,
                    markerfacecolor=color, markeredgecolor='white', markeredgewidth=1.0,
                )
                # 标准格式：mean [lower, upper]
                ax.text(
                    i,
                    row.upper + 0.12,
                    f"{row.mean:.2f} [{row.lower:.2f}, {row.upper:.2f}]",
                    ha='center', va='bottom', fontsize=9, fontweight='bold'
                )
            ax.set_xticks(x)
            ax.set_xticklabels(stats['display_name'], rotation=20, ha='right')
            ax.set_ylabel('LLM-Judge Score (Mean ± 3·SE)')
            # 保存两套：全范围0–10与放大4–9
            ax.set_ylim(0, 10)
            ax.set_title('Model Scores Forest Plot (Non-ELO)', fontsize=14, fontweight='bold')
            style_axes(ax)
            ax.grid(axis='y', alpha=0.35)
        else:
            fig, ax = plt.subplots(figsize=(12, 7))
            y = np.arange(len(stats))
            for i, row in enumerate(stats.itertuples(index=False)):
                color = COLOR_SCHEME['models'][row.model]
                ax.errorbar(
                    row.mean, i,
                    xerr=[[row.mean - row.lower], [row.upper - row.mean]],
                    fmt='o', color='#4D4D4D', ecolor='#4D4D4D', elinewidth=1.8, capsize=4, capthick=1.8,
                    markersize=PLOT_STYLE['marker_size'] + 2,
                    markerfacecolor=color, markeredgecolor='white', markeredgewidth=1.0,
                )
                ax.text(
                    row.upper + 0.08,
                    i,
                    f"{row.mean:.2f} [{row.lower:.2f}, {row.upper:.2f}]",
                    va='center', fontsize=9, fontweight='bold'
                )
            ax.set_yticks(y)
            ax.set_yticklabels(stats['display_name'])
            ax.set_xlabel('LLM-Judge Score (Mean ± 3·SE)')
            # 保存两套：全范围0–10与放大4–9
            ax.set_xlim(0, 10)
            ax.set_title('Model Scores Forest Plot (Non-ELO)', fontsize=14, fontweight='bold')
            style_axes(ax)
            ax.grid(axis='x', alpha=0.35)
            ax.invert_yaxis()

        # 保存全范围版本（0–10）
        for fmt in save_format:
            suffix = 'vertical' if orientation == 'vertical' else 'horizontal'
            path = self.output_dir / f"score_forest_{suffix}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"评分森林图已保存: {path}")

        # 保存放大版（4–9）
        if orientation == 'vertical':
            ax.set_ylim(4, 9)
        else:
            ax.set_xlim(4, 9)
        for fmt in save_format:
            suffix = 'vertical_zoomed' if orientation == 'vertical' else 'horizontal_zoomed'
            path = self.output_dir / f"score_forest_{suffix}.{fmt}"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"评分森林图已保存: {path}")
        return fig, ax


def main():
    viz = ScoreViolinAndForestVisualizer()
    try:
        print('=== 生成评分小提琴图与评分森林图 ===')
        viz.create_violin_plot()
        viz.create_score_forest(orientation='vertical')
        viz.create_score_forest(orientation='horizontal')
        print('\n生成完成！')
        plt.show()
    except Exception as e:
        print(f"评分图生成出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
