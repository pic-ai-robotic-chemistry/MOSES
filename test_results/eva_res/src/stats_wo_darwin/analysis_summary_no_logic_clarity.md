# Individual Evaluation Analysis Summary (Excluding Logic and Clarity)

## Data Quality Summary

- **Total records**: 37800
- **Array wrapped scores**: 16866
- **Invalid scores**: 0
- **Missing evaluations**: 4
- **JSON parse errors**: 4
- **Incomplete evaluation sets**: 21

*Note: This analysis excludes Logic and Clarity dimensions, assuming judge models did not provide these evaluations.*

## Judge Models Overview (Excluding Logic/Clarity)

| Judge Model | Total Evaluations | Data Completeness |
|-------------|-------------------|-------------------|
| Doubao-Seed-1.6-combined | 3780 | Complete (200.0%) |
| fxx_gemini2.5-pro | 3780 | Complete (200.0%) |

## Model Average Scores by Judge (Excluding Logic/Clarity)

### Judge: Doubao-Seed-1.6-combined

*Total evaluations: 3780*

#### Overall Ranking

| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |
|------|-------|---------------|---------|-------------|----------|
| 1 | MOSES | 8.34 | 1.41 | 270 | 270/270 (100.0%) |
| 2 | o3 | 7.64 | 1.88 | 270 | 270/270 (100.0%) |
| 3 | gpt-4.1 | 6.48 | 1.82 | 270 | 270/270 (100.0%) |
| 4 | lightrag-4.1-nano | 6.35 | 1.52 | 270 | 270/270 (100.0%) |
| 5 | o1 | 6.33 | 1.80 | 270 | 270/270 (100.0%) |
| 6 | lightrag-4.1 | 6.09 | 1.56 | 270 | 270/270 (100.0%) |
| 7 | MOSES-nano | 5.94 | 1.90 | 270 | 270/270 (100.0%) |
| 8 | gpt-4.1-nano | 5.81 | 1.78 | 270 | 270/270 (100.0%) |
| 9 | gpt-4o | 5.20 | 1.90 | 270 | 270/270 (100.0%) |
| 10 | spark-chem13b-think | 4.81 | 2.27 | 270 | 270/270 (100.0%) |
| 11 | spark-chem13b-nothink | 4.70 | 2.42 | 270 | 270/270 (100.0%) |
| 12 | gpt-4o-mini | 4.42 | 1.96 | 270 | 270/270 (100.0%) |
| 13 | llasmol-top1 | 0.52 | 1.11 | 270 | 270/270 (100.0%) |
| 14 | llasmol-top5 | 0.51 | 1.21 | 270 | 270/270 (100.0%) |

#### Dimension-wise Scores

| Model | Correctness | Completeness | Theoretical Depth | Rigor And Information Density |
|-------|-------:|-------:|-------:|-------:|
| MOSES | 9.56 | 8.72 | 6.51 | 8.58 |
| o3 | 9.29 | 7.87 | 4.55 | 8.84 |
| gpt-4.1 | 8.47 | 6.62 | 3.20 | 7.65 |
| lightrag-4.1-nano | 8.02 | 6.02 | 4.03 | 7.35 |
| o1 | 8.29 | 5.51 | 3.60 | 7.91 |
| lightrag-4.1 | 7.63 | 5.52 | 4.03 | 7.19 |
| MOSES-nano | 7.55 | 5.31 | 4.00 | 6.88 |
| gpt-4.1-nano | 7.86 | 5.35 | 3.12 | 6.90 |
| gpt-4o | 6.96 | 4.88 | 2.75 | 6.20 |
| spark-chem13b-think | 6.33 | 4.37 | 2.79 | 5.76 |
| spark-chem13b-nothink | 6.34 | 4.34 | 2.59 | 5.52 |
| gpt-4o-mini | 5.84 | 4.07 | 2.43 | 5.35 |
| llasmol-top1 | 1.17 | 0.14 | 0.16 | 0.60 |
| llasmol-top5 | 1.21 | 0.11 | 0.10 | 0.61 |

### Judge: fxx_gemini2.5-pro

*Total evaluations: 3780*

#### Overall Ranking

| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |
|------|-------|---------------|---------|-------------|----------|
| 1 | MOSES | 9.14 | 1.15 | 270 | 270/270 (100.0%) |
| 2 | o3 | 8.91 | 1.64 | 270 | 270/270 (100.0%) |
| 3 | o1 | 7.48 | 2.06 | 270 | 270/270 (100.0%) |
| 4 | lightrag-4.1-nano | 7.45 | 1.75 | 270 | 270/270 (100.0%) |
| 5 | lightrag-4.1 | 7.31 | 1.80 | 270 | 270/270 (100.0%) |
| 6 | gpt-4.1 | 7.16 | 1.84 | 270 | 270/270 (100.0%) |
| 7 | MOSES-nano | 6.16 | 2.49 | 270 | 270/270 (100.0%) |
| 8 | gpt-4.1-nano | 5.74 | 2.22 | 270 | 270/270 (100.0%) |
| 9 | gpt-4o | 5.00 | 2.42 | 270 | 270/270 (100.0%) |
| 10 | spark-chem13b-think | 4.85 | 2.75 | 270 | 270/270 (100.0%) |
| 11 | spark-chem13b-nothink | 4.55 | 2.85 | 270 | 270/270 (100.0%) |
| 12 | gpt-4o-mini | 4.02 | 2.61 | 270 | 270/270 (100.0%) |
| 13 | llasmol-top5 | 0.60 | 1.38 | 270 | 270/270 (100.0%) |
| 14 | llasmol-top1 | 0.42 | 1.03 | 270 | 270/270 (100.0%) |

#### Dimension-wise Scores

| Model | Correctness | Completeness | Theoretical Depth | Rigor And Information Density |
|-------|-------:|-------:|-------:|-------:|
| MOSES | 9.67 | 8.60 | 8.68 | 9.62 |
| o3 | 9.38 | 8.16 | 8.26 | 9.86 |
| o1 | 9.11 | 5.43 | 6.03 | 9.34 |
| lightrag-4.1-nano | 9.10 | 5.96 | 6.19 | 8.56 |
| lightrag-4.1 | 9.16 | 5.46 | 6.23 | 8.38 |
| gpt-4.1 | 9.18 | 6.59 | 4.27 | 8.63 |
| MOSES-nano | 7.90 | 5.49 | 4.75 | 6.49 |
| gpt-4.1-nano | 8.52 | 5.02 | 3.19 | 6.25 |
| gpt-4o | 7.84 | 4.74 | 2.35 | 5.06 |
| spark-chem13b-think | 6.41 | 4.90 | 3.01 | 5.08 |
| spark-chem13b-nothink | 6.23 | 4.60 | 2.68 | 4.67 |
| gpt-4o-mini | 6.32 | 4.07 | 1.85 | 3.83 |
| llasmol-top5 | 1.83 | 0.02 | 0.03 | 0.50 |
| llasmol-top1 | 1.23 | 0.01 | 0.06 | 0.36 |

## Best Answer Rounds Analysis (Excluding Logic/Clarity)

*This shows which answer round performed best for each model using only 4 dimensions.*

### Judge: Doubao-Seed-1.6-combined

| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |
|-------|------------|------------|----------|-------------|-------------|----------|
| gpt-4.1 | 4 | 6.58 | 0.99 | 6.43 - 6.58 | 2.4% | 27 |
| gpt-4.1-nano | 2 | 5.86 | 1.19 | 5.74 - 5.86 | 2.0% | 27 |
| gpt-4o | 1 | 5.29 | 1.54 | 5.13 - 5.29 | 3.3% | 27 |
| gpt-4o-mini | 2 | 4.50 | 1.58 | 4.37 - 4.50 | 3.0% | 27 |
| lightrag-4.1 | 1 | 6.70 | 0.85 | 5.79 - 6.70 | 15.7% | 27 |
| lightrag-4.1-nano | 4 | 6.56 | 1.05 | 5.68 - 6.56 | 15.4% | 27 |
| llasmol-top1 | 2 | 0.54 | 1.02 | 0.50 - 0.54 | 7.4% | 27 |
| llasmol-top5 | 5 | 0.69 | 1.13 | 0.37 - 0.69 | 85.6% | 27 |
| MOSES | 4 | 8.38 | 0.77 | 8.31 - 8.38 | 0.7% | 27 |
| MOSES-nano | 5 | 6.17 | 1.56 | 5.78 - 6.17 | 6.8% | 27 |
| o1 | 4 | 6.37 | 1.27 | 6.30 - 6.37 | 1.2% | 27 |
| o3 | 1 | 7.72 | 1.24 | 7.58 - 7.72 | 1.8% | 27 |
| spark-chem13b-nothink | 3 | 4.91 | 2.16 | 4.32 - 4.91 | 13.4% | 27 |
| spark-chem13b-think | 2 | 5.05 | 1.92 | 4.58 - 5.05 | 10.4% | 27 |

