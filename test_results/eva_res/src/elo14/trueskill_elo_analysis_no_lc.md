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

- **Total matches analyzed**: 19,656
- **Unique models**: 14
- **Judge models**: 2
- **Dimensions analyzed**: 4
- **Match generation**: Real question-dimension matches

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | MOSES | 34.73 | 38.07 | 1.11 | weighted_mean | 4 dimensions |
| 2 | o3 | 31.83 | 34.86 | 1.01 | weighted_mean | 4 dimensions |
| 3 | lightrag-4.1-nano | 26.20 | 28.85 | 0.88 | weighted_mean | 4 dimensions |
| 4 | o1 | 26.12 | 28.79 | 0.89 | weighted_mean | 4 dimensions |
| 5 | gpt-4.1 | 26.08 | 28.72 | 0.88 | weighted_mean | 4 dimensions |
| 6 | MOSES-nano | 24.94 | 27.55 | 0.87 | weighted_mean | 4 dimensions |
| 7 | lightrag-4.1 | 24.26 | 26.88 | 0.88 | weighted_mean | 4 dimensions |
| 8 | gpt-4.1-nano | 22.34 | 24.93 | 0.86 | weighted_mean | 4 dimensions |
| 9 | spark-chem13b-think | 21.85 | 24.48 | 0.88 | weighted_mean | 4 dimensions |
| 10 | spark-chem13b-nothink | 21.13 | 23.76 | 0.88 | weighted_mean | 4 dimensions |
| 11 | gpt-4o | 19.52 | 22.18 | 0.89 | weighted_mean | 4 dimensions |
| 12 | gpt-4o-mini | 17.28 | 20.05 | 0.92 | weighted_mean | 4 dimensions |
| 13 | llasmol-top5 | 7.74 | 11.38 | 1.21 | weighted_mean | 4 dimensions |
| 14 | llasmol-top1 | 6.73 | 10.46 | 1.24 | weighted_mean | 4 dimensions |

