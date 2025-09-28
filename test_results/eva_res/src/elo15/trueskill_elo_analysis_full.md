# TrueSkill ELO Rating Analysis (Full Analysis)

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

- **Total matches analyzed**: 17,010
- **Unique models**: 15
- **Judge models**: 1
- **Dimensions analyzed**: 6
- **Match generation**: Real question-dimension matches

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | o3 | 34.37 | 37.73 | 1.12 | weighted_mean | 6 dimensions |
| 2 | MOSES | 33.50 | 36.87 | 1.12 | weighted_mean | 6 dimensions |
| 3 | o1 | 27.95 | 30.82 | 0.96 | weighted_mean | 6 dimensions |
| 4 | gpt-4.1 | 27.72 | 30.54 | 0.94 | weighted_mean | 6 dimensions |
| 5 | lightrag-4.1 | 24.10 | 26.82 | 0.90 | weighted_mean | 6 dimensions |
| 6 | lightrag-4.1-nano | 24.04 | 26.77 | 0.91 | weighted_mean | 6 dimensions |
| 7 | gpt-4.1-nano | 23.84 | 26.55 | 0.90 | weighted_mean | 6 dimensions |
| 8 | MOSES-nano | 22.09 | 24.81 | 0.91 | weighted_mean | 6 dimensions |
| 9 | gpt-4o | 21.60 | 24.32 | 0.91 | weighted_mean | 6 dimensions |
| 10 | spark-chem13b-nothink | 20.39 | 23.11 | 0.91 | weighted_mean | 6 dimensions |
| 11 | spark-chem13b-think | 19.05 | 21.80 | 0.92 | weighted_mean | 6 dimensions |
| 12 | gpt-4o-mini | 17.45 | 20.25 | 0.93 | weighted_mean | 6 dimensions |
| 13 | darwin | 6.00 | 9.49 | 1.16 | weighted_mean | 6 dimensions |
| 14 | llasmol-top5 | 5.78 | 9.20 | 1.14 | weighted_mean | 6 dimensions |
| 15 | llasmol-top1 | 5.36 | 8.87 | 1.17 | weighted_mean | 6 dimensions |

