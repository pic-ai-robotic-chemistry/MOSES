"""
可视化配置文件
定义颜色方案、模型信息和维度映射
"""

import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any

# 颜色配置（参考图片中的配色方案）
COLOR_SCHEME = {
    # 模型配色（更亮更清新的色系，接近 seaborn Accent 并微调）
    'models': {
        # 论文主图常用的6色：红、亮蓝、清新绿、橙/黄、薰衣草紫、薄荷青
        'MOSES': '#E64B35',            # 明亮红（主色）
        'MOSES-nano': '#4DBBD5',       # 亮蓝青
        'gpt-4.1':'#91D1C2',      # 薄荷绿
        'gpt-4.1-nano': '#FDC086',     # 柔和橙（Accent）
        'lightrag-4.1': '#BEAED4',     # 薰衣草
        'lightrag-4.1-nano': '#EFC000',# 鲜黄（微调比 #FFFF99 更稳）
        # 其余模型，保持同系倾向以避免冲突
        'o3': '#386CB0',           # 蓝（Accent 深蓝）
        'gpt-4o': '#F141A8',               # 品红（与红区别开）
        'gpt-4o-mini': '#7FC97F',          # 清新绿（Accent）
    },
    
    # 维度颜色
    'dimensions': {
        '正确性': '#E84855',
        '完备性': '#4472C4', 
        '理论深度': '#70AD47',
        '论述严谨性与信息密度': '#FFC000'
    },
    
    # 通用颜色
    'forest_plot': {
        'point': '#4472C4',
        'error_bar': '#333333',
        'background': '#F8F9FA'
    },
    
    # 雷达图配色
    'radar': {
        'grid': '#CCCCCC',
        'text': '#333333',
        'background': 'white'
    }
}

# 统一的标记样式（用于散点与图例映射）
# 与 MODEL_INFO['order'] 一一对应，避免颜色相近时难以区分
MARKER_SCHEME = {
    'models': {
        'MOSES': 'o',            # circle
        'o3': 's',               # square
        'gpt-4.1': 'D',          # diamond
        'lightrag-4.1-nano': '^',# triangle_up
        'lightrag-4.1': 'v',     # triangle_down
        'MOSES-nano': 'P',       # plus (filled)
        'gpt-4.1-nano': 'X',     # x (filled)
        'gpt-4o': 'H',           # hexagon
        'gpt-4o-mini': '*',      # star
    }
}

# 模型信息
MODEL_INFO = {
    'order': ['MOSES', 'o3', 'gpt-4.1', 'lightrag-4.1-nano', 'lightrag-4.1', 
              'MOSES-nano', 'gpt-4.1-nano', 'gpt-4o', 'gpt-4o-mini'],
    
    'display_names': {
        'MOSES': 'MOSES',
        'o3': 'O3',
        'gpt-4.1': 'GPT-4.1', 
        'lightrag-4.1-nano': 'LightRAG-nano',
        'lightrag-4.1': 'LightRAG',
        'MOSES-nano': 'MOSES-nano',
        'gpt-4.1-nano': 'GPT-4.1-nano',
        'gpt-4o': 'GPT-4o',
        'gpt-4o-mini': 'GPT-4o-mini'
    },
    
    # 顶级模型（用于雷达图）
    'top_models': ['MOSES', 'o3', 'gpt-4.1']
}

# 维度信息
DIMENSION_INFO = {
    'order': ['正确性', '完备性', '理论深度', '论述严谨性与信息密度'],
    
    'display_names': {
        '正确性': 'Correctness',
        '完备性': 'Completeness',
        '理论深度': 'Theoretical Depth', 
        '论述严谨性与信息密度': 'Rigor & Information Density'
    },
    
    'short_names': {
        '正确性': 'Correctness',
        '完备性': 'Completeness',  
        '理论深度': 'Theo. Depth',
        '论述严谨性与信息密度': 'Rigor & Info'
    }
}

# 图表样式配置
PLOT_STYLE = {
    'figure_size': (12, 8),
    'dpi': 300,
    'font_family': 'Arial',
    'font_size': {
        'title': 14,
        'label': 12,
        'tick': 10,
        'legend': 10
    },
    'line_width': 2,
    'marker_size': 8,
    'alpha': 0.7,
    # 统一网格与线型，贴近参考图风格
    'grid_linestyle': (0, (3, 3)),  # dashed
    'grid_color': '#BDBDBD',
    'spine_color': '#222222',
    'tick_color': '#333333'
}

# 文件路径配置
PATHS = {
    'data': {
        'performance': '../src/analysis_summary.md',
        'elo_4dim': '../src/elo15/trueskill_elo_analysis_no_lc.json',
        'consistency': '../consistency_analysis/results/actual_20250902_144907'
    },
    
    'output': {
        'performance_matrix': './plots/performance_matrix/',
        'radar_charts': './plots/radar_charts/', 
        'forest_plots': './plots/forest_plots/'
    }
}

def setup_plot_style():
    """设置全局绘图样式"""
    plt.style.use('default')
    # 使用上面定义的更亮配色作为全局色板，按模型顺序取色
    sns.set_palette([COLOR_SCHEME['models'][model] for model in MODEL_INFO['order'] if model in COLOR_SCHEME['models']])
    
    plt.rcParams.update({
        'font.family': PLOT_STYLE['font_family'],
        'font.size': PLOT_STYLE['font_size']['tick'],
        'axes.labelsize': PLOT_STYLE['font_size']['label'],
        'axes.titlesize': PLOT_STYLE['font_size']['title'],
        'xtick.labelsize': PLOT_STYLE['font_size']['tick'],
        'ytick.labelsize': PLOT_STYLE['font_size']['tick'],
        'legend.fontsize': PLOT_STYLE['font_size']['legend'],
        'figure.dpi': PLOT_STYLE['dpi'],
        'savefig.dpi': PLOT_STYLE['dpi'],
        'savefig.bbox': 'tight',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': PLOT_STYLE['grid_linestyle'],
        'grid.color': PLOT_STYLE['grid_color'],
        'xtick.color': PLOT_STYLE['tick_color'],
        'ytick.color': PLOT_STYLE['tick_color']
    })


# Heatmap 统一色系（与参考图整体冷色调一致，偏蓝）
def get_heatmap_cmap(reverse: bool = False) -> Any:
    """返回统一的热图配色（浅→深蓝）。
    reverse=True 时返回反向（深→浅），用于排名类热图使 Rank=1 更深色。
    """
    base_blue = COLOR_SCHEME['models'].get('MOSES', '#4472C4')
    cmap = sns.light_palette(base_blue, as_cmap=True)
    return cmap.reversed() if reverse else cmap


# 通用的坐标轴微调，确保风格统一
def style_axes(ax):
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_color(PLOT_STYLE['spine_color'])
    ax.spines['bottom'].set_color(PLOT_STYLE['spine_color'])
    if 'right' in ax.spines:
        ax.spines['right'].set_visible(False)
    if 'top' in ax.spines:
        ax.spines['top'].set_visible(False)
    ax.grid(True, linestyle=PLOT_STYLE['grid_linestyle'], color=PLOT_STYLE['grid_color'], alpha=0.4)
