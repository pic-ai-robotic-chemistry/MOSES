"""
Supplementary correlation figures:
- Dimension-wise: LLM-Judge scores vs overall TrueSkill ELO (rep20 JSON, same as forest plot)
- Two variants: (1) Pearson+Spearman; (2) Pearson+Spearman+Kendall
With an improved, elegant legend mapping point styles to model names.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys
import os

# Import config and data processor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_processing'))

from vis_config import (
    COLOR_SCHEME,
    MODEL_INFO,
    DIMENSION_INFO,
    PLOT_STYLE,
    setup_plot_style,
    style_axes,
    MARKER_SCHEME,
)
from data_processor import DataProcessor

try:
    from scipy import stats as spstats
except Exception:
    spstats = None


class SupplementCorrelationVisualizer:
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/supplement_figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        setup_plot_style()

    def _build_model_legend(self):
        import matplotlib.lines as mlines
        handles, labels = [], []
        for m in MODEL_INFO['order']:
            if m not in COLOR_SCHEME['models']:
                continue
            handle = mlines.Line2D([], [],
                                   color=COLOR_SCHEME['models'][m],
                                   marker=MARKER_SCHEME['models'].get(m, 'o'),
                                   linestyle='None', markersize=8,
                                   markeredgecolor='white', markeredgewidth=0.8)
            handles.append(handle)
            labels.append(MODEL_INFO['display_names'].get(m, m))
        return handles, labels

    def _collect_xy(self, dim: str):
        perf_df = self.processor.load_performance_scores()
        forest_df = self.processor.create_forest_plot_data()  # overall elo (rep20)
        elo_map = {m: r for m, r in zip(forest_df['model'], forest_df['elo_rating'])}
        xs, ys, models = [], [], []
        for m in MODEL_INFO['order']:
            if m not in perf_df['model'].values or m not in elo_map:
                continue
            perf = float(perf_df[perf_df['model'] == m][dim].iloc[0])
            elo = float(elo_map[m])
            xs.append(perf)
            ys.append(elo)
            models.append(m)
        return xs, ys, models

    def create_perf_vs_overall_elo_corr(self, save_format=['png', 'pdf']):
        """Pearson + Spearman; legend shows model mapping (color+marker)."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        dims = DIMENSION_INFO['order']
        legend_handles, legend_labels = self._build_model_legend()

        for i, dim in enumerate(dims):
            ax = axes[i // 2, i % 2]
            xs, ys, models = self._collect_xy(dim)
            # scatter with per-model markers
            for x, y, m in zip(xs, ys, models):
                ax.scatter([x], [y],
                           color=COLOR_SCHEME['models'][m],
                           marker=MARKER_SCHEME['models'].get(m, 'o'),
                           s=90, alpha=0.9, edgecolors='white', linewidth=1.0)
            if len(xs) >= 2:
                z = np.polyfit(xs, ys, 1)
                pl = np.poly1d(z)
                xs_line = np.linspace(min(xs), max(xs), 100)
                ax.plot(xs_line, pl(xs_line), 'r--', alpha=0.5, linewidth=1)

            # stats
            if spstats is not None and len(xs) >= 3:
                pr, p_pr = spstats.pearsonr(xs, ys)
                srho, p_srho = spstats.spearmanr(xs, ys)
            else:
                pr = p_pr = srho = p_srho = np.nan

            ax.set_xlabel('LLM-Judge Score (0-10)', fontsize=10)
            ax.set_ylabel('TrueSkill ELO Rating', fontsize=10)
            ax.set_title(f"{DIMENSION_INFO['short_names'][dim]}", fontsize=11, fontweight='bold')
            text = f"Pearson r = {pr:.3f} (p={p_pr:.3g})\n" \
                   f"Spearman ρ = {srho:.3f} (p={p_srho:.3g})"
            ax.text(0.02, 0.98, text, transform=ax.transAxes,
                    va='top', ha='left', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, edgecolor='#dddddd'))
            style_axes(ax)

        fig.legend(legend_handles, legend_labels, title='Models',
                   loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
        fig.suptitle('LLM-Judge Score vs TrueSkill ELO\n(Pearson + Spearman; ELO from rep20 overall)',
                     fontsize=14, fontweight='bold')

        plt.tight_layout()
        for fmt in save_format:
            fp = self.output_dir / f"sup_perf_elo_corr_pearson_spearman.{fmt}"
            plt.savefig(fp, dpi=300, bbox_inches='tight')
            print(f"补充图已保存: {fp}")
        return fig, axes

    def create_perf_vs_overall_elo_corr_with_kendall(self, save_format=['png', 'pdf']):
        """Pearson + Spearman + Kendall τ; legend shows model mapping (color+marker)."""
        if spstats is None:
            print('SciPy 未安装，无法计算 Kendall τ；改为生成 Pearson+Spearman 版本。')
            return self.create_perf_vs_overall_elo_corr(save_format=save_format)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        dims = DIMENSION_INFO['order']
        legend_handles, legend_labels = self._build_model_legend()

        for i, dim in enumerate(dims):
            ax = axes[i // 2, i % 2]
            xs, ys, models = self._collect_xy(dim)
            for x, y, m in zip(xs, ys, models):
                ax.scatter([x], [y],
                           color=COLOR_SCHEME['models'][m],
                           marker=MARKER_SCHEME['models'].get(m, 'o'),
                           s=100, alpha=0.85, edgecolors='white', linewidth=1)

            if len(xs) >= 2:
                z = np.polyfit(xs, ys, 1)
                pl = np.poly1d(z)
                xs_line = np.linspace(min(xs), max(xs), 100)
                ax.plot(xs_line, pl(xs_line), 'r--', alpha=0.5, linewidth=1)

            if len(xs) >= 3:
                pr, p_pr = spstats.pearsonr(xs, ys)
                srho, p_srho = spstats.spearmanr(xs, ys)
                ktau, p_tau = spstats.kendalltau(xs, ys)
            else:
                pr = p_pr = srho = p_srho = ktau = p_tau = np.nan

            ax.set_xlabel('LLM-Judge Score (0-10)', fontsize=10)
            ax.set_ylabel('TrueSkill ELO Rating', fontsize=10)
            ax.set_title(f"{DIMENSION_INFO['short_names'][dim]}", fontsize=11, fontweight='bold')
            text = (
                f"Pearson r = {pr:.3f} (p={p_pr:.3g})\n"
                f"Spearman ρ = {srho:.3f} (p={p_srho:.3g})\n"
                f"Kendall τ = {ktau:.3f} (p={p_tau:.3g})"
            )
            ax.text(0.02, 0.98, text, transform=ax.transAxes,
                    va='top', ha='left', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, edgecolor='#dddddd'))
            style_axes(ax)

        fig.legend(legend_handles, legend_labels, title='Models',
                   loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
        fig.suptitle('LLM-Judge Score vs TrueSkill ELO\n(Pearson + Spearman + Kendall τ; ELO from rep20 overall)',
                     fontsize=14, fontweight='bold')

        plt.tight_layout()
        for fmt in save_format:
            fp = self.output_dir / f"sup_perf_elo_corr_with_kendall.{fmt}"
            plt.savefig(fp, dpi=300, bbox_inches='tight')
            print(f"补充图已保存: {fp}")
        return fig, axes

