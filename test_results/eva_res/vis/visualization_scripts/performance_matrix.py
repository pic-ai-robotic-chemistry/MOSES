"""
性能矩阵热图可视化脚本
创建模型-维度性能矩阵的热图展示
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# 添加配置和数据处理模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_processing'))

from vis_config import (
    COLOR_SCHEME,
    MODEL_INFO,
    DIMENSION_INFO,
    PLOT_STYLE,
    setup_plot_style,
    get_heatmap_cmap,
    style_axes,
)
from data_processor import DataProcessor


class PerformanceMatrixVisualizer:
    """性能矩阵热图可视化器"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = Path(__file__).parent.parent / "plots/performance_matrix"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        setup_plot_style()
    
    def create_heatmap(self, save_format=['png', 'pdf', 'svg']):
        """
        创建性能矩阵热图
        """
        # 获取数据
        matrix, matrix_df = self.processor.create_performance_matrix()
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建热图
        heatmap = sns.heatmap(
            matrix,
            annot=True,
            fmt='.2f',
            cmap=get_heatmap_cmap(),  # 冷色统一（浅→深蓝）
            cbar_kws={'label': 'Performance Score (0-10)'},
            linewidths=0.6,
            linecolor='white',
            ax=ax,
            vmin=0.0,
            vmax=10.0,
            annot_kws={'size': 10, 'weight': 'bold', 'color': '#1f1f1f'},
            square=True,
        )
        
        # 设置标题和标签
        ax.set_title('AI Model Performance Matrix\n(Doubao Judge Evaluation)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Evaluation Dimensions', fontsize=12, fontweight='bold')
        ax.set_ylabel('AI Models', fontsize=12, fontweight='bold')

        # 旋转x轴标签
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        style_axes(ax)
        
        # 调整颜色条
        cbar = heatmap.collections[0].colorbar
        cbar.set_label('Performance Score (0-10)', rotation=270, labelpad=20)
        cbar.set_ticks([0, 2, 4, 6, 8, 10])
        
        # 添加统计信息
        avg_scores = matrix.mean(axis=1).sort_values(ascending=False)
        
        # 在右侧添加平均分数
        for i, (model, score) in enumerate(avg_scores.items()):
            model_idx = matrix.index.get_loc(model)
            ax.text(
                matrix.shape[1] + 0.1,
                model_idx + 0.5,
                f'{score:.2f}',
                ha='left',
                va='center',
                fontweight='bold',
                fontsize=10,
                color='#1f1f1f',
            )
        
        # 添加平均分数标题
        ax.text(matrix.shape[1] + 0.1, -0.5, 'Avg', ha='left', va='center', 
                fontweight='bold', fontsize=11)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"performance_matrix.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"性能矩阵热图已保存: {filepath}")
        
        return fig, ax
    
    def create_annotated_heatmap(self, save_format=['png', 'pdf']):
        """
        创建带详细注释的性能矩阵热图
        """
        # 获取数据
        matrix, matrix_df = self.processor.create_performance_matrix()
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), 
                                      gridspec_kw={'width_ratios': [3, 1]})
        
        # 主热图
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.2f',
            cmap=get_heatmap_cmap(),
            cbar_kws={'label': 'Performance Score', 'shrink': 0.8},
            linewidths=0.6,
            linecolor='white',
            ax=ax1,
            vmin=0.0,
            vmax=10.0,
            annot_kws={'size': 9, 'weight': 'bold', 'color': '#1f1f1f'},
            square=True,
        )
        
        # 设置主图标题和标签
        ax1.set_title('AI Model Performance Matrix\n(4 Dimensions, Doubao Judge)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.set_xlabel('Evaluation Dimensions', fontsize=12, fontweight='bold')
        ax1.set_ylabel('AI Models (Ranked by Overall Score)', fontsize=12, fontweight='bold')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)
        style_axes(ax1)
        
        # 计算统计信息
        model_stats = []
        for model in matrix.index:
            row = matrix.loc[model]
            model_stats.append({
                'model': model,
                'mean': row.mean(),
                'std': row.std(),
                'min': row.min(),
                'max': row.max(),
                'range': row.max() - row.min()
            })
        
        stats_df = pd.DataFrame(model_stats)
        
        # 创建统计信息表格
        ax2.axis('off')
        ax2.set_title('Model Statistics', fontsize=12, fontweight='bold')
        
        # 创建表格数据
        table_data = []
        for _, row in stats_df.iterrows():
            table_data.append([
                row['model'],
                f"{row['mean']:.2f}",
                f"{row['std']:.2f}", 
                f"{row['range']:.2f}"
            ])
        
        # 创建表格
        table = ax2.table(cellText=table_data,
                         colLabels=['Model', 'Mean', 'Std', 'Range'],
                         cellLoc='center',
                         loc='upper left',
                         colWidths=[0.35, 0.2, 0.2, 0.25])
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # 设置表格样式
        table[(0, 0)].set_facecolor('#4472C4')
        table[(0, 1)].set_facecolor('#4472C4') 
        table[(0, 2)].set_facecolor('#4472C4')
        table[(0, 3)].set_facecolor('#4472C4')
        
        for i in range(4):
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"performance_matrix_annotated.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"详细注释热图已保存: {filepath}")
        
        return fig, (ax1, ax2)
    
    def create_clustered_heatmap(self, save_format=['png', 'pdf']):
        """
        创建聚类热图，展示模型和维度的相似性
        """
        # 获取数据
        matrix, _ = self.processor.create_performance_matrix()
        
        # 创建聚类热图
        g = sns.clustermap(
            matrix,
            annot=True,
            fmt='.2f',
            cmap=get_heatmap_cmap(),
            figsize=(12, 10),
            cbar_kws={'label': 'Performance Score'},
            linewidths=0.6,
            linecolor='white',
            method='average',  # 聚类方法
            metric='euclidean',  # 距离度量
            annot_kws={'size': 10, 'weight': 'bold', 'color': '#1f1f1f'},
            square=True,
        )
        
        # 设置标题
        g.fig.suptitle('Clustered AI Model Performance Matrix\n(Hierarchical Clustering)', 
                      fontsize=14, fontweight='bold', y=0.98)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        for fmt in save_format:
            filepath = self.output_dir / f"performance_matrix_clustered.{fmt}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"聚类热图已保存: {filepath}")
        
        return g


def main():
    """主函数，生成所有热图"""
    visualizer = PerformanceMatrixVisualizer()
    
    try:
        print("=== 生成性能矩阵热图 ===")
        
        # 基础热图
        print("1. 创建基础热图...")
        visualizer.create_heatmap()
        
        # 详细注释热图  
        print("2. 创建详细注释热图...")
        visualizer.create_annotated_heatmap()
        
        # 聚类热图
        print("3. 创建聚类热图...")
        visualizer.create_clustered_heatmap()
        
        print("\n所有热图生成完成！")
        
        # 显示图形
        plt.show()
        
    except Exception as e:
        print(f"可视化生成出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