### Judge: fxx_gemini2.5-pro

| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |
|-------|------------|------------|----------|-------------|-------------|----------|
| gpt-4.1 | 1 | 7.29 | 1.00 | 7.03 - 7.29 | 3.7% | 27 |
| gpt-4.1-nano | 2 | 5.83 | 1.74 | 5.65 - 5.83 | 3.2% | 27 |
| gpt-4o | 1 | 5.04 | 1.74 | 4.94 - 5.04 | 1.9% | 27 |
| gpt-4o-mini | 1 | 4.11 | 2.19 | 3.88 - 4.11 | 6.0% | 27 |
| lightrag-4.1 | 1 | 7.84 | 1.41 | 7.00 - 7.84 | 12.0% | 27 |
| lightrag-4.1-nano | 2 | 7.81 | 1.08 | 6.45 - 7.81 | 21.0% | 27 |
| llasmol-top1 | 5 | 0.43 | 0.86 | 0.41 - 0.43 | 5.5% | 27 |
| llasmol-top5 | 5 | 0.82 | 1.34 | 0.50 - 0.82 | 63.6% | 27 |
| MOSES | 1 | 9.23 | 0.92 | 9.00 - 9.23 | 2.6% | 27 |
| MOSES-nano | 2 | 6.53 | 2.14 | 5.94 - 6.53 | 10.0% | 27 |
| o1 | 4 | 7.55 | 1.28 | 7.41 - 7.55 | 1.9% | 27 |
| o3 | 3 | 9.01 | 1.03 | 8.70 - 9.01 | 3.6% | 27 |
| spark-chem13b-nothink | 3 | 4.85 | 2.44 | 4.38 - 4.85 | 10.6% | 27 |
| spark-chem13b-think | 2 | 5.19 | 2.41 | 4.64 - 5.19 | 11.8% | 27 |

## Detailed Round Statistics (MOSES and ChemSpark Series)

*Comprehensive round-by-round performance analysis for MOSES and ChemSpark model families using 4 dimensions.*

### Judge: Doubao-Seed-1.6-combined

#### MOSES

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 8.37 | 0.96 | 27 | -0.1% |
| 2 | 8.31 | 0.77 | 27 | -0.7% |
| 3 | 8.34 | 1.18 | 27 | -0.5% |
| 4 | 8.38 | 0.77 | 27 | +0.0% ⭐ |
| 5 | 8.33 | 0.85 | 27 | -0.6% |

#### MOSES-nano

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 6.03 | 1.70 | 27 | -2.3% |
| 2 | 5.89 | 1.52 | 27 | -4.7% |
| 3 | 5.78 | 1.33 | 27 | -6.3% |
| 4 | 5.81 | 1.65 | 27 | -5.8% |
| 5 | 6.17 | 1.56 | 27 | +0.0% ⭐ |

#### spark-chem13b-think

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 4.62 | 2.09 | 27 | -8.5% |
| 2 | 5.05 | 1.92 | 27 | +0.0% ⭐ |
| 3 | 4.77 | 2.04 | 27 | -5.6% |
| 4 | 4.58 | 1.73 | 27 | -9.4% |
| 5 | 5.05 | 1.71 | 27 | -0.1% |

#### spark-chem13b-nothink

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 4.32 | 1.98 | 27 | -11.9% |
| 2 | 4.84 | 2.17 | 27 | -1.4% |
| 3 | 4.91 | 2.16 | 27 | +0.0% ⭐ |
| 4 | 4.59 | 1.70 | 27 | -6.4% |
| 5 | 4.83 | 2.10 | 27 | -1.5% |


