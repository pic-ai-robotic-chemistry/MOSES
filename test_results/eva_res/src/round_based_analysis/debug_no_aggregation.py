#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug version to see what's happening in no_aggregation analysis.
"""

import sys
import time
import os
from pathlib import Path

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

print("开始调试no_aggregation分析...")
print("=" * 50)

try:
    # 检查必要的库
    print("检查依赖库...")
    try:
        import trueskill
        print("OK TrueSkill库已安装")
    except ImportError:
        print("ERROR TrueSkill库未安装")
        sys.exit(1)
    
    try:
        import pandas as pd
        print("OK Pandas库已安装")
    except ImportError:
        print("ERROR Pandas库未安装")
        sys.exit(1)
    
    # 检查数据文件
    print("\n检查数据文件...")
    data_dir = Path("C:/d/CursorProj/Chem-Ontology-Constructor/test_results/eva_res")
    
    if not data_dir.exists():
        print(f"ERROR 数据目录不存在: {data_dir}")
        sys.exit(1)
    else:
        print(f"OK 数据目录存在: {data_dir}")
    
    # 查找JSON文件
    json_files = list(data_dir.glob("**/*.json"))
    print(f"找到 {len(json_files)} 个JSON文件:")
    for f in json_files[:5]:  # 只显示前5个
        size_mb = f.stat().st_size / (1024*1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")
    
    # 尝试导入分析器
    print("\n尝试导入分析器...")
    try:
        from round_based_trueskill_elo import RoundBasedTrueSkillAnalyzer
        print("✓ 成功导入RoundBasedTrueSkillAnalyzer")
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        sys.exit(1)
    
    # 创建分析器实例
    print("\n创建分析器实例...")
    try:
        analyzer = RoundBasedTrueSkillAnalyzer(aggregation_mode="no_aggregation")
        print("✓ 成功创建分析器")
    except Exception as e:
        print(f"✗ 创建分析器失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 检查数据加载
    print("\n尝试加载数据...")
    try:
        # 直接调用数据加载方法
        data = analyzer._load_evaluation_data("full")
        if data:
            print(f"✓ 成功加载数据，包含 {len(data)} 条记录")
            
            # 显示数据结构
            if len(data) > 0:
                first_record = list(data.values())[0]
                print(f"数据结构示例: {list(first_record.keys())}")
        else:
            print("✗ 数据加载失败或为空")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 数据加载错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n所有检查通过！问题可能在于:")
    print("1. 数据处理阶段耗时过长")
    print("2. 内存不足导致处理缓慢") 
    print("3. 计算复杂度过高")
    
    print("\n建议:")
    print("- 先用test_no_aggregation.py测试no_lc数据集")
    print("- 监控系统内存使用情况")
    print("- 考虑分批处理数据")
        
except Exception as e:
    print(f"调试过程发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n调试完成")