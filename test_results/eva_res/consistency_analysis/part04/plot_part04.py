from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from ..constants import CANONICAL_MODELS, TARGET_DIM_KEYS, LLM_MODEL_NAME  # type: ignore
from ..part02.viz import apply_vis_style, get_model_color_map, get_model_display_names, get_dimension_style  # type: ignore


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def _violin(values: Dict[str, List[float]], x_order: List[str], title: str, ylabel: str, outpath: Path, palette: List[str], xtick_labels: List[str], y_min: float | None = None):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import pandas as pd
    except Exception:
        return
    apply_vis_style()

    dims = []
    vals = []
    for k in x_order:
        arr = values.get(k, [])
        dims += [k] * len(arr)
        vals += arr
    df = pd.DataFrame({"x": dims, "y": vals})

    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.violinplot(data=df, x="x", y="y", inner="quartile", cut=0, ax=ax, palette=palette)
    sns.stripplot(data=df, x="x", y="y", ax=ax, color="k", alpha=0.3, size=3, jitter=0.25)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(xtick_labels, rotation=0)
    ax.axhline(0, ls="--", c="#888", lw=1)
    if y_min is not None:
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(bottom=y_min, top=max(ymax, 1.0))
    fig.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


def generate_part04_plots(out_dir: Path):
    detail = out_dir / "part04_llm_internal_icc.csv"
    if not detail.exists():
        return
    rows = _read_csv(detail)

    # Group values by dimension and by model
    dim_vals: Dict[str, List[float]] = {d: [] for d in TARGET_DIM_KEYS}
    model_vals: Dict[str, List[float]] = {m: [] for m in CANONICAL_MODELS}
    for r in rows:
        try:
            v = float(r["icc_a1"])  # type: ignore
        except Exception:
            continue
        d = r["dimension"]
        m = r["model"]
        if d in dim_vals:
            dim_vals[d].append(v)
        if m in model_vals:
            model_vals[m].append(v)

    plots = out_dir / "plots"
    # Dimension palette: match the earlier reference (Seaborn Set2)
    import seaborn as sns  # safe inside plotting path
    dim_style = get_dimension_style(TARGET_DIM_KEYS)
    dim_palette = list(sns.color_palette("Set2", n_colors=len(TARGET_DIM_KEYS)))
    dim_labels = [dim_style[k]['label'] for k in TARGET_DIM_KEYS]
    _violin(dim_vals, TARGET_DIM_KEYS, "4.1 LLM Internal Consistency: ICC(A,1) by Dimension", "ICC(A,1)", plots / "part04_icc_violin_by_dim.png", dim_palette, dim_labels, y_min=None)

    # Model palette & labels from vis_config
    model_colors = get_model_color_map(CANONICAL_MODELS, LLM_MODEL_NAME)
    model_palette = [model_colors[m] for m in CANONICAL_MODELS]
    model_labels_map = get_model_display_names(CANONICAL_MODELS)
    model_labels = [model_labels_map[m] for m in CANONICAL_MODELS]
    _violin(model_vals, CANONICAL_MODELS, "4.1 LLM Internal Consistency: ICC(A,1) by Model", "ICC(A,1)", plots / "part04_icc_violin_by_model.png", model_palette, model_labels, y_min=None)

    # Also plot ICC(A,k) with same palettes
    # Re-read detail to gather icc_ak
    dim_vals_k: Dict[str, List[float]] = {d: [] for d in TARGET_DIM_KEYS}
    model_vals_k: Dict[str, List[float]] = {m: [] for m in CANONICAL_MODELS}
    for r in rows:
        try:
            v = float(r.get("icc_ak", "nan"))
        except Exception:
            continue
        d = r["dimension"]; m = r["model"]
        if d in dim_vals_k:
            dim_vals_k[d].append(v)
        if m in model_vals_k:
            model_vals_k[m].append(v)
    _violin(dim_vals_k, TARGET_DIM_KEYS, "4.1 LLM Internal Consistency: ICC(A,k) by Dimension", "ICC(A,k)", plots / "part04_iccAk_violin_by_dim.png", dim_palette, dim_labels)
    _violin(model_vals_k, CANONICAL_MODELS, "4.1 LLM Internal Consistency: ICC(A,k) by Model", "ICC(A,k)", plots / "part04_iccAk_violin_by_model.png", model_palette, model_labels)
