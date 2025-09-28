# Statistical Significance Analysis (Excluding Logic/Clarity)

## Methodology

This analysis employs the following statistical methods:

1. **Mann-Whitney U Test**: Non-parametric test for comparing two independent groups
2. **Kruskal-Wallis H Test**: Non-parametric ANOVA for comparing multiple groups
3. **Wilcoxon Signed-Rank Test**: For paired comparisons between judges
4. **Bonferroni Correction**: Multiple comparison correction to control family-wise error rate
5. **Effect Size (Cohen's d)**: Measure of practical significance
6. **Bootstrap Confidence Intervals**: Robust confidence interval estimation

**Significance Level**: α = 0.05

## Overall Model Ranking Tests

*Kruskal-Wallis H Test results for overall model differences*

| Judge | H-Statistic | p-value | Significant | Interpretation |
|-------|-------------|---------|-------------|----------------|
| Doubao-Seed-1.6-combined | 1910.428 | 0.000000 | ✓ | Very strong evidence against null hypothesis (models perform significantly differently) |
| fxx_gemini2.5-pro | 2148.263 | 0.000000 | ✓ | Very strong evidence against null hypothesis (models perform significantly differently) |

## Pairwise Model Comparisons Summary

### Judge: Doubao-Seed-1.6-combined

**Total Comparisons**: 91
**Significant (uncorrected)**: 76 (83.5%)
**Significant (Bonferroni corrected)**: 69 (75.8%)

#### Most Significant Differences (Bonferroni Corrected)

| Model 1 | Model 2 | Mean Diff | Effect Size | p-value (corrected) |
|---------|---------|-----------|-------------|---------------------|
| MOSES | llasmol-top1 | +7.483 | 6.826 | 0.000000 |
| MOSES | llasmol-top5 | +7.375 | 6.352 | 0.000000 |
| llasmol-top1 | o3 | -6.647 | -5.316 | 0.000000 |
| llasmol-top5 | o3 | -6.540 | -5.002 | 0.000000 |
| lightrag-4.1-nano | llasmol-top1 | +5.439 | 4.370 | 0.000000 |
| lightrag-4.1 | llasmol-top1 | +5.318 | 4.271 | 0.000000 |
| gpt-4.1 | llasmol-top1 | +5.675 | 4.193 | 0.000000 |
| lightrag-4.1-nano | llasmol-top5 | +5.332 | 4.094 | 0.000000 |
| llasmol-top1 | o1 | -5.472 | -4.056 | 0.000000 |
| lightrag-4.1 | llasmol-top5 | +5.211 | 4.000 | 0.000000 |

### Judge: fxx_gemini2.5-pro

**Total Comparisons**: 91
**Significant (uncorrected)**: 82 (90.1%)
**Significant (Bonferroni corrected)**: 78 (85.7%)

#### Most Significant Differences (Bonferroni Corrected)

| Model 1 | Model 2 | Mean Diff | Effect Size | p-value (corrected) |
|---------|---------|-----------|-------------|---------------------|
| MOSES | llasmol-top1 | +8.277 | 9.447 | 0.000000 |
| llasmol-top1 | o3 | -8.090 | -7.727 | 0.000000 |
| MOSES | llasmol-top5 | +7.855 | 7.488 | 0.000000 |
| llasmol-top5 | o3 | -7.668 | -6.414 | 0.000000 |
| lightrag-4.1 | llasmol-top1 | +6.818 | 5.660 | 0.000000 |
| lightrag-4.1-nano | llasmol-top1 | +6.744 | 5.365 | 0.000000 |
| gpt-4.1 | llasmol-top1 | +6.449 | 5.017 | 0.000000 |
| lightrag-4.1 | llasmol-top5 | +6.396 | 4.788 | 0.000000 |
| llasmol-top1 | o1 | -6.707 | -4.695 | 0.000000 |
| lightrag-4.1-nano | llasmol-top5 | +6.322 | 4.571 | 0.000000 |

## Judge Agreement Analysis

### Inter-Judge Correlations

| Judge Pair | Pearson r | p-value | Spearman ρ | p-value | Agreement Level |
|------------|-----------|---------|------------|---------|----------------|
| Doubao-Seed-1.6-combined vs fxx_gemini2.5-pro | 0.979 | 0.0000 | 0.956 | 0.0000 | Very High |

## Dimension Analysis

*Statistical properties of evaluation dimensions*

### Judge: Doubao-Seed-1.6-combined

| Dimension | Mean | Std | Range | 95% CI | CV |
|-----------|------|-----|-------|--------|----|
| Correctness | 6.75 | 2.58 | 8.39 | [5.24, 7.89] | 0.383 |
| Completeness | 4.92 | 2.41 | 8.62 | [3.59, 6.09] | 0.491 |
| Theoretical Depth | 3.13 | 1.64 | 6.41 | [2.32, 3.92] | 0.524 |
| Rigor And Information Density | 6.10 | 2.55 | 8.24 | [4.79, 7.23] | 0.419 |

### Judge: fxx_gemini2.5-pro

| Dimension | Mean | Std | Range | 95% CI | CV |
|-----------|------|-----|-------|--------|----|
| Correctness | 7.28 | 2.71 | 8.43 | [5.84, 8.50] | 0.372 |
| Completeness | 4.93 | 2.45 | 8.59 | [3.75, 6.07] | 0.496 |
| Theoretical Depth | 4.11 | 2.72 | 8.65 | [2.75, 5.53] | 0.662 |
| Rigor And Information Density | 6.19 | 3.14 | 9.50 | [4.59, 7.75] | 0.508 |

## Key Statistical Findings

### Significant Overall Differences
The following judges show statistically significant differences between models:
- **Doubao-Seed-1.6-combined**: Very strong evidence against null hypothesis (models perform significantly differently)
- **fxx_gemini2.5-pro**: Very strong evidence against null hypothesis (models perform significantly differently)

### Most Discriminating Judge
**fxx_gemini2.5-pro** shows the highest proportion of significant model differences (85.7% of comparisons)

