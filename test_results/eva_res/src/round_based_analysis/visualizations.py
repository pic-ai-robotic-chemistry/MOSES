#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round-Based TrueSkill Visualization Module.

This module provides comprehensive visualizations for round-based TrueSkill analysis,
including heat maps, radar charts, trend lines, and comparative analysis.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

class RoundBasedVisualizer:
    """Creates comprehensive visualizations for round-based TrueSkill analysis."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.vis_dir = self.output_dir / "visualizations"
        self.vis_dir.mkdir(exist_ok=True)
        
        # Set visualization style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Custom color schemes
        self.round_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        self.dimension_colors = {
            'correctness': '#FF6B6B',
            'completeness': '#4ECDC4', 
            'logic': '#45B7D1',
            'clarity': '#96CEB4',
            'theoretical_depth': '#FFEAA7',
            'rigor_and_information_density': '#DDA0DD'
        }
        
    def create_all_visualizations(self, results: Dict[str, Any]):
        """Create all visualizations for round-based analysis."""
        print(f"Creating visualizations for {results.get('aggregation_mode', 'unknown')} mode...")
        
        # Extract data
        model_analyses = results.get("model_analyses", {})
        round_ratings = results.get("round_ratings", {})
        
        if not model_analyses or not round_ratings:
            print("No data available for visualization")
            return
        
        # Create visualizations
        self.create_round_performance_heatmap(model_analyses)
        self.create_model_consistency_radar(model_analyses)
        self.create_dimension_trend_lines(model_analyses)
        self.create_elo_distribution_comparison(round_ratings, model_analyses)
        self.create_round_progression_curves(model_analyses)
        self.create_stability_scatter_plot(model_analyses)
        
        # Create aggregation method comparison
        self.create_aggregation_method_comparison(model_analyses)
        
        print(f"All visualizations saved to: {self.vis_dir}")
    
    def create_round_performance_heatmap(self, model_analyses: Dict):
        """Create heatmaps showing model performance across rounds and dimensions."""
        print("Creating round performance heatmaps...")
        
        # Combine data from all judges
        all_data = []
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                for round_num, round_data in analysis["round_ratings"].items():
                    for dimension, rating_data in round_data.items():
                        all_data.append({
                            'Judge': judge,
                            'Model': model,
                            'Round': int(round_num),
                            'Dimension': dimension,
                            'Rating': rating_data['rating'],
                            'Mu': rating_data['mu'],
                            'Sigma': rating_data['sigma']
                        })
        
        df = pd.DataFrame(all_data)
        
        # Create separate heatmap for each judge and dimension
        judges = df['Judge'].unique()
        dimensions = df['Dimension'].unique()
        
        fig, axes = plt.subplots(len(judges), len(dimensions), 
                                figsize=(4*len(dimensions), 3*len(judges)))
        
        if len(judges) == 1:
            axes = axes.reshape(1, -1)
        if len(dimensions) == 1:
            axes = axes.reshape(-1, 1)
        
        for i, judge in enumerate(judges):
            for j, dimension in enumerate(dimensions):
                ax = axes[i, j] if len(judges) > 1 else axes[j]
                
                # Create pivot table for heatmap
                subset = df[(df['Judge'] == judge) & (df['Dimension'] == dimension)]
                if subset.empty:
                    ax.set_visible(False)
                    continue
                
                pivot = subset.pivot(index='Model', columns='Round', values='Rating')
                
                # Create heatmap
                sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                           center=25, ax=ax, cbar_kws={'shrink': 0.8})
                
                ax.set_title(f'{judge}\n{dimension.replace("_", " ").title()}', fontsize=10)
                ax.set_xlabel('Round' if i == len(judges)-1 else '')
                ax.set_ylabel('Model' if j == 0 else '')
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'round_performance_heatmaps.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_model_consistency_radar(self, model_analyses: Dict):
        """Create radar charts showing model consistency across dimensions."""
        print("Creating model consistency radar charts...")
        
        # Prepare data
        models = set()
        dimensions = set()
        for judge_data in model_analyses.values():
            models.update(judge_data.keys())
            for analysis in judge_data.values():
                for round_data in analysis["round_ratings"].values():
                    dimensions.update(round_data.keys())
        
        models = sorted(models)
        dimensions = sorted(dimensions)
        
        if not models or not dimensions:
            print("No data available for radar chart")
            return
        
        # Create subplots for each model
        n_models = len(models)
        n_cols = min(4, n_models)
        n_rows = (n_models + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, subplot_kw=dict(projection='polar'),
                                figsize=(4*n_cols, 4*n_rows))
        
        # Handle single plot case
        if n_models == 1:
            axes = [axes]
        elif n_rows == 1:
            if n_cols == 1:
                axes = [axes]
            else:
                axes = axes.reshape(1, -1)
        
        for idx, model in enumerate(models):
            row = idx // n_cols
            col = idx % n_cols
            
            if n_rows > 1:
                ax = axes[row][col]
            else:
                ax = axes[col] if n_cols > 1 else axes[idx]
            
            # Calculate average ratings across judges and rounds for each dimension
            dimension_averages = {}
            for dimension in dimensions:
                ratings = []
                for judge_data in model_analyses.values():
                    if model in judge_data:
                        analysis = judge_data[model]
                        for round_data in analysis["round_ratings"].values():
                            if dimension in round_data:
                                ratings.append(round_data[dimension]['rating'])
                
                if ratings:
                    dimension_averages[dimension] = np.mean(ratings)
                else:
                    dimension_averages[dimension] = 25  # Default TrueSkill rating
            
            # Prepare data for radar chart
            if dimension_averages:
                angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False).tolist()
                angles += angles[:1]  # Complete the circle
                
                values = [dimension_averages[dim] for dim in dimensions]
                values += values[:1]  # Complete the circle
                
                ax.plot(angles, values, 'o-', linewidth=2, label=model)
                ax.fill(angles, values, alpha=0.25)
                
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels([d.replace('_', '\n') for d in dimensions], fontsize=8)
                ax.set_ylim(0, max(35, max(values) * 1.1))
                ax.set_title(model, fontsize=12, pad=20)
                ax.grid(True)
        
        # Hide empty subplots
        for idx in range(n_models, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            if n_rows > 1:
                axes[row][col].set_visible(False)
            elif n_cols > 1:
                axes[col].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'model_consistency_radar.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_dimension_trend_lines(self, model_analyses: Dict):
        """Create line plots showing dimension performance trends across rounds."""
        print("Creating dimension trend lines...")
        
        # Prepare data
        all_data = []
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                for round_num, round_data in analysis["round_ratings"].items():
                    for dimension, rating_data in round_data.items():
                        all_data.append({
                            'Judge': judge,
                            'Model': model,
                            'Round': int(round_num),
                            'Dimension': dimension,
                            'Rating': rating_data['rating']
                        })
        
        df = pd.DataFrame(all_data)
        
        # Calculate mean rating by dimension and round
        trend_data = df.groupby(['Dimension', 'Round'])['Rating'].agg(['mean', 'std']).reset_index()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for dimension in trend_data['Dimension'].unique():
            dim_data = trend_data[trend_data['Dimension'] == dimension]
            color = self.dimension_colors.get(dimension, '#333333')
            
            ax.plot(dim_data['Round'], dim_data['mean'], 
                   marker='o', linewidth=2, label=dimension.replace('_', ' ').title(),
                   color=color)
            
            # Add error bars
            ax.fill_between(dim_data['Round'], 
                           dim_data['mean'] - dim_data['std'],
                           dim_data['mean'] + dim_data['std'],
                           alpha=0.2, color=color)
        
        ax.set_xlabel('Round', fontsize=12)
        ax.set_ylabel('Average ELO Rating', fontsize=12)
        ax.set_title('Dimension Performance Trends Across Rounds', fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(1, 6))
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'dimension_trend_lines.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_elo_distribution_comparison(self, round_ratings: Dict, model_analyses: Dict):
        """Create violin plots comparing ELO distributions."""
        print("Creating ELO distribution comparison...")
        
        # Extract all individual round ratings
        individual_ratings = []
        for judge, judge_data in round_ratings.items():
            for dimension, dimension_data in judge_data.items():
                for player_id, rating_data in dimension_data.items():
                    individual_ratings.append({
                        'Type': 'Individual Round',
                        'Rating': rating_data['rating']
                    })
        
        # Extract aggregated ratings
        aggregated_ratings = []
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                for method, rating in analysis["aggregated_ratings"].items():
                    aggregated_ratings.append({
                        'Type': f'Aggregated ({method})',
                        'Rating': rating
                    })
        
        # Combine data
        all_ratings = individual_ratings + aggregated_ratings
        df = pd.DataFrame(all_ratings)
        
        # Create violin plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.violinplot(data=df, x='Type', y='Rating', ax=ax)
        ax.set_title('ELO Rating Distribution Comparison', fontsize=14)
        ax.set_ylabel('ELO Rating', fontsize=12)
        ax.set_xlabel('Rating Type', fontsize=12)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'elo_distribution_violins.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_round_progression_curves(self, model_analyses: Dict):
        """Create curves showing how models progress across rounds."""
        print("Creating round progression curves...")
        
        # Calculate model averages across rounds
        model_progression = defaultdict(list)
        
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                # Get actual round numbers from data instead of assuming 1-5
                available_rounds = sorted([int(r) if isinstance(r, str) else r for r in analysis["round_ratings"].keys()])
                
                for round_num in available_rounds:
                    if str(round_num) in analysis["round_ratings"]:
                        round_data = analysis["round_ratings"][str(round_num)]
                        if round_data:  # Check if round_data is not empty
                            round_avg = np.mean([r['rating'] for r in round_data.values() if isinstance(r, dict) and 'rating' in r])
                            model_progression[model].append(round_avg)
                    else:
                        model_progression[model].append(np.nan)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for model, ratings in model_progression.items():
            if any(not np.isnan(r) for r in ratings) and len(ratings) > 0:  # Only plot if has data
                # Use actual round numbers instead of fixed range(1, 6)
                x_values = range(1, len(ratings) + 1)
                ax.plot(x_values, ratings, marker='o', linewidth=2, 
                       label=model, alpha=0.7)
        
        ax.set_xlabel('Round', fontsize=12)
        ax.set_ylabel('Average ELO Rating', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        # Remove fixed x-axis ticks
        # ax.set_xticks(range(1, 6))
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'round_progression_curves.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_stability_scatter_plot(self, model_analyses: Dict):
        """Create scatter plot of performance vs stability."""
        print("Creating stability scatter plot...")
        
        # Extract stability and performance metrics
        scatter_data = []
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                performance = analysis["aggregated_ratings"].get("weighted_mean", 25)
                stability = analysis["stability_metrics"].get("round_consistency", 0.5)
                
                scatter_data.append({
                    'Model': model,
                    'Performance': performance,
                    'Stability': stability,
                    'Judge': judge
                })
        
        df = pd.DataFrame(scatter_data)
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        judges = df['Judge'].unique()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, judge in enumerate(judges):
            judge_data = df[df['Judge'] == judge]
            ax.scatter(judge_data['Performance'], judge_data['Stability'], 
                      alpha=0.7, s=100, label=judge, 
                      color=colors[i % len(colors)])
            
            # Add model labels
            for _, row in judge_data.iterrows():
                ax.annotate(row['Model'], 
                           (row['Performance'], row['Stability']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.7)
        
        ax.set_xlabel('Performance (Weighted Mean ELO)', fontsize=12)
        ax.set_ylabel('Round Consistency', fontsize=12)
        ax.set_title('Performance vs Stability Trade-off', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'stability_scatter_plots.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_aggregation_method_comparison(self, model_analyses: Dict):
        """Create comparison of different aggregation methods."""
        print("Creating aggregation method comparison...")
        
        # Extract data for comparison
        comparison_data = []
        for judge, judge_data in model_analyses.items():
            for model, analysis in judge_data.items():
                for method, rating in analysis["aggregated_ratings"].items():
                    comparison_data.append({
                        'Model': model,
                        'Method': method,
                        'Rating': rating,
                        'Judge': judge
                    })
        
        df = pd.DataFrame(comparison_data)
        
        # Create grouped bar plot
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Pivot data for plotting
        pivot_df = df.pivot_table(index='Model', columns='Method', 
                                 values='Rating', aggfunc='mean')
        
        pivot_df.plot(kind='bar', ax=ax, width=0.8)
        
        ax.set_title('Model Rankings by Aggregation Method', fontsize=14)
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('ELO Rating', fontsize=12)
        ax.legend(title='Aggregation Method', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(self.vis_dir / 'aggregation_method_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_visualization_summary(self, results: Dict[str, Any]) -> str:
        """Generate markdown summary of all visualizations."""
        mode = results.get("aggregation_mode", "unknown")
        analysis_type = results.get("analysis_type", "unknown")
        
        summary = f"""
