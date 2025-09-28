#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate precise win rates using the exact same TrueSkill formula as elo_final.py.
Uses actual μ (skill) and σ (uncertainty) values from the MD report.
"""

import math
import pandas as pd
from pathlib import Path


def calculate_trueskill_win_probability(mu1: float, sigma1: float, mu2: float, sigma2: float, beta: float = 4.167) -> float:
    """
    Calculate win probability using the exact same formula as elo_final.py.
    
    This is the official TrueSkill win probability formula:
    P(A beats B) = CDF((μA - μB) / sqrt(σA² + σB² + 2β²))
    
    Args:
        mu1, sigma1: Player 1's skill mean and uncertainty  
        mu2, sigma2: Player 2's skill mean and uncertainty
        beta: TrueSkill beta parameter (skill difference scaling)
        
    Returns:
        Probability that player 1 beats player 2 (0.0 to 1.0)
    """
    # TrueSkill win probability formula (same as elo_final.py line 1376-1381)
    mu_diff = mu1 - mu2
    sigma_combined = math.sqrt(sigma1**2 + sigma2**2 + 2*beta**2)
    
    # Standard normal CDF using error function
    win_probability = 0.5 * (1 + math.erf(mu_diff / (sigma_combined * math.sqrt(2))))
    
    return win_probability


def main():
    """Calculate precise win rates using actual TrueSkill data from MD report."""
    
    # Actual data from trueskill_llm_only_4dim_rep5.md - Overall ELO table (lines 45-59)
    models_data = [
        # (rank, model_name, overall_elo, mu_skill, sigma_uncertainty, reported_win_rate)
        (1,  "MOSES",                  32.42, 35.35, 0.98, "59.7%"),
        (2,  "o3",                     31.05, 33.86, 0.94, "77.7%"), 
        (3,  "gpt-4.1",                26.70, 29.27, 0.86, "50.2%"),
        (4,  "o1",                     26.69, 29.24, 0.85, "53.8%"),
        (5,  "lightrag-4.1-nano",      26.10, 28.67, 0.85, "53.3%"),
        (6,  "lightrag-4.1",           25.60, 28.17, 0.86, "50.7%"),
        (7,  "MOSES-nano",             25.52, 28.07, 0.85, "58.7%"),
        (8,  "gpt-4.1-nano",           24.21, 26.75, 0.85, "63.4%"),
        (9,  "spark-chem13b-nothink",  22.14, 24.69, 0.85, "50.2%"),
        (10, "spark-chem13b-think",    22.10, 24.65, 0.85, "50.1%"),
        (11, "gpt-4o",                 22.06, 24.64, 0.86, "63.1%"),
        (12, "gpt-4o-mini",            20.00, 22.62, 0.87, "92.5%"),
        (13, "llasmol-top5",           10.84, 13.92, 1.03, "50.6%"),
        (14, "llasmol-top1",           10.78, 13.83, 1.02, "52.8%"),
        (15, "darwin",                 10.32, 13.40, 1.03, "N/A")
    ]
    
    print("Precise TrueSkill Win Rate Calculation")
    print("Using exact same formula as elo_final.py")
    print("=" * 80)
    print()
    
    results = []
    
    # Calculate win rates between adjacent models (higher rank vs lower rank)
    for i in range(len(models_data) - 1):
        higher_rank, higher_model, higher_elo, higher_mu, higher_sigma, reported_rate = models_data[i]
        lower_rank, lower_model, lower_elo, lower_mu, lower_sigma, _ = models_data[i + 1]
        
        # Calculate precise win probability using TrueSkill formula
        win_probability = calculate_trueskill_win_probability(
            higher_mu, higher_sigma, lower_mu, lower_sigma
        )
        
        # Extract reported win rate for comparison (remove % and convert to float)
        reported_win_prob = None
        if reported_rate != "N/A":
            reported_win_prob = float(reported_rate.strip('%')) / 100.0
        
        # Calculate differences
        elo_diff = higher_elo - lower_elo
        mu_diff = higher_mu - lower_mu
        sigma_avg = (higher_sigma + lower_sigma) / 2
        
        # Check if our calculation matches the reported rate
        match_status = "N/A"
        if reported_win_prob is not None:
            diff = abs(win_probability - reported_win_prob)
            if diff < 0.001:  # Within 0.1%
                match_status = "✓ Perfect"
            elif diff < 0.005:  # Within 0.5%
                match_status = "✓ Close"
            else:
                match_status = f"✗ Diff {diff*100:.1f}%"
        
        results.append({
            "Higher_Rank": higher_rank,
            "Higher_Model": higher_model,
            "Higher_ELO": higher_elo,
            "Higher_Mu": higher_mu,
            "Higher_Sigma": higher_sigma,
            "Lower_Rank": lower_rank,
            "Lower_Model": lower_model, 
            "Lower_ELO": lower_elo,
            "Lower_Mu": lower_mu,
            "Lower_Sigma": lower_sigma,
            "ELO_Difference": elo_diff,
            "Mu_Difference": mu_diff,
            "Sigma_Average": sigma_avg,
            "Calculated_Win_Rate": win_probability,
            "Reported_Win_Rate": reported_win_prob,
            "Calculated_Percent": f"{win_probability * 100:.1f}%",
            "Reported_Percent": reported_rate,
            "Match_Status": match_status
        })
        
        print(f"{higher_rank:2d}. {higher_model:20s} vs {lower_model:20s}")
        print(f"    ELO:  {higher_elo:6.2f} vs {lower_elo:6.2f} (Δ: {elo_diff:5.2f})")
        print(f"    Mu:   {higher_mu:6.2f} vs {lower_mu:6.2f} (Δ: {mu_diff:5.2f})")
        print(f"    Sigma: {higher_sigma:5.2f} vs {lower_sigma:5.2f} (Avg: {sigma_avg:.2f})")
        print(f"    Calculated: {win_probability * 100:5.1f}%")
        print(f"    Reported:   {reported_rate:>5s}")
        print(f"    Match:      {match_status}")
        print()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to files
    output_dir = Path(__file__).parent
    csv_file = output_dir / "precise_model_winrates.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved precise win rates to: {csv_file}")
    
    # Save to Excel with enhanced formatting
    try:
        excel_file = output_dir / "precise_model_winrates.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Precise_Win_Rates', index=False)
            
            # Summary sheet
            perfect_matches = sum(1 for status in df['Match_Status'] if status.startswith('✓ Perfect'))
            close_matches = sum(1 for status in df['Match_Status'] if status.startswith('✓ Close'))
            total_comparisons = sum(1 for status in df['Match_Status'] if status != 'N/A')
            
            calculated_rates = [r for r in df['Calculated_Win_Rate'] if not math.isnan(r)]
            
            summary_data = {
                "Metric": [
                    "Total Model Pairs",
                    "Perfect Matches (±0.1%)",
                    "Close Matches (±0.5%)",
                    "Match Rate",
                    "Highest Win Rate",
                    "Lowest Win Rate", 
                    "Average Win Rate",
                    "Most Competitive (closest to 50%)",
                    "Biggest Advantage",
                    "Formula Used"
                ],
                "Value": [
                    len(results),
                    perfect_matches,
                    close_matches,
                    f"{((perfect_matches + close_matches) / max(total_comparisons, 1) * 100):.1f}%",
                    f"{max(calculated_rates) * 100:.1f}%" if calculated_rates else "N/A",
                    f"{min(calculated_rates) * 100:.1f}%" if calculated_rates else "N/A", 
                    f"{sum(calculated_rates) / len(calculated_rates) * 100:.1f}%" if calculated_rates else "N/A",
                    f"{min(calculated_rates, key=lambda x: abs(x - 0.5)) * 100:.1f}%" if calculated_rates else "N/A",
                    f"{max(calculated_rates) * 100:.1f}%" if calculated_rates else "N/A",
                    "TrueSkill: 0.5 * (1 + erf((μ1-μ2) / sqrt(σ1²+σ2²+2β²) / sqrt(2)))"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format worksheets
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
                    
                    adjusted_width = min(max_length + 2, 50 if sheet_name == 'Summary' else 25)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Saved Excel file to: {excel_file}")
        
    except ImportError:
        print("⚠ openpyxl not available, skipping Excel export")
    
    # Validation summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    if total_comparisons > 0:
        print(f"Total comparisons with reported rates: {total_comparisons}")
        print(f"Perfect matches (±0.1%): {perfect_matches}")
        print(f"Close matches (±0.5%): {close_matches}")
        print(f"Match rate: {((perfect_matches + close_matches) / total_comparisons * 100):.1f}%")
    else:
        print("No reported win rates available for comparison")
    
    print(f"\n🎯 FORMULA USED (identical to elo_final.py):")
    print(f"   win_probability = 0.5 * (1 + erf(mu_diff / (sigma_combined * sqrt(2))))")
    print(f"   where sigma_combined = sqrt(σ1² + σ2² + 2*β²)")
    print(f"   and β = 4.167 (TrueSkill default)")
    
    if calculated_rates:
        print(f"\n📊 WIN RATE STATISTICS:")
        print(f"   Highest: {max(calculated_rates) * 100:.1f}%")
        print(f"   Lowest:  {min(calculated_rates) * 100:.1f}%")
        print(f"   Average: {sum(calculated_rates) / len(calculated_rates) * 100:.1f}%")
        print(f"   Most competitive: {min(calculated_rates, key=lambda x: abs(x - 0.5)) * 100:.1f}%")


if __name__ == "__main__":
    main()