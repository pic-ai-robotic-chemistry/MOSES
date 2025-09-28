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
- **Analysis duration**: 148.2s

## TrueSkill Model Rankings - Overall ELO (Multi-Repetition Aggregated)

**Final ELO calculated by aggregating 5 repetitions**: Each repetition uses randomized match order, then results are averaged for stable ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 32.42 | 35.35 | 0.98 | mean_across_5_repetitions | 4 dimensions | 59.7% | Elite |
| 2 | o3 | 31.05 | 33.86 | 0.94 | mean_across_5_repetitions | 4 dimensions | 77.7% | Elite |
| 3 | gpt-4.1 | 26.70 | 29.27 | 0.86 | mean_across_5_repetitions | 4 dimensions | 50.2% | Expert |
| 4 | o1 | 26.69 | 29.24 | 0.85 | mean_across_5_repetitions | 4 dimensions | 53.8% | Expert |
| 5 | lightrag-4.1-nano | 26.10 | 28.67 | 0.85 | mean_across_5_repetitions | 4 dimensions | 53.3% | Expert |
| 6 | lightrag-4.1 | 25.60 | 28.17 | 0.86 | mean_across_5_repetitions | 4 dimensions | 50.7% | Expert |
| 7 | MOSES-nano | 25.52 | 28.07 | 0.85 | mean_across_5_repetitions | 4 dimensions | 58.7% | Expert |
| 8 | gpt-4.1-nano | 24.21 | 26.75 | 0.85 | mean_across_5_repetitions | 4 dimensions | 63.4% | Advanced |
| 9 | spark-chem13b-nothink | 22.14 | 24.69 | 0.85 | mean_across_5_repetitions | 4 dimensions | 50.2% | Advanced |
| 10 | spark-chem13b-think | 22.10 | 24.65 | 0.85 | mean_across_5_repetitions | 4 dimensions | 50.1% | Advanced |
| 11 | gpt-4o | 22.06 | 24.64 | 0.86 | mean_across_5_repetitions | 4 dimensions | 63.1% | Advanced |
| 12 | gpt-4o-mini | 20.00 | 22.62 | 0.87 | mean_across_5_repetitions | 4 dimensions | 92.5% | Intermediate |
| 13 | llasmol-top5 | 10.84 | 13.92 | 1.03 | mean_across_5_repetitions | 4 dimensions | 50.6% | Novice |
| 14 | llasmol-top1 | 10.78 | 13.83 | 1.02 | mean_across_5_repetitions | 4 dimensions | 52.8% | Novice |
| 15 | darwin | 10.32 | 13.40 | 1.03 | mean_across_5_repetitions | 4 dimensions | N/A | Novice |

## Detailed Dimension Analysis (Multi-Repetition Aggregated)

