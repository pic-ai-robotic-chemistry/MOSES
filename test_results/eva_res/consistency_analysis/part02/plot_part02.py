from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from .viz import apply_vis_style, get_model_color_map, get_dimension_style
from ..constants import OUT_DIR, TARGET_DIM_KEYS, CANONICAL_MODELS, LLM_MODEL_NAME  # type: ignore


def _read_detail(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def _read_pairs(out_dir: Path):
    """Build pairs DataFrame: model, question_idx, dimension, human, llm."""
    try:
        import pandas as pd
    except Exception:
        return None
    hp = out_dir / "human_avg.csv"
    lp = out_dir / "llm_avg_overall.csv"
    if not (hp.exists() and lp.exists()):
        return None
    h = pd.read_csv(hp)
    l = pd.read_csv(lp)
    h = h[["model", "question_idx", "dimension", "human_avg"]]
    l = l[["model", "question_idx", "dimension", "llm_avg_overall"]]
    df = pd.merge(h, l, on=["model", "question_idx", "dimension"], how="inner")
    df.rename(columns={"human_avg": "human", "llm_avg_overall": "llm"}, inplace=True)
    return df[df["dimension"].isin(TARGET_DIM_KEYS) & df["model"].isin(CANONICAL_MODELS)]


def _plot_scatter_overall(df, outpath: Path):
    """图A：按维度分面散点，灰点 + 总体拟合线 + y=x。"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except Exception:
        return
    apply_vis_style()
    dims = list(TARGET_DIM_KEYS)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()
    for i, dim in enumerate(dims):
        ax = axes[i]
        sub = df[df["dimension"] == dim]
        if sub.empty:
            continue
        sns.scatterplot(data=sub, x="human", y="llm", ax=ax, color="#444444", alpha=0.45, s=18, edgecolor=None)
        lo = float(min(sub["human"].min(), sub["llm"].min()))
        hi = float(max(sub["human"].max(), sub["llm"].max()))
        ax.plot([lo, hi], [lo, hi], linestyle="--", color="#888888", linewidth=1)
        sns.regplot(data=sub, x="human", y="llm", scatter=False, ax=ax, color="#1f77b4", ci=None, line_kws={"linewidth": 1.6})
        ax.set_title(dim)
        ax.set_xlabel("Human_Avg")
        ax.set_ylabel("LLM_Avg_Overall")
        ax.grid(True, linestyle="--", alpha=0.3)
    fig.suptitle("2.1 A: LLM vs Human (Overall Trend) by Dimension", y=0.98)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(outpath, dpi=200)
    # Also save vector PDF for AI editing
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


from typing import List


def _plot_scatter_by_model(df, outpath: Path, models_subset: List[str]):
    """图B子图：给定模型子集，按维度分面散点，子集内每模型着色并拟合一条线。"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except Exception:
        return
    apply_vis_style()
    dims = list(TARGET_DIM_KEYS)
    # Use color map from vis_config based on JSON model names
    full_cmap = get_model_color_map(CANONICAL_MODELS, LLM_MODEL_NAME)
    color_map = {m: full_cmap[m] for m in models_subset if m in full_cmap}
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    for i, dim in enumerate(dims):
        ax = axes[i]
        sub = df[(df["dimension"] == dim) & (df["model"].isin(models_subset))]
        if sub.empty:
            continue
        sns.scatterplot(
            data=sub,
            x="human",
            y="llm",
            hue="model",
            hue_order=models_subset,
            palette=color_map,
            ax=ax,
            alpha=0.6,
            s=20,
            edgecolor=None,
            legend=False,
        )
        # Per-model trends
        for m in models_subset:
            ms = sub[sub["model"] == m]
            if len(ms) >= 3:
                # Disable CI shading to avoid light bands; draw only trend line
                sns.regplot(data=ms, x="human", y="llm", scatter=False, ax=ax, color=color_map[m], ci=None, line_kws={"linewidth": 1.4})
        lo = float(min(sub["human"].min(), sub["llm"].min()))
        hi = float(max(sub["human"].max(), sub["llm"].max()))
        ax.plot([lo, hi], [lo, hi], linestyle="--", color="#888", linewidth=1)
        ax.set_title(dim)
        ax.set_xlabel("Human_Avg")
        ax.set_ylabel("LLM_Avg_Overall")
        ax.grid(True, linestyle="--", alpha=0.3)
    # Legend on the right inside figure (so it is included in savefig)
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=m,
                          markerfacecolor=color_map[m], markersize=6) for m in models_subset]
    fig.subplots_adjust(right=0.82)  # leave space for legend
    fig.legend(handles=handles, loc='center left', ncol=1, frameon=False, bbox_to_anchor=(0.855, 0.5))
    fig.suptitle("2.1 B: LLM vs Human by Model (per-model trends)", y=0.99)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


