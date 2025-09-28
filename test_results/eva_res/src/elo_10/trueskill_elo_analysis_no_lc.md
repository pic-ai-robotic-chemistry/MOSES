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
- **Draw probability**: 10.00%
- **Total matches analyzed**: 1,820
- **Simulation used**: Yes

## TrueSkill Model Rankings

### Judge: Doubao-Seed-1.6-combined

| Rank | Model | TrueSkill Rating | μ (Skill) | σ (Uncertainty) | Games | Win Rate | Performance Level |
|------|-------|------------------|-----------|-----------------|-------|----------|-------------------|
| 1 | MOSES | 30.53 | 33.86 | 1.11 | 130 | 91.5% | Elite |
| 2 | o3 | 27.31 | 30.25 | 0.98 | 130 | 80.8% | Expert |
| 3 | lightrag-4.1-nano | 23.81 | 26.48 | 0.89 | 130 | 60.8% | Advanced |
| 4 | gpt-4.1 | 22.77 | 25.76 | 1.00 | 130 | 61.5% | Advanced |
| 5 | o1 | 22.24 | 24.90 | 0.89 | 130 | 54.6% | Advanced |
| 6 | MOSES-nano | 22.19 | 24.84 | 0.88 | 130 | 54.6% | Advanced |
| 7 | gpt-4.1-nano | 22.01 | 24.78 | 0.92 | 130 | 53.1% | Advanced |
| 8 | lightrag-4.1 | 21.89 | 24.56 | 0.89 | 130 | 56.2% | Advanced |
| 9 | gpt-4o | 21.42 | 24.11 | 0.90 | 130 | 48.5% | Advanced |
| 10 | spark-chem13b-think | 20.50 | 23.19 | 0.90 | 130 | 46.2% | Advanced |
| 11 | gpt-4o-mini | 19.32 | 22.01 | 0.90 | 130 | 41.5% | Intermediate |
| 12 | spark-chem13b-nothink | 19.27 | 22.00 | 0.91 | 130 | 39.2% | Intermediate |
| 13 | llasmol-top5 | 9.53 | 13.28 | 1.25 | 130 | 8.5% | Beginner |
| 14 | llasmol-top1 | 5.62 | 9.92 | 1.43 | 130 | 3.1% | Beginner |

### Judge: fxx_gemini2.5-pro

| Rank | Model | TrueSkill Rating | μ (Skill) | σ (Uncertainty) | Games | Win Rate | Performance Level |
|------|-------|------------------|-----------|-----------------|-------|----------|-------------------|
| 1 | MOSES | 30.70 | 33.85 | 1.05 | 130 | 87.7% | Elite |
| 2 | o3 | 29.76 | 32.72 | 0.98 | 130 | 82.3% | Expert |
| 3 | lightrag-4.1-nano | 28.21 | 31.02 | 0.94 | 130 | 76.2% | Expert |
| 4 | o1 | 25.99 | 28.72 | 0.91 | 130 | 63.8% | Expert |
| 5 | lightrag-4.1 | 24.52 | 27.21 | 0.90 | 130 | 60.0% | Advanced |
| 6 | gpt-4.1 | 24.49 | 27.61 | 1.04 | 130 | 58.5% | Advanced |
| 7 | MOSES-nano | 22.94 | 25.66 | 0.91 | 130 | 52.3% | Advanced |
| 8 | spark-chem13b-think | 22.60 | 25.29 | 0.90 | 130 | 46.9% | Advanced |
| 9 | gpt-4.1-nano | 21.80 | 24.62 | 0.94 | 130 | 49.2% | Advanced |
| 10 | spark-chem13b-nothink | 21.72 | 24.45 | 0.91 | 130 | 40.0% | Advanced |
| 11 | gpt-4o | 19.11 | 21.95 | 0.95 | 130 | 35.4% | Intermediate |
| 12 | gpt-4o-mini | 18.30 | 21.10 | 0.93 | 130 | 30.8% | Intermediate |
| 13 | llasmol-top5 | 12.33 | 15.93 | 1.20 | 130 | 10.0% | Novice |
| 14 | llasmol-top1 | 10.66 | 14.47 | 1.27 | 130 | 6.9% | Novice |

## Key TrueSkill Insights

### Highest Rated Model
**MOSES** achieves the highest TrueSkill rating of **30.70** (μ=33.85, σ=1.05)

### Most Consistent Model
**MOSES-nano** shows the lowest uncertainty with σ=0.88

### Rating Distribution
- **Mean Rating**: 21.48
- **Rating Std**: 5.94
- **Rating Range**: 30.70 - 5.62
- **Models Analyzed**: 14

