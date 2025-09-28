#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run no_aggregation analysis with no_lc (4 dimensions without logic and clarity).
"""

import sys
import time
from pathlib import Path

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer, TRUESKILL_AVAILABLE

def run_4_dimension_analysis():
    """Run no_aggregation analysis with 4 dimensions (no logic, no clarity)."""
    
    if not TRUESKILL_AVAILABLE:
        print("错误: TrueSkill库未安装")
        return
    
    print("执行4维度no_aggregation分析")
    print("=" * 50)
    print("维度: correctness, completeness, theoretical_depth, rigor_and_information_density")
    print("模式: no_aggregation (每个评估独立)")
    print()
    
    try:
        analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode="no_aggregation")
        
        # 使用no_lc模式（4维度）
        analysis_type = "no_lc"
        print(f"开始运行 {analysis_type} 分析...")
        
        start_time = time.time()
        results = analyzer.run_round_based_analysis(analysis_type)
        
        if results:
            elapsed = time.time() - start_time
            total_matches = results["match_statistics"]["total_matches"]
            
            print(f"\n4维度分析完成!")
            print(f"总耗时: {elapsed/60:.1f}分钟")
            print(f"总比赛数: {total_matches:,}")
            print(f"处理速度: {total_matches/elapsed:,.0f} 比赛/秒")
            
            # 显示关键统计
            stats = results["match_statistics"]
            print(f"\n关键统计:")
            print(f"- 实际玩家数: {stats.get('actual_players', 'N/A')}")
            print(f"- 维度数量: {stats.get('dimensions_count', 'N/A')}")
            print(f"- 模型数量: {stats.get('unique_models', 'N/A')}")
            
            # 保存结果
            analyzer.save_results(results)
            print(f"结果已保存到: {analyzer.output_dir}")
            
        else:
            print("分析失败")
            
    except Exception as e:
        print(f"执行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_4_dimension_analysis()