#### Detailed Dimension Analysis for Doubao-Seed-1.6-combined

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 33.40 | 1.03 | 30.31 | 378 | 91.0% | Elite |
| 2 | o3 | 32.63 | 0.98 | 29.69 | 378 | 89.4% | Expert |
| 3 | gpt-4.1 | 26.64 | 0.86 | 24.05 | 378 | 70.4% | Advanced |
| 4 | o1 | 26.57 | 0.87 | 23.96 | 378 | 67.7% | Advanced |
| 5 | gpt-4.1-nano | 26.09 | 0.86 | 23.52 | 378 | 57.9% | Advanced |
| 6 | lightrag-4.1-nano | 24.41 | 0.86 | 21.85 | 378 | 58.2% | Advanced |
| 7 | gpt-4o | 24.13 | 0.84 | 21.60 | 378 | 48.9% | Advanced |
| 8 | lightrag-4.1 | 23.58 | 0.85 | 21.03 | 378 | 51.6% | Advanced |
| 9 | spark-chem13b-nothink | 22.63 | 0.85 | 20.07 | 378 | 46.6% | Advanced |
| 10 | spark-chem13b-think | 22.04 | 0.85 | 19.47 | 378 | 46.8% | Intermediate |
| 11 | MOSES-nano | 21.50 | 0.86 | 18.92 | 378 | 50.3% | Intermediate |
| 12 | gpt-4o-mini | 20.25 | 0.86 | 17.65 | 378 | 37.6% | Intermediate |
| 13 | llasmol-top5 | 13.03 | 0.99 | 10.06 | 378 | 13.2% | Novice |
| 14 | llasmol-top1 | 12.31 | 1.02 | 9.26 | 378 | 11.4% | Beginner |
| 15 | darwin | 12.22 | 1.05 | 9.08 | 378 | 9.0% | Beginner |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 34.77 | 1.07 | 31.56 | 378 | 93.4% | Elite |
| 2 | o3 | 32.03 | 0.95 | 29.19 | 378 | 86.0% | Expert |
| 3 | gpt-4.1 | 29.12 | 0.88 | 26.48 | 378 | 72.2% | Expert |
| 4 | lightrag-4.1 | 26.88 | 0.86 | 24.32 | 378 | 59.5% | Advanced |
| 5 | lightrag-4.1-nano | 26.60 | 0.87 | 24.01 | 378 | 63.2% | Advanced |
| 6 | spark-chem13b-nothink | 24.97 | 0.86 | 22.38 | 378 | 49.2% | Advanced |
| 7 | gpt-4.1-nano | 24.69 | 0.86 | 22.12 | 378 | 54.8% | Advanced |
| 8 | o1 | 24.33 | 0.86 | 21.74 | 378 | 57.9% | Advanced |
| 9 | gpt-4o | 23.93 | 0.86 | 21.35 | 378 | 49.2% | Advanced |
| 10 | spark-chem13b-think | 23.37 | 0.86 | 20.77 | 378 | 47.1% | Advanced |
| 11 | MOSES-nano | 22.67 | 0.87 | 20.05 | 378 | 53.2% | Advanced |
| 12 | gpt-4o-mini | 21.03 | 0.88 | 18.38 | 378 | 39.4% | Intermediate |
| 13 | llasmol-top5 | 10.31 | 1.13 | 6.91 | 378 | 9.5% | Beginner |
| 14 | llasmol-top1 | 10.07 | 1.15 | 6.61 | 378 | 8.2% | Beginner |
| 15 | darwin | 9.54 | 1.17 | 6.02 | 378 | 7.1% | Beginner |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 44.84 | 1.35 | 40.80 | 378 | 96.6% | Elite |
| 2 | MOSES | 40.96 | 1.20 | 37.36 | 378 | 93.1% | Elite |
| 3 | o1 | 34.63 | 1.03 | 31.54 | 378 | 81.5% | Elite |
| 4 | gpt-4.1 | 32.43 | 0.99 | 29.47 | 378 | 73.8% | Expert |
| 5 | lightrag-4.1-nano | 29.34 | 0.95 | 26.48 | 378 | 67.5% | Expert |
| 6 | lightrag-4.1 | 28.81 | 0.93 | 26.02 | 378 | 60.3% | Expert |
| 7 | gpt-4.1-nano | 25.79 | 0.93 | 23.00 | 378 | 54.0% | Advanced |
| 8 | MOSES-nano | 25.73 | 0.93 | 22.95 | 378 | 53.7% | Advanced |
| 9 | spark-chem13b-nothink | 23.56 | 0.93 | 20.77 | 378 | 39.2% | Advanced |
| 10 | gpt-4o | 22.06 | 0.95 | 19.21 | 378 | 39.4% | Intermediate |
| 11 | spark-chem13b-think | 22.01 | 0.96 | 19.14 | 378 | 39.7% | Intermediate |
| 12 | gpt-4o-mini | 18.32 | 1.00 | 15.31 | 378 | 28.6% | Intermediate |
| 13 | darwin | 9.22 | 1.19 | 5.64 | 378 | 10.1% | Beginner |
| 14 | llasmol-top5 | 6.90 | 1.20 | 3.30 | 378 | 7.4% | Beginner |
| 15 | llasmol-top1 | 6.61 | 1.25 | 2.87 | 378 | 5.3% | Beginner |

##### Clarity

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 42.79 | 1.25 | 39.05 | 378 | 96.0% | Elite |
| 2 | o1 | 35.62 | 1.04 | 32.51 | 378 | 84.7% | Elite |
| 3 | MOSES | 35.05 | 1.05 | 31.89 | 378 | 87.0% | Elite |
| 4 | gpt-4.1 | 34.57 | 1.01 | 31.52 | 378 | 80.2% | Elite |
| 5 | gpt-4.1-nano | 30.72 | 0.96 | 27.85 | 378 | 66.1% | Expert |
| 6 | gpt-4o | 28.77 | 0.95 | 25.93 | 378 | 58.5% | Expert |
| 7 | lightrag-4.1 | 23.62 | 0.94 | 20.80 | 378 | 47.9% | Advanced |
| 8 | lightrag-4.1-nano | 23.29 | 0.94 | 20.48 | 378 | 51.3% | Advanced |
| 9 | MOSES-nano | 23.02 | 0.93 | 20.23 | 378 | 48.9% | Advanced |
| 10 | gpt-4o-mini | 21.92 | 0.93 | 19.14 | 378 | 39.7% | Intermediate |
| 11 | spark-chem13b-nothink | 20.77 | 0.95 | 17.91 | 378 | 33.1% | Intermediate |
| 12 | spark-chem13b-think | 20.21 | 0.96 | 17.33 | 378 | 32.5% | Intermediate |
| 13 | llasmol-top5 | 8.74 | 1.15 | 5.28 | 378 | 9.0% | Beginner |
| 14 | darwin | 8.78 | 1.17 | 5.27 | 378 | 9.3% | Beginner |
| 15 | llasmol-top1 | 7.25 | 1.20 | 3.64 | 378 | 5.8% | Beginner |

