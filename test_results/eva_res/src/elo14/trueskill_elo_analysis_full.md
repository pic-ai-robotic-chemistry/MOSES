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

- **Total matches analyzed**: 29,484
- **Unique models**: 14
- **Judge models**: 2
- **Dimensions analyzed**: 6
- **Match generation**: Real question-dimension matches

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | MOSES | 34.13 | 37.40 | 1.09 | weighted_mean | 6 dimensions |
| 2 | o3 | 33.93 | 37.22 | 1.10 | weighted_mean | 6 dimensions |
| 3 | o1 | 27.52 | 30.31 | 0.93 | weighted_mean | 6 dimensions |
| 4 | gpt-4.1 | 27.21 | 29.95 | 0.91 | weighted_mean | 6 dimensions |
| 5 | lightrag-4.1-nano | 25.17 | 27.85 | 0.89 | weighted_mean | 6 dimensions |
| 6 | MOSES-nano | 23.87 | 26.51 | 0.88 | weighted_mean | 6 dimensions |
| 7 | lightrag-4.1 | 23.06 | 25.72 | 0.89 | weighted_mean | 6 dimensions |
| 8 | gpt-4.1-nano | 22.95 | 25.58 | 0.88 | weighted_mean | 6 dimensions |
| 9 | gpt-4o | 20.09 | 22.76 | 0.89 | weighted_mean | 6 dimensions |
| 10 | spark-chem13b-think | 20.02 | 22.70 | 0.90 | weighted_mean | 6 dimensions |
| 11 | spark-chem13b-nothink | 19.95 | 22.63 | 0.89 | weighted_mean | 6 dimensions |
| 12 | gpt-4o-mini | 16.88 | 19.66 | 0.93 | weighted_mean | 6 dimensions |
| 13 | llasmol-top5 | 6.97 | 10.65 | 1.23 | weighted_mean | 6 dimensions |
| 14 | llasmol-top1 | 6.02 | 9.79 | 1.26 | weighted_mean | 6 dimensions |

#### Detailed Dimension Analysis for Doubao-Seed-1.6-combined