### Judge: fxx_gemini2.5-pro

#### MOSES

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 9.23 | 0.92 | 27 | +0.0% ⭐ |
| 2 | 9.00 | 1.06 | 27 | -2.5% |
| 3 | 9.15 | 1.20 | 27 | -0.9% |
| 4 | 9.19 | 0.98 | 27 | -0.4% |
| 5 | 9.14 | 0.93 | 27 | -1.0% |

#### MOSES-nano

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 5.94 | 2.48 | 27 | -9.0% |
| 2 | 6.53 | 2.14 | 27 | +0.0% ⭐ |
| 3 | 6.09 | 2.34 | 27 | -6.7% |
| 4 | 5.96 | 2.49 | 27 | -8.6% |
| 5 | 6.26 | 2.06 | 27 | -4.1% |

#### spark-chem13b-think

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 4.96 | 2.65 | 27 | -4.6% |
| 2 | 5.19 | 2.41 | 27 | +0.0% ⭐ |
| 3 | 4.79 | 2.38 | 27 | -7.8% |
| 4 | 4.64 | 2.55 | 27 | -10.6% |
| 5 | 4.68 | 2.54 | 27 | -9.9% |

#### spark-chem13b-nothink

| Round | Average Score | Std Dev | Questions | Performance vs Best |
|-------|---------------|---------|-----------|---------------------|
| 1 | 4.40 | 2.50 | 27 | -9.1% |
| 2 | 4.43 | 2.78 | 27 | -8.7% |
| 3 | 4.85 | 2.44 | 27 | +0.0% ⭐ |
| 4 | 4.38 | 2.65 | 27 | -9.6% |
| 5 | 4.68 | 2.58 | 27 | -3.5% |


## Model Stability Analysis (Excluding Logic/Clarity)

### Answer Round Volatility

*Measures consistency across different answer rounds using 4 dimensions. Lower CV = more stable.*

#### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Mean Score | Std Dev | CV | Stability |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 8.34 | 0.03 | 0.003 | Excellent |
| 2 | o1 | 6.33 | 0.03 | 0.005 | Excellent |
| 3 | o3 | 7.64 | 0.05 | 0.007 | Excellent |
| 4 | gpt-4.1-nano | 5.81 | 0.04 | 0.007 | Excellent |
| 5 | gpt-4.1 | 6.48 | 0.06 | 0.009 | Excellent |
| 6 | gpt-4o | 5.20 | 0.06 | 0.012 | Excellent |
| 7 | gpt-4o-mini | 4.42 | 0.06 | 0.013 | Excellent |
| 8 | MOSES-nano | 5.94 | 0.16 | 0.027 | Excellent |
| 9 | llasmol-top1 | 0.52 | 0.02 | 0.033 | Excellent |
| 10 | spark-chem13b-think | 4.81 | 0.23 | 0.047 | Excellent |
| 11 | spark-chem13b-nothink | 4.70 | 0.24 | 0.051 | Excellent |
| 12 | lightrag-4.1 | 6.09 | 0.36 | 0.059 | Excellent |
| 13 | lightrag-4.1-nano | 6.35 | 0.38 | 0.059 | Excellent |
| 14 | llasmol-top5 | 0.51 | 0.13 | 0.254 | Fair |

#### Judge: fxx_gemini2.5-pro

| Rank | Model | Mean Score | Std Dev | CV | Stability |
|------|-------|------------|---------|----|-----------|
| 1 | o1 | 7.48 | 0.06 | 0.008 | Excellent |
| 2 | gpt-4o | 5.00 | 0.04 | 0.009 | Excellent |
| 3 | MOSES | 9.14 | 0.09 | 0.010 | Excellent |
| 4 | gpt-4.1-nano | 5.74 | 0.08 | 0.013 | Excellent |
| 5 | o3 | 8.91 | 0.13 | 0.014 | Excellent |
| 6 | gpt-4.1 | 7.16 | 0.11 | 0.015 | Excellent |
| 7 | gpt-4o-mini | 4.02 | 0.10 | 0.025 | Excellent |
| 8 | llasmol-top1 | 0.42 | 0.01 | 0.027 | Excellent |
| 9 | MOSES-nano | 6.16 | 0.24 | 0.040 | Excellent |
| 10 | lightrag-4.1 | 7.31 | 0.32 | 0.044 | Excellent |
| 11 | spark-chem13b-nothink | 4.55 | 0.21 | 0.045 | Excellent |
| 12 | spark-chem13b-think | 4.85 | 0.23 | 0.047 | Excellent |
| 13 | lightrag-4.1-nano | 7.45 | 0.57 | 0.076 | Excellent |
| 14 | llasmol-top5 | 0.60 | 0.13 | 0.219 | Fair |

