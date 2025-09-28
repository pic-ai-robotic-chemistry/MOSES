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
- **Total matches analyzed**: 283,500
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)
- **Analysis duration**: 33.0s

## TrueSkill Model Rankings - Overall ELO (Single Run)

**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 34.17 | 37.55 | 1.12 | mean | 4 dimensions | 87.4% | Elite |
| 2 | o3 | 27.30 | 30.55 | 1.09 | mean | 4 dimensions | 52.0% | Expert |
| 3 | MOSES-nano | 27.28 | 30.25 | 0.99 | mean | 4 dimensions | 77.0% | Expert |
| 4 | gpt-4.1 | 22.98 | 25.78 | 0.93 | mean | 4 dimensions | 51.1% | Advanced |
| 5 | gpt-4.1-nano | 22.81 | 25.61 | 0.93 | mean | 4 dimensions | 49.5% | Advanced |
| 6 | lightrag-4.1-nano | 22.72 | 25.69 | 0.99 | mean | 4 dimensions | 52.7% | Advanced |
| 7 | spark-chem13b-nothink | 22.44 | 25.29 | 0.95 | mean | 4 dimensions | 65.7% | Advanced |
| 8 | spark-chem13b-think | 19.97 | 22.85 | 0.96 | mean | 4 dimensions | 51.3% | Intermediate |
| 9 | lightrag-4.1 | 19.69 | 22.64 | 0.98 | mean | 4 dimensions | 60.5% | Intermediate |
| 10 | o1 | 17.98 | 21.03 | 1.02 | mean | 4 dimensions | 55.0% | Intermediate |
| 11 | gpt-4o-mini | 17.33 | 20.26 | 0.98 | mean | 4 dimensions | 56.4% | Intermediate |
| 12 | gpt-4o | 16.28 | 19.29 | 1.00 | mean | 4 dimensions | 99.7% | Intermediate |
| 13 | llasmol-top5 | -0.44 | 2.47 | 0.97 | mean | 4 dimensions | 46.5% | Beginner |
| 14 | darwin | -0.84 | 3.01 | 1.28 | mean | 4 dimensions | 56.3% | Beginner |
| 15 | llasmol-top1 | -0.86 | 2.04 | 0.97 | mean | 4 dimensions | N/A | Beginner |

