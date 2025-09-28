# TrueSkill ELO Rating Analysis (Full Analysis)

## Methodology

This analysis uses Microsoft's **TrueSkill** algorithm to calculate dynamic skill ratings:

- **TrueSkill**: Bayesian skill rating system where each model has skill ~ N(μ, σ²)
- **μ (mu)**: Mean skill level
- **σ (sigma)**: Uncertainty about skill level
- **Rating**: Conservative estimate = μ - 3σ (99.7% confidence lower bound)
- **Match Simulation**: Multiple matches simulated from score distributions

### TrueSkill Parameters

- **Initial μ**: 25.0
- **Initial σ**: 8.333
- **β (skill gap)**: 4.100 (custom fixed value)
- **τ (dynamics)**: 0.083
- **Draw probability**: 5.00%
- **β estimation**: Manual override: β=4.100

### Match Statistics

- **Repetitions**: 1 (single run)
- **Total matches analyzed**: 486
- **Unique models**: 13
- **Judge models**: 1
- **Dimensions analyzed**: 6
- **Match generation**: Human question-dimension matches (aggregation: double)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)

## TrueSkill Model Rankings - Overall ELO (Single Run)

**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.

### Judge: human

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 27.06 | 29.14 | 0.69 | mean | 6 dimensions | 62.3% | Expert |
| 2 | lightrag-gpt-4_1 | 25.35 | 27.29 | 0.65 | mean | 6 dimensions | 53.3% | Expert |
| 3 | o3-final | 24.87 | 26.80 | 0.64 | mean | 6 dimensions | 50.8% | Advanced |
| 4 | gpt-4.1-final | 24.77 | 26.68 | 0.64 | mean | 6 dimensions | 55.6% | Advanced |
| 5 | gpt-4.1-nano-final-815-1 | 23.94 | 25.86 | 0.64 | mean | 6 dimensions | 51.5% | Advanced |
| 6 | lightrag-gpt-4_1-nano | 23.71 | 25.63 | 0.64 | mean | 6 dimensions | 50.9% | Advanced |
| 7 | reordered_MOSES-nano-final | 23.56 | 25.50 | 0.65 | mean | 6 dimensions | 50.2% | Advanced |
| 8 | o1-final | 23.55 | 25.47 | 0.64 | mean | 6 dimensions | 50.9% | Advanced |
| 9 | gpt-4o-final-815-1 | 23.40 | 25.34 | 0.64 | mean | 6 dimensions | 53.1% | Advanced |
| 10 | gpt-4o-mini-final-815-1 | 22.90 | 24.88 | 0.66 | mean | 6 dimensions | 50.3% | Advanced |
| 11 | chemqa27_from_chem13b_rag_infer_yesthink | 22.85 | 24.84 | 0.66 | mean | 6 dimensions | 82.5% | Advanced |
| 12 | llasmol | 16.90 | 19.33 | 0.81 | mean | 6 dimensions | 54.1% | Intermediate |
| 13 | darwin | 15.73 | 18.72 | 1.00 | mean | 6 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Single Run)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: human

