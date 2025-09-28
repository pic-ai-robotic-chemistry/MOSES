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
- **β (skill gap)**: 4.167 (TrueSkill package default)
- **τ (dynamics)**: 0.083
- **Draw probability**: 5.00%
- **β estimation**: TrueSkill package default: β=4.167

### Match Statistics

- **Repetitions**: 1 (single run)
- **Total matches analyzed**: 97,200
- **Unique models**: 9
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)
- **Analysis duration**: 9.9s

## TrueSkill Model Rankings - Overall ELO (Single Run)

**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 34.60 | 37.50 | 0.97 | mean | 4 dimensions | 79.6% | Elite |
| 2 | o3 | 29.85 | 32.51 | 0.89 | mean | 4 dimensions | 74.7% | Expert |
| 3 | MOSES-nano | 25.95 | 28.51 | 0.85 | mean | 4 dimensions | 56.4% | Expert |
| 4 | lightrag-4.1-nano | 24.95 | 27.53 | 0.86 | mean | 4 dimensions | 64.0% | Advanced |
| 5 | lightrag-4.1 | 22.73 | 25.38 | 0.89 | mean | 4 dimensions | 57.6% | Advanced |
| 6 | gpt-4.1 | 21.53 | 24.24 | 0.90 | mean | 4 dimensions | 51.5% | Advanced |
| 7 | gpt-4.1-nano | 21.34 | 24.01 | 0.89 | mean | 4 dimensions | 75.6% | Advanced |
| 8 | gpt-4o | 16.86 | 19.82 | 0.99 | mean | 4 dimensions | 58.4% | Intermediate |
| 9 | gpt-4o-mini | 15.35 | 18.53 | 1.06 | mean | 4 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Single Run)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 37.76 | 0.90 | 35.07 | 5400 | 86.5% | 65.1% | Elite |
| 2 | o3 | 35.42 | 0.91 | 32.70 | 5400 | 78.2% | 81.5% | Elite |
| 3 | lightrag-4.1-nano | 30.02 | 0.86 | 27.42 | 5400 | 47.2% | 65.2% | Expert |
| 4 | MOSES-nano | 27.67 | 0.85 | 25.11 | 5400 | 41.3% | 56.3% | Expert |
| 5 | lightrag-4.1 | 26.71 | 0.90 | 24.01 | 5400 | 43.3% | 65.8% | Advanced |
| 6 | gpt-4.1 | 24.26 | 0.90 | 21.56 | 5400 | 60.6% | 52.8% | Advanced |
| 7 | gpt-4.1-nano | 23.83 | 0.92 | 21.07 | 5400 | 38.9% | 70.2% | Advanced |
| 8 | gpt-4o | 20.63 | 0.98 | 17.69 | 5400 | 32.9% | 57.2% | Intermediate |
| 9 | gpt-4o-mini | 19.53 | 1.03 | 16.43 | 5400 | 21.0% | N/A | Intermediate |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 31.85 | 0.84 | 29.32 | 5400 | 83.8% | 78.2% | Expert |
| 2 | o3 | 27.18 | 0.78 | 24.83 | 5400 | 80.2% | 52.4% | Advanced |
| 3 | lightrag-4.1-nano | 26.82 | 0.79 | 24.44 | 5400 | 43.4% | 55.1% | Advanced |
| 4 | MOSES-nano | 26.05 | 0.78 | 23.69 | 5400 | 44.9% | 69.6% | Advanced |
| 5 | gpt-4o-mini | 22.97 | 0.83 | 20.48 | 5400 | 18.9% | 57.2% | Advanced |
| 6 | lightrag-4.1 | 21.88 | 0.84 | 19.35 | 5400 | 38.3% | 51.2% | Intermediate |
| 7 | gpt-4o | 21.70 | 0.85 | 19.15 | 5400 | 33.1% | 57.1% | Intermediate |
| 8 | gpt-4.1-nano | 20.61 | 0.88 | 17.99 | 5400 | 46.3% | 72.3% | Intermediate |
| 9 | gpt-4.1 | 17.04 | 0.98 | 14.11 | 5400 | 61.1% | N/A | Novice |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 38.58 | 1.00 | 35.58 | 5400 | 92.8% | 56.6% | Elite |
| 2 | MOSES | 37.58 | 0.92 | 34.82 | 5400 | 87.1% | 94.0% | Elite |
| 3 | MOSES-nano | 28.22 | 0.90 | 25.53 | 5400 | 41.3% | 54.4% | Expert |
| 4 | lightrag-4.1-nano | 27.55 | 0.92 | 24.78 | 5400 | 51.8% | 58.9% | Advanced |
| 5 | gpt-4.1 | 26.20 | 0.92 | 23.43 | 5400 | 62.2% | 64.7% | Advanced |
| 6 | lightrag-4.1 | 23.92 | 0.96 | 21.03 | 5400 | 46.1% | 57.7% | Advanced |
| 7 | gpt-4.1-nano | 22.74 | 0.95 | 19.87 | 5400 | 39.9% | 88.1% | Intermediate |
| 8 | gpt-4o | 15.57 | 1.13 | 12.17 | 5400 | 21.0% | 61.8% | Novice |
| 9 | gpt-4o-mini | 13.73 | 1.26 | 9.95 | 5400 | 7.8% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 42.82 | 1.21 | 39.19 | 5400 | 94.0% | 96.1% | Elite |
| 2 | MOSES-nano | 32.09 | 0.87 | 29.48 | 5400 | 61.2% | 67.0% | Expert |
| 3 | gpt-4.1 | 29.44 | 0.81 | 27.01 | 5400 | 38.9% | 52.7% | Expert |
| 4 | lightrag-4.1 | 29.03 | 0.84 | 26.52 | 5400 | 63.5% | 51.1% | Expert |
| 5 | gpt-4.1-nano | 28.87 | 0.82 | 26.41 | 5400 | 35.2% | 50.0% | Expert |
| 6 | o3 | 28.87 | 0.86 | 26.31 | 5400 | 62.7% | 69.8% | Expert |
| 7 | lightrag-4.1-nano | 25.75 | 0.86 | 23.18 | 5400 | 63.2% | 76.7% | Advanced |
| 8 | gpt-4o | 21.36 | 0.98 | 18.43 | 5400 | 20.1% | 71.6% | Intermediate |
| 9 | gpt-4o-mini | 17.90 | 1.12 | 14.53 | 5400 | 11.3% | N/A | Novice |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **34.60**

