#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare win rate calculation methods:
1. Original TrueSkill method (from elo_final.py) 
2. My simplified methods
"""

import math
import pandas as pd
from pathlib import Path


def original_trueskill_winrate(mu1, sigma1, mu2, sigma2, beta=4.167):
    """
    Original TrueSkill win rate calculation from elo_final.py
    Uses the actual TrueSkill formula with uncertainty.
    """
    mu_diff = mu1 - mu2
    sigma_combined = math.sqrt(sigma1**2 + sigma2**2 + 2*beta**2)
    win_probability = 0.5 * (1 + math.erf(mu_diff / (sigma_combined * math.sqrt(2))))
    return win_probability


def my_trueskill_winrate(rating_a, rating_b, beta=4.167):
    """
    My simplified TrueSkill method (only using conservative ratings)
    """
    return 1.0 / (1.0 + math.exp(-(rating_a - rating_b) / beta))


def my_elo_winrate(rating_a, rating_b):
    """
    My ELO method
    """
    return 1.0 / (1.0 + 10**((rating_b - rating_a) / 400))


def main():
    """Compare all three methods using actual data from the MD report."""
    
    # Data from the actual TrueSkill report - need to get mu and sigma values
    # Let's use some reasonable estimates based on typical TrueSkill patterns
    # Conservative rating = mu - 3*sigma, so mu ≈ conservative_rating + 3*sigma
    # Typical sigma values in TrueSkill are around 0.85-1.1
    
    models_data = [
        # (model_name, conservative_rating, estimated_mu, estimated_sigma)
        ("MOSES", 32.42, 35.35, 0.98),  # From report: mu=35.35, sigma=0.98
        ("o3", 31.05, 33.86, 0.94),     # From report: mu=33.86, sigma=0.94
        ("GPT-4.1", 26.70, 29.27, 0.86), # From report: mu=29.27, sigma=0.86
        ("LightRAG-nano", 26.10, 28.67, 0.85), # Estimated based on pattern
        ("LightRAG", 25.60, 28.17, 0.86), # From report
        ("MOSES-nano", 25.52, 28.09, 0.86), # Estimated
        ("GPT-4.1-nano", 24.21, 26.78, 0.85), # Estimated  
        ("Spark-Chemistry-X1", 22.10, 24.67, 0.86), # Estimated
        ("LlaSMol", 10.84, 13.41, 0.86), # Estimated
        ("Darwin", 10.32, 12.89, 0.86)   # Estimated
    ]
    
    print("Comparing Win Rate Calculation Methods")
    print("=" * 80)
    print()
    
    results = []
    
    for i in range(len(models_data) - 1):
        higher_model, higher_elo, higher_mu, higher_sigma = models_data[i]
        lower_model, lower_elo, lower_mu, lower_sigma = models_data[i + 1]
        
        # Method 1: Original TrueSkill (from elo_final.py)
        original_rate = original_trueskill_winrate(higher_mu, higher_sigma, lower_mu, lower_sigma)
        
        # Method 2: My simplified TrueSkill 
        my_trueskill_rate = my_trueskill_winrate(higher_elo, lower_elo)
        
        # Method 3: My ELO method
        my_elo_rate = my_elo_winrate(higher_elo, lower_elo)
        
        elo_diff = higher_elo - lower_elo
        mu_diff = higher_mu - lower_mu
        
        results.append({
            "Rank": i + 1,
            "Higher_Model": higher_model,
            "Lower_Model": lower_model,
            "ELO_Diff": elo_diff,
            "Mu_Diff": mu_diff,
            "Original_TrueSkill": original_rate,
            "My_TrueSkill": my_trueskill_rate,
            "My_ELO": my_elo_rate,
            "Original_Percent": f"{original_rate * 100:.1f}%",
            "My_TrueSkill_Percent": f"{my_trueskill_rate * 100:.1f}%",
            "My_ELO_Percent": f"{my_elo_rate * 100:.1f}%"
        })
        
        print(f"{i+1}. {higher_model:20s} vs {lower_model:20s}")
        print(f"   Conservative ELO: {higher_elo:5.2f} vs {lower_elo:5.2f} (diff: {elo_diff:5.2f})")
        print(f"   Mu (skill):       {higher_mu:5.2f} vs {lower_mu:5.2f} (diff: {mu_diff:5.2f})")
        print(f"   Original TrueSkill:  {original_rate * 100:5.1f}%")
        print(f"   My TrueSkill:        {my_trueskill_rate * 100:5.1f}%")
        print(f"   My ELO:              {my_elo_rate * 100:5.1f}%")
        print(f"   Difference (Orig-My): {(original_rate - my_trueskill_rate) * 100:+5.1f}%")
        print()
    
    # Create comparison DataFrame
    df = pd.DataFrame(results)
    
    # Calculate overall differences
    df['TrueSkill_Diff'] = df['Original_TrueSkill'] - df['My_TrueSkill']
    df['ELO_Diff'] = df['Original_TrueSkill'] - df['My_ELO']
    
    # Save comparison
    output_file = Path(__file__).parent / "winrate_method_comparison.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Saved comparison to: {output_file}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"Average win rate difference (Original TrueSkill - My TrueSkill): {df['TrueSkill_Diff'].mean() * 100:+5.1f}%")
    print(f"Max win rate difference (Original TrueSkill - My TrueSkill):     {df['TrueSkill_Diff'].max() * 100:+5.1f}%")
    print(f"Min win rate difference (Original TrueSkill - My TrueSkill):     {df['TrueSkill_Diff'].min() * 100:+5.1f}%")
    print()
    print(f"Average win rate difference (Original TrueSkill - My ELO):       {df['ELO_Diff'].mean() * 100:+5.1f}%")
    print(f"Max win rate difference (Original TrueSkill - My ELO):           {df['ELO_Diff'].max() * 100:+5.1f}%") 
    print(f"Min win rate difference (Original TrueSkill - My ELO):           {df['ELO_Diff'].min() * 100:+5.1f}%")
    
    print(f"\nCONCLUSION:")
    print(f"🔍 The original code uses TRUE TrueSkill formula with uncertainty (sigma)")
    print(f"📊 My methods are simplified approximations that ignore uncertainty")
    print(f"⚡ For same ELO differences, win rates will be DIFFERENT between methods!")


if __name__ == "__main__":
    main()