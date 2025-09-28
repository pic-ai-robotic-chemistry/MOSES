# 评估数据统计分析方法详细说明

## 概述

本文档详细说明了`test_results/eva_res/src`文件夹中各脚本的统计计算方法。这些脚本对AI模型评估数据进行全面的统计分析，包括基本统计、显著性检验、实用性分析和ELO评级系统。

## 数据结构与处理流程

### 原始数据结构

**输入数据格式** (JSON行格式):
```json
{
  "source": "judge_model_name",         // 评判者模型
  "model_name": "evaluated_model",     // 被评估模型
  "answer_round": "1",                 // 回答轮次 (1-5)
  "question_id": "Q1",                 // 问题ID (Q1-Q27)
  "evaluation_round": 0,               // 评估轮次 (0-4, 每个回答评5次)
  "evaluation_type": "with_reference", // 评估类型
  "dimensions": ["correctness", "completeness", ...], // 评估维度
  "answer": "{'correctness': 8, 'completeness': 7, ...}" // 评分结果JSON
}
```

**数据维度**:
- `correctness`: 正确性 (有参考答案)
- `completeness`: 完整性 (有参考答案)  
- `logic`: 逻辑性 (无参考答案)
- `clarity`: 清晰度 (无参考答案)
- `theoretical_depth`: 理论深度 (无参考答案)
- `rigor_and_information_density`: 严谨性和信息密度 (无参考答案)

### 数据清洗与预处理

#### 1. JSON解析处理 (`individual.py:119-211`)

**处理步骤**:
1. **Markdown代码块清理**: 移除```json和````标记
2. **截断JSON修复**: 自动补全不完整的JSON结构
   - 缺少引号: `"key": "value` → `"key": "value"}`
   - 缺少值: `"key":` → `"key": null}`
   - 缺少结束括号: 自动添加`}`

**数据质量统计**:
- `array_wrapped_scores`: 数组包装的分数数量
- `invalid_scores`: 超出0-10范围的无效分数
- `missing_evaluations`: 缺失的评估
- `json_parse_errors`: JSON解析错误
- `incomplete_evaluation_sets`: 不完整的评估集合

#### 2. 评分提取 (`individual.py:83-95`)

**多格式处理**:
```python
def extract_score(score_value):
    if isinstance(score_value, list):
        return float(score_value[0])  # [8] → 8.0
    elif isinstance(score_value, (int, float)):
        return float(score_value)     # 8 → 8.0
    else:
        return None                   # 无效值
```

#### 3. 评判者模型合并 (`individual.py:105-107`)

**合并策略**:
```python
if judge_model in ["Doubao-Seed-1.6-no", "shsy_doubao-seed-1-6-no"]:
    judge_model = "Doubao-Seed-1.6-combined"
```

## 核心统计计算方法

### 1. 基础统计分析 (`individual.py`)

#### 模型平均分计算 (`calculate_model_average_scores`)

**数据聚合层次**:
1. **评估层次**: 5次评估 → 维度平均分
2. **问题-轮次层次**: 各维度平均分 → 评估类型平均分
3. **模型层次**: 所有评估类型平均分 → 模型总体平均分

**计算公式**:
```python
# 第1步: 维度内评估聚合
dimension_avg = mean([score1, score2, score3, score4, score5])

# 第2步: 评估类型聚合
with_reference_avg = mean([correctness_avg, completeness_avg])
without_reference_avg = mean([logic_avg, clarity_avg, theoretical_depth_avg, rigor_avg])

# 第3步: 模型总体聚合  
model_overall_avg = mean([all_evaluation_type_averages])
model_overall_std = stdev([all_evaluation_type_averages])
```

**输出结构**:
```json
{
  "judge_model": {
    "evaluated_model": {
      "overall_average": 7.39,
      "overall_std": 1.43,
      "dimension_averages": {
        "correctness": 8.47,
        "completeness": 6.62,
        ...
      },
      "total_evaluations": 270
    }
  }
}
```

#### 最佳回答轮次分析 (`find_best_answer_rounds`)

**方法**: 为每个模型找出表现最好的回答轮次

**计算步骤**:
1. 计算每个问题在该轮次的所有维度平均分
2. 计算该轮次所有问题的平均分和标准差
3. 选择平均分最高的轮次作为最佳轮次

