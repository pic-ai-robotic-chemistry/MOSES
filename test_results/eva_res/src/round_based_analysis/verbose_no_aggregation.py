#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verbose no_aggregation analysis with progress output.
"""

import sys
import time
import os
from pathlib import Path

# Enable unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer, TRUESKILL_AVAILABLE

def run_verbose_no_aggregation():
    """Run no_aggregation with verbose progress output."""
    
    if not TRUESKILL_AVAILABLE:
        print("错误: TrueSkill库未安装")
        return
    
    print("执行完全不聚合ELO分析 (详细输出版本)")
    print("=" * 50)
    print("预期: 350个玩家, ~990万场比赛")
    print()
    
    try:
        print("[1/6] 创建分析器实例...")
        analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode="no_aggregation")
        print("     完成")
        
        print("[2/6] 开始分析...")
        start_time = time.time()
        
        # 使用no_lc先测试（较小数据集）
        analysis_type = "no_lc"
        print(f"     分析类型: {analysis_type} (较小数据集用于测试)")
        
        results = analyzer.run_round_based_analysis(analysis_type)
        
        if results:
            elapsed = time.time() - start_time
            total_matches = results["match_statistics"]["total_matches"]
            
            print()
            print("[6/6] 分析完成!")
            print(f"     总耗时: {elapsed/60:.1f}分钟")
            print(f"     总比赛数: {total_matches:,}")
            print(f"     处理速度: {total_matches/elapsed:,.0f} 比赛/秒")
            
            # 显示关键统计
            stats = results["match_statistics"]
            print()
            print("关键统计:")
            print(f"  - 实际玩家数: {stats.get('actual_players', 'N/A')}")
            print(f"  - 预期玩家数: {stats.get('expected_players', 'N/A')}")  
            print(f"  - 维度数量: {stats.get('dimensions_count', 'N/A')}")
            print(f"  - 模型数量: {stats.get('unique_models', 'N/A')}")
            
            # 保存结果
            print()
            print("保存结果...")
            analyzer.save_results(results)
            print(f"结果已保存到: {analyzer.output_dir}")
            
            print()
            print("=== no_lc测试成功完成! ===")
            print("现在可以运行full分析 (如果需要)")
            
        else:
            print("分析失败 - 未生成结果")
            
    except KeyboardInterrupt:
        print("\n用户中断分析")
    except Exception as e:
        print(f"\n执行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_verbose_no_aggregation()