**Dimension ELO aggregated from 5 repetitions**: Each dimension calculated separately per repetition, then averaged for final ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 33.76 | 0.93 | 30.96 | 47250 | 90.3% | 58.3% | Elite |
| 2 | o3 | 32.49 | 0.89 | 29.81 | 47250 | 83.8% | 67.0% | Expert |
| 3 | gpt-4.1 | 29.85 | 0.85 | 27.29 | 47250 | 71.0% | 63.9% | Expert |
| 4 | lightrag-4.1 | 27.71 | 0.84 | 25.21 | 47250 | 58.6% | 50.1% | Expert |
| 5 | lightrag-4.1-nano | 27.69 | 0.84 | 25.18 | 47250 | 62.5% | 56.3% | Expert |
| 6 | o1 | 26.75 | 0.83 | 24.27 | 47250 | 57.7% | 50.6% | Advanced |
| 7 | MOSES-nano | 26.66 | 0.83 | 24.15 | 47250 | 56.6% | 51.2% | Advanced |
| 8 | gpt-4.1-nano | 26.47 | 0.83 | 23.98 | 47250 | 54.8% | 53.1% | Advanced |
| 9 | gpt-4o | 26.00 | 0.83 | 23.52 | 47250 | 50.2% | 53.6% | Advanced |
| 10 | spark-chem13b-nothink | 25.46 | 0.83 | 22.98 | 47250 | 48.2% | 55.5% | Advanced |
| 11 | spark-chem13b-think | 24.63 | 0.83 | 22.15 | 47250 | 46.8% | 56.0% | Advanced |
| 12 | gpt-4o-mini | 23.72 | 0.85 | 21.18 | 47250 | 41.5% | 90.5% | Advanced |
| 13 | llasmol-top1 | 15.81 | 0.96 | 12.93 | 47250 | 10.2% | 51.9% | Novice |
| 14 | llasmol-top5 | 15.51 | 0.99 | 12.55 | 47250 | 9.3% | 50.4% | Novice |
| 15 | darwin | 15.45 | 0.98 | 12.52 | 47250 | 8.5% | N/A | Novice |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 32.64 | 0.87 | 30.02 | 47250 | 87.0% | 53.3% | Elite |
| 2 | o3 | 32.15 | 0.87 | 29.55 | 47250 | 83.6% | 70.3% | Expert |
| 3 | gpt-4.1 | 28.95 | 0.82 | 26.48 | 47250 | 68.8% | 54.5% | Expert |
| 4 | o1 | 28.26 | 0.82 | 25.80 | 47250 | 67.0% | 57.1% | Expert |
| 5 | MOSES-nano | 27.19 | 0.82 | 24.74 | 47250 | 58.0% | 50.9% | Advanced |
| 6 | gpt-4.1-nano | 27.06 | 0.82 | 24.59 | 47250 | 57.9% | 51.7% | Advanced |
| 7 | lightrag-4.1-nano | 26.80 | 0.82 | 24.35 | 47250 | 57.0% | 53.6% | Advanced |
| 8 | lightrag-4.1 | 26.26 | 0.82 | 23.80 | 47250 | 53.3% | 55.8% | Advanced |
| 9 | spark-chem13b-nothink | 25.38 | 0.81 | 22.94 | 47250 | 48.7% | 50.7% | Advanced |
| 10 | gpt-4o | 25.28 | 0.82 | 22.83 | 47250 | 48.0% | 52.1% | Advanced |
| 11 | spark-chem13b-think | 24.97 | 0.83 | 22.49 | 47250 | 47.4% | 61.4% | Advanced |
| 12 | gpt-4o-mini | 23.23 | 0.83 | 20.75 | 47250 | 37.3% | 80.5% | Advanced |
| 13 | llasmol-top5 | 18.05 | 0.89 | 15.38 | 47250 | 15.1% | 52.7% | Intermediate |
| 14 | llasmol-top1 | 17.64 | 0.92 | 14.89 | 47250 | 12.7% | 61.2% | Novice |
| 15 | darwin | 15.91 | 0.96 | 13.04 | 47250 | 7.9% | N/A | Novice |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 39.55 | 1.12 | 36.20 | 47250 | 94.8% | 66.0% | Elite |
| 2 | MOSES | 37.04 | 1.01 | 34.01 | 47250 | 90.6% | 75.6% | Elite |
| 3 | o1 | 32.85 | 0.91 | 30.14 | 47250 | 78.9% | 58.7% | Elite |
| 4 | gpt-4.1 | 31.53 | 0.90 | 28.84 | 47250 | 71.9% | 63.0% | Expert |
| 5 | lightrag-4.1-nano | 29.53 | 0.89 | 26.85 | 47250 | 64.5% | 58.8% | Expert |
| 6 | lightrag-4.1 | 28.19 | 0.88 | 25.54 | 47250 | 60.3% | 51.3% | Expert |
| 7 | MOSES-nano | 27.99 | 0.89 | 25.34 | 47250 | 56.5% | 53.6% | Expert |
| 8 | gpt-4.1-nano | 27.45 | 0.89 | 24.79 | 47250 | 55.0% | 71.4% | Advanced |
| 9 | spark-chem13b-think | 24.04 | 0.90 | 21.35 | 47250 | 41.8% | 51.8% | Advanced |
| 10 | spark-chem13b-nothink | 23.77 | 0.89 | 21.09 | 47250 | 40.7% | 50.6% | Advanced |
| 11 | gpt-4o | 23.68 | 0.91 | 20.96 | 47250 | 40.8% | 67.5% | Advanced |
| 12 | gpt-4o-mini | 20.95 | 0.94 | 18.12 | 47250 | 31.2% | 96.2% | Intermediate |
| 13 | darwin | 10.15 | 1.14 | 6.74 | 47250 | 7.7% | 50.7% | Beginner |
| 14 | llasmol-top5 | 10.05 | 1.14 | 6.63 | 47250 | 8.2% | 51.7% | Beginner |
| 15 | llasmol-top1 | 9.79 | 1.13 | 6.39 | 47250 | 7.1% | N/A | Beginner |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 37.98 | 1.10 | 34.67 | 47250 | 96.0% | 86.6% | Elite |
| 2 | o3 | 31.26 | 0.87 | 28.65 | 47250 | 73.5% | 54.1% | Expert |
| 3 | lightrag-4.1-nano | 30.65 | 0.87 | 28.03 | 47250 | 73.6% | 50.9% | Expert |
| 4 | lightrag-4.1 | 30.51 | 0.89 | 27.85 | 47250 | 74.0% | 50.5% | Expert |
| 5 | MOSES-nano | 30.44 | 0.87 | 27.84 | 47250 | 72.4% | 58.9% | Expert |
| 6 | o1 | 29.09 | 0.85 | 26.55 | 47250 | 64.8% | 65.2% | Expert |
| 7 | gpt-4.1 | 26.74 | 0.86 | 24.17 | 47250 | 55.3% | 54.8% | Advanced |
| 8 | gpt-4.1-nano | 26.02 | 0.85 | 23.46 | 47250 | 52.3% | 56.9% | Advanced |
| 9 | spark-chem13b-think | 24.97 | 0.85 | 22.42 | 47250 | 46.2% | 55.5% | Advanced |
| 10 | spark-chem13b-nothink | 24.13 | 0.86 | 21.56 | 47250 | 43.6% | 53.7% | Advanced |
| 11 | gpt-4o | 23.57 | 0.88 | 20.93 | 47250 | 40.6% | 56.5% | Advanced |
| 12 | gpt-4o-mini | 22.59 | 0.88 | 19.94 | 47250 | 33.9% | 95.9% | Intermediate |
| 13 | darwin | 12.08 | 1.03 | 9.00 | 47250 | 7.4% | 50.1% | Beginner |
| 14 | llasmol-top1 | 12.07 | 1.06 | 8.90 | 47250 | 8.3% | 50.1% | Beginner |
| 15 | llasmol-top5 | 12.05 | 1.08 | 8.80 | 47250 | 8.2% | N/A | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **32.42**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.85

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Rigor And Information Density | o3 | 36.20 | 39.55 | 1.12 | 2.19 |
| Correctness | MOSES | 30.02 | 32.64 | 0.87 | 0.47 |
| Completeness | MOSES | 30.96 | 33.76 | 0.93 | 1.15 |
| Theoretical Depth | MOSES | 34.67 | 37.98 | 1.10 | 6.01 |

### Rating Distribution
- **Mean Overall ELO**: 22.43
- **ELO Std**: 6.68
- **ELO Range**: 32.42 - 10.32
- **Mean μ (Skill)**: 25.14
- **Mean σ (Uncertainty)**: 0.90
- **Models Analyzed**: 15
- **Data Source**: real
