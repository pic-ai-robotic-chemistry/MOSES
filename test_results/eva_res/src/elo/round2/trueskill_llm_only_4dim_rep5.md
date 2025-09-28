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

- **Repetitions**: 5 (with randomized match order)
- **Base matches per repetition**: 283,500
- **Total matches across all repetitions**: 1,417,500
- **Final ratings**: Aggregated across all repetitions (reported below)
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)
- **Analysis duration**: 151.1s

## TrueSkill Model Rankings - Overall ELO (Multi-Repetition Aggregated)

**Final ELO calculated by aggregating 5 repetitions**: Each repetition uses randomized match order, then results are averaged for stable ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 32.41 | 35.42 | 1.00 | mean_across_5_repetitions | 4 dimensions | 63.8% | Elite |
| 2 | o3 | 30.50 | 33.29 | 0.93 | mean_across_5_repetitions | 4 dimensions | 76.2% | Elite |
| 3 | o1 | 26.42 | 28.99 | 0.85 | mean_across_5_repetitions | 4 dimensions | 52.0% | Expert |
| 4 | gpt-4.1 | 26.12 | 28.69 | 0.86 | mean_across_5_repetitions | 4 dimensions | 53.3% | Expert |
| 5 | lightrag-4.1-nano | 25.63 | 28.19 | 0.85 | mean_across_5_repetitions | 4 dimensions | 53.2% | Expert |
| 6 | lightrag-4.1 | 25.13 | 27.70 | 0.86 | mean_across_5_repetitions | 4 dimensions | 50.4% | Expert |
| 7 | MOSES-nano | 25.10 | 27.65 | 0.85 | mean_across_5_repetitions | 4 dimensions | 58.3% | Expert |
| 8 | gpt-4.1-nano | 23.85 | 26.39 | 0.85 | mean_across_5_repetitions | 4 dimensions | 63.5% | Advanced |
| 9 | spark-chem13b-think | 21.78 | 24.32 | 0.85 | mean_across_5_repetitions | 4 dimensions | 50.7% | Advanced |
| 10 | spark-chem13b-nothink | 21.67 | 24.21 | 0.85 | mean_across_5_repetitions | 4 dimensions | 50.4% | Advanced |
| 11 | gpt-4o | 21.58 | 24.15 | 0.86 | mean_across_5_repetitions | 4 dimensions | 63.2% | Advanced |
| 12 | gpt-4o-mini | 19.49 | 22.13 | 0.88 | mean_across_5_repetitions | 4 dimensions | 91.6% | Intermediate |
| 13 | llasmol-top5 | 10.74 | 13.80 | 1.02 | mean_across_5_repetitions | 4 dimensions | 53.0% | Novice |
| 14 | llasmol-top1 | 10.29 | 13.35 | 1.02 | mean_across_5_repetitions | 4 dimensions | 53.3% | Novice |
| 15 | darwin | 9.76 | 12.84 | 1.03 | mean_across_5_repetitions | 4 dimensions | N/A | Beginner |

## Detailed Dimension Analysis (Multi-Repetition Aggregated)

