# Practical Statistical Significance Analysis (Full Analysis)

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
| Doubao-Seed-1.6-combined | 195.23 | 0.000000 | ✓ Significant | Very strong evidence of significant differences among 14 models |
| fxx_gemini2.5-pro | 201.61 | 0.000000 | ✓ Significant | Very strong evidence of significant differences among 14 models |

## Model Significance Boundaries

*For each model, shows the first lower-ranked model with statistically significant difference*

### Judge: Doubao-Seed-1.6-combined

**Summary**: 12/14 models have significant differences with lower-ranked models

| Rank | Model | Score | Significance Boundary | Gap | Difference | p-value | Effect Size | Non-Significant Models |
|------|-------|-------|----------------------|-----|------------|---------|-------------|------------------------|
| #1 | MOSES | 8.800 | #2 o3 | 1 ranks | +0.899 | 0.0339 | 0.462 | None |
| #2 | o3 | 7.901 | #5 lightrag-4.1-nano | 3 ranks | +1.103 | 0.0065 | 0.619 | gpt-4.1, o1 |
| #3 | gpt-4.1 | 7.466 | #6 lightrag-4.1 | 3 ranks | +0.834 | 0.0299 | 0.433 | o1, lightrag-4.1-nano |
| #4 | o1 | 7.284 | #9 gpt-4o | 5 ranks | +1.242 | 0.0151 | 0.531 | lightrag-4.1-nano, lightrag-4.1, gpt-4.1-nano, ... |
| #5 | lightrag-4.1-nano | 6.798 | #10 gpt-4o-mini | 5 ranks | +1.213 | 0.0046 | 0.578 | lightrag-4.1, gpt-4.1-nano, MOSES-nano, gpt-4o |
| #6 | lightrag-4.1 | 6.632 | #10 gpt-4o-mini | 4 ranks | +1.047 | 0.0280 | 0.461 | gpt-4.1-nano, MOSES-nano, gpt-4o |
| #7 | gpt-4.1-nano | 6.542 | #10 gpt-4o-mini | 3 ranks | +0.957 | 0.0280 | 0.447 | MOSES-nano, gpt-4o |
| #8 | MOSES-nano | 6.334 | #12 spark-chem13b-nothink | 4 ranks | +1.374 | 0.0174 | 0.518 | gpt-4o, gpt-4o-mini, spark-chem13b-think |
| #9 | gpt-4o | 6.042 | #12 spark-chem13b-nothink | 3 ranks | +1.082 | 0.0319 | 0.465 | gpt-4o-mini, spark-chem13b-think |
| #10 | gpt-4o-mini | 5.585 | #13 llasmol-top5 | 3 ranks | +4.469 | 0.0000 | 2.351 | spark-chem13b-think, spark-chem13b-nothink |
| #11 | spark-chem13b-think | 5.269 | #13 llasmol-top5 | 2 ranks | +4.153 | 0.0000 | 1.549 | spark-chem13b-nothink |
| #12 | spark-chem13b-nothink | 4.960 | #13 llasmol-top5 | 1 ranks | +3.844 | 0.0000 | 1.622 | None |
| #13 | llasmol-top5 | 1.116 | No significant diff | N/A | N/A | N/A | N/A | llasmol-top1 |

### Judge: fxx_gemini2.5-pro

**Summary**: 12/14 models have significant differences with lower-ranked models

