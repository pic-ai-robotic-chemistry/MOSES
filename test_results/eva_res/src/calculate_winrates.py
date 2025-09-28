#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate win rates between adjacent models based on ELO scores.
Uses the standard ELO win rate formula.
"""

import pandas as pd
import numpy as np
import math
from pathlib import Path


def elo_win_rate(rating_a, rating_b):
    """
    Calculate the expected win rate of player A against player B using ELO formula.
    
    Args:
        rating_a: ELO rating of player A
        rating_b: ELO rating of player B
        
    Returns:
        Expected win rate of A against B (0.0 to 1.0)
    """
    return 1.0 / (1.0 + 10**((rating_b - rating_a) / 400))


def trueskill_win_rate(rating_a, rating_b, beta=4.167):
    """
    Calculate win rate using TrueSkill-style approach.
    Uses the difference in conservative ratings with logistic function.
    
    Args:
        rating_a: TrueSkill conservative rating of player A  
        rating_b: TrueSkill conservative rating of player B
        beta: Skill difference parameter (default: TrueSkill standard)
        
    Returns:
        Expected win rate of A against B (0.0 to 1.0)
    """
    # Using logistic function with beta scaling
    diff = rating_a - rating_b
    return 1.0 / (1.0 + np.exp(-diff / beta))


def main():
    """Calculate win rates between adjacent models and save to files."""
    
    # Model data from the TrueSkill analysis
    models_data = [
        ("MOSES", 32.42),
        ("o3", 31.05),
        ("GPT-4.1", 26.70),
        ("LightRAG-nano", 26.10),
        ("LightRAG", 25.60),
        ("MOSES-nano", 25.52),
        ("GPT-4.1-nano", 24.21),
        ("Spark-Chemistry-X1", 22.10),
        ("LlaSMol", 10.84),
        ("Darwin", 10.32)
    ]
    
    print("Calculating Win Rates Between Adjacent Models")
    print("=" * 50)
    
    results = []
    
    for i in range(len(models_data) - 1):
        higher_model, higher_elo = models_data[i]
        lower_model, lower_elo = models_data[i + 1]
        
        # Calculate win rates using both methods
        elo_rate = elo_win_rate(higher_elo, lower_elo)
        trueskill_rate = trueskill_win_rate(higher_elo, lower_elo)
        
        # Calculate score differences
        elo_diff = higher_elo - lower_elo
        
        results.append({
            "Rank_Higher": i + 1,
            "Model_Higher": higher_model,
            "ELO_Higher": higher_elo,
            "Rank_Lower": i + 2,
            "Model_Lower": lower_model,
            "ELO_Lower": lower_elo,
            "ELO_Difference": elo_diff,
            "Win_Rate_ELO_Method": elo_rate,
            "Win_Rate_TrueSkill_Method": trueskill_rate,
            "Win_Rate_ELO_Percent": f"{elo_rate * 100:.1f}%",
            "Win_Rate_TrueSkill_Percent": f"{trueskill_rate * 100:.1f}%"
        })
        
        print(f"{i+1:2d}. {higher_model:20s} ({higher_elo:5.2f}) vs {lower_model:20s} ({lower_elo:5.2f})")
        print(f"    ELO Method:      {elo_rate * 100:5.1f}% win rate")
        print(f"    TrueSkill Method: {trueskill_rate * 100:5.1f}% win rate")
        print(f"    Score Difference: {elo_diff:5.2f}")
        print()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent
    
    # Save to CSV
    csv_file = output_dir / "model_winrates.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved CSV to: {csv_file}")
    
    # Save to Excel with formatting
    try:
        excel_file = output_dir / "model_winrates.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name='Win_Rates', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Win_Rates']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 25)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Create summary sheet
            summary_data = {
                "Metric": [
                    "Largest Win Rate (ELO Method)",
                    "Smallest Win Rate (ELO Method)", 
                    "Average Win Rate (ELO Method)",
                    "Largest Win Rate (TrueSkill Method)",
                    "Smallest Win Rate (TrueSkill Method)",
                    "Average Win Rate (TrueSkill Method)",
                    "Largest ELO Difference",
                    "Smallest ELO Difference",
                    "Average ELO Difference"
                ],
                "Value": [
                    f"{df['Win_Rate_ELO_Method'].max() * 100:.1f}%",
                    f"{df['Win_Rate_ELO_Method'].min() * 100:.1f}%",
                    f"{df['Win_Rate_ELO_Method'].mean() * 100:.1f}%",
                    f"{df['Win_Rate_TrueSkill_Method'].max() * 100:.1f}%",
                    f"{df['Win_Rate_TrueSkill_Method'].min() * 100:.1f}%",
                    f"{df['Win_Rate_TrueSkill_Method'].mean() * 100:.1f}%",
                    f"{df['ELO_Difference'].max():.2f}",
                    f"{df['ELO_Difference'].min():.2f}",
                    f"{df['ELO_Difference'].mean():.2f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format summary sheet
            summary_ws = writer.sheets['Summary']
            for column in summary_ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 35)
                summary_ws.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Saved Excel to: {excel_file}")
        
    except ImportError:
        print("⚠ openpyxl not available, skipping Excel export")
        print("  Install with: pip install openpyxl")
    
    # Print summary statistics
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    print(f"Total model pairs analyzed: {len(results)}")
    print(f"ELO Method Win Rates:")
    print(f"  Highest: {df['Win_Rate_ELO_Method'].max() * 100:.1f}%")
    print(f"  Lowest:  {df['Win_Rate_ELO_Method'].min() * 100:.1f}%") 
    print(f"  Average: {df['Win_Rate_ELO_Method'].mean() * 100:.1f}%")
    print(f"TrueSkill Method Win Rates:")
    print(f"  Highest: {df['Win_Rate_TrueSkill_Method'].max() * 100:.1f}%")
    print(f"  Lowest:  {df['Win_Rate_TrueSkill_Method'].min() * 100:.1f}%")
    print(f"  Average: {df['Win_Rate_TrueSkill_Method'].mean() * 100:.1f}%")
    print(f"ELO Score Differences:")
    print(f"  Largest:  {df['ELO_Difference'].max():.2f}")
    print(f"  Smallest: {df['ELO_Difference'].min():.2f}")
    print(f"  Average:  {df['ELO_Difference'].mean():.2f}")
    
    print(f"\nMethod Notes:")
    print(f"- ELO Method: Standard chess ELO formula (1/(1+10^((B-A)/400)))")
    print(f"- TrueSkill Method: Logistic function with β={4.167} (1/(1+exp(-(A-B)/β)))")
    print(f"- Both methods show similar trends but different magnitudes")


if __name__ == "__main__":
    main()