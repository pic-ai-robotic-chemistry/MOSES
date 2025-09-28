#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate win rates for general-purpose models only (excluding domain-specific models).
Removed: Spark-Chemistry-X1, LlaSMol, Darwin
Remaining: 9 general-purpose models
"""

import math
import pandas as pd
from pathlib import Path


def calculate_trueskill_win_probability(mu1: float, sigma1: float, mu2: float, sigma2: float, beta: float = 4.167) -> float:
    """
    Calculate win probability using the exact TrueSkill formula from elo_final.py.
    """
    mu_diff = mu1 - mu2
    sigma_combined = math.sqrt(sigma1**2 + sigma2**2 + 2*beta**2)
    win_probability = 0.5 * (1 + math.erf(mu_diff / (sigma_combined * math.sqrt(2))))
    return win_probability


def main():
    """Calculate win rates for general-purpose models only (9 models)."""
    
    # General-purpose models only (removed Spark-Chemistry-X1, LlaSMol, Darwin)
    # (your_name, elo_score, actual_name_in_report, mu, sigma)
    general_models = [
        ("MOSES", 32.42, "MOSES", 35.35, 0.98),
        ("o3", 31.05, "o3", 33.86, 0.94),
        ("GPT-4.1", 26.70, "gpt-4.1", 29.27, 0.86),
        ("LightRAG-nano", 26.10, "lightrag-4.1-nano", 28.67, 0.85),
        ("LightRAG", 25.60, "lightrag-4.1", 28.17, 0.86),
        ("MOSES-nano", 25.52, "MOSES-nano", 28.07, 0.85),
        ("GPT-4.1-nano", 24.21, "gpt-4.1-nano", 26.75, 0.85),
        ("GPT-4o", 22.06, "gpt-4o", 24.64, 0.86),
        ("GPT-4o-mini", 20.00, "gpt-4o-mini", 22.62, 0.87)
    ]
    
    excluded_models = ["Spark-Chemistry-X1", "LlaSMol", "Darwin"]
    
    print("Win Rate Calculation for General-Purpose Models Only")
    print(f"Excluded domain-specific models: {', '.join(excluded_models)}")
    print("Using precise TrueSkill formula with actual μ and σ values")
    print("=" * 75)
    print()
    
    results = []
    
    # Calculate win rates between adjacent models (higher vs lower)
    for i in range(len(general_models) - 1):
        higher_name, higher_elo, _, higher_mu, higher_sigma = general_models[i]
        lower_name, lower_elo, _, lower_mu, lower_sigma = general_models[i + 1]
        
        # Calculate precise win probability
        win_probability = calculate_trueskill_win_probability(
            higher_mu, higher_sigma, lower_mu, lower_sigma
        )
        
        # Calculate differences
        elo_diff = higher_elo - lower_elo
        mu_diff = higher_mu - lower_mu
        sigma_avg = (higher_sigma + lower_sigma) / 2
        
        results.append({
            "Rank_Higher": i + 1,
            "Model_Higher": higher_name,
            "ELO_Higher": higher_elo,
            "Mu_Higher": higher_mu,
            "Sigma_Higher": higher_sigma,
            "Rank_Lower": i + 2,
            "Model_Lower": lower_name,
            "ELO_Lower": lower_elo,
            "Mu_Lower": lower_mu,
            "Sigma_Lower": lower_sigma,
            "ELO_Difference": elo_diff,
            "Mu_Difference": mu_diff,
            "Sigma_Average": sigma_avg,
            "Win_Rate": win_probability,
            "Win_Rate_Percent": f"{win_probability * 100:.1f}%"
        })
        
        print(f"{i+1:2d}. {higher_name:18s} vs {lower_name:18s}")
        print(f"    ELO:   {higher_elo:6.2f} vs {lower_elo:6.2f} (Δ: {elo_diff:5.2f})")
        print(f"    μ:     {higher_mu:6.2f} vs {lower_mu:6.2f} (Δ: {mu_diff:5.2f})")
        print(f"    σ:     {higher_sigma:6.2f} vs {lower_sigma:6.2f} (Avg: {sigma_avg:.2f})")
        print(f"    Win Rate: {win_probability * 100:5.1f}%")
        print()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    output_dir = Path(__file__).parent
    csv_file = output_dir / "general_models_winrates.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved to CSV: {csv_file}")
    
    # Save to Excel with summary
    try:
        excel_file = output_dir / "general_models_winrates.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='General_Models_WinRates', index=False)
            
            # Summary sheet
            win_rates = df['Win_Rate'].values
            
            summary_data = {
                "Metric": [
                    "General Models Analyzed",
                    "Model Pairs",
                    "Excluded Domain Models",
                    "Highest Win Rate",
                    "Lowest Win Rate", 
                    "Average Win Rate",
                    "Most Competitive Pair",
                    "Biggest Advantage",
                    "Largest ELO Gap",
                    "Smallest ELO Gap",
                    "Average ELO Gap",
                    "ELO Range (General Models)",
                    "Performance Spread"
                ],
                "Value": [
                    len(general_models),
                    len(results),
                    f"{len(excluded_models)} models: {', '.join(excluded_models)}",
                    f"{max(win_rates) * 100:.1f}%",
                    f"{min(win_rates) * 100:.1f}%",
                    f"{win_rates.mean() * 100:.1f}%",
                    f"{min(win_rates, key=lambda x: abs(x - 0.5)) * 100:.1f}%",
                    f"{max(win_rates) * 100:.1f}%",
                    f"{df['ELO_Difference'].max():.2f}",
                    f"{df['ELO_Difference'].min():.2f}",
                    f"{df['ELO_Difference'].mean():.2f}",
                    f"{general_models[0][1]:.2f} - {general_models[-1][1]:.2f}",
                    f"{general_models[0][1] - general_models[-1][1]:.2f} ELO points"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format columns
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 35)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Saved to Excel: {excel_file}")
        
    except ImportError:
        print("⚠ openpyxl not available, skipping Excel export")
    
    # Print summary table for easy reading
    print("\n" + "=" * 75)
    print("SUMMARY TABLE - General-Purpose Models Only (9 Models)")
    print("=" * 75)
    print("| Rank | Higher Model      | vs | Lower Model       | Win Rate | ELO Gap |")
    print("|------|-------------------|----|-------------------|----------|---------|")
    
    for i, result in enumerate(results):
        print(f"| {i+1:4d} | {result['Model_Higher']:17s} | vs | {result['Model_Lower']:17s} | {result['Win_Rate_Percent']:>8s} | {result['ELO_Difference']:>7.2f} |")
    
    print("=" * 75)
    
    # Analysis insights
    total_elo_range = general_models[0][1] - general_models[-1][1]
    most_competitive = min(win_rates, key=lambda x: abs(x - 0.5))
    biggest_advantage = max(win_rates)
    
    print(f"\n📊 GENERAL MODELS ANALYSIS:")
    print(f"   Total models: {len(general_models)}")
    print(f"   ELO range: {general_models[0][1]:.2f} - {general_models[-1][1]:.2f} ({total_elo_range:.2f} points)")
    print(f"   Most competitive: {most_competitive * 100:.1f}% (closest to 50%)")
    print(f"   Biggest advantage: {biggest_advantage * 100:.1f}%")
    print(f"   Average win rate: {win_rates.mean() * 100:.1f}%")
    
    print(f"\n🚫 EXCLUDED DOMAIN-SPECIFIC MODELS:")
    for model in excluded_models:
        if model == "Spark-Chemistry-X1":
            print(f"   {model}: ELO 22.10 (chemistry-focused)")
        elif model == "LlaSMol":
            print(f"   {model}: ELO 10.84 (molecular analysis)")
        elif model == "Darwin":
            print(f"   {model}: ELO 10.32 (domain-specific)")
    
    print(f"\n🎯 Using exact TrueSkill formula: 0.5 * (1 + erf(Δμ / sqrt(σ₁²+σ₂²+2β²) / √2))")
    print(f"   This analysis focuses on general-purpose AI models only")


if __name__ == "__main__":
    main()