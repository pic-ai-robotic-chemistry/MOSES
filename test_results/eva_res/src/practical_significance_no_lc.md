# Practical Statistical Significance Analysis (Excluding Logic/Clarity)

## Methodology

This analysis focuses on **practical significance** for model comparisons that matter:

### Statistical Tests Used
1. **Friedman Test**: Non-parametric test for repeated measures across multiple models
2. **Wilcoxon Signed-Rank Test**: For paired comparisons within logical model groups
3. **Bonferroni Correction**: Applied within each comparison group to control family-wise error
4. **Effect Size Analysis**: Cohen's d for practical significance assessment

### Practical Comparison Focus
- **Model Family Variants**: Full vs nano versions, different configurations
- **Adjacent Rankings**: Statistical significance between consecutive ranked models
- **Reasoning Approaches**: Chain-of-thought vs direct reasoning impact
- **Competing Technologies**: Similar models from different providers

**Significance Level**: α = 0.05
**Effect Size Thresholds**: Small (0.2), Medium (0.5), Large (0.8)

## Overall Model Differences (Friedman Test)

*Tests whether there are any significant differences among all models*

| Judge | χ² Statistic | p-value | Result | Interpretation |
|-------|-------------|---------|--------|----------------|
| Doubao-Seed-1.6-combined | 183.90 | 0.000000 | ✓ Significant | Very strong evidence of significant differences among 14 models |
| fxx_gemini2.5-pro | 207.89 | 0.000000 | ✓ Significant | Very strong evidence of significant differences among 14 models |

## Model Significance Boundaries

*For each model, shows the first lower-ranked model with statistically significant difference*

### Judge: Doubao-Seed-1.6-combined

**Summary**: 12/14 models have significant differences with lower-ranked models

| Rank | Model | Score | Significance Boundary | Gap | Difference | p-value | Effect Size | Non-Significant Models |
|------|-------|-------|----------------------|-----|------------|---------|-------------|------------------------|
| #1 | MOSES | 8.383 | #3 lightrag-4.1-nano | 2 ranks | +1.462 | 0.0017 | 0.693 | o3 |
| #2 | o3 | 7.786 | #4 gpt-4.1 | 2 ranks | +1.180 | 0.0362 | 0.388 | lightrag-4.1-nano |
| #3 | lightrag-4.1-nano | 6.921 | #7 lightrag-4.1 | 4 ranks | +0.945 | 0.0362 | 0.455 | gpt-4.1, o1, MOSES-nano |
| #4 | gpt-4.1 | 6.606 | #10 gpt-4o | 6 ranks | +1.480 | 0.0121 | 0.534 | o1, MOSES-nano, lightrag-4.1, gpt-4.1-nano, spa... |
| #5 | o1 | 6.538 | #10 gpt-4o | 5 ranks | +1.413 | 0.0130 | 0.515 | MOSES-nano, lightrag-4.1, gpt-4.1-nano, spark-c... |
| #6 | MOSES-nano | 6.060 | #10 gpt-4o | 4 ranks | +0.935 | 0.0436 | 0.395 | lightrag-4.1, gpt-4.1-nano, spark-chem13b-nothink |
| #7 | lightrag-4.1 | 5.975 | #12 gpt-4o-mini | 5 ranks | +1.547 | 0.0162 | 0.529 | gpt-4.1-nano, spark-chem13b-nothink, gpt-4o, sp... |
| #8 | gpt-4.1-nano | 5.912 | #11 spark-chem13b-think | 3 ranks | +1.076 | 0.0299 | 0.401 | spark-chem13b-nothink, gpt-4o |
| #9 | spark-chem13b-nothink | 5.321 | #13 llasmol-top5 | 4 ranks | +4.383 | 0.0000 | 1.800 | gpt-4o, spark-chem13b-think, gpt-4o-mini |
| #10 | gpt-4o | 5.125 | #13 llasmol-top5 | 3 ranks | +4.188 | 0.0000 | 1.934 | spark-chem13b-think, gpt-4o-mini |
| #11 | spark-chem13b-think | 4.836 | #13 llasmol-top5 | 2 ranks | +3.898 | 0.0000 | 1.798 | gpt-4o-mini |
| #12 | gpt-4o-mini | 4.428 | #13 llasmol-top5 | 1 ranks | +3.491 | 0.0000 | 1.636 | None |
| #13 | llasmol-top5 | 0.937 | No significant diff | N/A | N/A | N/A | N/A | llasmol-top1 |

