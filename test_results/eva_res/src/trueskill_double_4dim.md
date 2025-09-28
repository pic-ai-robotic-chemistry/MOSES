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

- **Total matches analyzed**: 11,340
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: double)
- **Analysis duration**: 1.1s

## TrueSkill Model Rankings - Overall ELO (Dimension Averaging)

**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 34.21 | 37.60 | 1.13 | mean | 4 dimensions | 66.2% | Elite |
| 2 | o3 | 31.92 | 35.05 | 1.04 | mean | 4 dimensions | 82.9% | Elite |
| 3 | o1 | 26.55 | 29.29 | 0.91 | mean | 4 dimensions | 53.9% | Expert |
| 4 | gpt-4.1 | 25.99 | 28.70 | 0.90 | mean | 4 dimensions | 53.7% | Expert |
| 5 | lightrag-4.1-nano | 25.44 | 28.13 | 0.90 | mean | 4 dimensions | 60.5% | Expert |
| 6 | MOSES-nano | 23.87 | 26.53 | 0.89 | mean | 4 dimensions | 52.5% | Advanced |
| 7 | lightrag-4.1 | 23.48 | 26.16 | 0.89 | mean | 4 dimensions | 55.2% | Advanced |
| 8 | gpt-4.1-nano | 22.72 | 25.37 | 0.88 | mean | 4 dimensions | 65.0% | Advanced |
| 9 | spark-chem13b-think | 20.37 | 23.05 | 0.89 | mean | 4 dimensions | 52.1% | Advanced |
| 10 | spark-chem13b-nothink | 20.07 | 22.74 | 0.89 | mean | 4 dimensions | 56.6% | Advanced |
| 11 | gpt-4o | 19.02 | 21.73 | 0.90 | mean | 4 dimensions | 64.2% | Intermediate |
| 12 | gpt-4o-mini | 16.75 | 19.53 | 0.93 | mean | 4 dimensions | 92.9% | Intermediate |
| 13 | darwin | 7.31 | 10.64 | 1.11 | mean | 4 dimensions | 55.2% | Beginner |
| 14 | llasmol-top5 | 6.59 | 9.84 | 1.08 | mean | 4 dimensions | 53.1% | Beginner |
| 15 | llasmol-top1 | 6.09 | 9.37 | 1.09 | mean | 4 dimensions | N/A | Beginner |

