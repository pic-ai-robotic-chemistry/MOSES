# TrueSkill ELO Rating Analysis (Excluding Logic/Clarity)

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
- **Total matches analyzed**: 324
- **Unique models**: 13
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Human question-dimension matches (aggregation: double)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)

## TrueSkill Model Rankings - Overall ELO (Single Run)

**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.

### Judge: human

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 28.44 | 30.60 | 0.72 | mean | 4 dimensions | 68.2% | Expert |
| 2 | lightrag-gpt-4_1 | 25.88 | 27.82 | 0.65 | mean | 4 dimensions | 53.9% | Expert |
| 3 | o3-final | 25.32 | 27.25 | 0.64 | mean | 4 dimensions | 52.5% | Expert |
| 4 | gpt-4.1-final | 24.96 | 26.88 | 0.64 | mean | 4 dimensions | 57.3% | Advanced |
| 5 | gpt-4.1-nano-final-815-1 | 23.89 | 25.80 | 0.63 | mean | 4 dimensions | 51.7% | Advanced |
| 6 | reordered_MOSES-nano-final | 23.64 | 25.55 | 0.64 | mean | 4 dimensions | 50.2% | Advanced |
| 7 | lightrag-gpt-4_1-nano | 23.61 | 25.52 | 0.64 | mean | 4 dimensions | 51.1% | Advanced |
| 8 | gpt-4o-final-815-1 | 23.45 | 25.36 | 0.63 | mean | 4 dimensions | 51.0% | Advanced |
| 9 | o1-final | 23.31 | 25.21 | 0.64 | mean | 4 dimensions | 55.7% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 22.44 | 24.37 | 0.64 | mean | 4 dimensions | 51.0% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 22.31 | 24.22 | 0.64 | mean | 4 dimensions | 86.0% | Advanced |
| 12 | llasmol | 15.79 | 17.89 | 0.70 | mean | 4 dimensions | 53.2% | Intermediate |
| 13 | darwin | 15.29 | 17.41 | 0.71 | mean | 4 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Single Run)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: human

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 28.83 | 0.65 | 26.89 | 81 | 84.9% | 51.5% | Expert |
| 2 | gpt-4.1-final | 28.61 | 0.65 | 26.65 | 81 | 81.3% | 53.7% | Expert |
| 3 | o3-final | 28.07 | 0.65 | 26.13 | 81 | 78.7% | 51.0% | Expert |
| 4 | lightrag-gpt-4_1 | 27.92 | 0.64 | 25.99 | 81 | 77.5% | 59.4% | Expert |
| 5 | gpt-4.1-nano-final-815-1 | 26.52 | 0.64 | 24.60 | 81 | 65.5% | 52.4% | Advanced |
| 6 | gpt-4o-final-815-1 | 26.17 | 0.64 | 24.26 | 81 | 63.8% | 56.6% | Advanced |
| 7 | gpt-4o-mini-final-815-1 | 25.19 | 0.64 | 23.27 | 81 | 58.4% | 52.2% | Advanced |
| 8 | lightrag-gpt-4_1-nano | 24.88 | 0.64 | 22.96 | 81 | 51.7% | 50.5% | Advanced |
| 9 | o1-final | 24.81 | 0.64 | 22.89 | 81 | 51.0% | 50.7% | Advanced |
| 10 | reordered_MOSES-nano-final | 24.70 | 0.64 | 22.78 | 81 | 50.9% | 55.3% | Advanced |
| 11 | chemqa27_from_chem13b_rag_infer_yesthink | 23.91 | 0.65 | 21.97 | 81 | 45.5% | 87.5% | Advanced |
| 12 | llasmol | 17.16 | 0.70 | 15.07 | 81 | 12.2% | 54.0% | Intermediate |
| 13 | darwin | 16.57 | 0.71 | 14.45 | 81 | 10.9% | N/A | Novice |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | gpt-4.1-final | 26.79 | 0.63 | 24.90 | 81 | 94.1% | 51.1% | Advanced |
| 2 | reordered_MOSES-final | 26.62 | 0.63 | 24.74 | 81 | 89.5% | 50.9% | Advanced |
| 3 | o3-final | 26.49 | 0.63 | 24.60 | 81 | 87.2% | 50.5% | Advanced |
| 4 | lightrag-gpt-4_1 | 26.41 | 0.63 | 24.52 | 81 | 89.4% | 50.5% | Advanced |
| 5 | o1-final | 26.33 | 0.63 | 24.45 | 81 | 87.4% | 50.7% | Advanced |
| 6 | gpt-4.1-nano-final-815-1 | 26.23 | 0.63 | 24.34 | 81 | 86.3% | 51.3% | Advanced |
| 7 | lightrag-gpt-4_1-nano | 26.04 | 0.63 | 24.15 | 81 | 85.5% | 51.7% | Advanced |
| 8 | reordered_MOSES-nano-final | 25.79 | 0.63 | 23.89 | 81 | 77.4% | 50.4% | Advanced |
| 9 | gpt-4o-final-815-1 | 25.73 | 0.63 | 23.84 | 81 | 75.4% | 55.3% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 24.96 | 0.64 | 23.05 | 81 | 62.9% | 52.9% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 24.53 | 0.64 | 22.62 | 81 | 60.9% | 81.1% | Advanced |
| 12 | llasmol | 19.34 | 0.70 | 17.25 | 80 | 22.5% | 53.4% | Intermediate |
| 13 | darwin | 18.84 | 0.71 | 16.71 | 81 | 13.0% | N/A | Intermediate |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 30.06 | 0.67 | 28.05 | 81 | 95.9% | 65.9% | Expert |
| 2 | o3-final | 27.65 | 0.64 | 25.73 | 81 | 80.1% | 50.3% | Expert |
| 3 | lightrag-gpt-4_1 | 27.61 | 0.64 | 25.69 | 81 | 81.6% | 54.2% | Expert |
| 4 | gpt-4.1-final | 26.99 | 0.63 | 25.09 | 81 | 79.0% | 54.2% | Expert |
| 5 | gpt-4.1-nano-final-815-1 | 26.37 | 0.63 | 24.47 | 81 | 70.6% | 51.7% | Advanced |
| 6 | o1-final | 26.12 | 0.63 | 24.22 | 81 | 69.5% | 51.8% | Advanced |
| 7 | lightrag-gpt-4_1-nano | 25.86 | 0.64 | 23.95 | 81 | 66.2% | 50.6% | Advanced |
| 8 | reordered_MOSES-nano-final | 25.77 | 0.64 | 23.87 | 81 | 64.5% | 51.5% | Advanced |
| 9 | gpt-4o-final-815-1 | 25.55 | 0.64 | 23.64 | 81 | 63.3% | 55.4% | Advanced |
| 10 | chemqa27_from_chem13b_rag_infer_yesthink | 24.74 | 0.64 | 22.82 | 81 | 54.4% | 53.6% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 24.22 | 0.64 | 22.29 | 81 | 52.8% | 88.1% | Advanced |
| 12 | llasmol | 17.29 | 0.71 | 15.15 | 81 | 11.4% | 54.3% | Intermediate |
| 13 | darwin | 16.65 | 0.72 | 14.48 | 81 | 10.0% | N/A | Novice |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | reordered_MOSES-final | 36.88 | 0.93 | 34.09 | 81 | 99.3% | 89.9% | Elite |
| 2 | lightrag-gpt-4_1 | 29.34 | 0.67 | 27.32 | 81 | 85.4% | 66.8% | Expert |
| 3 | o3-final | 26.79 | 0.65 | 24.84 | 81 | 70.9% | 55.7% | Advanced |
| 4 | reordered_MOSES-nano-final | 25.94 | 0.64 | 24.01 | 81 | 69.7% | 54.4% | Advanced |
| 5 | lightrag-gpt-4_1-nano | 25.30 | 0.64 | 23.38 | 81 | 65.3% | 51.2% | Advanced |
| 6 | gpt-4.1-final | 25.13 | 0.64 | 23.20 | 81 | 64.0% | 57.2% | Advanced |
| 7 | gpt-4.1-nano-final-815-1 | 24.07 | 0.64 | 22.16 | 81 | 56.6% | 50.6% | Advanced |
| 8 | gpt-4o-final-815-1 | 23.98 | 0.64 | 22.07 | 81 | 56.4% | 50.8% | Advanced |
| 9 | chemqa27_from_chem13b_rag_infer_yesthink | 23.86 | 0.64 | 21.93 | 81 | 52.9% | 51.9% | Advanced |
| 10 | o1-final | 23.58 | 0.64 | 21.66 | 81 | 51.2% | 54.3% | Advanced |
| 11 | gpt-4o-mini-final-815-1 | 22.95 | 0.64 | 21.04 | 81 | 47.6% | 81.2% | Advanced |
| 12 | llasmol | 17.76 | 0.68 | 15.71 | 81 | 14.9% | 51.2% | Intermediate |
| 13 | darwin | 17.57 | 0.69 | 15.51 | 81 | 13.7% | N/A | Intermediate |


## Key TrueSkill Insights

### Highest Rated Model
**reordered_MOSES-final** achieves the highest overall ELO rating of **28.44**

### Most Consistent Model
**gpt-4.1-nano-final-815-1** shows the lowest uncertainty with σ=0.63

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Completeness | reordered_MOSES-final | 26.89 | 28.83 | 0.65 | 0.24 |
| Rigor And Information Density | reordered_MOSES-final | 28.05 | 30.06 | 0.67 | 2.33 |
| Theoretical Depth | reordered_MOSES-final | 34.09 | 36.88 | 0.93 | 6.77 |
| Correctness | gpt-4.1-final | 24.90 | 26.79 | 0.63 | 0.16 |

### Rating Distribution
- **Mean Overall ELO**: 22.95
- **ELO Std**: 3.52
- **ELO Range**: 28.44 - 15.29
- **Mean μ (Skill)**: 24.91
- **Mean σ (Uncertainty)**: 0.65
- **Models Analyzed**: 13
- **Data Source**: human
- **Total Matches**: 324
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

