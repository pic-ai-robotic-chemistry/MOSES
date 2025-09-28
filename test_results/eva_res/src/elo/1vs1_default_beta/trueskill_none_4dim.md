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
- **Match generation**: Real question-dimension matches (aggregation: none)
- **Analysis duration**: 59.3s

## TrueSkill Model Rankings - Overall ELO (Joint Modeling)

**Overall ELO calculated using joint modeling**: All dimension matches combined into single TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 35.18 | 38.68 | 1.16 | 37800 | 88.8% | 86.2% | Elite |
| 2 | o3 | 29.22 | 32.05 | 0.94 | 37800 | 81.8% | 69.8% | Expert |
| 3 | lightrag-4.1 | 26.21 | 28.92 | 0.90 | 37800 | 61.1% | 50.7% | Expert |
| 4 | MOSES-nano | 26.09 | 28.81 | 0.91 | 37800 | 60.2% | 52.4% | Expert |
| 5 | o1 | 25.71 | 28.44 | 0.91 | 37800 | 66.0% | 50.2% | Expert |
| 6 | lightrag-4.1-nano | 25.71 | 28.41 | 0.90 | 37800 | 63.8% | 56.1% | Expert |
| 7 | spark-chem13b-think | 24.72 | 27.48 | 0.92 | 37800 | 46.8% | 58.7% | Advanced |
| 8 | spark-chem13b-nothink | 23.42 | 26.15 | 0.91 | 37800 | 45.5% | 55.2% | Advanced |
| 9 | gpt-4.1 | 22.68 | 25.36 | 0.89 | 37800 | 65.9% | 53.7% | Advanced |
| 10 | gpt-4.1-nano | 22.11 | 24.80 | 0.90 | 37800 | 55.7% | 51.5% | Advanced |
| 11 | gpt-4o | 21.85 | 24.57 | 0.91 | 37800 | 47.0% | 70.7% | Advanced |
| 12 | gpt-4o-mini | 18.49 | 21.28 | 0.93 | 37800 | 37.7% | 93.6% | Intermediate |
| 13 | llasmol-top5 | 8.90 | 12.04 | 1.05 | 37800 | 10.7% | 62.1% | Beginner |
| 14 | darwin | 6.20 | 10.15 | 1.31 | 37800 | 8.5% | 55.9% | Beginner |
| 15 | llasmol-top1 | 6.03 | 9.23 | 1.07 | 37800 | 10.3% | N/A | Beginner |