## Detailed Dimension Analysis (Separate Modeling)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 35.90 | 1.08 | 32.66 | 378 | 93.4% | 74.3% | Elite |
| 2 | o3 | 31.95 | 0.96 | 29.08 | 378 | 86.0% | 75.5% | Expert |
| 3 | gpt-4.1 | 27.79 | 0.87 | 25.19 | 378 | 72.1% | 60.4% | Expert |
| 4 | lightrag-4.1-nano | 26.20 | 0.87 | 23.60 | 378 | 63.0% | 51.3% | Advanced |
| 5 | o1 | 26.01 | 0.86 | 23.43 | 378 | 58.1% | 57.5% | Advanced |
| 6 | gpt-4.1-nano | 24.87 | 0.86 | 22.29 | 378 | 54.8% | 51.4% | Advanced |
| 7 | MOSES-nano | 24.66 | 0.86 | 22.08 | 378 | 53.2% | 51.2% | Advanced |
| 8 | lightrag-4.1 | 24.48 | 0.86 | 21.90 | 378 | 59.5% | 55.9% | Advanced |
| 9 | spark-chem13b-nothink | 23.58 | 0.86 | 21.01 | 378 | 49.1% | 51.9% | Advanced |
| 10 | spark-chem13b-think | 23.29 | 0.86 | 20.70 | 378 | 47.0% | 56.1% | Advanced |
| 11 | gpt-4o | 22.36 | 0.87 | 19.76 | 378 | 49.2% | 58.9% | Intermediate |
| 12 | gpt-4o-mini | 21.01 | 0.88 | 18.37 | 378 | 39.6% | 95.8% | Intermediate |
| 13 | darwin | 10.55 | 1.08 | 7.30 | 378 | 8.3% | 51.6% | Beginner |
| 14 | llasmol-top1 | 10.30 | 1.07 | 7.10 | 378 | 8.7% | 51.8% | Beginner |
| 15 | llasmol-top5 | 10.03 | 1.07 | 6.80 | 378 | 8.2% | N/A | Beginner |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 33.25 | 0.99 | 30.28 | 378 | 90.1% | 64.4% | Elite |
| 2 | o3 | 31.02 | 0.94 | 28.19 | 378 | 89.4% | 76.0% | Expert |
| 3 | gpt-4.1 | 26.77 | 0.85 | 24.21 | 378 | 71.2% | 53.6% | Advanced |
| 4 | o1 | 26.24 | 0.86 | 23.66 | 378 | 68.1% | 57.9% | Advanced |
| 5 | lightrag-4.1-nano | 25.04 | 0.85 | 22.49 | 378 | 58.3% | 50.5% | Advanced |
| 6 | gpt-4.1-nano | 24.97 | 0.84 | 22.46 | 378 | 57.1% | 54.0% | Advanced |
| 7 | MOSES-nano | 24.38 | 0.84 | 21.84 | 378 | 50.4% | 57.3% | Advanced |
| 8 | spark-chem13b-nothink | 23.27 | 0.84 | 20.76 | 378 | 46.7% | 51.0% | Advanced |
| 9 | spark-chem13b-think | 23.11 | 0.84 | 20.58 | 378 | 46.8% | 55.0% | Advanced |
| 10 | lightrag-4.1 | 22.35 | 0.85 | 19.81 | 378 | 52.5% | 54.6% | Intermediate |
| 11 | gpt-4o | 21.66 | 0.85 | 19.12 | 378 | 47.9% | 60.8% | Intermediate |
| 12 | gpt-4o-mini | 20.02 | 0.86 | 17.44 | 378 | 37.6% | 86.4% | Intermediate |
| 13 | llasmol-top5 | 13.39 | 0.96 | 10.51 | 378 | 13.1% | 55.1% | Novice |
| 14 | darwin | 12.61 | 1.02 | 9.54 | 378 | 9.0% | 52.2% | Beginner |
| 15 | llasmol-top1 | 12.28 | 0.99 | 9.31 | 378 | 11.8% | N/A | Beginner |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 43.70 | 1.32 | 39.72 | 378 | 96.6% | 71.5% | Elite |
| 2 | MOSES | 40.21 | 1.14 | 36.79 | 378 | 92.9% | 82.7% | Elite |
| 3 | o1 | 34.48 | 1.02 | 31.42 | 378 | 81.6% | 61.0% | Elite |
| 4 | gpt-4.1 | 32.79 | 0.99 | 29.81 | 378 | 73.8% | 68.1% | Expert |
| 5 | lightrag-4.1-nano | 29.94 | 0.95 | 27.09 | 378 | 67.6% | 68.0% | Expert |
| 6 | lightrag-4.1 | 27.12 | 0.93 | 24.32 | 378 | 60.3% | 51.0% | Advanced |
| 7 | MOSES-nano | 26.97 | 0.93 | 24.18 | 378 | 53.6% | 54.4% | Advanced |
| 8 | gpt-4.1-nano | 26.31 | 0.93 | 23.53 | 378 | 54.2% | 73.6% | Advanced |
| 9 | spark-chem13b-think | 22.51 | 0.95 | 19.66 | 378 | 39.4% | 52.6% | Intermediate |
| 10 | spark-chem13b-nothink | 22.12 | 0.94 | 19.29 | 378 | 38.9% | 53.9% | Intermediate |
| 11 | gpt-4o | 21.53 | 0.95 | 18.67 | 378 | 39.6% | 71.6% | Intermediate |
| 12 | gpt-4o-mini | 18.08 | 1.00 | 15.08 | 378 | 28.8% | 91.5% | Intermediate |
| 13 | darwin | 9.72 | 1.18 | 6.17 | 378 | 9.9% | 64.0% | Beginner |
| 14 | llasmol-top5 | 7.52 | 1.17 | 4.02 | 378 | 7.4% | 56.0% | Beginner |
| 15 | llasmol-top1 | 6.60 | 1.19 | 3.03 | 378 | 5.4% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 41.05 | 1.31 | 37.13 | 378 | 97.6% | 89.1% | Elite |
| 2 | o3 | 33.54 | 0.95 | 30.70 | 378 | 75.8% | 64.1% | Elite |
| 3 | lightrag-4.1-nano | 31.35 | 0.93 | 28.57 | 378 | 75.9% | 54.3% | Expert |
| 4 | lightrag-4.1 | 30.70 | 0.93 | 27.91 | 378 | 77.2% | 51.8% | Expert |
| 5 | o1 | 30.44 | 0.91 | 27.70 | 378 | 66.4% | 52.1% | Expert |
| 6 | MOSES-nano | 30.12 | 0.92 | 27.37 | 378 | 74.9% | 67.1% | Expert |
| 7 | gpt-4.1 | 27.45 | 0.90 | 24.76 | 378 | 56.2% | 63.8% | Advanced |
| 8 | gpt-4.1-nano | 25.33 | 0.91 | 22.60 | 378 | 51.1% | 63.3% | Advanced |
| 9 | spark-chem13b-think | 23.29 | 0.92 | 20.54 | 378 | 41.7% | 58.6% | Advanced |
| 10 | spark-chem13b-nothink | 21.98 | 0.92 | 19.23 | 378 | 40.1% | 54.0% | Intermediate |
| 11 | gpt-4o | 21.37 | 0.95 | 18.53 | 378 | 39.3% | 65.1% | Intermediate |
| 12 | gpt-4o-mini | 19.03 | 0.98 | 16.09 | 378 | 31.0% | 93.8% | Intermediate |
| 13 | darwin | 9.68 | 1.15 | 6.22 | 378 | 8.1% | 58.2% | Beginner |
| 14 | llasmol-top5 | 8.42 | 1.13 | 5.04 | 378 | 7.7% | 50.8% | Beginner |
| 15 | llasmol-top1 | 8.29 | 1.13 | 4.91 | 378 | 7.1% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **34.21**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.88

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Correctness | MOSES | 30.28 | 33.25 | 0.99 | 2.08 |
| Rigor And Information Density | o3 | 39.72 | 43.70 | 1.32 | 2.93 |
| Completeness | MOSES | 32.66 | 35.90 | 1.08 | 3.58 |
| Theoretical Depth | MOSES | 37.13 | 41.05 | 1.31 | 6.43 |

### Rating Distribution
- **Mean Overall ELO**: 20.69
- **ELO Std**: 8.27
- **ELO Range**: 34.21 - 6.09
- **Mean μ (Skill)**: 23.58
- **Mean σ (Uncertainty)**: 0.96
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 11,340
- **Matches per Dimension**: 2,835

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

