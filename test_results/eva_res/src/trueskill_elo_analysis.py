#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrected TrueSkill ELO Rating System for AI Model Evaluation.
Properly handles dimensions and questions to calculate meaningful ELO ratings.

Key Improvements:
1. Preserves question-level information 
2. Calculates separate ELO ratings for each dimension
3. Proper question-dimension matches per model pair
4. Aggregates dimension ELOs into overall model ratings

TrueSkill Algorithm:
- Microsoft's TrueSkill is a Bayesian skill rating system
- Each model has dimension-specific skills: N(μ, σ²) per dimension
- Conservative skill estimate: μ - 3σ (99.7% confidence lower bound)
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import pandas as pd
import itertools
from dataclasses import dataclass
import math
import warnings
warnings.filterwarnings('ignore')

try:
    import trueskill as ts
    TRUESKILL_AVAILABLE = True
except ImportError:
    TRUESKILL_AVAILABLE = False
    print("Warning: TrueSkill library not available. Please install with: pip install trueskill")

@dataclass
class DimensionRating:
    """Represents a model's TrueSkill rating for a specific dimension."""
    name: str
    dimension: str
    mu: float          # Skill mean
    sigma: float       # Skill uncertainty  
    rating: float      # Conservative rating (mu - 3*sigma)
    games_played: int  # Number of matches
    wins: int         # Number of wins
    losses: int       # Number of losses
    win_rate: float   # Win percentage

@dataclass
class ModelRating:
    """Represents a model's complete TrueSkill ratings across dimensions."""
    name: str
    dimension_ratings: Dict[str, DimensionRating]  # dimension -> rating
    overall_rating: float      # Aggregated overall rating
    aggregation_method: str    # How overall rating was calculated

