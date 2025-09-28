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
- **Draw probability**: 10.00%
- **Total matches analyzed**: 1,820
- **Simulation used**: Yes

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | TrueSkill Rating | μ (Skill) | σ (Uncertainty) | Games | Win Rate | Performance Level |
|------|-------|------------------|-----------|-----------------|-------|----------|-------------------|
| 1 | MOSES | 27.34 | 30.58 | 1.08 | 130 | 87.7% | Expert |
| 2 | o3 | 26.57 | 29.53 | 0.99 | 130 | 82.3% | Expert |
| 3 | gpt-4.1 | 23.75 | 26.85 | 1.03 | 130 | 73.1% | Advanced |
| 4 | lightrag-4.1-nano | 22.42 | 25.15 | 0.91 | 130 | 64.6% | Advanced |
| 5 | gpt-4.1-nano | 21.34 | 24.09 | 0.92 | 130 | 57.7% | Advanced |
| 6 | o1 | 21.22 | 23.91 | 0.90 | 130 | 55.4% | Advanced |
| 7 | MOSES-nano | 20.91 | 23.62 | 0.91 | 130 | 53.8% | Advanced |
| 8 | lightrag-4.1 | 20.47 | 23.15 | 0.89 | 130 | 56.2% | Advanced |
| 9 | gpt-4o | 19.22 | 21.95 | 0.91 | 130 | 47.7% | Intermediate |
| 10 | spark-chem13b-think | 17.73 | 20.48 | 0.92 | 130 | 40.8% | Intermediate |
| 11 | spark-chem13b-nothink | 17.31 | 20.11 | 0.94 | 130 | 37.7% | Intermediate |
| 12 | gpt-4o-mini | 15.80 | 18.58 | 0.93 | 130 | 34.6% | Intermediate |
| 13 | llasmol-top1 | 4.35 | 8.69 | 1.45 | 130 | 4.6% | Beginner |
| 14 | llasmol-top5 | 3.65 | 8.09 | 1.48 | 130 | 3.8% | Beginner |

### Judge: fxx_gemini2.5-pro

| Rank | Model | TrueSkill Rating | μ (Skill) | σ (Uncertainty) | Games | Win Rate | Performance Level |
|------|-------|------------------|-----------|-----------------|-------|----------|-------------------|
| 1 | MOSES | 26.38 | 29.49 | 1.04 | 130 | 81.5% | Expert |
| 2 | o3 | 26.26 | 29.29 | 1.01 | 130 | 83.1% | Expert |
| 3 | lightrag-4.1 | 23.86 | 26.71 | 0.95 | 130 | 67.7% | Advanced |
| 4 | lightrag-4.1-nano | 23.85 | 26.63 | 0.93 | 130 | 66.2% | Advanced |
| 5 | o1 | 23.84 | 26.63 | 0.93 | 130 | 69.2% | Advanced |
| 6 | gpt-4.1 | 22.53 | 25.61 | 1.03 | 130 | 63.1% | Advanced |
| 7 | gpt-4.1-nano | 20.70 | 23.60 | 0.96 | 130 | 53.8% | Advanced |
| 8 | gpt-4o | 20.61 | 23.41 | 0.93 | 130 | 50.0% | Advanced |
| 9 | MOSES-nano | 19.80 | 22.52 | 0.91 | 130 | 48.5% | Intermediate |
| 10 | spark-chem13b-nothink | 18.53 | 21.28 | 0.92 | 130 | 40.0% | Intermediate |
| 11 | spark-chem13b-think | 16.76 | 19.61 | 0.95 | 130 | 32.3% | Intermediate |
| 12 | gpt-4o-mini | 16.54 | 19.39 | 0.95 | 130 | 33.8% | Intermediate |
| 13 | llasmol-top5 | 6.21 | 10.16 | 1.32 | 130 | 6.2% | Beginner |
| 14 | llasmol-top1 | 4.63 | 8.77 | 1.38 | 130 | 4.6% | Beginner |

## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest TrueSkill rating of **27.34** (μ=30.58, σ=1.08)

### Most Consistent Model
**lightrag-4.1** shows the lowest uncertainty with σ=0.89

### Rating Distribution
- **Mean Rating**: 19.02
- **Rating Std**: 6.60
- **Rating Range**: 27.34 - 3.65
- **Models Analyzed**: 14