**Dimension ELO aggregated from 5 repetitions**: Each dimension calculated separately per repetition, then averaged for final ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 34.25 | 0.96 | 31.35 | 47250 | 90.3% | 65.0% | Elite |
| 2 | o3 | 31.92 | 0.89 | 29.24 | 47250 | 83.8% | 68.6% | Expert |
| 3 | gpt-4.1 | 29.01 | 0.84 | 26.48 | 47250 | 71.0% | 59.6% | Expert |
| 4 | lightrag-4.1-nano | 27.55 | 0.84 | 25.01 | 47250 | 62.5% | 52.9% | Expert |
| 5 | lightrag-4.1 | 27.11 | 0.84 | 24.60 | 47250 | 58.6% | 50.4% | Advanced |
| 6 | o1 | 27.04 | 0.83 | 24.56 | 47250 | 57.7% | 54.2% | Advanced |
| 7 | MOSES-nano | 26.41 | 0.84 | 23.90 | 47250 | 56.6% | 50.7% | Advanced |
| 8 | gpt-4.1-nano | 26.30 | 0.83 | 23.80 | 47250 | 54.8% | 57.8% | Advanced |
| 9 | spark-chem13b-nothink | 25.13 | 0.83 | 22.65 | 47250 | 48.2% | 50.6% | Advanced |
| 10 | gpt-4o | 25.04 | 0.83 | 22.55 | 47250 | 50.2% | 53.9% | Advanced |
| 11 | spark-chem13b-think | 24.44 | 0.83 | 21.95 | 47250 | 46.8% | 58.0% | Advanced |
| 12 | gpt-4o-mini | 23.23 | 0.84 | 20.70 | 47250 | 41.5% | 90.3% | Advanced |
| 13 | llasmol-top1 | 15.39 | 0.96 | 12.50 | 47250 | 10.2% | 50.1% | Novice |
| 14 | llasmol-top5 | 15.37 | 0.97 | 12.46 | 47250 | 9.3% | 52.8% | Novice |
| 15 | darwin | 14.94 | 0.98 | 12.01 | 47250 | 8.5% | N/A | Novice |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 32.33 | 0.88 | 29.69 | 47250 | 87.0% | 56.0% | Expert |
| 2 | o3 | 31.42 | 0.85 | 28.86 | 47250 | 83.6% | 71.3% | Expert |
| 3 | o1 | 28.05 | 0.82 | 25.58 | 47250 | 67.0% | 50.3% | Expert |
| 4 | gpt-4.1 | 28.01 | 0.82 | 25.56 | 47250 | 68.8% | 57.9% | Expert |
| 5 | gpt-4.1-nano | 26.82 | 0.82 | 24.36 | 47250 | 57.9% | 51.9% | Advanced |
| 6 | MOSES-nano | 26.53 | 0.81 | 24.09 | 47250 | 58.0% | 54.4% | Advanced |
| 7 | lightrag-4.1-nano | 25.87 | 0.81 | 23.43 | 47250 | 57.0% | 50.3% | Advanced |
| 8 | lightrag-4.1 | 25.82 | 0.82 | 23.36 | 47250 | 53.3% | 53.2% | Advanced |
| 9 | gpt-4o | 25.33 | 0.81 | 22.89 | 47250 | 48.0% | 52.7% | Advanced |
| 10 | spark-chem13b-nothink | 24.93 | 0.81 | 22.48 | 47250 | 48.7% | 51.9% | Advanced |
| 11 | spark-chem13b-think | 24.64 | 0.82 | 22.18 | 47250 | 47.4% | 61.0% | Advanced |
| 12 | gpt-4o-mini | 22.95 | 0.83 | 20.46 | 47250 | 37.3% | 80.6% | Advanced |
| 13 | llasmol-top5 | 17.77 | 0.90 | 15.08 | 47250 | 15.1% | 56.2% | Intermediate |
| 14 | llasmol-top1 | 16.83 | 0.93 | 14.04 | 47250 | 12.7% | 59.2% | Novice |
| 15 | darwin | 15.43 | 0.96 | 12.54 | 47250 | 7.9% | N/A | Novice |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 39.45 | 1.11 | 36.13 | 47250 | 94.8% | 67.9% | Elite |
| 2 | MOSES | 36.62 | 1.03 | 33.54 | 47250 | 90.6% | 75.0% | Elite |
| 3 | o1 | 32.54 | 0.91 | 29.82 | 47250 | 78.9% | 60.1% | Expert |
| 4 | gpt-4.1 | 31.00 | 0.90 | 28.29 | 47250 | 71.9% | 63.7% | Expert |
| 5 | lightrag-4.1-nano | 28.89 | 0.88 | 26.26 | 47250 | 64.5% | 59.6% | Expert |
| 6 | lightrag-4.1 | 27.43 | 0.89 | 24.77 | 47250 | 60.3% | 51.9% | Advanced |
| 7 | MOSES-nano | 27.15 | 0.87 | 24.54 | 47250 | 56.5% | 55.7% | Advanced |
| 8 | gpt-4.1-nano | 26.29 | 0.88 | 23.64 | 47250 | 55.0% | 65.8% | Advanced |
| 9 | spark-chem13b-think | 23.84 | 0.88 | 21.19 | 47250 | 41.8% | 55.0% | Advanced |
| 10 | gpt-4o | 23.08 | 0.90 | 20.38 | 47250 | 40.8% | 50.3% | Advanced |
| 11 | spark-chem13b-nothink | 23.03 | 0.89 | 20.35 | 47250 | 40.7% | 66.1% | Advanced |
| 12 | gpt-4o-mini | 20.53 | 0.94 | 17.71 | 47250 | 31.2% | 95.8% | Intermediate |
| 13 | llasmol-top5 | 10.07 | 1.13 | 6.67 | 47250 | 8.2% | 55.7% | Beginner |
| 14 | darwin | 9.19 | 1.10 | 5.88 | 47250 | 7.7% | 50.8% | Beginner |
| 15 | llasmol-top1 | 9.06 | 1.13 | 5.69 | 47250 | 7.1% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 38.49 | 1.15 | 35.04 | 47250 | 96.0% | 90.6% | Elite |
| 2 | MOSES-nano | 30.49 | 0.88 | 27.87 | 47250 | 72.4% | 50.3% | Expert |
| 3 | lightrag-4.1-nano | 30.45 | 0.88 | 27.82 | 47250 | 73.6% | 50.1% | Expert |
| 4 | lightrag-4.1 | 30.44 | 0.89 | 27.78 | 47250 | 74.0% | 50.5% | Expert |
| 5 | o3 | 30.36 | 0.87 | 27.76 | 47250 | 73.5% | 63.4% | Expert |
| 6 | o1 | 28.31 | 0.86 | 25.73 | 47250 | 64.8% | 60.3% | Expert |
| 7 | gpt-4.1 | 26.73 | 0.86 | 24.14 | 47250 | 55.3% | 53.8% | Advanced |
| 8 | gpt-4.1-nano | 26.16 | 0.86 | 23.59 | 47250 | 52.3% | 61.7% | Advanced |
| 9 | spark-chem13b-think | 24.36 | 0.85 | 21.80 | 47250 | 46.2% | 54.0% | Advanced |
| 10 | spark-chem13b-nothink | 23.76 | 0.86 | 21.18 | 47250 | 43.6% | 54.1% | Advanced |
| 11 | gpt-4o | 23.14 | 0.88 | 20.52 | 47250 | 40.6% | 58.9% | Advanced |
| 12 | gpt-4o-mini | 21.79 | 0.89 | 19.11 | 47250 | 33.9% | 94.5% | Intermediate |
| 13 | llasmol-top1 | 12.10 | 1.06 | 8.92 | 47250 | 8.3% | 50.7% | Beginner |
| 14 | llasmol-top5 | 11.99 | 1.08 | 8.76 | 47250 | 8.2% | 51.1% | Beginner |
| 15 | darwin | 11.81 | 1.06 | 8.62 | 47250 | 7.4% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **32.41**

### Most Consistent Model
**spark-chem13b-think** shows the lowest uncertainty with σ=0.85

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Completeness | MOSES | 31.35 | 34.25 | 0.96 | 2.11 |
| Correctness | MOSES | 29.69 | 32.33 | 0.88 | 0.83 |
| Theoretical Depth | MOSES | 35.04 | 38.49 | 1.15 | 7.18 |
| Rigor And Information Density | o3 | 36.13 | 39.45 | 1.11 | 2.59 |

### Rating Distribution
- **Mean Overall ELO**: 22.03
- **ELO Std**: 6.70
- **ELO Range**: 32.41 - 9.76
- **Mean μ (Skill)**: 24.74
- **Mean σ (Uncertainty)**: 0.90
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches (All Repetitions)**: 1,417,500
- **Matches per Repetition**: 283,500
- **Matches per Dimension per Repetition**: 70,875

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

