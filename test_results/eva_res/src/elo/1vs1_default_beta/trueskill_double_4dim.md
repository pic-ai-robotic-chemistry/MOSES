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
- **Analysis duration**: 2.3s

## TrueSkill Model Rankings - Overall ELO (Joint Modeling)

**Overall ELO calculated using joint modeling**: All dimension matches combined into single TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 36.41 | 39.96 | 1.18 | 1512 | 93.7% | 90.7% | Elite |
| 2 | MOSES-nano | 29.15 | 31.93 | 0.92 | 1512 | 58.0% | 51.4% | Expert |
| 3 | o3 | 29.01 | 31.72 | 0.91 | 1512 | 86.7% | 55.4% | Expert |
| 4 | lightrag-4.1 | 28.16 | 30.91 | 0.92 | 1512 | 62.4% | 50.2% | Expert |
| 5 | lightrag-4.1-nano | 28.16 | 30.87 | 0.90 | 1512 | 66.0% | 61.5% | Expert |
| 6 | o1 | 26.44 | 29.12 | 0.89 | 1512 | 68.7% | 68.2% | Expert |
| 7 | gpt-4.1 | 23.62 | 26.26 | 0.88 | 1512 | 68.1% | 56.5% | Advanced |
| 8 | gpt-4.1-nano | 22.62 | 25.27 | 0.88 | 1512 | 54.2% | 67.1% | Advanced |
| 9 | spark-chem13b-think | 19.95 | 22.61 | 0.89 | 1512 | 43.6% | 50.6% | Intermediate |
| 10 | spark-chem13b-nothink | 19.86 | 22.52 | 0.89 | 1512 | 43.8% | 53.4% | Intermediate |
| 11 | gpt-4o | 19.29 | 22.00 | 0.90 | 1512 | 44.0% | 60.7% | Intermediate |
| 12 | gpt-4o-mini | 17.60 | 20.37 | 0.92 | 1512 | 34.3% | 88.9% | Intermediate |
| 13 | llasmol-top5 | 9.71 | 12.96 | 1.08 | 1512 | 8.9% | 52.4% | Beginner |
| 14 | darwin | 9.35 | 12.60 | 1.08 | 1512 | 9.1% | 57.7% | Beginner |
| 15 | llasmol-top1 | 8.16 | 11.42 | 1.09 | 1512 | 8.5% | N/A | Beginner |

## Detailed Dimension Analysis (Separate Modeling)