##### Logic

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 41.09 | 1.24 | 37.38 | 351 | 96.0% | Elite |
| 2 | MOSES | 35.87 | 1.04 | 32.74 | 351 | 87.5% | Elite |
| 3 | o1 | 33.05 | 0.99 | 30.09 | 351 | 81.5% | Elite |
| 4 | gpt-4.1 | 31.43 | 0.96 | 28.56 | 351 | 77.5% | Expert |
| 5 | lightrag-4.1-nano | 26.50 | 0.91 | 23.78 | 351 | 55.6% | Advanced |
| 6 | gpt-4.1-nano | 26.24 | 0.89 | 23.56 | 351 | 56.7% | Advanced |
| 7 | MOSES-nano | 24.44 | 0.88 | 21.80 | 351 | 45.3% | Advanced |
| 8 | lightrag-4.1 | 23.81 | 0.90 | 21.12 | 351 | 49.0% | Advanced |
| 9 | gpt-4o | 22.86 | 0.89 | 20.20 | 351 | 45.6% | Advanced |
| 10 | spark-chem13b-nothink | 21.85 | 0.91 | 19.14 | 351 | 34.5% | Intermediate |
| 11 | spark-chem13b-think | 19.85 | 0.92 | 17.07 | 351 | 30.8% | Intermediate |
| 12 | gpt-4o-mini | 18.40 | 0.94 | 15.59 | 351 | 29.3% | Intermediate |
| 13 | llasmol-top5 | 10.11 | 1.22 | 6.45 | 351 | 7.4% | Beginner |
| 14 | llasmol-top1 | 8.41 | 1.33 | 4.42 | 351 | 3.4% | Beginner |

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 33.83 | 0.96 | 30.96 | 351 | 88.9% | Elite |
| 2 | o3 | 32.77 | 0.95 | 29.93 | 351 | 88.6% | Expert |
| 3 | gpt-4.1 | 27.64 | 0.84 | 25.11 | 351 | 70.1% | Expert |
| 4 | lightrag-4.1-nano | 26.99 | 0.84 | 24.48 | 351 | 55.6% | Advanced |
| 5 | o1 | 26.43 | 0.83 | 23.94 | 351 | 65.2% | Advanced |
| 6 | spark-chem13b-nothink | 25.54 | 0.83 | 23.06 | 351 | 42.7% | Advanced |
| 7 | MOSES-nano | 25.23 | 0.83 | 22.74 | 351 | 46.7% | Advanced |
| 8 | spark-chem13b-think | 25.10 | 0.83 | 22.62 | 351 | 42.5% | Advanced |
| 9 | gpt-4.1-nano | 24.86 | 0.83 | 22.38 | 351 | 54.7% | Advanced |
| 10 | lightrag-4.1 | 24.07 | 0.83 | 21.58 | 351 | 48.4% | Advanced |
| 11 | gpt-4o | 22.67 | 0.84 | 20.15 | 351 | 44.4% | Advanced |
| 12 | gpt-4o-mini | 21.03 | 0.86 | 18.45 | 351 | 33.3% | Intermediate |
| 13 | llasmol-top5 | 17.23 | 0.98 | 14.29 | 351 | 9.1% | Novice |
| 14 | llasmol-top1 | 16.52 | 0.99 | 13.57 | 351 | 9.7% | Novice |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 43.85 | 1.33 | 39.86 | 351 | 96.6% | Elite |
| 2 | MOSES | 41.05 | 1.17 | 37.54 | 351 | 92.3% | Elite |
| 3 | o1 | 34.29 | 1.00 | 31.28 | 351 | 80.3% | Elite |
| 4 | gpt-4.1 | 31.98 | 0.96 | 29.10 | 351 | 71.5% | Expert |
| 5 | lightrag-4.1-nano | 30.03 | 0.94 | 27.20 | 351 | 65.0% | Expert |
| 6 | lightrag-4.1 | 27.38 | 0.92 | 24.62 | 351 | 57.5% | Advanced |
| 7 | MOSES-nano | 26.72 | 0.90 | 24.01 | 351 | 50.1% | Advanced |
| 8 | gpt-4.1-nano | 25.74 | 0.91 | 23.02 | 351 | 50.7% | Advanced |
| 9 | spark-chem13b-think | 22.60 | 0.94 | 19.78 | 351 | 34.8% | Intermediate |
| 10 | spark-chem13b-nothink | 21.81 | 0.94 | 19.01 | 351 | 33.9% | Intermediate |
| 11 | gpt-4o | 21.06 | 0.94 | 18.24 | 351 | 34.8% | Intermediate |
| 12 | gpt-4o-mini | 17.56 | 1.00 | 14.55 | 351 | 23.4% | Novice |
| 13 | llasmol-top5 | 8.96 | 1.30 | 5.07 | 351 | 5.4% | Beginner |
| 14 | llasmol-top1 | 7.28 | 1.33 | 3.28 | 351 | 3.7% | Beginner |

