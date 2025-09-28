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
| 1 | MOSES | 31.21 | 33.93 | 0.91 | mean | 4 dimensions | 53.4% | Elite |
| 2 | o3 | 30.57 | 33.42 | 0.95 | mean | 4 dimensions | 74.7% | Elite |
| 3 | gpt-4.1 | 26.76 | 29.40 | 0.88 | mean | 4 dimensions | 66.1% | Expert |
| 4 | MOSES-nano | 24.23 | 26.90 | 0.89 | mean | 4 dimensions | 56.0% | Advanced |
| 5 | gpt-4.1-nano | 23.27 | 25.98 | 0.90 | mean | 4 dimensions | 52.6% | Advanced |
| 6 | lightrag-4.1-nano | 22.90 | 25.59 | 0.90 | mean | 4 dimensions | 61.8% | Advanced |
| 7 | lightrag-4.1 | 21.13 | 23.79 | 0.89 | mean | 4 dimensions | 56.1% | Advanced |
| 8 | gpt-4o | 20.02 | 22.86 | 0.95 | mean | 4 dimensions | 67.8% | Advanced |
| 9 | gpt-4o-mini | 17.08 | 20.07 | 1.00 | mean | 4 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Single Run)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 33.44 | 0.97 | 30.54 | 5400 | 78.2% | 66.6% | Elite |
| 2 | gpt-4.1 | 30.86 | 0.83 | 28.36 | 5400 | 60.6% | 69.3% | Expert |
| 3 | gpt-4.1-nano | 27.83 | 0.85 | 25.27 | 5400 | 38.9% | 52.4% | Expert |
| 4 | MOSES | 27.47 | 0.82 | 25.01 | 5400 | 86.5% | 73.8% | Expert |
| 5 | gpt-4o | 23.63 | 0.87 | 21.04 | 5400 | 32.9% | 52.3% | Advanced |
| 6 | MOSES-nano | 23.28 | 0.87 | 20.68 | 5400 | 41.3% | 61.4% | Advanced |
| 7 | gpt-4o-mini | 21.53 | 0.88 | 18.88 | 5400 | 21.0% | 59.7% | Intermediate |
| 8 | lightrag-4.1 | 20.05 | 0.90 | 17.33 | 5400 | 43.3% | 60.8% | Intermediate |
| 9 | lightrag-4.1-nano | 18.39 | 0.92 | 15.62 | 5400 | 47.2% | N/A | Intermediate |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | gpt-4.1 | 31.75 | 0.81 | 29.32 | 5400 | 61.1% | 50.7% | Expert |
| 2 | o3 | 31.65 | 0.95 | 28.80 | 5400 | 80.2% | 74.0% | Expert |
| 3 | gpt-4.1-nano | 27.76 | 0.84 | 25.25 | 5400 | 46.3% | 56.2% | Expert |
| 4 | MOSES | 26.83 | 0.80 | 24.42 | 5400 | 83.8% | 66.3% | Advanced |
| 5 | gpt-4o | 24.30 | 0.87 | 21.69 | 5400 | 33.1% | 69.2% | Advanced |
| 6 | gpt-4o-mini | 21.28 | 0.89 | 18.61 | 5400 | 18.9% | 52.4% | Intermediate |
| 7 | MOSES-nano | 20.91 | 0.88 | 18.27 | 5400 | 44.9% | 71.8% | Intermediate |
| 8 | lightrag-4.1 | 17.43 | 0.93 | 14.66 | 5400 | 38.3% | 60.6% | Novice |
| 9 | lightrag-4.1-nano | 15.81 | 0.94 | 13.00 | 5400 | 43.4% | N/A | Novice |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 38.57 | 0.99 | 35.62 | 5400 | 92.8% | 62.4% | Elite |
| 2 | MOSES | 36.67 | 0.86 | 34.08 | 5400 | 87.1% | 79.5% | Elite |
| 3 | lightrag-4.1-nano | 31.71 | 0.87 | 29.11 | 5400 | 51.8% | 68.0% | Expert |
| 4 | gpt-4.1 | 28.90 | 0.90 | 26.19 | 5400 | 62.2% | 60.3% | Expert |
| 5 | MOSES-nano | 27.33 | 0.92 | 24.55 | 5400 | 41.3% | 50.9% | Advanced |
| 6 | lightrag-4.1 | 27.18 | 0.90 | 24.47 | 5400 | 46.1% | 85.8% | Advanced |
| 7 | gpt-4.1-nano | 20.71 | 1.00 | 17.70 | 5400 | 39.9% | 72.5% | Intermediate |
| 8 | gpt-4o | 17.08 | 1.12 | 13.72 | 5400 | 21.0% | 69.5% | Novice |
| 9 | gpt-4o-mini | 13.96 | 1.24 | 10.24 | 5400 | 7.8% | N/A | Novice |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 44.77 | 1.15 | 41.33 | 5400 | 94.0% | 91.5% | Elite |
| 2 | lightrag-4.1-nano | 36.46 | 0.86 | 33.89 | 5400 | 63.2% | 52.6% | Elite |
| 3 | MOSES-nano | 36.07 | 0.88 | 33.42 | 5400 | 61.2% | 82.2% | Elite |
| 4 | lightrag-4.1 | 30.51 | 0.82 | 28.05 | 5400 | 63.5% | 53.3% | Expert |
| 5 | o3 | 30.02 | 0.89 | 27.34 | 5400 | 62.7% | 65.4% | Expert |
| 6 | gpt-4.1-nano | 27.62 | 0.92 | 24.86 | 5400 | 35.2% | 57.7% | Advanced |
| 7 | gpt-4o | 26.44 | 0.93 | 23.65 | 5400 | 20.1% | 52.3% | Advanced |
| 8 | gpt-4.1 | 26.10 | 0.97 | 23.18 | 5400 | 38.9% | 66.4% | Advanced |
| 9 | gpt-4o-mini | 23.53 | 0.99 | 20.58 | 5400 | 11.3% | N/A | Advanced |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **31.21**

### Most Consistent Model
**gpt-4.1** shows the lowest uncertainty with σ=0.88

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Correctness | gpt-4.1 | 29.32 | 31.75 | 0.81 | 0.52 |
| Rigor And Information Density | o3 | 35.62 | 38.57 | 0.99 | 1.54 |
| Completeness | o3 | 30.54 | 33.44 | 0.97 | 2.18 |
| Theoretical Depth | MOSES | 41.33 | 44.77 | 1.15 | 7.44 |

### Rating Distribution
- **Mean Overall ELO**: 24.13
- **ELO Std**: 4.43
- **ELO Range**: 31.21 - 17.08
- **Mean μ (Skill)**: 26.88
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