def _plot_scatter_b_supplementary(df, outpath: Path):
    """2.1 B_Supplementary: all grey points + overall fit, and highlight
    MOSES, O3, LightRAG, GPT-4.1 with colored points and per-model lines.
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except Exception:
        return
    apply_vis_style()

    highlight = ["MOSES", "o3", "LightRAG", "GPT-4.1"]
    cmap = get_model_color_map(CANONICAL_MODELS, LLM_MODEL_NAME)
    dims = list(TARGET_DIM_KEYS)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    for i, dim in enumerate(dims):
        ax = axes[i]
        sub = df[df["dimension"] == dim]
        if sub.empty:
            continue
        # All points in grey
        sns.scatterplot(data=sub, x="human", y="llm", ax=ax, color="#7f7f7f", alpha=0.35, s=16, edgecolor=None)
        # Overall fit in dashed black
        sns.regplot(data=sub, x="human", y="llm", scatter=False, ax=ax, color="#000000", ci=None, line_kws={"linewidth": 1.6, "linestyle": "--"})
        # y=x reference (dotted)
        lo = float(min(sub["human"].min(), sub["llm"].min()))
        hi = float(max(sub["human"].max(), sub["llm"].max()))
        ax.plot([lo, hi], [lo, hi], linestyle=":", color="#888", linewidth=1)
        # Highlighted models
        for m in highlight:
            ms = sub[sub["model"] == m]
            if ms.empty:
                continue
            sns.scatterplot(data=ms, x="human", y="llm", ax=ax, color=cmap.get(m, "#1f77b4"), alpha=0.85, s=28, edgecolor=None)
            if len(ms) >= 3:
                sns.regplot(data=ms, x="human", y="llm", scatter=False, ax=ax, color=cmap.get(m, "#1f77b4"), ci=None, line_kws={"linewidth": 1.6})
        ax.set_title(dim)
        ax.set_xlabel("Human_Avg")
        ax.set_ylabel("LLM_Avg_Overall")
        ax.grid(True, linestyle="--", alpha=0.3)

    # Legend on the right inside
    handles = [
        plt.Line2D([0], [0], marker='o', color='w', label=m, markerfacecolor=cmap.get(m, "#1f77b4"), markersize=6)
        for m in highlight
    ]
    handles.append(plt.Line2D([0], [0], color='#000000', linestyle='--', label='Overall fit'))
    fig.subplots_adjust(right=0.82)
    fig.legend(handles=handles, loc='center left', frameon=False, bbox_to_anchor=(0.855, 0.5))
    fig.suptitle("2.1 B_Supplementary: Overall + Highlighted Models (MOSES, O3, LightRAG, GPT-4.1)", y=0.99)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 0.86, 0.96])
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


def _plot_forest_from_detail(df: List[Dict[str, str]], outpath: Path):
    """图C：每维度3个点（Kendall/Spearman/ICC），竖向误差棒为99.7%CI。"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except Exception:
        return
    apply_vis_style()

    vals = {dim: {"kendall_tau_b": [], "spearman_rho": [], "icc_a1": []} for dim in TARGET_DIM_KEYS}
    for row in df:
        d = row.get("dimension")
        if d not in vals:
            continue
        for k in ("kendall_tau_b", "spearman_rho", "icc_a1"):
            try:
                v = float(row.get(k, "nan"))
            except Exception:
                continue
            if v == v:
                vals[d][k].append(v)

    dims = list(TARGET_DIM_KEYS)
    metrics = ["kendall_tau_b", "spearman_rho", "icc_a1"]
    colors = {"kendall_tau_b": "#1f77b4", "spearman_rho": "#ff7f0e", "icc_a1": "#2ca02c"}
    markers = {"kendall_tau_b": "o", "spearman_rho": "s", "icc_a1": "^"}
    x = None
    try:
        import numpy as np
        x = np.arange(len(dims))
    except Exception:
        return

    fig, ax = plt.subplots(figsize=(10, 5.5))
    offset = {"kendall_tau_b": -0.18, "spearman_rho": 0.0, "icc_a1": 0.18}
    for i, dim in enumerate(dims):
        for m in metrics:
            import numpy as _np
            arr = _np.asarray(vals[dim][m], dtype=float)
            arr = arr[_np.isfinite(arr)]
            if arr.size == 0:
                continue
            mean = float(_np.nanmean(arr))
            if arr.size > 1:
                std = float(_np.nanstd(arr, ddof=1))
                se = std / float(_np.sqrt(arr.size))
                ci = 3.0 * se
            else:
                ci = 0.0
            xpos = x[i] + offset[m]
            ax.errorbar(xpos, mean, yerr=ci, fmt=markers[m], color=colors[m], capsize=4, markersize=6, lw=1.4, label=m if i == 0 else "")
    ax.set_xticks(x)
    ax.set_xticklabels(dims)
    ax.set_ylabel("Correlation / ICC")
    ax.set_title("2.1 C: Rank Consistency Summary (Mean ± 99.7% CI)")
    ax.grid(True, axis='y', linestyle='--', alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(title="Metric", ncol=3, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.08))
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    import matplotlib.pyplot as _plt
    _plt.close(fig)


