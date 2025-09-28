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

- **Repetitions**: 20 (with randomized match order)
- **Base matches per repetition**: 97,200
- **Total matches across all repetitions**: 1,944,000
- **Final ratings**: Aggregated across all repetitions (reported below)
- **Unique models**: 9
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches (aggregation: llm_only)
- **Aggregation mode**: Single aggregation (LLM评分→平均, 保留回答轮次)
- **Analysis duration**: 202.1s

## TrueSkill Model Rankings - Overall ELO (Multi-Repetition Aggregated)

**Final ELO calculated by aggregating 20 repetitions**: Each repetition uses randomized match order, then results are averaged for stable ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |
|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|
| 1 | MOSES | 29.74 | 32.51 | 0.92 | mean_across_20_repetitions | 4 dimensions | 63.5% | Expert |
| 2 | o3 | 27.78 | 30.42 | 0.88 | mean_across_20_repetitions | 4 dimensions | 77.3% | Expert |
| 3 | gpt-4.1 | 23.47 | 25.92 | 0.82 | mean_across_20_repetitions | 4 dimensions | 55.0% | Advanced |
| 4 | lightrag-4.1-nano | 22.72 | 25.17 | 0.82 | mean_across_20_repetitions | 4 dimensions | 52.7% | Advanced |
| 5 | lightrag-4.1 | 22.30 | 24.76 | 0.82 | mean_across_20_repetitions | 4 dimensions | 51.0% | Advanced |
| 6 | MOSES-nano | 22.16 | 24.61 | 0.82 | mean_across_20_repetitions | 4 dimensions | 57.6% | Advanced |
| 7 | gpt-4.1-nano | 21.00 | 23.45 | 0.82 | mean_across_20_repetitions | 4 dimensions | 66.6% | Advanced |
| 8 | gpt-4o | 18.36 | 20.88 | 0.84 | mean_across_20_repetitions | 4 dimensions | 66.6% | Intermediate |
| 9 | gpt-4o-mini | 15.61 | 18.29 | 0.90 | mean_across_20_repetitions | 4 dimensions | N/A | Intermediate |

## Detailed Dimension Analysis (Multi-Repetition Aggregated)

**Dimension ELO aggregated from 20 repetitions**: Each dimension calculated separately per repetition, then averaged for final ratings.

📊 **Note**: Individual repetition details are available in the accompanying JSON file for granular analysis.

### Judge: Doubao-Seed-1.6-combined

#### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 31.46 | 0.88 | 28.81 | 108000 | 86.5% | 62.5% | Expert |
| 2 | o3 | 29.54 | 0.84 | 27.02 | 108000 | 78.2% | 67.9% | Expert |
| 3 | gpt-4.1 | 26.75 | 0.81 | 24.32 | 108000 | 60.6% | 65.7% | Advanced |
| 4 | lightrag-4.1-nano | 24.32 | 0.80 | 21.91 | 108000 | 47.2% | 51.3% | Advanced |
| 5 | lightrag-4.1 | 24.13 | 0.80 | 21.73 | 108000 | 43.3% | 53.0% | Advanced |
| 6 | MOSES-nano | 23.68 | 0.80 | 21.27 | 108000 | 41.3% | 50.8% | Advanced |
| 7 | gpt-4.1-nano | 23.55 | 0.80 | 21.14 | 108000 | 38.9% | 58.0% | Advanced |
| 8 | gpt-4o | 22.34 | 0.81 | 19.91 | 108000 | 32.9% | 63.3% | Intermediate |
| 9 | gpt-4o-mini | 20.30 | 0.84 | 17.77 | 108000 | 21.0% | N/A | Intermediate |

#### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 30.62 | 0.84 | 28.08 | 108000 | 83.8% | 55.2% | Expert |
| 2 | o3 | 29.82 | 0.83 | 27.32 | 108000 | 80.2% | 70.4% | Expert |
| 3 | gpt-4.1 | 26.60 | 0.80 | 24.21 | 108000 | 61.1% | 63.5% | Advanced |
| 4 | gpt-4.1-nano | 24.53 | 0.79 | 22.15 | 108000 | 46.3% | 51.0% | Advanced |
| 5 | MOSES-nano | 24.38 | 0.79 | 21.99 | 108000 | 44.9% | 53.4% | Advanced |
| 6 | lightrag-4.1-nano | 23.86 | 0.80 | 21.46 | 108000 | 43.4% | 52.7% | Advanced |
| 7 | lightrag-4.1 | 23.45 | 0.80 | 21.06 | 108000 | 38.3% | 56.9% | Advanced |
| 8 | gpt-4o | 22.42 | 0.80 | 20.00 | 108000 | 33.1% | 65.8% | Advanced |
| 9 | gpt-4o-mini | 19.97 | 0.84 | 17.44 | 108000 | 18.9% | N/A | Intermediate |

#### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | o3 | 35.34 | 1.03 | 32.26 | 108000 | 92.8% | 64.1% | Elite |
| 2 | MOSES | 33.16 | 0.94 | 30.33 | 108000 | 87.1% | 83.7% | Elite |
| 3 | gpt-4.1 | 27.24 | 0.85 | 24.70 | 108000 | 62.2% | 62.1% | Advanced |
| 4 | lightrag-4.1-nano | 25.39 | 0.84 | 22.88 | 108000 | 51.8% | 57.1% | Advanced |
| 5 | lightrag-4.1 | 24.31 | 0.84 | 21.80 | 108000 | 46.1% | 56.5% | Advanced |
| 6 | MOSES-nano | 23.32 | 0.84 | 20.81 | 108000 | 41.3% | 51.1% | Advanced |
| 7 | gpt-4.1-nano | 23.15 | 0.85 | 20.60 | 108000 | 39.9% | 73.5% | Advanced |
| 8 | gpt-4o | 19.37 | 0.88 | 16.72 | 108000 | 21.0% | 72.8% | Intermediate |
| 9 | gpt-4o-mini | 15.70 | 0.98 | 12.77 | 108000 | 7.8% | N/A | Novice |

#### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |
|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|
| 1 | MOSES | 34.79 | 1.01 | 31.75 | 108000 | 94.0% | 89.7% | Elite |
| 2 | lightrag-4.1 | 27.14 | 0.84 | 24.63 | 108000 | 63.5% | 50.1% | Advanced |
| 3 | lightrag-4.1-nano | 27.12 | 0.83 | 24.62 | 108000 | 63.2% | 50.5% | Advanced |
| 4 | MOSES-nano | 27.05 | 0.83 | 24.57 | 108000 | 61.2% | 50.5% | Advanced |
| 5 | o3 | 26.98 | 0.82 | 24.52 | 108000 | 62.7% | 74.1% | Advanced |
| 6 | gpt-4.1 | 23.10 | 0.82 | 20.63 | 108000 | 38.9% | 53.5% | Advanced |
| 7 | gpt-4.1-nano | 22.58 | 0.82 | 20.11 | 108000 | 35.2% | 70.2% | Advanced |
| 8 | gpt-4o | 19.39 | 0.87 | 16.79 | 108000 | 20.1% | 64.2% | Intermediate |
| 9 | gpt-4o-mini | 17.19 | 0.92 | 14.44 | 108000 | 11.3% | N/A | Novice |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **29.74**

### Most Consistent Model
**MOSES-nano** shows the lowest uncertainty with σ=0.82

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Theoretical Depth | MOSES | 31.75 | 34.79 | 1.01 | 7.12 |
| Rigor And Information Density | o3 | 32.26 | 35.34 | 1.03 | 1.93 |
| Correctness | MOSES | 28.08 | 30.62 | 0.84 | 0.76 |
| Completeness | MOSES | 28.81 | 31.46 | 0.88 | 1.80 |

### Rating Distribution
- **Mean Overall ELO**: 22.57
- **ELO Std**: 4.06
- **ELO Range**: 29.74 - 15.61
- **Mean μ (Skill)**: 25.11
- **Mean σ (Uncertainty)**: 0.85
- **Models Analyzed**: 9
- **Data Source**: real
- **Total Matches (All Repetitions)**: 1,944,000
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