```python
# 伪代码
for answer_round in [1,2,3,4,5]:
    round_scores = []
    for question in questions:
        question_scores = [mean(dimension_scores) for dimension in dimensions]
        round_scores.append(mean(question_scores))
    
    round_stats[answer_round] = {
        "mean": mean(round_scores),
        "std": stdev(round_scores),
        "count": len(round_scores)
    }

best_round = max(round_stats, key=lambda k: round_stats[k]["mean"])
```

#### 稳定性分析

**回答轮次波动性** (`calculate_answer_round_volatility`):
- **指标**: 变异系数 (CV = σ/μ)
- **含义**: 衡量模型在不同回答轮次间的一致性
- **计算**: CV < 0.1 (优秀), 0.1-0.2 (良好), >0.3 (较差)

**问题间波动性** (`calculate_question_volatility`):
- **指标**: 不同问题表现的变异系数
- **含义**: 衡量模型对不同问题类型的适应性

### 2. 显著性检验分析 (`significance_analysis.py`)

#### 统计方法选择

**Mann-Whitney U检验** (双样本比较):
- **适用**: 非参数检验，不要求数据正态分布
- **零假设**: 两个模型性能无显著差异
- **替代假设**: 双侧检验

**Kruskal-Wallis H检验** (多样本比较):
- **适用**: 非参数ANOVA，比较多个模型
- **零假设**: 所有模型性能相同
- **后续分析**: 如显著，进行成对比较

**多重比较校正**:
```python
# Bonferroni校正
corrected_p_values = multipletests(
    p_values, 
    alpha=0.05, 
    method='bonferroni'
)[1]
```

#### 效应量计算

**Cohen's d** (标准化效应量):
```python
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    s1, s2 = std(group1, ddof=1), std(group2, ddof=1)
    
    # 合并标准差
    pooled_std = sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))
    
    # Cohen's d
    return (mean(group1) - mean(group2)) / pooled_std
```

**效应量解释**:
- |d| < 0.2: 小效应
- 0.2 ≤ |d| < 0.5: 中等效应  
- 0.5 ≤ |d| < 0.8: 大效应
- |d| ≥ 0.8: 很大效应

#### Bootstrap置信区间

```python
def bootstrap_ci(data, n_bootstrap=1000, confidence=0.95):
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))
    
    lower_pct = (1-confidence)/2 * 100
    upper_pct = (1+confidence)/2 * 100
    
    return np.percentile(bootstrap_means, [lower_pct, upper_pct])
```

### 3. 实用显著性分析 (`practical_significance_analysis.py`)

#### 模型分组策略

**实用比较组定义**:
```python
model_groups = {
    "gpt_family": ["gpt-4.1", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"],
    "moses_family": ["MOSES", "MOSES-nano"], 
    "spark_family": ["spark-chem13b-think", "spark-chem13b-nothink"],
    "flagship_models": ["MOSES", "o3", "gpt-4.1", "o1", "lightrag-4.1-nano"]
}
```

#### Friedman检验

**适用场景**: 重复测量设计，每个问题被所有模型回答
**数据结构**: 行=问题，列=模型
**零假设**: 所有模型的排名分布相同

```python
# 伪代码
friedman_stat, p_value = friedmanchisquare(*model_data)
```

#### 级联显著性分析

**方法**: 对每个模型，找到第一个有显著差异的较低排名模型

**算法**:
1. 按性能排序所有模型
2. 对排名第i的模型，依次与排名i+1, i+2, ...比较
3. 找到第一个有显著差异(p<0.05)的模型
4. 记录"显著性边界"

**输出意义**: 
- 如果模型A在第5名，显著性边界在第8名，说明A与第6、7名无显著差异，但与第8名有显著差异
- 帮助理解模型性能的实际区分度

#### 成对比较策略

**组内比较**:
- 使用Wilcoxon符号秩检验(配对样本)
- 在每个模型组内应用Bonferroni校正

**相邻排名比较**:
- 检验连续排名模型间的显著性
- 识别哪些排名差异具有统计学意义

### 4. TrueSkill ELO评级系统

#### 原始实现的问题 (`trueskill_elo_analysis.py`)

**主要缺陷**:
- 完全丢失问题级信息，只使用模型总体平均分
- 完全丢失维度信息，所有维度聚合为单一分数
- 基于模拟数据生成匹配，不反映真实表现模式

#### 修正后的实现 (`trueskill_elo_integrated.py`)

##### TrueSkill算法原理