class TrueSkillELOAnalyzer:
    """TrueSkill-based ELO rating system for model evaluation."""
    
    def __init__(self, results_file: str = None, processed_data_file: str = None, 
                 mu: float = 25.0, sigma: float = 8.333, 
                 beta: float = None, tau: float = None, draw_probability: float = 0.05,
                 custom_beta: Optional[float] = None, use_trueskill_default: bool = False,
                 match_mode: str = "1vs1", max_none_samples: Optional[int] = 25,
                 aggregate_dimensions: bool = False):
        """
        Initialize TrueSkill analyzer.
        
        Args:
            results_file: Path to analysis_results.json (for fallback)
            processed_data_file: Path to save/load processed_data (optional)  
            mu, sigma, beta, tau, draw_probability: TrueSkill parameters
            custom_beta: If specified, use this fixed β value and skip data-driven estimation
            use_trueskill_default: If True, use TrueSkill's default β (overrides custom_beta)
            match_mode: "1vs1" (pairwise) or "multi" (multi-model ranking per question-dimension)
            max_none_samples: Max samples for 'none' aggregation mode. None = use all matches (up to 625 per model pair per question-dimension)
            aggregate_dimensions: If True, average all dimension scores before TrueSkill calculation (reduces order sensitivity)
        """
        if not TRUESKILL_AVAILABLE:
            raise ImportError("TrueSkill library is required. Install with: pip install trueskill")
        
        if results_file is None:
            script_dir = Path(__file__).parent
            results_file = script_dir / "analysis_results.json"
        
        self.results_file = Path(results_file)
        self.processed_data_file = processed_data_file
        self.processed_data = None
        
        # Load data - try to get processed_data, fallback to results file
        self._load_data()
        
        # TrueSkill parameters
        self.mu = mu
        self.sigma = sigma
        self.tau = tau or (sigma / 100.0)
        self.draw_probability = draw_probability
        
        # β parameter handling
        if use_trueskill_default:
            # Use TrueSkill package default (don't specify β)
            self.beta = None  # Will be set by TrueSkill to default
            self.custom_beta = None
            self.use_data_driven_beta = False
            print(f"Using TrueSkill default β (will be σ/2 ≈ {sigma/2:.3f})")
        elif custom_beta is not None:
            # Use custom fixed β
            self.beta = float(custom_beta)
            self.custom_beta = custom_beta
            self.use_data_driven_beta = False
            print(f"Using custom β = {self.beta:.3f} (manual override, skipping data-driven estimation)")
        else:
            # Use data-driven β estimation
            self.beta = beta or (sigma / 2.0)
            self.custom_beta = None
            self.use_data_driven_beta = True
        
        # Store configuration
        self.use_trueskill_default = use_trueskill_default
        self.match_mode = match_mode
        self.max_none_samples = max_none_samples
        self.aggregate_dimensions = aggregate_dimensions
        
        print(f"Match mode: {match_mode.upper()}")
        if match_mode == "multi":
            print("  - Multi-model ranking: All models ranked per question-dimension")
        else:
            print("  - Pairwise 1vs1: All model pairs compete separately")
        
        print(f"Dimension aggregation: {'ENABLED' if aggregate_dimensions else 'DISABLED'}")
        if aggregate_dimensions:
            print("  - Dimensions are averaged before TrueSkill calculation (reduces order sensitivity)")
        else:
            print("  - Each dimension is calculated independently")
        
        # Setup TrueSkill environment
        if use_trueskill_default:
            # Let TrueSkill use its own defaults
            self.ts_env = ts.TrueSkill(
                mu=self.mu,
                sigma=self.sigma,
                tau=self.tau,
                draw_probability=self.draw_probability
                # Don't specify beta - let TrueSkill use default
            )
            # Update our beta to match TrueSkill's default
            self.beta = self.ts_env.beta
        else:
            self.ts_env = ts.TrueSkill(
                mu=self.mu,
                sigma=self.sigma,
                beta=self.beta,
                tau=self.tau,
                draw_probability=self.draw_probability
            )
        ts.setup(env=self.ts_env)
        
    def _load_data(self):
        """Load processed data or results data."""
        # First try to import and use processed_data directly
        try:
            from individual import IndividualEvaluationAnalyzer
            print("Loading processed data from IndividualEvaluationAnalyzer...")
            
            individual_analyzer = IndividualEvaluationAnalyzer()
            individual_analyzer.load_data()
            individual_analyzer.process_data()
            
            self.processed_data = individual_analyzer.processed_data
            self.use_real_data = True
            print("Successfully loaded real processed data!")
            return
            
        except ImportError:
            print("Warning: Could not import IndividualEvaluationAnalyzer")
        except Exception as e:
            print(f"Warning: Error loading processed data: {e}")
        
        # Fallback to results file
        print("Falling back to results file...")
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        self.use_real_data = False
        
    def _load_results(self) -> Dict[str, Any]:
        """Load analysis results from JSON file."""
        print(f"Loading results from: {self.results_file}")
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_real_question_dimension_scores(self, analysis_type: str = "full", aggregation_level: str = "double") -> Dict:
        """
        Extract question-dimension-level scores from REAL processed_data with different aggregation levels.
        
        Args:
            analysis_type: "full" (6 dimensions) or other (4 dimensions)
            aggregation_level: "double" (current), "llm_only", or "none"
        
        Returns different structures based on aggregation_level:
        - "double": judge -> model -> question -> dimension -> average_score
        - "llm_only": judge -> model -> question -> dimension -> round -> round_avg_score
        - "none": judge -> model -> question -> dimension -> round -> llm_eval -> individual_score
        """
        print(f"Extracting REAL question-dimension scores ({analysis_type}, aggregation: {aggregation_level})...")
        
        if not self.use_real_data or not self.processed_data:
            raise ValueError("Real processed_data not available! Cannot extract real scores.")
        
        if analysis_type == "full":
            target_dimensions = ['correctness', 'completeness', 'logic', 'clarity', 'theoretical_depth', 'rigor_and_information_density']
        else:
            target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
        
        question_dimension_scores = {}
        
        for judge, judge_data in self.processed_data.items():
            print(f"  Processing judge: {judge}")
            question_dimension_scores[judge] = {}
            
            for model, model_data in judge_data.items():
                question_dimension_scores[judge][model] = {}
                
                # model_data: answer_round -> question_id -> dimension -> [list of 5 scores]
                
                # First, collect all questions across all rounds
                all_questions = set()
                for round_data in model_data.values():
                    all_questions.update(round_data.keys())
                
                for question_id in sorted(all_questions):
                    question_dimension_scores[judge][model][question_id] = {}
                    
                    for dimension in target_dimensions:
                        if aggregation_level == "double":
                            # Current approach: double aggregation
                            dimension_scores_for_question = []
                            
                            for round_id, round_data in model_data.items():
                                if question_id in round_data and dimension in round_data[question_id]:
                                    round_scores = round_data[question_id][dimension]
                                    if round_scores:
                                        round_avg = sum(round_scores) / len(round_scores)
                                        dimension_scores_for_question.append(round_avg)
                            
                            if dimension_scores_for_question:
                                question_avg = sum(dimension_scores_for_question) / len(dimension_scores_for_question)
                                question_dimension_scores[judge][model][question_id][dimension] = question_avg
                                
                        elif aggregation_level == "llm_only":
                            # Only aggregate LLM evaluations, preserve round variations
                            question_dimension_scores[judge][model][question_id][dimension] = {}
                            
                            for round_id, round_data in model_data.items():
                                if question_id in round_data and dimension in round_data[question_id]:
                                    round_scores = round_data[question_id][dimension]
                                    if round_scores:
                                        round_avg = sum(round_scores) / len(round_scores)
                                        question_dimension_scores[judge][model][question_id][dimension][round_id] = round_avg
                                        
                        elif aggregation_level == "none":
                            # No aggregation: preserve all individual scores
                            question_dimension_scores[judge][model][question_id][dimension] = {}
                            
                            for round_id, round_data in model_data.items():
                                if question_id in round_data and dimension in round_data[question_id]:
                                    round_scores = round_data[question_id][dimension]
                                    if round_scores:
                                        question_dimension_scores[judge][model][question_id][dimension][round_id] = {}
                                        for idx, score in enumerate(round_scores):
                                            question_dimension_scores[judge][model][question_id][dimension][round_id][f"llm_eval_{idx}"] = score
            
            model_count = len(question_dimension_scores[judge])
            if model_count > 0:
                question_count = len(next(iter(question_dimension_scores[judge].values())))
                print(f"    Extracted REAL scores for {model_count} models × {question_count} questions (aggregation: {aggregation_level})")
        
        return question_dimension_scores
    
    def generate_dimension_matches(self, question_dimension_scores: Dict, aggregation_level: str = "double") -> Dict[str, List[Tuple]]:
        """
        Generate matches for each dimension based on different aggregation levels.
        
        Args:
            question_dimension_scores: Data structure varies by aggregation_level
            aggregation_level: "double", "llm_only", or "none"
            
        Returns: dimension -> [(winner, loser, judge, question_id, round_id?, llm_eval_id?), ...]
        """
        print(f"Generating dimension-specific matches (aggregation: {aggregation_level})...")
        
        # Handle dimension aggregation if enabled
        if self.aggregate_dimensions:
            print("  Aggregating dimensions before match generation...")
            question_dimension_scores = self._aggregate_dimensions_in_scores(question_dimension_scores, aggregation_level)
        
        dimension_matches = defaultdict(list)
        
        for judge, judge_data in question_dimension_scores.items():
            print(f"  Processing judge: {judge}")
            
            models = list(judge_data.keys())
            
            # Get all questions and dimensions
            all_questions = set()
            all_dimensions = set()
            for model_data in judge_data.values():
                all_questions.update(model_data.keys())
                for question_data in model_data.values():
                    if aggregation_level == "double":
                        all_dimensions.update(question_data.keys())
                    else:
                        # For llm_only and none, need to go deeper
                        for dim_data in question_data.values():
                            all_dimensions.add(list(question_data.keys())[list(question_data.values()).index(dim_data)])
            
            match_counts = {dim: 0 for dim in all_dimensions}
            
            # For each dimension, generate matches based on aggregation level and match mode
            for dimension in all_dimensions:
                if aggregation_level == "double":
                    if self.match_mode == "multi":
                        # Multi-model ranking: rank all models per question-dimension simultaneously
                        for question_id in all_questions:
                            # Collect all models that have scores for this question-dimension
                            models_with_scores = []
                            for model in models:
                                if (question_id in judge_data[model] and 
                                    dimension in judge_data[model][question_id]):
                                    score = judge_data[model][question_id][dimension]
                                    models_with_scores.append((model, score))
                            
                            # Need at least 2 models to create a match
                            if len(models_with_scores) >= 2:
                                # Sort by score (descending - higher is better)
                                models_with_scores.sort(key=lambda x: x[1], reverse=True)
                                
                                # Create a multi-model ranking match
                                # Format: (models_list, scores_list, judge, question_id, "multi")
                                models_list = [model for model, score in models_with_scores]
                                scores_list = [score for model, score in models_with_scores]
                                
                                dimension_matches[dimension].append((models_list, scores_list, judge, question_id, "multi"))
                                match_counts[dimension] += 1
                    else:
                        # Original 1vs1 pairwise logic
                        for question_id in all_questions:
                            for model1, model2 in itertools.combinations(models, 2):
                                if (question_id in judge_data[model1] and 
                                    dimension in judge_data[model1][question_id] and
                                    question_id in judge_data[model2] and 
                                    dimension in judge_data[model2][question_id]):
                                    
                                    score1 = judge_data[model1][question_id][dimension]
                                    score2 = judge_data[model2][question_id][dimension]
                                    
                                    if score1 > score2:
                                        winner, loser, is_draw = model1, model2, False
                                    elif score2 > score1:
                                        winner, loser, is_draw = model2, model1, False
                                    else:
                                        # Handle draw properly instead of random assignment
                                        winner, loser, is_draw = model1, model2, True
                                    
                                    dimension_matches[dimension].append((winner, loser, judge, question_id, is_draw))
                                    match_counts[dimension] += 1
                                
                elif aggregation_level == "llm_only":
                    if self.match_mode == "multi":
                        # Multi-model ranking for each question-dimension with round-level scores
                        for question_id in all_questions:
                            # Collect all models and their round-level scores
                            models_with_round_scores = []
                            for model in models:
                                if (question_id in judge_data[model] and 
                                    dimension in judge_data[model][question_id]):
                                    # Each model has multiple rounds
                                    model_rounds = judge_data[model][question_id][dimension]
                                    for round_id, score in model_rounds.items():
                                        models_with_round_scores.append((f"{model}_{round_id}", score, model))
                            
                            # Need at least 2 model-round combinations
                            if len(models_with_round_scores) >= 2:
                                # Sort by score (descending - higher is better)
                                models_with_round_scores.sort(key=lambda x: x[1], reverse=True)
                                
                                # Create a multi-model ranking match with round-level granularity
                                model_round_list = [item[0] for item in models_with_round_scores]
                                scores_list = [item[1] for item in models_with_round_scores]
                                
                                dimension_matches[dimension].append((model_round_list, scores_list, judge, question_id, "multi_rounds"))
                                match_counts[dimension] += 1
                    else:
                        # Original 1vs1 logic for llm_only
                        # Each question-dimension-model_pair produces 5×5=25 matches
                        # Model1's 5 rounds vs Model2's 5 rounds = all combinations
                        for question_id in all_questions:
                            for model1, model2 in itertools.combinations(models, 2):
                                if (question_id in judge_data[model1] and 
                                    dimension in judge_data[model1][question_id] and
                                    question_id in judge_data[model2] and 
                                    dimension in judge_data[model2][question_id]):
                                    
                                    # Get all rounds for both models
                                    rounds1 = list(judge_data[model1][question_id][dimension].keys())
                                    rounds2 = list(judge_data[model2][question_id][dimension].keys())
                                    
                                    # Generate all 5×5=25 combinations
                                    for round1 in rounds1:
                                        for round2 in rounds2:
                                            score1 = judge_data[model1][question_id][dimension][round1]
                                            score2 = judge_data[model2][question_id][dimension][round2]
                                            
                                            if score1 > score2:
                                                winner, loser, is_draw = model1, model2, False
                                            elif score2 > score1:
                                                winner, loser, is_draw = model2, model1, False
                                            else:
                                                # Handle draw properly instead of random assignment
                                                winner, loser, is_draw = model1, model2, True
                                            
                                            dimension_matches[dimension].append((winner, loser, judge, question_id, f"{round1}_vs_{round2}", is_draw))
                                            match_counts[dimension] += 1
                                        
                elif aggregation_level == "none":
                    if self.match_mode == "multi":
                        # Multi-model ranking for each question-dimension with individual LLM evaluation scores
                        for question_id in all_questions:
                            # Collect all individual LLM evaluations for all models
                            all_individual_scores = []
                            for model in models:
                                if (question_id in judge_data[model] and 
                                    dimension in judge_data[model][question_id]):
                                    # Each model has multiple rounds, each with multiple LLM evaluations
                                    model_rounds = judge_data[model][question_id][dimension]
                                    for round_id, round_data in model_rounds.items():
                                        for llm_eval_id, score in round_data.items():
                                            all_individual_scores.append((f"{model}_{round_id}_{llm_eval_id}", score, model))
                            
                            # Need at least 2 individual evaluations
                            if len(all_individual_scores) >= 2:
                                # Sort by score (descending - higher is better)
                                all_individual_scores.sort(key=lambda x: x[1], reverse=True)
                                
                                # Create a multi-model ranking match with individual evaluation granularity
                                eval_id_list = [item[0] for item in all_individual_scores]
                                scores_list = [item[1] for item in all_individual_scores]
                                
                                dimension_matches[dimension].append((eval_id_list, scores_list, judge, question_id, "multi_evals"))
                                match_counts[dimension] += 1
                    else:
                        # Original 1vs1 logic for none aggregation
                        # Maximum granularity: individual LLM evaluations
                        # Each question-dimension-model_pair could produce 25×25=625 matches
                        # But we sample 25 matches to keep computation manageable
                        for question_id in all_questions:
                            for model1, model2 in itertools.combinations(models, 2):
                                if (question_id in judge_data[model1] and 
                                    dimension in judge_data[model1][question_id] and
                                    question_id in judge_data[model2] and 
                                    dimension in judge_data[model2][question_id]):
                                    
                                    # Collect all individual scores for both models
                                    all_scores1 = []
                                    all_scores2 = []
                                    
                                    for round_id, round_data in judge_data[model1][question_id][dimension].items():
                                        for llm_eval_id, score in round_data.items():
                                            all_scores1.append((score, f"{round_id}_{llm_eval_id}"))
                                    
                                    for round_id, round_data in judge_data[model2][question_id][dimension].items():
                                        for llm_eval_id, score in round_data.items():
                                            all_scores2.append((score, f"{round_id}_{llm_eval_id}"))
                                    
                                    # Potential matches: len(all_scores1) × len(all_scores2)
                                    # Sample matches based on max_none_samples setting
                                    all_possible_matches = []
                                    for score1, id1 in all_scores1:
                                        for score2, id2 in all_scores2:
                                            all_possible_matches.append((score1, score2, id1, id2))
                                    
                                    # Determine sample size based on max_none_samples setting
                                    max_possible = len(all_possible_matches)
                                    if self.max_none_samples is None:
                                        # Use all matches
                                        sample_size = max_possible
                                        sampled_matches = all_possible_matches
                                    else:
                                        # Use specified max or all if less
                                        sample_size = min(self.max_none_samples, max_possible)
                                        import random
                                        sampled_matches = random.sample(all_possible_matches, sample_size)
                                    
                                    for score1, score2, id1, id2 in sampled_matches:
                                        if score1 > score2:
                                            winner, loser, is_draw = model1, model2, False
                                        elif score2 > score1:
                                            winner, loser, is_draw = model2, model1, False
                                        else:
                                            # Handle draw properly instead of random assignment
                                            winner, loser, is_draw = model1, model2, True
                                        
                                        dimension_matches[dimension].append((winner, loser, judge, question_id, f"{id1}_vs_{id2}", is_draw))
                                        match_counts[dimension] += 1
            
            print(f"    Match counts by dimension: {match_counts}")
        
        total_matches = sum(len(matches) for matches in dimension_matches.values())
        print(f"Total matches generated: {total_matches}")
        
        return dimension_matches
    
    def calculate_dimension_trueskill_ratings(self, dimension_matches: Dict[str, List[Tuple]]) -> Dict[str, Dict[str, Dict[str, DimensionRating]]]:
        """
        Calculate TrueSkill ratings for each dimension separately.
        Returns: judge -> dimension -> model -> DimensionRating
        """
        print("Calculating dimension-specific TrueSkill ratings...")
        
        all_ratings = {}  # judge -> dimension -> model -> DimensionRating
        
        for dimension, matches in dimension_matches.items():
            print(f"  Processing dimension: {dimension} ({len(matches)} matches)")
            
            # Group matches by judge - handle different match formats
            matches_by_judge = defaultdict(list)
            for match in matches:
                judge = match[2]  # judge is always at position 2
                
                # Check if this is a multi-model match or 1vs1 match
                if len(match) >= 5 and match[4] == "multi":
                    # Multi-model match: (models_list, scores_list, judge, question_id, "multi")
                    models_list, scores_list = match[0], match[1]
                    matches_by_judge[judge].append(("multi", models_list, scores_list))
                else:
                    # 1vs1 match: extract winner, loser and draw flag
                    winner, loser = match[0], match[1]
                    
                    # Check for draw flag
                    is_draw = False
                    if len(match) >= 5 and isinstance(match[4], bool):
                        is_draw = match[4]
                    elif len(match) >= 6 and isinstance(match[5], bool):
                        is_draw = match[5]
                    
                    matches_by_judge[judge].append(("1vs1", winner, loser, is_draw))
            
            for judge, judge_matches in matches_by_judge.items():
                if judge not in all_ratings:
                    all_ratings[judge] = {}
                
                print(f"    Judge {judge}: {len(judge_matches)} matches")
                
                # Initialize ratings for all models in this judge-dimension combination
                model_ratings = {}
                model_stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0})
                
                # Get all unique models from all matches
                all_models = set()
                for match in judge_matches:
                    if match[0] == "multi":
                        # Multi-model match
                        models_list = match[1]
                        all_models.update(models_list)
                    else:
                        # 1vs1 match
                        winner, loser = match[1], match[2]
                        all_models.add(winner)
                        all_models.add(loser)
                
                # Initialize TrueSkill ratings
                for model in all_models:
                    model_ratings[model] = self.ts_env.Rating()
                
                # Process matches sequentially
                for match in judge_matches:
                    if match[0] == "multi":
                        # Multi-model ranking match
                        models_list, scores_list = match[1], match[2]
                        
                        # Create rating groups for TrueSkill rate() function
                        rating_groups = []
                        for model in models_list:
                            rating_groups.append([model_ratings[model]])
                        
                        # Convert scores to ranks (lower rank = better performance)
                        # Sort by scores (descending) and assign ranks
                        model_score_pairs = list(zip(models_list, scores_list))
                        model_score_pairs.sort(key=lambda x: x[1], reverse=True)
                        
                        # Create ranks - models with same score get same rank
                        ranks = []
                        current_rank = 0
                        for i, (model, score) in enumerate(model_score_pairs):
                            if i > 0 and score < model_score_pairs[i-1][1]:
                                current_rank = i
                            ranks.append(current_rank)
                        
                        # Use TrueSkill's rate() function for multi-model ranking
                        new_ratings = ts.rate(rating_groups, ranks=ranks)
                        
                        # Update model ratings
                        for i, model in enumerate(models_list):
                            model_ratings[model] = new_ratings[i][0]
                            model_stats[model]["games"] += 1
                            
                            # Calculate wins based on rank (better rank = more wins)
                            wins_gained = (len(models_list) - 1 - ranks[i]) / (len(models_list) - 1) if len(models_list) > 1 else 0
                            model_stats[model]["wins"] += wins_gained
                            model_stats[model]["losses"] += (1 - wins_gained)
                    
                    else:
                        # 1vs1 match
                        winner, loser, is_draw = match[1], match[2], match[3]
                        
                        # Get current ratings
                        winner_rating = model_ratings[winner]
                        loser_rating = model_ratings[loser]
                        
                        # Update ratings based on match outcome
                        if is_draw:
                            new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating, drawn=True)
                        else:
                            new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating)
                        
                        # Store updated ratings
                        model_ratings[winner] = new_winner_rating
                        model_ratings[loser] = new_loser_rating
                        
                        # Update statistics
                        model_stats[winner]["games"] += 1
                        model_stats[loser]["games"] += 1
                        
                        if is_draw:
                            # Both players get 0.5 wins for a draw
                            model_stats[winner]["wins"] += 0.5
                            model_stats[loser]["wins"] += 0.5
                            model_stats[winner]["losses"] += 0.5
                            model_stats[loser]["losses"] += 0.5
                        else:
                            # Normal win/loss
                            model_stats[winner]["wins"] += 1
                            model_stats[loser]["losses"] += 1
                
                # Convert to DimensionRating objects
                judge_dimension_ratings = {}
                for model, rating in model_ratings.items():
                    stats = model_stats[model]
                    win_rate = stats["wins"] / stats["games"] if stats["games"] > 0 else 0
                    
                    judge_dimension_ratings[model] = DimensionRating(
                        name=model,
                        dimension=dimension,
                        mu=rating.mu,
                        sigma=rating.sigma,
                        rating=self.ts_env.expose(rating),  # Conservative rating
                        games_played=stats["games"],
                        wins=stats["wins"],
                        losses=stats["losses"],
                        win_rate=win_rate
                    )
                
                all_ratings[judge][dimension] = judge_dimension_ratings
        
        return all_ratings
    
    def calculate_joint_overall_ratings(self, dimension_matches: Dict[str, List[Tuple]]) -> Dict[str, Dict[str, DimensionRating]]:
        """
        Calculate joint overall ratings by combining all dimension matches.
        This is the corrected approach for overall ELO calculation.
        
        Args:
            dimension_matches: All dimension matches from generate_dimension_matches
            
        Returns: judge -> model -> DimensionRating (with dimension="overall")
        """
        print("Calculating joint overall TrueSkill ratings (联合建模)...")
        
        overall_ratings = {}  # judge -> model -> DimensionRating
        
        # Combine all matches from all dimensions
        all_matches = []
        for dimension, matches in dimension_matches.items():
            all_matches.extend(matches)
        
        print(f"  Total matches from all dimensions: {len(all_matches)}")
        
        # Group matches by judge - handle different match formats  
        matches_by_judge = defaultdict(list)
        for match in all_matches:
            judge = match[2]  # judge is always at position 2
            
            # Check if this is a multi-model match or 1vs1 match
            if len(match) >= 5 and match[4] == "multi":
                # Multi-model match: (models_list, scores_list, judge, question_id, "multi")
                models_list, scores_list = match[0], match[1]
                matches_by_judge[judge].append(("multi", models_list, scores_list))
            else:
                # 1vs1 match: extract winner, loser and draw flag
                winner, loser = match[0], match[1]
                
                # Check for draw flag
                is_draw = False
                if len(match) >= 5 and isinstance(match[4], bool):
                    is_draw = match[4]
                elif len(match) >= 6 and isinstance(match[5], bool):
                    is_draw = match[5]
                
                matches_by_judge[judge].append(("1vs1", winner, loser, is_draw))
        
        for judge, judge_matches in matches_by_judge.items():
            print(f"    Judge {judge}: {len(judge_matches)} total matches")
            
            # Initialize ratings for all models in this judge
            model_ratings = {}
            model_stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0})
            
            # Get all unique models from all matches
            all_models = set()
            for match in judge_matches:
                if match[0] == "multi":
                    # Multi-model match
                    models_list = match[1]
                    all_models.update(models_list)
                else:
                    # 1vs1 match
                    winner, loser = match[1], match[2]
                    all_models.add(winner)
                    all_models.add(loser)
            
            # Initialize TrueSkill ratings
            for model in all_models:
                model_ratings[model] = self.ts_env.Rating()
            
            # Process all matches sequentially
            for match in judge_matches:
                if match[0] == "multi":
                    # Multi-model ranking match
                    models_list, scores_list = match[1], match[2]
                    
                    # Create rating groups for TrueSkill rate() function
                    rating_groups = []
                    for model in models_list:
                        rating_groups.append([model_ratings[model]])
                    
                    # Convert scores to ranks (lower rank = better performance)
                    model_score_pairs = list(zip(models_list, scores_list))
                    model_score_pairs.sort(key=lambda x: x[1], reverse=True)
                    
                    # Create ranks - models with same score get same rank
                    ranks = []
                    current_rank = 0
                    for i, (model, score) in enumerate(model_score_pairs):
                        if i > 0 and score < model_score_pairs[i-1][1]:
                            current_rank = i
                        ranks.append(current_rank)
                    
                    # Use TrueSkill's rate() function for multi-model ranking
                    new_ratings = ts.rate(rating_groups, ranks=ranks)
                    
                    # Update model ratings
                    for i, model in enumerate(models_list):
                        model_ratings[model] = new_ratings[i][0]
                        model_stats[model]["games"] += 1
                        
                        # Calculate wins based on rank (better rank = more wins)
                        wins_gained = (len(models_list) - 1 - ranks[i]) / (len(models_list) - 1) if len(models_list) > 1 else 0
                        model_stats[model]["wins"] += wins_gained
                        model_stats[model]["losses"] += (1 - wins_gained)
                
                else:
                    # 1vs1 match
                    winner, loser, is_draw = match[1], match[2], match[3]
                    
                    # Get current ratings
                    winner_rating = model_ratings[winner]
                    loser_rating = model_ratings[loser]
                    
                    # Update ratings based on match outcome
                    if is_draw:
                        new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating, drawn=True)
                    else:
                        new_winner_rating, new_loser_rating = ts.rate_1vs1(winner_rating, loser_rating)
                    
                    # Store updated ratings
                    model_ratings[winner] = new_winner_rating
                    model_ratings[loser] = new_loser_rating
                    
                    # Update statistics
                    model_stats[winner]["games"] += 1
                    model_stats[loser]["games"] += 1
                    
                    if is_draw:
                        # Both players get 0.5 wins for a draw
                        model_stats[winner]["wins"] += 0.5
                        model_stats[loser]["wins"] += 0.5
                        model_stats[winner]["losses"] += 0.5
                        model_stats[loser]["losses"] += 0.5
                    else:
                        # Normal win/loss
                        model_stats[winner]["wins"] += 1
                        model_stats[loser]["losses"] += 1
            
            # Convert to DimensionRating objects
            judge_overall_ratings = {}
            for model, rating in model_ratings.items():
                stats = model_stats[model]
                win_rate = stats["wins"] / stats["games"] if stats["games"] > 0 else 0
                
                judge_overall_ratings[model] = DimensionRating(
                    name=model,
                    dimension="overall",
                    mu=rating.mu,
                    sigma=rating.sigma,
                    rating=self.ts_env.expose(rating),  # Conservative rating
                    games_played=stats["games"],
                    wins=stats["wins"],
                    losses=stats["losses"],
                    win_rate=win_rate
                )
            
            overall_ratings[judge] = judge_overall_ratings
        
        return overall_ratings
    
    def aggregate_dimension_ratings(self, dimension_ratings: Dict, method: str = "weighted_mean") -> Dict[str, Dict[str, ModelRating]]:
        """
        Aggregate dimension-specific ratings into overall model ratings.
        """
        print(f"Aggregating dimension ratings using method: {method}")
        
        aggregated_ratings = {}
        
        for judge, judge_data in dimension_ratings.items():
            aggregated_ratings[judge] = {}
            
            # Get all models across all dimensions
            all_models = set()
            for dimension_data in judge_data.values():
                all_models.update(dimension_data.keys())
            
            for model in all_models:
                # Collect ratings for this model across all dimensions
                model_dim_ratings = {}
                ratings_list = []
                weights_list = []
                
                for dimension, dimension_data in judge_data.items():
                    if model in dimension_data:
                        dim_rating = dimension_data[model]
                        model_dim_ratings[dimension] = dim_rating
                        ratings_list.append(dim_rating.rating)
                        weights_list.append(dim_rating.games_played)
                
                if ratings_list:
                    # Calculate aggregated rating based on method
                    if method == "weighted_mean" and sum(weights_list) > 0:
                        # Weighted average of ratings (μ - 3σ)
                        overall_rating = sum(r * w for r, w in zip(ratings_list, weights_list)) / sum(weights_list)
                        
                        # Also calculate weighted averages of mu and sigma separately
                        mus_list = [dim_rating.mu for dim_rating in model_dim_ratings.values()]
                        sigmas_list = [dim_rating.sigma for dim_rating in model_dim_ratings.values()]
                        
                        overall_mu = sum(m * w for m, w in zip(mus_list, weights_list)) / sum(weights_list)
                        overall_sigma = sum(s * w for s, w in zip(sigmas_list, weights_list)) / sum(weights_list)
                        
                        # Alternative: calculate rating from aggregated mu and sigma
                        # overall_rating_alt = overall_mu - 3 * overall_sigma
                        
                    elif method == "mean":
                        # Simple average
                        overall_rating = sum(ratings_list) / len(ratings_list)
                        mus_list = [dim_rating.mu for dim_rating in model_dim_ratings.values()]
                        sigmas_list = [dim_rating.sigma for dim_rating in model_dim_ratings.values()]
                        overall_mu = sum(mus_list) / len(mus_list)
                        overall_sigma = sum(sigmas_list) / len(sigmas_list)
                        
                    elif method == "conservative":
                        # Use minimum rating (most conservative estimate)
                        overall_rating = min(ratings_list)
                        # For conservative, also use corresponding mu and sigma
                        min_idx = ratings_list.index(overall_rating)
                        dim_rating = list(model_dim_ratings.values())[min_idx]
                        overall_mu = dim_rating.mu
                        overall_sigma = dim_rating.sigma
                        
                    elif method == "optimistic":
                        # Use maximum rating (most optimistic estimate)
                        overall_rating = max(ratings_list)
                        # For optimistic, also use corresponding mu and sigma
                        max_idx = ratings_list.index(overall_rating)
                        dim_rating = list(model_dim_ratings.values())[max_idx]
                        overall_mu = dim_rating.mu
                        overall_sigma = dim_rating.sigma
                        
                    else:
                        overall_rating = sum(ratings_list) / len(ratings_list)
                        mus_list = [dim_rating.mu for dim_rating in model_dim_ratings.values()]
                        sigmas_list = [dim_rating.sigma for dim_rating in model_dim_ratings.values()]
                        overall_mu = sum(mus_list) / len(mus_list)
                        overall_sigma = sum(sigmas_list) / len(sigmas_list)
                    
                    # Create aggregated rating object
                    aggregated_ratings[judge][model] = ModelRating(
                        name=model,
                        dimension_ratings=model_dim_ratings,
                        overall_rating=overall_rating,
                        aggregation_method=method
                    )
                    
                    # Store mu and sigma for reporting (add them as attributes)
                    aggregated_ratings[judge][model].overall_mu = overall_mu
                    aggregated_ratings[judge][model].overall_sigma = overall_sigma
                    
        return aggregated_ratings
    
    def run_full_trueskill_analysis(self, analysis_type: str = "full", aggregation_level: str = "double") -> Dict[str, Any]:
        """
        Run complete corrected TrueSkill ELO analysis with proper overall rating calculation.
        
        Args:
            analysis_type: "full" (6 dimensions) or other (4 dimensions)
            aggregation_level: "double", "llm_only", or "none"
        """
        print(f"\n=== Running Corrected TrueSkill Analysis ({analysis_type.upper()}, aggregation: {aggregation_level}) ===")
        print(f"Using real data: {self.use_real_data}")
        
        # Step 1: Extract question-dimension scores with specified aggregation level
        if self.use_real_data:
            question_dimension_scores = self.extract_real_question_dimension_scores(analysis_type, aggregation_level)
        else:
            # Fallback to simulated data (only supports "double" aggregation)
            print("WARNING: Using simulated data fallback! Only supports double aggregation.")
            question_dimension_scores = self._extract_fallback_scores(analysis_type)
            aggregation_level = "double"  # Force to double for fallback
        
        # Step 2: Generate dimension-specific matches
        dimension_matches = self.generate_dimension_matches(question_dimension_scores, aggregation_level)
        
        if not dimension_matches:
            print("No matches found for analysis!")
            return {}
        
        # Step 2.5: β Parameter Handling
        if self.use_data_driven_beta:
            print("\n--- Data-Driven β Parameter Estimation ---")
            optimal_beta, beta_method = self.estimate_optimal_beta(dimension_matches)
            if optimal_beta != self.beta:
                print(f"Updating β from {self.beta:.3f} to {optimal_beta:.3f}")
                self.beta = optimal_beta
            else:
                print(f"Keeping original β = {self.beta:.3f}")
        elif self.use_trueskill_default:
            print(f"\n--- Using TrueSkill Default β Parameter ---")
            print(f"β = {self.beta:.3f} (TrueSkill package default)")
            beta_method = f"TrueSkill package default: β={self.beta:.3f}"
        else:
            print(f"\n--- Using Custom β Parameter ---")
            print(f"β = {self.beta:.3f} (manual override)")
            beta_method = f"Manual override: β={self.beta:.3f}"
        
        # Step 3: Calculate dimension-specific TrueSkill ratings first (纯分离)
        dimension_ratings = self.calculate_dimension_trueskill_ratings(dimension_matches)
        
        # Step 4: Aggregate dimension ratings to get overall ratings (分维度计算后取平均)
        overall_ratings = self.aggregate_dimension_ratings(dimension_ratings, method="mean")
        
        # Calculate statistics
        judges_count = len(dimension_ratings)
        unique_models = len(set(model for judge_data in overall_ratings.values() for model in judge_data.keys()))
        total_matches = sum(len(matches) for matches in dimension_matches.values())
        
        print(f"Analysis Statistics:")
        print(f"  Total matches: {total_matches:,}")
        print(f"  Unique models: {unique_models}")
        print(f"  Judges: {judges_count}")
        print(f"  Dimensions: {len(dimension_matches)}")
        print(f"  Aggregation level: {aggregation_level}")
        print(f"  Data source: {'Real processed data' if self.use_real_data else 'Simulated fallback'}")
        
        # Compile results (new structure with joint overall ratings)
        results = {
            "analysis_type": analysis_type,
            "aggregation_level": aggregation_level,
            "data_source": "real" if self.use_real_data else "simulated",
            "trueskill_parameters": {
                "mu": self.mu,
                "sigma": self.sigma,
                "beta": self.beta,
                "tau": self.tau,
                "draw_probability": self.draw_probability,
                "beta_estimation_method": beta_method
            },
            "match_statistics": {
                "total_matches": total_matches,
                "unique_models": unique_models,
                "judges_count": judges_count,
                "dimensions_count": len(dimension_matches),
                "matches_by_dimension": {dim: len(matches) for dim, matches in dimension_matches.items()},
                "match_type": f"Real question-dimension matches (aggregation: {aggregation_level})" if self.use_real_data else "Simulated matches"
            },
            "dimension_ratings": self._serialize_dimension_ratings(dimension_ratings),
            "overall_ratings": self._serialize_aggregated_ratings(overall_ratings)  # Aggregated ratings (dimension average)
        }
        
        return results
    
    def _extract_fallback_scores(self, analysis_type: str) -> Dict:
        """Fallback method using simulated data from results file."""
        print("Using fallback simulated data extraction...")
        
        if analysis_type == "full":
            score_key = "model_average_scores"
            target_dimensions = ['correctness', 'completeness', 'logic', 'clarity', 'theoretical_depth', 'rigor_and_information_density']
        else:
            score_key = "model_average_scores_no_lc"
            target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
        
        question_dimension_scores = {}
        
        for judge, judge_data in self.results[score_key].items():
            question_dimension_scores[judge] = {}
            
            for model, stats in judge_data.items():
                question_dimension_scores[judge][model] = {}
                
                # Generate 27 questions
                for question_id in [f"Q{i+1}" for i in range(27)]:
                    question_dimension_scores[judge][model][question_id] = {}
                    
                    for dimension in target_dimensions:
                        if dimension in stats.get("dimension_averages", {}):
                            dim_avg = stats["dimension_averages"][dimension]
                            overall_std = stats["overall_std"]
                            
                            # Add realistic question variation
                            question_variation = np.random.normal(0, overall_std * 0.4)
                            question_score = dim_avg + question_variation
                            question_score = np.clip(question_score, 0, 10)
                            
                            question_dimension_scores[judge][model][question_id][dimension] = question_score
        
        return question_dimension_scores
    
    def _serialize_dimension_ratings(self, dimension_ratings: Dict) -> Dict[str, Any]:
        """Convert dimension ratings to serializable format."""
        serialized = {}
        
        for judge, judge_data in dimension_ratings.items():
            serialized[judge] = {}
            
            for dimension, dimension_data in judge_data.items():
                serialized[judge][dimension] = {}
                
                for model, rating in dimension_data.items():
                    serialized[judge][dimension][model] = {
                        "name": rating.name,
                        "dimension": rating.dimension,
                        "mu": float(rating.mu),
                        "sigma": float(rating.sigma),
                        "rating": float(rating.rating),
                        "games_played": rating.games_played,
                        "wins": rating.wins,
                        "losses": rating.losses,
                        "win_rate": float(rating.win_rate)
                    }
        
        return serialized
    
    def _serialize_overall_ratings(self, overall_ratings: Dict) -> Dict[str, Any]:
        """Convert joint overall ratings to serializable format."""
        serialized = {}
        
        for judge, judge_data in overall_ratings.items():
            serialized[judge] = {}
            
            for model, rating in judge_data.items():
                serialized[judge][model] = {
                    "name": rating.name,
                    "dimension": rating.dimension,  # should be "overall"
                    "mu": float(rating.mu),
                    "sigma": float(rating.sigma),
                    "rating": float(rating.rating),
                    "games_played": rating.games_played,
                    "wins": rating.wins,
                    "losses": rating.losses,
                    "win_rate": float(rating.win_rate)
                }
        
        return serialized
    
    def _serialize_aggregated_ratings(self, aggregated_ratings: Dict) -> Dict[str, Any]:
        """Convert aggregated model ratings to serializable format."""
        serialized = {}
        
        for judge, judge_data in aggregated_ratings.items():
            serialized[judge] = {}
            
            for model, model_rating in judge_data.items():
                # Serialize dimension ratings
                dim_ratings = {}
                for dimension, dim_rating in model_rating.dimension_ratings.items():
                    dim_ratings[dimension] = {
                        "mu": float(dim_rating.mu),
                        "sigma": float(dim_rating.sigma),
                        "rating": float(dim_rating.rating),
                        "games_played": dim_rating.games_played,
                        "wins": dim_rating.wins,
                        "losses": dim_rating.losses,
                        "win_rate": float(dim_rating.win_rate)
                    }
                
                serialized[judge][model] = {
                    "name": model_rating.name,
                    "overall_rating": float(model_rating.overall_rating),
                    "overall_mu": float(getattr(model_rating, 'overall_mu', 0)),
                    "overall_sigma": float(getattr(model_rating, 'overall_sigma', 0)),
                    "aggregation_method": model_rating.aggregation_method,
                    "dimension_ratings": dim_ratings
                }
        
        return serialized
    
    def _calculate_win_probability(self, mu1: float, sigma1: float, mu2: float, sigma2: float) -> float:
        """
        Calculate win probability between two TrueSkill ratings.
        
        Args:
            mu1, sigma1: Player 1's skill mean and uncertainty
            mu2, sigma2: Player 2's skill mean and uncertainty
            
        Returns:
            Probability that player 1 beats player 2
        """
        import math
        
        # Use the actual TrueSkill beta parameter from the environment
        beta = self.beta  # This is the correct system-wide beta
        
        # TrueSkill win probability formula:
        # P(A beats B) = CDF((μA - μB) / sqrt(σA² + σB² + 2β²))
        mu_diff = mu1 - mu2
        sigma_combined = math.sqrt(sigma1**2 + sigma2**2 + 2*beta**2)
        
        # Standard normal CDF using error function
        win_probability = 0.5 * (1 + math.erf(mu_diff / (sigma_combined * math.sqrt(2))))
        
        return win_probability
    
    def estimate_optimal_beta(self, dimension_matches: Dict[str, List[Tuple]]) -> Tuple[float, str]:
        """
        Estimate optimal β value using Maximum Likelihood Estimation.
        
        β represents the variance introduced by performance variability.
        We find the β that maximizes the likelihood of observed match outcomes
        given the skill differences.
        
        Returns:
            Tuple of (optimal β value, estimation method description)
        """
        print("Estimating optimal β value using Maximum Likelihood Estimation...")
        
        # Collect all matches and extract score information
        match_data = []
        for dimension, matches in dimension_matches.items():
            for match in matches:
                winner, loser, judge = match[0], match[1], match[2]
                # Extract score information if available in match tuple
                if len(match) >= 6:
                    # For detailed matches, we might have score info
                    match_data.append({
                        'winner': winner,
                        'loser': loser,
                        'judge': judge,
                        'dimension': dimension
                    })
                else:
                    match_data.append({
                        'winner': winner,
                        'loser': loser,
                        'judge': judge,
                        'dimension': dimension
                    })
        
        if len(match_data) < 100:
            method = f"Insufficient data ({len(match_data)} matches < 100), using default β"
            print(f"  {method}={self.beta:.3f}")
            return self.beta, method
        
        # First, get initial skill estimates using default beta
        print(f"  Computing initial skill estimates from {len(match_data)} matches...")
        temp_ratings = self._compute_initial_ratings(match_data)
        
        # Try different β values to find optimal
        beta_candidates = np.linspace(0.1, 2.0, 30)  # Broader range for thorough search
        best_beta = self.beta
        best_log_likelihood = float('-inf')
        
        print(f"  Testing {len(beta_candidates)} β candidates...")
        
        # Sample matches for computational efficiency
        sample_size = min(1000, len(match_data))
        sampled_matches = np.random.choice(len(match_data), sample_size, replace=False)
        
        for i, beta_candidate in enumerate(beta_candidates):
            if i % 5 == 0:
                print(f"    Progress: {i+1}/{len(beta_candidates)} (β={beta_candidate:.3f})")
            
            log_likelihood = 0
            valid_comparisons = 0
            
            for match_idx in sampled_matches:
                match = match_data[match_idx]
                winner, loser, judge, dimension = match['winner'], match['loser'], match['judge'], match['dimension']
                
                # Get skill estimates for this match
                if judge in temp_ratings and dimension in temp_ratings[judge]:
                    winner_rating = temp_ratings[judge][dimension].get(winner)
                    loser_rating = temp_ratings[judge][dimension].get(loser)
                    
                    if winner_rating and loser_rating:
                        # Calculate win probability using current β candidate
                        mu1, sigma1 = winner_rating['mu'], winner_rating['sigma']
                        mu2, sigma2 = loser_rating['mu'], loser_rating['sigma']
                        
                        # TrueSkill win probability formula
                        mu_diff = mu1 - mu2
                        sigma_combined = math.sqrt(sigma1**2 + sigma2**2 + 2*beta_candidate**2)
                        win_prob = 0.5 * (1 + math.erf(mu_diff / (sigma_combined * math.sqrt(2))))
                        
                        # Ensure probability is within valid range
                        win_prob = max(1e-10, min(1-1e-10, win_prob))
                        
                        # Add log-likelihood of observing this outcome
                        # Winner won, so we observe outcome = 1
                        log_likelihood += math.log(win_prob)
                        valid_comparisons += 1
            
            if valid_comparisons > 0:
                avg_log_likelihood = log_likelihood / valid_comparisons
                
                if avg_log_likelihood > best_log_likelihood:
                    best_log_likelihood = avg_log_likelihood
                    best_beta = beta_candidate
        
        # Additional validation: β should be reasonable relative to skill variance
        skill_variances = []
        for judge in temp_ratings:
            for dimension in temp_ratings[judge]:
                for model, rating in temp_ratings[judge][dimension].items():
                    skill_variances.append(rating['sigma']**2)
        
        method_details = []
        if skill_variances:
            avg_skill_variance = np.mean(skill_variances)
            avg_skill_sigma = math.sqrt(avg_skill_variance)
            
            # β合理范围：应该是技能不确定性的0.2到3.0倍
            # TrueSkill论文建议β约为σ/2到2σ之间
            reasonable_beta_range = (max(0.1, 0.2 * avg_skill_sigma), 
                                   min(5.0, 3.0 * avg_skill_sigma))
            
            print(f"    Skill variance analysis: avg_σ={avg_skill_sigma:.3f}, reasonable β range: {reasonable_beta_range}")
            
            if not (reasonable_beta_range[0] <= best_beta <= reasonable_beta_range[1]):
                print(f"    Note: Estimated β={best_beta:.3f} outside reasonable range {reasonable_beta_range}")
                print(f"    This suggests either: (1) high performance variability, or (2) estimation uncertainty")
                print(f"    Using MLE estimate β={best_beta:.3f} without clamping for better model fit")
                # Don't clamp - trust the MLE estimate unless it's extremely unreasonable
                if best_beta > 10.0 or best_beta < 0.05:
                    original_beta = best_beta
                    best_beta = min(max(best_beta, 0.1), 3.0)
                    method_details.append(f"extreme value clamped from {original_beta:.3f}")
        
        log_likelihood_improvement = best_log_likelihood - (-np.inf) if best_log_likelihood > -np.inf else 0
        method = f"Maximum Likelihood Estimation on {sample_size} matches"
        if method_details:
            method += f" ({', '.join(method_details)})"
        
        print(f"  Optimal β = {best_beta:.3f} (log-likelihood: {best_log_likelihood:.3f})")
        print(f"  Method: {method}")
        if best_beta != self.beta:
            print(f"  Recommendation: Use data-driven β={best_beta:.3f} instead of default β={self.beta:.3f}")
        
        return best_beta, method
    
    def _compute_initial_ratings(self, match_data: List[Dict]) -> Dict:
        """Compute initial skill ratings for beta estimation."""
        # Initialize ratings similar to main calculation
        temp_ratings = {}
        
        # Group matches by judge and dimension
        matches_by_judge_dim = defaultdict(lambda: defaultdict(list))
        for match in match_data:
            judge = match['judge']
            dimension = match['dimension']
            matches_by_judge_dim[judge][dimension].append((match['winner'], match['loser']))
        
        # Calculate initial ratings using default beta
        for judge in matches_by_judge_dim:
            temp_ratings[judge] = {}
            
            for dimension, matches in matches_by_judge_dim[judge].items():
                # Initialize TrueSkill environment
                if TRUESKILL_AVAILABLE:
                    trueskill_env = ts.TrueSkill(mu=self.mu, sigma=self.sigma, beta=self.beta)
                    
                    # Get all models
                    all_models = set()
                    for winner, loser in matches:
                        all_models.add(winner)
                        all_models.add(loser)
                    
                    # Initialize ratings
                    model_ratings = {model: trueskill_env.create_rating() for model in all_models}
                    
                    # Update with matches
                    for winner, loser in matches:
                        winner_rating = model_ratings[winner]
                        loser_rating = model_ratings[loser]
                        
                        new_winner, new_loser = trueskill_env.rate_1vs1(winner_rating, loser_rating)
                        model_ratings[winner] = new_winner
                        model_ratings[loser] = new_loser
                    
                    # Store ratings
                    temp_ratings[judge][dimension] = {
                        model: {'mu': rating.mu, 'sigma': rating.sigma}
                        for model, rating in model_ratings.items()
                    }
                else:
                    # Fallback: use default values if TrueSkill not available
                    all_models = set()
                    for winner, loser in matches:
                        all_models.add(winner)
                        all_models.add(loser)
                    
                    temp_ratings[judge][dimension] = {
                        model: {'mu': self.mu, 'sigma': self.sigma}
                        for model in all_models
                    }
        
        return temp_ratings
    
    def save_trueskill_results(self, results: Dict[str, Any], output_file: str = None):
        """Save TrueSkill analysis results to JSON and markdown files."""
        if output_file is None:
            analysis_type = results.get("analysis_type", "full")
            output_file = f"trueskill_elo_analysis_{analysis_type}.json"
        
        output_path = Path(output_file)
        
        # Save JSON results
        print(f"Saving TrueSkill results to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Generate markdown report
        md_path = output_path.with_suffix('.md')
        self._generate_trueskill_report(results, md_path)
    
    def _generate_trueskill_report(self, results: Dict[str, Any], output_path: Path):
        """Generate human-readable TrueSkill analysis report."""
        analysis_type = results.get("analysis_type", "full")
        title_suffix = " (Full Analysis)" if analysis_type == "full" else " (Excluding Logic/Clarity)"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# TrueSkill ELO Rating Analysis{title_suffix}\n\n")
            
            # Methodology
            f.write("## Methodology\n\n")
            f.write("This analysis uses Microsoft's **TrueSkill** algorithm to calculate dynamic skill ratings:\n\n")
            f.write("- **TrueSkill**: Bayesian skill rating system where each model has skill ~ N(μ, σ²)\n")
            f.write("- **μ (mu)**: Mean skill level\n")
            f.write("- **σ (sigma)**: Uncertainty about skill level\n")
            f.write("- **Rating**: Conservative estimate = μ - 3σ (99.7% confidence lower bound)\n")
            f.write("- **Match Simulation**: Multiple matches simulated from score distributions\n\n")
            
            # Parameters
            params = results["trueskill_parameters"]
            match_stats = results["match_statistics"]
            f.write("### TrueSkill Parameters\n\n")
            f.write(f"- **Initial μ**: {params['mu']}\n")
            f.write(f"- **Initial σ**: {params['sigma']:.3f}\n")
            f.write(f"- **β (skill gap)**: {params['beta']:.3f} {'(TrueSkill package default)' if 'TrueSkill package default' in params.get('beta_estimation_method', '') else '(custom fixed value)' if 'Manual override' in params.get('beta_estimation_method', '') else '(data-driven estimate)' if 'beta_estimation_method' in params else '(default)'}\n")
            f.write(f"- **τ (dynamics)**: {params['tau']:.3f}\n")
            f.write(f"- **Draw probability**: {params['draw_probability']:.2%}\n")
            if 'beta_estimation_method' in params:
                f.write(f"- **β estimation**: {params['beta_estimation_method']}\n")
            f.write("\n")
            
            f.write("### Match Statistics\n\n")
            f.write(f"- **Total matches analyzed**: {match_stats['total_matches']:,}\n")
            f.write(f"- **Unique models**: {match_stats['unique_models']}\n")
            f.write(f"- **Judge models**: {match_stats['judges_count']}\n")
            f.write(f"- **Dimensions analyzed**: {match_stats['dimensions_count']}\n")
            f.write(f"- **Match generation**: {match_stats['match_type']}\n")
            
            # Add timing information if available
            if "timing" in results:
                timing = results["timing"]
                f.write(f"- **Analysis duration**: {timing['analysis_duration_formatted']}\n")
            
            f.write("\n")
            
            # Model rankings - Overall ELO from Joint Modeling
            f.write("## TrueSkill Model Rankings - Overall ELO (Dimension Averaging)\n\n")
            
            # Check if we have overall_ratings (new structure) or ratings (old structure)
            if "overall_ratings" in results and results["overall_ratings"]:
                # New structure with joint modeling
                f.write("**Overall ELO calculated using dimension averaging**: Each dimension calculated separately, then averaged for overall rating.\n\n")
                
                for judge, judge_ratings in results["overall_ratings"].items():
                    f.write(f"### Judge: {judge}\n\n")
                    
                    # Sort models by overall rating
                    models = list(judge_ratings.items())
                    models.sort(key=lambda x: x[1]["overall_rating"], reverse=True)
                    
                    f.write("| Rank | Model | Overall ELO | μ (Skill) | σ (Uncertainty) | Aggregation | Dimensions | Win Rate vs Next | Performance Level |\n")
                    f.write("|------|-------|-------------|-----------|-----------------|-------------|------------|------------------|-------------------|\n")
                    
                    for i, (model, ratings) in enumerate(models, 1):
                        # Determine performance level based on rating
                        elo_rating = ratings["overall_rating"]
                        if elo_rating > 30:
                            level = "Elite"
                        elif elo_rating > 25:
                            level = "Expert"
                        elif elo_rating > 20:
                            level = "Advanced"
                        elif elo_rating > 15:
                            level = "Intermediate"
                        elif elo_rating > 10:
                            level = "Novice"
                        else:
                            level = "Beginner"
                        
                        # Calculate win rate vs next ranked model using TrueSkill probability
                        win_rate_vs_next = "N/A"
                        if i < len(models):
                            next_model_mu = models[i][1]["overall_mu"]
                            next_model_sigma = models[i][1]["overall_sigma"]
                            current_mu = ratings["overall_mu"]
                            current_sigma = ratings["overall_sigma"]
                            
                            # Use the helper method with correct beta
                            win_probability = self._calculate_win_probability(
                                current_mu, current_sigma, next_model_mu, next_model_sigma
                            )
                            win_rate_vs_next = f"{win_probability:.1%}"
                        
                        # For aggregated ratings, we don't have individual game stats
                        # Instead, use dimensions info
                        dimensions_count = len(ratings.get('dimension_ratings', {}))
                        aggregation_method = ratings.get('aggregation_method', 'mean')
                        
                        f.write(f"| {i} | {model} | {elo_rating:.2f} | {ratings['overall_mu']:.2f} | {ratings['overall_sigma']:.2f} | {aggregation_method} | {dimensions_count} dimensions | {win_rate_vs_next} | {level} |\n")
                    
                    f.write("\n")
                    
            elif "ratings" in results and results["ratings"]:
                # Old structure with aggregated ratings (for backward compatibility)
                f.write("**Overall ELO calculated using dimension aggregation** (legacy method).\n\n")
                
                for judge, judge_ratings in results["ratings"].items():
                    f.write(f"### Judge: {judge}\n\n")
                    
                    # Sort models by rating
                    models = list(judge_ratings.items())
                    models.sort(key=lambda x: x[1]["overall_rating"], reverse=True)
                    
                    f.write("| Rank | Model | Overall ELO | Overall μ | Overall σ | Aggregation Method | Dimensions Available |\n")
                    f.write("|------|-------|-------------|-----------|-----------|--------------------|-----------------------|\n")
                    
                    for i, (model, ratings) in enumerate(models, 1):
                        dimensions_count = len(ratings.get("dimension_ratings", {}))
                        overall_mu = ratings.get("overall_mu", 0)
                        overall_sigma = ratings.get("overall_sigma", 0)
                        
                        f.write(f"| {i} | {model} | {ratings['overall_rating']:.2f} | {overall_mu:.2f} | {overall_sigma:.2f} | {ratings['aggregation_method']} | {dimensions_count} dimensions |\n")
                    
                    f.write("\n")
            
            # Detailed dimension analysis - from dimension_ratings (纯分离)
            if "dimension_ratings" in results and results["dimension_ratings"]:
                f.write("## Detailed Dimension Analysis (Separate Modeling)\n\n")
                f.write("**Dimension ELO calculated separately**: Each dimension has independent TrueSkill calculation.\n\n")
                
                for judge, judge_data in results["dimension_ratings"].items():
                    f.write(f"### Judge: {judge}\n\n")
                    
                    # judge_data structure: dimension -> model -> rating_data
                    # We want to create one table per dimension
                    
                    for dimension in sorted(judge_data.keys()):
                        dimension_data = judge_data[dimension]  # This contains model -> rating_data
                        
                        f.write(f"#### {dimension.replace('_', ' ').title()}\n\n")
                        f.write("| Rank | Model | μ (Skill) | σ (Uncertainty) | ELO (μ-3σ) | Games | Win Rate (Total) | Win Rate vs Next | Performance Level |\n")
                        f.write("|------|-------|-----------|-----------------|------------|-------|------------------|------------------|-------------------|\n")
                        
                        # Collect all models for this dimension and sort by rating
                        dimension_models = []
                        for model_name, rating_data in dimension_data.items():
                            dimension_models.append((model_name, rating_data))
                        
                        # Sort models by ELO rating for this specific dimension
                        dimension_models.sort(key=lambda x: x[1]["rating"], reverse=True)
                        
                        # Generate table rows for this dimension
                        for rank, (model_name, rating_data) in enumerate(dimension_models, 1):
                            # Determine performance level based on ELO rating
                            elo_rating = rating_data["rating"]  # This is μ-3σ
                            if elo_rating > 30:
                                level = "Elite"
                            elif elo_rating > 25:
                                level = "Expert"
                            elif elo_rating > 20:
                                level = "Advanced"
                            elif elo_rating > 15:
                                level = "Intermediate"
                            elif elo_rating > 10:
                                level = "Novice"
                            else:
                                level = "Beginner"
                            
                            # Calculate win rate vs next ranked model in this dimension
                            win_rate_vs_next = "N/A"
                            if rank < len(dimension_models):
                                next_model_data = dimension_models[rank][1]  # Next ranked model's rating data
                                next_model_mu = next_model_data["mu"]
                                next_model_sigma = next_model_data["sigma"]
                                current_mu = rating_data["mu"]
                                current_sigma = rating_data["sigma"]
                                
                                # Use TrueSkill probability calculation
                                win_probability = self._calculate_win_probability(
                                    current_mu, current_sigma, next_model_mu, next_model_sigma
                                )
                                win_rate_vs_next = f"{win_probability:.1%}"
                            
                            # Total win rate
                            total_win_rate = rating_data['win_rate']
                            
                            f.write(f"| {rank} | {model_name} | {rating_data['mu']:.2f} | {rating_data['sigma']:.2f} | {elo_rating:.2f} | {rating_data['games_played']} | {total_win_rate:.1%} | {win_rate_vs_next} | {level} |\n")
                        
                        f.write("\n")
                
                f.write("\n")
            
            # Key insights
            f.write("## Key TrueSkill Insights\n\n")
            
            # Find overall top performer - use new overall_ratings structure
            all_ratings = []
            all_mus = []
            all_sigmas = []
            
            # Check if we have overall_ratings (new structure) or ratings (old structure)
            if "overall_ratings" in results and results["overall_ratings"]:
                for judge_ratings in results["overall_ratings"].values():
                    for model, ratings in judge_ratings.items():
                        all_ratings.append((model, ratings["overall_rating"], judge_ratings))
                        all_mus.append(ratings.get("overall_mu", 0))
                        all_sigmas.append(ratings.get("overall_sigma", 0))
            elif "ratings" in results and results["ratings"]:
                for judge_ratings in results["ratings"].values():
                    for model, ratings in judge_ratings.items():
                        all_ratings.append((model, ratings["overall_rating"], judge_ratings))
                        all_mus.append(ratings.get("overall_mu", 0))
                        all_sigmas.append(ratings.get("overall_sigma", 0))
            
            if all_ratings:
                # Top rated model overall
                top_model = max(all_ratings, key=lambda x: x[1])
                f.write(f"### Highest Rated Model\n")
                f.write(f"**{top_model[0]}** achieves the highest overall ELO rating of **{top_model[1]:.2f}**\n\n")
                
                # Most consistent model (lowest sigma)
                if all_sigmas:
                    min_sigma_idx = all_sigmas.index(min(all_sigmas))
                    most_consistent = all_ratings[min_sigma_idx]
                    f.write(f"### Most Consistent Model\n")
                    f.write(f"**{most_consistent[0]}** shows the lowest uncertainty with σ={all_sigmas[min_sigma_idx]:.2f}\n\n")
                
                # Dimension analysis summary - use dimension_ratings structure
                if "dimension_ratings" in results and results["dimension_ratings"]:
                    f.write("### Dimension Performance Summary\n\n")
                    
                    # Analyze top performers by dimension
                    dimension_leaders = {}
                    for judge_data in results["dimension_ratings"].values():
                        for dimension, dimension_data in judge_data.items():
                            for model, dim_rating in dimension_data.items():
                                if dimension not in dimension_leaders:
                                    dimension_leaders[dimension] = []
                                dimension_leaders[dimension].append((model, dim_rating["rating"], dim_rating["mu"], dim_rating["sigma"]))
                    
                    f.write("| Dimension | Top Model | ELO Rating | μ (Skill) | σ (Uncertainty) | Performance Gap |\n")
                    f.write("|-----------|-----------|------------|-----------|-----------------|------------------|\n")
                    
                    for dimension, models in dimension_leaders.items():
                        models.sort(key=lambda x: x[1], reverse=True)
                        top_model = models[0]
                        second_model = models[1] if len(models) > 1 else None
                        
                        gap = f"{top_model[1] - second_model[1]:.2f}" if second_model else "N/A"
                        
                        f.write(f"| {dimension.replace('_', ' ').title()} | {top_model[0]} | {top_model[1]:.2f} | {top_model[2]:.2f} | {top_model[3]:.2f} | {gap} |\n")
                    
                    f.write("\n")
                
                # Rating distribution
                ratings_only = [x[1] for x in all_ratings]
                f.write(f"### Rating Distribution\n")
                f.write(f"- **Mean Overall ELO**: {np.mean(ratings_only):.2f}\n")
                f.write(f"- **ELO Std**: {np.std(ratings_only):.2f}\n")
                f.write(f"- **ELO Range**: {max(ratings_only):.2f} - {min(ratings_only):.2f}\n")
                f.write(f"- **Mean μ (Skill)**: {np.mean(all_mus):.2f}\n")
                f.write(f"- **Mean σ (Uncertainty)**: {np.mean(all_sigmas):.2f}\n")
                f.write(f"- **Models Analyzed**: {len(set(x[0] for x in all_ratings))}\n")
                f.write(f"- **Data Source**: {results.get('data_source', 'unknown')}\n")
                f.write(f"- **Total Matches**: {results['match_statistics']['total_matches']:,}\n")
                f.write(f"- **Matches per Dimension**: {results['match_statistics']['total_matches'] // results['match_statistics']['dimensions_count']:,}\n\n")
                
                # Aggregation method explanation
                f.write("### Method Details\n\n")
                agg_level = results.get("aggregation_level", "unknown")
                
                f.write("**Overall ELO Calculation**:\n")
                f.write("- Uses dimension averaging approach\n")
                f.write("- Each dimension calculated independently, then averaged\n")
                f.write("- Provides balanced ranking across all evaluation aspects\n\n")
                
                f.write("**Dimension ELO Calculations**:\n")
                f.write("- Each dimension calculated independently (pure separation)\n")
                f.write("- Allows comparison of model strengths across different aspects\n\n")
                
                f.write(f"**Data Aggregation Level**: {agg_level}\n")
                if agg_level == "double":
                    f.write("- LLM评分聚合: 5个LLM评分 → 平均值\n")
                    f.write("- 回答轮次聚合: 多轮回答 → 平均值\n")
                    f.write("- 每个问题-维度生成1个匹配\n\n")
                elif agg_level == "llm_only":
                    f.write("- LLM评分聚合: 5个LLM评分 → 平均值\n")
                    f.write("- 回答轮次保留: 保持轮次间差异\n")
                    f.write("- 每个问题-维度生成N个匹配（N=回答轮次数）\n\n")
                elif agg_level == "none":
                    f.write("- 无聚合: 保留所有原始评分\n")
                    f.write("- 每个问题-维度生成N×5个匹配（N=回答轮次数）\n\n")
        
        print(f"TrueSkill analysis report saved to: {output_path}")
    
    def _aggregate_dimensions_in_scores(self, question_dimension_scores: Dict, aggregation_level: str) -> Dict:
        """
        Aggregate all dimension scores into a single 'overall' dimension for each question.
        
        This reduces order sensitivity by averaging all dimensional scores before TrueSkill calculation,
        preventing models from being trapped in loops due to being strong in some dimensions but weak in others.
        
        Args:
            question_dimension_scores: Original scores structure
            aggregation_level: "double", "llm_only", or "none"
            
        Returns: Modified scores with dimensions averaged into 'overall' dimension
        """
        aggregated_scores = {}
        
        for judge, judge_data in question_dimension_scores.items():
            aggregated_scores[judge] = {}
            
            for model, model_data in judge_data.items():
                aggregated_scores[judge][model] = {}
                
                for question_id, question_data in model_data.items():
                    aggregated_scores[judge][model][question_id] = {}
                    
                    if aggregation_level == "double":
                        # question_data = {dimension: score, ...}
                        dimension_scores = list(question_data.values())
                        overall_score = sum(dimension_scores) / len(dimension_scores) if dimension_scores else 0
                        aggregated_scores[judge][model][question_id]["overall"] = overall_score
                        
                    elif aggregation_level == "llm_only":
                        # question_data = {dimension: {round_id: score, ...}, ...}
                        aggregated_scores[judge][model][question_id]["overall"] = {}
                        
                        # Get all rounds across all dimensions
                        all_rounds = set()
                        for dim_data in question_data.values():
                            if isinstance(dim_data, dict):
                                all_rounds.update(dim_data.keys())
                        
                        # For each round, average across all dimensions
                        for round_id in all_rounds:
                            round_scores = []
                            for dim_data in question_data.values():
                                if isinstance(dim_data, dict) and round_id in dim_data:
                                    round_scores.append(dim_data[round_id])
                            
                            if round_scores:
                                overall_round_score = sum(round_scores) / len(round_scores)
                                aggregated_scores[judge][model][question_id]["overall"][round_id] = overall_round_score
                                
                    elif aggregation_level == "none":
                        # question_data = {dimension: {round_id: {llm_eval_id: score, ...}, ...}, ...}
                        aggregated_scores[judge][model][question_id]["overall"] = {}
                        
                        # Get all rounds and evaluations across all dimensions
                        all_round_eval_pairs = set()
                        for dim_data in question_data.values():
                            if isinstance(dim_data, dict):
                                for round_id, round_data in dim_data.items():
                                    if isinstance(round_data, dict):
                                        for eval_id in round_data.keys():
                                            all_round_eval_pairs.add((round_id, eval_id))
                        
                        # For each round-eval pair, average across all dimensions
                        round_eval_dict = defaultdict(dict)
                        for round_id, eval_id in all_round_eval_pairs:
                            eval_scores = []
                            for dim_data in question_data.values():
                                if (isinstance(dim_data, dict) and round_id in dim_data and 
                                    isinstance(dim_data[round_id], dict) and eval_id in dim_data[round_id]):
                                    eval_scores.append(dim_data[round_id][eval_id])
                            
                            if eval_scores:
                                overall_eval_score = sum(eval_scores) / len(eval_scores)
                                round_eval_dict[round_id][eval_id] = overall_eval_score
                        
                        aggregated_scores[judge][model][question_id]["overall"] = dict(round_eval_dict)
        
        print(f"    Aggregated {len(question_dimension_scores)} judges' scores into 'overall' dimension")
        return aggregated_scores

def main(include_logic_clarity: bool = False, custom_beta: Optional[float] = 4.1, use_trueskill_default_beta: bool = False, match_mode: str = "1vs1", max_none_samples: Optional[int] = 25):
    """
    Main function to run corrected TrueSkill ELO analysis with dimension averaging.
    
    Args:
        include_logic_clarity: If True, also generate 6-dimension analysis (includes logic and clarity)
        custom_beta: If specified, use this fixed β value instead of data-driven estimation
        use_trueskill_default_beta: If True, use TrueSkill's default β (overrides custom_beta)
        match_mode: "1vs1" for pairwise matching or "multi" for multi-model ranking
        max_none_samples: Max samples for 'none' aggregation mode. None = use all matches (up to 625 per model pair)
    """
    import time
    start_time = time.time()
    
    if not TRUESKILL_AVAILABLE:
        print("Error: TrueSkill library is not installed.")
        print("Please install it with: pip install trueskill")
        return
    
    print("Corrected TrueSkill ELO Rating Analysis - Dimension Averaging")
    print("=" * 75)
    print("This version uses REAL processed data with dimension averaging for overall ELO")
    print("Three aggregation levels: double, llm_only, none")
    print(f"Dimension analysis: 4 dimensions {'+ 6 dimensions (logic, clarity)' if include_logic_clarity else 'only'}")
    print(f"Match mode: {match_mode.upper()} ({'pairwise competitions' if match_mode == '1vs1' else 'multi-model ranking'})")
    print("Overall ELO calculation: Each dimension calculated separately, then averaged")
    
    # Determine β parameter strategy
    if use_trueskill_default_beta:
        custom_beta = None  # Will use TrueSkill package default
        print("β parameter: TRUESKILL DEFAULT (σ/2 ≈ 4.167)")
    elif custom_beta is not None:
        print(f"β parameter: FIXED at {custom_beta} (manual override)")
    else:
        print("β parameter: DATA-DRIVEN estimation")
    print()
    
    analyzer = TrueSkillELOAnalyzer(custom_beta=custom_beta, use_trueskill_default=use_trueskill_default_beta, match_mode=match_mode, max_none_samples=max_none_samples)
    
    # Define analysis configurations
    aggregation_levels = [
        ("double", "双重聚合"),
        ("llm_only", "仅LLM聚合"), 
        ("none", "完全不聚合")
    ]
    
    analysis_types = [("4dim", "no_lc", "4维度")]
    if include_logic_clarity:
        analysis_types.append(("6dim", "full", "6维度"))
    
    generated_files = []
    total_analyses = len(aggregation_levels) * len(analysis_types)
    current_analysis = 0
    
    # Run all combinations
    for aggregation_level, agg_desc in aggregation_levels:
        for dim_suffix, analysis_type, dim_desc in analysis_types:
            current_analysis += 1
            
            print(f"\n{current_analysis}/{total_analyses}. Running TrueSkill analysis ({dim_desc}, {agg_desc})...")
            analysis_start = time.time()
            
            try:
                results = analyzer.run_full_trueskill_analysis(analysis_type, aggregation_level)
                
                if results:
                    # Add timing information to results
                    analysis_time = time.time() - analysis_start
                    results["timing"] = {
                        "analysis_duration_seconds": analysis_time,
                        "analysis_duration_formatted": f"{analysis_time:.1f}s"
                    }
                    
                    # Generate output filename
                    output_filename = f"trueskill_{aggregation_level}_{dim_suffix}.json"
                    
                    # Save results
                    analyzer.save_trueskill_results(results, output_filename)
                    generated_files.append(output_filename.replace('.json', ''))
                    
                    print(f"    ✓ Saved: {output_filename} and corresponding .md file (耗时: {analysis_time:.1f}s)")
                else:
                    print(f"    ✗ Failed: No results generated")
                    
            except Exception as e:
                print(f"    ✗ Error in {agg_desc} + {dim_desc}: {e}")
                import traceback
                traceback.print_exc()
    
    # Calculate total execution time
    total_time = time.time() - start_time
    
    # Summary
    print(f"\nCorrected TrueSkill ELO analysis completed!")
    print(f"Total execution time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"Generated {len(generated_files)} analysis pairs (JSON + MD files):")
    print()
    
    for i, file_base in enumerate(generated_files, 1):
        parts = file_base.split('_')
        agg_level = parts[1]
        dim_type = parts[2]
        
        agg_descriptions = {
            "double": "双重聚合 (LLM评分→平均, 回答轮次→平均)",
            "llm_only": "仅LLM聚合 (LLM评分→平均, 保留回答轮次)",
            "none": "完全不聚合 (保留所有原始数据)"
        }
        
        dim_descriptions = {
            "4dim": "4维度 (correctness, completeness, theoretical_depth, rigor_and_information_density)",
            "6dim": "6维度 (+ logic, clarity)"
        }
        
        print(f"{i}. {file_base}.json/md")
        print(f"   - 聚合方法: {agg_descriptions.get(agg_level, agg_level)}")
        print(f"   - 维度范围: {dim_descriptions.get(dim_type, dim_type)}")
        print(f"   - 总分计算: 联合建模 (合并所有维度匹配)")
        print(f"   - 维度分计算: 纯分离 (每个维度独立计算)")
        print()
    
    print("关键改进:")
    print("+ 修正了总分ELO计算逻辑 (联合建模 vs 错误的维度ELO聚合)")
    print("+ 支持三种不同的数据聚合级别") 
    print("+ 保持了原有的报告格式 (总分表格 + 维度详细分析)")
    print("+ 每个文件包含完整的方法论说明和统计信息")
    print("+ 数据驱动的β参数估计 (替代固定超参数)")
    print(f"+ 性能优化: 平均每个分析耗时 {total_time/max(len(generated_files), 1):.1f}s")
    
if __name__ == "__main__":
    # Generate latest reports with dimension aggregation feature
    
    # 1. Standard analysis with dimension averaging
    print("=== 4-Dimension Analysis (dimension averaging) ===")
    main(include_logic_clarity=False, use_trueskill_default_beta=True, match_mode="1vs1", max_none_samples=None)
    
    # Additional configurations (uncomment as needed):
    
    # 2. 6-dimension analysis with dimension averaging
    # print("\n=== 6-Dimension Analysis (dimension averaging) ===")
    # main(include_logic_clarity=True, use_trueskill_default_beta=True, match_mode="1vs1", max_none_samples=None)
    
    # Additional configurations (uncomment as needed):
    
    # 3. 6-dimension analysis with aggregation
    # print("\n=== 6-Dimension + Aggregation Analysis ===")
    # main(include_logic_clarity=True, use_trueskill_default_beta=True, match_mode="1vs1", max_none_samples=None, aggregate_dimensions=True)
    
    # 4. Limited sampling comparison 
    # print("\n=== Limited Sampling (25 matches) + Aggregation ===")
    # main(include_logic_clarity=False, use_trueskill_default_beta=True, match_mode="1vs1", max_none_samples=25, aggregate_dimensions=True)
    
    # 5. Custom β with aggregation
    # print("\n=== Custom β=4.1 + Aggregation ===")
    # main(include_logic_clarity=False, custom_beta=4.1, use_trueskill_default_beta=False, match_mode="1vs1", max_none_samples=None, aggregate_dimensions=True)