## Visualizations for {mode.title().replace('_', ' ')} Mode ({analysis_type.upper()})

### Available Visualizations

1. **Round Performance Heatmaps** (`round_performance_heatmaps.png`)
   - Shows model performance across different rounds and dimensions
   - Color intensity indicates ELO rating strength
   - Separate heatmaps for each judge and dimension

2. **Model Consistency Radar Charts** (`model_consistency_radar.png`)
   - Radar charts for each model showing performance across dimensions
   - Different lines for each round reveal consistency patterns
   - Identifies models with balanced vs specialized performance

3. **Dimension Trend Lines** (`dimension_trend_lines.png`)
   - Average performance trends across rounds for each dimension
   - Shows which dimensions benefit from multiple attempts
   - Error bands indicate variability across models

4. **ELO Distribution Comparison** (`elo_distribution_violins.png`)
   - Compares distributions of individual round ratings vs aggregated ratings
   - Shows effect of aggregation on rating spread
   - Violin plots reveal distribution shapes

5. **Round Progression Curves** (`round_progression_curves.png`)
   - Individual model trajectories across rounds
   - Identifies learning vs declining patterns
   - Distinguishes consistent vs variable performers

6. **Stability Scatter Plot** (`stability_scatter_plots.png`)
   - Performance vs consistency trade-off analysis
   - X-axis: Average performance, Y-axis: Round consistency
   - Ideal models appear in upper-right quadrant

7. **Aggregation Method Comparison** (`aggregation_method_comparison.png`)
   - Side-by-side comparison of different aggregation strategies
   - Shows how ranking changes based on aggregation method
   - Helps identify most appropriate aggregation strategy

### Key Insights from Visualizations

*This section would be automatically populated with insights derived from the actual data analysis.*

"""
        return summary

from collections import defaultdict

def integrate_visualizations_with_analyzer():
    """Integration function to add visualization capability to the main analyzer."""
    pass