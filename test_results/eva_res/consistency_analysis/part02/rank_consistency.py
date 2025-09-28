from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ..loaders import LLMScore, HumanScore  # type: ignore
from ..aggregations import HumanAvg, LLMAggregate  # type: ignore
from ..constants import OUT_DIR, TARGET_DIM_KEYS, CANONICAL_MODELS  # type: ignore
from .stats_utils import kendall_tau_b, spearman_rho, icc_a1


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def _group_pairs_by_question_and_dim(human_csv: Path, llm_csv: Path) -> Dict[Tuple[int, str], List[Tuple[float, float]]]:
    human_rows = _read_csv(human_csv)
    llm_rows = _read_csv(llm_csv)

    # Build maps: (model, q, dim)->score
    hmap: Dict[Tuple[str, int, str], float] = {}
    for r in human_rows:
        model = r["model"]
        q = int(r["question_idx"])  # type: ignore
        dim = r["dimension"]
        if dim not in TARGET_DIM_KEYS or model not in CANONICAL_MODELS:
            continue
        hmap[(model, q, dim)] = float(r["human_avg"])  # type: ignore

    lmap: Dict[Tuple[str, int, str], float] = {}
    for r in llm_rows:
        model = r["model"]
        q = int(r["question_idx"])  # type: ignore
        dim = r["dimension"]
        if dim not in TARGET_DIM_KEYS or model not in CANONICAL_MODELS:
            continue
        lmap[(model, q, dim)] = float(r["llm_avg_overall"])  # type: ignore

    # For each (q, dim), collect pairs in canonical model order
    by_qd: Dict[Tuple[int, str], List[Tuple[float, float]]] = {}
    qs = {int(r["question_idx"]) for r in human_rows}
    for q in sorted(qs):
        for dim in TARGET_DIM_KEYS:
            pairs: List[Tuple[float, float]] = []
            for model in CANONICAL_MODELS:
                key = (model, q, dim)
                if key in hmap and key in lmap:
                    pairs.append((hmap[key], lmap[key]))
            if len(pairs) >= 3:  # need at least 3 to be meaningful
                by_qd[(q, dim)] = pairs
    return by_qd


def compute_rank_consistency(out_dir: Path) -> Tuple[Path, Path]:
    """
    Implements Part 2.1: For each (question, dimension), compute Kendall's tau-b,
    Spearman's rho, and ICC(A,1) between human and LLM across models.
    Returns paths to detailed and summary CSVs.
    """
    human_csv = out_dir / "human_avg.csv"
    llm_csv = out_dir / "llm_avg_overall.csv"
    detail_out = out_dir / "part02_corr_by_question_dim.csv"
    summary_out = out_dir / "part02_corr_summary_by_dimension.csv"

    pairs_by_qd = _group_pairs_by_question_and_dim(human_csv, llm_csv)

    # Write detailed results
    detail_rows: List[List[str]] = []
    header = [
        "question_idx",
        "dimension",
        "n_pairs",
        "kendall_tau_b",
        "kendall_p",
        "spearman_rho",
        "spearman_p",
        "icc_a1",
        "icc_p",
    ]

    summary_acc: Dict[str, List[float]] = {"kendall_tau_b": [], "spearman_rho": [], "icc_a1": []}
    summary_bins: Dict[str, Dict[str, List[float]]] = {}
    for dim in TARGET_DIM_KEYS:
        summary_bins[dim] = {"kendall_tau_b": [], "spearman_rho": [], "icc_a1": []}

    for (q, dim), pairs in sorted(pairs_by_qd.items()):
        hx = [p[0] for p in pairs]
        lx = [p[1] for p in pairs]
        tau, tau_p = kendall_tau_b(hx, lx)
        rho, rho_p = spearman_rho(hx, lx)
        icc, icc_p = icc_a1(list(zip(hx, lx)))
        detail_rows.append([
            str(q),
            dim,
            str(len(pairs)),
            f"{tau:.6g}",
            "NA" if tau_p is None else f"{tau_p:.6g}",
            f"{rho:.6g}",
            "NA" if rho_p is None else f"{rho_p:.6g}",
            f"{icc:.6g}",
            "NA" if icc_p is None else f"{icc_p:.6g}",
        ])
        summary_bins[dim]["kendall_tau_b"].append(tau)
        summary_bins[dim]["spearman_rho"].append(rho)
        summary_bins[dim]["icc_a1"].append(icc)

    # Write detail CSV
    with detail_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(detail_rows)

    # Summaries per dimension
    def _stats(vals: List[float]) -> Tuple[float, float, float, int]:
        import numpy as np
        if not vals:
            return 0.0, 0.0, 0.0, 0
        a = np.asarray(vals, dtype=float)
        a = a[~np.isnan(a)]
        n = int(a.size)
        if n == 0:
            return 0.0, 0.0, 0.0, 0
        mean = float(np.nanmean(a))
        med = float(np.nanmedian(a))
        std = float(np.nanstd(a, ddof=1)) if n > 1 else 0.0
        return mean, med, std, n

    # Aggregate p-values: mean p and proportion below thresholds
    p_bins: Dict[str, Dict[str, List[float]]] = {dim: {"kendall_p": [], "spearman_p": [], "icc_p": []} for dim in TARGET_DIM_KEYS}
    for row in detail_rows:
        dim = row[1]
        if dim in p_bins:
            for key, pkey in [("kendall_p", "kendall_p"), ("spearman_p", "spearman_p"), ("icc_p", "icc_p")]:
                pstr = row[["question_idx", "dimension", "n_pairs", "kendall_tau_b", "kendall_p", "spearman_rho", "spearman_p", "icc_a1", "icc_p"].index(pkey)]
                try:
                    pv = float(pstr)
                    p_bins[dim][key].append(pv)
                except Exception:
                    pass

    def _pstats(vals: List[float]) -> Tuple[float, float, float, int]:
        import numpy as np
        if not vals:
            return 0.0, 0.0, 0.0, 0
        a = np.asarray(vals, dtype=float)
        a = a[np.isfinite(a)]
        if a.size == 0:
            return 0.0, 0.0, 0.0, 0
        mean = float(np.nanmean(a))
        prop_005 = float((a < 0.05).mean())
        prop_001 = float((a < 0.01).mean())
        return mean, prop_005, prop_001, int(a.size)

    summary_rows: List[List[str]] = []
    summary_header = ["dimension", "metric", "mean", "median", "std", "n", "mean_p", "prop_p_lt_0.05", "prop_p_lt_0.01", "n_p"]
    for dim in TARGET_DIM_KEYS:
        for metric in ["kendall_tau_b", "spearman_rho", "icc_a1"]:
            m, med, sd, n = _stats(summary_bins[dim][metric])
            # p-value buckets
            pk = {"kendall_tau_b": "kendall_p", "spearman_rho": "spearman_p", "icc_a1": "icc_p"}[metric]
            mean_p, p005, p001, npcount = _pstats(p_bins[dim].get(pk, []))
            summary_rows.append([dim, metric, f"{m:.6g}", f"{med:.6g}", f"{sd:.6g}", str(n), f"{mean_p:.6g}", f"{p005:.4f}", f"{p001:.4f}", str(npcount)])

    with summary_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(summary_header)
        w.writerows(summary_rows)

    return detail_out, summary_out
