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
- **β (skill gap)**: 4.167
- **τ (dynamics)**: 0.083
- **Draw probability**: 5.00%

### Match Statistics

- **Total matches analyzed**: 11,340
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | MOSES | 33.94 | 37.38 | 1.14 | weighted_mean | 4 dimensions |
| 2 | o3 | 32.10 | 35.21 | 1.04 | weighted_mean | 4 dimensions |
| 3 | gpt-4.1 | 26.11 | 28.83 | 0.91 | weighted_mean | 4 dimensions |
| 4 | o1 | 25.77 | 28.52 | 0.92 | weighted_mean | 4 dimensions |
| 5 | lightrag-4.1 | 25.44 | 28.12 | 0.89 | weighted_mean | 4 dimensions |
| 6 | lightrag-4.1-nano | 25.32 | 28.01 | 0.90 | weighted_mean | 4 dimensions |
| 7 | MOSES-nano | 22.86 | 25.55 | 0.90 | weighted_mean | 4 dimensions |
| 8 | gpt-4.1-nano | 22.63 | 25.29 | 0.89 | weighted_mean | 4 dimensions |
| 9 | spark-chem13b-nothink | 21.11 | 23.79 | 0.89 | weighted_mean | 4 dimensions |
| 10 | gpt-4o | 20.12 | 22.81 | 0.90 | weighted_mean | 4 dimensions |
| 11 | spark-chem13b-think | 19.82 | 22.52 | 0.90 | weighted_mean | 4 dimensions |
| 12 | gpt-4o-mini | 16.97 | 19.77 | 0.93 | weighted_mean | 4 dimensions |
| 13 | llasmol-top1 | 6.72 | 10.15 | 1.14 | weighted_mean | 4 dimensions |
| 14 | darwin | 6.36 | 9.81 | 1.15 | weighted_mean | 4 dimensions |
| 15 | llasmol-top5 | 5.81 | 9.24 | 1.14 | weighted_mean | 4 dimensions |