##### Clarity

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 41.81 | 1.25 | 38.05 | 351 | 96.3% | Elite |
| 2 | MOSES | 35.77 | 1.03 | 32.67 | 351 | 85.5% | Elite |
| 3 | o1 | 34.56 | 1.03 | 31.47 | 351 | 84.0% | Elite |
| 4 | gpt-4.1 | 33.29 | 1.00 | 30.31 | 351 | 78.3% | Elite |
| 5 | gpt-4.1-nano | 27.35 | 0.91 | 24.61 | 351 | 63.8% | Advanced |
| 6 | lightrag-4.1-nano | 25.04 | 0.92 | 22.27 | 351 | 48.1% | Advanced |
| 7 | gpt-4o | 24.51 | 0.90 | 21.80 | 351 | 54.4% | Advanced |
| 8 | MOSES-nano | 24.37 | 0.91 | 21.64 | 351 | 44.7% | Advanced |
| 9 | lightrag-4.1 | 22.78 | 0.91 | 20.04 | 351 | 44.4% | Advanced |
| 10 | gpt-4o-mini | 19.43 | 0.92 | 16.66 | 351 | 34.8% | Intermediate |
| 11 | spark-chem13b-nothink | 18.77 | 0.94 | 15.94 | 351 | 27.6% | Intermediate |
| 12 | spark-chem13b-think | 18.65 | 0.94 | 15.82 | 351 | 27.1% | Intermediate |
| 13 | llasmol-top5 | 9.13 | 1.25 | 5.38 | 351 | 6.3% | Beginner |
| 14 | llasmol-top1 | 8.11 | 1.25 | 4.36 | 351 | 4.6% | Beginner |

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 42.23 | 1.29 | 38.36 | 351 | 97.4% | Elite |
| 2 | MOSES-nano | 32.67 | 0.91 | 29.93 | 351 | 72.9% | Expert |
| 3 | o3 | 31.67 | 0.89 | 29.00 | 351 | 73.8% | Expert |
| 4 | lightrag-4.1 | 31.28 | 0.92 | 28.53 | 351 | 75.8% | Expert |
| 5 | lightrag-4.1-nano | 30.97 | 0.90 | 28.25 | 351 | 74.1% | Expert |
| 6 | o1 | 29.26 | 0.88 | 26.62 | 351 | 63.8% | Expert |
| 7 | gpt-4.1 | 27.21 | 0.87 | 24.58 | 351 | 53.0% | Advanced |
| 8 | gpt-4.1-nano | 24.76 | 0.89 | 22.09 | 351 | 47.0% | Advanced |
| 9 | spark-chem13b-think | 24.73 | 0.89 | 22.05 | 351 | 37.3% | Advanced |
| 10 | spark-chem13b-nothink | 23.49 | 0.90 | 20.77 | 351 | 36.2% | Advanced |
| 11 | gpt-4o | 22.20 | 0.92 | 19.44 | 351 | 34.8% | Intermediate |
| 12 | gpt-4o-mini | 19.66 | 0.97 | 16.76 | 351 | 25.6% | Intermediate |
| 13 | llasmol-top5 | 7.86 | 1.37 | 3.74 | 351 | 4.6% | Beginner |
| 14 | llasmol-top1 | 6.99 | 1.41 | 2.75 | 351 | 3.7% | Beginner |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 35.67 | 1.06 | 32.49 | 351 | 93.2% | Elite |
| 2 | o3 | 32.12 | 0.93 | 29.34 | 351 | 84.9% | Expert |
| 3 | gpt-4.1 | 28.15 | 0.85 | 25.60 | 351 | 69.2% | Expert |
| 4 | lightrag-4.1-nano | 27.58 | 0.85 | 25.02 | 351 | 60.1% | Expert |
| 5 | MOSES-nano | 25.63 | 0.85 | 23.10 | 351 | 49.6% | Advanced |
| 6 | spark-chem13b-think | 25.30 | 0.84 | 22.77 | 351 | 42.7% | Advanced |
| 7 | lightrag-4.1 | 24.97 | 0.84 | 22.45 | 351 | 56.4% | Advanced |
| 8 | gpt-4.1-nano | 24.55 | 0.84 | 22.04 | 351 | 51.9% | Advanced |
| 9 | spark-chem13b-nothink | 24.29 | 0.84 | 21.77 | 351 | 45.3% | Advanced |
| 10 | o1 | 24.25 | 0.84 | 21.72 | 351 | 54.7% | Advanced |
| 11 | gpt-4o | 23.26 | 0.84 | 20.73 | 351 | 45.6% | Advanced |
| 12 | gpt-4o-mini | 21.88 | 0.87 | 19.28 | 351 | 35.6% | Intermediate |
| 13 | llasmol-top1 | 11.44 | 1.24 | 7.73 | 351 | 5.7% | Beginner |
| 14 | llasmol-top5 | 10.64 | 1.25 | 6.88 | 351 | 5.1% | Beginner |


### Judge: fxx_gemini2.5-pro

| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |
|------|-------|-------------|-----------|-----------|--------------------|-----------------------|
| 1 | o3 | 31.91 | 34.82 | 0.97 | weighted_mean | 6 dimensions |
| 2 | MOSES | 31.87 | 34.82 | 0.99 | weighted_mean | 6 dimensions |
| 3 | o1 | 28.32 | 31.03 | 0.90 | weighted_mean | 6 dimensions |
| 4 | gpt-4.1 | 26.58 | 29.19 | 0.87 | weighted_mean | 6 dimensions |
| 5 | lightrag-4.1-nano | 26.41 | 29.03 | 0.87 | weighted_mean | 6 dimensions |
| 6 | lightrag-4.1 | 25.87 | 28.49 | 0.87 | weighted_mean | 6 dimensions |
| 7 | MOSES-nano | 22.65 | 25.27 | 0.88 | weighted_mean | 6 dimensions |
| 8 | gpt-4.1-nano | 21.60 | 24.21 | 0.87 | weighted_mean | 6 dimensions |
| 9 | gpt-4o | 20.68 | 23.31 | 0.88 | weighted_mean | 6 dimensions |
| 10 | spark-chem13b-think | 20.64 | 23.26 | 0.88 | weighted_mean | 6 dimensions |
| 11 | spark-chem13b-nothink | 20.62 | 23.23 | 0.87 | weighted_mean | 6 dimensions |
| 12 | gpt-4o-mini | 17.59 | 20.31 | 0.91 | weighted_mean | 6 dimensions |
| 13 | llasmol-top5 | 10.07 | 13.44 | 1.12 | weighted_mean | 6 dimensions |
| 14 | llasmol-top1 | 9.40 | 12.85 | 1.15 | weighted_mean | 6 dimensions |

#### Detailed Dimension Analysis for fxx_gemini2.5-pro

##### Logic

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 33.09 | 0.93 | 30.30 | 351 | 84.9% | Elite |
| 2 | o1 | 31.77 | 0.91 | 29.04 | 351 | 78.3% | Expert |
| 3 | MOSES | 31.54 | 0.90 | 28.83 | 351 | 77.8% | Expert |
| 4 | gpt-4.1 | 30.30 | 0.88 | 27.65 | 351 | 74.6% | Expert |
| 5 | lightrag-4.1-nano | 28.83 | 0.87 | 26.22 | 351 | 65.5% | Expert |
| 6 | lightrag-4.1 | 28.82 | 0.87 | 26.19 | 351 | 65.8% | Expert |
| 7 | gpt-4.1-nano | 24.92 | 0.87 | 22.32 | 351 | 55.8% | Advanced |
| 8 | gpt-4o | 23.87 | 0.86 | 21.29 | 351 | 51.9% | Advanced |
| 9 | MOSES-nano | 22.88 | 0.89 | 20.21 | 351 | 37.0% | Advanced |
| 10 | spark-chem13b-nothink | 20.76 | 0.89 | 18.09 | 351 | 29.1% | Intermediate |
| 11 | spark-chem13b-think | 20.31 | 0.90 | 17.61 | 351 | 32.5% | Intermediate |
| 12 | gpt-4o-mini | 20.08 | 0.90 | 17.39 | 351 | 35.0% | Intermediate |
| 13 | llasmol-top5 | 11.79 | 1.19 | 8.22 | 351 | 6.8% | Beginner |
| 14 | llasmol-top1 | 10.29 | 1.22 | 6.63 | 351 | 4.8% | Beginner |

##### Correctness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 31.69 | 0.87 | 29.09 | 351 | 74.6% | Expert |
| 2 | o3 | 30.86 | 0.85 | 28.30 | 351 | 73.8% | Expert |
| 3 | o1 | 29.68 | 0.84 | 27.15 | 351 | 73.5% | Expert |
| 4 | gpt-4.1 | 28.73 | 0.83 | 26.24 | 351 | 68.4% | Expert |
| 5 | lightrag-4.1 | 27.90 | 0.83 | 25.42 | 351 | 63.5% | Expert |
| 6 | lightrag-4.1-nano | 27.25 | 0.82 | 24.79 | 351 | 60.4% | Advanced |
| 7 | gpt-4.1-nano | 26.07 | 0.82 | 23.61 | 351 | 61.0% | Advanced |
| 8 | gpt-4o | 26.02 | 0.82 | 23.57 | 351 | 55.0% | Advanced |
| 9 | MOSES-nano | 24.61 | 0.82 | 22.14 | 351 | 41.0% | Advanced |
| 10 | spark-chem13b-nothink | 23.30 | 0.83 | 20.81 | 351 | 36.2% | Advanced |
| 11 | spark-chem13b-think | 22.96 | 0.84 | 20.45 | 351 | 34.5% | Advanced |
| 12 | gpt-4o-mini | 22.06 | 0.84 | 19.54 | 351 | 34.5% | Intermediate |
| 13 | llasmol-top5 | 18.92 | 0.91 | 16.17 | 351 | 12.0% | Intermediate |
| 14 | llasmol-top1 | 17.71 | 0.93 | 14.91 | 351 | 11.7% | Novice |