## Detailed Dimension Analysis (Separate Modeling)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 40.04 | 1.12 | 36.69 | 9450 | 82.2% | 84.4% | Elite |
| 2 | MOSES | 33.90 | 0.94 | 31.07 | 9450 | 88.6% | 64.0% | Elite |
| 3 | spark-chem13b-nothink | 31.74 | 0.93 | 28.95 | 9450 | 47.4% | 66.9% | Expert |
| 4 | o1 | 29.09 | 0.92 | 26.32 | 9450 | 57.7% | 52.9% | Expert |
| 5 | spark-chem13b-think | 28.65 | 0.95 | 25.81 | 9450 | 47.8% | 52.2% | Expert |
| 6 | lightrag-4.1 | 28.33 | 0.91 | 25.59 | 9450 | 58.4% | 54.3% | Expert |
| 7 | lightrag-4.1-nano | 27.68 | 0.92 | 24.93 | 9450 | 62.7% | 55.6% | Advanced |
| 8 | MOSES-nano | 26.83 | 0.94 | 24.02 | 9450 | 56.1% | 51.7% | Advanced |
| 9 | gpt-4.1-nano | 26.58 | 0.92 | 23.83 | 9450 | 55.3% | 58.9% | Advanced |
| 10 | gpt-4.1 | 25.22 | 0.90 | 22.53 | 9450 | 69.8% | 63.8% | Advanced |
| 11 | gpt-4o | 23.08 | 0.92 | 20.32 | 9450 | 50.9% | 59.7% | Advanced |
| 12 | gpt-4o-mini | 21.60 | 0.95 | 18.75 | 9450 | 42.1% | 95.4% | Intermediate |
| 13 | llasmol-top1 | 11.38 | 1.07 | 8.17 | 9450 | 11.2% | 54.4% | Beginner |
| 14 | llasmol-top5 | 10.71 | 1.07 | 7.51 | 9450 | 10.4% | 52.8% | Beginner |
| 15 | darwin | 10.27 | 1.33 | 6.27 | 9450 | 9.6% | N/A | Beginner |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 37.91 | 0.98 | 34.99 | 9450 | 81.2% | 75.7% | Elite |
| 2 | spark-chem13b-nothink | 33.71 | 0.91 | 30.97 | 9450 | 48.3% | 55.1% | Elite |
| 3 | MOSES | 32.94 | 0.91 | 30.21 | 9450 | 84.0% | 61.7% | Elite |
| 4 | spark-chem13b-think | 31.15 | 0.92 | 28.40 | 9450 | 48.4% | 55.7% | Expert |
| 5 | lightrag-4.1 | 30.29 | 0.90 | 27.58 | 9450 | 54.2% | 54.2% | Expert |
| 6 | MOSES-nano | 29.65 | 0.90 | 26.94 | 9450 | 58.0% | 49.9% | Expert |
| 7 | o1 | 29.67 | 0.91 | 26.93 | 9450 | 66.4% | 54.8% | Expert |
| 8 | gpt-4.1-nano | 28.93 | 0.90 | 26.23 | 9450 | 58.4% | 53.4% | Expert |
| 9 | gpt-4o | 28.42 | 0.90 | 25.72 | 9450 | 49.3% | 56.7% | Expert |
| 10 | lightrag-4.1-nano | 27.40 | 0.92 | 24.65 | 9450 | 58.0% | 66.5% | Advanced |
| 11 | gpt-4.1 | 24.83 | 0.89 | 22.16 | 9450 | 68.4% | 56.9% | Advanced |
| 12 | gpt-4o-mini | 23.78 | 0.94 | 20.95 | 9450 | 38.2% | 92.6% | Advanced |
| 13 | llasmol-top5 | 14.98 | 1.08 | 11.74 | 9450 | 15.4% | 73.3% | Novice |
| 14 | llasmol-top1 | 11.20 | 1.08 | 7.96 | 9450 | 12.8% | 45.9% | Beginner |
| 15 | darwin | 11.84 | 1.36 | 7.76 | 9450 | 9.1% | N/A | Beginner |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 37.65 | 1.15 | 34.19 | 9450 | 91.7% | 73.3% | Elite |
| 2 | MOSES | 33.87 | 1.02 | 30.81 | 9450 | 87.8% | 51.6% | Elite |
| 3 | o1 | 33.62 | 1.04 | 30.49 | 9450 | 76.4% | 65.6% | Elite |
| 4 | lightrag-4.1-nano | 31.18 | 1.00 | 28.19 | 9450 | 63.8% | 51.0% | Expert |
| 5 | gpt-4.1 | 31.02 | 0.99 | 28.04 | 9450 | 70.8% | 50.3% | Expert |
| 6 | lightrag-4.1 | 30.97 | 1.01 | 27.94 | 9450 | 60.5% | 67.5% | Expert |
| 7 | gpt-4.1-nano | 28.22 | 0.96 | 25.33 | 9450 | 56.4% | 71.3% | Expert |
| 8 | MOSES-nano | 24.82 | 0.94 | 22.01 | 9450 | 56.5% | 50.0% | Advanced |
| 9 | spark-chem13b-nothink | 24.83 | 0.99 | 21.86 | 9450 | 41.8% | 66.4% | Advanced |
| 10 | gpt-4o | 22.26 | 0.93 | 19.47 | 9450 | 43.7% | 53.6% | Intermediate |
| 11 | spark-chem13b-think | 21.71 | 1.00 | 18.71 | 9450 | 43.4% | 54.2% | Intermediate |
| 12 | gpt-4o-mini | 21.07 | 0.94 | 18.25 | 9450 | 33.6% | 97.1% | Intermediate |
| 13 | llasmol-top5 | 9.58 | 1.05 | 6.42 | 9450 | 8.1% | 64.3% | Beginner |
| 14 | darwin | 7.33 | 1.32 | 3.35 | 9450 | 7.6% | 63.4% | Beginner |
| 15 | llasmol-top1 | 5.22 | 1.13 | 1.83 | 9450 | 8.0% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 38.22 | 1.16 | 34.72 | 9450 | 95.0% | 86.2% | Elite |
| 2 | o3 | 31.58 | 0.94 | 28.76 | 9450 | 72.3% | 69.8% | Expert |
| 3 | lightrag-4.1 | 28.46 | 0.90 | 25.75 | 9450 | 71.4% | 50.7% | Expert |
| 4 | MOSES-nano | 28.35 | 0.91 | 25.63 | 9450 | 70.2% | 52.4% | Expert |
| 5 | o1 | 27.98 | 0.91 | 25.25 | 9450 | 63.7% | 50.2% | Expert |
| 6 | lightrag-4.1-nano | 27.94 | 0.90 | 25.24 | 9450 | 70.8% | 56.1% | Expert |
| 7 | spark-chem13b-think | 27.02 | 0.92 | 24.26 | 9450 | 47.5% | 58.7% | Advanced |
| 8 | spark-chem13b-nothink | 25.68 | 0.91 | 22.96 | 9450 | 44.6% | 55.2% | Advanced |
| 9 | gpt-4.1 | 24.90 | 0.89 | 22.22 | 9450 | 54.6% | 53.7% | Advanced |
| 10 | gpt-4.1-nano | 24.34 | 0.90 | 21.65 | 9450 | 52.9% | 51.5% | Advanced |
| 11 | gpt-4o | 24.11 | 0.91 | 21.38 | 9450 | 44.0% | 70.7% | Advanced |
| 12 | gpt-4o-mini | 20.82 | 0.93 | 18.03 | 9450 | 37.1% | 93.6% | Intermediate |
| 13 | llasmol-top5 | 11.58 | 1.05 | 8.44 | 9450 | 9.0% | 62.1% | Beginner |
| 14 | darwin | 9.68 | 1.31 | 5.74 | 9450 | 7.6% | 55.9% | Beginner |
| 15 | llasmol-top1 | 8.77 | 1.07 | 5.57 | 9450 | 9.3% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **35.18**

### Most Consistent Model
**gpt-4.1** shows the lowest uncertainty with σ=0.89

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Completeness | o3 | 36.69 | 40.04 | 1.12 | 5.62 |
| Rigor And Information Density | o3 | 34.19 | 37.65 | 1.15 | 3.38 |
| Correctness | o3 | 34.99 | 37.91 | 0.98 | 4.02 |
| Theoretical Depth | MOSES | 34.72 | 38.22 | 1.16 | 5.96 |

### Rating Distribution
- **Mean Overall ELO**: 21.50
- **ELO Std**: 8.09
- **ELO Range**: 35.18 - 6.03
- **Mean μ (Skill)**: 24.42
- **Mean σ (Uncertainty)**: 0.97
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

**Data Aggregation Level**: none
- 无聚合: 保留所有原始评分
- 每个问题-维度生成N×5个匹配（N=回答轮次数）

