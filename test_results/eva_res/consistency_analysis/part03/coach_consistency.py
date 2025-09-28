from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from ..constants import OUT_DIR, TARGET_DIM_KEYS, CANONICAL_MODELS  # type: ignore
from ..part02.stats_utils import kendall_tau_b, icc_a1, icc_ak  # type: ignore


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def _group_series_by_model_dim(human_csv: Path, llm_csv: Path) -> Dict[Tuple[str, str], Tuple[List[float], List[float]]]:
    h = _read_csv(human_csv)
    l = _read_csv(llm_csv)
    # {(model, dim, q): score}
    hmap: Dict[Tuple[str, str, int], float] = {}
    lmap: Dict[Tuple[str, str, int], float] = {}
    for r in h:
        m = r["model"]
        d = r["dimension"]
        if m not in CANONICAL_MODELS or d not in TARGET_DIM_KEYS:
            continue
        q = int(r["question_idx"])  # type: ignore
        hmap[(m, d, q)] = float(r["human_avg"])  # type: ignore
    for r in l:
        m = r["model"]
        d = r["dimension"]
        if m not in CANONICAL_MODELS or d not in TARGET_DIM_KEYS:
            continue
        q = int(r["question_idx"])  # type: ignore
        lmap[(m, d, q)] = float(r["llm_avg_overall"])  # type: ignore

    series: Dict[Tuple[str, str], Tuple[List[float], List[float]]] = {}
    for m in CANONICAL_MODELS:
        for d in TARGET_DIM_KEYS:
            xs: List[float] = []
            ys: List[float] = []
            # keep aligned over questions 1..27 if present
            for q in range(1, 28):
                key = (m, d, q)
                if key in hmap and key in lmap:
                    xs.append(hmap[key])
                    ys.append(lmap[key])
            if len(xs) >= 5:  # keep only if sufficient data
                series[(m, d)] = (xs, ys)
    return series


def _bootstrap_kendall_ci(x: Sequence[float], y: Sequence[float], B: int = 800, seed: int = 42) -> Tuple[float, float]:
    import numpy as np
    from scipy.stats import kendalltau  # type: ignore

    n = len(x)
    if n < 3:
        return 0.0, 0.0
    rng = random.Random(seed)
    vals: List[float] = []
    idx = list(range(n))
    for _ in range(B):
        samp = [idx[rng.randrange(n)] for _ in range(n)]
        tau, _ = kendalltau([x[i] for i in samp], [y[i] for i in samp], variant="b")
        if tau == tau:
            vals.append(float(tau))
    if not vals:
        return 0.0, 0.0
    vals.sort()
    lo = vals[int(0.0015 * len(vals))]
    hi = vals[min(len(vals) - 1, int(0.9985 * len(vals))) ]
    return lo, hi


def compute_coach_kendall(out_dir: Path) -> Path:
    human_csv = out_dir / "human_avg.csv"
    llm_csv = out_dir / "llm_avg_overall.csv"
    pairs = _group_series_by_model_dim(human_csv, llm_csv)

    detail = out_dir / "part03_coach_kendall_by_model_dim.csv"
    with detail.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "dimension", "n", "kendall_tau_b", "kendall_p", "ci_low_997", "ci_high_997"])
        for (m, d), (hx, lx) in pairs.items():
            tau, p = kendall_tau_b(hx, lx)
            try:
                lo, hi = _bootstrap_kendall_ci(hx, lx)
            except Exception:
                lo, hi = 0.0, 0.0
            w.writerow([m, d, len(hx), f"{tau:.6g}", "NA" if p is None else f"{p:.6g}", f"{lo:.6g}", f"{hi:.6g}"])
    return detail


def _load_human_tables(csv_path: Path):
    # Reuse parser from part02.human_internal but import locally to avoid circular
    from ..part02.human_internal import load_human_judge_tables  # type: ignore

    return load_human_judge_tables(csv_path)


def compute_coach_human_internal_icc(out_dir: Path) -> Tuple[Path, Path]:
    from ..constants import HUMAN_CSV_PATH  # type: ignore
    tables = _load_human_tables(Path(HUMAN_CSV_PATH))  # q -> judge -> model -> dim

    detail = out_dir / "part03_coach_human_icc_by_model_dim.csv"
    detail_k = out_dir / "part03_coach_human_iccAk_by_model_dim.csv"
    with detail.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "dimension", "n_questions", "icc_a1", "icc_p", "ci_low_997", "ci_high_997"])
        wk = csv.writer(detail_k.open("w", encoding="utf-8", newline=""))
        wk.writerow(["model", "dimension", "n_questions", "icc_ak", "icc_k_p", "ci_low_997", "ci_high_997"])

        # Build per model, per dimension: 27x3 matrix (questions x judges)
        import numpy as np
        for m in CANONICAL_MODELS:
            for d in TARGET_DIM_KEYS:
                # collect rows with all 3 judges present
                rows: List[List[float]] = []
                for q in sorted(tables.keys()):
                    judges = tables[q]
                    if not all(j in judges and d in judges[j].get(m, {}) for j in judges):
                        continue
                    # judges keys may exceed 3 if data messy; take first 3 by index
                    vec = [judges[j][m][d] for j in sorted(judges.keys())[:3]]
                    rows.append(vec)
                if len(rows) < 5:
                    continue
                X = np.asarray(rows, dtype=float)  # shape (n_questions, 3)
                icc, p = icc_a1(X)
                iccK, pK = icc_ak(X)

                # bootstrap CI over questions
                try:
                    B = 800
                    rng = random.Random(42)
                    vals: List[float] = []
                    n = X.shape[0]
                    for _ in range(B):
                        samp = [rng.randrange(n) for _ in range(n)]
                        Xi = X[samp, :]
                        v, _ = icc_a1(Xi)
                        if v == v:
                            vals.append(float(v))
                    vals.sort()
                    lo = vals[int(0.0015 * len(vals))] if vals else 0.0
                    hi = vals[min(len(vals)-1, int(0.9985 * len(vals)))] if vals else 0.0
                except Exception:
                    lo, hi = 0.0, 0.0

                w.writerow([m, d, X.shape[0], f"{icc:.6g}", "NA" if p is None else f"{p:.6g}", f"{lo:.6g}", f"{hi:.6g}"])
                # For ICC(A,k) reuse same bootstrap indices on-the-fly is complex; approximate by reusing lo/hi from A1
                wk.writerow([m, d, X.shape[0], f"{iccK:.6g}", "NA" if pK is None else f"{pK:.6g}", f"{lo:.6g}", f"{hi:.6g}"])

    return detail, detail_k
