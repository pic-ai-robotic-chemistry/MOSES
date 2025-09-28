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

- **Total matches analyzed**: 283,500
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Analysis duration**: 58.9s

## TrueSkill Model Rankings - Overall ELO (Joint Modeling)

**Overall ELO calculated using joint modeling**: All dimension matches combined into single TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 36.03 | 39.64 | 1.20 | 37800 | 90.9% | 91.2% | Elite |
| 2 | o3 | 28.53 | 31.39 | 0.95 | 37800 | 84.0% | 53.1% | Expert |
| 3 | lightrag-4.1-nano | 28.12 | 30.91 | 0.93 | 37800 | 64.5% | 60.4% | Expert |
| 4 | o1 | 26.54 | 29.32 | 0.93 | 37800 | 67.0% | 51.2% | Expert |
| 5 | MOSES-nano | 26.38 | 29.14 | 0.92 | 37800 | 60.9% | 55.6% | Expert |
| 6 | lightrag-4.1 | 25.53 | 28.28 | 0.92 | 37800 | 61.5% | 65.6% | Expert |
| 7 | spark-chem13b-think | 23.07 | 25.85 | 0.93 | 37800 | 45.6% | 53.5% | Advanced |
| 8 | spark-chem13b-nothink | 22.54 | 25.33 | 0.93 | 37800 | 45.4% | 66.2% | Advanced |
| 9 | gpt-4.1 | 20.03 | 22.81 | 0.92 | 37800 | 66.7% | 52.2% | Advanced |
| 10 | gpt-4.1-nano | 19.65 | 22.47 | 0.94 | 37800 | 54.9% | 59.9% | Intermediate |
| 11 | gpt-4o | 18.11 | 20.94 | 0.95 | 37800 | 45.0% | 67.4% | Intermediate |
| 12 | gpt-4o-mini | 15.19 | 18.22 | 1.01 | 37800 | 36.0% | 92.3% | Intermediate |
| 13 | llasmol-top5 | 6.35 | 9.55 | 1.07 | 37800 | 10.1% | 68.7% | Beginner |
| 14 | llasmol-top1 | 3.34 | 6.59 | 1.08 | 37800 | 9.6% | 47.0% | Beginner |
| 15 | darwin | 2.99 | 7.05 | 1.35 | 37800 | 7.9% | N/A | Beginner |