### Judge: fxx_gemini2.5-pro

**Summary**: 13/14 models have significant differences with lower-ranked models

| Rank | Model | Score | Significance Boundary | Gap | Difference | p-value | Effect Size | Non-Significant Models |
|------|-------|-------|----------------------|-----|------------|---------|-------------|------------------------|
| #1 | MOSES | 8.836 | #3 lightrag-4.1 | 2 ranks | +1.306 | 0.0013 | 0.706 | o3 |
| #2 | o3 | 8.717 | #3 lightrag-4.1 | 1 ranks | +1.187 | 0.0188 | 0.524 | None |
| #3 | lightrag-4.1 | 7.530 | #7 gpt-4.1-nano | 4 ranks | +1.217 | 0.0151 | 0.505 | o1, lightrag-4.1-nano, gpt-4.1 |
| #4 | o1 | 7.404 | #8 MOSES-nano | 4 ranks | +1.561 | 0.0174 | 0.539 | lightrag-4.1-nano, gpt-4.1, gpt-4.1-nano |
| #5 | lightrag-4.1-nano | 7.229 | #8 MOSES-nano | 3 ranks | +1.386 | 0.0096 | 0.551 | gpt-4.1, gpt-4.1-nano |
| #6 | gpt-4.1 | 7.009 | #8 MOSES-nano | 2 ranks | +1.166 | 0.0463 | 0.444 | gpt-4.1-nano |
| #7 | gpt-4.1-nano | 6.313 | #10 spark-chem13b-nothink | 3 ranks | +1.588 | 0.0187 | 0.478 | MOSES-nano, spark-chem13b-think |
| #8 | MOSES-nano | 5.843 | #11 gpt-4o | 3 ranks | +1.626 | 0.0089 | 0.533 | spark-chem13b-think, spark-chem13b-nothink |
| #9 | spark-chem13b-think | 5.267 | #13 llasmol-top5 | 4 ranks | +4.438 | 0.0000 | 1.653 | spark-chem13b-nothink, gpt-4o, gpt-4o-mini |
| #10 | spark-chem13b-nothink | 4.725 | #13 llasmol-top5 | 3 ranks | +3.896 | 0.0000 | 1.440 | gpt-4o, gpt-4o-mini |
| #11 | gpt-4o | 4.217 | #13 llasmol-top5 | 2 ranks | +3.387 | 0.0000 | 1.445 | gpt-4o-mini |
| #12 | gpt-4o-mini | 3.977 | #13 llasmol-top5 | 1 ranks | +3.148 | 0.0000 | 1.207 | None |
| #13 | llasmol-top5 | 0.829 | #14 llasmol-top1 | 1 ranks | +0.454 | 0.0156 | 0.540 | None |

## Practical Model Comparisons

*Focus on comparisons that have practical implications for model selection*

### Judge: Doubao-Seed-1.6-combined

**Summary**: 4/13 group comparisons significant (30.8%), 0/9 adjacent ranks significant (0.0%)

#### Model Family & Technology Comparisons

##### GPT Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| gpt-4.1 vs gpt-4.1-nano | +0.693 | 0.284 (Small) | 0.1698 | 0.5094 | ✗ | ✗ |
| gpt-4o vs gpt-4o-mini | +0.697 | 0.236 (Small) | 0.1286 | 0.3858 | ✗ | ✗ |
| gpt-4.1 vs gpt-4o | +1.480 | 0.534 (Medium) | 0.0121 | 0.0362 | ✓ | ✓ |

##### LightRAG Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| lightrag-4.1 vs lightrag-4.1-nano | -0.945 | -0.455 (Small) | 0.0362 | 0.0362 | ✓ | ✗ |

##### MOSES Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs MOSES-nano | +2.323 | 1.026 (Large) | 0.0001 | 0.0001 | ✓ | ✓ |

##### Spark-Chem Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| spark-chem13b-think vs spark-chem13b-nothink | -0.485 | -0.178 (Negligible) | 0.3483 | 0.3483 | ✗ | ✗ |