| Rank | Model | Score | Significance Boundary | Gap | Difference | p-value | Effect Size | Non-Significant Models |
|------|-------|-------|----------------------|-----|------------|---------|-------------|------------------------|
| #1 | o3 | 8.950 | #4 gpt-4.1 | 3 ranks | +0.762 | 0.0462 | 0.428 | MOSES, lightrag-4.1 |
| #2 | MOSES | 8.900 | #4 gpt-4.1 | 2 ranks | +0.712 | 0.0385 | 0.424 | lightrag-4.1 |
| #3 | lightrag-4.1 | 8.351 | #7 gpt-4.1-nano | 4 ranks | +1.567 | 0.0030 | 0.632 | gpt-4.1, o1, lightrag-4.1-nano |
| #4 | gpt-4.1 | 8.188 | #7 gpt-4.1-nano | 3 ranks | +1.403 | 0.0030 | 0.645 | o1, lightrag-4.1-nano |
| #5 | o1 | 7.725 | #9 MOSES-nano | 4 ranks | +1.222 | 0.0362 | 0.451 | lightrag-4.1-nano, gpt-4.1-nano, gpt-4o |
| #6 | lightrag-4.1-nano | 7.682 | #8 gpt-4o | 2 ranks | +1.079 | 0.0280 | 0.490 | gpt-4.1-nano |
| #7 | gpt-4.1-nano | 6.785 | #10 spark-chem13b-think | 3 ranks | +1.199 | 0.0245 | 0.437 | gpt-4o, MOSES-nano |
| #8 | gpt-4o | 6.602 | #12 gpt-4o-mini | 4 ranks | +1.433 | 0.0362 | 0.460 | MOSES-nano, spark-chem13b-think, spark-chem13b-... |
| #9 | MOSES-nano | 6.504 | #12 gpt-4o-mini | 3 ranks | +1.334 | 0.0089 | 0.566 | spark-chem13b-think, spark-chem13b-nothink |
| #10 | spark-chem13b-think | 5.586 | #13 llasmol-top1 | 3 ranks | +4.048 | 0.0000 | 1.314 | spark-chem13b-nothink, gpt-4o-mini |
| #11 | spark-chem13b-nothink | 5.333 | #13 llasmol-top1 | 2 ranks | +3.796 | 0.0000 | 1.295 | gpt-4o-mini |
| #12 | gpt-4o-mini | 5.170 | #13 llasmol-top1 | 1 ranks | +3.632 | 0.0000 | 1.453 | None |
| #13 | llasmol-top1 | 1.537 | No significant diff | N/A | N/A | N/A | N/A | llasmol-top5 |

## Practical Model Comparisons

*Focus on comparisons that have practical implications for model selection*

### Judge: Doubao-Seed-1.6-combined

**Summary**: 2/13 group comparisons significant (15.4%), 0/9 adjacent ranks significant (0.0%)

#### Model Family & Technology Comparisons

##### GPT Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| gpt-4.1 vs gpt-4.1-nano | +0.924 | 0.464 (Small) | 0.0362 | 0.1086 | ✗ | ✗ |
| gpt-4o vs gpt-4o-mini | +0.457 | 0.191 (Negligible) | 0.4410 | 1.0000 | ✗ | ✗ |
| gpt-4.1 vs gpt-4o | +1.424 | 0.748 (Medium) | 0.0011 | 0.0034 | ✓ | ✓ |

##### LightRAG Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| lightrag-4.1 vs lightrag-4.1-nano | -0.166 | -0.087 (Negligible) | 0.4553 | 0.4553 | ✗ | ✗ |

##### MOSES Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs MOSES-nano | +2.466 | 1.049 (Large) | 0.0000 | 0.0000 | ✓ | ✓ |

##### Spark-Chem Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| spark-chem13b-think vs spark-chem13b-nothink | +0.308 | 0.099 (Negligible) | 0.4410 | 0.4410 | ✗ | ✗ |

##### LlasMol Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| llasmol-top1 vs llasmol-top5 | -0.109 | -0.075 (Negligible) | 0.8612 | 0.8612 | ✗ | ✗ |

##### Flagship/Best Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs o3 | +0.899 | 0.462 (Small) | 0.0339 | 0.1358 | ✗ | ✗ |
| o3 vs gpt-4.1 | +0.435 | 0.259 (Small) | 0.4133 | 1.0000 | ✗ | ✗ |
| gpt-4.1 vs o1 | +0.182 | 0.082 (Negligible) | 0.8889 | 1.0000 | ✗ | ✗ |
| o1 vs lightrag-4.1-nano | +0.486 | 0.223 (Small) | 0.1937 | 0.7747 | ✗ | ✗ |