## Detailed Dimension Analysis (Single Run)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 29.72 | 0.93 | 26.94 | 9450 | 90.3% | 70.3% | Expert |
| 2 | spark-chem13b-nothink | 26.51 | 0.91 | 23.79 | 9450 | 48.2% | 53.0% | Advanced |
| 3 | spark-chem13b-think | 26.05 | 0.92 | 23.30 | 9450 | 46.8% | 54.1% | Advanced |
| 4 | MOSES-nano | 25.42 | 0.90 | 22.72 | 9450 | 56.6% | 68.8% | Advanced |
| 5 | o3 | 22.47 | 0.95 | 19.61 | 9450 | 83.8% | 53.4% | Intermediate |
| 6 | gpt-4.1-nano | 21.95 | 0.91 | 19.21 | 9450 | 54.8% | 54.5% | Intermediate |
| 7 | gpt-4o-mini | 21.26 | 0.93 | 18.47 | 9450 | 41.5% | 51.1% | Intermediate |
| 8 | gpt-4.1 | 21.09 | 0.91 | 18.35 | 9450 | 71.0% | 55.6% | Intermediate |
| 9 | lightrag-4.1-nano | 20.24 | 0.95 | 17.40 | 9450 | 62.5% | 65.8% | Intermediate |
| 10 | lightrag-4.1 | 17.78 | 0.99 | 14.81 | 9450 | 58.6% | 53.6% | Novice |
| 11 | gpt-4o | 17.23 | 0.99 | 14.25 | 9450 | 50.2% | 67.7% | Novice |
| 12 | o1 | 14.44 | 1.12 | 11.09 | 9450 | 57.7% | 98.8% | Novice |
| 13 | llasmol-top1 | 0.75 | 0.94 | -2.08 | 9450 | 10.2% | 50.2% | Beginner |
| 14 | llasmol-top5 | 0.73 | 0.94 | -2.09 | 9450 | 9.3% | 50.9% | Beginner |
| 15 | darwin | 0.58 | 1.29 | -3.29 | 9450 | 8.5% | N/A | Beginner |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 29.97 | 0.92 | 27.21 | 9450 | 87.0% | 57.2% | Expert |
| 2 | spark-chem13b-nothink | 28.87 | 0.93 | 26.08 | 9450 | 48.7% | 56.7% | Expert |
| 3 | MOSES-nano | 27.86 | 0.90 | 25.17 | 9450 | 58.0% | 71.6% | Expert |
| 4 | spark-chem13b-think | 24.42 | 0.90 | 21.70 | 9450 | 47.4% | 57.5% | Advanced |
| 5 | o3 | 23.27 | 0.93 | 20.49 | 9450 | 83.6% | 51.7% | Advanced |
| 6 | gpt-4.1-nano | 23.01 | 0.88 | 20.36 | 9450 | 57.9% | 69.2% | Advanced |
| 7 | lightrag-4.1-nano | 19.99 | 0.93 | 17.21 | 9450 | 57.0% | 51.7% | Intermediate |
| 8 | gpt-4.1 | 19.73 | 0.89 | 17.06 | 9450 | 68.8% | 52.6% | Intermediate |
| 9 | o1 | 19.34 | 0.98 | 16.42 | 9450 | 67.0% | 62.9% | Intermediate |
| 10 | lightrag-4.1 | 17.35 | 0.96 | 14.47 | 9450 | 53.3% | 55.9% | Novice |
| 11 | gpt-4o-mini | 16.45 | 0.97 | 13.54 | 9450 | 37.3% | 65.9% | Novice |
| 12 | gpt-4o | 13.97 | 1.03 | 10.89 | 9450 | 48.0% | 98.7% | Novice |
| 13 | llasmol-top5 | 0.55 | 0.99 | -2.43 | 9450 | 15.1% | 56.6% | Beginner |
| 14 | llasmol-top1 | -0.45 | 0.98 | -3.40 | 9450 | 12.7% | 44.4% | Beginner |
| 15 | darwin | 0.41 | 1.33 | -3.58 | 9450 | 7.9% | N/A | Beginner |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 40.50 | 1.20 | 36.89 | 9450 | 90.6% | 78.2% | Elite |
| 2 | o3 | 35.72 | 1.20 | 32.12 | 9450 | 94.8% | 70.4% | Elite |
| 3 | MOSES-nano | 32.44 | 1.06 | 29.25 | 9450 | 56.5% | 68.8% | Expert |
| 4 | gpt-4.1 | 29.48 | 0.94 | 26.67 | 9450 | 71.9% | 60.0% | Expert |
| 5 | lightrag-4.1-nano | 27.95 | 0.97 | 25.04 | 9450 | 64.5% | 61.2% | Expert |
| 6 | gpt-4.1-nano | 26.23 | 0.93 | 23.43 | 9450 | 55.0% | 61.0% | Advanced |
| 7 | lightrag-4.1 | 24.55 | 0.94 | 21.72 | 9450 | 60.3% | 61.4% | Advanced |
| 8 | o1 | 22.81 | 0.96 | 19.93 | 9450 | 78.9% | 55.9% | Intermediate |
| 9 | spark-chem13b-nothink | 21.90 | 0.98 | 18.95 | 9450 | 40.7% | 61.9% | Intermediate |
| 10 | spark-chem13b-think | 20.07 | 1.00 | 17.08 | 9450 | 41.8% | 64.7% | Intermediate |
| 11 | gpt-4o | 17.79 | 1.02 | 14.72 | 9450 | 40.8% | 55.8% | Novice |
| 12 | gpt-4o-mini | 16.90 | 1.05 | 13.75 | 9450 | 31.2% | 99.3% | Novice |
| 13 | darwin | 1.77 | 1.34 | -2.25 | 9450 | 7.7% | 60.5% | Beginner |
| 14 | llasmol-top5 | 0.14 | 1.02 | -2.91 | 9450 | 8.2% | 54.7% | Beginner |
| 15 | llasmol-top1 | -0.58 | 1.02 | -3.63 | 9450 | 7.1% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 49.99 | 1.45 | 45.65 | 9450 | 96.0% | 93.2% | Elite |
| 2 | o3 | 40.75 | 1.26 | 36.97 | 9450 | 73.5% | 81.4% | Elite |
| 3 | MOSES-nano | 35.28 | 1.10 | 31.99 | 9450 | 72.4% | 54.6% | Elite |
| 4 | lightrag-4.1-nano | 34.57 | 1.11 | 31.23 | 9450 | 73.6% | 61.3% | Elite |
| 5 | gpt-4.1 | 32.82 | 1.00 | 29.83 | 9450 | 55.3% | 60.3% | Expert |
| 6 | gpt-4.1-nano | 31.24 | 1.00 | 28.24 | 9450 | 52.3% | 52.3% | Expert |
| 7 | lightrag-4.1 | 30.90 | 1.04 | 27.77 | 9450 | 74.0% | 67.3% | Expert |
| 8 | gpt-4o | 28.18 | 0.97 | 25.26 | 9450 | 40.6% | 54.3% | Expert |
| 9 | o1 | 27.53 | 1.02 | 24.47 | 9450 | 64.8% | 57.2% | Advanced |
| 10 | gpt-4o-mini | 26.43 | 0.96 | 23.55 | 9450 | 33.9% | 66.5% | Advanced |
| 11 | spark-chem13b-nothink | 23.86 | 0.97 | 20.95 | 9450 | 43.6% | 69.0% | Advanced |
| 12 | spark-chem13b-think | 20.85 | 1.02 | 17.78 | 9450 | 46.2% | 97.1% | Intermediate |
| 13 | darwin | 9.29 | 1.18 | 5.76 | 9450 | 7.4% | 55.4% | Beginner |
| 14 | llasmol-top5 | 8.48 | 0.93 | 5.68 | 9450 | 8.2% | 50.2% | Beginner |
| 15 | llasmol-top1 | 8.45 | 0.93 | 5.65 | 9450 | 8.3% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **34.17**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.93

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Theoretical Depth | MOSES | 45.65 | 49.99 | 1.45 | 8.67 |
| Completeness | MOSES | 26.94 | 29.72 | 0.93 | 3.15 |
| Correctness | MOSES | 27.21 | 29.97 | 0.92 | 1.13 |
| Rigor And Information Density | MOSES | 36.89 | 40.50 | 1.20 | 4.77 |

### Rating Distribution
- **Mean Overall ELO**: 17.92
- **ELO Std**: 10.28
- **ELO Range**: 34.17 - -0.86
- **Mean μ (Skill)**: 20.95
- **Mean σ (Uncertainty)**: 1.01
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 283,500
- **Matches per Dimension**: 70,875

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

