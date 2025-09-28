# Round-Based TrueSkill ELO Analysis (Full Analysis) - Evaluation Aggregated

## Executive Summary

This analysis treats each answer round as an independent player, providing unprecedented granularity in AI model evaluation.

- **Analysis Mode**: Eval Aggregated
- **Total Matches**: 782,460
- **Processing Time**: 78.3 seconds
- **Processing Speed**: 9,991 matches/second
- **Models Analyzed**: 14
- **Dimensions**: 6

## Methodology

### Round-Based Player System

**Evaluation Aggregated Mode**:
- Each model-round combination treated as an independent player
- Player ID format: `model_roundX` (e.g., `gpt-4.1_round3`)
- 5 evaluations per answer aggregated into single score
- Total players: 70
- Provides clean round-level analysis with noise reduction

## Performance Analysis

### Model Rankings by Aggregation Method

#### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Simple Mean | Weighted Mean | Best Round | Consistency Weighted | Round Consistency | Trend |
|------|-------|-------------|---------------|------------|---------------------|-------------------|-------|
| 1 | MOSES | 31.50 | 31.50 | 33.13 | 31.74 | 0.972 | improving |
| 2 | o3 | 29.66 | 29.66 | 30.40 | 30.39 | 0.972 | declining |
| 3 | gpt-4.1 | 26.13 | 26.13 | 27.15 | 26.20 | 0.967 | stable |
| 4 | o1 | 25.21 | 25.21 | 26.10 | 25.44 | 0.981 | improving |
| 5 | lightrag-4.1-nano | 24.31 | 24.31 | 25.48 | 24.36 | 0.948 | improving |
| 6 | lightrag-4.1 | 22.94 | 22.94 | 25.42 | 22.55 | 0.944 | declining |
| 7 | gpt-4.1-nano | 22.38 | 22.38 | 22.98 | 22.25 | 0.974 | improving |
| 8 | MOSES-nano | 21.84 | 21.84 | 24.53 | 21.96 | 0.870 | improving |
| 9 | gpt-4o | 19.25 | 19.25 | 20.64 | 19.85 | 0.956 | declining |
| 10 | spark-chem13b-think | 18.14 | 18.14 | 19.55 | 17.83 | 0.937 | improving |
| 11 | gpt-4o-mini | 17.28 | 17.28 | 17.89 | 17.32 | 0.959 | declining |
| 12 | spark-chem13b-nothink | 16.94 | 16.94 | 18.49 | 17.99 | 0.948 | improving |
| 13 | llasmol-top5 | 4.30 | 4.30 | 4.71 | 5.07 | 0.942 | stable |
| 14 | llasmol-top1 | 3.68 | 3.68 | 3.86 | 3.75 | 0.956 | stable |

#### Judge: fxx_gemini2.5-pro

| Rank | Model | Simple Mean | Weighted Mean | Best Round | Consistency Weighted | Round Consistency | Trend |
|------|-------|-------------|---------------|------------|---------------------|-------------------|-------|
| 1 | MOSES | 31.08 | 31.08 | 31.92 | 30.32 | 0.978 | improving |
| 2 | o3 | 30.51 | 30.51 | 30.81 | 29.85 | 0.991 | stable |
| 3 | o1 | 28.18 | 28.18 | 28.78 | 27.53 | 0.981 | improving |
| 4 | lightrag-4.1-nano | 27.77 | 27.77 | 28.96 | 27.60 | 0.972 | improving |
| 5 | lightrag-4.1 | 27.20 | 27.20 | 28.62 | 27.28 | 0.969 | declining |
| 6 | gpt-4.1 | 26.91 | 26.91 | 27.84 | 26.63 | 0.970 | stable |
| 7 | gpt-4.1-nano | 23.92 | 23.92 | 25.65 | 23.86 | 0.959 | declining |
| 8 | MOSES-nano | 22.06 | 22.06 | 25.68 | 22.14 | 0.865 | improving |
| 9 | gpt-4o | 20.87 | 20.87 | 22.74 | 20.69 | 0.932 | stable |
| 10 | spark-chem13b-think | 20.33 | 20.33 | 21.51 | 20.01 | 0.952 | improving |
| 11 | gpt-4o-mini | 20.28 | 20.28 | 21.32 | 19.78 | 0.952 | declining |
| 12 | spark-chem13b-nothink | 19.48 | 19.48 | 20.62 | 19.36 | 0.939 | stable |
| 13 | llasmol-top5 | 8.94 | 8.94 | 9.74 | 9.27 | 0.916 | stable |
| 14 | llasmol-top1 | 8.14 | 8.14 | 8.54 | 8.46 | 0.953 | declining |

### Round-Level Performance Analysis

#### Performance Trends Across Rounds