**贝叶斯技能评级**:
- 每个模型在每个维度的技能: N(μ, σ²)
- μ: 技能水平均值
- σ: 技能不确定性

**参数设置**:
```python
mu = 25.0        # 初始技能均值
sigma = 8.333    # 初始不确定性 (25/3)
beta = 4.167     # 技能差距参数 (sigma/2)
tau = 0.083      # 动态因子 (sigma/100)
```

##### 正确的数据处理流程

**1. 问题-维度级分数提取**:
```python
# 保留问题和维度信息
# judge -> model -> question -> dimension -> avg_score
for question_id in questions:
    for dimension in dimensions:
        # 5次评估 → 维度平均分
        # 5轮回答 → 问题维度平均分
        question_dim_score = mean([round_averages])
```

**2. 维度特定匹配生成**:
```python
# 每个维度独立生成匹配
for dimension in dimensions:
    for question_id in questions:
        for model1, model2 in model_pairs:
            # 基于真实问题-维度分数比较
            score1 = question_dim_data[model1][question_id][dimension]
            score2 = question_dim_data[model2][question_id][dimension]
            winner = model1 if score1 > score2 else model2
```

**3. 维度特定ELO计算**:
```python
# 每个维度独立计算ELO评级
for dimension in dimensions:
    dimension_matches = matches[dimension]
    dimension_elos = calculate_trueskill(dimension_matches)
```

**4. 多维度ELO聚合**:
```python
def aggregate_elos(dimension_elos, method="weighted_mean"):
    if method == "weighted_mean":
        # 按比赛数量加权平均
        weights = [elo.games_played for elo in dimension_elos]
        overall_elo = weighted_average(elos, weights)
    elif method == "mean":
        # 简单平均
        overall_elo = mean([elo.rating for elo in dimension_elos])
    elif method == "conservative":
        # 最保守估计（最小值）
        overall_elo = min([elo.rating for elo in dimension_elos])
    elif method == "optimistic":
        # 最乐观估计（最大值）
        overall_elo = max([elo.rating for elo in dimension_elos])
```

##### 输出结构

**维度特定ELO**:
```json
{
  "judge": {
    "dimension": {
      "model": {
        "rating": 23.5,
        "mu": 24.8,
        "sigma": 0.43,
        "games": 135,
        "win_rate": 0.67
      }
    }
  }
}
```

**聚合模型ELO**:
```json
{
  "judge": {
    "model": {
      "overall_elo": 24.2,
      "aggregation_method": "weighted_mean",
      "dimension_ratings": {
        "correctness": {"rating": 25.1, "games": 135},
        "completeness": {"rating": 23.8, "games": 135},
        "theoretical_depth": {"rating": 22.9, "games": 135}
      }
    }
  }
}
```

##### 比赛统计

**真实比赛计数**:
- 27个问题 × N个模型对 × M个维度 = 真实比赛数
- 每个维度：(模型数 × (模型数-1) / 2) × 27 = 维度特定比赛数
- 例：14个模型，6个维度 → (14×13/2)×27×6 = 14,742场比赛

**数据利用率**:
- 完全利用问题级信息：每个问题对ELO贡献独立匹配
- 完全利用维度信息：每个维度获得独立ELO评级
- 完全利用评估信息：5次评估聚合为可靠的分数估计

## 多重评分数据处理策略

### 处理多次评分

#### 策略1: 评估内聚合 (当前实现)
**方法**: 每5次评估 → 1个维度平均分
```python
dimension_avg = mean([eval1, eval2, eval3, eval4, eval5])
```

**优点**: 减少噪声，稳定估计
**缺点**: 丢失评估间变异信息

#### 策略2: 完全展开 (未实现)
**方法**: 将每次评估作为独立数据点
- 27问题 × 5轮次 × 5评估 = 675个数据点/模型

**优点**: 保留所有信息，更准确的统计推断
**缺点**: 增加数据复杂性，需考虑层次结构

### 处理多次回答

#### 当前方法: 分层聚合
1. **问题层次**: 5轮回答在问题内聚合
2. **模型层次**: 27个问题聚合到模型

#### 替代方法: 混合效应模型 (建议改进)
```python
# 伪代码 - 层次线性模型
model = '分数 ~ 模型 + (1|问题) + (1|轮次) + (1|评判者)'
```

## 数据完整性与质量控制

### 完整性检查

