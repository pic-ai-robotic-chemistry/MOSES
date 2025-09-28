from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from ..constants import CANONICAL_MODELS, OUT_DIR  # type: ignore
from ..part02.viz import apply_vis_style, get_model_color_map, get_model_display_names  # type: ignore
from ..constants import LLM_MODEL_NAME  # type: ignore


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def compute_disagreement_summary(out_dir: Path) -> Path:
    path = out_dir / "disagreement_scores.csv"
    rows = _read_csv(path)
    # Average per model
    from collections import defaultdict
    import statistics as S
    agg: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        m = r["model"]
        if m not in CANONICAL_MODELS:
            continue
        try:
            v = float(r["disagreement"])  # type: ignore
        except Exception:
            continue
        agg[m].append(v)
    out = out_dir / "part05_disagreement_summary.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "n", "mean", "median"])
        for m in CANONICAL_MODELS:
            arr = agg.get(m, [])
            if arr:
                w.writerow([m, len(arr), f"{S.mean(arr):.6g}", f"{S.median(arr):.6g}"])
            else:
                w.writerow([m, 0, "", ""])
    return out


def plot_disagreement_violin(out_dir: Path):
    path = out_dir / "disagreement_scores.csv"
    rows = _read_csv(path)
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
    except Exception:
        return
    apply_vis_style()

    data = {m: [] for m in CANONICAL_MODELS}
    for r in rows:
        m = r["model"]
        if m not in data:
            continue
        try:
            v = float(r["disagreement"])  # type: ignore
        except Exception:
            continue
        data[m].append(v)

    models = []
    vals = []
    for m in CANONICAL_MODELS:
        v = data.get(m, [])
        models += [m] * len(v)
        vals += v
    df = pd.DataFrame({"model": models, "disagreement": vals})

    fig, ax = plt.subplots(figsize=(12, 5.2))
    # Use consistent model palette and labels
    cmap = get_model_color_map(CANONICAL_MODELS, LLM_MODEL_NAME)
    palette = [cmap[m] for m in CANONICAL_MODELS]
    labels_map = get_model_display_names(CANONICAL_MODELS)
    sns.violinplot(data=df, x="model", y="disagreement", inner="quartile", cut=0, ax=ax, palette=palette, order=CANONICAL_MODELS)
    sns.stripplot(data=df, x="model", y="disagreement", ax=ax, color="k", alpha=0.25, size=2.5, jitter=0.25)
    ax.axhline(0, ls="--", c="#888", lw=1)
    ax.set_title("5. Disagreement Distribution (LLM - Human)")
    ax.set_xlabel("Model")
    ax.set_ylabel("Disagreement_Score (LLM - Human)")
    ax.set_xticklabels([labels_map[m] for m in CANONICAL_MODELS], rotation=0)
    fig.tight_layout()
    plots = out_dir / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    outpath = plots / "part05_disagreement_violin.png"
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.with_suffix('.pdf'))
    plt.close(fig)
