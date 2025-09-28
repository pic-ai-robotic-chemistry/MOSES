Title: 评估大型语言模型与人类评审的一致性——基于四维度的系统性分析

一、方法概述（Methods）
我们以27道化学知识性与推理性混合问题、4个评价维度（correctness、completeness、theoretical_depth、rigor_and_information_density）为骨架，将9个AI模型在每道题上的得分与3位人类评审的平均分进行一致性评估。核心统计量包括：
- 相关性与排序一致性：Kendall’s τ-b 与 Spearman’s ρ；
- 评分一致性：ICC(A,1) 与 ICC(A,k)；
- 重复性：对每个{模型, 问题, 维度, 提示语}的5次重复作答计算ICC(1,1)；
- 偏差度量：Disagreement_Score = LLM_Avg_Overall − Human_Avg。
图与数据来源：见 out/ 与 out/plots 目录（例如：out/plots/part02_A_scatter_overall.png，out/part02_corr_summary_by_dimension.csv 等）。

二、总体一致性：LLM 与人类的对齐趋势（Results: Overall Alignment）
总体散点与回归趋势（图1，out/plots/part02_A_scatter_overall.png）显示，四个维度均呈正相关，其中 completeness 与 theoretical_depth 的对齐最强；rigor_and_information_density 与 correctness 稍弱但依然显著。分维度的汇总统计（out/part02_corr_summary_by_dimension.csv）为：
- theoretical_depth：τ-b=0.58，ρ=0.72，ICC(A,1)=0.66；
- completeness：τ-b=0.47，ρ=0.60，ICC(A,1)=0.53；
- rigor_and_information_density：τ-b=0.41，ρ=0.51，ICC(A,1)=0.39；
- correctness：τ-b=0.34，ρ=0.43，ICC(A,1)=0.33。
解读：
- 深度（theoretical_depth）与完整性（completeness）上，LLM 的平均评分与人类高度同向，表明模型较好捕捉到了“是否深入展开”和“覆盖是否充分”的判据；
- 严谨/信息密度（rigor_and_information_density）与正确性（correctness）存在明显但相对较弱的对齐，回归斜率通常低于y=x，提示 LLM 在高分区间有“压缩”现象（预测幅度保守、分布更集中）。

三、按模型分层：一致性存在显著异质性（By-model Heterogeneity）
森林图与分模型散点（图2–3，out/plots/part02_B1_scatter_by_model_main.png、out/plots/part02_B2_scatter_by_model_nano.png、out/plots/part03_kendall_forest.png）揭示不同模型在不同维度上的一致性差异：
- completeness：GPT-4o 在 τ-b 上最高（≈0.73），GPT-4o-mini 亦高（≈0.65），显示其对“覆盖面”的判断与人类最为一致；
- theoretical_depth：GPT-4.1‑nano 在 τ-b 上最高（≈0.50），次为 GPT-4.1（≈0.38），更擅长把握“理论阐释的层次与内在联系”；
- correctness：GPT-4o-mini 与 GPT-4.1‑nano 领先（≈0.61 与 ≈0.51），提示其对“是否正确”的评分排序更贴近人类；
- rigor_and_information_density：GPT-4o-mini 领先（≈0.53），GPT-4o 与 GPT-4.1‑nano 中等（≈0.32 与 ≈0.25）。
轻量型RAG与部分开源/小参数模型在 theoretical_depth 与 rigor 两维上存在较大波动（τ-b 常低于0.2），说明对复杂论证质量的捕捉仍具挑战。

四、人类标注的一致性与显著性（Human Reliability）
我们以每道题跨9个模型的评分，计算三名评审之间的 ICC。结果见图4（out/plots/part03_human_icc_forest.png、out/plots/part03_human_iccAk_forest.png）与表格（out/part02_human_internal_icc_by_question_dim.csv）：
- 多数题目在 completeness 与 theoretical_depth 上达到中高一致性（ICC(A,1)常见0.60–0.95），rigor 维度波动较大，个别题目出现低或负ICC；
- 汇总层面（out/part03_coach_human_icc_by_model_dim.csv），不同模型的样本集上，人类ICC(A,1)多处于0.30–0.78 区间，其中 GPT‑4o 在 correctness 与 rigor 上的人类一致性最高（≈0.78 与 ≈0.71），表明这些样本的可判定性较强；
- 大部分结果p<0.05，统计显著。
结论：人类标注整体可靠，但严谨度维度更依赖题目设计与评分细则，建议后续在该维度加强锚定范式与示例库。

五、模型“自洽性”：重复作答的稳定度（LLM Repeatability）
基于5次重复作答的ICC（out/part04_llm_internal_icc_summary.csv；图5：out/plots/part04_icc_violin_by_model.png 与 out/plots/part04_icc_violin_by_dim.png）：
- 平均 ICC(A,1)=0.79，ICC(A,k)=0.94；
- 所有条目 p<0.01；
- 跨模型与维度的分布窄、离散度小。
解读：在固定提示语与评审器下，模型输出在统计意义上高度可重复，表明“评分差异的主要来源在不同模型/题目本身”，而非随机波动。

六、偏差分析：LLM 对人类的系统性高/低估（Bias）
以 Disagreement_Score 衡量LLM与人类均值的差额（图6：out/plots/part05_disagreement_violin.png；表：out/part05_disagreement_summary.csv）：
- 除 o3 外，其余8个模型的均值均为负，显示相对“保守打分”倾向（整体低于人类均值）；
- 绝对偏差量级：LightRAG 与 GPT‑4o/mini 的负偏差更大（例如 GPT‑4o ≈ −0.88，LightRAG ≈ −1.63），o3 为正偏差（≈ +0.44）。
启示：在以LLM作自动评分器的场景，应按模型-维度做校准；对“偏保守”模型可引入线性后校正或分位数映射，以复原人类评分分布。

七、讨论与意义（Discussion）
- 可推广性：在 completeness 与 theoretical_depth 上，多个主流模型已能稳定复现人类的排序与区分，适合作为弱监督的评分器或候选筛选器。
- 维度差异：rigor 与 correctness 的一致性偏低，可能源于评分标准更依赖“事实核验与论证链完整性”的细粒度证据，建议结合基于证据的Rubric与检索增强评估。
- 生态建议：将“人类一致性（ICC）—模型一致性（τ/ρ）—模型自洽性（ICC重复）—偏差（Disagreement）”四视角联合报告，作为跨数据集与模型的标准化一致性基线。
- 局限：样本量为27题，题目覆盖面与难度分布仍有限；严谨度维度的主观性较高、需要更强锚定；不同评分刻度间的缩放效应可能影响ICC大小。

图注与对应文件
- 图1（总体散点）：out/plots/part02_A_scatter_overall.png
- 图2（分模型散点-主流）：out/plots/part02_B1_scatter_by_model_main.png
- 图3（排序一致性森林）：out/plots/part03_kendall_forest.png
- 图4（人类ICC森林）：out/plots/part03_human_icc_forest.png, out/plots/part03_human_iccAk_forest.png
- 图5（LLM重复性小提琴）：out/plots/part04_icc_violin_by_model.png, out/plots/part04_icc_violin_by_dim.png
- 图6（偏差小提琴）：out/plots/part05_disagreement_violin.png

