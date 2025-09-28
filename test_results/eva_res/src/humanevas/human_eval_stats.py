#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human evaluation analysis: compute TrueSkill ELO and conventional averages.

This script parses the raw human scoring CSV under
`test_results/eva_res/human/` and computes:
- TrueSkill-based ELO (per-dimension and overall via joint modeling)
- Conventional per-model mean and standard deviation

It reuses the TrueSkill match generation and rating logic from
`test_results/eva_res/src/elo_final.py` as much as possible, with light
adaptation for the human rating data format.

Usage:
  python -m test_results.eva_res.src.humanevas.human_eval_stats \
      --input "test_results/eva_res/human/副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv" \
      --outdir "test_results/eva_res/src/humanevas" \
      --match-mode multi

Notes:
- Expects UTF-8 BOM safe CSV (utf-8-sig). The first two columns are treated
  as metadata (e.g., question id and text). Each subsequent group is a model
  name followed by six dimension columns in Chinese.
- Dimensions are mapped to the internal keys used by the LLM analysis code.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Import TrueSkill functions from existing ELO implementation
try:
    # Direct import by path-like sys.path update at runtime
    import sys
    # elo_final.py sits in the sibling folder of this file's directory: .../src/
    SRC_DIR = Path(__file__).resolve().parents[1]
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    from elo_final import TrueSkillELOAnalyzer, DimensionRating, ModelRating  # type: ignore
except Exception as e:  # pragma: no cover - import-time diagnostics
    raise RuntimeError(
        f"Failed to import TrueSkillELOAnalyzer from elo_final.py. Ensure the repo layout is intact. Details: {e}"
    )


# Chinese -> internal dimension key mapping used across the repo
DIM_MAP = {
    "正确性": "correctness",
    "逻辑性": "logic",
    "清晰度": "clarity",
    "完备性": "completeness",
    "理论深度": "theoretical_depth",
    "论述严谨性与信息密度": "rigor_and_information_density",
}

# Use 4 dimensions (exclude logic and clarity)
INTERNAL_DIM_ORDER = [
    "correctness",
    "completeness",
    "theoretical_depth",
    "rigor_and_information_density",
]
ACTIVE_DIM_KEYS = set(INTERNAL_DIM_ORDER)