#### Clarity

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | gpt-4.1-final | 27.03 | 0.63 | 25.14 | 81 | 94.2% | 51.3% | Expert |
| 2 | reordered_MOSES-final | 26.84 | 0.63 | 24.95 | 81 | 87.8% | 51.0% | Advanced |
| 3 | o1-final | 26.69 | 0.63 | 24.80 | 81 | 89.5% | 50.8% | Advanced |
| 4 | o3-final | 26.56 | 0.63 | 24.67 | 81 | 85.7% | 51.0% | Advanced |
| 5 | gpt-4.1-nano-final-815-1 | 26.42 | 0.63 | 24.54 | 81 | 82.4% | 51.0% | Advanced |
| 6 | lightrag-gpt-4_1-nano | 26.28 | 0.63 | 24.39 | 81 | 82.2% | 50.9% | Advanced |
| 7 | lightrag-gpt-4_1 | 26.15 | 0.63 | 24.25 | 81 | 74.6% | 52.9% | Advanced |
| 8 | gpt-4o-final-815-1 | 25.72 | 0.63 | 23.83 | 81 | 74.0% | 51.8% | Advanced |
| 9 | reordered_MOSES-nano-final | 25.47 | 0.63 | 23.57 | 81 | 65.8% | 50.1% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 25.45 | 0.63 | 23.55 | 81 | 65.2% | 52.1% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 25.14 | 0.63 | 23.24 | 81 | 63.9% | 79.9% | Advanced |
| 12 | llasmol | 20.22 | 0.68 | 18.17 | 81 | 26.6% | 58.3% | Intermediate |
| 13 | darwin | 18.98 | 0.71 | 16.85 | 81 | 12.0% | N/A | Intermediate |

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 28.87 | 0.65 | 26.92 | 81 | 84.8% | 52.4% | Expert |
| 2 | gpt-4.1-final | 28.51 | 0.65 | 26.56 | 81 | 81.3% | 53.2% | Expert |
| 3 | o3-final | 28.04 | 0.65 | 26.09 | 81 | 78.7% | 51.3% | Expert |
| 4 | lightrag-gpt-4_1 | 27.84 | 0.65 | 25.90 | 80 | 77.9% | 59.1% | Expert |
| 5 | gpt-4.1-nano-final-815-1 | 26.49 | 0.64 | 24.58 | 81 | 65.5% | 53.8% | Advanced |
| 6 | gpt-4o-final-815-1 | 25.94 | 0.64 | 24.03 | 81 | 63.7% | 50.9% | Advanced |
| 7 | gpt-4o-mini-final-815-1 | 25.81 | 0.64 | 23.90 | 81 | 58.4% | 57.1% | Advanced |
| 8 | reordered_MOSES-nano-final | 24.76 | 0.64 | 22.84 | 81 | 50.9% | 50.3% | Advanced |
| 9 | lightrag-gpt-4_1-nano | 24.72 | 0.64 | 22.80 | 81 | 51.7% | 50.9% | Advanced |
| 10 | o1-final | 24.58 | 0.64 | 22.66 | 81 | 51.0% | 53.0% | Advanced |
| 11 | chemqa27_from_chem13b_rag_infer_yesthink | 24.14 | 0.65 | 22.19 | 81 | 45.5% | 88.7% | Advanced |
| 12 | llasmol | 17.02 | 0.70 | 14.93 | 81 | 12.3% | 53.7% | Novice |
| 13 | darwin | 16.48 | 0.71 | 14.36 | 81 | 10.9% | N/A | Novice |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | gpt-4.1-final | 25.00 | 0.65 | 23.06 | 73 | 100.0% | 50.0% | Advanced |
| 2 | lightrag-gpt-4_1 | 25.00 | 0.65 | 23.04 | 68 | 100.0% | 50.0% | Advanced |
| 3 | o3-final | 25.00 | 0.66 | 23.03 | 66 | 100.0% | 50.0% | Advanced |
| 4 | reordered_MOSES-final | 25.00 | 0.66 | 23.03 | 66 | 100.0% | 50.0% | Advanced |
| 5 | o1-final | 25.00 | 0.66 | 23.02 | 64 | 100.0% | 50.0% | Advanced |
| 6 | lightrag-gpt-4_1-nano | 25.00 | 0.66 | 23.01 | 63 | 100.0% | 50.0% | Advanced |
| 7 | gpt-4.1-nano-final-815-1 | 25.00 | 0.67 | 23.00 | 62 | 100.0% | 50.0% | Advanced |
| 8 | reordered_MOSES-nano-final | 25.00 | 0.69 | 22.93 | 53 | 100.0% | 50.0% | Advanced |
| 9 | gpt-4o-final-815-1 | 25.00 | 0.70 | 22.91 | 51 | 100.0% | 50.0% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 25.00 | 0.77 | 22.68 | 38 | 100.0% | 50.0% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 25.00 | 0.78 | 22.66 | 36 | 100.0% | 50.0% | Advanced |
| 12 | llasmol | 25.00 | 1.38 | 20.86 | 10 | 100.0% | 50.0% | Advanced |
| 13 | darwin | 25.00 | 2.42 | 17.75 | 3 | 100.0% | N/A | Intermediate |

