from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

from ..constants import CANONICAL_MODELS, TARGET_DIM_KEYS, OUT_DIR  # type: ignore
from ..loaders import load_llm_jsonl  # type: ignore
from ..part02.stats_utils import icc_a1, icc_ak  # type: ignore


def compute_llm_internal_icc(out_dir: Path, jsonl_path: str) -> Tuple[Path, Path]:
    """
    Build matrices per (model, dimension, answer_round): shape (27 questions, 5 evaluation_rounds)
    and compute ICC(A,1) with p-value. This yields 9*4*5=180 ICC values.
    Outputs a detailed CSV and a summary CSV with mean/median and significance proportions.
    """
    rows = load_llm_jsonl(jsonl_path)

    # Group scores: (model, q, dim, answer_round, evaluation_round) -> score already present
    # Build matrix per (model, dim, answer_round)
    from collections import defaultdict
    import numpy as np

    mat: Dict[Tuple[str, str, int], Dict[int, Dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        if r.model not in CANONICAL_MODELS or r.dimension not in TARGET_DIM_KEYS:
            continue
        key = (r.model, r.dimension, r.answer_round)
        mat[key][r.question_idx][r.evaluation_round] = r.score

    detail_path = out_dir / "part04_llm_internal_icc.csv"
    with detail_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "dimension", "answer_round", "n_questions", "icc_a1", "icc_p", "icc_ak", "icc_k_p"])
        detail_rows: List[List[str]] = []
        for (m, d, a), qmap in sorted(mat.items()):
            # Build matrix Qx5 ordered by question 1..27 and eval 1..5
            X = []
            for q in range(1, 28):
                if q not in qmap:
                    continue
                row = [qmap[q].get(e, None) for e in range(1, 6)]
                if any(v is None for v in row):
                    continue
                X.append(row)
            if len(X) < 5:
                continue
            X = np.asarray(X, dtype=float)
            icc, p = icc_a1(X)
            iccK, pK = icc_ak(X)
            detail_rows.append([m, d, a, X.shape[0], f"{icc:.6g}", "NA" if p is None else f"{p:.6g}", f"{iccK:.6g}", "NA" if pK is None else f"{pK:.6g}"])
        w.writerows(detail_rows)

    # Summary
    import statistics as S
    import math
    sig_counts: Dict[str, int] = {"p_lt_0.05": 0, "p_lt_0.01": 0}
    sig_counts_k: Dict[str, int] = {"p_lt_0.05": 0, "p_lt_0.01": 0}
    vals: List[float] = []
    vals_k: List[float] = []
    for r in detail_rows:
        v = float(r[4]); vals.append(v)
        try:
            vk = float(r[6]); vals_k.append(vk)
        except Exception:
            pass
        try:
            p = float(r[5]) if r[5] != "NA" else math.nan
            if not math.isnan(p):
                if p < 0.05:
                    sig_counts["p_lt_0.05"] += 1
                if p < 0.01:
                    sig_counts["p_lt_0.01"] += 1
            pk = float(r[7]) if r[7] != "NA" else math.nan
            if not math.isnan(pk):
                if pk < 0.05:
                    sig_counts_k["p_lt_0.05"] += 1
                if pk < 0.01:
                    sig_counts_k["p_lt_0.01"] += 1
        except Exception:
            pass
    summary_path = out_dir / "part04_llm_internal_icc_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        if vals:
            w.writerow(["mean", f"{S.mean(vals):.6g}"])
            w.writerow(["median", f"{S.median(vals):.6g}"])
        w.writerow(["n", str(len(vals))])
        w.writerow(["prop_p_lt_0.05", f"{sig_counts['p_lt_0.05']/(len(vals) or 1):.4f}"])
        w.writerow(["prop_p_lt_0.01", f"{sig_counts['p_lt_0.01']/(len(vals) or 1):.4f}"])
        # Also for ICC(A,k)
        if vals_k:
            w.writerow(["mean_k", f"{S.mean(vals_k):.6g}"])
            w.writerow(["median_k", f"{S.median(vals_k):.6g}"])
        w.writerow(["n_k", str(len(vals_k))])
        w.writerow(["prop_p_lt_0.05_k", f"{sig_counts_k['p_lt_0.05']/(len(vals_k) or 1):.4f}"])
        w.writerow(["prop_p_lt_0.01_k", f"{sig_counts_k['p_lt_0.01']/(len(vals_k) or 1):.4f}"])

    return detail_path, summary_path
