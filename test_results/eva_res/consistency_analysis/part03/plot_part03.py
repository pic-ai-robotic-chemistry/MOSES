from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from ..constants import CANONICAL_MODELS, TARGET_DIM_KEYS, LLM_MODEL_NAME  # type: ignore
from ..part02.viz import apply_vis_style, get_model_color_map  # type: ignore


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def _plot_forest_by_model(detail_csv: Path, metric: str, lo_col: str, hi_col: str, title: str, outpath: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import pandas as pd
    except Exception:
        return

    apply_vis_style()
    data = _read_csv(detail_csv)
    df = pd.DataFrame(data)
    # Ensure numeric
    df[metric] = pd.to_numeric(df[metric], errors="coerce")
    df[lo_col] = pd.to_numeric(df[lo_col], errors="coerce")
    df[hi_col] = pd.to_numeric(df[hi_col], errors="coerce")

    # Use configured model colors
    color_map = get_model_color_map(CANONICAL_MODELS, LLM_MODEL_NAME)

    # Facet by dimension
    dims = list(TARGET_DIM_KEYS)
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharey=True)
    axes = axes.flatten()
    for i, dim in enumerate(dims):
        ax = axes[i]
        sub = df[df["dimension"] == dim]
        if sub.empty:
            continue
        # Keep model order consistent
        sub = sub.set_index("model").reindex(CANONICAL_MODELS).reset_index()
        x = np.arange(len(CANONICAL_MODELS))
        y = sub[metric].to_numpy(float)
        lo = sub[lo_col].to_numpy(float)
        hi = sub[hi_col].to_numpy(float)
        colors = [color_map.get(m, "#333333") for m in CANONICAL_MODELS]
        for xi, yi, lo_i, hi_i, c in zip(x, y, lo, hi, colors):
            if not np.isfinite(yi):
                continue
            lo_err = 0.0
            hi_err = 0.0
            if np.isfinite(lo_i):
                lo_err = max(0.0, yi - lo_i)
            if np.isfinite(hi_i):
                hi_err = max(0.0, hi_i - yi)
            ax.errorbar(xi, yi, yerr=[[lo_err], [hi_err]], fmt='o', color=c, ecolor=c, capsize=4, lw=1.2)
        ax.set_xticks(x)
        ax.set_xticklabels(CANONICAL_MODELS, rotation=30, ha='right')
        ax.set_title(dim)
        ax.grid(True, axis='y', linestyle='--', alpha=0.35)
    fig.suptitle(title, y=0.99)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)


def generate_part03_plots(out_dir: Path):
    # Coach Kendall forest
    kcsv = out_dir / "part03_coach_kendall_by_model_dim.csv"
    if kcsv.exists():
        _plot_forest_by_model(
            kcsv,
            metric="kendall_tau_b",
            lo_col="ci_low_997",
            hi_col="ci_high_997",
            title="3.1 Coach Consistency: Kendall's Tau-b (Mean ± 99.7% CI) by Dimension",
            outpath=out_dir / "plots/part03_kendall_forest.png",
        )

    # Human internal coach-view ICC forest
    iccsv = out_dir / "part03_coach_human_icc_by_model_dim.csv"
    if iccsv.exists():
        _plot_forest_by_model(
            iccsv,
            metric="icc_a1",
            lo_col="ci_low_997",
            hi_col="ci_high_997",
            title="3.2 Human Internal Consistency: ICC(A,1) (Mean ± 99.7% CI) by Dimension",
            outpath=out_dir / "plots/part03_human_icc_forest.png",
        )
    # ICC(A,k) (k=3) forest
    iccsvk = out_dir / "part03_coach_human_iccAk_by_model_dim.csv"
    if iccsvk.exists():
        _plot_forest_by_model(
            iccsvk,
            metric="icc_ak",
            lo_col="ci_low_997",
            hi_col="ci_high_997",
            title="3.2 Human Internal Consistency: ICC(A,k) (Mean ± 99.7% CI) by Dimension",
            outpath=out_dir / "plots/part03_human_iccAk_forest.png",
        )
