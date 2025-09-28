# Round-Based TrueSkill ELO Analysis (Excluding Logic/Clarity) - Evaluation Aggregated

## Executive Summary

This analysis treats each answer round as an independent player, providing unprecedented granularity in AI model evaluation.

- **Analysis Mode**: eval_aggregated
- **Total Matches**: 521,640
- **Processing Time**: 51.8 seconds
- **Models Analyzed**: 14
- **Dimensions**: 4

## Methodology

### Round-Based Player System

**Evaluation Aggregated Mode**:
- Each model-round combination treated as an independent player
- Player ID format: `model_roundX` (e.g., `gpt-4.1_round3`)
- 5 evaluations per answer aggregated into single score
- Total players: 70

## Key Findings

*Detailed findings and visualizations would be generated here*

## Model Rankings by Aggregation Method

*Round-level ranking tables and analysis would be generated here*

## Technical Details

### TrueSkill Parameters

- **Initial μ**: 25.0
- **Initial σ**: 8.333
- **β (skill gap)**: 4.167
- **τ (dynamics)**: 0.083
- **Draw probability**: 5.00%

### Match Statistics

- **Total matches**: 521,640
- **Matches per dimension**: 130,410
- **Processing time**: 51.8 seconds
- **Matches per second**: 10,069