### Question-to-Question Volatility

*Measures consistency across different questions using 4 dimensions. Lower CV = more consistent.*

#### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Mean Score | Std Dev | CV | Consistency |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 8.34 | 0.47 | 0.056 | Excellent |
| 2 | MOSES-nano | 5.94 | 0.62 | 0.104 | Excellent |
| 3 | o3 | 7.64 | 1.04 | 0.137 | Excellent |
| 4 | lightrag-4.1-nano | 6.35 | 0.97 | 0.152 | Excellent |
| 5 | gpt-4.1 | 6.48 | 1.02 | 0.157 | Excellent |
| 6 | lightrag-4.1 | 6.09 | 1.09 | 0.178 | Excellent |
| 7 | o1 | 6.33 | 1.30 | 0.205 | Good |
| 8 | gpt-4.1-nano | 5.81 | 1.25 | 0.215 | Good |
| 9 | gpt-4o | 5.20 | 1.43 | 0.275 | Good |
| 10 | spark-chem13b-think | 4.81 | 1.65 | 0.342 | Fair |
| 11 | gpt-4o-mini | 4.42 | 1.60 | 0.362 | Fair |
| 12 | spark-chem13b-nothink | 4.70 | 1.80 | 0.383 | Fair |
| 13 | llasmol-top5 | 0.51 | 0.92 | 1.806 | Poor |
| 14 | llasmol-top1 | 0.52 | 0.98 | 1.890 | Poor |

#### Judge: fxx_gemini2.5-pro

| Rank | Model | Mean Score | Std Dev | CV | Consistency |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 9.14 | 0.59 | 0.065 | Excellent |
| 2 | o3 | 8.91 | 1.10 | 0.123 | Excellent |
| 3 | gpt-4.1 | 7.16 | 1.08 | 0.151 | Excellent |
| 4 | lightrag-4.1 | 7.31 | 1.25 | 0.171 | Excellent |
| 5 | o1 | 7.48 | 1.28 | 0.171 | Excellent |
| 6 | lightrag-4.1-nano | 7.45 | 1.32 | 0.177 | Excellent |
| 7 | MOSES-nano | 6.16 | 1.20 | 0.194 | Excellent |
| 8 | gpt-4.1-nano | 5.74 | 1.68 | 0.293 | Good |
| 9 | gpt-4o | 5.00 | 1.65 | 0.331 | Fair |
| 10 | spark-chem13b-think | 4.85 | 2.17 | 0.448 | Poor |
| 11 | gpt-4o-mini | 4.02 | 2.06 | 0.512 | Poor |
| 12 | spark-chem13b-nothink | 4.55 | 2.33 | 0.512 | Poor |
| 13 | llasmol-top5 | 0.60 | 0.87 | 1.460 | Poor |
| 14 | llasmol-top1 | 0.42 | 0.81 | 1.954 | Poor |

## Key Insights Summary (Excluding Logic/Clarity)

### Top Performing Models
1. **MOSES**: 8.34 ± 1.41
2. **o3**: 7.64 ± 1.88
3. **gpt-4.1**: 6.48 ± 1.82

### Most Stable Models (Answer Round Volatility)
1. **MOSES**: CV = 0.003
2. **o1**: CV = 0.005
3. **o3**: CV = 0.007

### Most Consistent Models (Question-to-Question)
1. **MOSES**: CV = 0.056
2. **MOSES-nano**: CV = 0.104
3. **o3**: CV = 0.137

### Data Quality Notes
- **Analysis scope**: Correctness, Completeness, Theoretical Depth, Rigor and Information Density only
- **Excluded dimensions**: Logic and Clarity (assumed not provided by judge models)
- **Total records processed**: 37,800
- **Successfully parsed**: 37,796 (99.99%)
