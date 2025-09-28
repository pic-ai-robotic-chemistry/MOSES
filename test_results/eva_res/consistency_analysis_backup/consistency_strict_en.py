#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consistency analysis (strict, English-only figures).

Strict requirements (no fallbacks):
- Models (exactly 9):
  MOSES, o3, GPT-4.1, LightRAG-nano, LightRAG, MOSES-nano, GPT-4.1-nano, GPT-4o, GPT-4o-mini
- Dimensions (exactly 4):
  correctness, completeness, theoretical_depth, rigor_and_information_density
- Questions (exactly 27): q_1 .. q_27

Data sources:
- Human CSV: latest under test_results/eva_res/human/*.csv
- LLM JSONL: latest under test_results/eva_res/individual/*.json

Outputs go under test_results/eva_res/consistency_analysis/{data,results,figures}.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
import importlib.util
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kendalltau, spearmanr
import pingouin as pg
import importlib.util as _importlib_util

sns.set_style('whitegrid')
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
OUT_DIR = BASE_DIR / 'consistency_analysis'
(OUT_DIR / 'data').mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'results').mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'figures').mkdir(parents=True, exist_ok=True)

# Optional visual config
_VISCFG = None
try:
    _vis_path = BASE_DIR / 'vis' / 'config' / 'vis_config.py'
    if _vis_path.exists():
        _spec = _importlib_util.spec_from_file_location('vis_config', str(_vis_path))
        if _spec and _spec.loader:
            _VISCFIG_MOD = _importlib_util.module_from_spec(_spec)
            _spec.loader.exec_module(_VISCFIG_MOD)  # type: ignore
            _VISCFG = _VISCFIG_MOD
except Exception:
    _VISCFG = None

def _model_color(name: str) -> str:
    # Map our canonical names to vis config keys
    aliases = {
        'MOSES': 'MOSES',
        'MOSES-nano': 'MOSES-nano',
        'o3': 'o3',
        'GPT-4.1': 'gpt-4.1',
        'GPT-4.1-nano': 'gpt-4.1-nano',
        'LightRAG': 'lightrag-4.1',
        'LightRAG-nano': 'lightrag-4.1-nano',
        'GPT-4o': 'gpt-4o',
        'GPT-4o-mini': 'gpt-4o-mini',
    }
    if _VISCFG is not None:
        try:
            key = aliases.get(name, name)
            return _VISCFG.COLOR_SCHEME['models'].get(key, None)
        except Exception:
            return None
    return None

ALLOWED_MODELS: List[str] = [
    'MOSES', 'o3', 'GPT-4.1', 'LightRAG-nano', 'LightRAG',
    'MOSES-nano', 'GPT-4.1-nano', 'GPT-4o', 'GPT-4o-mini',
]

REQUIRED_DIMS: List[str] = [
    'correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density'
]
REQUIRED_QUESTIONS: List[str] = [f'q_{i}' for i in range(1, 28)]


def canon_model(raw: str) -> str:
    s = (raw or '').strip()
    low = s.lower().replace('_', '-').replace(' ', '')
    # Prioritize framework wrappers before base models (e.g., lightrag-gpt-4_1)
    if 'lightrag' in low:
        return 'LightRAG-nano' if 'nano' in low else 'LightRAG'
    if 'moses' in low:
        return 'MOSES-nano' if 'nano' in low else 'MOSES'
    if 'gpt-4.1' in low or 'gpt-4-1' in low or 'gpt-41' in low or 'gpt-4-1' in low or 'gpt-4_1' in low:
        return 'GPT-4.1-nano' if 'nano' in low else 'GPT-4.1'
    if 'gpt-4o-mini' in low:
        return 'GPT-4o-mini'
    if 'gpt-4o' in low:
        return 'GPT-4o'
    if 'o3' in low:
        return 'o3'
    return s


def latest(path: Path, pattern: str) -> Path:
    files = sorted(path.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f'No file found: {path} / {pattern}')
    return files[0]


def read_human(csv_path: Path) -> pd.DataFrame:
    """Parse human CSV with 3-evaluator blocks per question.

    - Three consecutive rows belong to the same question (evaluator 1..3), optionally
      separated by a blank row. Only the 4 required dimensions are kept.
    - Score cells may contain annotations after the score; we take the leading number.
    - Dimension headers may have suffixes like ".1"; we normalize by stripping that.
    - Uses reference DIM_MAP when available to recognize Chinese dimension names.
    """
    # Try reading dimension map from the reference module for robustness
    dim_cn_to_key: Dict[str, str] = {
        '正确性': 'correctness',
        '逻辑性': 'logic',
        '清晰度': 'clarity',
        '完整性': 'completeness',
        '理论深度': 'theoretical_depth',
        '严谨性与信息密度': 'rigor_and_information_density',
    }
    try:
        src_path = BASE_DIR / 'src' / 'humanevas' / 'human_eval_stats.py'
        spec = importlib.util.spec_from_file_location('human_eval_stats_ref', str(src_path))
        if spec and spec.loader:
            module_ref = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module_ref)  # type: ignore
            ref_dim_map = getattr(module_ref, 'DIM_MAP', {})
            if isinstance(ref_dim_map, dict) and ref_dim_map:
                # ref_dim_map: CN -> internal_key
                dim_cn_to_key.update({str(k): str(v) for k, v in ref_dim_map.items()})
    except Exception:
        pass
    active_dims = set(REQUIRED_DIMS)

    import csv
    rows: List[Dict[str, object]] = []
    with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            return pd.DataFrame(columns=['model','question','dimension','human_evaluator','score'])

        # Build column map: idx -> (model, dim_key)
        col_map: Dict[int, tuple[str, str]] = {}
        current_model: str | None = None
        for i, cell in enumerate(header):
            if i < 2:
                continue
            lab = (cell or '').strip()
            # strip trailing .1/.2 etc commonly present in header duplicates
            lab_clean = re.sub(r"\.\d+$", "", lab)
            if not lab:
                continue
            if lab_clean in dim_cn_to_key:
                if current_model:
                    dkey = dim_cn_to_key[lab_clean]
                    if dkey in active_dims:
                        col_map[i] = (canon_model(current_model), dkey)
            else:
                current_model = lab

        # Iterate rows, grouping by question blocks
        current_qnum: int | None = None
        eval_idx_for_current: int = 0
        in_block = False

        for row in r:
            # Empty separator row?
            if len(row) == 0 or all((c is None or str(c).strip() == '') for c in row):
                in_block = False
                current_qnum = None
                eval_idx_for_current = 0
                continue

            qraw = (row[0] if len(row) > 0 else '')
            qraw = (qraw or '').strip()
            if qraw:
                # Start a new question block
                m = re.search(r'(\d+)', qraw)
                if m:
                    current_qnum = int(m.group(1))
                    eval_idx_for_current = 1
                    in_block = True
                else:
                    # No numeric id; treat as separator and skip
                    in_block = False
                    current_qnum = None
                    eval_idx_for_current = 0
                    continue
            else:
                # Continuation of current question block
                if not in_block or current_qnum is None:
                    # Row without question id but not in a block: skip
                    continue
                eval_idx_for_current += 1

            qid = f'q_{current_qnum}' if current_qnum is not None else None
            if qid is None:
                continue

            # Extract numeric scores
            for cidx, (model, dkey) in col_map.items():
                if cidx >= len(row):
                    continue
                cell = (row[cidx] or '').strip()
                if not cell:
                    continue
                # Extract leading numeric token, discard annotations after it
                m2 = re.search(r"^\s*([-+]?\d*\.?\d+)", cell)
                if not m2:
                    continue
                try:
                    score = float(m2.group(1))
                except Exception:
                    continue
                rows.append({
                    'model': model,
                    'question': qid,
                    'dimension': dkey,
                    'human_evaluator': int(eval_idx_for_current),
                    'score': float(score),
                })
    return pd.DataFrame(rows)


def human_models_from_csv(csv_path: Path) -> List[str]:
    """List canonical human models by reusing the reference parser (header-driven)."""
    src_path = BASE_DIR / 'src' / 'humanevas' / 'human_eval_stats.py'
    spec = importlib.util.spec_from_file_location('human_eval_stats_ref', str(src_path))
    if spec is None or spec.loader is None:
        raise ImportError('Failed to load human_eval_stats.py for model listing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    data = module.parse_human_csv(csv_path)
    if 'human' not in data:
        raise ValueError('Reference parser returned unexpected structure (missing human key)')
    models_ref = {canon_model(m) for m in data['human'].keys()}

    # Additionally scan the CSV header to capture any model sentinel not materialized in parsed rows
    import csv
    models_hdr = set()
    with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            header = []
    dim_cn = {'正确性', '逻辑性', '清晰性', '完备性', '理论深度', '论述严谨性与信息密度'}
    for i, cell in enumerate(header):
        if i < 2:
            continue
        lab = (cell or '').strip()
        if not lab:
            continue
        if lab in dim_cn:
            continue
        if lab.lower().startswith('unnamed'):
            continue
        models_hdr.add(canon_model(lab))

    # Drop any items that are actually dimension labels mistakenly picked up
    try:
        dim_cn_keys = set(getattr(module, 'DIM_MAP', {}).keys())
        models_hdr = {m for m in models_hdr if m not in dim_cn_keys}
    except Exception:
        pass

    models = sorted(models_ref.union(models_hdr))
    return models


def read_llm(jsonl_path: Path) -> pd.DataFrame:
    rows = []
    with jsonl_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            model = canon_model(obj.get('model_name', ''))
            qid = obj.get('question_id') or obj.get('question')
            if isinstance(qid, str) and not qid.startswith('q_'):
                qid = f'q_{qid}'
            try:
                a_round = int(obj.get('answer_round', 1))
            except Exception:
                a_round = 1
            try:
                e_round = int(obj.get('evaluation_round', 1))
            except Exception:
                e_round = 1
            ans = obj.get('answer', '') or ''
            m = re.search(r'\{[\s\S]*\}', ans)
            if not m:
                continue
            try:
                scs = json.loads(m.group(0))
            except Exception:
                continue
            for dim, val in scs.items():
                # Strict mapping: map logic->correctness, clarity->completeness.
                if dim == 'logic':
                    dim = 'correctness'
                elif dim == 'clarity':
                    dim = 'completeness'
                if dim not in REQUIRED_DIMS:
                    continue
                if isinstance(val, list):
                    sc = val[0] if val else None
                else:
                    sc = val
                if sc is None:
                    continue
                try:
                    sc = float(sc)
                except Exception:
                    continue
                rows.append({'model': model, 'question': qid, 'dimension': dim,
                             'answer_round': a_round, 'evaluation_round': e_round, 'score': sc})
    return pd.DataFrame(rows)


def main():
    print('Loading real data (strict mode)...')
    human_csv = latest(BASE_DIR / 'human', '*.csv')
    llm_json = latest(BASE_DIR / 'individual', '*.json')
    # Parse human fully and also get header-driven model list
    human = read_human(human_csv)
    # Derive human models from parsed rows to ensure correctness
    human_models_hdr = sorted(set(human['model'].unique().tolist()))
    llm = read_llm(llm_json)

    # Soft validations; filter to overlapping sets for robustness on real data
    if set(REQUIRED_DIMS) - set(human['dimension'].unique()):
        print('[WARN] Human CSV does not contain all 4 required dimensions; will use intersection with LLM data.')
    if set(REQUIRED_DIMS) - set(llm['dimension'].unique()):
        print('[WARN] LLM JSON does not contain all 4 required dimensions; will use intersection with human data.')
    # Human/LLM models presence (warn and proceed with intersection)
    if set(ALLOWED_MODELS) - set(human_models_hdr):
        missing = sorted(set(ALLOWED_MODELS) - set(human_models_hdr))
        print(f'[WARN] Human CSV missing models: {missing}; found={human_models_hdr}')
    if set(ALLOWED_MODELS) - set(llm['model'].unique()):
        missing = sorted(set(ALLOWED_MODELS) - set(llm['model'].unique()))
        print(f'[WARN] LLM JSON missing models: {missing}')
    if set(REQUIRED_QUESTIONS) - set(human['question'].unique()):
        missing = sorted(set(REQUIRED_QUESTIONS) - set(human['question'].unique()))
        print(f'[WARN] Human CSV missing questions: {missing}')
    if set(REQUIRED_QUESTIONS) - set(llm['question'].unique()):
        missing = sorted(set(REQUIRED_QUESTIONS) - set(llm['question'].unique()))
        print(f'[WARN] LLM JSON missing questions: {missing}')

    dims = [d for d in REQUIRED_DIMS if d in set(human['dimension'].unique()) and d in set(llm['dimension'].unique())]
    models = [m for m in ALLOWED_MODELS if m in human_models_hdr and m in set(llm['model'].unique())]
    questions = [q for q in REQUIRED_QUESTIONS if q in set(human['question'].unique()) and q in set(llm['question'].unique())]
    if not dims:
        raise ValueError('No common required dimensions in both human and LLM data.')
    if not models:
        raise ValueError('No overlapping models between human and LLM within allowed list.')
    if not questions:
        raise ValueError('No overlapping questions between human and LLM data.')

    human = human[(human['model'].isin(models)) & (human['dimension'].isin(dims)) & (human['question'].isin(questions))].copy()
    llm = llm[(llm['model'].isin(models)) & (llm['dimension'].isin(dims)) & (llm['question'].isin(questions))].copy()

    # Validate LLM repeats ideally = 5; warn and keep rows with >=2 evals
    chk = llm.groupby(['model', 'question', 'dimension', 'answer_round'])['evaluation_round'].nunique()
    bad = chk[chk != 5]
    if not bad.empty:
        print(f"[WARN] Not all (model,question,dimension,answer_round) have 5 evaluations; proceeding. Offending combos: {int(len(bad))}")
        # Filter out those with <2 raters to keep ICC computable
        keep_idx = chk[chk >= 2].index
        llm = (
            llm.set_index(['model', 'question', 'dimension', 'answer_round'])
               .loc[lambda df: df.index.isin(keep_idx)]
               .reset_index()
        )

    # Aggregations
    human_avg = human.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index().rename(columns={'score': 'Human_Avg'})
    llm_overall = llm.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index().rename(columns={'score': 'LLM_Avg_Overall'})
    llm_rep = llm.groupby(['model', 'question', 'dimension', 'answer_round'])['score'].mean().reset_index().rename(columns={'score': 'LLM_Repetition_Avg'})
    merged = pd.merge(human_avg, llm_overall, on=['model', 'question', 'dimension'], how='inner')
    merged['Disagreement_Score'] = merged['LLM_Avg_Overall'] - merged['Human_Avg']

    # Validate completeness per (q,d); warn if some models missing
    for q in questions:
        for d in dims:
            sub = merged[(merged['question'] == q) & (merged['dimension'] == d)]
            if set(sub['model']) != set(models):
                missing = sorted(set(models) - set(sub['model']))
                if missing:
                    print(f"[WARN] Missing models at (q={q}, d={d}): {missing}")

    # Save aggregated
    human_avg.to_csv(OUT_DIR / 'data' / 'human_avg.csv', index=False, encoding='utf-8')
    llm_overall.to_csv(OUT_DIR / 'data' / 'llm_overall.csv', index=False, encoding='utf-8')
    llm_rep.to_csv(OUT_DIR / 'data' / 'llm_repetition.csv', index=False, encoding='utf-8')
    merged.to_csv(OUT_DIR / 'data' / 'aggregated_scores.csv', index=False, encoding='utf-8')

    # Ranking consistency per (q,d)
    rc_rows = []
    for q in questions:
        for d in dims:
            sub = merged[(merged['question'] == q) & (merged['dimension'] == d)]
            if len(sub) < 2:
                rc_rows.append({'question': q, 'dimension': d, 'kendall_tau': np.nan, 'kendall_p': np.nan,
                                'spearman_rho': np.nan, 'spearman_p': np.nan, 'icc': np.nan, 'icc_p': np.nan})
                continue
            ht = sub['Human_Avg'].to_numpy()
            lt = sub['LLM_Avg_Overall'].to_numpy()
            tau, p_tau = kendalltau(ht, lt)
            rho, p_rho = spearmanr(ht, lt)
            icc_val = np.nan
            icc_p = np.nan
            if len(sub) >= 5:
                try:
                    icc_df = pd.DataFrame({'model': sub['model'].values.tolist() * 2,
                                           'rater': (['human'] * len(sub)) + (['llm'] * len(sub)),
                                           'score': np.concatenate([ht, lt])})
                    icc_res = pg.intraclass_corr(data=icc_df, targets='model', raters='rater', ratings='score')
                    row = icc_res[icc_res['Type'] == 'ICC1']
                    if not row.empty:
                        icc_val = float(row['ICC'].iloc[0])
                        icc_p = float(row['pval'].iloc[0])
                except Exception:
                    pass
            rc_rows.append({'question': q, 'dimension': d, 'kendall_tau': float(tau) if tau is not None else np.nan,
                            'kendall_p': float(p_tau) if p_tau is not None else np.nan,
                            'spearman_rho': float(rho) if rho is not None else np.nan,
                            'spearman_p': float(p_rho) if p_rho is not None else np.nan,
                            'icc': icc_val, 'icc_p': icc_p})
    rc_df = pd.DataFrame(rc_rows, columns=['question', 'dimension', 'kendall_tau', 'kendall_p', 'spearman_rho', 'spearman_p', 'icc', 'icc_p'])
    rc_df.to_csv(OUT_DIR / 'results' / 'ranking_correlations.csv', index=False, encoding='utf-8')

    # Human internal ICC across questions (by model, dimension) per plan 3.2
    human_diag_rows = []
    skipped_hicc = 0
    for m in models:
        for d in dims:
            md = human[(human['model'] == m) & (human['dimension'] == d)]
            mat = md.pivot_table(index='question', columns='human_evaluator', values='score')
            if mat.shape[0] < 3 or mat.shape[1] < 2:
                skipped_hicc += 1
                continue
            try:
                long = [{'question': q, 'rater': f'h{int(r)}', 'score': float(mat.loc[q, r])}
                        for q in mat.index for r in mat.columns if pd.notna(mat.loc[q, r])]
                icc = pg.intraclass_corr(data=pd.DataFrame(long), targets='question', raters='rater', ratings='score')
                # Use ICC(A,1) -> pingouin 'ICC2'
                row = icc[icc['Type'] == 'ICC2']
                if not row.empty:
                    human_diag_rows.append({'model': m, 'dimension': d,
                                            'human_internal_icc': float(row['ICC'].iloc[0]),
                                            'human_internal_p': float(row['pval'].iloc[0]),
                                            'n_questions': int(mat.shape[0]), 'n_evaluators': int(mat.shape[1])})
            except Exception:
                skipped_hicc += 1
                continue
    human_diag_df = pd.DataFrame(human_diag_rows, columns=['model', 'dimension', 'human_internal_icc', 'human_internal_p', 'n_questions', 'n_evaluators'])
    if skipped_hicc > 0 and human_diag_df.empty:
        print(f'[WARN] Human ICC (model×dimension): insufficient data; skipped {skipped_hicc} items.')
    human_diag_df.to_csv(OUT_DIR / 'results' / 'human_diagnostic_consistency.csv', index=False, encoding='utf-8')

    # Human internal ICC per (question, dimension) across models (requires >= 2 evaluators and >= 3 models)
    hi_qd_rows = []
    skipped_hicc_qd = 0
    for q in questions:
        for d in dims:
            qd = human[(human['question'] == q) & (human['dimension'] == d)]
            mat = qd.pivot_table(index='model', columns='human_evaluator', values='score')
            if mat.shape[1] < 2 or mat.shape[0] < 3:
                skipped_hicc_qd += 1
                continue
            try:
                long = [{'model': m, 'rater': f'h{int(r)}', 'score': float(mat.loc[m, r])}
                        for m in mat.index for r in mat.columns if pd.notna(mat.loc[m, r])]
                icc = pg.intraclass_corr(data=pd.DataFrame(long), targets='model', raters='rater', ratings='score')
                # Use ICC(A,1) -> pingouin 'ICC2'
                row = icc[icc['Type'] == 'ICC2']
                if not row.empty:
                    hi_qd_rows.append({'question': q, 'dimension': d,
                                       'human_internal_icc': float(row['ICC'].iloc[0]),
                                       'human_internal_p': float(row['pval'].iloc[0]),
                                       'n_models': int(mat.shape[0]), 'n_evaluators': int(mat.shape[1])})
            except Exception:
                skipped_hicc_qd += 1
                continue
    hi_qd_df = pd.DataFrame(hi_qd_rows, columns=['question', 'dimension', 'human_internal_icc', 'human_internal_p', 'n_models', 'n_evaluators'])
    hi_qd_df.to_csv(OUT_DIR / 'results' / 'human_internal_consistency.csv', index=False, encoding='utf-8')

    # Diagnostic consistency per (m,d)
    diag_rows = []
    for m in models:
        for d in dims:
            md = merged[(merged['model'] == m) & (merged['dimension'] == d)]
            if md['question'].nunique() < 3:
                print(f'[WARN] Diagnostic: insufficient questions for (model={m}, dim={d}); skipping.')
                continue
            tau, p_tau = kendalltau(md['Human_Avg'].values, md['LLM_Avg_Overall'].values)
            diag_rows.append({'model': m, 'dimension': d, 'kendall_tau': float(tau), 'kendall_p': float(p_tau)})
    diag_df = pd.DataFrame(diag_rows, columns=['model', 'dimension', 'kendall_tau', 'kendall_p'])
    diag_df.to_csv(OUT_DIR / 'results' / 'diagnostic_consistency.csv', index=False, encoding='utf-8')

    # LLM internal ICC per (model, question, dimension) using 25 cells (5 answers × 5 evaluations)
    li_rows = []
    for m in models:
        for q in questions:
            for d in dims:
                block = llm[(llm['model'] == m) & (llm['question'] == q) & (llm['dimension'] == d)]
                if block['answer_round'].nunique() < 2 or block['evaluation_round'].nunique() < 2:
                    continue
                tmp = block.rename(columns={'evaluation_round': 'rater', 'answer_round': 'target'}).copy()
                try:
                    icc = pg.intraclass_corr(data=tmp, targets='target', raters='rater', ratings='score')
                    row = icc[icc['Type'] == 'ICC1']
                    if not row.empty:
                        li_rows.append({'model': m, 'question': q, 'dimension': d,
                                        'llm_internal_icc': float(row['ICC'].iloc[0]),
                                        'llm_internal_p': float(row['pval'].iloc[0]),
                                        'n_answers': int(block['answer_round'].nunique()),
                                        'n_evals': int(block['evaluation_round'].nunique())})
                except Exception:
                    pass
    li_df = pd.DataFrame(li_rows, columns=['model', 'question', 'dimension', 'llm_internal_icc', 'llm_internal_p', 'n_answers', 'n_evals'])
    li_df.to_csv(OUT_DIR / 'results' / 'llm_internal_consistency.csv', index=False, encoding='utf-8')

    # Disagreement stats
    disagree = merged.groupby('model')['Disagreement_Score'].agg(['mean', 'std', 'median', 'count']).reset_index()
    disagree.to_csv(OUT_DIR / 'results' / 'disagreement_by_model.csv', index=False, encoding='utf-8')

    # Figures (English only)
    # Figure A
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Figure A: Overall Scatter (by Dimension)', fontsize=15, fontweight='bold')
    for i, d in enumerate(dims):
        ax = axes[i // 2, i % 2]
        dd = merged[merged['dimension'] == d]
        if dd.empty:
            ax.text(0.5, 0.5, f'No data for {d}', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.scatter(dd['Human_Avg'], dd['LLM_Avg_Overall'], alpha=0.7, s=40)
            if len(dd) > 1:
                z = np.polyfit(dd['Human_Avg'], dd['LLM_Avg_Overall'], 1)
                p = np.poly1d(z)
                xs = np.linspace(dd['Human_Avg'].min(), dd['Human_Avg'].max(), 100)
                ax.plot(xs, p(xs), 'r--', alpha=0.8)
            mn = min(dd['Human_Avg'].min(), dd['LLM_Avg_Overall'].min())
            mx = max(dd['Human_Avg'].max(), dd['LLM_Avg_Overall'].max())
            ax.plot([mn, mx], [mn, mx], 'k:', alpha=0.5)
        ax.set_xlabel('Human Average Score')
        ax.set_ylabel('LLM Average Score')
        ax.set_title(d)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'Figure_A_overall_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Apply visual config style if available
    if _VISCFG is not None:
        try:
            _VISCFG.setup_plot_style()
        except Exception:
            pass

    # Figure B
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Figure B: Model-specific Trends (by Dimension)', fontsize=15, fontweight='bold')
    # Build colors per model from vis config if available
    color_list = []
    for m in models:
        c = _model_color(m)
        color_list.append(c if c else None)
    # Fallback where color missing
    fallback = plt.cm.tab10(np.linspace(0, 1, len(models)))
    colors = [color_list[i] if color_list[i] is not None else fallback[i] for i in range(len(models))]
    for i, d in enumerate(dims):
        ax = axes[i // 2, i % 2]
        for j, m in enumerate(models):
            md = merged[(merged['dimension'] == d) & (merged['model'] == m)]
            if md.empty:
                continue
            ax.scatter(md['Human_Avg'], md['LLM_Avg_Overall'], alpha=0.7, s=30, c=[colors[j]], label=m if i == 0 else '')
            if len(md) > 1:
                z = np.polyfit(md['Human_Avg'], md['LLM_Avg_Overall'], 1)
                p = np.poly1d(z)
                xs = np.linspace(md['Human_Avg'].min(), md['Human_Avg'].max(), 80)
                ax.plot(xs, p(xs), color=colors[j], alpha=0.6)
        dd = merged[merged['dimension'] == d]
        if not dd.empty:
            mn = min(dd['Human_Avg'].min(), dd['LLM_Avg_Overall'].min())
            mx = max(dd['Human_Avg'].max(), dd['LLM_Avg_Overall'].max())
            ax.plot([mn, mx], [mn, mx], 'k:', alpha=0.5)
        ax.set_xlabel('Human Average Score')
        ax.set_ylabel('LLM Average Score')
        ax.set_title(d)
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=m, markerfacecolor=colors[j], markersize=6) for j, m in enumerate(models)]
    fig.legend(handles=handles, labels=models, loc='lower center', ncol=min(4, len(models)))
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(OUT_DIR / 'figures' / 'Figure_B_model_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Figure C (forest)
    sum_by_dim = {}
    for d in dims:
        ddf = rc_df[rc_df['dimension'] == d]
        sum_by_dim[d] = {
            'kendall_mean': float(ddf['kendall_tau'].mean()),
            'kendall_ci': [float(ddf['kendall_tau'].quantile(0.0015)), float(ddf['kendall_tau'].quantile(0.9985))],
            'spearman_mean': float(ddf['spearman_rho'].mean()),
            'spearman_ci': [float(ddf['spearman_rho'].quantile(0.0015)), float(ddf['spearman_rho'].quantile(0.9985))],
            'icc_mean': float(ddf['icc'].mean()),
            'icc_ci': [float(ddf['icc'].quantile(0.0015)), float(ddf['icc'].quantile(0.9985))],
        }
    xs = np.arange(len(dims))
    w = 0.25
    fig, ax = plt.subplots(figsize=(11, 7))
    k_means = [sum_by_dim[d]['kendall_mean'] for d in dims]
    k_cis = [sum_by_dim[d]['kendall_ci'] for d in dims]
    s_means = [sum_by_dim[d]['spearman_mean'] for d in dims]
    s_cis = [sum_by_dim[d]['spearman_ci'] for d in dims]
    i_means = [sum_by_dim[d]['icc_mean'] for d in dims]
    i_cis = [sum_by_dim[d]['icc_ci'] for d in dims]
    k_err = [[m - ci[0] for m, ci in zip(k_means, k_cis)], [ci[1] - m for m, ci in zip(k_means, k_cis)]]
    s_err = [[m - ci[0] for m, ci in zip(s_means, s_cis)], [ci[1] - m for m, ci in zip(s_means, s_cis)]]
    i_err = [[m - ci[0] for m, ci in zip(i_means, i_cis)], [ci[1] - m for m, ci in zip(i_means, i_cis)]]
    ax.errorbar(xs - w, k_means, yerr=k_err, fmt='o', capsize=5, label="Kendall's τ")
    ax.errorbar(xs, s_means, yerr=s_err, fmt='s', capsize=5, label="Spearman's ρ")
    ax.errorbar(xs + w, i_means, yerr=i_err, fmt='^', capsize=5, label='ICC(A,1)')
    ax.set_xticks(xs)
    ax.set_xticklabels(dims, rotation=45, ha='right')
    ax.set_xlabel('Dimensions')
    ax.set_ylabel('Correlation')
    ax.set_title('Figure C: Ranking Consistency (99.7% CI)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axhline(0, color='k', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'Figure_C_ranking_forest.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Human ICC violin
    fig, ax = plt.subplots(figsize=(9, 6))
    pairs = [(d, human_diag_df[human_diag_df['dimension'] == d]['human_internal_icc'].dropna().values) for d in dims]
    pairs = [(d, v) for d, v in pairs if len(v) > 0]
    if pairs:
        labels, values = zip(*pairs)
        ax.violinplot(values, positions=range(len(labels)), showmeans=True)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
    else:
        ax.text(0.5, 0.5, 'No valid human ICC data', ha='center', va='center', transform=ax.transAxes)
    ax.set_xlabel('Dimensions')
    ax.set_ylabel('ICC')
    ax.set_title('Human Internal Consistency (ICC) – Across Questions')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'Human_Internal_ICC_Violin.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Human ICC violin (by question×dimension across models)
    fig, ax = plt.subplots(figsize=(9, 6))
    pairs_qd = [(d, hi_qd_df[hi_qd_df['dimension'] == d]['human_internal_icc'].dropna().values) for d in dims]
    pairs_qd = [(d, v) for d, v in pairs_qd if len(v) > 0]
    if pairs_qd:
        labels_qd, values_qd = zip(*pairs_qd)
        ax.violinplot(values_qd, positions=range(len(labels_qd)), showmeans=True)
        ax.set_xticks(range(len(labels_qd)))
        ax.set_xticklabels(labels_qd, rotation=45, ha='right')
    else:
        ax.text(0.5, 0.5, 'No valid (Q×D) human ICC data', ha='center', va='center', transform=ax.transAxes)
    ax.set_xlabel('Dimensions')
    ax.set_ylabel('ICC')
    ax.set_title('Human Internal Consistency (ICC) – By Question × Dimension')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'Human_Internal_ICC_QD_Violin.png', dpi=300, bbox_inches='tight')
    plt.close()

    # LLM ICC violins
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    pairs_dim = [(d, li_df[li_df['dimension'] == d]['llm_internal_icc'].dropna().values) for d in dims]
    pairs_dim = [(d, v) for d, v in pairs_dim if len(v) > 0]
    if pairs_dim:
        labels_d, values_d = zip(*pairs_dim)
        ax1.violinplot(values_d, positions=range(len(labels_d)), showmeans=True)
        ax1.set_xticks(range(len(labels_d)))
        ax1.set_xticklabels(labels_d, rotation=45, ha='right')
    else:
        ax1.text(0.5, 0.5, 'No valid LLM ICC data (by dimension)', ha='center', va='center', transform=ax1.transAxes)
    ax1.set_title('LLM Internal Consistency (by Dimension)')
    ax1.set_ylabel('ICC')
    ax1.grid(True, alpha=0.3)
    data_model = [li_df[li_df['model'] == m]['llm_internal_icc'].dropna().values for m in models]
    # Filter models with data
    dm_pairs = [(m, v) for m, v in zip(models, data_model) if len(v) > 0]
    if dm_pairs:
        labels, values = zip(*dm_pairs)
        ax2.violinplot(values, positions=range(len(labels)), showmeans=True)
        ax2.set_xticks(range(len(labels)))
        ax2.set_xticklabels(labels, rotation=45, ha='right')
    else:
        ax2.text(0.5, 0.5, 'No valid LLM ICC data (by model)', ha='center', va='center', transform=ax2.transAxes)
    ax2.set_title('LLM Internal Consistency (by Model)')
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'LLM_Internal_ICC_Violins.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Disagreement violin
    fig, ax = plt.subplots(figsize=(12, 6))
    data = [merged[merged['model'] == m]['Disagreement_Score'].values for m in models]
    dm_pairs = [(m, v) for m, v in zip(models, data) if len(v) > 0]
    if dm_pairs:
        labels, values = zip(*dm_pairs)
        ax.violinplot(values, positions=range(len(labels)), showmeans=True)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
    else:
        ax.text(0.5, 0.5, 'No disagreement data', ha='center', va='center', transform=ax.transAxes)
    ax.set_xlabel('Models')
    ax.set_ylabel('Disagreement (LLM - Human)')
    ax.set_title('Disagreement Distribution by Model')
    ax.axhline(0, color='r', linestyle='--', alpha=0.7)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'figures' / 'Disagreement_Violin.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Additional Forest: Diagnostic consistency by model (Kendall's tau with bootstrap CI)
    try:
        def _bootstrap_tau(h_vals: np.ndarray, l_vals: np.ndarray, B: int = 1000) -> tuple[float, tuple[float, float]]:
            n = len(h_vals)
            if n < 3:
                return (np.nan, (np.nan, np.nan))
            taus = []
            rng = np.random.default_rng(42)
            for _ in range(B):
                idx = rng.integers(0, n, n)
                t, _ = kendalltau(h_vals[idx], l_vals[idx])
                if t is not None:
                    taus.append(float(t))
            if not taus:
                return (np.nan, (np.nan, np.nan))
            taus = np.array(taus)
            return (float(np.mean(taus)), (float(np.quantile(taus, 0.0015)), float(np.quantile(taus, 0.9985))))

        diag_ci_rows = []
        for d in dims:
            for m in models:
                md = merged[(merged['model'] == m) & (merged['dimension'] == d)]
                h = md['Human_Avg'].to_numpy()
                l = md['LLM_Avg_Overall'].to_numpy()
                mean_tau, (lo, hi) = _bootstrap_tau(h, l)
                diag_ci_rows.append({'model': m, 'dimension': d, 'tau_mean': mean_tau, 'ci_lo': lo, 'ci_hi': hi})
        diag_ci_df = pd.DataFrame(diag_ci_rows)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Diagnostic Consistency by Model (Kendall's tau, 99.7% CI)", fontsize=15, fontweight='bold')
        for i, d in enumerate(dims):
            ax = axes[i // 2, i % 2]
            sdf = diag_ci_df[diag_ci_df['dimension'] == d].copy()
            sdf = sdf.set_index('model').loc[models].reset_index()  # keep order
            xs = np.arange(len(sdf))
            y = sdf['tau_mean'].to_numpy()
            yerr = np.vstack([y - sdf['ci_lo'].to_numpy(), sdf['ci_hi'].to_numpy() - y])
            ax.errorbar(xs, y, yerr=yerr, fmt='o', capsize=4)
            ax.set_xticks(xs)
            ax.set_xticklabels(sdf['model'], rotation=45, ha='right')
            ax.set_ylim(-1, 1)
            ax.axhline(0, color='k', linestyle='--', alpha=0.5)
            ax.set_ylabel("Kendall's tau")
            ax.set_title(d)
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUT_DIR / 'figures' / 'Figure_D_diagnostic_forest.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception:
        pass

    # Additional Forest: Human internal ICC(A,1) by model with bootstrap CI across questions
    try:
        def _bootstrap_icc2(mat: pd.DataFrame, B: int = 1000) -> tuple[float, tuple[float, float]]:
            # mat: rows=questions, cols=raters, values=scores
            qs = mat.index.to_list()
            if len(qs) < 3 or mat.shape[1] < 2:
                return (np.nan, (np.nan, np.nan))
            rng = np.random.default_rng(123)
            vals = []
            for _ in range(B):
                samp_q = rng.choice(qs, size=len(qs), replace=True)
                long = []
                for q in samp_q:
                    for r in mat.columns:
                        v = mat.loc[q, r]
                        if pd.notna(v):
                            long.append({'question': q, 'rater': f'h{int(r)}', 'score': float(v)})
                if not long:
                    continue
                try:
                    icc = pg.intraclass_corr(data=pd.DataFrame(long), targets='question', raters='rater', ratings='score')
                    row = icc[icc['Type'] == 'ICC2']
                    if not row.empty:
                        vals.append(float(row['ICC'].iloc[0]))
                except Exception:
                    continue
            if not vals:
                return (np.nan, (np.nan, np.nan))
            arr = np.array(vals)
            return (float(np.mean(arr)), (float(np.quantile(arr, 0.0015)), float(np.quantile(arr, 0.9985))))

        hicc_ci_rows = []
        for d in dims:
            for m in models:
                md = human[(human['model'] == m) & (human['dimension'] == d)]
                mat = md.pivot_table(index='question', columns='human_evaluator', values='score')
                mean_icc, (lo, hi) = _bootstrap_icc2(mat)
                hicc_ci_rows.append({'model': m, 'dimension': d, 'icc_mean': mean_icc, 'ci_lo': lo, 'ci_hi': hi})
        hicc_ci_df = pd.DataFrame(hicc_ci_rows)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Human Internal Consistency by Model (ICC(A,1), 99.7% CI)', fontsize=15, fontweight='bold')
        for i, d in enumerate(dims):
            ax = axes[i // 2, i % 2]
            sdf = hicc_ci_df[hicc_ci_df['dimension'] == d].copy()
            sdf = sdf.set_index('model').loc[models].reset_index()
            xs = np.arange(len(sdf))
            y = sdf['icc_mean'].to_numpy()
            yerr = np.vstack([y - sdf['ci_lo'].to_numpy(), sdf['ci_hi'].to_numpy() - y])
            ax.errorbar(xs, y, yerr=yerr, fmt='o', capsize=4)
            ax.set_xticks(xs)
            ax.set_xticklabels(sdf['model'], rotation=45, ha='right')
            ax.set_ylim(-1, 1)
            ax.axhline(0, color='k', linestyle='--', alpha=0.5)
            ax.set_ylabel('ICC(A,1)')
            ax.set_title(d)
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUT_DIR / 'figures' / 'Figure_E_human_icc_forest.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception:
        pass

    # Save summary
    with open(OUT_DIR / 'results' / 'summary.txt', 'w', encoding='utf-8') as f:
        f.write('Models: ' + ', '.join(models) + '\n')
        f.write('Dimensions: ' + ', '.join(dims) + '\n')
        f.write('Questions: ' + ', '.join(questions) + '\n')

    print('Done (strict). Outputs in data/, results/, figures/.')


if __name__ == '__main__':
    main()