##### Logic

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 41.87 | 1.27 | 38.06 | 378 | 96.3% | Elite |
| 2 | MOSES | 36.14 | 1.08 | 32.91 | 378 | 88.9% | Elite |
| 3 | o1 | 34.88 | 1.02 | 31.81 | 378 | 83.1% | Elite |
| 4 | gpt-4.1 | 33.62 | 1.00 | 30.61 | 378 | 79.4% | Elite |
| 5 | gpt-4.1-nano | 27.55 | 0.91 | 24.82 | 378 | 58.7% | Advanced |
| 6 | gpt-4o | 25.33 | 0.90 | 22.62 | 378 | 48.4% | Advanced |
| 7 | lightrag-4.1 | 25.19 | 0.91 | 22.45 | 378 | 52.9% | Advanced |
| 8 | lightrag-4.1-nano | 25.20 | 0.92 | 22.43 | 378 | 58.7% | Advanced |
| 9 | MOSES-nano | 23.72 | 0.91 | 20.98 | 378 | 49.2% | Advanced |
| 10 | spark-chem13b-nothink | 22.83 | 0.92 | 20.08 | 378 | 38.9% | Advanced |
| 11 | spark-chem13b-think | 20.69 | 0.94 | 17.87 | 378 | 36.0% | Intermediate |
| 12 | gpt-4o-mini | 20.43 | 0.94 | 17.62 | 378 | 35.2% | Intermediate |
| 13 | darwin | 9.30 | 1.17 | 5.79 | 378 | 9.5% | Beginner |
| 14 | llasmol-top5 | 8.81 | 1.16 | 5.34 | 378 | 8.7% | Beginner |
| 15 | llasmol-top1 | 8.09 | 1.20 | 4.50 | 378 | 6.1% | Beginner |

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 40.88 | 1.30 | 36.98 | 378 | 97.6% | Elite |
| 2 | lightrag-4.1 | 32.83 | 0.94 | 30.00 | 378 | 77.2% | Expert |
| 3 | o3 | 32.21 | 0.92 | 29.45 | 378 | 75.7% | Expert |
| 4 | MOSES-nano | 32.22 | 0.94 | 29.41 | 378 | 74.6% | Expert |
| 5 | lightrag-4.1-nano | 31.79 | 0.93 | 28.99 | 378 | 75.9% | Expert |
| 6 | o1 | 28.87 | 0.91 | 26.14 | 378 | 66.7% | Expert |
| 7 | gpt-4.1 | 26.88 | 0.90 | 24.17 | 378 | 56.3% | Advanced |
| 8 | gpt-4.1-nano | 24.46 | 0.91 | 21.72 | 378 | 51.1% | Advanced |
| 9 | spark-chem13b-nothink | 23.89 | 0.93 | 21.12 | 378 | 40.7% | Advanced |
| 10 | spark-chem13b-think | 22.47 | 0.93 | 19.69 | 378 | 41.0% | Intermediate |
| 11 | gpt-4o | 21.72 | 0.94 | 18.90 | 378 | 39.4% | Intermediate |
| 12 | gpt-4o-mini | 19.55 | 0.98 | 16.62 | 378 | 31.0% | Intermediate |
| 13 | llasmol-top1 | 8.91 | 1.21 | 5.27 | 378 | 7.9% | Beginner |
| 14 | darwin | 7.86 | 1.23 | 4.18 | 378 | 7.7% | Beginner |
| 15 | llasmol-top5 | 7.42 | 1.22 | 3.77 | 378 | 7.1% | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**o3** achieves the highest overall ELO rating of **34.37**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.90

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Correctness | MOSES | 30.31 | 33.40 | 1.03 | 0.62 |
| Completeness | MOSES | 31.56 | 34.77 | 1.07 | 2.37 |
| Rigor And Information Density | o3 | 40.80 | 44.84 | 1.35 | 3.44 |
| Clarity | o3 | 39.05 | 42.79 | 1.25 | 6.54 |
| Logic | o3 | 38.06 | 41.87 | 1.27 | 5.15 |
| Theoretical Depth | MOSES | 36.98 | 40.88 | 1.30 | 6.98 |

### Rating Distribution
- **Mean Overall ELO**: 20.88
- **ELO Std**: 8.85
- **ELO Range**: 34.37 - 5.36
- **Mean μ (Skill)**: 23.86
- **Mean σ (Uncertainty)**: 0.99
- **Models Analyzed**: 15
- **Data Source**: real
- **Total Matches**: 17,010
- **Matches per Dimension**: 2,835

### Aggregation Method Details

**Weighted Mean Aggregation**:
- Overall ELO = Σ(dimension_rating × games_played) / Σ(games_played)
- Overall μ = Σ(dimension_μ × games_played) / Σ(games_played)
- Overall σ = Σ(dimension_σ × games_played) / Σ(games_played)
- Weights based on number of matches per dimension
- More reliable dimensions (more matches) have higher influence

