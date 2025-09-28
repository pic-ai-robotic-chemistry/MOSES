#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute no_aggregation mode ELO analysis as requested by user.
This script runs the full no-aggregation analysis with 350 players and ~9.9M matches.
"""

import sys
import time
from pathlib import Path

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer, TRUESKILL_AVAILABLE

def run_no_aggregation_analysis():
    """Run the no_aggregation mode analysis as explicitly requested."""
    
    if not TRUESKILL_AVAILABLE:
        print("Error: TrueSkill library is not installed.")
        print("Please install it with: pip install trueskill")
        return
    
    print("执行完全不聚合的ELO分析")
    print("=" * 50)
    print("预期: 350个玩家 (14模型 × 5轮次 × 5评估)")
    print("预期: ~9.9百万场比赛")
    print("预期时长: 10-30分钟")
    print()
    
    mode = "no_aggregation"
    
    try:
        analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode=mode)
        
        # 只运行full分析（更全面的数据集）
        analysis_type = "full"
        print(f"开始运行 {analysis_type} 分析...")
        
        start_time = time.time()
        results = analyzer.run_round_based_analysis(analysis_type)
        
        if results:
            elapsed = time.time() - start_time
            total_matches = results["match_statistics"]["total_matches"]
            print(f"\n分析完成!")
            print(f"总耗时: {elapsed/60:.1f}分钟")
            print(f"总比赛数: {total_matches:,}")
            print(f"处理速度: {total_matches/elapsed:,.0f} 比赛/秒")
            
            # 保存结果
            analyzer.save_results(results)
            print(f"结果已保存到: {analyzer.output_dir}")
            
            # 显示一些关键统计
            print(f"\n关键统计:")
            print(f"- 实际玩家数: {results['match_statistics']['actual_players']}")
            print(f"- 预期玩家数: {results['match_statistics']['expected_players']}")
            print(f"- 处理维度数: {results['match_statistics']['dimensions_count']}")
            
        else:
            print("分析失败，未生成结果")
            
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n完全不聚合ELO分析执行完毕!")

if __name__ == "__main__":
    run_no_aggregation_analysis()