## Detailed Dimension Analysis (Separate Modeling)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 43.05 | 1.25 | 39.30 | 9450 | 83.8% | 89.5% | Elite |
| 2 | MOSES | 35.41 | 1.01 | 32.37 | 9450 | 90.1% | 64.0% | Elite |
| 3 | spark-chem13b-nothink | 33.24 | 0.96 | 30.37 | 9450 | 48.2% | 75.5% | Elite |
| 4 | o1 | 29.06 | 0.95 | 26.23 | 9450 | 57.5% | 52.4% | Expert |
| 5 | spark-chem13b-think | 28.71 | 0.98 | 25.77 | 9450 | 47.0% | 59.7% | Expert |
| 6 | lightrag-4.1 | 27.23 | 0.93 | 24.44 | 9450 | 58.5% | 52.4% | Advanced |
| 7 | lightrag-4.1-nano | 26.86 | 0.93 | 24.07 | 9450 | 62.5% | 57.0% | Advanced |
| 8 | MOSES-nano | 25.80 | 0.97 | 22.90 | 9450 | 56.7% | 66.4% | Advanced |
| 9 | gpt-4.1-nano | 23.25 | 0.92 | 20.48 | 9450 | 54.6% | 51.9% | Advanced |
| 10 | gpt-4.1 | 22.95 | 0.92 | 20.20 | 9450 | 70.9% | 70.3% | Advanced |
| 11 | gpt-4o | 19.74 | 0.96 | 16.87 | 9450 | 50.3% | 57.8% | Intermediate |
| 12 | gpt-4o-mini | 18.55 | 0.99 | 15.56 | 9450 | 41.7% | 96.0% | Intermediate |
| 13 | llasmol-top5 | 7.93 | 1.07 | 4.71 | 9450 | 9.2% | 55.3% | Beginner |
| 14 | llasmol-top1 | 7.12 | 1.08 | 3.89 | 9450 | 10.3% | 51.2% | Beginner |
| 15 | darwin | 6.93 | 1.37 | 2.81 | 9450 | 8.6% | N/A | Beginner |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 40.68 | 1.08 | 37.44 | 9450 | 83.7% | 81.6% | Elite |
| 2 | MOSES | 35.23 | 0.93 | 32.44 | 9450 | 86.9% | 63.8% | Elite |
| 3 | spark-chem13b-nothink | 33.09 | 0.92 | 30.32 | 9450 | 48.9% | 55.8% | Elite |
| 4 | spark-chem13b-think | 32.22 | 0.93 | 29.44 | 9450 | 47.4% | 57.9% | Expert |
| 5 | o1 | 31.01 | 0.92 | 28.24 | 9450 | 67.0% | 54.3% | Expert |
| 6 | MOSES-nano | 30.36 | 0.92 | 27.59 | 9450 | 57.9% | 63.7% | Expert |
| 7 | lightrag-4.1 | 28.24 | 0.92 | 25.47 | 9450 | 53.5% | 54.3% | Expert |
| 8 | gpt-4.1-nano | 27.59 | 0.91 | 24.85 | 9450 | 57.8% | 51.6% | Advanced |
| 9 | gpt-4o | 27.35 | 0.92 | 24.59 | 9450 | 48.1% | 56.0% | Advanced |
| 10 | lightrag-4.1-nano | 26.44 | 0.95 | 23.60 | 9450 | 57.1% | 68.6% | Advanced |
| 11 | gpt-4.1 | 23.52 | 0.91 | 20.80 | 9450 | 68.8% | 70.1% | Advanced |
| 12 | gpt-4o-mini | 20.33 | 1.02 | 17.26 | 9450 | 37.3% | 89.2% | Intermediate |
| 13 | llasmol-top5 | 12.81 | 1.13 | 9.44 | 9450 | 15.1% | 72.9% | Beginner |
| 14 | llasmol-top1 | 9.09 | 1.09 | 5.83 | 9450 | 12.6% | 59.1% | Beginner |
| 15 | darwin | 7.67 | 1.40 | 3.46 | 9450 | 7.9% | N/A | Beginner |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 46.11 | 1.45 | 41.77 | 9450 | 94.8% | 88.5% | Elite |
| 2 | MOSES | 38.71 | 1.15 | 35.25 | 9450 | 90.5% | 71.0% | Elite |
| 3 | o1 | 35.32 | 1.17 | 31.82 | 9450 | 78.7% | 67.1% | Elite |
| 4 | lightrag-4.1-nano | 32.63 | 1.07 | 29.44 | 9450 | 64.7% | 58.6% | Expert |
| 5 | lightrag-4.1 | 31.31 | 1.08 | 28.06 | 9450 | 60.2% | 51.8% | Expert |
| 6 | gpt-4.1 | 31.04 | 1.03 | 27.94 | 9450 | 71.8% | 67.0% | Expert |
| 7 | gpt-4.1-nano | 28.36 | 1.01 | 25.32 | 9450 | 55.0% | 74.6% | Expert |
| 8 | MOSES-nano | 24.34 | 0.98 | 21.40 | 9450 | 56.6% | 52.2% | Advanced |
| 9 | spark-chem13b-nothink | 24.01 | 1.05 | 20.87 | 9450 | 40.7% | 70.2% | Advanced |
| 10 | gpt-4o | 20.79 | 0.96 | 17.92 | 9450 | 40.9% | 50.3% | Intermediate |
| 11 | spark-chem13b-think | 20.75 | 1.06 | 17.57 | 9450 | 41.9% | 63.2% | Intermediate |
| 12 | gpt-4o-mini | 18.70 | 0.97 | 15.81 | 9450 | 31.2% | 95.5% | Intermediate |
| 13 | llasmol-top5 | 8.38 | 1.10 | 5.07 | 9450 | 8.2% | 73.3% | Beginner |
| 14 | llasmol-top1 | 4.59 | 1.12 | 1.22 | 9450 | 7.2% | 56.6% | Beginner |
| 15 | darwin | 3.56 | 1.39 | -0.59 | 9450 | 7.6% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 40.91 | 1.20 | 37.30 | 9450 | 96.0% | 91.2% | Elite |
| 2 | o3 | 32.66 | 0.95 | 29.80 | 9450 | 73.6% | 53.1% | Expert |
| 3 | lightrag-4.1-nano | 32.19 | 0.93 | 29.39 | 9450 | 73.6% | 60.4% | Expert |
| 4 | o1 | 30.60 | 0.93 | 27.81 | 9450 | 64.6% | 51.2% | Expert |
| 5 | MOSES-nano | 30.41 | 0.92 | 27.66 | 9450 | 72.3% | 55.6% | Expert |
| 6 | lightrag-4.1 | 29.56 | 0.92 | 26.80 | 9450 | 74.0% | 65.6% | Expert |
| 7 | spark-chem13b-think | 27.13 | 0.93 | 24.34 | 9450 | 46.3% | 53.5% | Advanced |
| 8 | spark-chem13b-nothink | 26.60 | 0.93 | 23.82 | 9450 | 43.6% | 66.2% | Advanced |
| 9 | gpt-4.1 | 24.08 | 0.92 | 21.30 | 9450 | 55.4% | 52.2% | Advanced |
| 10 | gpt-4.1-nano | 23.74 | 0.94 | 20.92 | 9450 | 52.3% | 59.9% | Advanced |
| 11 | gpt-4o | 22.22 | 0.95 | 19.38 | 9450 | 40.5% | 67.4% | Intermediate |
| 12 | gpt-4o-mini | 19.49 | 1.01 | 16.46 | 9450 | 33.9% | 92.3% | Intermediate |
| 13 | llasmol-top5 | 10.82 | 1.07 | 7.62 | 9450 | 7.9% | 68.7% | Beginner |
| 14 | llasmol-top1 | 7.86 | 1.08 | 4.61 | 9450 | 8.3% | 47.0% | Beginner |
| 15 | darwin | 8.32 | 1.35 | 4.27 | 9450 | 7.7% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **36.03**

