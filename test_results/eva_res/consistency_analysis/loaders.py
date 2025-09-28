from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass
import logging
from typing import Dict, Iterable, List, Optional, Tuple

from .constants import (
    CANONICAL_MODELS,
    HUMAN_CSV_MODEL_HEADER,
    LLM_MODEL_NAME,
    ZH_DIM_TO_KEY,
    TARGET_DIM_KEYS,
)


@dataclass
class HumanScore:
    model: str  # canonical
    question_idx: int  # 1-based question index
    dimension: str  # internal dim key
    score: float


@dataclass
class LLMScore:
    model: str  # canonical
    question_idx: int  # parsed from question_id like 'q_12' -> 12
    dimension: str  # internal dim key
    answer_round: int  # 1..5
    evaluation_round: int  # 1..5
    score: float


def _safe_float(cell: str) -> Optional[float]:
    cell = (cell or "").strip()
    if not cell:
        return None
    try:
        return float(cell)
    except ValueError:
        m = re.search(r"[-+]?\d*\.?\d+", cell)
        if m:
            try:
                return float(m.group(0))
            except Exception:
                return None
    return None


logger = logging.getLogger(__name__)


def _normalize_key(k: str) -> str:
    import re
    return re.sub(r"[^a-z]", "", (k or "").lower())


_TARGET_NORM_MAP = {
    "correctness": "correctness",
    "completeness": "completeness",
    "theoreticaldepth": "theoretical_depth",
    "rigorandinformationdensity": "rigor_and_information_density",
}


def _lenient_extract_target_scores(text: str) -> Dict[str, float]:
    """Regex-based fallback to salvage target dims from messy text."""
    patterns = {
        "correctness": [r"(?i)\bcorrectness\b\s*[:=]\s*([-+]?\d*\.?\d+)"],
        "completeness": [r"(?i)\bcompleteness\b\s*[:=]\s*([-+]?\d*\.?\d+)"],
        "theoretical_depth": [r"(?i)\btheoretical[_\s-]*depth\b\s*[:=]\s*([-+]?\d*\.?\d+)"],
        "rigor_and_information_density": [
            r"(?i)\brig(or|our)[_\s-]*(and|&)?[_\s-]*information[_\s-]*density\b\s*[:=]\s*([-+]?\d*\.?\d+)",
        ],
    }
    out: Dict[str, float] = {}
    for dim, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, text)
            if m:
                try:
                    num = float(m.groups()[-1])
                except Exception:
                    num = None
                if num is not None:
                    out[dim] = num
                    break
    return out


def load_human_csv(csv_path: str) -> List[HumanScore]:
    """
    Parse the human aggregated CSV. The format is:
    - First two columns: metadata (id, question text)
    - Then repeating groups per model:
        [model_name_header, 正确性, 逻辑性, 清晰度, 完备性, 理论深度, 论述严谨性与信息密度]
    We keep only TARGET_DIM_KEYS and only CANONICAL_MODELS.
    """
    results: List[HumanScore] = []

    logger.info(f"Loading human CSV: {csv_path}")
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        # Build a map: column index -> (canonical_model, dim_key)
        col_map: Dict[int, Tuple[str, str]] = {}
        current_model_header: Optional[str] = None

        # Reverse map for quick lookup human header -> canonical
        human_header_to_canonical = {v: k for k, v in HUMAN_CSV_MODEL_HEADER.items()}

        mapped_models: List[str] = []
        unmapped_model_headers: List[str] = []

        for idx, name in enumerate(header):
            if idx < 2:
                continue
            label = (name or "").strip()
            if label and label not in ZH_DIM_TO_KEY:
                # Likely a model header sentinel
                current_model_header = label
                if current_model_header not in human_header_to_canonical:
                    unmapped_model_headers.append(current_model_header)
                continue
            if label in ZH_DIM_TO_KEY and current_model_header:
                dim_key = ZH_DIM_TO_KEY[label]
                canonical = human_header_to_canonical.get(current_model_header)
                if canonical in CANONICAL_MODELS and dim_key in TARGET_DIM_KEYS:
                    col_map[idx] = (canonical, dim_key)
                    if canonical not in mapped_models:
                        mapped_models.append(canonical)

        logger.info(
            "Human CSV header mapped: %d score columns across models=%s, dims=%s",
            len(col_map),
            mapped_models,
            TARGET_DIM_KEYS,
        )
        if unmapped_model_headers:
            logger.warning("Human CSV contains unmapped model headers (ignored): %s", sorted(set(unmapped_model_headers)))

        # Iterate rows
        total_rows = 0
        nonempty_rows = 0
        cells_parsed = 0
        cells_skipped_empty = 0
        cells_skipped_non_numeric = 0
        skipped_samples: List[str] = []

        last_q_idx: Optional[int] = None

        for row_idx, row in enumerate(reader, start=1):
            total_rows += 1
            # question index forward-fill using last seen non-empty id
            qid_raw = (row[0] if len(row) > 0 else "").strip()
            q_idx: Optional[int] = None
            if qid_raw:
                m_q = re.search(r"\d+", qid_raw)
                if m_q:
                    q_idx = int(m_q.group(0))
                    last_q_idx = q_idx
            if q_idx is None:
                # If first column empty (e.g., separator or same-question other judge), use last seen
                q_idx = last_q_idx

            row_had_value = False
            for col, (canonical, dim) in col_map.items():
                if col >= len(row):
                    continue
                raw_cell = row[col] if col < len(row) else ""
                val = _safe_float(raw_cell)
                if val is None:
                    if (raw_cell or "").strip():
                        cells_skipped_non_numeric += 1
                        if len(skipped_samples) < 5:
                            skipped_samples.append(raw_cell[:120])
                    else:
                        cells_skipped_empty += 1
                    continue
                results.append(HumanScore(model=canonical, question_idx=q_idx, dimension=dim, score=val))
                cells_parsed += 1
                row_had_value = True

            if row_had_value:
                nonempty_rows += 1

    logger.info(
        "Human CSV loaded: rows=%d (nonempty=%d), parsed_cells=%d, empty_cells=%d, non_numeric_cells=%d, records=%d",
        total_rows,
        nonempty_rows,
        cells_parsed,
        cells_skipped_empty,
        cells_skipped_non_numeric,
        len(results),
    )
    if skipped_samples:
        logger.info("Human CSV non-numeric sample cells (up to 5): %s", skipped_samples)
    # Expected cells only counts non-empty rows × mapped score columns
    expected_cells = nonempty_rows * len(col_map)
    logger.info(
        "Human CSV expected target cells=%d (= rows %d × mapped_score_columns %d)",
        expected_cells,
        nonempty_rows,
        len(col_map),
    )
    # Quick distinct stats
    models = sorted({r.model for r in results})
    dims = sorted({r.dimension for r in results})
    qcnt = len({r.question_idx for r in results})
    logger.info("Human coverage — models=%s, dims=%s, questions=%d", models, dims, qcnt)

    return results


