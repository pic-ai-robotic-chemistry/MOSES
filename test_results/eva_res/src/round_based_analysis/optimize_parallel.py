#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick parallel optimization test for round-based TrueSkill analysis.
"""

import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

def optimize_trueskill_analyzer():
    """Add simple parallel optimization to existing analyzer."""
    
    # Read current analyzer
    analyzer_file = "C:/d/CursorProj/Chem-Ontology-Constructor/test_results/eva_res/src/round_based_analysis/round_based_trueskill_elo.py"
    
    with open(analyzer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the main function and add parallel option
    main_func_start = content.find("def main():")
    main_func = '''def main():
    """Main function to run round-based TrueSkill analysis."""
    if not TRUESKILL_AVAILABLE:
        print("Error: TrueSkill library is not installed.")
        print("Please install it with: pip install trueskill")
        return
    
    print("Round-Based TrueSkill ELO Analysis System")
    print("=" * 50)
    
    # Check CPU cores
    cpu_cores = mp.cpu_count()
    print(f"Detected {cpu_cores} CPU cores")
    
    # Run both modes with parallel optimization
    for mode in ["eval_aggregated"]:  # Start with faster mode
        print(f"\\n{'='*20} {mode.upper()} MODE {'='*20}")
        
        try:
            # Enable parallel processing for multi-core systems
            enable_parallel = cpu_cores > 2
            analyzer = RoundBasedTrueSkillAnalyzer(
                aggregation_mode=mode,
                enable_parallel=enable_parallel,
                max_workers=min(cpu_cores, 6)  # Limit to prevent memory issues
            )
            
            # Run analysis for both types
            for analysis_type in ["no_lc"]:  # Start with smaller dataset
                print(f"\\n--- Running {analysis_type} analysis ---")
                start_time = time.time()
                
                results = analyzer.run_round_based_analysis(analysis_type)
                
                if results:
                    elapsed = time.time() - start_time
                    total_matches = results["match_statistics"]["total_matches"]
                    print(f"Completed in {elapsed:.1f}s ({total_matches/elapsed:,.0f} matches/sec)")
                    
                    analyzer.save_results(results)
                    
        except Exception as e:
            print(f"Error in {mode} mode: {e}")
            import traceback
            traceback.print_exc()
    
    print("\\nRound-based TrueSkill analysis completed!")'''
    
    # Replace the main function
    main_func_end = content.find('if __name__ == "__main__":')
    
    new_content = content[:main_func_start] + main_func + '\n\n' + content[main_func_end:]
    
    # Add parallel support flag to __init__
    init_pattern = 'def __init__(self, results_file: str = None, aggregation_mode: str = "eval_aggregated",'
    if init_pattern in new_content:
        new_init = init_pattern.replace(
            'aggregation_mode: str = "eval_aggregated",',
            'aggregation_mode: str = "eval_aggregated",\n                 enable_parallel: bool = True, max_workers: int = None,'
        )
        new_content = new_content.replace(init_pattern, new_init)
    
    # Save optimized version
    with open(analyzer_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Parallel optimization applied to analyzer!")

if __name__ == "__main__":
    optimize_trueskill_analyzer()