### Most Consistent Model
**lightrag-4.1** shows the lowest uncertainty with σ=0.92

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Completeness | o3 | 39.30 | 43.05 | 1.25 | 6.93 |
| Rigor And Information Density | o3 | 41.77 | 46.11 | 1.45 | 6.51 |
| Correctness | o3 | 37.44 | 40.68 | 1.08 | 5.00 |
| Theoretical Depth | MOSES | 37.30 | 40.91 | 1.20 | 7.50 |

### Rating Distribution
- **Mean Overall ELO**: 20.16
- **ELO Std**: 9.33
- **ELO Range**: 36.03 - 2.99
- **Mean μ (Skill)**: 23.17
- **Mean σ (Uncertainty)**: 1.00
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 283,500
- **Matches per Dimension**: 70,875

### Method Details

**Overall ELO Calculation**:
- Uses joint modeling approach
- Combines all dimension matches into single TrueSkill calculation
- Provides unified ranking across all evaluation aspects

**Dimension ELO Calculations**:
- Each dimension calculated independently (pure separation)
- Allows comparison of model strengths across different aspects

**Data Aggregation Level**: llm_only
- LLM评分聚合: 5个LLM评分 → 平均值
- 回答轮次保留: 保持轮次间差异
- 每个问题-维度生成N个匹配（N=回答轮次数）

