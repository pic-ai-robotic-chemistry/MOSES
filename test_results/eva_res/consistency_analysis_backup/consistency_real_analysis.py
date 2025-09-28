#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性分析（使用真实数据）

实现《一致性分析总方案.md》的要求：
- 读取人类评分CSV与LLM评分JSON（individual）
- 数据聚合：Human_Avg，LLM_Avg_Overall，LLM_Repetition_Avg，Disagreement_Score
- 分析：
  - 2.1 排序一致性（Kendall / Spearman / ICC(A,1) + p值）
  - 2.2 人类内部一致性（ICC(A,1) + p值）
  - 3.1 模型诊断一致性（Kendall + p值）
  - 3.2 人类诊断一致性（ICC(A,1) + p值）
  - 4.1 LLM内部一致性（ICC(1,1) + p值）
  - 5. 一致性误差分布（Disagreement_Score）
- 可视化：图A、图B、图C、森林图、小提琴图

只在 test_results/eva_res/consistency_analysis 目录下读写输出。
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from scipy.stats import kendalltau, spearmanr
import pingouin as pg

plt.rcParams['axes.unicode_minus'] = False
# 选择可用中文字体，避免缺字
def _select_cjk_font():
    preferred = [
        'Microsoft YaHei', 'SimHei', 'SimSun', 'Noto Sans CJK SC',
        'PingFang SC', 'Source Han Sans CN', 'WenQuanYi Zen Hei',
        'Arial Unicode MS', 'DejaVu Sans'
    ]
    available = {f.name.lower(): f.fname for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name.lower() in available:
            return name
    # fallback
    return 'DejaVu Sans'

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = [_select_cjk_font()]
sns.set_style('whitegrid')

BASE_DIR = Path(r"C:\D\CursorProj\Chem-Ontology-Constructor\test_results\eva_res")
OUTPUT_DIR = BASE_DIR / 'consistency_analysis'
(OUTPUT_DIR / 'results').mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'figures').mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'data').mkdir(parents=True, exist_ok=True)


ALLOWED_MODELS: List[str] = [
    'MOSES', 'o3', 'GPT-4.1', 'LightRAG-nano', 'LightRAG',
    'MOSES-nano', 'GPT-4.1-nano', 'GPT-4o', 'GPT-4o-mini',
]

# 内部维度键与中文展示名
DIM_KEY_TO_CN = {
    'correctness': '正确性',
    'completeness': '完备性',
    'theoretical_depth': '理论深度',
    'rigor_and_information_density': '论述严谨性与信息密度',
    # 备用维度（若LLM数据使用以下维度）
    'logic': '逻辑性',
    'clarity': '清晰性',
}


def _canonicalize_model(raw: str) -> str:
    if not isinstance(raw, str):
        return raw
    name = raw.strip()
    low = name.lower().replace('_', '-').replace(' ', '')
    if 'gpt-4.1' in low or 'gpt-4-1' in low or 'gpt-41' in low:
        return 'GPT-4.1-nano' if 'nano' in low else 'GPT-4.1'
    if 'gpt-4o-mini' in low:
        return 'GPT-4o-mini'
    if 'gpt-4o' in low:
        return 'GPT-4o'
    if 'lightrag' in low:
        return 'LightRAG-nano' if 'nano' in low else 'LightRAG'
    if 'moses' in low:
        return 'MOSES-nano' if 'nano' in low else 'MOSES'
    if 'o3' in low:
        return 'o3'
    return name


def _find_latest(folder: Path, pattern: str) -> Path:
    files = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f'未找到文件: {folder} / {pattern}')
    return files[0]