#### Detailed Dimension Analysis for Doubao-Seed-1.6-combined

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 33.18 | 1.01 | 30.14 | 378 | 90.7% | Elite |
| 2 | o3 | 32.25 | 0.96 | 29.37 | 378 | 88.4% | Expert |
| 3 | gpt-4.1 | 26.92 | 0.86 | 24.34 | 378 | 70.9% | Advanced |
| 4 | o1 | 26.64 | 0.87 | 24.05 | 378 | 68.0% | Advanced |
| 5 | gpt-4.1-nano | 26.25 | 0.86 | 23.68 | 378 | 58.2% | Advanced |
| 6 | lightrag-4.1-nano | 24.48 | 0.85 | 21.93 | 378 | 58.2% | Advanced |
| 7 | lightrag-4.1 | 23.92 | 0.85 | 21.37 | 378 | 52.6% | Advanced |
| 8 | gpt-4o | 23.85 | 0.84 | 21.33 | 378 | 47.4% | Advanced |
| 9 | spark-chem13b-nothink | 22.70 | 0.85 | 20.15 | 378 | 46.6% | Advanced |
| 10 | spark-chem13b-think | 22.11 | 0.85 | 19.55 | 378 | 46.8% | Intermediate |
| 11 | MOSES-nano | 21.59 | 0.86 | 19.02 | 378 | 50.5% | Intermediate |
| 12 | gpt-4o-mini | 20.39 | 0.86 | 17.81 | 378 | 37.8% | Intermediate |
| 13 | llasmol-top5 | 13.06 | 0.99 | 10.09 | 378 | 13.0% | Novice |
| 14 | llasmol-top1 | 12.51 | 1.02 | 9.46 | 378 | 10.8% | Beginner |
| 15 | darwin | 12.51 | 1.04 | 9.40 | 378 | 10.1% | Beginner |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 34.60 | 1.07 | 31.39 | 378 | 93.4% | Elite |
| 2 | o3 | 31.87 | 0.94 | 29.04 | 378 | 86.0% | Expert |
| 3 | gpt-4.1 | 28.88 | 0.88 | 26.25 | 378 | 71.7% | Expert |
| 4 | lightrag-4.1 | 26.79 | 0.85 | 24.22 | 378 | 59.5% | Advanced |
| 5 | lightrag-4.1-nano | 26.47 | 0.86 | 23.88 | 378 | 63.2% | Advanced |
| 6 | spark-chem13b-nothink | 24.86 | 0.86 | 22.28 | 378 | 49.2% | Advanced |
| 7 | gpt-4.1-nano | 24.53 | 0.85 | 21.96 | 378 | 54.5% | Advanced |
| 8 | o1 | 24.19 | 0.86 | 21.61 | 378 | 57.7% | Advanced |
| 9 | gpt-4o | 23.89 | 0.86 | 21.32 | 378 | 49.7% | Advanced |
| 10 | spark-chem13b-think | 23.42 | 0.86 | 20.83 | 378 | 46.8% | Advanced |
| 11 | MOSES-nano | 22.56 | 0.87 | 19.96 | 378 | 53.2% | Intermediate |
| 12 | gpt-4o-mini | 20.76 | 0.88 | 18.12 | 378 | 39.4% | Intermediate |
| 13 | llasmol-top1 | 11.83 | 1.11 | 8.51 | 378 | 10.8% | Beginner |
| 14 | darwin | 9.85 | 1.17 | 6.35 | 378 | 7.1% | Beginner |
| 15 | llasmol-top5 | 9.20 | 1.14 | 5.77 | 378 | 7.7% | Beginner |

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 40.95 | 1.30 | 37.04 | 378 | 97.6% | Elite |
| 2 | lightrag-4.1 | 32.88 | 0.94 | 30.04 | 378 | 77.5% | Elite |
| 3 | o3 | 32.24 | 0.92 | 29.48 | 378 | 75.7% | Expert |
| 4 | MOSES-nano | 32.27 | 0.94 | 29.46 | 378 | 74.9% | Expert |
| 5 | lightrag-4.1-nano | 31.82 | 0.93 | 29.02 | 378 | 75.9% | Expert |
| 6 | o1 | 28.67 | 0.91 | 25.95 | 378 | 66.1% | Expert |
| 7 | gpt-4.1 | 27.10 | 0.90 | 24.40 | 378 | 56.3% | Advanced |
| 8 | gpt-4.1-nano | 24.54 | 0.91 | 21.81 | 378 | 51.6% | Advanced |
| 9 | spark-chem13b-nothink | 23.99 | 0.93 | 21.21 | 378 | 40.2% | Advanced |
| 10 | spark-chem13b-think | 22.48 | 0.93 | 19.71 | 378 | 41.3% | Intermediate |
| 11 | gpt-4o | 21.41 | 0.94 | 18.59 | 378 | 38.6% | Intermediate |
| 12 | gpt-4o-mini | 19.56 | 0.98 | 16.64 | 378 | 31.0% | Intermediate |
| 13 | llasmol-top1 | 9.25 | 1.21 | 5.62 | 378 | 7.9% | Beginner |
| 14 | darwin | 7.87 | 1.19 | 4.28 | 378 | 8.7% | Beginner |
| 15 | llasmol-top5 | 7.95 | 1.23 | 4.26 | 378 | 6.6% | Beginner |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 44.49 | 1.32 | 40.52 | 378 | 96.3% | Elite |
| 2 | MOSES | 40.77 | 1.19 | 37.20 | 378 | 93.1% | Elite |
| 3 | o1 | 34.56 | 1.03 | 31.48 | 378 | 81.5% | Elite |
| 4 | gpt-4.1 | 32.41 | 0.98 | 29.45 | 378 | 73.8% | Expert |
| 5 | lightrag-4.1-nano | 29.28 | 0.95 | 26.44 | 378 | 67.2% | Expert |
| 6 | lightrag-4.1 | 28.89 | 0.93 | 26.10 | 378 | 60.6% | Expert |
| 7 | gpt-4.1-nano | 25.83 | 0.93 | 23.05 | 378 | 54.2% | Advanced |
| 8 | MOSES-nano | 25.76 | 0.93 | 22.98 | 378 | 53.7% | Advanced |
| 9 | spark-chem13b-nothink | 23.60 | 0.93 | 20.81 | 378 | 39.2% | Advanced |
| 10 | gpt-4o | 22.09 | 0.95 | 19.24 | 378 | 39.4% | Intermediate |
| 11 | spark-chem13b-think | 22.05 | 0.96 | 19.18 | 378 | 39.7% | Intermediate |
| 12 | gpt-4o-mini | 18.36 | 1.01 | 15.34 | 378 | 28.6% | Intermediate |
| 13 | darwin | 9.01 | 1.20 | 5.42 | 378 | 9.8% | Beginner |
| 14 | llasmol-top1 | 6.99 | 1.23 | 3.29 | 378 | 5.8% | Beginner |
| 15 | llasmol-top5 | 6.74 | 1.21 | 3.13 | 378 | 7.1% | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **33.94**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.89

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Correctness | MOSES | 30.14 | 33.18 | 1.01 | 0.77 |
| Completeness | MOSES | 31.39 | 34.60 | 1.07 | 2.36 |
| Theoretical Depth | MOSES | 37.04 | 40.95 | 1.30 | 7.00 |
| Rigor And Information Density | o3 | 40.52 | 44.49 | 1.32 | 3.32 |

### Rating Distribution
- **Mean Overall ELO**: 20.74
- **ELO Std**: 8.37
- **ELO Range**: 33.94 - 5.81
- **Mean μ (Skill)**: 23.67
- **Mean σ (Uncertainty)**: 0.98
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 11,340
- **Matches per Dimension**: 2,835

### Aggregation Method Details

**Weighted Mean Aggregation**:
- Overall ELO = Σ(dimension_rating × games_played) / Σ(games_played)
- Overall μ = Σ(dimension_μ × games_played) / Σ(games_played)
- Overall σ = Σ(dimension_σ × games_played) / Σ(games_played)
- Weights based on number of matches per dimension
- More reliable dimensions (more matches) have higher influence

