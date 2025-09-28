from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable, List, Tuple

from .loaders import HumanScore, LLMScore


@dataclass
class HumanAvg:
    model: str
    question_idx: int
    dimension: str
    human_avg: float


@dataclass
class LLMRepetitionAvg:
    model: str
    question_idx: int
    dimension: str
    answer_round: int
    llm_repetition_avg: float


@dataclass
class LLMAggregate:
    model: str
    question_idx: int
    dimension: str
    llm_avg_overall: float


@dataclass
class Disagreement:
    model: str
    question_idx: int
    dimension: str
    human_avg: float
    llm_avg_overall: float
    disagreement: float  # llm - human


def aggregate_human_avg(rows: Iterable[HumanScore]) -> List[HumanAvg]:
    # Human CSV already contains a single aggregated score per dimension.
    # If duplicates appear, average them just in case.
    acc: Dict[Tuple[str, int, str], List[float]] = defaultdict(list)
    for r in rows:
        acc[(r.model, r.question_idx, r.dimension)].append(r.score)
    out: List[HumanAvg] = []
    for (model, q_idx, dim), vals in acc.items():
        out.append(HumanAvg(model, q_idx, dim, mean(vals)))
    return out


def aggregate_llm(rows: Iterable[LLMScore]) -> Tuple[List[LLMRepetitionAvg], List[LLMAggregate]]:
    # Group by (model, q, dim, answer_round) to compute repetition avg over evaluation_round
    rep_acc: Dict[Tuple[str, int, str, int], List[float]] = defaultdict(list)
    for r in rows:
        rep_acc[(r.model, r.question_idx, r.dimension, r.answer_round)].append(r.score)

    rep_avgs: List[LLMRepetitionAvg] = []
    for (model, q_idx, dim, a_round), vals in rep_acc.items():
        rep_avgs.append(LLMRepetitionAvg(model, q_idx, dim, a_round, mean(vals)))

    # Overall average: by (model, q, dim) across all answer_rounds and eval rounds (i.e., all values)
    overall_acc: Dict[Tuple[str, int, str], List[float]] = defaultdict(list)
    for r in rows:
        overall_acc[(r.model, r.question_idx, r.dimension)].append(r.score)

    overall_avgs: List[LLMAggregate] = []
    for (model, q_idx, dim), vals in overall_acc.items():
        overall_avgs.append(LLMAggregate(model, q_idx, dim, mean(vals)))

    return rep_avgs, overall_avgs


def compute_disagreement(human: Iterable[HumanAvg], llm_overall: Iterable[LLMAggregate]) -> List[Disagreement]:
    human_map: Dict[Tuple[str, int, str], float] = {
        (h.model, h.question_idx, h.dimension): h.human_avg for h in human
    }
    out: List[Disagreement] = []
    for a in llm_overall:
        key = (a.model, a.question_idx, a.dimension)
        if key not in human_map:
            continue
        hv = human_map[key]
        out.append(
            Disagreement(
                model=a.model,
                question_idx=a.question_idx,
                dimension=a.dimension,
                human_avg=hv,
                llm_avg_overall=a.llm_avg_overall,
                disagreement=a.llm_avg_overall - hv,
            )
        )
    return out

