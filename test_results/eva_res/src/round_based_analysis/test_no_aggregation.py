#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the no_aggregation mode with a smaller dataset first.
"""

import sys
import time
from pathlib import Path

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer, TRUESKILL_AVAILABLE

def test_no_aggregation_mode():
    """Test the no_aggregation mode with no_lc dataset first."""
    
    if not TRUESKILL_AVAILABLE:
        print("Error: TrueSkill library is not installed.")
        print("Please install it with: pip install trueskill")
        return
    
    print("测试不聚合模式（使用较小的no_lc数据集）")
    print("=" * 50)
    
    mode = "no_aggregation"
    
    try:
        analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode=mode)
        
        # 先运行no_lc分析（较小的数据集）
        analysis_type = "no_lc"
        print(f"开始测试 {analysis_type} 分析...")
        
        start_time = time.time()
        results = analyzer.run_round_based_analysis(analysis_type)
        
        if results:
            elapsed = time.time() - start_time
            total_matches = results["match_statistics"]["total_matches"]
            print(f"\n测试成功完成!")
            print(f"耗时: {elapsed:.1f}秒")
            print(f"比赛数: {total_matches:,}")
            print(f"处理速度: {total_matches/elapsed:,.0f} 比赛/秒")
            
            # 显示关键统计
            print(f"\n关键统计:")
            print(f"- 实际玩家数: {results['match_statistics']['actual_players']}")
            print(f"- 预期玩家数: {results['match_statistics']['expected_players']}")
            print(f"- 处理维度数: {results['match_statistics']['dimensions_count']}")
            
            # 保存结果
            analyzer.save_results(results)
            print(f"测试结果已保存")
            
            print("\n测试成功！现在可以运行full分析。")
            
        else:
            print("测试失败，未生成结果")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_aggregation_mode()