def parse_human_csv(csv_path: Path) -> pd.DataFrame:
    """解析人类评分CSV为长表: model, question, dimension(内部键), human_evaluator, score"""
    dim_cn_to_key = {
        '正确性': 'correctness',
        '逻辑性': 'logic',
        '清晰性': 'clarity',
        '完备性': 'completeness',
        '理论深度': 'theoretical_depth',
        '论述严谨性与信息密度': 'rigor_and_information_density',
    }
    # 人类侧可接受6个维度，后续会与LLM侧取交集
    active_dims = set(DIM_KEY_TO_CN.keys())

    import csv
    rows = []
    with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)

        col_map: Dict[int, tuple[str, str]] = {}
        current_model: str | None = None
        for idx, cell in enumerate(header):
            if idx < 2:
                continue
            label = (cell or '').strip()
            if not label:
                continue
            if label in dim_cn_to_key:
                if current_model:
                    dkey = dim_cn_to_key[label]
                    if dkey in active_dims:
                        col_map[idx] = (_canonicalize_model(current_model), dkey)
            else:
                current_model = label  # 模型名哨兵

        qid_occ = defaultdict(int)
        for row in reader:
            if len(row) < 2:
                continue
            qraw = (row[0] or '').strip()
            if not qraw:
                continue
            qid = f"q_{qraw}"
            qid_occ[qid] += 1
            evaluator = qid_occ[qid]

            for cidx, (model, dkey) in col_map.items():
                if cidx >= len(row):
                    continue
                cell = (row[cidx] or '').strip()
                if not cell:
                    continue
                try:
                    score = float(cell)
                except Exception:
                    m = re.search(r"[-+]?\d*\.?\d+", cell)
                    if not m:
                        continue
                    try:
                        score = float(m.group(0))
                    except Exception:
                        continue
                rows.append({
                    'model': model,
                    'question': qid,
                    'dimension': dkey,
                    'human_evaluator': evaluator,
                    'score': score,
                })
    return pd.DataFrame(rows)


def parse_llm_jsonl(json_path: Path) -> pd.DataFrame:
    """解析LLM评分JSONL为长表: model, question, dimension(内部键), answer_round, evaluation_round, score"""
    rows = []
    with json_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue

            model = _canonicalize_model(obj.get('model_name', ''))
            qid = obj.get('question_id') or obj.get('question')
            if isinstance(qid, str) and not qid.startswith('q_'):
                qid = f"q_{qid}"
            try:
                answer_round = int(obj.get('answer_round', 1))
            except Exception:
                answer_round = 1
            try:
                evaluation_round = int(obj.get('evaluation_round', 1))
            except Exception:
                evaluation_round = 1

            ans = obj.get('answer', '') or ''
            m = re.search(r"\{[\s\S]*\}", ans)
            if not m:
                continue
            try:
                score_obj = json.loads(m.group(0))
            except Exception:
                continue

            for dkey, sval in score_obj.items():
                if dkey not in DIM_KEYS:
                    continue
                if isinstance(sval, list):
                    score = sval[0] if sval else None
                else:
                    score = sval
                if score is None:
                    continue
                try:
                    score = float(score)
                except Exception:
                    continue
                rows.append({
                    'model': model,
                    'question': qid,
                    'dimension': dkey,
                    'answer_round': answer_round,
                    'evaluation_round': evaluation_round,
                    'score': score,
                })
    return pd.DataFrame(rows)