def _plot_metric(df: List[Dict[str, str]], metric: str, outpath: Path, title: str):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except Exception:
        return

    apply_vis_style()

    # Prepare data per dimension
    data = {dim: [] for dim in TARGET_DIM_KEYS}
    for row in df:
        dim = row["dimension"]
        if dim not in data:
            continue
        try:
            val = float(row[metric])
        except Exception:
            continue
        data[dim].append(val)

    # Build long-form lists
    dims = []
    vals = []
    for dim, arr in data.items():
        dims += [dim] * len(arr)
        vals += arr

    import pandas as pd
    pdf = pd.DataFrame({"dimension": dims, "value": vals})

    fig, ax = plt.subplots(figsize=(9, 5.5))
    # Use vis_config dimension palette and English labels
    dim_style = get_dimension_style(TARGET_DIM_KEYS)
    palette = [dim_style[k]['color'] for k in TARGET_DIM_KEYS]
    labels = [dim_style[k]['label'] for k in TARGET_DIM_KEYS]
    sns.violinplot(
        data=pdf,
        x="dimension",
        y="value",
        ax=ax,
        inner="quartile",  # draw Q1/median/Q3 lines as参考示意
        cut=0,
        linewidth=1.2,
        palette=palette,
    )
    # Jittered scatter points to show per-question values
    sns.stripplot(
        data=pdf,
        x="dimension",
        y="value",
        ax=ax,
        color="k",
        alpha=0.35,
        size=3,
        jitter=0.25,
    )
    # Beautify: grid lines, tick params
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)

    # 不再叠加红色误差棒；仅保留小提琴的四分位线 + 散点

    ax.set_title(title)
    ax.set_xlabel("Dimension")
    ax.set_ylabel(metric)
    ax.set_xticklabels(labels, rotation=0)
    # For A1 versions, set lower y-limit to -0.75 (upper keep auto)
    if metric.lower() in {"icc_a1", "icc(a,1)", "icc_a1_value"}:
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(bottom=-0.75, top=max(ymax, 1.0))
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


def generate_part02_plots(out_dir: Path):
    detail = out_dir / "part02_corr_by_question_dim.csv"
    if not detail.exists():
        return
    rows = _read_detail(detail)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 2.1 图A/图B/图C
    pairs_df = _read_pairs(out_dir)
    if pairs_df is not None:
        _plot_scatter_overall(pairs_df, plots_dir / "part02_A_scatter_overall.png")
        # 图B拆分：主模型 vs nano/mini；并增加 B3 = B1 去除 GPT-4o
        group_main = ["MOSES", "LightRAG", "o3", "GPT-4.1", "GPT-4o"]
        group_main_no_gpt4o = ["MOSES", "LightRAG", "o3", "GPT-4.1"]
        group_nano = ["MOSES-nano", "LightRAG-nano", "GPT-4.1-nano", "GPT-4o-mini"]
        _plot_scatter_by_model(pairs_df, plots_dir / "part02_B1_scatter_by_model_main.png", group_main)
        _plot_scatter_by_model(pairs_df, plots_dir / "part02_B3_scatter_by_model_main_wo_gpt4o.png", group_main_no_gpt4o)
        _plot_scatter_by_model(pairs_df, plots_dir / "part02_B2_scatter_by_model_nano.png", group_nano)
        _plot_scatter_b_supplementary(pairs_df, plots_dir / "part02_B_supplementary.png")
    _plot_forest_from_detail(rows, plots_dir / "part02_C_forest.png")

    # Human internal consistency (2.2) violin
    human_detail = out_dir / "part02_human_internal_icc_by_question_dim.csv"
    if human_detail.exists():
        hrows = _read_detail(human_detail)
        # Reuse the plotter with icc_a1 metric
        for r in hrows:
            r["value"] = r.get("icc_a1", "")
        _plot_metric(hrows, "icc_a1", plots_dir / "part02_human_icc_violin.png", "Human Internal ICC(A,1) by Dimension (Q-wise)")
    # ICC(A,k) (k=3) for human judges
    human_detail_k = out_dir / "part02_human_internal_iccAk_by_question_dim.csv"
    if human_detail_k.exists():
        hkrows = _read_detail(human_detail_k)
        for r in hkrows:
            r["value"] = r.get("icc_ak", "")
        _plot_metric(hkrows, "icc_ak", plots_dir / "part02_human_iccAk_violin.png", "Human Internal ICC(A,k) by Dimension (Q-wise)")

    # 2.2 人类内部一致性小提琴