def parse_human_csv(csv_path: Path) -> Dict[str, Dict[str, Dict[str, Dict[str, float]]]]:
    """
    Parse human scoring CSV and pool all evaluators into one judge, but treat
    each evaluator's row as a separate match by giving unique question ids.

    Effect: for each original question (e.g., 1..27), if there are 3 evaluators,
    you'll get 3 distinct matches per dimension: Q1#1, Q1#2, Q1#3, all under the
    same judge key 'human'. This yields 27*3 matches per dimension.

    Returns: {'human': {model: {question_id_with_suffix: {dimension: score}}}}
    """
    judge_key = "human"
    data: Dict[str, Dict[str, Dict[str, Dict[str, float]]]] = {judge_key: defaultdict(dict)}

    # Build column mapping: index -> (model_name, dim_key)
    # First two columns are metadata (id, question text). From column 2 onward,
    # we expect repeating groups: [model_name, dim1, dim2, ..., dim6, model_name, ...]
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"CSV is empty: {csv_path}")

        col_map: Dict[int, Tuple[str, str]] = {}  # col_idx -> (model, dim_internal)
        current_model: Optional[str] = None

        # Identify the first two metadata columns, then group columns by model
        # Strategy: whenever a header cell is not a known Chinese dimension name
        # and is non-empty, treat it as a model name sentinel. Subsequent known
        # dimension headers map to that model until another sentinel appears.
        for idx, name in enumerate(header):
            if idx < 2:
                continue  # skip metadata columns
            label = (name or "").strip()
            if label and label not in DIM_MAP:
                current_model = label
                continue
            if label in DIM_MAP and current_model:
                dim_key = DIM_MAP[label]
                if dim_key in ACTIVE_DIM_KEYS:
                    col_map[idx] = (current_model, dim_key)

        if not col_map:
            raise ValueError("Failed to map any model/dimension columns from header.\n"
                             f"Header sample: {header[:20]}")

        # Track number of times each question id has been seen (to suffix QID)
        qid_occurrence: Dict[str, int] = defaultdict(int)

        # Read rows and populate data
        for row_idx, row in enumerate(reader, start=1):
            # Basic sanity: require at least the two metadata columns
            if len(row) < 2:
                continue

            # Derive question id; use explicit id in col0 if present, else row index
            qid_raw = (row[0] or "").strip()
            question_id = qid_raw if qid_raw else f"Q{row_idx}"
            qid_occurrence[question_id] += 1
            qid_suffixed = f"{question_id}#{qid_occurrence[question_id]}"

            # For each mapped score column, parse float and store
            per_model_scores: Dict[str, Dict[str, float]] = defaultdict(dict)
            for col_idx, (model, dim_key) in col_map.items():
                if col_idx >= len(row):
                    continue
                cell = (row[col_idx] or "").strip()
                if not cell:
                    continue
                # Robust numeric parsing: extract the first number like 9, 9.5, 10分, 88%
                score = None
                try:
                    score = float(cell)
                except ValueError:
                    import re
                    m = re.search(r"[-+]?\d*\.?\d+", cell)
                    if m:
                        try:
                            score = float(m.group(0))
                        except Exception:
                            score = None
                if score is None:
                    continue
                per_model_scores[model][dim_key] = score

            # Assign into pooled judge structure with suffixed question id
            for model, dim_scores in per_model_scores.items():
                if dim_scores:
                    data[judge_key].setdefault(model, {})
                    data[judge_key][model].setdefault(qid_suffixed, {})
                    data[judge_key][model][qid_suffixed].update(dim_scores)

    # Convert nested defaultdicts to plain dicts for safety
    data[judge_key] = {m: dict(qmap) for m, qmap in data[judge_key].items()}
    return data