##### Reasoning Approaches

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| o1 vs o3 | -0.617 | -0.315 (Small) | 0.2291 | 0.4581 | ✗ | ✗ |
| spark-chem13b-think vs spark-chem13b-nothink | +0.308 | 0.099 (Negligible) | 0.4410 | 0.8821 | ✗ | ✗ |

#### Adjacent Ranking Significance

*Statistical significance between consecutively ranked models*

| Ranking | Models | Mean Diff | Effect Size | p-value | Corrected p | Significant | Distinguishable |
|---------|--------|-----------|-------------|---------|-------------|-------------|------------------|
| #1 vs #2 | MOSES vs o3 | +0.899 | 0.462 (Small) | 0.0339 | 0.3055 | ✗ | ✓ |
| #2 vs #3 | o3 vs gpt-4.1 | +0.435 | 0.259 (Small) | 0.4133 | 1.0000 | ✗ | ✓ |
| #3 vs #4 | gpt-4.1 vs o1 | +0.182 | 0.082 (Negligible) | 0.8889 | 1.0000 | ✗ | ✗ |
| #4 vs #5 | o1 vs lightrag-4.1-nano | +0.486 | 0.223 (Small) | 0.1937 | 1.0000 | ✗ | ✓ |
| #5 vs #6 | lightrag-4.1-nano vs lightrag-4.1 | +0.166 | 0.087 (Negligible) | 0.4553 | 1.0000 | ✗ | ✗ |
| #6 vs #7 | lightrag-4.1 vs gpt-4.1-nano | +0.091 | 0.038 (Negligible) | 0.9153 | 1.0000 | ✗ | ✗ |
| #7 vs #8 | gpt-4.1-nano vs MOSES-nano | +0.207 | 0.074 (Negligible) | 0.7496 | 1.0000 | ✗ | ✗ |
| #8 vs #9 | MOSES-nano vs gpt-4o | +0.292 | 0.106 (Negligible) | 0.6109 | 1.0000 | ✗ | ✗ |
| #9 vs #10 | gpt-4o vs gpt-4o-mini | +0.457 | 0.191 (Negligible) | 0.4410 | 1.0000 | ✗ | ✗ |

### Judge: fxx_gemini2.5-pro

**Summary**: 4/13 group comparisons significant (30.8%), 0/9 adjacent ranks significant (0.0%)

#### Model Family & Technology Comparisons

##### GPT Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| gpt-4.1 vs gpt-4.1-nano | +1.403 | 0.645 (Medium) | 0.0030 | 0.0089 | ✓ | ✓ |
| gpt-4o vs gpt-4o-mini | +1.433 | 0.460 (Small) | 0.0362 | 0.1086 | ✗ | ✗ |
| gpt-4.1 vs gpt-4o | +1.586 | 0.671 (Medium) | 0.0039 | 0.0116 | ✓ | ✓ |

##### LightRAG Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| lightrag-4.1 vs lightrag-4.1-nano | +0.670 | 0.346 (Small) | 0.0765 | 0.0765 | ✗ | ✗ |

##### MOSES Family Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs MOSES-nano | +2.397 | 1.070 (Large) | 0.0000 | 0.0000 | ✓ | ✓ |

##### Spark-Chem Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| spark-chem13b-think vs spark-chem13b-nothink | +0.252 | 0.063 (Negligible) | 0.8779 | 0.8779 | ✗ | ✗ |

##### LlasMol Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| llasmol-top1 vs llasmol-top5 | +0.099 | 0.051 (Negligible) | 0.9090 | 0.9090 | ✗ | ✗ |

