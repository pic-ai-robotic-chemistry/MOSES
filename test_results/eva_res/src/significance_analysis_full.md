# Statistical Significance Analysis (Full Analysis)

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
| Doubao-Seed-1.6-combined | 1939.933 | 0.000000 | ✓ | Very strong evidence against null hypothesis (models perform significantly differently) |
| fxx_gemini2.5-pro | 2078.490 | 0.000000 | ✓ | Very strong evidence against null hypothesis (models perform significantly differently) |

## Pairwise Model Comparisons Summary

### Judge: Doubao-Seed-1.6-combined

**Total Comparisons**: 91
**Significant (uncorrected)**: 84 (92.3%)
**Significant (Bonferroni corrected)**: 72 (79.1%)

#### Most Significant Differences (Bonferroni Corrected)

| Model 1 | Model 2 | Mean Diff | Effect Size | p-value (corrected) |
|---------|---------|-----------|-------------|---------------------|
| MOSES | llasmol-top5 | +7.644 | 7.003 | 0.000000 |
| MOSES | llasmol-top1 | +7.609 | 6.938 | 0.000000 |
| llasmol-top5 | o3 | -7.253 | -5.948 | 0.000000 |
| llasmol-top1 | o3 | -7.218 | -5.897 | 0.000000 |
| gpt-4.1 | llasmol-top5 | +6.304 | 5.010 | 0.000000 |
| gpt-4.1 | llasmol-top1 | +6.269 | 4.964 | 0.000000 |
| lightrag-4.1-nano | llasmol-top5 | +6.003 | 4.779 | 0.000000 |
| lightrag-4.1-nano | llasmol-top1 | +5.967 | 4.734 | 0.000000 |
| lightrag-4.1 | llasmol-top5 | +5.934 | 4.609 | 0.000000 |
| lightrag-4.1 | llasmol-top1 | +5.899 | 4.566 | 0.000000 |

### Judge: fxx_gemini2.5-pro

**Total Comparisons**: 91
**Significant (uncorrected)**: 80 (87.9%)
**Significant (Bonferroni corrected)**: 77 (84.6%)

#### Most Significant Differences (Bonferroni Corrected)

| Model 1 | Model 2 | Mean Diff | Effect Size | p-value (corrected) |
|---------|---------|-----------|-------------|---------------------|
| MOSES | llasmol-top1 | +8.072 | 8.494 | 0.000000 |
| llasmol-top1 | o3 | -7.949 | -7.293 | 0.000000 |
| MOSES | llasmol-top5 | +7.750 | 6.862 | 0.000000 |
| llasmol-top5 | o3 | -7.627 | -6.106 | 0.000000 |
| gpt-4.1 | llasmol-top1 | +7.033 | 5.997 | 0.000000 |
| lightrag-4.1 | llasmol-top1 | +6.767 | 5.146 | 0.000000 |
| lightrag-4.1-nano | llasmol-top1 | +6.828 | 5.092 | 0.000000 |
| gpt-4.1 | llasmol-top5 | +6.711 | 5.076 | 0.000000 |
| llasmol-top1 | o1 | -6.720 | -4.579 | 0.000000 |
| lightrag-4.1 | llasmol-top5 | +6.445 | 4.446 | 0.000000 |

## Judge Agreement Analysis

### Inter-Judge Correlations

| Judge Pair | Pearson r | p-value | Spearman ρ | p-value | Agreement Level |
|------------|-----------|---------|------------|---------|----------------|
| Doubao-Seed-1.6-combined vs fxx_gemini2.5-pro | 0.988 | 0.0000 | 0.978 | 0.0000 | Very High |

## Dimension Analysis

*Statistical properties of evaluation dimensions*

### Judge: Doubao-Seed-1.6-combined

| Dimension | Mean | Std | Range | 95% CI | CV |
|-----------|------|-----|-------|--------|----|
| Correctness | 6.75 | 2.58 | 8.39 | [5.20, 7.95] | 0.383 |
| Completeness | 4.92 | 2.41 | 8.62 | [3.50, 6.02] | 0.491 |
| Logic | 7.40 | 2.69 | 8.44 | [5.84, 8.56] | 0.363 |
| Clarity | 7.71 | 2.59 | 7.97 | [6.30, 8.80] | 0.336 |
| Theoretical Depth | 3.13 | 1.64 | 6.41 | [2.30, 3.99] | 0.524 |
| Rigor And Information Density | 6.10 | 2.55 | 8.24 | [4.79, 7.20] | 0.419 |

### Judge: fxx_gemini2.5-pro

| Dimension | Mean | Std | Range | 95% CI | CV |
|-----------|------|-----|-------|--------|----|
| Correctness | 7.28 | 2.71 | 8.43 | [5.77, 8.43] | 0.372 |
| Completeness | 4.93 | 2.45 | 8.59 | [3.64, 6.04] | 0.496 |
| Logic | 7.47 | 2.99 | 8.94 | [5.93, 8.86] | 0.400 |
| Clarity | 7.91 | 2.67 | 8.10 | [6.39, 9.08] | 0.338 |
| Theoretical Depth | 4.11 | 2.72 | 8.65 | [2.74, 5.40] | 0.662 |
| Rigor And Information Density | 6.19 | 3.14 | 9.50 | [4.48, 7.72] | 0.508 |

## Key Statistical Findings

### Significant Overall Differences
The following judges show statistically significant differences between models:
- **Doubao-Seed-1.6-combined**: Very strong evidence against null hypothesis (models perform significantly differently)
- **fxx_gemini2.5-pro**: Very strong evidence against null hypothesis (models perform significantly differently)

### Most Discriminating Judge
**fxx_gemini2.5-pro** shows the highest proportion of significant model differences (84.6% of comparisons)

