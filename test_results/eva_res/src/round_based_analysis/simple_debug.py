#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pathlib import Path

print("调试no_aggregation分析...")
print("=" * 40)

try:
    # 检查库
    import trueskill
    import pandas as pd
    print("库检查: OK")
    
    # 检查数据目录
    data_dir = Path("C:/d/CursorProj/Chem-Ontology-Constructor/test_results/eva_res")
    if data_dir.exists():
        print(f"数据目录: OK")
        json_files = list(data_dir.glob("**/*.json"))
        print(f"JSON文件数量: {len(json_files)}")
    else:
        print("数据目录: 不存在")
        sys.exit(1)
    
    # 尝试导入分析器
    sys.path.append(str(Path(__file__).parent))
    from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer
    print("分析器导入: OK")
    
    # 创建实例
    analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode="no_aggregation")
    print("分析器创建: OK")
    
    # 测试数据加载
    print("开始测试数据加载...")
    start_time = time.time()
    data = analyzer._load_evaluation_data("full")
    load_time = time.time() - start_time
    
    if data:
        print(f"数据加载: OK ({len(data)} records, {load_time:.1f}s)")
        
        # 测试轮次数据提取
        print("测试轮次数据提取...")
        round_data = analyzer.extract_round_level_scores(data)
        
        if round_data:
            total_players = sum(len(judge_data) for dimension_data in round_data.values() 
                              for judge_data in dimension_data.values())
            print(f"轮次数据提取: OK ({total_players} total players)")
            
            # 显示统计信息
            judges = list(round_data.keys())
            dimensions = list(round_data[judges[0]].keys()) if judges else []
            print(f"评判者数量: {len(judges)}")
            print(f"维度数量: {len(dimensions)}")
            
            # 估算比赛数量
            if total_players > 0:
                estimated_matches = (total_players * (total_players - 1)) // 2 * 27 * len(dimensions)
                print(f"预计比赛数量: {estimated_matches:,}")
                print(f"预计处理时间: {estimated_matches/10000:.0f}秒")
        else:
            print("轮次数据提取: 失败")
    else:
        print("数据加载: 失败")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("调试完成")