def _parse_answer_scores(answer_text: str) -> Optional[Dict[str, float]]:
    """Extract scores dict from `answer` string which may include code fences."""
    if not answer_text:
        return None
    text = answer_text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        # remove first fence line
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1 :]
        # remove trailing ``` if present
        if text.endswith("```"):
            text = text[: -3]
    text = text.strip()
    try:
        obj = json.loads(text)
    except Exception:
        # try to locate first {...} block
        try:
            s = text.find("{")
            e = text.rfind("}")
            if s != -1 and e != -1 and e > s:
                obj = json.loads(text[s : e + 1])
            else:
                return None
        except Exception:
            return None
    if not isinstance(obj, dict):
        return None
    out: Dict[str, float] = {}
    for k, v in obj.items():
        if not isinstance(k, str):
            continue
        nk = _normalize_key(k)
        if nk in _TARGET_NORM_MAP:
            key = _TARGET_NORM_MAP[nk]
            num = None
            try:
                num = float(v)
            except Exception:
                num = _safe_float(str(v))
            if num is not None:
                out[key] = num
    return out


def load_llm_jsonl(jsonl_path: str) -> List[LLMScore]:
    """
    Parse the LLM individual evaluation JSONL file.
    We expect one JSON object per line with keys including:
      model_name, question_id (e.g., 'q_12'), answer_round ('1'..'5' or int),
      evaluation_round (int), dimensions (list of keys), and answer (JSON string with scores).

    We keep only CANONICAL_MODELS and dimensions intersecting TARGET_DIM_KEYS.
    """
    logger.info(f"Loading LLM JSONL: {jsonl_path}")
    results: List[LLMScore] = []
    model_lookup = {v: k for k, v in LLM_MODEL_NAME.items()}  # json model_name -> canonical

    # Some files can be large; stream line by line
    total_lines = 0
    json_errors = 0
    model_filtered = 0
    missing_qid = 0
    score_objects_missing_bad_json = 0
    score_objects_missing_only_nontarget = 0
    scores_parsed = 0
    dims_count = {k: 0 for k in TARGET_DIM_KEYS}
    dims_per_line_hist = {}  # dim_count -> occurrences
    kept_lines = 0
    models_set = set()
    questions_set = set()
    ans_rounds_set = set()
    eva_rounds_set = set()
    fallback_recovered = 0

    filtered_model_names = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except Exception:
                json_errors += 1
                continue

            json_model = (obj.get("model_name") or "").strip()
            canonical = model_lookup.get(json_model)
            if canonical not in CANONICAL_MODELS:
                model_filtered += 1
                # Track raw names for diagnostics
                filtered_model_names[json_model] = filtered_model_names.get(json_model, 0) + 1
                continue

            qid = (obj.get("question_id") or "").strip()
            # Extract trailing integer index from e.g., 'q_12'
            m = re.search(r"(\d+)$", qid)
            if not m:
                missing_qid += 1
                continue
            question_idx = int(m.group(1))

            # Round identifiers
            try:
                answer_round = int(obj.get("answer_round"))
            except Exception:
                # Accept strings like '1' or 'A1'
                m2 = re.search(r"\d+", str(obj.get("answer_round") or ""))
                answer_round = int(m2.group(0)) if m2 else 1
            try:
                evaluation_round = int(obj.get("evaluation_round"))
            except Exception:
                evaluation_round = 1

            # Scores are embedded in the 'answer' field as JSON text
            scores_raw = obj.get("answer") or ""
            parsed_scores = _parse_answer_scores(scores_raw)
            if parsed_scores is None:
                # Try lenient regex fallback
                fallback = _lenient_extract_target_scores(scores_raw)
                if not fallback:
                    score_objects_missing_bad_json += 1
                    continue
                parsed_scores = fallback
                fallback_recovered += sum(1 for _ in fallback)
            scores = parsed_scores or {}

            # Only keep target dims that exist in the file
            per_line_dim_added = 0
            for dim in TARGET_DIM_KEYS:
                if dim not in scores:
                    continue
                try:
                    score_val = float(scores[dim])
                except Exception:
                    continue
                results.append(
                    LLMScore(
                        model=canonical,
                        question_idx=question_idx,
                        dimension=dim,
                        answer_round=answer_round,
                        evaluation_round=evaluation_round,
                        score=score_val,
                    )
                )
                scores_parsed += 1
                dims_count[dim] += 1
                per_line_dim_added += 1

            if per_line_dim_added > 0:
                kept_lines += 1
                dims_per_line_hist[per_line_dim_added] = dims_per_line_hist.get(per_line_dim_added, 0) + 1
                models_set.add(canonical)
                questions_set.add(question_idx)
                ans_rounds_set.add(answer_round)
                eva_rounds_set.add(evaluation_round)
            else:
                # Parsed but none of the target dims present
                dims_in_meta = [str(d).lower() for d in (obj.get("dimensions") or [])]
                if dims_in_meta and set(dims_in_meta).issubset({"logic", "clarity"}):
                    score_objects_missing_only_nontarget += 1
                else:
                    score_objects_missing_bad_json += 1

    logger.info(
        "LLM JSONL loaded: lines=%d, json_errors=%d, model_filtered=%d, missing_qid=%d, scores_parsed=%d, records=%d",
        total_lines,
        json_errors,
        model_filtered,
        missing_qid,
        scores_parsed,
        len(results),
    )
    if filtered_model_names:
        # Log top filtered names
        top = sorted(filtered_model_names.items(), key=lambda x: -x[1])[:10]
        logger.info("LLM filtered (non-target) model_name counts (top10): %s", dict(top))
    if score_objects_missing_bad_json or score_objects_missing_only_nontarget:
        logger.info(
            "LLM entries lacking usable target dims — bad_answer_json=%d, only_non_target_dims=%d, fallback_recovered_values=%d",
            score_objects_missing_bad_json,
            score_objects_missing_only_nontarget,
            fallback_recovered,
        )
    # Report model_name frequencies actually seen
    try:
        from collections import Counter

        model_freq = Counter([r.model for r in results])
        logger.info("LLM records per canonical model: %s", dict(sorted(model_freq.items())))
    except Exception:
        pass
    logger.info("LLM per-dimension record counts: %s", {k: v for k, v in dims_count.items() if v})
    logger.info("LLM lines kept with target dims: %d; dims_per_line_hist=%s", kept_lines, dict(sorted(dims_per_line_hist.items())))
    # Quick distinct stats
    models = sorted({r.model for r in results})
    dims = sorted({r.dimension for r in results})
    qcnt = len({r.question_idx for r in results})
    logger.info("LLM coverage — models=%s, dims=%s, questions=%d", models, dims, qcnt)

    # Report a theoretical completeness upper bound based on observed unique sets
    # Expectation (if fully dense): |models| * |questions| * |answer_rounds| * |evaluation_rounds| * 4 dims
    theoretical_max = len(models_set) * len(questions_set) * len(ans_rounds_set) * len(eva_rounds_set) * 4
    if theoretical_max:
        logger.info(
            "LLM theoretical max records based on observed axes: %d (=%d*%d*%d*%d*4)",
            theoretical_max,
            len(models_set),
            len(questions_set),
            len(ans_rounds_set),
            len(eva_rounds_set),
        )
        logger.info(
            "LLM observed round sets: answer_rounds=%s, evaluation_rounds=%s",
            sorted(ans_rounds_set),
            sorted(eva_rounds_set),
        )
        if len(results) < theoretical_max:
            logger.warning(
                "LLM observed records (%d) < theoretical max (%d). Missing entries likely due to absent dims per line; see dims_per_line_hist.",
                len(results),
                theoretical_max,
            )

    return results
