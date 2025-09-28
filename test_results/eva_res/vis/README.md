# 🎨 Nature系列期刊可视化系统

本系统专为Nature系列期刊投稿设计，提供高质量的AI模型评估可视化图表。

## 📋 系统概述

### 数据范围
- **模型数量**: 9个主流AI模型 (MOSES, O3, GPT-4.1, LightRAG-nano, LightRAG, MOSES-nano, GPT-4.1-nano, GPT-4o, GPT-4o-mini)
- **评估维度**: 4个核心维度 (正确性、完备性、理论深度、论述严谨性与信息密度)
- **评分数据**: 豆包Seed-1.6评分 + TrueSkill ELO算法
- **统计基础**: 2,430条评估记录，11,340场ELO匹配

### 可视化类型
1. **性能矩阵热图** - 模型-维度性能对比
2. **顶级模型雷达图** - 多维度性能分析
3. **ELO森林图** - TrueSkill排名展示
4. **分维度ELO雷达图** - 基于ELO的多维对比

## 🚀 快速开始

### 环境要求
```bash
python >= 3.8
matplotlib >= 3.5.0
seaborn >= 0.11.0
pandas >= 1.3.0
numpy >= 1.21.0
```

### 安装依赖
```bash
pip install matplotlib seaborn pandas numpy
```

### 生成所有图表
```bash
cd C:/D/CursorProj/Chem-Ontology-Constructor/test_results/eva_res/vis
python generate_all_plots.py
```

## 📁 目录结构

```
vis/
├── config/                    # 配置文件
│   └── vis_config.py         # 颜色方案和模型配置
├── data_processing/           # 数据处理模块
│   └── data_processor.py     # 数据提取和清洗
├── visualization_scripts/     # 可视化脚本
│   ├── performance_matrix.py # 性能矩阵热图
│   ├── radar_charts.py       # 顶级模型雷达图
│   ├── forest_plots.py       # ELO森林图
│   └── dimension_elo_radar.py# 分维度ELO雷达图
├── plots/                     # 输出图表
│   ├── performance_matrix/   # 热图输出
│   ├── radar_charts/         # 雷达图输出
│   └── forest_plots/         # 森林图输出
├── generate_all_plots.py     # 主生成脚本
└── README.md                 # 说明文档
```

## 🎯 使用指南

### 1. 单独运行脚本

#### 性能矩阵热图
```bash
cd visualization_scripts
python performance_matrix.py
```
生成内容：
- `performance_matrix.png/pdf/svg` - 基础热图
- `performance_matrix_annotated.png/pdf` - 详细注释版
- `performance_matrix_clustered.png/pdf` - 聚类分析版

#### 顶级模型雷达图
```bash
python radar_charts.py
```
生成内容：
- `top_models_radar.png/pdf/svg` - 综合对比雷达图
- `individual_model_radars.png/pdf` - 独立模型分析
- `comparative_radar_analysis.png/pdf` - 绝对vs相对比较

#### ELO森林图
```bash
python forest_plots.py
```
生成内容：
- `elo_forest_plot.png/pdf/svg` - 标准森林图
- `elo_tiered_forest_plot.png/pdf` - 分层展示
- `elo_uncertainty_analysis.png/pdf` - 不确定性分析

#### 分维度ELO雷达图
```bash
python dimension_elo_radar.py
```
生成内容：
- `all_models_elo_radar.png/pdf/svg` - 全模型ELO对比
- `top_models_elo_radar.png/pdf/svg` - 顶级模型ELO分析
- `performance_elo_correlation.png/pdf` - 相关性分析
- `dimension_ranking_heatmap.png/pdf` - 排名热图

### 2. 批量生成所有图表
```bash
python generate_all_plots.py
```

### 3. 自定义配置

编辑 `config/vis_config.py` 来修改：
- 颜色方案 (`COLOR_SCHEME`)
- 模型信息 (`MODEL_INFO`) 
- 维度信息 (`DIMENSION_INFO`)
- 图表样式 (`PLOT_STYLE`)

## 📊 输出规格

### 图表质量
- **分辨率**: 300 DPI (期刊标准)
- **格式**: PNG (展示)、PDF (印刷)、SVG (矢量)
- **颜色**: 统一专业配色方案
- **字体**: Arial (Nature标准)

### 统计严谨性
- **置信区间**: 99.7% (μ ± 3σ)
- **相关系数**: Pearson & Spearman
- **显著性检验**: p值标注
- **贝叶斯评估**: TrueSkill算法

## 🔧 故障排除

### 常见问题

1. **找不到数据文件**
   ```
   FileNotFoundError: 找不到分析摘要文件
   ```
   - 确保 `../src/analysis_summary.md` 存在
   - 确保 `../src/elo15/trueskill_elo_analysis_no_lc.json` 存在

2. **matplotlib配置错误** 
   ```
   KeyError: 'axes.grid.alpha' is not a valid rc parameter
   ```
   - 更新matplotlib版本: `pip install --upgrade matplotlib`

3. **中文字体显示问题**
   ```python
   plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
   plt.rcParams['axes.unicode_minus'] = False
   ```

### 数据更新

如需更新数据源：
1. 修改 `data_processing/data_processor.py` 中的文件路径
2. 调整 `config/vis_config.py` 中的模型列表
3. 重新运行生成脚本

## 📚 技术说明

### 数据处理架构
- **分离设计**: 数据预处理与可视化分离
- **模块化**: 每种图表独立脚本
- **可扩展**: 易于添加新的数据源和图表类型

### 颜色方案
参考提供的小提琴图样式：
- MOSES: #4472C4 (蓝色，最佳模型)
- O3: #E84855 (红色，次佳模型)
- GPT-4.1: #70AD47 (绿色)
- 其他模型使用协调的配色方案

### Nature期刊适配
- 遵循Nature出版规范的图表样式
- 高对比度配色适合黑白印刷
- 清晰的图例和标注
- 适当的图表尺寸比例

## 📈 应用建议

### 论文主图推荐
1. **顶级模型雷达图** (`top_models_radar.png`) - 突出前三名性能
2. **ELO森林图** (`elo_forest_plot.png`) - 展示统计严谨的排名
3. **性能矩阵热图** (`performance_matrix.png`) - 全面性能对比

### 补充材料推荐
1. **聚类热图** - 展示模型相似性
2. **不确定性分析** - 评估排名可靠性
3. **相关性分析** - 验证评分方法一致性

---

**版本**: 1.0
**更新时间**: 2025-01-27
**适用期刊**: Nature系列期刊
**联系信息**: 请通过项目仓库提交issue