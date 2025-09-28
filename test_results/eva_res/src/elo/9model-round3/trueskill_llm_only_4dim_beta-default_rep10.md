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

- **Repetitions**: 10 (with randomized match order)
- **Base matches per repetition**: 97,200
- **Total matches across all repetitions**: 972,000
- **Final ratings**: Aggregated across all repetitions (reported below)
- **Unique models**: 9
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)
- **Analysis duration**: 99.8s

## TrueSkill Model Rankings - Overall ELO (Multi-Repetition Aggregated)

**Final ELO calculated by aggregating 10 repetitions**: Each repetition uses randomized match order, then results are averaged for stable ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 29.51 | 32.28 | 0.92 | mean_across_10_repetitions | 4 dimensions | 62.6% | Expert |
| 2 | o3 | 27.69 | 30.34 | 0.88 | mean_across_10_repetitions | 4 dimensions | 76.5% | Expert |
| 3 | gpt-4.1 | 23.52 | 25.98 | 0.82 | mean_across_10_repetitions | 4 dimensions | 56.2% | Advanced |
| 4 | lightrag-4.1-nano | 22.60 | 25.04 | 0.82 | mean_across_10_repetitions | 4 dimensions | 52.2% | Advanced |
| 5 | lightrag-4.1 | 22.24 | 24.71 | 0.82 | mean_across_10_repetitions | 4 dimensions | 51.6% | Advanced |
| 6 | MOSES-nano | 22.02 | 24.47 | 0.82 | mean_across_10_repetitions | 4 dimensions | 59.0% | Advanced |
| 7 | gpt-4.1-nano | 20.64 | 23.09 | 0.82 | mean_across_10_repetitions | 4 dimensions | 65.7% | Advanced |
| 8 | gpt-4o | 18.15 | 20.67 | 0.84 | mean_across_10_repetitions | 4 dimensions | 66.9% | Intermediate |
| 9 | gpt-4o-mini | 15.34 | 18.04 | 0.90 | mean_across_10_repetitions | 4 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Multi-Repetition Aggregated)