#### Detailed Dimension Analysis for Doubao-Seed-1.6-combined

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 42.18 | 1.29 | 38.31 | 351 | 97.4% | Elite |
| 2 | MOSES-nano | 32.62 | 0.91 | 29.88 | 351 | 72.9% | Expert |
| 3 | o3 | 31.62 | 0.89 | 28.94 | 351 | 73.8% | Expert |
| 4 | lightrag-4.1 | 31.22 | 0.92 | 28.47 | 351 | 75.5% | Expert |
| 5 | lightrag-4.1-nano | 30.88 | 0.90 | 28.17 | 351 | 73.8% | Expert |
| 6 | o1 | 29.40 | 0.88 | 26.75 | 351 | 64.4% | Expert |
| 7 | gpt-4.1 | 27.16 | 0.87 | 24.54 | 351 | 53.0% | Advanced |
| 8 | gpt-4.1-nano | 24.73 | 0.89 | 22.06 | 351 | 47.3% | Advanced |
| 9 | spark-chem13b-think | 24.65 | 0.89 | 21.97 | 351 | 36.8% | Advanced |
| 10 | spark-chem13b-nothink | 23.26 | 0.90 | 20.56 | 351 | 36.2% | Advanced |
| 11 | gpt-4o | 21.94 | 0.92 | 19.18 | 351 | 34.2% | Intermediate |
| 12 | gpt-4o-mini | 19.67 | 0.96 | 16.78 | 351 | 25.6% | Intermediate |
| 13 | llasmol-top5 | 9.17 | 1.32 | 5.23 | 351 | 6.0% | Beginner |
| 14 | llasmol-top1 | 7.67 | 1.38 | 3.54 | 351 | 3.1% | Beginner |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 43.10 | 1.28 | 39.25 | 351 | 96.0% | Elite |
| 2 | MOSES | 40.62 | 1.15 | 37.18 | 351 | 92.3% | Elite |
| 3 | o1 | 34.14 | 0.99 | 31.16 | 351 | 80.3% | Elite |
| 4 | gpt-4.1 | 31.97 | 0.96 | 29.10 | 351 | 71.8% | Expert |
| 5 | lightrag-4.1-nano | 30.16 | 0.94 | 27.34 | 351 | 65.2% | Expert |
| 6 | lightrag-4.1 | 27.29 | 0.92 | 24.54 | 351 | 57.3% | Advanced |
| 7 | MOSES-nano | 26.78 | 0.90 | 24.08 | 351 | 50.1% | Advanced |
| 8 | gpt-4.1-nano | 25.80 | 0.90 | 23.09 | 351 | 50.7% | Advanced |
| 9 | spark-chem13b-think | 22.73 | 0.94 | 19.91 | 351 | 35.0% | Intermediate |
| 10 | spark-chem13b-nothink | 21.91 | 0.93 | 19.11 | 351 | 33.9% | Intermediate |
| 11 | gpt-4o | 21.17 | 0.94 | 18.35 | 351 | 34.8% | Intermediate |
| 12 | gpt-4o-mini | 17.71 | 1.00 | 14.71 | 351 | 23.4% | Novice |
| 13 | llasmol-top5 | 8.56 | 1.30 | 4.67 | 351 | 5.1% | Beginner |
| 14 | llasmol-top1 | 8.00 | 1.33 | 4.02 | 351 | 4.0% | Beginner |

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 33.87 | 0.96 | 30.99 | 351 | 89.2% | Elite |
| 2 | o3 | 32.64 | 0.95 | 29.81 | 351 | 88.3% | Expert |
| 3 | gpt-4.1 | 27.57 | 0.84 | 25.04 | 351 | 69.5% | Expert |
| 4 | o1 | 26.91 | 0.84 | 24.40 | 351 | 67.0% | Advanced |
| 5 | lightrag-4.1-nano | 26.83 | 0.84 | 24.32 | 351 | 54.7% | Advanced |
| 6 | spark-chem13b-nothink | 25.45 | 0.83 | 22.96 | 351 | 42.2% | Advanced |
| 7 | spark-chem13b-think | 25.21 | 0.83 | 22.73 | 351 | 43.0% | Advanced |
| 8 | MOSES-nano | 25.20 | 0.83 | 22.71 | 351 | 46.7% | Advanced |
| 9 | gpt-4.1-nano | 24.66 | 0.82 | 22.19 | 351 | 54.1% | Advanced |
| 10 | lightrag-4.1 | 24.08 | 0.83 | 21.58 | 351 | 49.0% | Advanced |
| 11 | gpt-4o | 22.52 | 0.84 | 20.00 | 351 | 44.4% | Intermediate |
| 12 | gpt-4o-mini | 20.96 | 0.86 | 18.38 | 351 | 32.8% | Intermediate |
| 13 | llasmol-top5 | 17.28 | 0.96 | 14.39 | 351 | 10.8% | Novice |
| 14 | llasmol-top1 | 16.31 | 1.00 | 13.32 | 351 | 8.3% | Novice |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 35.60 | 1.05 | 32.44 | 351 | 92.9% | Elite |
| 2 | o3 | 32.09 | 0.93 | 29.31 | 351 | 84.9% | Expert |
| 3 | gpt-4.1 | 28.18 | 0.85 | 25.62 | 351 | 70.1% | Expert |
| 4 | lightrag-4.1-nano | 27.54 | 0.85 | 24.99 | 351 | 59.8% | Advanced |
| 5 | MOSES-nano | 25.61 | 0.85 | 23.07 | 351 | 49.6% | Advanced |
| 6 | spark-chem13b-think | 25.31 | 0.84 | 22.78 | 351 | 42.7% | Advanced |
| 7 | lightrag-4.1 | 24.94 | 0.84 | 22.42 | 351 | 56.4% | Advanced |
| 8 | o1 | 24.72 | 0.85 | 22.18 | 351 | 55.3% | Advanced |
| 9 | gpt-4.1-nano | 24.52 | 0.84 | 22.00 | 351 | 51.9% | Advanced |
| 10 | spark-chem13b-nothink | 24.42 | 0.84 | 21.89 | 351 | 45.3% | Advanced |
| 11 | gpt-4o | 23.10 | 0.85 | 20.56 | 351 | 45.3% | Advanced |
| 12 | gpt-4o-mini | 21.84 | 0.87 | 19.24 | 351 | 35.6% | Intermediate |
| 13 | llasmol-top5 | 10.51 | 1.28 | 6.67 | 351 | 4.8% | Beginner |
| 14 | llasmol-top1 | 9.87 | 1.27 | 6.06 | 351 | 5.4% | Beginner |


