from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..constants import HUMAN_CSV_PATH, TARGET_DIM_KEYS, CANONICAL_MODELS, HUMAN_CSV_MODEL_HEADER  # type: ignore
from .stats_utils import icc_a1, icc_ak


def _map_header(header: List[str]):
    from ..loaders import ZH_DIM_TO_KEY  # type: ignore

    col_map: Dict[int, Tuple[str, str]] = {}
    current_model_header: Optional[str] = None
    rev = {v: k for k, v in HUMAN_CSV_MODEL_HEADER.items()}
    for idx, name in enumerate(header):
        if idx < 2:
            continue
        label = (name or "").strip()
        if label and label not in ZH_DIM_TO_KEY:
            current_model_header = label
            continue
        if label in ZH_DIM_TO_KEY and current_model_header:
            dim_key = ZH_DIM_TO_KEY[label]
            canonical = rev.get(current_model_header)
            if canonical in CANONICAL_MODELS and dim_key in TARGET_DIM_KEYS:
                col_map[idx] = (canonical, dim_key)
    return col_map


def _safe_float(cell: str) -> Optional[float]:
    try:
        return float(cell)
    except Exception:
        import re
        m = re.search(r"[-+]?\d*\.?\d+", str(cell or ""))
        return float(m.group(0)) if m else None


def load_human_judge_tables(csv_path: Path) -> Dict[int, Dict[int, Dict[str, Dict[str, float]]]]:
    """
    Return nested dict:
      by_question[q_idx][judge_idx][model][dimension] = score
    judge_idx is 1..3 per question determined by contiguous non-empty rows.
    """
    tables: Dict[int, Dict[int, Dict[str, Dict[str, float]]]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        col_map = _map_header(header)

        last_q: Optional[int] = None
        judge_idx = 0
        for row in r:
            # Identify if this row has any score in mapped columns
            has_any = False
            for col in col_map:
                if col < len(row) and (row[col] or "").strip():
                    has_any = True
                    break

            # Determine question id (forward-fill on non-empty rows)
            q_raw = (row[0] if len(row) > 0 else "").strip()
            if has_any and q_raw:
                import re as _re
                m = _re.search(r"\d+", q_raw)
                if m:
                    q_idx = int(m.group(0))
                    # New question starts → reset judge counter
                    if last_q != q_idx:
                        last_q = q_idx
                        judge_idx = 0
            if not has_any:
                # likely separator row
                continue

            if last_q is None:
                continue

            judge_idx += 1
            tables.setdefault(last_q, {})[judge_idx] = {}

            # Fill model-dim scores for this judge row
            for col, (model, dim) in col_map.items():
                if col >= len(row):
                    continue
                v = _safe_float(row[col])
                if v is None:
                    continue
                tables[last_q][judge_idx].setdefault(model, {})[dim] = v
    return tables


def compute_human_internal_icc(out_dir: Path) -> Path:
    """
    For each (question, dimension), compute ICC(A,1) across the 3 human judges
    using 9 models as targets (rows). Writes detailed CSV and returns its path.
    """
    csv_path = Path(HUMAN_CSV_PATH)
    tables = load_human_judge_tables(csv_path)

    detail = out_dir / "part02_human_internal_icc_by_question_dim.csv"
    detail_k = out_dir / "part02_human_internal_iccAk_by_question_dim.csv"
    rows: List[List[str]] = []
    rows_k: List[List[str]] = []
    header = ["question_idx", "dimension", "n_models", "icc_a1", "icc_p"]
    header_k = ["question_idx", "dimension", "n_models", "icc_ak", "icc_k_p"]

    for q_idx in sorted(tables.keys()):
        judges = tables[q_idx]
        # need at least 3 judges with data
        if len(judges) < 3:
            continue
        # Build matrix per dimension: shape (n_models, 3)
        for dim in TARGET_DIM_KEYS:
            # Collect models that have scores for all 3 judges
            common_models = [
                m
                for m in CANONICAL_MODELS
                if all(dim in judges[j].get(m, {}) for j in judges)
            ]
            if len(common_models) < 3:
                continue
            import numpy as np

            X = []
            for m in common_models:
                X.append([judges[j][m][dim] for j in sorted(judges.keys())[:3]])
            X = np.asarray(X, dtype=float)  # (n_models, 3)
            icc, p = icc_a1(X)
            iccK, pK = icc_ak(X)
            rows.append([
                str(q_idx),
                dim,
                str(len(common_models)),
                f"{icc:.6g}",
                "NA" if p is None else f"{p:.6g}",
            ])
            rows_k.append([
                str(q_idx),
                dim,
                str(len(common_models)),
                f"{iccK:.6g}",
                "NA" if pK is None else f"{pK:.6g}",
            ])

    with detail.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    with detail_k.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header_k)
        w.writerows(rows_k)
    return detail