#### Logic

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 27.47 | 0.63 | 25.57 | 80 | 90.8% | 50.6% | Expert |
| 2 | gpt-4.1-final | 27.37 | 0.63 | 25.48 | 81 | 93.4% | 50.9% | Expert |
| 3 | o3-final | 27.23 | 0.63 | 25.34 | 81 | 90.3% | 50.2% | Expert |
| 4 | lightrag-gpt-4_1 | 27.21 | 0.63 | 25.31 | 80 | 89.2% | 52.3% | Expert |
| 5 | gpt-4.1-nano-final-815-1 | 26.87 | 0.63 | 24.98 | 81 | 83.4% | 51.1% | Advanced |
| 6 | o1-final | 26.72 | 0.63 | 24.82 | 80 | 82.7% | 52.3% | Advanced |
| 7 | lightrag-gpt-4_1-nano | 26.37 | 0.63 | 24.48 | 81 | 77.5% | 53.2% | Advanced |
| 8 | gpt-4o-final-815-1 | 25.89 | 0.63 | 24.00 | 81 | 71.5% | 51.5% | Advanced |
| 9 | reordered_MOSES-nano-final | 25.67 | 0.64 | 23.76 | 81 | 62.7% | 52.6% | Advanced |
| 10 | gpt-4o-mini-final-815-1 | 25.28 | 0.64 | 23.36 | 81 | 60.5% | 50.2% | Advanced |
| 11 | chemqa27_from_chem13b_rag_infer_yesthink | 25.24 | 0.64 | 23.32 | 81 | 59.1% | 86.2% | Advanced |
| 12 | llasmol | 18.83 | 0.70 | 16.72 | 81 | 15.7% | 55.4% | Intermediate |
| 13 | darwin | 18.04 | 0.73 | 15.86 | 81 | 10.9% | N/A | Intermediate |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 29.68 | 0.66 | 27.69 | 81 | 95.9% | 63.5% | Expert |
| 2 | lightrag-gpt-4_1 | 27.65 | 0.64 | 25.74 | 81 | 81.6% | 52.0% | Expert |
| 3 | o3-final | 27.36 | 0.64 | 25.44 | 81 | 80.1% | 53.1% | Expert |
| 4 | gpt-4.1-final | 26.90 | 0.63 | 25.00 | 81 | 79.0% | 54.3% | Expert |
| 5 | gpt-4.1-nano-final-815-1 | 26.27 | 0.63 | 24.37 | 81 | 70.6% | 50.7% | Advanced |
| 6 | o1-final | 26.17 | 0.63 | 24.27 | 81 | 69.5% | 51.4% | Advanced |
| 7 | lightrag-gpt-4_1-nano | 25.96 | 0.64 | 24.05 | 81 | 66.2% | 50.8% | Advanced |
| 8 | reordered_MOSES-nano-final | 25.83 | 0.64 | 23.92 | 81 | 64.5% | 53.0% | Advanced |
| 9 | gpt-4o-final-815-1 | 25.39 | 0.64 | 23.48 | 81 | 63.3% | 53.8% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 24.82 | 0.65 | 22.88 | 81 | 54.4% | 51.0% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 24.68 | 0.64 | 22.76 | 81 | 52.8% | 90.3% | Advanced |
| 12 | llasmol | 17.05 | 0.72 | 14.90 | 81 | 11.4% | 56.5% | Novice |
| 13 | darwin | 16.08 | 0.73 | 13.90 | 81 | 10.0% | N/A | Novice |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 36.97 | 0.92 | 34.21 | 81 | 99.2% | 88.4% | Elite |
| 2 | lightrag-gpt-4_1 | 29.90 | 0.68 | 27.87 | 81 | 85.4% | 71.2% | Expert |
| 3 | o3-final | 26.62 | 0.65 | 24.67 | 81 | 70.9% | 52.3% | Advanced |
| 4 | reordered_MOSES-nano-final | 26.28 | 0.65 | 24.34 | 81 | 69.6% | 55.5% | Advanced |
| 5 | lightrag-gpt-4_1-nano | 25.47 | 0.64 | 23.54 | 80 | 65.3% | 51.3% | Advanced |
| 6 | gpt-4.1-final | 25.27 | 0.64 | 23.35 | 81 | 63.9% | 56.1% | Advanced |
| 7 | chemqa27_from_chem13b_rag_infer_yesthink | 24.38 | 0.64 | 22.44 | 80 | 53.3% | 51.9% | Advanced |
| 8 | gpt-4o-final-815-1 | 24.09 | 0.64 | 22.18 | 81 | 56.3% | 50.1% | Advanced |
| 9 | gpt-4.1-nano-final-815-1 | 24.08 | 0.64 | 22.17 | 81 | 56.6% | 52.7% | Advanced |
| 10 | o1-final | 23.68 | 0.64 | 21.75 | 81 | 51.2% | 52.0% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 23.39 | 0.64 | 21.47 | 80 | 47.4% | 82.5% | Advanced |
| 12 | llasmol | 17.90 | 0.69 | 15.84 | 81 | 14.8% | 51.0% | Intermediate |
| 13 | darwin | 17.75 | 0.69 | 15.68 | 81 | 13.6% | N/A | Intermediate |


## Key TrueSkill Insights

### Highest Rated Model
**reordered_MOSES-final** achieves the highest overall ELO rating of **27.06**

### Most Consistent Model
**gpt-4.1-final** shows the lowest uncertainty with σ=0.64

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Theoretical Depth | reordered_MOSES-final | 34.21 | 36.97 | 0.92 | 6.34 |
| Logic | reordered_MOSES-final | 25.57 | 27.47 | 0.63 | 0.09 |
| Rigor And Information Density | reordered_MOSES-final | 27.69 | 29.68 | 0.66 | 1.96 |
| Correctness | gpt-4.1-final | 23.06 | 25.00 | 0.65 | 0.03 |
| Clarity | gpt-4.1-final | 25.14 | 27.03 | 0.63 | 0.19 |
| Completeness | reordered_MOSES-final | 26.92 | 28.87 | 0.65 | 0.36 |

### Rating Distribution
- **Mean Overall ELO**: 22.97
- **ELO Std**: 3.05
- **ELO Range**: 27.06 - 15.73
- **Mean μ (Skill)**: 25.04
- **Mean σ (Uncertainty)**: 0.69
- **Models Analyzed**: 13
- **Data Source**: human
- **Total Matches**: 486
- **Matches per Dimension**: 81

### Method Details

**Overall ELO Calculation**:
- Uses dimension averaging approach
- Each dimension calculated independently, then averaged
- Provides balanced ranking across all evaluation aspects

**Dimension ELO Calculations**:
- Each dimension calculated independently (pure separation)
- Allows comparison of model strengths across different aspects

**Data Aggregation Level**: double
- LLM评分聚合: 5个LLM评分 → 平均值
- 回答轮次聚合: 多轮回答 → 平均值
- 每个问题-维度生成1个匹配

