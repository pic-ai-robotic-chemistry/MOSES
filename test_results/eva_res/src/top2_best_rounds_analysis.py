#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Top2 Best Rounds Analysis for Llasmol and Darwin models.
Based on existing round analysis logic from individual.py.
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import sys

# Import the existing analyzer
from individual import IndividualEvaluationAnalyzer

class Top2BestRoundsAnalyzer:
    """Analyzer for finding top2 best rounds for specific models."""
    
    def __init__(self):
        self.analyzer = IndividualEvaluationAnalyzer()
        self.target_models = ["llasmol-top1", "llasmol-top5", "darwin"]
        
    def load_and_process_data(self):
        """Load and process data using existing analyzer."""
        print("Loading data using IndividualEvaluationAnalyzer...")
        self.analyzer.load_data()
        self.analyzer.process_data()
        print("Data processing completed!")
        
    def find_top2_best_rounds(self, exclude_logic_clarity: bool = False) -> Dict[str, Any]:
        """
        Find top2 best rounds for llasmol and darwin models.
        For llasmol, combines top1 and top5 as a single model with 10 rounds total.
        
        Args:
            exclude_logic_clarity: Whether to exclude logic and clarity dimensions
        """
        print(f"Finding top2 best rounds (exclude_logic_clarity={exclude_logic_clarity})...")
        
        if exclude_logic_clarity:
            target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
            analysis_type = "no_logic_clarity"
        else:
            target_dimensions = ['correctness', 'completeness', 'logic', 'clarity', 'theoretical_depth', 'rigor_and_information_density']
            analysis_type = "full"
        
        results = {}
        
        for judge_model, judge_data in self.analyzer.processed_data.items():
            results[judge_model] = {}
            
            # Process llasmol models (combine top1 and top5 into 10 rounds)
            llasmol_combined_data = {}
            llasmol_found = False
            
            for model_name in ["llasmol-top1", "llasmol-top5"]:
                if model_name in judge_data:
                    llasmol_found = True
                    model_data = judge_data[model_name]
                    print(f"  Found {model_name} with {len(model_data)} rounds")
                    
                    for answer_round, round_data in model_data.items():
                        # Create unique round keys for combined model
                        if model_name == "llasmol-top1":
                            combined_round_key = f"top1_round{answer_round}"
                        else:  # llasmol-top5
                            combined_round_key = f"top5_round{answer_round}"
                        
                        llasmol_combined_data[combined_round_key] = round_data
            
            if llasmol_found:
                print(f"  合并后的llasmol数据: {len(llasmol_combined_data)} 个轮次")
                llasmol_round_stats = self._calculate_round_stats(llasmol_combined_data, target_dimensions)
                if llasmol_round_stats:
                    # Find top2 best rounds
                    sorted_rounds = sorted(llasmol_round_stats.items(), 
                                         key=lambda x: x[1]["mean"], reverse=True)
                    
                    results[judge_model]["llasmol"] = {
                        "top2_best_rounds": sorted_rounds[:2],
                        "all_round_stats": llasmol_round_stats,
                        "model_components": ["llasmol-top1", "llasmol-top5"],
                        "total_rounds": len(llasmol_round_stats)
                    }
            
            # Process darwin model
            if "darwin" in judge_data:
                darwin_round_stats = self._calculate_round_stats(judge_data["darwin"], target_dimensions)
                if darwin_round_stats:
                    # Find top2 best rounds
                    sorted_rounds = sorted(darwin_round_stats.items(), 
                                         key=lambda x: x[1]["mean"], reverse=True)
                    
                    results[judge_model]["darwin"] = {
                        "top2_best_rounds": sorted_rounds[:2],
                        "all_round_stats": darwin_round_stats,
                        "model_components": ["darwin"],
                        "total_rounds": len(darwin_round_stats)
                    }
        
        return {
            "analysis_type": analysis_type,
            "target_dimensions": target_dimensions,
            "results": results
        }
    
    def _calculate_round_stats(self, model_data: Dict, target_dimensions: List[str]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each round of a model."""
        round_stats = {}
        
        for answer_round, round_data in model_data.items():
            round_scores = []
            
            for question_id, question_data in round_data.items():
                # Calculate average score across target dimensions for this question
                question_scores = []
                for dimension, scores in question_data.items():
                    if dimension in target_dimensions and scores:
                        question_scores.append(statistics.mean(scores))
                
                if question_scores:
                    round_scores.append(statistics.mean(question_scores))
            
            if round_scores:
                round_mean = statistics.mean(round_scores)
                round_std = statistics.stdev(round_scores) if len(round_scores) > 1 else 0
                
                round_stats[answer_round] = {
                    "mean": round_mean,
                    "std": round_std,
                    "count": len(round_scores)
                }
        
        return round_stats
    
    def save_results(self, results: Dict[str, Any], output_file: str = None):
        """Save top2 analysis results to files."""
        if output_file is None:
            analysis_type = results["analysis_type"]
            output_file = f"top2_best_rounds_{analysis_type}.json"
        
        output_path = Path(output_file)
        
        # Save JSON results
        print(f"Saving top2 analysis results to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Generate markdown report
        md_path = output_path.with_suffix('.md')
        self._generate_report(results, md_path)
    
    def _generate_report(self, results: Dict[str, Any], output_path: Path):
        """Generate markdown report for top2 best rounds analysis."""
        analysis_type = results["analysis_type"]
        target_dims = results["target_dimensions"]
        
        title_suffix = " (完整分析)" if analysis_type == "full" else " (排除逻辑性和清晰度)"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Llasmol和Darwin模型Top2最佳轮次分析{title_suffix}\n\n")
            
            f.write("## 分析概述\n\n")
            f.write("本分析统计了llasmol（合并top1和top5）和darwin模型的top2最佳表现轮次。\n\n")
            f.write(f"- **分析类型**: {analysis_type}\n")
            f.write(f"- **目标维度**: {', '.join(target_dims)}\n")
            f.write(f"- **目标模型**: llasmol (合并top1+top5), darwin\n\n")
            
            # Results by judge
            for judge, judge_data in results["results"].items():
                f.write(f"## 评判者: {judge}\n\n")
                
                for model, model_results in judge_data.items():
                    f.write(f"### {model.upper()}\n\n")
                    
                    if "model_components" in model_results:
                        components = ", ".join(model_results["model_components"])
                        f.write(f"**模型组成**: {components}\n\n")
                    
                    # Top2 best rounds
                    top2_rounds = model_results["top2_best_rounds"]
                    f.write("#### Top2 最佳轮次\n\n")
                    f.write("| 排名 | 轮次 | 平均分 | 标准差 | 样本数 |\n")
                    f.write("|------|------|--------|--------|--------|\n")
                    
                    for rank, (round_key, stats) in enumerate(top2_rounds, 1):
                        f.write(f"| {rank} | {round_key} | {stats['mean']:.3f} | {stats['std']:.3f} | {stats['count']} |\n")
                    
                    f.write("\n")
                    
                    # All rounds performance
                    f.write("#### 所有轮次表现\n\n")
                    f.write("| 轮次 | 平均分 | 标准差 | 样本数 | 排名 |\n")
                    f.write("|------|--------|--------|--------|------|\n")
                    
                    all_rounds = model_results["all_round_stats"]
                    sorted_all_rounds = sorted(all_rounds.items(), 
                                             key=lambda x: x[1]["mean"], reverse=True)
                    
                    for rank, (round_key, stats) in enumerate(sorted_all_rounds, 1):
                        f.write(f"| {round_key} | {stats['mean']:.3f} | {stats['std']:.3f} | {stats['count']} | {rank} |\n")
                    
                    f.write("\n")
                
                f.write("\n")
            
            # Summary section
            f.write("## 总结\n\n")
            f.write("### 关键发现\n\n")
            
            # Calculate overall statistics
            all_models_top2 = []
            for judge_data in results["results"].values():
                for model, model_results in judge_data.items():
                    top2_rounds = model_results["top2_best_rounds"]
                    if len(top2_rounds) >= 2:
                        best_score = top2_rounds[0][1]["mean"]
                        second_score = top2_rounds[1][1]["mean"]
                        all_models_top2.append({
                            "model": model,
                            "best_round": top2_rounds[0][0],
                            "best_score": best_score,
                            "second_round": top2_rounds[1][0], 
                            "second_score": second_score,
                            "score_gap": best_score - second_score
                        })
            
            if all_models_top2:
                f.write("- **最佳表现模型**: ")
                best_overall = max(all_models_top2, key=lambda x: x["best_score"])
                f.write(f"{best_overall['model']} (第{best_overall['best_round']}轮, {best_overall['best_score']:.3f}分)\n")
                
                f.write("- **最稳定表现**: ")
                most_stable = min(all_models_top2, key=lambda x: x["score_gap"])
                f.write(f"{most_stable['model']} (轮次间差距: {most_stable['score_gap']:.3f}分)\n")
                
                # Round frequency analysis
                round_freq = defaultdict(int)
                for model_data in all_models_top2:
                    round_freq[model_data["best_round"]] += 1
                    round_freq[model_data["second_round"]] += 1
                
                most_common_round = max(round_freq, key=round_freq.get)
                f.write(f"- **最常见高表现轮次**: 第{most_common_round}轮 (出现{round_freq[most_common_round]}次)\n")
                
            f.write("\n### 模型对比\n\n")
            f.write("| 模型 | 最佳轮次 | 最佳分数 | 第二轮次 | 第二分数 | 轮次差距 |\n")
            f.write("|------|----------|----------|----------|----------|----------|\n")
            
            for model_data in all_models_top2:
                f.write(f"| {model_data['model']} | 第{model_data['best_round']}轮 | {model_data['best_score']:.3f} | 第{model_data['second_round']}轮 | {model_data['second_score']:.3f} | {model_data['score_gap']:.3f} |\n")
            
            f.write("\n")
        
        print(f"Top2 analysis report saved to: {output_path}")

def main():
    """Main function to run top2 best rounds analysis."""
    print("Top2 Best Rounds Analysis for Llasmol and Darwin")
    print("=" * 55)
    
    try:
        analyzer = Top2BestRoundsAnalyzer()
        analyzer.load_and_process_data()
        
        # Run analysis for both types
        print("\n1. Running full analysis (all dimensions)...")
        results_full = analyzer.find_top2_best_rounds(exclude_logic_clarity=False)
        analyzer.save_results(results_full, "top2_best_rounds_full.json")
        
        print("\n2. Running analysis excluding Logic and Clarity...")
        results_no_lc = analyzer.find_top2_best_rounds(exclude_logic_clarity=True)
        analyzer.save_results(results_no_lc, "top2_best_rounds_no_logic_clarity.json")
        
        print("\nTop2 best rounds analysis completed!")
        print("\nGenerated files:")
        print("- top2_best_rounds_full.json/md: Full analysis (6 dimensions)")
        print("- top2_best_rounds_no_logic_clarity.json/md: Analysis excluding Logic/Clarity (4 dimensions)")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()