**Dimension ELO aggregated from 10 repetitions**: Each dimension calculated separately per repetition, then averaged for final ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 30.90 | 0.89 | 28.24 | 54000 | 86.5% | 60.7% | Expert |
| 2 | o3 | 29.26 | 0.85 | 26.71 | 54000 | 78.2% | 70.2% | Expert |
| 3 | gpt-4.1 | 26.08 | 0.81 | 23.65 | 54000 | 60.6% | 64.8% | Advanced |
| 4 | lightrag-4.1-nano | 23.79 | 0.80 | 21.38 | 54000 | 47.2% | 51.5% | Advanced |
| 5 | lightrag-4.1 | 23.57 | 0.80 | 21.17 | 54000 | 43.3% | 53.0% | Advanced |
| 6 | MOSES-nano | 23.12 | 0.80 | 20.71 | 54000 | 41.3% | 53.8% | Advanced |
| 7 | gpt-4.1-nano | 22.54 | 0.81 | 20.12 | 54000 | 38.9% | 56.9% | Advanced |
| 8 | gpt-4o | 21.50 | 0.81 | 19.06 | 54000 | 32.9% | 64.0% | Intermediate |
| 9 | gpt-4o-mini | 19.35 | 0.85 | 16.81 | 54000 | 21.0% | N/A | Intermediate |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 30.36 | 0.84 | 27.84 | 54000 | 83.8% | 54.2% | Expert |
| 2 | o3 | 29.72 | 0.83 | 27.22 | 54000 | 80.2% | 69.0% | Expert |
| 3 | gpt-4.1 | 26.75 | 0.80 | 24.34 | 54000 | 61.1% | 65.5% | Advanced |
| 4 | MOSES-nano | 24.36 | 0.79 | 21.98 | 54000 | 44.9% | 50.3% | Advanced |
| 5 | gpt-4.1-nano | 24.32 | 0.79 | 21.94 | 54000 | 46.3% | 51.5% | Advanced |
| 6 | lightrag-4.1-nano | 24.10 | 0.80 | 21.71 | 54000 | 43.4% | 56.7% | Advanced |
| 7 | lightrag-4.1 | 23.08 | 0.80 | 20.67 | 54000 | 38.3% | 56.0% | Advanced |
| 8 | gpt-4o | 22.17 | 0.80 | 19.76 | 54000 | 33.1% | 63.6% | Intermediate |
| 9 | gpt-4o-mini | 20.09 | 0.84 | 17.58 | 54000 | 18.9% | N/A | Intermediate |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 35.22 | 1.02 | 32.15 | 54000 | 92.8% | 63.7% | Elite |
| 2 | MOSES | 33.10 | 0.95 | 30.25 | 54000 | 87.1% | 83.1% | Elite |
| 3 | gpt-4.1 | 27.32 | 0.85 | 24.76 | 54000 | 62.2% | 64.5% | Advanced |
| 4 | lightrag-4.1-nano | 25.08 | 0.83 | 22.58 | 54000 | 51.8% | 54.7% | Advanced |
| 5 | lightrag-4.1 | 24.38 | 0.84 | 21.85 | 54000 | 46.1% | 57.1% | Advanced |
| 6 | MOSES-nano | 23.30 | 0.84 | 20.78 | 54000 | 41.3% | 50.9% | Advanced |
| 7 | gpt-4.1-nano | 23.17 | 0.85 | 20.63 | 54000 | 39.9% | 74.8% | Advanced |
| 8 | gpt-4o | 19.15 | 0.89 | 16.48 | 54000 | 21.0% | 74.1% | Intermediate |
| 9 | gpt-4o-mini | 15.24 | 0.99 | 12.27 | 54000 | 7.8% | N/A | Novice |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 34.76 | 1.01 | 31.73 | 54000 | 94.0% | 87.6% | Elite |
| 2 | lightrag-4.1 | 27.80 | 0.84 | 25.28 | 54000 | 63.5% | 53.9% | Expert |
| 3 | lightrag-4.1-nano | 27.21 | 0.83 | 24.72 | 54000 | 63.2% | 50.4% | Advanced |
| 4 | o3 | 27.15 | 0.82 | 24.68 | 54000 | 62.7% | 50.4% | Advanced |
| 5 | MOSES-nano | 27.08 | 0.83 | 24.60 | 54000 | 61.2% | 70.8% | Advanced |
| 6 | gpt-4.1 | 23.79 | 0.82 | 21.33 | 54000 | 38.9% | 59.5% | Advanced |
| 7 | gpt-4.1-nano | 22.34 | 0.82 | 19.87 | 54000 | 35.2% | 65.9% | Intermediate |
| 8 | gpt-4o | 19.87 | 0.86 | 17.29 | 54000 | 20.1% | 65.4% | Intermediate |
| 9 | gpt-4o-mini | 17.48 | 0.93 | 14.70 | 54000 | 11.3% | N/A | Novice |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **29.51**

### Most Consistent Model
**MOSES-nano** shows the lowest uncertainty with σ=0.82

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Rigor And Information Density | o3 | 32.15 | 35.22 | 1.02 | 1.90 |
| Correctness | MOSES | 27.84 | 30.36 | 0.84 | 0.62 |
| Completeness | MOSES | 28.24 | 30.90 | 0.89 | 1.54 |
| Theoretical Depth | MOSES | 31.73 | 34.76 | 1.01 | 6.45 |

### Rating Distribution
- **Mean Overall ELO**: 22.41
- **ELO Std**: 4.10
- **ELO Range**: 29.51 - 15.34
- **Mean μ (Skill)**: 24.96
- **Mean σ (Uncertainty)**: 0.85
- **Models Analyzed**: 9
- **Data Source**: real
- **Total Matches (All Repetitions)**: 972,000
- **Matches per Repetition**: 97,200
- **Matches per Dimension per Repetition**: 24,300

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