def compute_conventional_stats_by_judge(question_dimension_scores: Dict[str, Dict[str, Dict[str, Dict[str, float]]]]) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Compute conventional stats per judge and per model."""
    results: Dict[str, Dict[str, Dict[str, float]]] = {}
    for judge_key, model_map in question_dimension_scores.items():
        judge_rows: Dict[str, Dict[str, float]] = {}
        for model, qmap in model_map.items():
            per_question_averages: List[float] = []
            per_dim_accum: Dict[str, List[float]] = defaultdict(list)

            for _qid, dim_scores in qmap.items():
                vals = [v for k, v in dim_scores.items() if k in INTERNAL_DIM_ORDER]
                if vals:
                    per_question_averages.append(sum(vals) / len(vals))
                for d in INTERNAL_DIM_ORDER:
                    if d in dim_scores:
                        per_dim_accum[d].append(dim_scores[d])

            if not per_question_averages:
                continue

            overall_mean = statistics.mean(per_question_averages)
            overall_std = statistics.stdev(per_question_averages) if len(per_question_averages) > 1 else 0.0

            row = {
                "judge": judge_key,
                "overall_mean": overall_mean,
                "overall_std": overall_std,
                "total_questions": float(len(per_question_averages)),
            }
            for d in INTERNAL_DIM_ORDER:
                if per_dim_accum[d]:
                    row[f"dim_{d}_mean"] = statistics.mean(per_dim_accum[d])
            judge_rows[model] = row
        results[judge_key] = judge_rows
    return results


def compute_conventional_stats_overall(question_dimension_scores: Dict[str, Dict[str, Dict[str, Dict[str, float]]]]) -> Dict[str, Dict[str, float]]:
    """Compute conventional stats across all judges combined per model."""
    # Merge all judges' per-question per-dimension entries
    merged: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for _judge, model_map in question_dimension_scores.items():
        for model, qmap in model_map.items():
            for _qid, dim_scores in qmap.items():
                vals = [v for k, v in dim_scores.items() if k in INTERNAL_DIM_ORDER]
                if vals:
                    merged[model]["overall"].append(sum(vals) / len(vals))
                for d in INTERNAL_DIM_ORDER:
                    if d in dim_scores:
                        merged[model][d].append(dim_scores[d])

    results: Dict[str, Dict[str, float]] = {}
    for model, buckets in merged.items():
        overall_vals = buckets.get("overall", [])
        if not overall_vals:
            continue
        row = {
            "overall_mean": statistics.mean(overall_vals),
            "overall_std": statistics.stdev(overall_vals) if len(overall_vals) > 1 else 0.0,
            "total_questions": float(len(overall_vals)),
        }
        for d in INTERNAL_DIM_ORDER:
            if buckets.get(d):
                row[f"dim_{d}_mean"] = statistics.mean(buckets[d])
        results[model] = row
    return results


def run_human_trueskill(question_dimension_scores: Dict[str, Dict[str, Dict[str, Dict[str, float]]]],
                        outdir: Path,
                        match_mode: str = "multi",
                        beta: Optional[float] = 4.1) -> None:
    """
    Reuse TrueSkillELOAnalyzer to compute per-dimension and overall ratings from
    human scores.
    - Uses aggregation_level="double" since human CSV already provides a single
      score per question-dimension per model.
    - Uses multi-model ranking by default for better utilization of per-question
      score lists across many models.
    """
    analyzer = TrueSkillELOAnalyzer(custom_beta=beta, use_trueskill_default=False, match_mode=match_mode)

    # Generate matches directly from the human scores
    dim_matches = analyzer.generate_dimension_matches(question_dimension_scores, aggregation_level="double")

    # Dimension-wise ratings
    dim_ratings_nested = analyzer.calculate_dimension_trueskill_ratings(dim_matches)
    # Overall ratings via joint modeling across dimensions (for CSV reference)
    overall_ratings_nested = analyzer.calculate_joint_overall_ratings(dim_matches)
    # Aggregated overall ratings from dimension ratings (for MD report compatibility)
    aggregated_overall_ratings = analyzer.aggregate_dimension_ratings(dim_ratings_nested, method="mean")

    # Persist concise CSVs and JSONs
    outdir.mkdir(parents=True, exist_ok=True)

    # Overall per-judge (human) CSV
    for judge, model_map in overall_ratings_nested.items():
        rows = []
        for model, mr in model_map.items():
            # mr is DimensionRating with dimension="overall"
            rows.append({
                "judge": judge,
                "model": model,
                "dimension": getattr(mr, "dimension", "overall"),
                "mu": getattr(mr, "mu", float("nan")),
                "sigma": getattr(mr, "sigma", float("nan")),
                "conservative_rating": getattr(mr, "rating", float("nan")),
                "games": getattr(mr, "games_played", 0),
                "wins": getattr(mr, "wins", 0.0),
                "losses": getattr(mr, "losses", 0.0),
                "win_rate": getattr(mr, "win_rate", float("nan")),
            })

        # Save CSV
        csv_path = outdir / "human_trueskill_overall.csv"
        _write_csv(rows, csv_path)

    # Dimension CSV (flattened)
    dim_rows = []
    for judge, dim_map in dim_ratings_nested.items():
        for dimension, model_map in dim_map.items():
            for model, dr in model_map.items():
                dim_rows.append({
                    "judge": judge,
                    "dimension": dimension,
                    "model": model,
                    "mu": dr.mu,
                    "sigma": dr.sigma,
                    "conservative_rating": dr.rating,
                    "games": dr.games_played,
                    "wins": dr.wins,
                    "losses": dr.losses,
                    "win_rate": dr.win_rate,
                })
    _write_csv(dim_rows, outdir / "human_trueskill_by_dimension.csv")

    # Also dump raw JSON for completeness
    json_dump = {
        "overall": {
            judge: {model: asdict(mr) for model, mr in model_map.items()}
            for judge, model_map in overall_ratings_nested.items()
        },
        "by_dimension": {
            judge: {
                dim: {model: asdict(dr) for model, dr in model_map.items()}
                for dim, model_map in dim_map.items()
            } for judge, dim_map in dim_ratings_nested.items()
        },
        "overall_aggregated": analyzer._serialize_aggregated_ratings(aggregated_overall_ratings)
    }
    (outdir / "human_trueskill_ratings.json").write_text(json.dumps(json_dump, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build a results dict compatible with analyzer.save_trueskill_results to auto-generate MD
    total_matches = sum(len(m) for m in dim_matches.values())
    unique_models = len({model for jmap in overall_ratings_nested.values() for model in jmap.keys()})
    results_payload = {
        "analysis_type": "no_lc",
        "aggregation_level": "double",
        "data_source": "human",
        "repetitions": 1,
        "trueskill_parameters": {
            "mu": analyzer.mu,
            "sigma": analyzer.sigma,
            "beta": analyzer.beta,
            "tau": analyzer.tau,
            "draw_probability": analyzer.draw_probability,
            "beta_estimation_method": f"Manual override: β={analyzer.beta:.3f}"
        },
        "match_statistics": {
            "base_matches_per_repetition": total_matches,
            "total_matches_all_repetitions": total_matches,
            "unique_models": unique_models,
            "judges_count": len(dim_ratings_nested),
            "dimensions_count": len(dim_matches),
            "matches_by_dimension": {dim: len(m) for dim, m in dim_matches.items()},
            "match_type": "Human question-dimension matches (aggregation: double)"
        },
        "dimension_ratings": analyzer._serialize_dimension_ratings(dim_ratings_nested),
        "overall_ratings": analyzer._serialize_aggregated_ratings(aggregated_overall_ratings),
        "repetition_details": []
    }

    # Save JSON and MD report using existing helper
    analyzer.save_trueskill_results(results_payload, str(outdir / "trueskill_human_double_no_lc.json"))


def _write_csv(rows: List[Dict[str, object]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    import argparse

    default_input = Path("test_results/eva_res/human/副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv")
    default_outdir = Path("test_results/eva_res/src/humanevas")

    parser = argparse.ArgumentParser(description="Human evaluation ELO and average statistics")
    parser.add_argument("--input", type=str, default=str(default_input), help="Path to human CSV file")
    parser.add_argument("--outdir", type=str, default=str(default_outdir), help="Output directory for results")
    parser.add_argument("--match-mode", type=str, choices=["1vs1", "multi"], default="multi", help="Match mode for TrueSkill")
    parser.add_argument("--beta", type=float, default=4.1, help="TrueSkill beta value (None to use default)")

    args = parser.parse_args()
    csv_path = Path(args.input)
    outdir = Path(args.outdir)

    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    # 1) Parse human CSV -> question_dimension_scores
    qd_scores = parse_human_csv(csv_path)

    # 2) Conventional averages & std (per judge and overall)
    conv_by_judge = compute_conventional_stats_by_judge(qd_scores)
    rows_by_judge: List[Dict[str, object]] = []
    for judge, model_map in conv_by_judge.items():
        for model, stats_map in model_map.items():
            row = {"judge": judge, "model": model}
            row.update(stats_map)
            rows_by_judge.append(row)
    _write_csv(rows_by_judge, outdir / "human_conventional_stats_by_judge.csv")
    (outdir / "human_conventional_stats_by_judge.json").write_text(
        json.dumps(conv_by_judge, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    conv_overall = compute_conventional_stats_overall(qd_scores)
    rows_overall: List[Dict[str, object]] = []
    for model, stats_map in conv_overall.items():
        row = {"model": model}
        row.update(stats_map)
        rows_overall.append(row)
    _write_csv(rows_overall, outdir / "human_conventional_stats_overall.csv")
    (outdir / "human_conventional_stats_overall.json").write_text(
        json.dumps(conv_overall, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3) TrueSkill ELO from human scores
    beta_val: Optional[float] = args.beta if not (args.beta is None or math.isnan(args.beta)) else None
    run_human_trueskill(qd_scores, outdir=outdir, match_mode=args.match_mode, beta=beta_val)

    print(f"Done. Outputs under: {outdir}")


if __name__ == "__main__":
    main()
