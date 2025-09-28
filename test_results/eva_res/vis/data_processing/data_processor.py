"""
数据预处理模块
从原始数据源中提取和清理数据，为可视化做准备
"""

import pandas as pd
import numpy as np
import json
import re
from pathlib import Path
import sys
import os

# 添加配置文件路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from vis_config import MODEL_INFO, DIMENSION_INFO, PATHS


class DataProcessor:
    """数据处理器，负责从各种数据源提取和清理数据"""
    
    def __init__(self, base_path: str | Path | None = None):
        """初始化数据根路径。
        - 默认自动从当前`vis`目录向上寻址，找到包含`src/analysis_summary.md`的`eva_res`目录。
        - 也可显式传入 `base_path`。
        """
        if base_path is not None:
            self.base_path = Path(base_path)
        else:
            # 推断：.../test_results/eva_res/vis/data_processing/data_processor.py
            vis_dir = Path(__file__).resolve().parents[1]  # vis/
            candidate = vis_dir.parent  # eva_res/
            summary = candidate / "src/analysis_summary.md"
            if summary.exists():
                self.base_path = candidate
            else:
                # 退化：使用当前工作目录尝试
                cwd_candidate = Path.cwd()
                if (cwd_candidate / "src/analysis_summary.md").exists():
                    self.base_path = cwd_candidate
                else:
                    # 最后兜底：保持原硬编码路径（若存在）
                    default = Path("C:/D/CursorProj/Chem-Ontology-Constructor/test_results/eva_res")
                    self.base_path = default if (default / "src/analysis_summary.md").exists() else candidate
        
        print(f"[DataProcessor] 使用数据根目录: {self.base_path}")
        # 记录最后一次选用的 ELO 文件路径，便于上层脚本打印
        self.last_elo_path: Path | None = None
        
    def load_performance_scores(self):
        """
        从analysis_summary.md中提取豆包评分数据
        返回格式化的DataFrame
        """
        summary_path = self.base_path / "src/analysis_summary.md"
        
        if not summary_path.exists():
            raise FileNotFoundError(f"找不到分析摘要文件: {summary_path}")
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取豆包评分的维度分数表格
        pattern = r'\| Model \| Correctness \| Completeness \| Logic \| Clarity \| Theoretical Depth \| Rigor And Information Density \|.*?\n(.*?)(?=\n\n|\n###|\Z)'
        
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            raise ValueError("无法找到豆包评分维度表格")
        
        table_content = match.group(1).strip()
        lines = [line.strip() for line in table_content.split('\n') if line.strip() and '|' in line]
        
        # 解析表格数据
        performance_data = []
        for line in lines:
            if line.startswith('|---'):  # 跳过分隔行
                continue
                
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 7:  # 确保有足够的列
                model = parts[0]
                
                # 过滤只保留我们需要的模型
                if model in MODEL_INFO['order']:
                    scores = {
                        '正确性': float(parts[1]),
                        '完备性': float(parts[2]),
                        '理论深度': float(parts[5]),  # Logic和Clarity不需要，取Theoretical Depth
                        '论述严谨性与信息密度': float(parts[6])
                    }
                    
                    performance_data.append({
                        'model': model,
                        **scores,
                        'overall_score': np.mean(list(scores.values()))
                    })
        
        return pd.DataFrame(performance_data)
    
    def load_elo_scores(self):
        """
        从 ELO 分析 JSON 文件中提取 4 维度 ELO 评分。
        默认只使用 20 次重复版本：trueskill_llm_only_4dim_beta-default_rep20.json。
        若找不到该文件则报错（不再回退旧路径/模式）。
        返回两张表：overall_df（中心=μ，区间=μ±3σ）与 dimension_df（同口径）。
        """
        desired = 'trueskill_llm_only_4dim_beta-default_rep20.json'
        search_order = [
            self.base_path / 'src' / desired,              # 1) 根目录 src 下优先
            self.base_path / 'src' / 'elo' / desired,      # 2) src/elo 下次之
            self.base_path / 'src' / 'elo' / 'round1' / desired,  # 3) src/elo/round1 再次
        ]
        selected = None
        for p in search_order:
            if p.exists():
                selected = p
                break
        if selected is None:
            checked = '\n  - ' + '\n  - '.join(str(p) for p in search_order)
            raise FileNotFoundError(
                "未找到指定的 20 次重复 ELO JSON 文件: "
                f"{desired}\n请将该文件放置到以下任一位置：{checked}"
            )

        self.last_elo_path = selected
        print(f"[DataProcessor] 使用 ELO 文件: {self.last_elo_path}")

        with open(self.last_elo_path, 'r', encoding='utf-8') as f:
            elo_data = json.load(f)
        
        # 提取总体ELO评分
        overall_ratings = []
        # 选择 overall_ratings（首选）或 ratings
        if 'overall_ratings' in elo_data and isinstance(elo_data['overall_ratings'], dict):
            rating_root = elo_data['overall_ratings']
        elif 'ratings' in elo_data and isinstance(elo_data['ratings'], dict):
            rating_root = elo_data['ratings']
        else:
            raise ValueError('ELO JSON 结构不含 overall_ratings/ratings 字段，无法解析')

        # 优先Doubao组合口径，否则取首个键
        if 'Doubao-Seed-1.6-combined' in rating_root:
            judge_data = rating_root['Doubao-Seed-1.6-combined']
        else:
            judge_key = next(iter(rating_root.keys()))
            judge_data = rating_root[judge_key]
        
        for model, model_data in judge_data.items():
            if model in MODEL_INFO['order']:
                mu = model_data.get('overall_mu', None)
                sigma = model_data.get('overall_sigma', None)
                # 兼容旧字段名
                if mu is None and 'overall' in model_data:
                    mu = model_data['overall'].get('mu')
                    sigma = model_data['overall'].get('sigma')
                if mu is None or sigma is None:
                    continue
                overall_ratings.append({
                    'model': model,
                    'elo_rating': float(mu),           # 中心=μ
                    'elo_mu': float(mu),
                    'elo_sigma': float(sigma),
                    'elo_lower': float(mu) - 3*float(sigma),
                    'elo_upper': float(mu) + 3*float(sigma)
                })
        
        overall_df = pd.DataFrame(overall_ratings)
        
        # 提取分维度ELO评分
        dimension_ratings = []
        
        # 选择 dimension_ratings
        if 'dimension_ratings' in elo_data and isinstance(elo_data['dimension_ratings'], dict):
            dim_root = elo_data['dimension_ratings']
        elif 'ratings' in elo_data and isinstance(elo_data['ratings'], dict):
            # 某些结构把维度信息一起放在 ratings 里（不常见），这里兜底
            dim_root = elo_data['ratings']
        else:
            dim_root = {}

        if 'Doubao-Seed-1.6-combined' in dim_root:
            dim_judge = dim_root['Doubao-Seed-1.6-combined']
        elif isinstance(dim_root, dict) and len(dim_root) > 0:
            dim_judge = dim_root[next(iter(dim_root.keys()))]
        else:
            dim_judge = {}

        # 结构：dim_judge[dimension_en][model] = {mu, sigma}
        for dim_name, models_dict in dim_judge.items():
            # 映射维度名称
            if dim_name == 'correctness':
                dim_chinese = '正确性'
            elif dim_name == 'completeness':
                dim_chinese = '完备性'
            elif dim_name == 'theoretical_depth':
                dim_chinese = '理论深度'
            elif dim_name == 'rigor_and_information_density':
                dim_chinese = '论述严谨性与信息密度'
            else:
                continue
            if not isinstance(models_dict, dict):
                continue
            for model, dim_data in models_dict.items():
                if model not in MODEL_INFO['order']:
                    continue
                mu = dim_data.get('mu', None)
                sigma = dim_data.get('sigma', None)
                if mu is None or sigma is None:
                    continue
                dimension_ratings.append({
                    'model': model,
                    'dimension': dim_chinese,
                    'elo_rating': float(mu),
                    'elo_mu': float(mu),
                    'elo_sigma': float(sigma),
                    'elo_lower': float(mu) - 3*float(sigma),
                    'elo_upper': float(mu) + 3*float(sigma)
                })
        
        dimension_df = pd.DataFrame(dimension_ratings)
        
        return overall_df, dimension_df
    
    def create_performance_matrix(self):
        """
        创建性能矩阵数据，用于热图展示
        """
        perf_df = self.load_performance_scores()
        
        # 按模型顺序排序
        model_order = [m for m in MODEL_INFO['order'] if m in perf_df['model'].values]
        perf_df['model'] = pd.Categorical(perf_df['model'], categories=model_order, ordered=True)
        perf_df = perf_df.sort_values('model')
        
        # 创建矩阵
        matrix_data = []
        for _, row in perf_df.iterrows():
            for dim in DIMENSION_INFO['order']:
                matrix_data.append({
                    'model': row['model'],
                    'dimension': dim,
                    'score': row[dim],
                    'display_model': MODEL_INFO['display_names'][row['model']],
                    'display_dimension': DIMENSION_INFO['display_names'][dim]
                })
        
        matrix_df = pd.DataFrame(matrix_data)
        
        # 透视为矩阵形式
        pivot_matrix = matrix_df.pivot(index='display_model', 
                                     columns='display_dimension', 
                                     values='score')
        
        # 按照预定义顺序重新排列
        model_display_order = [MODEL_INFO['display_names'][m] for m in model_order]
        dim_display_order = [DIMENSION_INFO['display_names'][d] for d in DIMENSION_INFO['order']]
        
        pivot_matrix = pivot_matrix.reindex(index=model_display_order, columns=dim_display_order)
        
        return pivot_matrix, matrix_df
    
    def create_top_model_radar_data(self):
        """
        创建顶级模型雷达图数据
        """
        perf_df = self.load_performance_scores()
        top_models = MODEL_INFO['top_models']
        
        radar_data = []
        for model in top_models:
            model_data = perf_df[perf_df['model'] == model].iloc[0]
            
            model_scores = []
            for dim in DIMENSION_INFO['order']:
                model_scores.append(model_data[dim])
            
            radar_data.append({
                'model': model,
                'display_name': MODEL_INFO['display_names'][model],
                'scores': model_scores,
                'dimensions': [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
            })
        
        return radar_data

    def create_models_radar_data(self, models: list[str]):
        """按给定模型列表创建雷达图数据（四维，仅使用 performance 汇总数据）。
        返回: [{model, display_name, scores, dimensions}]
        """
        perf_df = self.load_performance_scores()
        # 仅保留需要的模型，且顺序按传入列表
        needed = [m for m in models if m in perf_df['model'].values]
        radar_data = []
        for model in needed:
            row = perf_df[perf_df['model'] == model].iloc[0]
            model_scores = [row[dim] for dim in DIMENSION_INFO['order']]
            radar_data.append({
                'model': model,
                'display_name': MODEL_INFO['display_names'].get(model, model),
                'scores': model_scores,
                'dimensions': [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
            })
        return radar_data
    
    def create_forest_plot_data(self):
        """
        创建森林图数据（整体ELO评分）
        """
        overall_df, _ = self.load_elo_scores()
        
        # 按ELO评分排序
        overall_df = overall_df.sort_values('elo_rating', ascending=False)
        
        # 添加显示名称
        overall_df['display_name'] = overall_df['model'].map(MODEL_INFO['display_names'])
        
        return overall_df

    # -------------------- 新增：从 analysis_results.json 读取原始评分 --------------------
    def load_question_scores_from_analysis_results(self, judge: str = 'Doubao-Seed-1.6-combined'):
        """加载每题评分分布（用于小提琴与评分森林图）。
        返回: dict(model -> list[score])
        数据来源: base_path/src/analysis_results.json 下 question_volatility/{judge}/{model}/question_scores
        """
        import json

        results_path = self.base_path / 'src' / 'analysis_results.json'
        if not results_path.exists():
            raise FileNotFoundError(f"找不到analysis_results.json: {results_path}")

        data = json.load(open(results_path, 'r', encoding='utf-8'))
        qv = data.get('question_volatility', {}).get(judge, {})
        model_to_scores = {}
        for model in MODEL_INFO['order']:
            mobj = qv.get(model)
            if not mobj:
                continue
            qs = mobj.get('question_scores', {})
            scores = list(qs.values())
            if scores:
                model_to_scores[model] = scores
        return model_to_scores

    def create_score_distribution_df(self, judge: str = 'Doubao-Seed-1.6-combined'):
        """将每题分数展开为长表 DataFrame: [model, display_name, score].
        优先使用individual原始JSON（逐题逐轮四维），若不可用则回退到analysis_results.json的逐题整体分数。
        """
        try:
            return self._create_score_distribution_from_individual()
        except Exception as e:
            # 回退到analysis_results.json
            model_to_scores = self.load_question_scores_from_analysis_results(judge)
            rows = []
            for model, scores in model_to_scores.items():
                disp = MODEL_INFO['display_names'][model]
                for s in scores:
                    rows.append({'model': model, 'display_name': disp, 'score': float(s)})
            return pd.DataFrame(rows)

    def _create_score_distribution_from_individual(self) -> pd.DataFrame:
        """优先复用 src/individual.py 中的 IndividualEvaluationAnalyzer 提取四维分数。
        产出每个模型的逐题平均分（四维平均后再按题聚合），用于小提琴/评分森林图。
        """
        import importlib.util
        src_individual = self.base_path / 'src' / 'individual.py'
        if not src_individual.exists():
            raise FileNotFoundError(f"找不到分析脚本: {src_individual}")
        spec = importlib.util.spec_from_file_location('indiv_mod', str(src_individual))
        indiv_mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(indiv_mod)

        analyzer = indiv_mod.IndividualEvaluationAnalyzer(data_folder=str(self.base_path / 'individual'))
        analyzer.load_data()
        analyzer.process_data()

        # 从 processed_data 中直接提取原始逐评估样本：
        # 对每个 (answer_round, question) 下，四维按同一评估轮对齐求平均，得到单样本分数。
        target_dims = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']

        proc = analyzer.processed_data
        judge = 'Doubao-Seed-1.6-combined'
        if judge not in proc:
            # 若没有合并名，取任意一个judge
            judge = next(iter(proc.keys())) if proc else judge

        rows = []
        judge_data = proc.get(judge, {})
        for model, model_data in judge_data.items():
            if model not in MODEL_INFO['order']:
                continue
            disp = MODEL_INFO['display_names'][model]
            for ans_round, round_data in model_data.items():
                for qid, qdata in round_data.items():
                    dim_lists = []
                    for dim in target_dims:
                        scores = qdata.get(dim, [])
                        if isinstance(scores, list) and scores:
                            dim_lists.append(scores)
                    if len(dim_lists) == 4:
                        n = min(len(lst) for lst in dim_lists)
                        for i in range(n):
                            val = float(np.mean([lst[i] for lst in dim_lists]))
                            rows.append({'model': model, 'display_name': disp, 'score': val})

        if not rows:
            raise ValueError('individual 提取为空：未能在原始记录中聚合到四维对齐样本，请检查individual结构/维度键名')
        return pd.DataFrame(rows)

    def create_score_forest_data(self, judge: str = 'Doubao-Seed-1.6-combined', ci_mult: float = 3.0):
        """计算各模型的评分均值与95%置信区间，用于‘评分森林图’。
        返回 DataFrame: [model, display_name, mean, lower, upper, n]
        """
        df = self.create_score_distribution_df(judge)
        stats = []
        for model, g in df.groupby('model'):
            arr = g['score'].to_numpy()
            n = len(arr)
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
            se = std / np.sqrt(n) if n > 0 else 0.0
            # CI multiplier (e.g., 1.96≈95%, 2.58≈99%, 3.0≈99.7%)
            ci = ci_mult * se
            stats.append({
                'model': model,
                'display_name': MODEL_INFO['display_names'][model],
                'mean': mean,
                'lower': mean - ci,
                'upper': mean + ci,
                'n': n,
            })
        df_stats = pd.DataFrame(stats).sort_values('mean', ascending=False)
        return df_stats
    
    def create_dimension_elo_radar_data(self):
        """
        创建分维度ELO雷达图数据
        """
        _, dimension_df = self.load_elo_scores()
        
        # 为每个模型创建雷达图数据
        radar_data = []
        for model in MODEL_INFO['order']:
            model_data = dimension_df[dimension_df['model'] == model]
            
            if len(model_data) == 4:  # 确保有4个维度的数据
                scores = []
                for dim in DIMENSION_INFO['order']:
                    dim_score = model_data[model_data['dimension'] == dim]['elo_rating'].iloc[0]
                    scores.append(dim_score)
                
                radar_data.append({
                    'model': model,
                    'display_name': MODEL_INFO['display_names'][model],
                    'scores': scores,
                    'dimensions': [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
                })
        
        return radar_data

    def create_models_elo_radar_data(self, models: list[str]):
        """按给定模型列表创建 ELO 雷达图数据（四维）。
        返回: [{model, display_name, scores, dimensions}]
        """
        _, dimension_df = self.load_elo_scores()
        radar_data = []
        for model in models:
            mdf = dimension_df[dimension_df['model'] == model]
            if len(mdf) == 0:
                continue
            scores = []
            for dim in DIMENSION_INFO['order']:
                val = mdf[mdf['dimension'] == dim]['elo_rating']
                if len(val) == 0:
                    break
                scores.append(float(val.iloc[0]))
            if len(scores) == len(DIMENSION_INFO['order']):
                radar_data.append({
                    'model': model,
                    'display_name': MODEL_INFO['display_names'].get(model, model),
                    'scores': scores,
                    'dimensions': [DIMENSION_INFO['short_names'][d] for d in DIMENSION_INFO['order']]
                })
        return radar_data
    
    def get_summary_stats(self):
        """
        获取数据摘要统计信息
        """
        perf_df = self.load_performance_scores()
        overall_df, dimension_df = self.load_elo_scores()
        
        summary = {
            'performance_stats': {
                'n_models': len(perf_df),
                'n_dimensions': 4,
                'score_range': (perf_df.select_dtypes(include=[np.number]).min().min(),
                              perf_df.select_dtypes(include=[np.number]).max().max()),
                'top_model': perf_df.loc[perf_df['overall_score'].idxmax(), 'model']
            },
            'elo_stats': {
                'n_models': len(overall_df),
                'elo_range': (overall_df['elo_rating'].min(), overall_df['elo_rating'].max()),
                'top_elo_model': overall_df.loc[overall_df['elo_rating'].idxmax(), 'model']
            }
        }
        
        return summary


def main():
    """测试数据处理功能"""
    processor = DataProcessor()
    
    try:
        # 测试性能数据加载
        print("=== 测试性能数据加载 ===")
        perf_df = processor.load_performance_scores()
        print(f"加载了 {len(perf_df)} 个模型的性能数据")
        print(perf_df.head())
        
        # 测试ELO数据加载
        print("\n=== 测试ELO数据加载 ===")
        overall_df, dimension_df = processor.load_elo_scores()
        print(f"加载了 {len(overall_df)} 个模型的整体ELO数据")
        print(f"加载了 {len(dimension_df)} 条维度ELO数据")
        
        # 测试矩阵数据创建
        print("\n=== 测试性能矩阵创建 ===")
        matrix, matrix_df = processor.create_performance_matrix()
        print(f"矩阵形状: {matrix.shape}")
        print(matrix)
        
        # 测试摘要统计
        print("\n=== 数据摘要统计 ===")
        summary = processor.get_summary_stats()
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"数据处理出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