### Judge: fxx_gemini2.5-pro

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | MOSES | 33.45 | 36.53 | 1.02 | weighted_mean | 4 dimensions |
| 2 | o3 | 32.93 | 35.90 | 0.99 | weighted_mean | 4 dimensions |
| 3 | o1 | 27.72 | 30.40 | 0.89 | weighted_mean | 4 dimensions |
| 4 | lightrag-4.1-nano | 27.13 | 29.78 | 0.88 | weighted_mean | 4 dimensions |
| 5 | gpt-4.1 | 26.63 | 29.25 | 0.87 | weighted_mean | 4 dimensions |
| 6 | lightrag-4.1 | 26.52 | 29.16 | 0.88 | weighted_mean | 4 dimensions |
| 7 | MOSES-nano | 24.30 | 26.93 | 0.87 | weighted_mean | 4 dimensions |
| 8 | spark-chem13b-think | 21.68 | 24.31 | 0.88 | weighted_mean | 4 dimensions |
| 9 | gpt-4.1-nano | 21.66 | 24.28 | 0.88 | weighted_mean | 4 dimensions |
| 10 | spark-chem13b-nothink | 21.14 | 23.75 | 0.87 | weighted_mean | 4 dimensions |
| 11 | gpt-4o | 20.25 | 22.92 | 0.89 | weighted_mean | 4 dimensions |
| 12 | gpt-4o-mini | 17.72 | 20.47 | 0.92 | weighted_mean | 4 dimensions |
| 13 | llasmol-top5 | 10.45 | 13.80 | 1.11 | weighted_mean | 4 dimensions |
| 14 | llasmol-top1 | 9.15 | 12.65 | 1.17 | weighted_mean | 4 dimensions |