**期望数据量**:
- 每个(模型, 问题, 轮次, 评判者, 维度)组合: 5次评估
- 如果27问题 × 5轮次 × 6维度 = 810个评估集合/模型/评判者

**实际检查**:
```python
for dimension_scores in question_data.values():
    if len(dimension_scores) != 5:
        # 记录不完整评估集合
        incomplete_count += 1
```

### 异常值处理

**分数范围检查**:
```python
if not (0 <= score <= 10):
    # 记录无效分数
    invalid_scores.append(score_info)
```

**JSON格式修复**:
- 自动检测和修复常见格式问题
- 记录修复日志供人工审核

## 统计假设与局限性

### 假设
1. **独立性**: 不同问题的评估相互独立
2. **同分布**: 同一维度的分数来自相同分布
3. **缺失随机**: 缺失数据是随机的

### 局限性
1. **数据聚合**: 当前实现丢失了评估内变异
2. **伪数据生成**: TrueSkill和部分分析使用模拟数据
3. **多重比较**: 大量比较可能增加假阳性率

### 改进建议
1. **保留原始数据**: 在统计分析中使用完整的层次结构
2. **混合效应模型**: 显式建模层次结构(评估→轮次→问题→模型)
3. **贝叶斯方法**: 使用贝叶斯统计处理不确定性
4. **交叉验证**: 验证统计推断的稳健性

## 实际应用指导

### 使用建议

**选择分析类型**:
- `full`: 包含所有6个维度
- `no_lc`: 排除logic和clarity维度(假设评判者未提供)

**解读统计显著性**:
- 关注Bonferroni校正后的p值
- 结合效应量判断实用显著性
- 考虑置信区间的重叠

**模型比较策略**:
1. 先查看整体排名(基础统计)
2. 检验显著性差异(显著性分析) 
3. 关注实用比较(实用显著性分析)
4. 考虑动态评级(TrueSkill分析)

**结果解释注意事项**:
- 统计显著 ≠ 实用重要
- 考虑效应量大小
- 注意多重比较问题
- 关注模型稳定性指标

## 技术实现细节

### 依赖库

**核心统计**:
- `scipy.stats`: 统计检验
- `numpy`: 数值计算
- `pandas`: 数据操作

**专业方法**:
- `trueskill`: ELO评级系统
- `statsmodels`: 高级统计分析

### 性能考虑

**内存使用**:
- 大文件逐行读取
- 增量统计计算

**计算复杂度**:
- 成对比较: O(n²)
- TrueSkill更新: O(matches)

### 输出格式

**JSON文件**: 完整数据，程序间交互
**Markdown文件**: 人类可读报告，包含表格和解释

## 修正后的ELO实现使用指导

### 推荐使用方法

**步骤1**: 运行基础数据处理
```python
from individual import IndividualEvaluationAnalyzer
analyzer = IndividualEvaluationAnalyzer()
analyzer.load_data()
analyzer.process_data()  # 得到processed_data
```

**步骤2**: 运行修正的TrueSkill分析
```python
from trueskill_elo_integrated import IntegratedTrueSkillAnalyzer
trueskill_analyzer = IntegratedTrueSkillAnalyzer(analyzer.processed_data)

# 运行分析（支持不同聚合方法）
results = trueskill_analyzer.run_analysis("full", "weighted_mean")
trueskill_analyzer.save_results(results, "trueskill_corrected.json")
```

### 聚合方法选择

**weighted_mean** (推荐):
- 按比赛数量加权，更可靠的维度权重更高
- 适用于不同维度比赛数差异较大的情况

**mean**:
- 简单算术平均，所有维度等权重
- 适用于认为所有维度同等重要的情况

**conservative**:
- 取最低维度ELO，保守估计
- 适用于风险敏感的场景

**optimistic**:
- 取最高维度ELO，乐观估计
- 适用于识别潜力的场景

### 结果解读

**维度特定ELO**:
- 反映模型在特定维度的技能水平
- 可识别模型的优势和劣势维度

**整体ELO**:
- 综合所有维度的技能评估
- 提供模型的总体排名参考

**与其他分析的对比**:
- ELO评级：动态竞争评级，反映相对强弱
- 基础统计：绝对分数，反映绝对表现
- 显著性检验：统计差异，反映差异可信度

这套修正后的实现真正实现了基于问题和维度的有意义ELO评级，为模型评估提供了更加精确和有用的排名系统。