##### Rigor And Information Density

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 39.56 | 1.11 | 36.23 | 351 | 94.0% | Elite |
| 2 | MOSES | 36.20 | 1.01 | 33.16 | 351 | 87.7% | Elite |
| 3 | o1 | 34.35 | 0.97 | 31.45 | 351 | 82.6% | Elite |
| 4 | lightrag-4.1-nano | 30.44 | 0.92 | 27.69 | 351 | 68.7% | Expert |
| 5 | gpt-4.1 | 30.16 | 0.89 | 27.49 | 351 | 67.2% | Expert |
| 6 | lightrag-4.1 | 29.53 | 0.91 | 26.81 | 351 | 64.7% | Expert |
| 7 | MOSES-nano | 24.63 | 0.90 | 21.93 | 351 | 45.0% | Advanced |
| 8 | gpt-4.1-nano | 23.70 | 0.90 | 21.00 | 351 | 44.2% | Advanced |
| 9 | spark-chem13b-think | 23.36 | 0.89 | 20.68 | 351 | 38.2% | Advanced |
| 10 | spark-chem13b-nothink | 22.79 | 0.90 | 20.10 | 351 | 33.9% | Advanced |
| 11 | gpt-4o | 22.31 | 0.90 | 19.60 | 351 | 36.2% | Intermediate |
| 12 | gpt-4o-mini | 19.50 | 0.94 | 16.68 | 351 | 26.5% | Intermediate |
| 13 | llasmol-top5 | 12.62 | 1.14 | 9.20 | 351 | 7.7% | Beginner |
| 14 | llasmol-top1 | 9.87 | 1.28 | 6.03 | 351 | 3.4% | Beginner |

##### Clarity

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | o3 | 33.03 | 0.97 | 30.13 | 351 | 89.2% | Elite |
| 2 | o1 | 32.51 | 0.93 | 29.72 | 351 | 84.0% | Expert |
| 3 | MOSES | 30.55 | 0.89 | 27.87 | 351 | 79.2% | Expert |
| 4 | gpt-4.1 | 27.98 | 0.86 | 25.42 | 351 | 68.4% | Expert |
| 5 | lightrag-4.1-nano | 26.64 | 0.84 | 24.11 | 351 | 60.1% | Advanced |
| 6 | lightrag-4.1 | 25.75 | 0.84 | 23.22 | 351 | 57.3% | Advanced |
| 7 | gpt-4o | 24.06 | 0.84 | 21.55 | 351 | 53.0% | Advanced |
| 8 | spark-chem13b-nothink | 23.38 | 0.85 | 20.84 | 351 | 37.9% | Advanced |
| 9 | gpt-4.1-nano | 23.02 | 0.84 | 20.49 | 351 | 47.3% | Advanced |
| 10 | spark-chem13b-think | 22.04 | 0.85 | 19.49 | 351 | 36.5% | Intermediate |
| 11 | MOSES-nano | 21.41 | 0.87 | 18.80 | 351 | 32.8% | Intermediate |
| 12 | gpt-4o-mini | 19.85 | 0.87 | 17.24 | 351 | 34.5% | Intermediate |
| 13 | llasmol-top1 | 17.50 | 0.92 | 14.74 | 351 | 12.0% | Novice |
| 14 | llasmol-top5 | 15.48 | 1.04 | 12.35 | 351 | 8.0% | Novice |

##### Theoretical Depth

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 41.77 | 1.19 | 38.20 | 351 | 94.6% | Elite |
| 2 | o3 | 38.31 | 1.02 | 35.26 | 351 | 88.9% | Elite |
| 3 | lightrag-4.1 | 33.51 | 0.95 | 30.65 | 351 | 76.4% | Elite |
| 4 | o1 | 32.93 | 0.93 | 30.13 | 351 | 73.2% | Elite |
| 5 | lightrag-4.1-nano | 32.53 | 0.94 | 29.72 | 351 | 73.5% | Expert |
| 6 | MOSES-nano | 30.05 | 0.92 | 27.27 | 351 | 61.5% | Expert |
| 7 | gpt-4.1 | 28.13 | 0.91 | 25.40 | 351 | 54.4% | Expert |
| 8 | spark-chem13b-think | 24.58 | 0.93 | 21.79 | 351 | 39.3% | Advanced |
| 9 | spark-chem13b-nothink | 23.75 | 0.92 | 20.99 | 351 | 35.3% | Advanced |
| 10 | gpt-4.1-nano | 23.37 | 0.94 | 20.55 | 351 | 41.6% | Advanced |
| 11 | gpt-4o | 20.02 | 0.98 | 17.07 | 351 | 28.8% | Intermediate |
| 12 | gpt-4o-mini | 18.12 | 1.01 | 15.08 | 351 | 23.1% | Intermediate |
| 13 | llasmol-top5 | 8.93 | 1.26 | 5.17 | 351 | 5.7% | Beginner |
| 14 | llasmol-top1 | 8.40 | 1.34 | 4.39 | 351 | 3.7% | Beginner |