#### Detailed Dimension Analysis for fxx_gemini2.5-pro

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 41.39 | 1.17 | 37.86 | 351 | 94.3% | Elite |
| 2 | o3 | 38.32 | 1.02 | 35.27 | 351 | 88.9% | Elite |
| 3 | lightrag-4.1 | 33.69 | 0.95 | 30.85 | 351 | 76.4% | Elite |
| 4 | o1 | 32.95 | 0.93 | 30.15 | 351 | 73.2% | Elite |
| 5 | lightrag-4.1-nano | 32.55 | 0.94 | 29.74 | 351 | 73.5% | Expert |
| 6 | MOSES-nano | 30.14 | 0.92 | 27.36 | 351 | 61.8% | Expert |
| 7 | gpt-4.1 | 28.16 | 0.91 | 25.43 | 351 | 54.4% | Expert |
| 8 | spark-chem13b-think | 24.39 | 0.93 | 21.60 | 351 | 39.3% | Advanced |
| 9 | spark-chem13b-nothink | 23.55 | 0.91 | 20.81 | 351 | 35.0% | Advanced |
| 10 | gpt-4.1-nano | 23.39 | 0.94 | 20.57 | 351 | 41.6% | Advanced |
| 11 | gpt-4o | 20.04 | 0.98 | 17.10 | 351 | 28.8% | Intermediate |
| 12 | gpt-4o-mini | 18.14 | 1.01 | 15.09 | 351 | 23.1% | Intermediate |
| 13 | llasmol-top5 | 9.20 | 1.25 | 5.43 | 351 | 5.4% | Beginner |
| 14 | llasmol-top1 | 9.16 | 1.31 | 5.24 | 351 | 4.3% | Beginner |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 40.08 | 1.14 | 36.66 | 351 | 95.2% | Elite |
| 2 | MOSES | 35.82 | 1.01 | 32.81 | 351 | 86.3% | Elite |
| 3 | o1 | 34.44 | 0.97 | 31.54 | 351 | 82.9% | Elite |
| 4 | lightrag-4.1-nano | 30.44 | 0.92 | 27.68 | 351 | 68.7% | Expert |
| 5 | gpt-4.1 | 30.15 | 0.89 | 27.47 | 351 | 67.2% | Expert |
| 6 | lightrag-4.1 | 29.53 | 0.91 | 26.81 | 351 | 64.7% | Expert |
| 7 | MOSES-nano | 24.62 | 0.90 | 21.92 | 351 | 45.0% | Advanced |
| 8 | gpt-4.1-nano | 23.69 | 0.90 | 20.99 | 351 | 44.2% | Advanced |
| 9 | spark-chem13b-think | 23.36 | 0.89 | 20.68 | 351 | 38.2% | Advanced |
| 10 | spark-chem13b-nothink | 22.78 | 0.90 | 20.09 | 351 | 33.9% | Advanced |
| 11 | gpt-4o | 22.31 | 0.90 | 19.60 | 351 | 36.2% | Intermediate |
| 12 | gpt-4o-mini | 19.50 | 0.94 | 16.68 | 351 | 26.5% | Intermediate |
| 13 | llasmol-top5 | 12.32 | 1.15 | 8.87 | 351 | 7.1% | Beginner |
| 14 | llasmol-top1 | 10.39 | 1.25 | 6.63 | 351 | 4.0% | Beginner |

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 31.65 | 0.87 | 29.04 | 351 | 74.1% | Expert |
| 2 | o3 | 31.06 | 0.85 | 28.51 | 351 | 73.2% | Expert |
| 3 | o1 | 29.00 | 0.83 | 26.51 | 351 | 72.6% | Expert |
| 4 | gpt-4.1 | 28.86 | 0.83 | 26.38 | 351 | 70.4% | Expert |
| 5 | lightrag-4.1 | 27.93 | 0.83 | 25.45 | 351 | 63.5% | Expert |
| 6 | lightrag-4.1-nano | 27.54 | 0.82 | 25.08 | 351 | 60.1% | Expert |
| 7 | gpt-4o | 25.90 | 0.81 | 23.46 | 351 | 54.1% | Advanced |
| 8 | gpt-4.1-nano | 25.76 | 0.81 | 23.32 | 351 | 59.8% | Advanced |
| 9 | MOSES-nano | 24.84 | 0.82 | 22.38 | 351 | 41.3% | Advanced |
| 10 | spark-chem13b-nothink | 23.25 | 0.83 | 20.77 | 351 | 36.2% | Advanced |
| 11 | spark-chem13b-think | 23.11 | 0.83 | 20.62 | 351 | 34.8% | Advanced |
| 12 | gpt-4o-mini | 22.08 | 0.84 | 19.56 | 351 | 34.5% | Intermediate |
| 13 | llasmol-top5 | 19.79 | 0.89 | 17.11 | 351 | 13.1% | Intermediate |
| 14 | llasmol-top1 | 18.38 | 0.92 | 15.62 | 351 | 12.3% | Intermediate |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 37.24 | 1.05 | 34.10 | 351 | 91.5% | Elite |
| 2 | o3 | 34.14 | 0.95 | 31.30 | 351 | 86.3% | Elite |
| 3 | gpt-4.1 | 29.83 | 0.86 | 27.25 | 351 | 71.2% | Expert |
| 4 | lightrag-4.1-nano | 28.58 | 0.85 | 26.02 | 351 | 61.8% | Expert |
| 5 | MOSES-nano | 28.11 | 0.85 | 25.56 | 351 | 53.8% | Expert |
| 6 | spark-chem13b-think | 26.38 | 0.85 | 23.82 | 351 | 45.9% | Advanced |
| 7 | lightrag-4.1 | 25.48 | 0.84 | 22.95 | 351 | 54.7% | Advanced |
| 8 | spark-chem13b-nothink | 25.43 | 0.84 | 22.90 | 351 | 45.0% | Advanced |
| 9 | o1 | 25.22 | 0.84 | 22.69 | 351 | 52.7% | Advanced |
| 10 | gpt-4.1-nano | 24.28 | 0.85 | 21.74 | 351 | 47.0% | Advanced |
| 11 | gpt-4o | 23.42 | 0.85 | 20.87 | 351 | 43.3% | Advanced |
| 12 | gpt-4o-mini | 22.15 | 0.87 | 19.55 | 351 | 35.0% | Intermediate |
| 13 | llasmol-top5 | 13.88 | 1.16 | 10.40 | 351 | 6.6% | Novice |
| 14 | llasmol-top1 | 12.66 | 1.19 | 9.09 | 351 | 5.1% | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **34.73**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.86

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Theoretical Depth | MOSES | 38.31 | 42.18 | 1.29 | 0.45 |
| Rigor And Information Density | o3 | 39.25 | 43.10 | 1.28 | 2.07 |
| Correctness | MOSES | 30.99 | 33.87 | 0.96 | 1.18 |
| Completeness | MOSES | 34.10 | 37.24 | 1.05 | 1.66 |

### Rating Distribution
- **Mean Overall ELO**: 22.55
- **ELO Std**: 7.22
- **ELO Range**: 34.73 - 6.73
- **Mean μ (Skill)**: 25.40
- **Mean σ (Uncertainty)**: 0.95
- **Models Analyzed**: 14
- **Data Source**: real
- **Total Matches**: 19,656
- **Matches per Dimension**: 4,914

### Aggregation Method Details

**Weighted Mean Aggregation**:
- Overall ELO = Σ(dimension_rating × games_played) / Σ(games_played)
- Overall μ = Σ(dimension_μ × games_played) / Σ(games_played)
- Overall σ = Σ(dimension_σ × games_played) / Σ(games_played)
- Weights based on number of matches per dimension
- More reliable dimensions (more matches) have higher influence