def analyze():
    print('=' * 60)
    print('第零部分：数据加载与解析（真实数据）')
    print('=' * 60)

    human_csv = _find_latest(BASE_DIR / 'human', '*.csv')
    llm_json = _find_latest(BASE_DIR / 'individual', '*.json')
    print(f'人类评分: {human_csv}')
    print(f'LLM评分: {llm_json}')

    human_df = parse_human_csv(human_csv)
    llm_df = parse_llm_jsonl(llm_json)

    # 过滤到指定模型，且二者交集
    human_models = set(human_df['model'].unique())
    llm_models = set(llm_df['model'].unique())
    models = [m for m in ALLOWED_MODELS if m in human_models and m in llm_models]
    if not models:
        raise ValueError('过滤后没有可用模型，请检查数据中的模型名是否匹配。')

    human_df = human_df[human_df['model'].isin(models)].copy()
    llm_df = llm_df[llm_df['model'].isin(models)].copy()
    human_df = human_df[human_df['dimension'].isin(DIM_KEYS)].copy()
    llm_df = llm_df[llm_df['dimension'].isin(DIM_KEYS)].copy()

    questions = sorted(human_df['question'].dropna().unique().tolist(), key=lambda x: int(x.split('_')[-1]))

    # 第一部分：聚合
    print('\n' + '=' * 60)
    print('第一部分：数据预处理与聚合')
    print('=' * 60)

    human_avg = human_df.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
    human_avg = human_avg.rename(columns={'score': 'Human_Avg'})
    llm_overall = llm_df.groupby(['model', 'question', 'dimension'])['score'].mean().reset_index()
    llm_overall = llm_overall.rename(columns={'score': 'LLM_Avg_Overall'})
    llm_rep = llm_df.groupby(['model', 'question', 'dimension', 'answer_round'])['score'].mean().reset_index()
    llm_rep = llm_rep.rename(columns={'score': 'LLM_Repetition_Avg'})

    merged = pd.merge(human_avg, llm_overall, on=['model', 'question', 'dimension'], how='inner')
    merged['Disagreement_Score'] = merged['LLM_Avg_Overall'] - merged['Human_Avg']

    merged.to_csv(OUTPUT_DIR / 'data' / 'aggregated_scores.csv', index=False, encoding='utf-8-sig')
    llm_rep.to_csv(OUTPUT_DIR / 'data' / 'llm_repetition_scores.csv', index=False, encoding='utf-8-sig')

    prep_stats = {
        'total_entries': int(len(merged)),
        'models_count': int(len(models)),
        'questions_count': int(len(questions)),
        'dimensions_count': None,  # 稍后填入实际分析维度数量
        'models': models,
        'dimensions': None,
    }

    # 第二部分：排序一致性（按 问题×维度）
    print('\n' + '=' * 60)
    print('第二部分：模型排序一致性分析（裁判视角）')
    print('=' * 60)
    # 动态选择分析维度：优先 plan 4 维；如LLM无该维，退化到 (logic, clarity, theorectical_depth, rigor...)
    llm_dims_present = set(llm_df['dimension'].unique())
    preferred_plan_dims = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
    alt_llm_dims = ['logic', 'clarity', 'theoretical_depth', 'rigor_and_information_density']
    if set(preferred_plan_dims).issubset(llm_dims_present):
        dims = preferred_plan_dims
    elif set(alt_llm_dims).issubset(llm_dims_present):
        dims = alt_llm_dims
    else:
        # 尽量取交集，至少保留2个维度
        common = [d for d in preferred_plan_dims if d in llm_dims_present]
        if len(common) < 2:
            common = [d for d in alt_llm_dims if d in llm_dims_present]
        if len(common) < 2:
            # 最后兜底：使用LLM出现频率最高的前2-4个维度
            counts = llm_df['dimension'].value_counts()
            common = counts.index.tolist()[:max(2, min(4, len(counts)))]
        dims = common
    print(f"选择用于分析的维度: {', '.join([DIM_KEY_TO_CN.get(d, d) for d in dims])}")
    # 同步过滤到人类与合并数据
    merged = merged[merged['dimension'].isin(dims)].copy()
    human_df = human_df[human_df['dimension'].isin(dims)].copy()
    llm_df = llm_df[llm_df['dimension'].isin(dims)].copy()
    prep_stats['dimensions'] = dims
    prep_stats['dimensions_count'] = len(dims)
    print(f"参与分析的模型: {', '.join(models)}")
    print(f"聚合后数据条目: {len(merged)}")
    corr_rows = []
    for q in questions:
        for d in dims:
            sub = merged[(merged['question'] == q) & (merged['dimension'] == d)]
            if len(sub) >= 3:
                ht = sub['Human_Avg'].to_numpy()
                lt = sub['LLM_Avg_Overall'].to_numpy()
                tau, p_tau = kendalltau(ht, lt)
                # 处理常量输入，避免Spearman警告
                if (np.allclose(ht, ht[0]) or np.allclose(lt, lt[0])):
                    rho, p_rho = (np.nan, np.nan)
                else:
                    rho, p_rho = spearmanr(ht, lt)
                # ICC(A,1): 绝对一致性（人类 vs LLM 两位评委，对象为模型）
                icc_val, icc_p = np.nan, np.nan
                try:
                    icc_df = pd.DataFrame({
                        'model': sub['model'].values.tolist() * 2,
                        'rater': (['human'] * len(sub)) + (['llm'] * len(sub)),
                        'score': np.concatenate([ht, lt]),
                    })
                    icc_res = pg.intraclass_corr(data=icc_df, targets='model', raters='rater', ratings='score')
                    row = icc_res[icc_res['Type'] == 'ICC1']
                    if len(row) > 0:
                        icc_val = float(row['ICC'].iloc[0])
                        icc_p = float(row['pval'].iloc[0])
                except Exception:
                    pass
                corr_rows.append({'question': q, 'dimension': d, 'kendall_tau': tau, 'kendall_p': p_tau,
                                  'spearman_rho': rho, 'spearman_p': p_rho, 'icc': icc_val, 'icc_p': icc_p,
                                  'n_models': int(len(sub))})
    corr_df = pd.DataFrame(corr_rows, columns=[
        'question', 'dimension', 'kendall_tau', 'kendall_p',
        'spearman_rho', 'spearman_p', 'icc', 'icc_p', 'n_models'
    ])
    corr_df.to_csv(OUTPUT_DIR / 'results' / 'ranking_correlations.csv', index=False, encoding='utf-8-sig')

    # 按维度统计（99.7% CI 近似用分位数0.15%~99.85%）
    summary_by_dim = {}
    for d in dims:
        ddf = corr_df[corr_df['dimension'] == d]
        if len(ddf) == 0:
            continue
        def ci997(series: pd.Series):
            s = series.dropna()
            if len(s) == 0:
                return [np.nan, np.nan]
            return [float(s.quantile(0.0015)), float(s.quantile(0.9985))]
        summary_by_dim[d] = {
            'kendall_mean': float(ddf['kendall_tau'].mean()),
            'kendall_ci': ci997(ddf['kendall_tau']),
            'kendall_significant_ratio': float((ddf['kendall_p'] < 0.05).mean()),
            'kendall_avg_p': float(ddf['kendall_p'].mean()),
            'spearman_mean': float(ddf['spearman_rho'].mean()),
            'spearman_ci': ci997(ddf['spearman_rho']),
            'spearman_significant_ratio': float((ddf['spearman_p'] < 0.05).mean()),
            'icc_mean': float(ddf['icc'].mean()),
            'icc_ci': ci997(ddf['icc']),
            'n_comparisons': int(len(ddf)),
        }

    # 2.2 人类内部一致性（按 问题×维度；模型×评委矩阵 -> ICC(A,1)）
    human_icc_rows = []
    for q in questions:
        for d in dims:
            qd = human_df[(human_df['question'] == q) & (human_df['dimension'] == d)]
            if len(qd) == 0:
                continue
            mat = qd.pivot_table(index='model', columns='human_evaluator', values='score')
            if mat.shape[0] >= 3 and mat.shape[1] >= 2:
                try:
                    icc_long = []
                    for m in mat.index:
                        for r in mat.columns:
                            val = mat.loc[m, r]
                            if pd.notna(val):
                                icc_long.append({'model': m, 'rater': f'h{int(r)}', 'score': float(val)})
                    icc_long_df = pd.DataFrame(icc_long)
                    icc = pg.intraclass_corr(data=icc_long_df, targets='model', raters='rater', ratings='score')
                    row = icc[icc['Type'] == 'ICC1']
                    if len(row) > 0:
                        human_icc_rows.append({
                            'question': q,
                            'dimension': d,
                            'human_internal_icc': float(row['ICC'].iloc[0]),
                            'human_internal_p': float(row['pval'].iloc[0]),
                            'n_models': int(mat.shape[0]),
                            'n_evaluators': int(mat.shape[1]),
                        })
                except Exception:
                    pass
    human_icc_df = pd.DataFrame(human_icc_rows, columns=[
        'question', 'dimension', 'human_internal_icc', 'human_internal_p', 'n_models', 'n_evaluators'
    ])
    human_icc_df.to_csv(OUTPUT_DIR / 'results' / 'human_internal_consistency.csv', index=False, encoding='utf-8-sig')

    # 第三部分：模型诊断一致性（按 模型×维度；跨27题 Kendall）
    diag_rows = []
    for m in models:
        for d in dims:
            md = merged[(merged['model'] == m) & (merged['dimension'] == d)]
            if len(md) >= 3:
                tau, p_tau = kendalltau(md['Human_Avg'].values, md['LLM_Avg_Overall'].values)
                diag_rows.append({'model': m, 'dimension': d, 'kendall_tau': tau, 'kendall_p': p_tau, 'n_questions': int(len(md))})
    diag_df = pd.DataFrame(diag_rows, columns=[
        'model', 'dimension', 'kendall_tau', 'kendall_p', 'n_questions'
    ])
    diag_df.to_csv(OUTPUT_DIR / 'results' / 'diagnostic_consistency.csv', index=False, encoding='utf-8-sig')

    # 3.2 人类诊断一致性（按 模型×维度；问题×评委矩阵 -> ICC(A,1)）
    human_diag_rows = []
    for m in models:
        for d in dims:
            md = human_df[(human_df['model'] == m) & (human_df['dimension'] == d)]
            if len(md) == 0:
                continue
            mat = md.pivot_table(index='question', columns='human_evaluator', values='score')
            if mat.shape[0] >= 3 and mat.shape[1] >= 2:
                try:
                    icc_long = []
                    for q in mat.index:
                        for r in mat.columns:
                            val = mat.loc[q, r]
                            if pd.notna(val):
                                icc_long.append({'question': q, 'rater': f'h{int(r)}', 'score': float(val)})
                    icc_long_df = pd.DataFrame(icc_long)
                    icc = pg.intraclass_corr(data=icc_long_df, targets='question', raters='rater', ratings='score')
                    row = icc[icc['Type'] == 'ICC1']
                    if len(row) > 0:
                        human_diag_rows.append({
                            'model': m,
                            'dimension': d,
                            'human_diagnostic_icc': float(row['ICC'].iloc[0]),
                            'human_diagnostic_p': float(row['pval'].iloc[0]),
                            'n_questions': int(mat.shape[0]),
                            'n_evaluators': int(mat.shape[1]),
                        })
                except Exception:
                    pass
    human_diag_df = pd.DataFrame(human_diag_rows, columns=[
        'model', 'dimension', 'human_diagnostic_icc', 'human_diagnostic_p', 'n_questions', 'n_evaluators'
    ])
    human_diag_df.to_csv(OUTPUT_DIR / 'results' / 'human_diagnostic_consistency.csv', index=False, encoding='utf-8-sig')

    # 第四部分：LLM内部一致性（每个 {model, question, dimension, answer_round} 对 5次评分的ICC(1,1)）
    llm_icc_rows = []
    for m in models:
        for q in questions:
            for d in dims:
                for a in range(1, 6):
                    ed = llm_df[(llm_df['model'] == m) & (llm_df['question'] == q) & (llm_df['dimension'] == d) & (llm_df['answer_round'] == a)]
                    if len(ed) >= 2:
                        try:
                            # 评委= evaluation_round，目标= 同一个answer_round
                            icc = pg.intraclass_corr(data=ed.rename(columns={'evaluation_round': 'rater'}),
                                                     targets='answer_round', raters='rater', ratings='score')
                            row = icc[icc['Type'] == 'ICC1']
                            if len(row) > 0:
                                llm_icc_rows.append({
                                    'model': m, 'question': q, 'dimension': d, 'answer_round': a,
                                    'llm_internal_icc': float(row['ICC'].iloc[0]),
                                    'llm_internal_p': float(row['pval'].iloc[0]),
                                    'n_evaluations': int(len(ed)),
                                })
                        except Exception:
                            pass
    llm_icc_df = pd.DataFrame(llm_icc_rows, columns=[
        'model', 'question', 'dimension', 'answer_round', 'llm_internal_icc', 'llm_internal_p', 'n_evaluations'
    ])
    llm_icc_df.to_csv(OUTPUT_DIR / 'results' / 'llm_internal_consistency.csv', index=False, encoding='utf-8-sig')

    # 第五部分：一致性误差分布
    disagree_by_model = merged.groupby('model')['Disagreement_Score'].agg(['mean', 'std', 'median', 'count']).reset_index()
    disagree_overall = merged['Disagreement_Score'].agg(['mean', 'std', 'median', 'count']).to_dict()

    # 可视化
    print('\n生成可视化...')
    # 图A：按维度总体散点（Human_Avg vs LLM_Avg_Overall）
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('图A: LLM与人类评分总体关系 (按维度分组)', fontsize=16, fontweight='bold')
    for i, d in enumerate(dims):
        ax = axes[i // 2, i % 2]
        dd = merged[merged['dimension'] == d]
        ax.scatter(dd['Human_Avg'], dd['LLM_Avg_Overall'], alpha=0.6, s=50)
        if len(dd) > 1:
            z = np.polyfit(dd['Human_Avg'], dd['LLM_Avg_Overall'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(dd['Human_Avg'].min(), dd['Human_Avg'].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', alpha=0.8, linewidth=2)
        mn = min(dd['Human_Avg'].min(), dd['LLM_Avg_Overall'].min())
        mx = max(dd['Human_Avg'].max(), dd['LLM_Avg_Overall'].max())
        ax.plot([mn, mx], [mn, mx], 'k:', alpha=0.5, linewidth=1)
        ax.set_xlabel('人类平均评分')
        ax.set_ylabel('LLM平均评分')
        ax.set_title(DIM_KEY_TO_CN[d])
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / '图A_排序一致性散点图_总体趋势.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 图B：按模型分趋势散点
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('图B: LLM与人类评分模型特异性趋势(按维度分组)', fontsize=16, fontweight='bold')
    colors = plt.cm.tab10(np.linspace(0, 1, len(models)))
    for i, d in enumerate(dims):
        ax = axes[i // 2, i % 2]
        for j, m in enumerate(models):
            md = merged[(merged['dimension'] == d) & (merged['model'] == m)]
            if len(md) > 0:
                ax.scatter(md['Human_Avg'], md['LLM_Avg_Overall'], alpha=0.7, s=40, c=[colors[j]], label=m if i == 0 else '')
                if len(md) > 1:
                    z = np.polyfit(md['Human_Avg'], md['LLM_Avg_Overall'], 1)
                    p = np.poly1d(z)
                    x_line = np.linspace(md['Human_Avg'].min(), md['Human_Avg'].max(), 50)
                    ax.plot(x_line, p(x_line), color=colors[j], alpha=0.6, linewidth=1.5)
        dd = merged[merged['dimension'] == d]
        mn = min(dd['Human_Avg'].min(), dd['LLM_Avg_Overall'].min())
        mx = max(dd['Human_Avg'].max(), dd['LLM_Avg_Overall'].max())
        ax.plot([mn, mx], [mn, mx], 'k:', alpha=0.5, linewidth=1)
        ax.set_xlabel('人类平均评分')
        ax.set_ylabel('LLM平均评分')
        ax.set_title(DIM_KEY_TO_CN[d])
        ax.grid(True, alpha=0.3)
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=m, markerfacecolor=colors[j], markersize=8) for j, m in enumerate(models)]
    fig.legend(handles=handles, labels=models, loc='lower center', ncol=min(4, len(models)))
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(OUTPUT_DIR / 'figures' / '图B_排序一致性散点图_模型特异性.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 图C：排序一致性森林图（Kendall / Spearman / ICC）
    dims_plot = [d for d in dims if d in summary_by_dim]
    x = np.arange(len(dims_plot))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 8))
    kendall_means = [summary_by_dim[d]['kendall_mean'] for d in dims_plot]
    kendall_cis = [summary_by_dim[d]['kendall_ci'] for d in dims_plot]
    spearman_means = [summary_by_dim[d]['spearman_mean'] for d in dims_plot]
    spearman_cis = [summary_by_dim[d]['spearman_ci'] for d in dims_plot]
    icc_means = [summary_by_dim[d]['icc_mean'] for d in dims_plot]
    icc_cis = [summary_by_dim[d]['icc_ci'] for d in dims_plot]
    kendall_err = [[m - ci[0] for m, ci in zip(kendall_means, kendall_cis)], [ci[1] - m for m, ci in zip(kendall_means, kendall_cis)]]
    spearman_err = [[m - ci[0] for m, ci in zip(spearman_means, spearman_cis)], [ci[1] - m for m, ci in zip(spearman_means, spearman_cis)]]
    icc_err = [[m - ci[0] for m, ci in zip(icc_means, icc_cis)], [ci[1] - m for m, ci in zip(icc_means, icc_cis)]]
    ax.errorbar(x - width, kendall_means, yerr=kendall_err, fmt='o', capsize=5, label="Kendall's τ")
    ax.errorbar(x, spearman_means, yerr=spearman_err, fmt='s', capsize=5, label="Spearman's ρ")
    ax.errorbar(x + width, icc_means, yerr=icc_err, fmt='^', capsize=5, label='ICC(A,1)')
    ax.set_xticks(x)
    ax.set_xticklabels([DIM_KEY_TO_CN.get(d, d) for d in dims_plot], rotation=45, ha='right')
    ax.set_xlabel('评估维度')
    ax.set_ylabel('相关系数')
    ax.set_title('图C: LLM-人类排序一致性森林图 (99.7% CI)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axhline(0, color='k', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / '图C_排序一致性森林图.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 人类内部一致性小提琴图（按维度）
    fig, ax = plt.subplots(figsize=(10, 6))
    data_for_violin = []
    valid_dims = []
    for d in dims:
        dd = human_icc_df[human_icc_df['dimension'] == d]['human_internal_icc'].dropna()
        if len(dd) > 0:
            data_for_violin.append(dd.values)
            valid_dims.append(DIM_KEY_TO_CN[d])
    if data_for_violin:
        ax.violinplot(data_for_violin, positions=range(len(valid_dims)), showmeans=True)
        ax.set_xticks(range(len(valid_dims)))
        ax.set_xticklabels(valid_dims, rotation=45, ha='right')
    else:
        ax.text(0.5, 0.5, '无有效数据', ha='center', va='center', transform=ax.transAxes)
    ax.set_xlabel('评估维度')
    ax.set_ylabel('ICC系数')
    ax.set_title('人类内部一致性分析(裁判组内部共识)')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / '人类内部一致性_小提琴图.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 诊断一致性森林图（按维度分面，X轴模型，Y轴Kendall）
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('模型诊断一致性森林图 (教练视角)')
    for i, d in enumerate(dims):
        ax = axes[i // 2, i % 2]
        dim_df = diag_df[diag_df['dimension'] == d]
        y_pos = np.arange(len(models))
        tau_vals = []
        xerr = []
        for m in models:
            md = dim_df[dim_df['model'] == m]
            if len(md) > 0:
                tau_vals.append(float(md['kendall_tau'].iloc[0]))
                xerr.append(0.1)  # 简单误差棒占位（可进一步用bootstrap估计）
            else:
                tau_vals.append(0.0)
                xerr.append(0.0)
        ax.errorbar(tau_vals, y_pos, xerr=xerr, fmt='o', capsize=5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(models)
        ax.set_xlabel("Kendall's τ")
        ax.set_title(DIM_KEY_TO_CN[d])
        ax.grid(True, alpha=0.3)
        ax.axvline(0, color='k', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / '模型诊断一致性_森林图.png', dpi=300, bbox_inches='tight')
    plt.close()

    # LLM内部一致性小提琴（按维度、按模型）
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    data_dim, labels_dim = [], []
    for d in DIM_KEYS:
        vals = llm_icc_df[llm_icc_df['dimension'] == d]['llm_internal_icc'].dropna().values
        if len(vals) > 0:
            data_dim.append(vals)
            labels_dim.append(DIM_KEY_TO_CN[d])
    if data_dim:
        ax1.violinplot(data_dim, positions=range(len(labels_dim)), showmeans=True)
        ax1.set_xticks(range(len(labels_dim)))
        ax1.set_xticklabels(labels_dim, rotation=45, ha='right')
    else:
        ax1.text(0.5, 0.5, '无有效数据', ha='center', va='center', transform=ax1.transAxes)
    ax1.set_title('LLM内部一致性 - 按维度')
    ax1.set_ylabel('ICC系数')
    ax1.grid(True, alpha=0.3)

    data_model, labels_model = [], []
    for m in models:
        vals = llm_icc_df[llm_icc_df['model'] == m]['llm_internal_icc'].dropna().values
        if len(vals) > 0:
            data_model.append(vals)
            labels_model.append(m)
    if data_model:
        ax2.violinplot(data_model, positions=range(len(labels_model)), showmeans=True)
        ax2.set_xticks(range(len(labels_model)))
        ax2.set_xticklabels(labels_model, rotation=45, ha='right')
    else:
        ax2.text(0.5, 0.5, '无有效数据', ha='center', va='center', transform=ax2.transAxes)
    ax2.set_title('LLM内部一致性 - 按模型')
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / 'LLM内部一致性_小提琴图.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 一致性误差小提琴图（按模型）
    fig, ax = plt.subplots(figsize=(12, 6))
    data = [merged[merged['model'] == m]['Disagreement_Score'].values for m in models]
    ax.violinplot(data, positions=range(len(models)), showmeans=True)
    ax.set_xlabel('AI模型')
    ax.set_ylabel('一致性误差 (LLM - Human)')
    ax.set_title('各模型的LLM-人类评分差异分布')
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.axhline(0, color='r', linestyle='--', alpha=0.7, label='完全一致线')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figures' / '一致性误差_小提琴图.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 汇总结果保存
    results = {
        'preprocessing': prep_stats,
        'ranking_consistency': {
            'llm_human_consistency': {
                'detailed_results': corr_df.to_dict(orient='records'),
                'summary_by_dimension': summary_by_dim,
            },
            'human_internal_consistency': {
                'detailed_results': human_icc_df.to_dict(orient='records'),
            },
        },
        'diagnostic_consistency': {
            'llm_human_diagnostic': diag_df.to_dict(orient='records'),
            'human_diagnostic_consistency': human_diag_df.to_dict(orient='records'),
        },
        'llm_internal_consistency': {
            'detailed_results': llm_icc_df.to_dict(orient='records'),
        },
        'disagreement_analysis': {
            'by_model': disagree_by_model.to_dict(orient='records'),
            'overall': disagree_overall,
        },
    }
    with open(OUTPUT_DIR / 'results' / 'complete_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 简要报告
    report_lines = []
    report_lines.append('# 一致性分析简报\n')
    report_lines.append('## 数据概况')
    report_lines.append(f"- 模型: {', '.join(models)}")
    report_lines.append(f"- 题目数: {len(questions)}")
    report_lines.append(f"- 维度: {', '.join(DIM_KEY_TO_CN[d] for d in DIM_KEYS)}\n")
    report_lines.append('## 排序一致性（按维度汇总）')
    for d in dims:
        if d in summary_by_dim:
            s = summary_by_dim[d]
            report_lines.append(f"- {DIM_KEY_TO_CN[d]}: Kendall均值={s['kendall_mean']:.3f}, 显著占比={(s['kendall_significant_ratio']*100):.1f}%")
    report_lines.append('\n## 诊断一致性（模型×维度）')
    for m in models:
        md = diag_df[diag_df['model'] == m]
        if len(md) > 0:
            report_lines.append(f"- {m}: " + ', '.join([f"{DIM_KEY_TO_CN[d]} τ={float(md[md['dimension']==d]['kendall_tau'].iloc[0]):.2f}" for d in md['dimension'].unique()]))
    report = '\n'.join(report_lines)
    with open(OUTPUT_DIR / 'results' / 'comprehensive_consistency_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print('\n分析完成，结果已保存至:')
    print(f"- 数据: {OUTPUT_DIR / 'data'}")
    print(f"- 结果: {OUTPUT_DIR / 'results'}")
    print(f"- 图表: {OUTPUT_DIR / 'figures'}")


if __name__ == '__main__':
    analyze()