##### Completeness

| Rank | Model | μ (Skill) | σ (Uncertainty) | Rating (μ-3σ) | Games | Win Rate | Performance Level |
|------|-------|-----------|-----------------|---------------|-------|----------|-------------------|
| 1 | MOSES | 37.20 | 1.05 | 34.06 | 351 | 91.5% | Elite |
| 2 | o3 | 34.06 | 0.95 | 31.22 | 351 | 86.6% | Elite |
| 3 | gpt-4.1 | 29.84 | 0.86 | 27.25 | 351 | 71.5% | Expert |
| 4 | lightrag-4.1-nano | 28.47 | 0.85 | 25.92 | 351 | 61.5% | Expert |
| 5 | MOSES-nano | 28.07 | 0.85 | 25.52 | 351 | 53.8% | Expert |
| 6 | spark-chem13b-think | 26.33 | 0.85 | 23.78 | 351 | 45.9% | Advanced |
| 7 | lightrag-4.1 | 25.44 | 0.84 | 22.91 | 351 | 54.7% | Advanced |
| 8 | spark-chem13b-nothink | 25.42 | 0.85 | 22.88 | 351 | 45.6% | Advanced |
| 9 | o1 | 24.93 | 0.84 | 22.40 | 351 | 51.9% | Advanced |
| 10 | gpt-4.1-nano | 24.18 | 0.85 | 21.63 | 351 | 47.0% | Advanced |
| 11 | gpt-4o | 23.55 | 0.85 | 21.00 | 351 | 43.6% | Advanced |
| 12 | gpt-4o-mini | 22.23 | 0.87 | 19.63 | 351 | 35.0% | Intermediate |
| 13 | llasmol-top1 | 13.30 | 1.19 | 9.72 | 351 | 5.4% | Beginner |
| 14 | llasmol-top5 | 12.87 | 1.19 | 9.30 | 351 | 6.0% | Beginner |


## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest overall ELO rating of **34.13**

### Most Consistent Model
**gpt-4.1-nano** shows the lowest uncertainty with σ=0.87

### Dimension Performance Summary

| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |
|-----------|-----------|------------|-----------|-----------------|------------------|
| Logic | o3 | 37.38 | 41.09 | 1.24 | 4.64 |
| Correctness | MOSES | 30.96 | 33.83 | 0.96 | 1.03 |
| Rigor And Information Density | o3 | 39.86 | 43.85 | 1.33 | 2.32 |
| Clarity | o3 | 38.05 | 41.81 | 1.25 | 5.38 |
| Theoretical Depth | MOSES | 38.36 | 42.23 | 1.29 | 0.17 |
| Completeness | MOSES | 34.06 | 37.20 | 1.05 | 1.58 |

### Rating Distribution
- **Mean Overall ELO**: 22.21
- **ELO Std**: 7.31
- **ELO Range**: 34.13 - 6.02
- **Mean μ (Skill)**: 25.07
- **Mean σ (Uncertainty)**: 0.95
- **Models Analyzed**: 14
- **Data Source**: real
- **Total Matches**: 29,484
- **Matches per Dimension**: 4,914

### Aggregation Method Details

**Weighted Mean Aggregation**:
- Overall ELO = Σ(dimension_rating × games_played) / Σ(games_played)
- Overall μ = Σ(dimension_μ × games_played) / Σ(games_played)
- Overall σ = Σ(dimension_σ × games_played) / Σ(games_played)
- Weights based on number of matches per dimension
- More reliable dimensions (more matches) have higher influence