##### Flagship/Best Models

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| MOSES vs o3 | -0.050 | -0.036 (Negligible) | 0.8489 | 1.0000 | ✗ | ✗ |
| o3 vs gpt-4.1 | +0.762 | 0.428 (Small) | 0.0462 | 0.1847 | ✗ | ✗ |
| gpt-4.1 vs o1 | +0.463 | 0.222 (Small) | 0.2687 | 1.0000 | ✗ | ✗ |
| o1 vs lightrag-4.1-nano | +0.044 | 0.020 (Negligible) | 0.8415 | 1.0000 | ✗ | ✗ |

##### Reasoning Approaches

| Comparison | Mean Diff | Effect Size | p-value | Corrected p | Significant | Practical Impact |
|------------|-----------|-------------|---------|-------------|-------------|------------------|
| o1 vs o3 | -1.225 | -0.560 (Medium) | 0.0094 | 0.0188 | ✓ | ✓ |
| spark-chem13b-think vs spark-chem13b-nothink | +0.252 | 0.063 (Negligible) | 0.8779 | 1.0000 | ✗ | ✗ |

#### Adjacent Ranking Significance

*Statistical significance between consecutively ranked models*

| Ranking | Models | Mean Diff | Effect Size | p-value | Corrected p | Significant | Distinguishable |
|---------|--------|-----------|-------------|---------|-------------|-------------|------------------|
| #1 vs #2 | o3 vs MOSES | +0.050 | 0.036 (Negligible) | 0.8489 | 1.0000 | ✗ | ✗ |
| #2 vs #3 | MOSES vs lightrag-4.1 | +0.549 | 0.289 (Small) | 0.2109 | 1.0000 | ✗ | ✓ |
| #3 vs #4 | lightrag-4.1 vs gpt-4.1 | +0.163 | 0.081 (Negligible) | 0.5303 | 1.0000 | ✗ | ✗ |
| #4 vs #5 | gpt-4.1 vs o1 | +0.463 | 0.222 (Small) | 0.2687 | 1.0000 | ✗ | ✓ |
| #5 vs #6 | o1 vs lightrag-4.1-nano | +0.044 | 0.020 (Negligible) | 0.8415 | 1.0000 | ✗ | ✗ |
| #6 vs #7 | lightrag-4.1-nano vs gpt-4.1-nano | +0.897 | 0.317 (Small) | 0.1167 | 1.0000 | ✗ | ✓ |
| #7 vs #8 | gpt-4.1-nano vs gpt-4o | +0.183 | 0.068 (Negligible) | 0.7496 | 1.0000 | ✗ | ✗ |
| #8 vs #9 | gpt-4o vs MOSES-nano | +0.099 | 0.036 (Negligible) | 0.9717 | 1.0000 | ✗ | ✗ |
| #9 vs #10 | MOSES-nano vs spark-chem13b-think | +0.918 | 0.339 (Small) | 0.0692 | 0.6230 | ✗ | ✓ |

## Key Practical Findings

### Significant Model Family Differences
- **Doubao-Seed-1.6-combined**: gpt-4.1 vs gpt-4o (GPT Family Models) - Mean difference: +1.424, Effect size: 0.748
- **Doubao-Seed-1.6-combined**: MOSES vs MOSES-nano (MOSES Family Models) - Mean difference: +2.466, Effect size: 1.049
- **fxx_gemini2.5-pro**: gpt-4.1 vs gpt-4.1-nano (GPT Family Models) - Mean difference: +1.403, Effect size: 0.645
- **fxx_gemini2.5-pro**: gpt-4.1 vs gpt-4o (GPT Family Models) - Mean difference: +1.586, Effect size: 0.671
- **fxx_gemini2.5-pro**: MOSES vs MOSES-nano (MOSES Family Models) - Mean difference: +2.397, Effect size: 1.070
- **fxx_gemini2.5-pro**: o1 vs o3 (Reasoning Approaches) - Mean difference: -1.225, Effect size: -0.560

## Practical Recommendations

Based on this statistical analysis:

1. **Model Variants Show Meaningful Differences**: 6 statistically significant and practically meaningful differences found between model variants