**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 37.24 | 1.08 | 34.00 | 378 | 93.4% | 64.4% | Elite |
| 2 | o3 | 35.00 | 0.96 | 32.12 | 378 | 86.0% | 82.6% | Elite |
| 3 | gpt-4.1 | 29.33 | 0.88 | 26.69 | 378 | 71.7% | 52.7% | Expert |
| 4 | o1 | 28.92 | 0.87 | 26.30 | 378 | 58.2% | 53.7% | Expert |
| 5 | lightrag-4.1-nano | 28.35 | 0.87 | 25.75 | 378 | 63.0% | 55.4% | Expert |
| 6 | lightrag-4.1 | 27.53 | 0.86 | 24.94 | 378 | 59.5% | 59.2% | Advanced |
| 7 | MOSES-nano | 26.13 | 0.87 | 23.52 | 378 | 53.2% | 51.6% | Advanced |
| 8 | gpt-4.1-nano | 25.89 | 0.87 | 23.30 | 378 | 55.0% | 58.0% | Advanced |
| 9 | spark-chem13b-nothink | 24.67 | 0.86 | 22.10 | 378 | 48.9% | 50.0% | Advanced |
| 10 | gpt-4o | 24.67 | 0.87 | 22.06 | 378 | 49.2% | 50.9% | Advanced |
| 11 | spark-chem13b-think | 24.53 | 0.86 | 21.95 | 378 | 47.1% | 65.4% | Advanced |
| 12 | gpt-4o-mini | 22.14 | 0.90 | 19.45 | 378 | 39.7% | 94.8% | Intermediate |
| 13 | llasmol-top5 | 12.25 | 1.16 | 8.77 | 378 | 7.9% | 52.4% | Beginner |
| 14 | llasmol-top1 | 11.88 | 1.15 | 8.43 | 378 | 8.5% | 51.0% | Beginner |
| 15 | darwin | 11.73 | 1.15 | 8.29 | 378 | 8.7% | N/A | Beginner |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 36.18 | 0.99 | 33.22 | 378 | 88.9% | 51.3% | Elite |
| 2 | MOSES | 35.98 | 1.00 | 32.98 | 378 | 90.5% | 81.7% | Elite |
| 3 | o1 | 30.52 | 0.87 | 27.90 | 378 | 68.3% | 55.2% | Expert |
| 4 | gpt-4.1 | 29.74 | 0.86 | 27.15 | 378 | 70.6% | 65.1% | Expert |
| 5 | gpt-4.1-nano | 27.41 | 0.85 | 24.87 | 378 | 56.9% | 52.2% | Advanced |
| 6 | lightrag-4.1-nano | 27.09 | 0.85 | 24.53 | 378 | 57.9% | 55.5% | Advanced |
| 7 | gpt-4o | 26.26 | 0.85 | 23.72 | 378 | 47.6% | 50.3% | Advanced |
| 8 | MOSES-nano | 26.21 | 0.85 | 23.65 | 378 | 50.3% | 52.9% | Advanced |
| 9 | lightrag-4.1 | 25.76 | 0.85 | 23.22 | 378 | 52.9% | 50.4% | Advanced |
| 10 | spark-chem13b-nothink | 25.69 | 0.84 | 23.17 | 378 | 46.6% | 52.4% | Advanced |
| 11 | spark-chem13b-think | 25.33 | 0.85 | 22.79 | 378 | 46.8% | 59.1% | Advanced |
| 12 | gpt-4o-mini | 23.95 | 0.86 | 21.37 | 378 | 37.6% | 87.5% | Advanced |
| 13 | llasmol-top1 | 17.00 | 0.95 | 14.14 | 378 | 12.4% | 55.4% | Novice |
| 14 | llasmol-top5 | 16.17 | 0.98 | 13.22 | 378 | 13.0% | 54.5% | Novice |
| 15 | darwin | 15.48 | 1.05 | 12.34 | 378 | 9.8% | N/A | Novice |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 42.74 | 1.28 | 38.91 | 378 | 96.3% | 59.0% | Elite |
| 2 | MOSES | 41.33 | 1.17 | 37.82 | 378 | 93.1% | 80.4% | Elite |
| 3 | o1 | 36.12 | 1.05 | 32.99 | 378 | 81.7% | 78.2% | Elite |
| 4 | gpt-4.1 | 31.39 | 0.98 | 28.47 | 378 | 73.8% | 54.3% | Expert |
| 5 | lightrag-4.1-nano | 30.74 | 0.96 | 27.87 | 378 | 67.5% | 63.0% | Expert |
| 6 | lightrag-4.1 | 28.74 | 0.94 | 25.93 | 378 | 60.1% | 60.5% | Expert |
| 7 | MOSES-nano | 27.13 | 0.94 | 24.31 | 378 | 53.7% | 55.5% | Advanced |
| 8 | gpt-4.1-nano | 26.29 | 0.94 | 23.48 | 378 | 54.5% | 76.0% | Advanced |
| 9 | gpt-4o | 22.03 | 0.96 | 19.14 | 378 | 39.4% | 52.7% | Intermediate |
| 10 | spark-chem13b-think | 21.62 | 0.94 | 18.78 | 378 | 39.4% | 51.1% | Intermediate |
| 11 | spark-chem13b-nothink | 21.45 | 0.95 | 18.61 | 378 | 38.9% | 67.4% | Intermediate |
| 12 | gpt-4o-mini | 18.73 | 1.00 | 15.73 | 378 | 28.8% | 93.2% | Intermediate |
| 13 | darwin | 9.66 | 1.19 | 6.09 | 378 | 9.5% | 51.6% | Beginner |
| 14 | llasmol-top5 | 9.41 | 1.19 | 5.84 | 378 | 7.1% | 63.1% | Beginner |
| 15 | llasmol-top1 | 7.35 | 1.21 | 3.71 | 378 | 6.1% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 43.11 | 1.35 | 39.06 | 378 | 97.6% | 94.3% | Elite |
| 2 | MOSES-nano | 33.44 | 0.95 | 30.60 | 378 | 74.9% | 53.6% | Elite |
| 3 | o3 | 32.89 | 0.92 | 30.13 | 378 | 75.7% | 52.6% | Elite |
| 4 | lightrag-4.1 | 32.50 | 0.95 | 29.66 | 378 | 77.2% | 51.0% | Expert |
| 5 | lightrag-4.1-nano | 32.35 | 0.93 | 29.57 | 378 | 75.7% | 63.6% | Expert |
| 6 | o1 | 30.25 | 0.91 | 27.52 | 378 | 66.7% | 70.0% | Expert |
| 7 | gpt-4.1 | 27.09 | 0.90 | 24.39 | 378 | 56.1% | 57.1% | Advanced |
| 8 | gpt-4.1-nano | 26.00 | 0.91 | 23.28 | 378 | 50.5% | 69.7% | Advanced |
| 9 | spark-chem13b-think | 22.89 | 0.91 | 20.16 | 378 | 41.0% | 51.1% | Advanced |
| 10 | spark-chem13b-nothink | 22.73 | 0.92 | 19.98 | 378 | 40.7% | 52.9% | Intermediate |
| 11 | gpt-4o | 22.29 | 0.94 | 19.47 | 378 | 39.7% | 63.0% | Intermediate |
| 12 | gpt-4o-mini | 20.28 | 0.97 | 17.35 | 378 | 31.0% | 95.1% | Intermediate |
| 13 | llasmol-top5 | 10.16 | 1.21 | 6.54 | 378 | 7.7% | 51.7% | Beginner |
| 14 | darwin | 9.90 | 1.19 | 6.32 | 378 | 8.5% | 61.1% | Beginner |
| 15 | llasmol-top1 | 8.17 | 1.21 | 4.55 | 378 | 7.1% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **36.41**

### Most Consistent Model
**gpt-4.1** shows the lowest uncertainty with σ=0.88

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Completeness | MOSES | 34.00 | 37.24 | 1.08 | 1.89 |
| Rigor And Information Density | o3 | 38.91 | 42.74 | 1.28 | 1.08 |
| Correctness | o3 | 33.22 | 36.18 | 0.99 | 0.24 |
| Theoretical Depth | MOSES | 39.06 | 43.11 | 1.35 | 8.46 |

### Rating Distribution
- **Mean Overall ELO**: 21.83
- **ELO Std**: 7.93
- **ELO Range**: 36.41 - 8.16
- **Mean μ (Skill)**: 24.70
- **Mean σ (Uncertainty)**: 0.96
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 11,340
- **Matches per Dimension**: 2,835

### Method Details

**Overall ELO Calculation**:
- Uses joint modeling approach
- Combines all dimension matches into single TrueSkill calculation
- Provides unified ranking across all evaluation aspects

**Dimension ELO Calculations**:
- Each dimension calculated independently (pure separation)
- Allows comparison of model strengths across different aspects

**Data Aggregation Level**: double
- LLM评分聚合: 5个LLM评分 → 平均值
- 回答轮次聚合: 多轮回答 → 平均值
- 每个问题-维度生成1个匹配