##### LlasMol Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| llasmol-top1 vs llasmol-top5 | -0.005 | -0.004 (Negligible) | 0.9250 | 0.9250 | ✗ | ✗ |

##### Flagship/Best Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs o3 | +0.597 | 0.327 (Small) | 0.2109 | 0.8435 | ✗ | ✗ |
| o3 vs gpt-4.1 | +1.180 | 0.388 (Small) | 0.0362 | 0.1448 | ✗ | ✗ |
| gpt-4.1 vs o1 | +0.068 | 0.024 (Negligible) | 0.6964 | 1.0000 | ✗ | ✗ |
| o1 vs lightrag-4.1-nano | -0.382 | -0.139 (Negligible) | 0.4698 | 1.0000 | ✗ | ✗ |

##### Reasoning Approaches

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| o1 vs o3 | -1.248 | -0.575 (Medium) | 0.0133 | 0.0266 | ✓ | ✓ |
| spark-chem13b-think vs spark-chem13b-nothink | -0.485 | -0.178 (Negligible) | 0.3483 | 0.6967 | ✗ | ✗ |

#### Adjacent Ranking Significance

*Statistical significance between consecutively ranked models*

| Ranking | Models | Mean Diff | Effect Size | p-value | Corrected p | Significant | Distinguishable |
|---------|--------|-----------|-------------|---------|-------------|-------------|------------------|
| #1 vs #2 | MOSES vs o3 | +0.597 | 0.327 (Small) | 0.2109 | 1.0000 | ✗ | ✓ |
| #2 vs #3 | o3 vs lightrag-4.1-nano | +0.865 | 0.383 (Small) | 0.0815 | 0.7334 | ✗ | ✓ |
| #3 vs #4 | lightrag-4.1-nano vs gpt-4.1 | +0.315 | 0.124 (Negligible) | 0.5149 | 1.0000 | ✗ | ✗ |
| #4 vs #5 | gpt-4.1 vs o1 | +0.068 | 0.024 (Negligible) | 0.6964 | 1.0000 | ✗ | ✗ |
| #5 vs #6 | o1 vs MOSES-nano | +0.478 | 0.208 (Small) | 0.3608 | 1.0000 | ✗ | ✓ |
| #6 vs #7 | MOSES-nano vs lightrag-4.1 | +0.085 | 0.037 (Negligible) | 0.7496 | 1.0000 | ✗ | ✗ |
| #7 vs #8 | lightrag-4.1 vs gpt-4.1-nano | +0.063 | 0.029 (Negligible) | 0.9529 | 1.0000 | ✗ | ✗ |
| #8 vs #9 | gpt-4.1-nano vs spark-chem13b-nothink | +0.591 | 0.199 (Negligible) | 0.3012 | 1.0000 | ✗ | ✗ |
| #9 vs #10 | spark-chem13b-nothink vs gpt-4o | +0.196 | 0.056 (Negligible) | 0.8593 | 1.0000 | ✗ | ✗ |

### Judge: fxx_gemini2.5-pro

**Summary**: 5/13 group comparisons significant (38.5%), 0/9 adjacent ranks significant (0.0%)

#### Model Family & Technology Comparisons

##### GPT Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| gpt-4.1 vs gpt-4.1-nano | +0.695 | 0.219 (Small) | 0.3158 | 0.9473 | ✗ | ✗ |
| gpt-4o vs gpt-4o-mini | +0.239 | 0.077 (Negligible) | 0.4133 | 1.0000 | ✗ | ✗ |
| gpt-4.1 vs gpt-4o | +2.792 | 0.863 (Large) | 0.0002 | 0.0007 | ✓ | ✓ |

##### LightRAG Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| lightrag-4.1 vs lightrag-4.1-nano | +0.301 | 0.114 (Negligible) | 0.6446 | 0.6446 | ✗ | ✗ |

##### MOSES Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs MOSES-nano | +2.993 | 1.153 (Large) | 0.0000 | 0.0000 | ✓ | ✓ |

##### Spark-Chem Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| spark-chem13b-think vs spark-chem13b-nothink | +0.542 | 0.143 (Negligible) | 0.6790 | 0.6790 | ✗ | ✗ |

##### LlasMol Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| llasmol-top1 vs llasmol-top5 | -0.454 | -0.540 (Medium) | 0.0156 | 0.0156 | ✓ | ✓ |