### Most Consistent Model
**MOSES-nano** shows the lowest uncertainty with σ=0.85

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Theoretical Depth | MOSES | 39.19 | 42.82 | 1.21 | 9.72 |
| Completeness | MOSES | 35.07 | 37.76 | 0.90 | 2.38 |
| Correctness | MOSES | 29.32 | 31.85 | 0.84 | 4.49 |
| Rigor And Information Density | o3 | 35.58 | 38.58 | 1.00 | 0.76 |

### Rating Distribution
- **Mean Overall ELO**: 23.68
- **ELO Std**: 5.69
- **ELO Range**: 34.60 - 15.35
- **Mean μ (Skill)**: 26.45
- **Mean σ (Uncertainty)**: 0.92
- **Models Analyzed**: 9
- **Data Source**: real
- **Total Matches**: 97,200
- **Matches per Dimension**: 24,300

### Method Details

**Overall ELO Calculation**:
- Uses dimension averaging approach
- Each dimension calculated independently, then averaged
- Provides balanced ranking across all evaluation aspects

**Dimension ELO Calculations**:
- Each dimension calculated independently (pure separation)
- Allows comparison of model strengths across different aspects

**Data Aggregation Level**: llm_only
- LLM评分聚合: 5个LLM评分 → 平均值
- 回答轮次保留: 保持轮次间差异
- 每个问题-维度生成N个匹配（N=回答轮次数）

