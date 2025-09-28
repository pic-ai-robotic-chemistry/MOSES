from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import List

from .constants import (
    OUT_DIR,
    HUMAN_CSV_PATH,
    LLM_JSONL_PATH,
    TARGET_DIM_KEYS,
    CANONICAL_MODELS,
)
from .loaders import load_human_csv, load_llm_jsonl
from .aggregations import aggregate_human_avg, aggregate_llm, compute_disagreement
from .log_setup import setup_logger


def ensure_out_dir() -> Path:
    out = Path(OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_csv(path: Path, header: List[str], rows: List[list]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    out_dir = ensure_out_dir()
    logger = setup_logger(
        __name__,
        logfile=out_dir / "preprocess.log",
    )

    logger.info("Starting Part 0–1 preprocessing…")
    human_rows = load_human_csv(HUMAN_CSV_PATH)
    llm_rows = load_llm_jsonl(LLM_JSONL_PATH)
    logger.info(
        "Loaded datasets: human_records=%d, llm_records=%d",
        len(human_rows),
        len(llm_rows),
    )

    # Part 0: brief info summary
    summary_lines = []
    summary_lines.append(f"Models (canonical, filtered): {len(CANONICAL_MODELS)} -> {', '.join(CANONICAL_MODELS)}")
    dims_in_llm = sorted({r.dimension for r in llm_rows})
    dims_used = sorted(set(TARGET_DIM_KEYS) & set(dims_in_llm))
    summary_lines.append(f"Dimensions (target ∩ available): {', '.join(dims_used)}")
    q_h = sorted({r.question_idx for r in human_rows})
    q_l = sorted({r.question_idx for r in llm_rows})
    summary_lines.append(f"Questions (unique) — human: {len(q_h)}, llm: {len(q_l)}, overlap: {len(set(q_h)&set(q_l))}")
    (out_dir / "part0_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")
    logger.info("Part 0 summary written: %s", out_dir / "part0_summary.txt")

    # Part 1: aggregates
    human_avg = aggregate_human_avg(human_rows)
    llm_rep, llm_overall = aggregate_llm(llm_rows)
    disag = compute_disagreement(human_avg, llm_overall)

    # Save artifacts
    write_csv(
        out_dir / "human_avg.csv",
        ["model", "question_idx", "dimension", "human_avg"],
        [[h.model, h.question_idx, h.dimension, f"{h.human_avg:.6g}"] for h in human_avg],
    )
    logger.info("Saved: %s (records=%d)", out_dir / "human_avg.csv", len(human_avg))

    write_csv(
        out_dir / "llm_repetition_avg.csv",
        ["model", "question_idx", "dimension", "answer_round", "llm_repetition_avg"],
        [
            [r.model, r.question_idx, r.dimension, r.answer_round, f"{r.llm_repetition_avg:.6g}"]
            for r in llm_rep
        ],
    )
    logger.info("Saved: %s (records=%d)", out_dir / "llm_repetition_avg.csv", len(llm_rep))

    write_csv(
        out_dir / "llm_avg_overall.csv",
        ["model", "question_idx", "dimension", "llm_avg_overall"],
        [[a.model, a.question_idx, a.dimension, f"{a.llm_avg_overall:.6g}"] for a in llm_overall],
    )
    logger.info("Saved: %s (records=%d)", out_dir / "llm_avg_overall.csv", len(llm_overall))

    write_csv(
        out_dir / "disagreement_scores.csv",
        ["model", "question_idx", "dimension", "human_avg", "llm_avg_overall", "disagreement"],
        [
            [d.model, d.question_idx, d.dimension, f"{d.human_avg:.6g}", f"{d.llm_avg_overall:.6g}", f"{d.disagreement:.6g}"]
            for d in disag
        ],
    )
    logger.info("Saved: %s (records=%d)", out_dir / "disagreement_scores.csv", len(disag))

    # Done marker
    (out_dir / "_READY_PART01.txt").write_text("part 0–1 preprocessing complete", encoding="utf-8")
    logger.info("Completed Part 0–1 preprocessing. Marker written: %s", out_dir / "_READY_PART01.txt")


if __name__ == "__main__":
    main()