##### Flagship/Best Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs o3 | +0.119 | 0.086 (Negligible) | 0.7140 | 1.0000 | ✗ | ✗ |
| o3 vs gpt-4.1 | +1.709 | 0.772 (Medium) | 0.0010 | 0.0040 | ✓ | ✓ |
| gpt-4.1 vs o1 | -0.395 | -0.121 (Negligible) | 0.4846 | 1.0000 | ✗ | ✗ |
| o1 vs lightrag-4.1-nano | +0.175 | 0.060 (Negligible) | 0.9153 | 1.0000 | ✗ | ✗ |

##### Reasoning Approaches

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| o1 vs o3 | -1.313 | -0.583 (Medium) | 0.0186 | 0.0371 | ✓ | ✓ |
| spark-chem13b-think vs spark-chem13b-nothink | +0.542 | 0.143 (Negligible) | 0.6790 | 1.0000 | ✗ | ✗ |

#### Adjacent Ranking Significance

*Statistical significance between consecutively ranked models*

| Ranking | Models | Mean Diff | Effect Size | p-value | Corrected p | Significant | Distinguishable |
|---------|--------|-----------|-------------|---------|-------------|-------------|------------------|
| #1 vs #2 | MOSES vs o3 | +0.119 | 0.086 (Negligible) | 0.7140 | 1.0000 | ✗ | ✗ |
| #2 vs #3 | o3 vs lightrag-4.1 | +1.187 | 0.524 (Medium) | 0.0188 | 0.1693 | ✗ | ✓ |
| #3 vs #4 | lightrag-4.1 vs o1 | +0.126 | 0.042 (Negligible) | 0.7775 | 1.0000 | ✗ | ✗ |
| #4 vs #5 | o1 vs lightrag-4.1-nano | +0.175 | 0.060 (Negligible) | 0.9153 | 1.0000 | ✗ | ✗ |
| #5 vs #6 | lightrag-4.1-nano vs gpt-4.1 | +0.221 | 0.094 (Negligible) | 0.7140 | 1.0000 | ✗ | ✗ |
| #6 vs #7 | gpt-4.1 vs gpt-4.1-nano | +0.695 | 0.219 (Small) | 0.3158 | 1.0000 | ✗ | ✓ |
| #7 vs #8 | gpt-4.1-nano vs MOSES-nano | +0.470 | 0.181 (Negligible) | 0.2792 | 1.0000 | ✗ | ✗ |
| #8 vs #9 | MOSES-nano vs spark-chem13b-think | +0.576 | 0.175 (Negligible) | 0.4270 | 1.0000 | ✗ | ✗ |
| #9 vs #10 | spark-chem13b-think vs spark-chem13b-nothink | +0.542 | 0.143 (Negligible) | 0.6790 | 1.0000 | ✗ | ✗ |

## Key Practical Findings

### Significant Model Family Differences
- **Doubao-Seed-1.6-combined**: gpt-4.1 vs gpt-4o (GPT Family Models) - Mean difference: +1.480, Effect size: 0.534
- **Doubao-Seed-1.6-combined**: MOSES vs MOSES-nano (MOSES Family Models) - Mean difference: +2.323, Effect size: 1.026
- **Doubao-Seed-1.6-combined**: o1 vs o3 (Reasoning Approaches) - Mean difference: -1.248, Effect size: -0.575
- **fxx_gemini2.5-pro**: gpt-4.1 vs gpt-4o (GPT Family Models) - Mean difference: +2.792, Effect size: 0.863
- **fxx_gemini2.5-pro**: MOSES vs MOSES-nano (MOSES Family Models) - Mean difference: +2.993, Effect size: 1.153
- **fxx_gemini2.5-pro**: llasmol-top1 vs llasmol-top5 (LlasMol Models) - Mean difference: -0.454, Effect size: -0.540
- **fxx_gemini2.5-pro**: o3 vs gpt-4.1 (Flagship/Best Models) - Mean difference: +1.709, Effect size: 0.772
- **fxx_gemini2.5-pro**: o1 vs o3 (Reasoning Approaches) - Mean difference: -1.313, Effect size: -0.583

## Practical Recommendations

Based on this statistical analysis:

1. **Model Variants Show Meaningful Differences**: 8 statistically significant and practically meaningful differences found between model variants

