# Individual Evaluation Analysis Summary

## Data Quality Summary

- **Total records**: 40500
- **Array wrapped scores**: 18622
- **Invalid scores**: 0
- **Missing evaluations**: 4
- **JSON parse errors**: 4
- **Incomplete evaluation sets**: 21

### All JSON Parse Errors
1. **fxx_gemini2.5-pro_llasmol-top5_1_q_27_3**
   - Original length: 69 chars
   - Original: ````json
{
  "logic": 0,
  "clarity": 0,
  "theoretical_depth": 0,
  "`
   - Cleaned: `{
  "logic": 0,
  "clarity": 0,
  "theoretical_depth": 0,
  "`
   - **Issue**: Likely truncated - ends with quote, missing closing brace
   - Fix attempted: `{
  "logic": 0,
  "clarity": 0,
  "theoretical_depth": 0,
  ""}...`

2. **fxx_gemini2.5-pro_llasmol-top5_5_q_19_3**
   - Original length: 7 chars
   - Original: ````json`
   - Cleaned: ````json`

3. **fxx_gemini2.5-pro_MOSES_5_q_2_3**
   - Original length: 62 chars
   - Original: ````json
{
  "logic": 10,
  "clarity": 10,
  "theoretical_depth`
   - Cleaned: `{
  "logic": 10,
  "clarity": 10,
  "theoretical_depth`
   - **Issue**: Unmatched braces (missing 1 closing braces)
   - Fix attempted: `{
  "logic": 10,
  "clarity": 10,
  "theoretical_depth}...`

4. **fxx_gemini2.5-pro_spark-chem13b-think_1_q_27_3**
   - Original length: 3 chars
   - Original: `````
   - Cleaned: `````


### Detailed Analysis of All Incomplete Evaluation Sets

| # | Judge | Model | Round | Question | Dimension | Count | Expected |
|---|-------|-------|--------|----------|-----------|--------|----------|
| 1 | fxx_gemini2.5-pro | lightrag-4.1-nano | 3 | q_9 | logic | 4 | 5 |
| 2 | fxx_gemini2.5-pro | lightrag-4.1-nano | 3 | q_9 | clarity | 4 | 5 |
| 3 | fxx_gemini2.5-pro | lightrag-4.1-nano | 3 | q_9 | theoretical_depth | 4 | 5 |
| 4 | fxx_gemini2.5-pro | lightrag-4.1-nano | 3 | q_9 | rigor_and_information_density | 4 | 5 |
| 5 | fxx_gemini2.5-pro | llasmol-top1 | 2 | q_13 | correctness | 4 | 5 |
| 6 | fxx_gemini2.5-pro | llasmol-top1 | 2 | q_13 | completeness | 4 | 5 |
| 7 | fxx_gemini2.5-pro | llasmol-top5 | 1 | q_27 | logic | 4 | 5 |
| 8 | fxx_gemini2.5-pro | llasmol-top5 | 1 | q_27 | clarity | 4 | 5 |
| 9 | fxx_gemini2.5-pro | llasmol-top5 | 1 | q_27 | theoretical_depth | 4 | 5 |
| 10 | fxx_gemini2.5-pro | llasmol-top5 | 1 | q_27 | rigor_and_information_density | 4 | 5 |
| 11 | fxx_gemini2.5-pro | llasmol-top5 | 5 | q_19 | correctness | 4 | 5 |
| 12 | fxx_gemini2.5-pro | llasmol-top5 | 5 | q_19 | completeness | 4 | 5 |
| 13 | fxx_gemini2.5-pro | MOSES | 5 | q_2 | logic | 4 | 5 |
| 14 | fxx_gemini2.5-pro | MOSES | 5 | q_2 | clarity | 4 | 5 |
| 15 | fxx_gemini2.5-pro | MOSES | 5 | q_2 | theoretical_depth | 4 | 5 |
| 16 | fxx_gemini2.5-pro | MOSES | 5 | q_2 | rigor_and_information_density | 4 | 5 |
| 17 | fxx_gemini2.5-pro | o1 | 5 | q_14 | rigor_and_information_density | 4 | 5 |
| 18 | fxx_gemini2.5-pro | spark-chem13b-think | 1 | q_27 | correctness | 4 | 5 |
| 19 | fxx_gemini2.5-pro | spark-chem13b-think | 1 | q_27 | completeness | 4 | 5 |
| 20 | fxx_gemini2.5-pro | spark-chem13b-think | 3 | q_23 | correctness | 4 | 5 |
| 21 | fxx_gemini2.5-pro | spark-chem13b-think | 3 | q_23 | completeness | 4 | 5 |

#### Patterns in Incomplete Sets

- **fxx_gemini2.5 → pro → lightrag-4.1-nano-logic**: 1 incomplete sets at R3Qq_9
- **fxx_gemini2.5 → pro → lightrag-4.1-nano-clarity**: 1 incomplete sets at R3Qq_9
- **fxx_gemini2.5 → pro → lightrag-4.1-nano-theoretical_depth**: 1 incomplete sets at R3Qq_9
- **fxx_gemini2.5 → pro → lightrag-4.1-nano-rigor_and_information_density**: 1 incomplete sets at R3Qq_9
- **fxx_gemini2.5 → pro → llasmol-top1-correctness**: 1 incomplete sets at R2Qq_13
- **fxx_gemini2.5 → pro → llasmol-top1-completeness**: 1 incomplete sets at R2Qq_13
- **fxx_gemini2.5 → pro → llasmol-top5-logic**: 1 incomplete sets at R1Qq_27
- **fxx_gemini2.5 → pro → llasmol-top5-clarity**: 1 incomplete sets at R1Qq_27
- **fxx_gemini2.5 → pro → llasmol-top5-theoretical_depth**: 1 incomplete sets at R1Qq_27
- **fxx_gemini2.5 → pro → llasmol-top5-rigor_and_information_density**: 1 incomplete sets at R1Qq_27
- **fxx_gemini2.5 → pro → llasmol-top5-correctness**: 1 incomplete sets at R5Qq_19
- **fxx_gemini2.5 → pro → llasmol-top5-completeness**: 1 incomplete sets at R5Qq_19
- **fxx_gemini2.5 → pro → MOSES-logic**: 1 incomplete sets at R5Qq_2
- **fxx_gemini2.5 → pro → MOSES-clarity**: 1 incomplete sets at R5Qq_2
- **fxx_gemini2.5 → pro → MOSES-theoretical_depth**: 1 incomplete sets at R5Qq_2
- **fxx_gemini2.5 → pro → MOSES-rigor_and_information_density**: 1 incomplete sets at R5Qq_2
- **fxx_gemini2.5 → pro → o1-rigor_and_information_density**: 1 incomplete sets at R5Qq_14
- **fxx_gemini2.5 → pro → spark-chem13b-think-correctness**: 2 incomplete sets at R1Qq_27, R3Qq_23
- **fxx_gemini2.5 → pro → spark-chem13b-think-completeness**: 2 incomplete sets at R1Qq_27, R3Qq_23

## Judge Models Overview

| Judge Model | Total Evaluations | Data Completeness |
|-------------|-------------------|-------------------|
| Doubao-Seed-1.6-combined | 4050 | Complete (200.0%) |
| fxx_gemini2.5-pro | 4050 | Complete (200.0%) |

## Model Average Scores by Judge

### Judge: Doubao-Seed-1.6-combined

*Total evaluations: 4050*

#### Overall Ranking

| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |
|------|-------|---------------|---------|-------------|----------|
| 1 | MOSES | 8.80 | 1.14 | 270 | 270/270 (100.0%) |
| 2 | o3 | 8.38 | 1.39 | 270 | 270/270 (100.0%) |
| 3 | gpt-4.1 | 7.39 | 1.43 | 270 | 270/270 (100.0%) |
| 4 | o1 | 7.18 | 1.67 | 270 | 270/270 (100.0%) |
| 5 | lightrag-4.1-nano | 7.07 | 1.32 | 270 | 270/270 (100.0%) |
| 6 | lightrag-4.1 | 6.80 | 1.46 | 270 | 270/270 (100.0%) |
| 7 | gpt-4.1-nano | 6.71 | 1.57 | 270 | 270/270 (100.0%) |
| 8 | MOSES-nano | 6.65 | 1.84 | 270 | 270/270 (100.0%) |
| 9 | gpt-4o | 6.19 | 1.74 | 270 | 270/270 (100.0%) |
| 10 | spark-chem13b-think | 5.63 | 2.21 | 270 | 270/270 (100.0%) |
| 11 | spark-chem13b-nothink | 5.58 | 2.27 | 270 | 270/270 (100.0%) |
| 12 | gpt-4o-mini | 5.41 | 1.93 | 270 | 270/270 (100.0%) |
| 13 | llasmol-top5 | 0.80 | 1.57 | 270 | 270/270 (100.0%) |
| 14 | llasmol-top1 | 0.80 | 1.53 | 270 | 270/270 (100.0%) |
| 15 | darwin | 0.32 | 0.80 | 270 | 270/270 (100.0%) |

#### Dimension-wise Scores

| Model | Correctness | Completeness | Logic | Clarity | Theoretical Depth | Rigor And Information Density |
|-------|-------:|-------:|-------:|-------:|-------:|-------:|
| MOSES | 9.56 | 8.72 | 9.44 | 9.33 | 6.51 | 8.58 |
| o3 | 9.29 | 7.87 | 9.69 | 9.65 | 4.55 | 8.84 |
| gpt-4.1 | 8.47 | 6.62 | 8.94 | 9.17 | 3.20 | 7.65 |
| o1 | 8.29 | 5.51 | 9.09 | 9.28 | 3.60 | 7.91 |
| lightrag-4.1-nano | 8.02 | 6.02 | 8.46 | 8.69 | 4.03 | 7.35 |
| lightrag-4.1 | 7.63 | 5.52 | 8.36 | 8.55 | 4.03 | 7.19 |
| gpt-4.1-nano | 7.86 | 5.35 | 8.42 | 8.85 | 3.12 | 6.90 |
| MOSES-nano | 7.55 | 5.31 | 8.13 | 8.51 | 4.00 | 6.88 |
| gpt-4o | 6.96 | 4.88 | 8.16 | 8.74 | 2.75 | 6.20 |
| spark-chem13b-think | 6.33 | 4.37 | 7.35 | 7.69 | 2.79 | 5.76 |
| spark-chem13b-nothink | 6.34 | 4.34 | 7.40 | 7.76 | 2.59 | 5.52 |
| gpt-4o-mini | 5.84 | 4.07 | 7.55 | 8.18 | 2.43 | 5.35 |
| llasmol-top5 | 1.21 | 0.11 | 1.26 | 1.78 | 0.10 | 0.61 |
| llasmol-top1 | 1.17 | 0.14 | 1.30 | 1.68 | 0.16 | 0.60 |
| darwin | 0.21 | 0.04 | 0.63 | 1.05 | 0.04 | 0.38 |

### Judge: fxx_gemini2.5-pro

*Total evaluations: 4050*

#### Overall Ranking

| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |
|------|-------|---------------|---------|-------------|----------|
| 1 | MOSES | 9.32 | 1.09 | 270 | 270/270 (100.0%) |
| 2 | o3 | 9.14 | 1.48 | 270 | 270/270 (100.0%) |
| 3 | o1 | 8.04 | 1.92 | 270 | 270/270 (100.0%) |
| 4 | gpt-4.1 | 7.98 | 1.46 | 270 | 270/270 (100.0%) |
| 5 | lightrag-4.1-nano | 7.95 | 1.64 | 270 | 270/270 (100.0%) |
| 6 | lightrag-4.1 | 7.83 | 1.68 | 270 | 270/270 (100.0%) |
| 7 | MOSES-nano | 6.78 | 2.34 | 270 | 270/270 (100.0%) |
| 8 | gpt-4.1-nano | 6.73 | 1.85 | 270 | 270/270 (100.0%) |
| 9 | gpt-4o | 6.21 | 1.96 | 270 | 270/270 (100.0%) |
| 10 | spark-chem13b-think | 5.58 | 2.63 | 270 | 270/270 (100.0%) |
| 11 | spark-chem13b-nothink | 5.37 | 2.64 | 270 | 270/270 (100.0%) |
| 12 | gpt-4o-mini | 5.10 | 2.41 | 270 | 270/270 (100.0%) |
| 13 | llasmol-top5 | 0.94 | 1.75 | 270 | 270/270 (100.0%) |
| 14 | llasmol-top1 | 0.72 | 1.44 | 270 | 270/270 (100.0%) |
| 15 | darwin | 0.47 | 1.17 | 270 | 270/270 (100.0%) |

#### Dimension-wise Scores

| Model | Correctness | Completeness | Logic | Clarity | Theoretical Depth | Rigor And Information Density |
|-------|-------:|-------:|-------:|-------:|-------:|-------:|
| MOSES | 9.67 | 8.60 | 9.81 | 9.89 | 8.68 | 9.62 |
| o3 | 9.38 | 8.16 | 9.93 | 9.99 | 8.26 | 9.86 |
| o1 | 9.11 | 5.43 | 9.92 | 9.92 | 6.03 | 9.34 |
| gpt-4.1 | 9.18 | 6.59 | 9.73 | 9.68 | 4.27 | 8.63 |
| lightrag-4.1-nano | 9.10 | 5.96 | 9.35 | 9.37 | 6.19 | 8.56 |
| lightrag-4.1 | 9.16 | 5.46 | 9.39 | 9.37 | 6.23 | 8.38 |
| MOSES-nano | 7.90 | 5.49 | 7.86 | 8.37 | 4.75 | 6.49 |
| gpt-4.1-nano | 8.52 | 5.02 | 8.70 | 8.63 | 3.19 | 6.25 |
| gpt-4o | 7.84 | 4.74 | 8.32 | 8.77 | 2.35 | 5.06 |
| spark-chem13b-think | 6.41 | 4.90 | 6.44 | 7.47 | 3.01 | 5.08 |
| spark-chem13b-nothink | 6.23 | 4.60 | 6.11 | 7.84 | 2.68 | 4.67 |
| gpt-4o-mini | 6.32 | 4.07 | 6.70 | 7.65 | 1.85 | 3.83 |
| llasmol-top5 | 1.83 | 0.02 | 1.28 | 1.97 | 0.03 | 0.50 |
| llasmol-top1 | 1.23 | 0.01 | 0.99 | 1.89 | 0.06 | 0.36 |
| darwin | 0.75 | 0.07 | 0.64 | 1.22 | 0.04 | 0.24 |

## Best Answer Rounds Analysis

*This shows which answer round (attempt) performed best for each model with detailed statistics.*

### Judge: Doubao-Seed-1.6-combined

| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |
|-------|------------|------------|----------|-------------|-------------|----------|
| gpt-4.1 | 4 | 7.41 | 0.67 | 7.31 - 7.41 | 1.3% | 27 |
| gpt-4.1-nano | 2 | 6.83 | 0.88 | 6.69 - 6.83 | 2.0% | 27 |
| gpt-4o | 1 | 6.37 | 1.24 | 6.24 - 6.37 | 2.0% | 27 |
| gpt-4o-mini | 2 | 5.62 | 1.36 | 5.53 - 5.62 | 1.6% | 27 |
| lightrag-4.1 | 1 | 7.37 | 0.66 | 6.63 - 7.37 | 11.1% | 27 |
| lightrag-4.1-nano | 4 | 7.26 | 0.81 | 6.53 - 7.26 | 11.1% | 27 |
| llasmol-top1 | 2 | 0.88 | 1.57 | 0.80 - 0.88 | 8.9% | 27 |
| llasmol-top5 | 5 | 1.09 | 1.70 | 0.71 - 1.09 | 53.7% | 27 |
| MOSES | 4 | 8.71 | 0.57 | 8.67 - 8.71 | 0.5% | 27 |
| MOSES-nano | 5 | 6.89 | 1.35 | 6.62 - 6.89 | 4.1% | 27 |
| o1 | 4 | 7.33 | 0.89 | 7.26 - 7.33 | 0.9% | 27 |
| o3 | 1 | 8.37 | 0.88 | 8.27 - 8.37 | 1.2% | 27 |
| spark-chem13b-nothink | 3 | 5.83 | 1.84 | 5.37 - 5.83 | 8.5% | 27 |
| spark-chem13b-think | 2 | 5.93 | 1.66 | 5.53 - 5.93 | 7.1% | 27 |
| darwin | 3 | 0.46 | 0.83 | 0.26 - 0.46 | 80.7% | 27 |

#### Detailed Round Statistics (MOSES & Spark-Chem Models)

##### MOSES

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 8.71 | 0.75 | 27 | Good |
| 2 | 8.67 | 0.62 | 27 | Good |
| 3 | 8.67 | 0.89 | 27 | Good |
| 4 | 8.71 | 0.57 | 27 | **BEST** |
| 5 | 8.70 | 0.63 | 27 | Good |

##### MOSES-nano

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 6.77 | 1.46 | 27 | Average |
| 2 | 6.69 | 1.25 | 27 | Average |
| 3 | 6.62 | 1.07 | 27 | Average |
| 4 | 6.68 | 1.25 | 27 | Average |
| 5 | 6.89 | 1.35 | 27 | **BEST** |

##### spark-chem13b-nothink

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 5.37 | 1.77 | 27 | Average |
| 2 | 5.75 | 1.78 | 27 | Average |
| 3 | 5.83 | 1.84 | 27 | **BEST** |
| 4 | 5.59 | 1.43 | 27 | Average |
| 5 | 5.76 | 1.81 | 27 | Average |

##### spark-chem13b-think

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 5.56 | 1.87 | 27 | Average |
| 2 | 5.93 | 1.66 | 27 | **BEST** |
| 3 | 5.68 | 1.77 | 27 | Average |
| 4 | 5.53 | 1.51 | 27 | Average |
| 5 | 5.88 | 1.46 | 27 | Average |

#### Round Comparison Summary

*Average performance across all models by round*

| Round | Avg Score | Models | Best Model | Worst Model |
|-------|-----------|--------|------------|-------------|
| 1 | 5.60 | 15 | MOSES (8.71) | darwin (0.40) |
| 2 | 5.63 | 15 | MOSES (8.67) | darwin (0.26) |
| 3 | 5.62 | 15 | MOSES (8.67) | darwin (0.46) |
| 4 | 5.62 | 15 | MOSES (8.71) | darwin (0.46) |
| 5 | 5.66 | 15 | MOSES (8.70) | darwin (0.38) |


### Judge: fxx_gemini2.5-pro

| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |
|-------|------------|------------|----------|-------------|-------------|----------|
| gpt-4.1 | 1 | 8.14 | 0.70 | 7.89 - 8.14 | 3.1% | 27 |
| gpt-4.1-nano | 4 | 6.79 | 1.56 | 6.64 - 6.79 | 2.2% | 27 |
| gpt-4o | 1 | 6.26 | 1.49 | 6.15 - 6.26 | 1.7% | 27 |
| gpt-4o-mini | 2 | 5.25 | 2.16 | 4.90 - 5.25 | 7.1% | 27 |
| lightrag-4.1 | 1 | 8.43 | 1.18 | 7.71 - 8.43 | 9.3% | 27 |
| lightrag-4.1-nano | 2 | 8.42 | 0.86 | 7.24 - 8.42 | 16.3% | 27 |
| llasmol-top1 | 4 | 0.77 | 1.30 | 0.74 - 0.77 | 3.6% | 27 |
| llasmol-top5 | 5 | 1.30 | 2.02 | 0.73 - 1.30 | 77.9% | 27 |
| MOSES | 1 | 9.46 | 0.67 | 9.26 - 9.46 | 2.2% | 27 |
| MOSES-nano | 2 | 7.16 | 1.93 | 6.61 - 7.16 | 8.3% | 27 |
| o1 | 4 | 8.36 | 0.85 | 8.23 - 8.36 | 1.6% | 27 |
| o3 | 1 | 9.33 | 0.80 | 9.11 - 9.33 | 2.5% | 27 |
| spark-chem13b-nothink | 3 | 5.65 | 2.38 | 5.12 - 5.65 | 10.3% | 27 |
| spark-chem13b-think | 2 | 5.77 | 2.37 | 5.17 - 5.77 | 11.6% | 27 |
| darwin | 4 | 0.79 | 1.58 | 0.32 - 0.79 | 146.3% | 27 |

#### Detailed Round Statistics (MOSES & Spark-Chem Models)

##### MOSES

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 9.46 | 0.67 | 27 | **BEST** |
| 2 | 9.26 | 0.90 | 27 | Good |
| 3 | 9.38 | 0.87 | 27 | Good |
| 4 | 9.41 | 0.72 | 27 | Good |
| 5 | 9.38 | 0.70 | 27 | Good |

##### MOSES-nano

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 6.62 | 2.34 | 27 | Average |
| 2 | 7.16 | 1.93 | 27 | **BEST** |
| 3 | 6.83 | 2.17 | 27 | Average |
| 4 | 6.61 | 2.32 | 27 | Average |
| 5 | 6.82 | 1.98 | 27 | Average |

##### spark-chem13b-nothink

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 5.30 | 2.45 | 27 | Average |
| 2 | 5.24 | 2.61 | 27 | Average |
| 3 | 5.65 | 2.38 | 27 | **BEST** |
| 4 | 5.12 | 2.55 | 27 | Average |
| 5 | 5.46 | 2.38 | 27 | Average |

##### spark-chem13b-think

| Round | Mean Score | Std Dev | Questions | Performance |
|-------|------------|---------|-----------|-------------|
| 1 | 5.69 | 2.69 | 27 | Average |
| 2 | 5.77 | 2.37 | 27 | **BEST** |
| 3 | 5.56 | 2.27 | 27 | Average |
| 4 | 5.56 | 2.42 | 27 | Average |
| 5 | 5.17 | 2.55 | 27 | Average |

#### Round Comparison Summary

*Average performance across all models by round*

| Round | Avg Score | Models | Best Model | Worst Model |
|-------|-----------|--------|------------|-------------|
| 1 | 5.90 | 15 | MOSES (9.46) | darwin (0.43) |
| 2 | 5.93 | 15 | MOSES (9.26) | darwin (0.32) |
| 3 | 5.94 | 15 | MOSES (9.38) | darwin (0.59) |
| 4 | 5.93 | 15 | MOSES (9.41) | llasmol-top1 (0.77) |
| 5 | 5.94 | 15 | MOSES (9.38) | darwin (0.33) |


## Model Stability Analysis

### Answer Round Volatility

*Measures consistency across different answer rounds. Lower CV = more stable.*

#### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Mean Score | Std Dev | CV | Stability |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 8.69 | 0.02 | 0.002 | Excellent |
| 2 | o1 | 7.28 | 0.03 | 0.004 | Excellent |
| 3 | o3 | 8.31 | 0.04 | 0.005 | Excellent |
| 4 | gpt-4.1 | 7.34 | 0.04 | 0.005 | Excellent |
| 5 | gpt-4o-mini | 5.57 | 0.04 | 0.007 | Excellent |
| 6 | gpt-4o | 6.28 | 0.05 | 0.008 | Excellent |
| 7 | gpt-4.1-nano | 6.75 | 0.05 | 0.008 | Excellent |
| 8 | MOSES-nano | 6.73 | 0.10 | 0.016 | Excellent |
| 9 | spark-chem13b-think | 5.72 | 0.18 | 0.032 | Excellent |
| 10 | spark-chem13b-nothink | 5.66 | 0.18 | 0.032 | Excellent |
| 11 | llasmol-top1 | 0.84 | 0.03 | 0.036 | Excellent |
| 12 | lightrag-4.1 | 6.88 | 0.29 | 0.042 | Excellent |
| 13 | lightrag-4.1-nano | 7.09 | 0.31 | 0.044 | Excellent |
| 14 | llasmol-top5 | 0.85 | 0.16 | 0.187 | Good |
| 15 | darwin | 0.39 | 0.08 | 0.215 | Fair |

#### Judge: fxx_gemini2.5-pro

| Rank | Model | Mean Score | Std Dev | CV | Stability |
|------|-------|------------|---------|----|-----------|
| 1 | o1 | 8.29 | 0.06 | 0.007 | Excellent |
| 2 | gpt-4o | 6.18 | 0.04 | 0.007 | Excellent |
| 3 | MOSES | 9.38 | 0.08 | 0.008 | Excellent |
| 4 | gpt-4.1-nano | 6.72 | 0.06 | 0.010 | Excellent |
| 5 | o3 | 9.26 | 0.09 | 0.010 | Excellent |
| 6 | gpt-4.1 | 8.01 | 0.09 | 0.012 | Excellent |
| 7 | llasmol-top1 | 0.76 | 0.01 | 0.013 | Excellent |
| 8 | gpt-4o-mini | 5.07 | 0.14 | 0.027 | Excellent |
| 9 | MOSES-nano | 6.81 | 0.22 | 0.032 | Excellent |
| 10 | lightrag-4.1 | 8.00 | 0.28 | 0.035 | Excellent |
| 11 | spark-chem13b-nothink | 5.36 | 0.21 | 0.038 | Excellent |
| 12 | spark-chem13b-think | 5.55 | 0.23 | 0.041 | Excellent |
| 13 | lightrag-4.1-nano | 8.09 | 0.49 | 0.060 | Excellent |
| 14 | llasmol-top5 | 0.94 | 0.22 | 0.231 | Fair |
| 15 | darwin | 0.49 | 0.20 | 0.401 | Poor |

### Question-to-Question Volatility

*Measures consistency across different questions. Lower CV = more consistent.*

#### Judge: Doubao-Seed-1.6-combined

| Rank | Model | Mean Score | Std Dev | CV | Consistency |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 8.69 | 0.35 | 0.040 | Excellent |
| 2 | MOSES-nano | 6.73 | 0.51 | 0.075 | Excellent |
| 3 | o3 | 8.31 | 0.74 | 0.089 | Excellent |
| 4 | gpt-4.1 | 7.34 | 0.71 | 0.097 | Excellent |
| 5 | lightrag-4.1-nano | 7.09 | 0.73 | 0.103 | Excellent |
| 6 | lightrag-4.1 | 6.88 | 0.85 | 0.123 | Excellent |
| 7 | o1 | 7.28 | 0.90 | 0.123 | Excellent |
| 8 | gpt-4.1-nano | 6.75 | 1.00 | 0.148 | Excellent |
| 9 | gpt-4o | 6.28 | 1.13 | 0.180 | Excellent |
| 10 | spark-chem13b-think | 5.72 | 1.36 | 0.238 | Good |
| 11 | gpt-4o-mini | 5.57 | 1.36 | 0.245 | Good |
| 12 | spark-chem13b-nothink | 5.66 | 1.49 | 0.263 | Good |
| 13 | darwin | 0.39 | 0.41 | 1.059 | Poor |
| 14 | llasmol-top5 | 0.85 | 1.39 | 1.642 | Poor |
| 15 | llasmol-top1 | 0.84 | 1.51 | 1.797 | Poor |

#### Judge: fxx_gemini2.5-pro

| Rank | Model | Mean Score | Std Dev | CV | Consistency |
|------|-------|------------|---------|----|-----------|
| 1 | MOSES | 9.38 | 0.45 | 0.048 | Excellent |
| 2 | o3 | 9.26 | 0.73 | 0.079 | Excellent |
| 3 | gpt-4.1 | 8.01 | 0.77 | 0.096 | Excellent |
| 4 | o1 | 8.29 | 0.87 | 0.105 | Excellent |
| 5 | lightrag-4.1 | 8.00 | 1.04 | 0.130 | Excellent |
| 6 | lightrag-4.1-nano | 8.09 | 1.09 | 0.135 | Excellent |
| 7 | MOSES-nano | 6.81 | 1.16 | 0.171 | Excellent |
| 8 | gpt-4.1-nano | 6.72 | 1.46 | 0.218 | Good |
| 9 | gpt-4o | 6.18 | 1.41 | 0.228 | Good |
| 10 | spark-chem13b-think | 5.55 | 2.10 | 0.379 | Fair |
| 11 | spark-chem13b-nothink | 5.36 | 2.16 | 0.404 | Poor |
| 12 | gpt-4o-mini | 5.07 | 2.08 | 0.410 | Poor |
| 13 | darwin | 0.49 | 0.57 | 1.158 | Poor |
| 14 | llasmol-top5 | 0.94 | 1.39 | 1.485 | Poor |
| 15 | llasmol-top1 | 0.76 | 1.32 | 1.742 | Poor |

## Judge Model Reliability Analysis

*Compares how different judge models rate the same answers.*

**Overall Judge Agreement**: CV = 0.257
**Agreement Level**: Fair

### Judge Agreement by Model

| Model | Avg Judge CV | Agreement Level | Measurements |
|-------|--------------|-----------------|---------------|
| gpt-4.1 | 0.131 | Good | 712 |
| gpt-4.1-nano | 0.171 | Good | 731 |
| gpt-4o | 0.209 | Fair | 733 |
| gpt-4o-mini | 0.324 | Poor | 759 |
| lightrag-4.1 | 0.189 | Good | 770 |
| lightrag-4.1-nano | 0.160 | Good | 765 |
| llasmol-top1 | 0.705 | Poor | 194 |
| llasmol-top5 | 0.734 | Poor | 217 |
| MOSES | 0.118 | Good | 626 |
| MOSES-nano | 0.230 | Fair | 755 |
| o1 | 0.161 | Good | 724 |
| o3 | 0.186 | Good | 593 |
| spark-chem13b-nothink | 0.369 | Poor | 744 |
| spark-chem13b-think | 0.336 | Poor | 756 |
| darwin | 0.909 | Poor | 227 |

## Key Insights Summary

### Top Performing Models
1. **MOSES**: 8.80 ± 1.14
2. **o3**: 8.38 ± 1.39
3. **gpt-4.1**: 7.39 ± 1.43

### Most Stable Models (Answer Round Volatility)
1. **MOSES**: CV = 0.002
2. **o1**: CV = 0.004
3. **o3**: CV = 0.005

### Most Consistent Models (Question-to-Question)
1. **MOSES**: CV = 0.040
2. **MOSES-nano**: CV = 0.075
3. **o3**: CV = 0.089

### Data Quality Notes
- **Total records processed**: 40,500
- **Successfully parsed**: 40,496 (99.99%)
- **Complete evaluation sets**: 8,095
- **Judges with complete data**: 0/2
