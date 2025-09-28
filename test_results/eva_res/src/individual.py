#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Individual evaluation data extraction and statistical analysis script.
Analyzes scoring data from multiple judge LLMs evaluating AI model answers.
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import statistics
import numpy as np

class IndividualEvaluationAnalyzer:
    """Analyzer for individual evaluation scoring data."""
    
    def __init__(self, data_folder: str = None):
        if data_folder is None:
            # Default to individual folder relative to this script
            script_dir = Path(__file__).parent
            self.data_folder = script_dir.parent / "individual"
        else:
            self.data_folder = Path(data_folder)
        
        self.raw_data = []
        self.processed_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
        self.data_quality_issues = {
            "array_wrapped_scores": 0,
            "invalid_scores": [],
            "missing_evaluations": [],
            "json_parse_errors": [],
            "incomplete_evaluation_sets": []
        }
        
    def load_data(self):
        """Load all JSON files from the individual folder."""
        print(f"Loading data from: {self.data_folder}")
        
        json_files = list(self.data_folder.glob("*.json"))
        if not json_files:
            raise ValueError(f"No JSON files found in {self.data_folder}")
        
        print(f"Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            print(f"Processing: {json_file.name}")
            file_size_mb = json_file.stat().st_size / (1024 * 1024)
            print(f"  File size: {file_size_mb:.1f} MB")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    line_count = 0
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            record = json.loads(line)
                            self.raw_data.append(record)
                            line_count += 1
                            
                            if line_count % 1000 == 0:
                                print(f"  Loaded {line_count} records...")
                                
                        except json.JSONDecodeError as e:
                            self.data_quality_issues["json_parse_errors"].append({
                                "file": json_file.name,
                                "line": line_num,
                                "error": str(e)
                            })
                            
                print(f"  Loaded {line_count} records from {json_file.name}")
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                
        print(f"Total records loaded: {len(self.raw_data)}")
        
    def extract_score(self, score_value) -> float:
        """Extract numeric score from various formats."""
        if isinstance(score_value, list):
            if len(score_value) == 1 and isinstance(score_value[0], (int, float)):
                self.data_quality_issues["array_wrapped_scores"] += 1
                return float(score_value[0])
            else:
                return None  # Will be handled as invalid
        elif isinstance(score_value, (int, float)):
            return float(score_value)
        else:
            return None  # Will be handled as invalid
    
    def process_data(self):
        """Process raw data into structured format for analysis."""
        print("Processing raw data...")
        
        for record in self.raw_data:
            try:
                # Extract key fields
                judge_model = record.get("source", "unknown")
                
                # Merge different Doubao judge names into one
                if judge_model in ["Doubao-Seed-1.6-no", "shsy_doubao-seed-1-6-no"]:
                    judge_model = "Doubao-Seed-1.6-combined"
                model_name = record.get("model_name", "unknown")
                answer_round = record.get("answer_round", "unknown")
                question_id = record.get("question_id", "unknown")
                evaluation_round = record.get("evaluation_round", 0)
                evaluation_type = record.get("evaluation_type", "unknown")
                dimensions = record.get("dimensions", [])
                
                # Parse answer scores - handle markdown code blocks
                answer_str = record.get("answer", "{}")
                original_answer = answer_str  # Keep original for error reporting
                
                # Clean up markdown code blocks if present
                if "```json" in answer_str:
                    # Extract JSON from markdown code block (handles both ``` and ````)
                    start = answer_str.find("```json") + len("```json")
                    # Find closing ``` or ````
                    end_triple = answer_str.find("```", start)
                    end_quad = answer_str.find("````", start)
                    
                    # Use the earlier occurrence (triple backticks come first)
                    if end_triple != -1:
                        end = end_triple
                    elif end_quad != -1:
                        end = end_quad
                    else:
                        end = len(answer_str)
                    
                    if end > start:
                        answer_str = answer_str[start:end].strip()
                elif "````json" in answer_str:
                    # Handle four backticks specifically
                    start = answer_str.find("````json") + len("````json")
                    end = answer_str.find("````", start)
                    if end > start:
                        answer_str = answer_str[start:end].strip()
                elif "```" in answer_str and "{" in answer_str:
                    # Handle cases where json is not specified but JSON is in code block
                    lines = answer_str.split('\n')
                    json_lines = []
                    in_code_block = False
                    for line in lines:
                        if line.strip().startswith("```"):
                            in_code_block = not in_code_block
                        elif in_code_block and (line.strip().startswith("{") or json_lines):
                            json_lines.append(line)
                            if line.strip().endswith("}") and line.count("}") >= line.count("{"):
                                break
                    if json_lines:
                        answer_str = "\n".join(json_lines).strip()
                elif "````" in answer_str and "{" in answer_str:
                    # Handle four backticks without json specification
                    lines = answer_str.split('\n')
                    json_lines = []
                    in_code_block = False
                    for line in lines:
                        if line.strip().startswith("````"):
                            in_code_block = not in_code_block
                        elif in_code_block and (line.strip().startswith("{") or json_lines):
                            json_lines.append(line)
                            if line.strip().endswith("}") and line.count("}") >= line.count("{"):
                                break
                    if json_lines:
                        answer_str = "\n".join(json_lines).strip()
                
                try:
                    scores_dict = json.loads(answer_str)
                except json.JSONDecodeError:
                    # Try to handle truncated JSON by attempting to reconstruct
                    fixed_answer = answer_str
                    
                    # If JSON appears truncated (ends with quote or incomplete value)
                    if ('{' in fixed_answer and 
                        fixed_answer.count('{') != fixed_answer.count('}') and
                        not fixed_answer.endswith('}')):
                        
                        # Try to close incomplete JSON
                        if fixed_answer.endswith('"'):
                            # Case: "key": "value (missing closing quote and brace)
                            fixed_answer += '"}'
                        elif fixed_answer.endswith(':'):
                            # Case: "key":  (missing value and closing)
                            fixed_answer += ' null}'
                        elif not fixed_answer.endswith('}'):
                            # General case: try adding closing brace
                            fixed_answer += '}'
                        
                        try:
                            scores_dict = json.loads(fixed_answer)
                            print(f"    FIXED TRUNCATED JSON for {judge_model}_{model_name}_{answer_round}_{question_id}_{evaluation_round}")
                        except json.JSONDecodeError:
                            self.data_quality_issues["json_parse_errors"].append({
                                "record": f"{judge_model}_{model_name}_{answer_round}_{question_id}_{evaluation_round}",
                                "answer": original_answer,
                                "cleaned_answer": answer_str,
                                "fix_attempted": fixed_answer
                            })
                            continue
                    else:
                        self.data_quality_issues["json_parse_errors"].append({
                            "record": f"{judge_model}_{model_name}_{answer_round}_{question_id}_{evaluation_round}",
                            "answer": original_answer,
                            "cleaned_answer": answer_str
                        })
                        continue
                
                # Extract scores for each dimension
                for dimension in dimensions:
                    if dimension in scores_dict:
                        score = self.extract_score(scores_dict[dimension])
                        if score is not None and 0 <= score <= 10:
                            # Store in nested structure: judge -> model -> answer_round -> question -> dimension -> [scores]
                            self.processed_data[judge_model][model_name][answer_round][question_id][dimension].append(score)
                        elif score is not None:
                            self.data_quality_issues["invalid_scores"].append({
                                "record": f"{judge_model}_{model_name}_{answer_round}_{question_id}_{evaluation_round}",
                                "dimension": dimension,
                                "score": score,
                                "original_answer": original_answer
                            })
                    else:
                        self.data_quality_issues["missing_evaluations"].append({
                            "judge": judge_model,
                            "model": model_name,
                            "round": answer_round,
                            "question": question_id,
                            "dimension": dimension,
                            "eval_round": evaluation_round,
                            "available_dimensions": list(scores_dict.keys()),
                            "original_answer": original_answer
                        })
                        
            except Exception as e:
                print(f"Error processing record: {e}")
                
        print("Data processing complete")
        
        # Print data quality summary
        print("\nData Quality Summary:")
        print(f"  Array wrapped scores: {self.data_quality_issues['array_wrapped_scores']}")
        print(f"  Invalid scores: {len(self.data_quality_issues['invalid_scores'])}")
        print(f"  Missing evaluations: {len(self.data_quality_issues['missing_evaluations'])}")
        print(f"  JSON parse errors: {len(self.data_quality_issues['json_parse_errors'])}")
        
        # Show first few invalid scores as examples
        if self.data_quality_issues['invalid_scores']:
            if len(self.data_quality_issues['invalid_scores']) <= 10:
                print("\n  === All Invalid Scores (≤10) ===")
                for i, invalid in enumerate(self.data_quality_issues['invalid_scores']):
                    print(f"    {i+1}. {invalid['record']} - {invalid['dimension']}: {invalid['score']}")
                    print(f"       Answer: {invalid['original_answer'][:100]}...")
            else:
                print("  Examples of invalid scores:")
                for i, invalid in enumerate(self.data_quality_issues['invalid_scores'][:3]):
                    print(f"    - {invalid['record']}: {invalid['score']}")
            
        if self.data_quality_issues['json_parse_errors']:
            if len(self.data_quality_issues['json_parse_errors']) <= 10:
                print("\n  === All JSON Parse Errors (≤10) ===")
                for i, error in enumerate(self.data_quality_issues['json_parse_errors']):
                    print(f"    {i+1}. {error['record']}")
                    print(f"       Original length: {len(error['answer'])}")
                    print(f"       Original: {error['answer']}")
                    print(f"       Cleaned length: {len(error['cleaned_answer'])}")
                    print(f"       Cleaned: {error['cleaned_answer']}")
                    
                    # Check if it's truncation issue
                    if error['answer'].endswith('"') and not error['cleaned_answer'].endswith('}'):
                        print(f"       >>> LIKELY TRUNCATION: Answer ends with quote but no closing brace")
                    elif '{' in error['cleaned_answer'] and not error['cleaned_answer'].count('{') == error['cleaned_answer'].count('}'):
                        print(f"       >>> LIKELY TRUNCATION: Unmatched braces ({{ count: {error['cleaned_answer'].count('{{')}, }} count: {error['cleaned_answer'].count('}}')})")
                    print()
            else:
                print("  Examples of JSON parse errors:")
                for i, error in enumerate(self.data_quality_issues['json_parse_errors'][:3]):
                    print(f"    - {error['record']}: truncated={len(error['answer'])} chars")
                    
        # Analyze incomplete evaluation patterns with more detail
        print("\n  === Analyzing Incomplete Evaluation Patterns ===")
        incomplete_patterns = {}
        question_round_issues = defaultdict(int)
        judge_model_issues = defaultdict(int)
        
        for eval_item in self.data_quality_issues.get('incomplete_evaluation_sets', []):
            pattern_key = f"{eval_item['judge']}_{eval_item['model']}_{eval_item['dimension']}"
            if pattern_key not in incomplete_patterns:
                incomplete_patterns[pattern_key] = 0
            incomplete_patterns[pattern_key] += 1
            
            # Track which question-round combinations are problematic
            qr_key = f"R{eval_item['round']}Q{eval_item['question']}"
            question_round_issues[qr_key] += 1
            
            # Track which judge-model combinations have issues
            jm_key = f"{eval_item['judge']}_{eval_item['model']}"
            judge_model_issues[jm_key] += 1
        
        if incomplete_patterns:
            print(f"  Top incomplete patterns:")
            sorted_patterns = sorted(incomplete_patterns.items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:5]:
                parts = pattern.split('_', 2)
                if len(parts) >= 3:
                    judge, model, dim = parts[0], parts[1], parts[2]
                    print(f"    {judge} -> {model} -> {dim}: {count} incomplete sets")
                    
            print(f"\n  Most problematic Question-Round combinations:")
            sorted_qr = sorted(question_round_issues.items(), key=lambda x: x[1], reverse=True)
            for qr, count in sorted_qr[:10]:
                print(f"    {qr}: {count} different model-dimension combinations affected")
                
            print(f"\n  Most problematic Judge-Model combinations:")
            sorted_jm = sorted(judge_model_issues.items(), key=lambda x: x[1], reverse=True)
            for jm, count in sorted_jm[:10]:
                judge, model = jm.split('_', 1)
                print(f"    {judge} -> {model}: {count} incomplete dimension sets")
        
    def check_evaluation_completeness(self):
        """Check for incomplete evaluation sets (should be 5 evaluations each)."""
        print("Checking evaluation completeness...")
        
        incomplete_count = 0
        for judge_model, judge_data in self.processed_data.items():
            for model_name, model_data in judge_data.items():
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        for dimension, scores in question_data.items():
                            if len(scores) != 5:
                                incomplete_count += 1
                                issue = {
                                    "judge": judge_model,
                                    "model": model_name,
                                    "round": answer_round,
                                    "question": question_id,
                                    "dimension": dimension,
                                    "count": len(scores),
                                    "expected": 5
                                }
                                self.data_quality_issues["incomplete_evaluation_sets"].append(issue)
                                
                                # Print detailed info for first 10 issues
                                if incomplete_count <= 10:
                                    print(f"  INCOMPLETE: {judge_model} -> {model_name} -> Round {answer_round} -> {question_id} -> {dimension}: {len(scores)}/5 evaluations")
                                elif incomplete_count == 11:
                                    print(f"  ... and {len(self.data_quality_issues['incomplete_evaluation_sets']) - 10} more incomplete evaluation sets")
        
        # Detailed analysis if incomplete count is small
        if incomplete_count <= 50:
            print(f"\n  === Detailed Analysis of All {incomplete_count} Incomplete Sets ===")
            for i, issue in enumerate(self.data_quality_issues["incomplete_evaluation_sets"]):
                print(f"    {i+1}. {issue['judge']} -> {issue['model']} -> R{issue['round']} -> {issue['question']} -> {issue['dimension']}: {issue['count']}/5")
        
        if incomplete_count == 0:
            print("  OK: All evaluation sets are complete (5 evaluations each)")
        else:
            print(f"  WARNING: Found {incomplete_count} incomplete evaluation sets")
    
    def calculate_model_average_scores(self) -> Dict[str, Any]:
        """Calculate average scores for each model."""
        print("Calculating model average scores...")
        
        results = {}
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                # We need to track by (question, round, evaluation_type) combinations
                # But since our data structure doesn't separate by evaluation_type,
                # we'll count by (question, round) and the dimensions within should represent both types
                
                all_question_round_eval_scores = []
                dimension_scores = defaultdict(list)
                
                # Collect scores by (question, round) combinations 
                # Each should represent one complete evaluation (combining both evaluation types)
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        # Check if we have both evaluation types by looking at dimensions
                        with_ref_dims = ['correctness', 'completeness'] 
                        without_ref_dims = ['logic', 'clarity', 'theoretical_depth', 'rigor_and_information_density']
                        
                        # Calculate scores for with_reference evaluation type
                        with_ref_scores = []
                        for dim in with_ref_dims:
                            if dim in question_data and question_data[dim]:
                                avg_score = statistics.mean(question_data[dim])
                                with_ref_scores.append(avg_score)
                                dimension_scores[dim].append(avg_score)
                        
                        if with_ref_scores:
                            with_ref_avg = statistics.mean(with_ref_scores)
                            all_question_round_eval_scores.append(with_ref_avg)
                        
                        # Calculate scores for without_reference evaluation type  
                        without_ref_scores = []
                        for dim in without_ref_dims:
                            if dim in question_data and question_data[dim]:
                                avg_score = statistics.mean(question_data[dim])
                                without_ref_scores.append(avg_score)
                                dimension_scores[dim].append(avg_score)
                        
                        if without_ref_scores:
                            without_ref_avg = statistics.mean(without_ref_scores)
                            all_question_round_eval_scores.append(without_ref_avg)
                
                if all_question_round_eval_scores:
                    results[judge_model][model_name] = {
                        "overall_average": statistics.mean(all_question_round_eval_scores),
                        "overall_std": statistics.stdev(all_question_round_eval_scores) if len(all_question_round_eval_scores) > 1 else 0,
                        "dimension_averages": {
                            dim: statistics.mean(scores) for dim, scores in dimension_scores.items()
                        },
                        "total_evaluations": len(all_question_round_eval_scores)
                    }
                    
        return results
    
    def calculate_model_average_scores_no_logic_clarity(self) -> Dict[str, Any]:
        """Calculate average scores for each model excluding Logic and Clarity dimensions."""
        print("Calculating model average scores (excluding Logic and Clarity)...")
        
        results = {}
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                all_question_round_eval_scores = []
                dimension_scores = defaultdict(list)
                
                # Exclude logic and clarity dimensions
                target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
                
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        # Calculate scores for with_reference evaluation type (correctness, completeness)
                        with_ref_dims = ['correctness', 'completeness'] 
                        with_ref_scores = []
                        for dim in with_ref_dims:
                            if dim in question_data and question_data[dim]:
                                avg_score = statistics.mean(question_data[dim])
                                with_ref_scores.append(avg_score)
                                dimension_scores[dim].append(avg_score)
                        
                        if with_ref_scores:
                            with_ref_avg = statistics.mean(with_ref_scores)
                            all_question_round_eval_scores.append(with_ref_avg)
                        
                        # Calculate scores for without_reference evaluation type (excluding logic and clarity)
                        without_ref_dims = ['theoretical_depth', 'rigor_and_information_density']
                        without_ref_scores = []
                        for dim in without_ref_dims:
                            if dim in question_data and question_data[dim]:
                                avg_score = statistics.mean(question_data[dim])
                                without_ref_scores.append(avg_score)
                                dimension_scores[dim].append(avg_score)
                        
                        if without_ref_scores:
                            without_ref_avg = statistics.mean(without_ref_scores)
                            all_question_round_eval_scores.append(without_ref_avg)
                
                if all_question_round_eval_scores:
                    results[judge_model][model_name] = {
                        "overall_average": statistics.mean(all_question_round_eval_scores),
                        "overall_std": statistics.stdev(all_question_round_eval_scores) if len(all_question_round_eval_scores) > 1 else 0,
                        "dimension_averages": {
                            dim: statistics.mean(scores) for dim, scores in dimension_scores.items()
                        },
                        "total_evaluations": len(all_question_round_eval_scores)
                    }
                    
        return results
    
    def find_best_answer_rounds(self) -> Dict[str, Any]:
        """Find the best answer round for each model with detailed statistics."""
        print("Finding best answer rounds...")
        
        results = {}
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                round_stats = {}
                
                for answer_round, round_data in model_data.items():
                    round_scores = []
                    
                    for question_id, question_data in round_data.items():
                        # Calculate average score across all dimensions for this question
                        question_scores = []
                        for dimension, scores in question_data.items():
                            if scores:
                                question_scores.append(statistics.mean(scores))
                        
                        if question_scores:
                            round_scores.append(statistics.mean(question_scores))
                    
                    if round_scores:
                        round_mean = statistics.mean(round_scores)
                        round_std = statistics.stdev(round_scores) if len(round_scores) > 1 else 0
                        
                        round_stats[answer_round] = {
                            "mean": round_mean,
                            "std": round_std,
                            "count": len(round_scores)
                        }
                
                if round_stats:
                    # Find best round based on mean score
                    best_round_key = max(round_stats.keys(), key=lambda k: round_stats[k]["mean"])
                    best_stats = round_stats[best_round_key]
                    
                    results[judge_model][model_name] = {
                        "best_round": best_round_key,
                        "best_score": best_stats["mean"],
                        "best_std": best_stats["std"],
                        "all_round_stats": round_stats,
                        "all_round_scores": {k: v["mean"] for k, v in round_stats.items()}  # Keep for compatibility
                    }
                    
        return results
    
    def analyze_best_answer_rounds_no_logic_clarity(self) -> Dict[str, Any]:
        """Find the best answer round for each model excluding Logic and Clarity dimensions."""
        print("Finding best answer rounds (excluding Logic and Clarity)...")
        
        results = {}
        target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                round_stats = {}
                
                for answer_round, round_data in model_data.items():
                    round_scores = []
                    
                    for question_id, question_data in round_data.items():
                        # Calculate average score across target dimensions for this question
                        question_scores = []
                        for dimension, scores in question_data.items():
                            if dimension in target_dimensions and scores:
                                question_scores.append(statistics.mean(scores))
                        
                        if question_scores:
                            round_scores.append(statistics.mean(question_scores))
                    
                    if round_scores:
                        round_mean = statistics.mean(round_scores)
                        round_std = statistics.stdev(round_scores) if len(round_scores) > 1 else 0
                        
                        round_stats[answer_round] = {
                            "mean": round_mean,
                            "std": round_std,
                            "count": len(round_scores)
                        }
                
                if round_stats:
                    # Find best round based on mean score
                    best_round_key = max(round_stats.keys(), key=lambda k: round_stats[k]["mean"])
                    best_stats = round_stats[best_round_key]
                    
                    results[judge_model][model_name] = {
                        "best_round": best_round_key,
                        "best_score": best_stats["mean"],
                        "best_std": best_stats["std"],
                        "all_round_stats": round_stats,
                        "all_round_scores": {k: v["mean"] for k, v in round_stats.items()}
                    }
                    
        return results
    
    def calculate_answer_round_volatility(self) -> Dict[str, Any]:
        """Calculate volatility across different answer rounds."""
        print("Calculating answer round volatility...")
        
        results = {}
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                round_averages = []
                
                for answer_round, round_data in model_data.items():
                    round_scores = []
                    
                    for question_id, question_data in round_data.items():
                        for dimension, scores in question_data.items():
                            if scores:
                                round_scores.append(statistics.mean(scores))
                    
                    if round_scores:
                        round_averages.append(statistics.mean(round_scores))
                
                if len(round_averages) > 1:
                    mean_score = statistics.mean(round_averages)
                    std_score = statistics.stdev(round_averages)
                    cv = std_score / mean_score if mean_score > 0 else 0
                    
                    results[judge_model][model_name] = {
                        "round_scores": round_averages,
                        "mean": mean_score,
                        "std": std_score,
                        "coefficient_of_variation": cv
                    }
                    
        return results
    
    def calculate_model_stability_no_logic_clarity(self) -> Dict[str, Any]:
        """Calculate model stability excluding Logic and Clarity dimensions."""
        print("Calculating model stability (excluding Logic and Clarity)...")
        
        target_dimensions = ['correctness', 'completeness', 'theoretical_depth', 'rigor_and_information_density']
        
        # Answer round volatility (no Logic/Clarity)
        answer_round_volatility = {}
        for judge_model, judge_data in self.processed_data.items():
            answer_round_volatility[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                round_averages = []
                
                for answer_round, round_data in model_data.items():
                    round_scores = []
                    
                    for question_id, question_data in round_data.items():
                        for dimension, scores in question_data.items():
                            if dimension in target_dimensions and scores:
                                round_scores.append(statistics.mean(scores))
                    
                    if round_scores:
                        round_averages.append(statistics.mean(round_scores))
                
                if len(round_averages) > 1:
                    mean_score = statistics.mean(round_averages)
                    std_score = statistics.stdev(round_averages)
                    cv = std_score / mean_score if mean_score > 0 else 0
                    
                    answer_round_volatility[judge_model][model_name] = {
                        "round_scores": round_averages,
                        "mean": mean_score,
                        "std": std_score,
                        "coefficient_of_variation": cv
                    }
        
        # Question volatility (no Logic/Clarity)
        question_volatility = {}
        for judge_model, judge_data in self.processed_data.items():
            question_volatility[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                question_averages = defaultdict(list)
                
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        question_scores = []
                        
                        for dimension, scores in question_data.items():
                            if dimension in target_dimensions and scores:
                                question_scores.append(statistics.mean(scores))
                        
                        if question_scores:
                            question_averages[question_id].append(statistics.mean(question_scores))
                
                # Calculate average score per question across all rounds
                question_means = {}
                for question_id, scores in question_averages.items():
                    if scores:
                        question_means[question_id] = statistics.mean(scores)
                
                if len(question_means) > 1:
                    all_question_scores = list(question_means.values())
                    mean_score = statistics.mean(all_question_scores)
                    std_score = statistics.stdev(all_question_scores)
                    cv = std_score / mean_score if mean_score > 0 else 0
                    
                    question_volatility[judge_model][model_name] = {
                        "question_scores": question_means,
                        "mean": mean_score,
                        "std": std_score,
                        "coefficient_of_variation": cv
                    }
        
        return {
            "answer_round_volatility": answer_round_volatility,
            "question_volatility": question_volatility
        }
    
    def calculate_question_volatility(self) -> Dict[str, Any]:
        """Calculate volatility across different questions."""
        print("Calculating question volatility...")
        
        results = {}
        
        for judge_model, judge_data in self.processed_data.items():
            results[judge_model] = {}
            
            for model_name, model_data in judge_data.items():
                question_averages = defaultdict(list)
                
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        question_scores = []
                        
                        for dimension, scores in question_data.items():
                            if scores:
                                question_scores.append(statistics.mean(scores))
                        
                        if question_scores:
                            question_averages[question_id].append(statistics.mean(question_scores))
                
                # Calculate average score per question across all rounds
                question_means = {}
                for question_id, scores in question_averages.items():
                    if scores:
                        question_means[question_id] = statistics.mean(scores)
                
                if len(question_means) > 1:
                    all_question_scores = list(question_means.values())
                    mean_score = statistics.mean(all_question_scores)
                    std_score = statistics.stdev(all_question_scores)
                    cv = std_score / mean_score if mean_score > 0 else 0
                    
                    results[judge_model][model_name] = {
                        "question_scores": question_means,
                        "mean": mean_score,
                        "std": std_score,
                        "coefficient_of_variation": cv
                    }
                    
        return results
    
    def calculate_judge_volatility(self) -> Dict[str, Any]:
        """Calculate volatility between different judges."""
        print("Calculating judge volatility...")
        
        # Group by (model, round, question, dimension) to compare judges
        judge_comparison = defaultdict(lambda: defaultdict(list))
        
        for judge_model, judge_data in self.processed_data.items():
            for model_name, model_data in judge_data.items():
                for answer_round, round_data in model_data.items():
                    for question_id, question_data in round_data.items():
                        for dimension, scores in question_data.items():
                            if scores:
                                key = (model_name, answer_round, question_id, dimension)
                                avg_score = statistics.mean(scores)
                                judge_comparison[key][judge_model].append(avg_score)
        
        # Calculate volatility for each combination
        results = {}
        
        for key, judge_scores in judge_comparison.items():
            model_name, answer_round, question_id, dimension = key
            
            if model_name not in results:
                results[model_name] = {}
            if answer_round not in results[model_name]:
                results[model_name][answer_round] = {}
            if question_id not in results[model_name][answer_round]:
                results[model_name][answer_round][question_id] = {}
            
            if len(judge_scores) > 1:
                # Get average score from each judge
                judge_averages = []
                for judge, scores in judge_scores.items():
                    judge_averages.append(statistics.mean(scores))
                
                if len(judge_averages) > 1:
                    mean_score = statistics.mean(judge_averages)
                    std_score = statistics.stdev(judge_averages)
                    cv = std_score / mean_score if mean_score > 0 else 0
                    
                    results[model_name][answer_round][question_id][dimension] = {
                        "judge_scores": {judge: statistics.mean(scores) for judge, scores in judge_scores.items()},
                        "mean": mean_score,
                        "std": std_score,
                        "coefficient_of_variation": cv
                    }
        
        return results
    
    def generate_data_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report."""
        print("Generating data quality report...")
        
        report = {
            "summary": {
                "total_records": len(self.raw_data),
                "array_wrapped_scores": self.data_quality_issues["array_wrapped_scores"],
                "invalid_scores_count": len(self.data_quality_issues["invalid_scores"]),
                "missing_evaluations_count": len(self.data_quality_issues["missing_evaluations"]),
                "json_parse_errors_count": len(self.data_quality_issues["json_parse_errors"]),
                "incomplete_evaluation_sets_count": len(self.data_quality_issues["incomplete_evaluation_sets"])
            },
            "details": self.data_quality_issues
        }
        
        return report
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analysis and return all results."""
        print("Starting full analysis...")
        
        # Load and process data
        self.load_data()
        self.process_data()
        self.check_evaluation_completeness()
        
        # Run all analyses
        results = {
            "model_average_scores": self.calculate_model_average_scores(),
            "best_answer_rounds": self.find_best_answer_rounds(),
            "answer_round_volatility": self.calculate_answer_round_volatility(),
            "question_volatility": self.calculate_question_volatility(),
            "judge_volatility": self.calculate_judge_volatility(),
            "data_quality_report": self.generate_data_quality_report(),
            # New analyses without Logic and Clarity
            "model_average_scores_no_lc": self.calculate_model_average_scores_no_logic_clarity(),
            "best_answer_rounds_no_lc": self.analyze_best_answer_rounds_no_logic_clarity(),
            "model_stability_no_lc": self.calculate_model_stability_no_logic_clarity()
        }
        
        print("Analysis complete!")
        return results
    
    def save_results(self, results: Dict[str, Any], output_file: str = None):
        """Save analysis results to JSON file."""
        if output_file is None:
            output_file = self.data_folder.parent / "src" / "analysis_results.json"
        else:
            output_file = Path(output_file)
        
        print(f"Saving results to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
        
        # Also save a summary report  
        summary_file = output_file.with_name("analysis_summary.md")
        self.save_summary_report(results, summary_file)
        
        # Save summary without Logic/Clarity
        summary_file_no_lc = output_file.with_name("analysis_summary_no_logic_clarity.md")
        self.save_summary_report_no_logic_clarity(results, summary_file_no_lc)
        
    def save_summary_report(self, results: Dict[str, Any], output_file: Path):
        """Save comprehensive human-readable summary report in Markdown format."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Individual Evaluation Analysis Summary\n\n")
            
            # Data Quality Summary
            quality = results["data_quality_report"]["summary"]
            f.write("## Data Quality Summary\n\n")
            f.write(f"- **Total records**: {quality['total_records']}\n")
            f.write(f"- **Array wrapped scores**: {quality['array_wrapped_scores']}\n")
            f.write(f"- **Invalid scores**: {quality['invalid_scores_count']}\n")
            f.write(f"- **Missing evaluations**: {quality['missing_evaluations_count']}\n")
            f.write(f"- **JSON parse errors**: {quality['json_parse_errors_count']}\n")
            f.write(f"- **Incomplete evaluation sets**: {quality['incomplete_evaluation_sets_count']}\n\n")
            
            # Show examples of remaining issues
            details = results["data_quality_report"]["details"]
            if details["invalid_scores"] and len(details["invalid_scores"]) <= 10:
                f.write("### All Invalid Scores\n")
                for i, issue in enumerate(details["invalid_scores"]):
                    if isinstance(issue, dict):
                        f.write(f"{i+1}. **{issue['record']}** - {issue['dimension']}: {issue['score']}\n")
                        f.write(f"   - Answer: `{issue['original_answer'][:100]}...`\n\n")
                    else:
                        f.write(f"{i+1}. {issue}\n")
                f.write("\n")
            elif details["invalid_scores"]:
                f.write("### Invalid Scores Examples\n")
                for i, issue in enumerate(details["invalid_scores"][:3]):
                    if isinstance(issue, dict):
                        f.write(f"- **{issue['record']}**: {issue['score']}\n")
                    else:
                        f.write(f"- {issue}\n")
                f.write("\n")
            
            if details["json_parse_errors"] and len(details["json_parse_errors"]) <= 10:
                f.write("### All JSON Parse Errors\n")
                for i, issue in enumerate(details["json_parse_errors"]):
                    f.write(f"{i+1}. **{issue['record']}**\n")
                    f.write(f"   - Original length: {len(issue['answer'])} chars\n")
                    f.write(f"   - Original: `{issue['answer'][:200]}{'...' if len(issue['answer']) > 200 else ''}`\n")
                    f.write(f"   - Cleaned: `{issue['cleaned_answer'][:200]}{'...' if len(issue['cleaned_answer']) > 200 else ''}`\n")
                    
                    # Analyze truncation patterns
                    if issue['answer'].endswith('"') and not issue['cleaned_answer'].endswith('}'):
                        f.write(f"   - **Issue**: Likely truncated - ends with quote, missing closing brace\n")
                    elif '{' in issue['cleaned_answer'] and issue['cleaned_answer'].count('{') != issue['cleaned_answer'].count('}'):
                        brace_diff = issue['cleaned_answer'].count('{') - issue['cleaned_answer'].count('}')
                        f.write(f"   - **Issue**: Unmatched braces (missing {brace_diff} closing braces)\n")
                    
                    if 'fix_attempted' in issue:
                        f.write(f"   - Fix attempted: `{issue['fix_attempted'][:100]}...`\n")
                    
                    f.write("\n")
                f.write("\n")
            elif details["json_parse_errors"]:
                f.write("### JSON Parse Errors Examples\n")
                for i, issue in enumerate(details["json_parse_errors"][:3]):
                    f.write(f"- **{issue['record']}**\n")
                    f.write(f"  Answer: `{issue['answer'][:100]}...`\n")
                f.write("\n")
            
            # Detailed analysis of incomplete evaluation sets if count is small
            if quality['incomplete_evaluation_sets_count'] > 0 and quality['incomplete_evaluation_sets_count'] <= 50:
                f.write("### Detailed Analysis of All Incomplete Evaluation Sets\n\n")
                incomplete_details = details.get("incomplete_evaluation_sets", [])
                if incomplete_details:
                    f.write("| # | Judge | Model | Round | Question | Dimension | Count | Expected |\n")
                    f.write("|---|-------|-------|--------|----------|-----------|--------|----------|\n")
                    
                    for i, issue in enumerate(incomplete_details, 1):
                        f.write(f"| {i} | {issue['judge']} | {issue['model']} | {issue['round']} | {issue['question']} | {issue['dimension']} | {issue['count']} | 5 |\n")
                    f.write("\n")
                    
                    # Pattern analysis
                    patterns = {}
                    for issue in incomplete_details:
                        key = f"{issue['judge']}-{issue['model']}-{issue['dimension']}"
                        if key not in patterns:
                            patterns[key] = []
                        patterns[key].append(f"R{issue['round']}Q{issue['question']}")
                    
                    f.write("#### Patterns in Incomplete Sets\n\n")
                    for pattern, locations in patterns.items():
                        judge, model, dim = pattern.split('-', 2)
                        f.write(f"- **{judge} → {model} → {dim}**: {len(locations)} incomplete sets at {', '.join(locations[:5])}")
                        if len(locations) > 5:
                            f.write(f" (and {len(locations)-5} more)")
                        f.write("\n")
                    f.write("\n")
            
            # Judge Models Overview
            f.write("## Judge Models Overview\n\n")
            f.write("| Judge Model | Total Evaluations | Data Completeness |\n")
            f.write("|-------------|-------------------|-------------------|\n")
            
            judge_stats = {}
            for judge, judge_data in results["model_average_scores"].items():
                total_evals = sum(stats["total_evaluations"] for stats in judge_data.values())
                model_count = len(judge_data)
                judge_stats[judge] = {"total_evals": total_evals, "models": model_count}
                
                # Expected calculation: 27 questions × 5 rounds × 14 models = 1890 question-round combinations per judge
                expected_total = 27 * 5 * model_count  # This should be the total
                coverage_pct = (total_evals / expected_total * 100) if expected_total > 0 else 0
                completeness = "Complete" if coverage_pct > 90 else "Partial" if coverage_pct > 50 else "Limited"
                
                f.write(f"| {judge} | {total_evals} | {completeness} ({coverage_pct:.1f}%) |\n")
                
                # Debug information
                print(f"DEBUG - Judge {judge}: {model_count} models × 135 evals = {model_count * 135} total, actual = {total_evals}")
                expected_per_model = 27 * 5  # 27 questions × 5 rounds = 135 per model
                print(f"DEBUG - Expected per model: {expected_per_model}, Got: {total_evals // model_count if model_count > 0 else 'N/A'}")
            f.write("\n")
            
            # Model Rankings with detailed dimension scores
            f.write("## Model Average Scores by Judge\n\n")
            for judge, judge_data in results["model_average_scores"].items():
                f.write(f"### Judge: {judge}\n\n")
                total_evals = judge_stats[judge]["total_evals"]
                f.write(f"*Total evaluations: {total_evals}*\n\n")
                
                # Overall ranking table
                f.write("#### Overall Ranking\n\n")
                f.write("| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |\n")
                f.write("|------|-------|---------------|---------|-------------|----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["overall_average"], reverse=True)
                expected_evals = 270  # 27 questions × 2 evaluation_types × 5 rounds
                
                for i, (model, stats) in enumerate(sorted_models, 1):
                    coverage = f"{stats['total_evaluations']}/{expected_evals} ({stats['total_evaluations']/expected_evals*100:.1f}%)"
                    f.write(f"| {i} | {model} | {stats['overall_average']:.2f} | {stats['overall_std']:.2f} | {stats['total_evaluations']} | {coverage} |\n")
                
                f.write("\n")
                
                # Dimension scores table
                f.write("#### Dimension-wise Scores\n\n")
                dimensions = ["correctness", "completeness", "logic", "clarity", "theoretical_depth", "rigor_and_information_density"]
                
                # Table header
                f.write("| Model |")
                for dim in dimensions:
                    if any(dim in model_stats.get("dimension_averages", {}) for model_stats in judge_data.values()):
                        f.write(f" {dim.replace('_', ' ').title()} |")
                f.write("\n")
                
                # Table separator
                f.write("|-------|")
                for dim in dimensions:
                    if any(dim in model_stats.get("dimension_averages", {}) for model_stats in judge_data.values()):
                        f.write("-------:|")
                f.write("\n")
                
                # Table data
                for model, stats in sorted_models:
                    f.write(f"| {model} |")
                    dim_scores = stats.get("dimension_averages", {})
                    for dim in dimensions:
                        if any(dim in model_stats.get("dimension_averages", {}) for model_stats in judge_data.values()):
                            score = dim_scores.get(dim, 0)
                            f.write(f" {score:.2f} |")
                    f.write("\n")
                
                f.write("\n")
            
            # Best Answer Rounds
            f.write("## Best Answer Rounds Analysis\n\n")
            f.write("*This shows which answer round (attempt) performed best for each model with detailed statistics.*\n\n")
            
            for judge, judge_data in results["best_answer_rounds"].items():
                f.write(f"### Judge: {judge}\n\n")
                f.write("| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |\n")
                f.write("|-------|------------|------------|----------|-------------|-------------|----------|\n")
                
                for model, stats in judge_data.items():
                    all_scores = list(stats["all_round_scores"].values())
                    if len(all_scores) > 1:
                        min_score = min(all_scores)
                        max_score = max(all_scores)
                        improvement = f"{((max_score - min_score) / min_score * 100):.1f}%" if min_score > 0 else "N/A"
                        score_range = f"{min_score:.2f} - {max_score:.2f}"
                    else:
                        improvement = "N/A"
                        score_range = f"{stats['best_score']:.2f}"
                    
                    best_std = stats.get('best_std', 0)
                    question_count = stats.get('all_round_stats', {}).get(stats['best_round'], {}).get('count', 'N/A')
                    
                    f.write(f"| {model} | {stats['best_round']} | {stats['best_score']:.2f} | {best_std:.2f} | {score_range} | {improvement} | {question_count} |\n")
                
                f.write("\n")
                
                # Detailed round-by-round statistics for MOSES and spark-chem models
                f.write("#### Detailed Round Statistics (MOSES & Spark-Chem Models)\n\n")
                
                # Define target models
                target_models = ['MOSES', 'MOSES-nano', 'spark-chem13b-think', 'spark-chem13b-nothink']
                
                for model, stats in judge_data.items():
                    if model in target_models and "all_round_stats" in stats:
                        f.write(f"##### {model}\n\n")
                        f.write("| Round | Mean Score | Std Dev | Questions | Performance |\n")
                        f.write("|-------|------------|---------|-----------|-------------|\n")
                        
                        round_stats = stats["all_round_stats"]
                        for round_num in sorted(round_stats.keys()):
                            round_data = round_stats[round_num]
                            is_best = round_num == stats["best_round"]
                            performance = "**BEST**" if is_best else "Good" if round_data["mean"] > 7 else "Average" if round_data["mean"] > 5 else "Poor"
                            
                            f.write(f"| {round_num} | {round_data['mean']:.2f} | {round_data['std']:.2f} | {round_data['count']} | {performance} |\n")
                        
                        f.write("\n")
                
                # Round comparison summary table
                f.write("#### Round Comparison Summary\n\n")
                f.write("*Average performance across all models by round*\n\n")
                
                # Collect all round data across models
                round_summary = defaultdict(list)
                for model, stats in judge_data.items():
                    if "all_round_stats" in stats:
                        for round_num, round_data in stats["all_round_stats"].items():
                            round_summary[round_num].append(round_data["mean"])
                
                if round_summary:
                    f.write("| Round | Avg Score | Models | Best Model | Worst Model |\n")
                    f.write("|-------|-----------|--------|------------|-------------|\n")
                    
                    for round_num in sorted(round_summary.keys()):
                        scores = round_summary[round_num]
                        if scores:
                            avg_score = statistics.mean(scores)
                            model_count = len(scores)
                            
                            # Find best and worst models for this round
                            round_models = []
                            for model, stats in judge_data.items():
                                if "all_round_stats" in stats and round_num in stats["all_round_stats"]:
                                    round_models.append((model, stats["all_round_stats"][round_num]["mean"]))
                            
                            if round_models:
                                round_models.sort(key=lambda x: x[1], reverse=True)
                                best_model = f"{round_models[0][0]} ({round_models[0][1]:.2f})"
                                worst_model = f"{round_models[-1][0]} ({round_models[-1][1]:.2f})"
                            else:
                                best_model = worst_model = "N/A"
                            
                            f.write(f"| {round_num} | {avg_score:.2f} | {model_count} | {best_model} | {worst_model} |\n")
                    
                    f.write("\n")
                
                f.write("\n")
            
            # Model Stability Analysis
            f.write("## Model Stability Analysis\n\n")
            
            # Answer Round Volatility
            f.write("### Answer Round Volatility\n\n")
            f.write("*Measures consistency across different answer rounds. Lower CV = more stable.*\n\n")
            
            for judge, judge_data in results["answer_round_volatility"].items():
                f.write(f"#### Judge: {judge}\n\n")
                f.write("| Rank | Model | Mean Score | Std Dev | CV | Stability |\n")
                f.write("|------|-------|------------|---------|----|-----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["coefficient_of_variation"])
                for i, (model, stats) in enumerate(sorted_models, 1):
                    cv = stats["coefficient_of_variation"]
                    stability = "Excellent" if cv < 0.1 else "Good" if cv < 0.2 else "Fair" if cv < 0.3 else "Poor"
                    f.write(f"| {i} | {model} | {stats['mean']:.2f} | {stats['std']:.2f} | {cv:.3f} | {stability} |\n")
                
                f.write("\n")
            
            # Question Volatility  
            f.write("### Question-to-Question Volatility\n\n")
            f.write("*Measures consistency across different questions. Lower CV = more consistent.*\n\n")
            
            for judge, judge_data in results["question_volatility"].items():
                f.write(f"#### Judge: {judge}\n\n")
                f.write("| Rank | Model | Mean Score | Std Dev | CV | Consistency |\n")
                f.write("|------|-------|------------|---------|----|-----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["coefficient_of_variation"])
                for i, (model, stats) in enumerate(sorted_models, 1):
                    cv = stats["coefficient_of_variation"]
                    consistency = "Excellent" if cv < 0.2 else "Good" if cv < 0.3 else "Fair" if cv < 0.4 else "Poor"
                    f.write(f"| {i} | {model} | {stats['mean']:.2f} | {stats['std']:.2f} | {cv:.3f} | {consistency} |\n")
                
                f.write("\n")
            
            # Judge Reliability Analysis
            f.write("## Judge Model Reliability Analysis\n\n")
            f.write("*Compares how different judge models rate the same answers.*\n\n")
            
            judge_volatility = results["judge_volatility"]
            if judge_volatility:
                # Aggregate judge volatility statistics
                all_cvs = []
                model_judge_stats = {}
                
                for model_name, model_data in judge_volatility.items():
                    if model_name not in model_judge_stats:
                        model_judge_stats[model_name] = {"cvs": [], "count": 0}
                    
                    for round_data in model_data.values():
                        for question_data in round_data.values():
                            for dimension_data in question_data.values():
                                cv = dimension_data.get("coefficient_of_variation", 0)
                                if cv > 0:  # Valid CV
                                    all_cvs.append(cv)
                                    model_judge_stats[model_name]["cvs"].append(cv)
                                    model_judge_stats[model_name]["count"] += 1
                
                if all_cvs:
                    avg_judge_cv = statistics.mean(all_cvs)
                    f.write(f"**Overall Judge Agreement**: CV = {avg_judge_cv:.3f}\n")
                    
                    agreement_level = "Excellent" if avg_judge_cv < 0.1 else "Good" if avg_judge_cv < 0.2 else "Fair" if avg_judge_cv < 0.3 else "Poor"
                    f.write(f"**Agreement Level**: {agreement_level}\n\n")
                    
                    # Model-specific judge agreement
                    f.write("### Judge Agreement by Model\n\n")
                    f.write("| Model | Avg Judge CV | Agreement Level | Measurements |\n")
                    f.write("|-------|--------------|-----------------|---------------|\n")
                    
                    for model, stats in model_judge_stats.items():
                        if stats["cvs"]:
                            avg_cv = statistics.mean(stats["cvs"])
                            agreement = "Excellent" if avg_cv < 0.1 else "Good" if avg_cv < 0.2 else "Fair" if avg_cv < 0.3 else "Poor"
                            f.write(f"| {model} | {avg_cv:.3f} | {agreement} | {stats['count']} |\n")
                    
                    f.write("\n")
            
            # Key Insights Summary
            f.write("## Key Insights Summary\n\n")
            
            # Top performers
            f.write("### Top Performing Models\n")
            main_judge = list(results["model_average_scores"].keys())[0]
            top_models = sorted(results["model_average_scores"][main_judge].items(), 
                              key=lambda x: x[1]["overall_average"], reverse=True)[:3]
            
            for i, (model, stats) in enumerate(top_models, 1):
                f.write(f"{i}. **{model}**: {stats['overall_average']:.2f} ± {stats['overall_std']:.2f}\n")
            f.write("\n")
            
            # Most stable models
            f.write("### Most Stable Models (Answer Round Volatility)\n")
            if main_judge in results["answer_round_volatility"]:
                stable_models = sorted(results["answer_round_volatility"][main_judge].items(), 
                                     key=lambda x: x[1]["coefficient_of_variation"])[:3]
                for i, (model, stats) in enumerate(stable_models, 1):
                    f.write(f"{i}. **{model}**: CV = {stats['coefficient_of_variation']:.3f}\n")
            f.write("\n")
            
            # Most consistent models  
            f.write("### Most Consistent Models (Question-to-Question)\n")
            if main_judge in results["question_volatility"]:
                consistent_models = sorted(results["question_volatility"][main_judge].items(), 
                                         key=lambda x: x[1]["coefficient_of_variation"])[:3]
                for i, (model, stats) in enumerate(consistent_models, 1):
                    f.write(f"{i}. **{model}**: CV = {stats['coefficient_of_variation']:.3f}\n")
            f.write("\n")
            
            # Data quality notes
            f.write("### Data Quality Notes\n")
            f.write(f"- **Total records processed**: {quality['total_records']:,}\n")
            f.write(f"- **Successfully parsed**: {quality['total_records'] - quality['json_parse_errors_count']:,} ({(quality['total_records'] - quality['json_parse_errors_count'])/quality['total_records']*100:.2f}%)\n")
            f.write(f"- **Complete evaluation sets**: {(quality['total_records'] - quality['incomplete_evaluation_sets_count'])//5:,}\n")
            f.write(f"- **Judges with complete data**: {sum(1 for judge, stats in judge_stats.items() if stats['total_evals'] > 5000)}/{len(judge_stats)}\n")
        
        print(f"Comprehensive summary report saved to {output_file}")
    
    def save_summary_report_no_logic_clarity(self, results: Dict[str, Any], output_file: Path):
        """Save summary report excluding Logic and Clarity dimensions."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Individual Evaluation Analysis Summary (Excluding Logic and Clarity)\n\n")
            
            # Data Quality Summary
            quality = results["data_quality_report"]["summary"]
            f.write("## Data Quality Summary\n\n")
            f.write(f"- **Total records**: {quality['total_records']}\n")
            f.write(f"- **Array wrapped scores**: {quality['array_wrapped_scores']}\n")
            f.write(f"- **Invalid scores**: {quality['invalid_scores_count']}\n")
            f.write(f"- **Missing evaluations**: {quality['missing_evaluations_count']}\n")
            f.write(f"- **JSON parse errors**: {quality['json_parse_errors_count']}\n")
            f.write(f"- **Incomplete evaluation sets**: {quality['incomplete_evaluation_sets_count']}\n\n")
            f.write("*Note: This analysis excludes Logic and Clarity dimensions, assuming judge models did not provide these evaluations.*\n\n")
            
            # Judge Models Overview
            f.write("## Judge Models Overview (Excluding Logic/Clarity)\n\n")
            f.write("| Judge Model | Total Evaluations | Data Completeness |\n")
            f.write("|-------------|-------------------|-------------------|\n")
            
            judge_stats = {}
            for judge, judge_data in results["model_average_scores_no_lc"].items():
                total_evals = sum(stats["total_evaluations"] for stats in judge_data.values())
                model_count = len(judge_data)
                judge_stats[judge] = {"total_evals": total_evals, "models": model_count}
                
                # Expected calculation for 4 dimensions: correctness, completeness, theoretical_depth, rigor_and_information_density
                expected_total = 27 * 5 * model_count  # Still 270 per model (27 questions × 2 eval_types × 5 rounds)
                coverage_pct = (total_evals / expected_total * 100) if expected_total > 0 else 0
                completeness = "Complete" if coverage_pct > 90 else "Partial" if coverage_pct > 50 else "Limited"
                
                f.write(f"| {judge} | {total_evals} | {completeness} ({coverage_pct:.1f}%) |\n")
                
            f.write("\n")
            
            # Model Rankings with detailed dimension scores (4 dimensions only)
            f.write("## Model Average Scores by Judge (Excluding Logic/Clarity)\n\n")
            for judge, judge_data in results["model_average_scores_no_lc"].items():
                f.write(f"### Judge: {judge}\n\n")
                total_evals = judge_stats[judge]["total_evals"]
                f.write(f"*Total evaluations: {total_evals}*\n\n")
                
                # Overall ranking table
                f.write("#### Overall Ranking\n\n")
                f.write("| Rank | Model | Overall Score | Std Dev | Evaluations | Coverage |\n")
                f.write("|------|-------|---------------|---------|-------------|----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["overall_average"], reverse=True)
                expected_evals = 270  # Still 270 as we just exclude 2 out of 6 dimensions from the calculation
                
                for i, (model, stats) in enumerate(sorted_models, 1):
                    coverage = f"{stats['total_evaluations']}/{expected_evals} ({stats['total_evaluations']/expected_evals*100:.1f}%)"
                    f.write(f"| {i} | {model} | {stats['overall_average']:.2f} | {stats['overall_std']:.2f} | {stats['total_evaluations']} | {coverage} |\n")
                
                f.write("\n")
                
                # Dimension scores table (4 dimensions only)
                f.write("#### Dimension-wise Scores\n\n")
                dimensions = ["correctness", "completeness", "theoretical_depth", "rigor_and_information_density"]
                
                # Table header
                f.write("| Model |")
                for dim in dimensions:
                    f.write(f" {dim.replace('_', ' ').title()} |")
                f.write("\n")
                
                # Table separator
                f.write("|-------|")
                for dim in dimensions:
                    f.write("-------:|")
                f.write("\n")
                
                # Table data
                for model, stats in sorted_models:
                    f.write(f"| {model} |")
                    dim_scores = stats.get("dimension_averages", {})
                    for dim in dimensions:
                        score = dim_scores.get(dim, 0)
                        f.write(f" {score:.2f} |")
                    f.write("\n")
                
                f.write("\n")
            
            # Best Answer Rounds (No Logic/Clarity)
            f.write("## Best Answer Rounds Analysis (Excluding Logic/Clarity)\n\n")
            f.write("*This shows which answer round performed best for each model using only 4 dimensions.*\n\n")
            
            for judge, judge_data in results["best_answer_rounds_no_lc"].items():
                f.write(f"### Judge: {judge}\n\n")
                f.write("| Model | Best Round | Best Score | Best Std | Score Range | Improvement | Questions |\n")
                f.write("|-------|------------|------------|----------|-------------|-------------|----------|\n")
                
                for model, stats in judge_data.items():
                    all_scores = list(stats["all_round_scores"].values())
                    if len(all_scores) > 1:
                        min_score = min(all_scores)
                        max_score = max(all_scores)
                        improvement = f"{((max_score - min_score) / min_score * 100):.1f}%" if min_score > 0 else "N/A"
                        score_range = f"{min_score:.2f} - {max_score:.2f}"
                    else:
                        improvement = "N/A"
                        score_range = f"{stats['best_score']:.2f}"
                    
                    best_std = stats.get('best_std', 0)
                    question_count = stats.get('all_round_stats', {}).get(stats['best_round'], {}).get('count', 'N/A')
                    
                    f.write(f"| {model} | {stats['best_round']} | {stats['best_score']:.2f} | {best_std:.2f} | {score_range} | {improvement} | {question_count} |\n")
                
                f.write("\n")
            
            # Detailed Round Statistics for MOSES and ChemSpark Series
            f.write("## Detailed Round Statistics (MOSES and ChemSpark Series)\n\n")
            f.write("*Comprehensive round-by-round performance analysis for MOSES and ChemSpark model families using 4 dimensions.*\n\n")
            
            target_models = ["MOSES", "MOSES-nano", "spark-chem13b-think", "spark-chem13b-nothink"]
            
            for judge, judge_data in results["best_answer_rounds_no_lc"].items():
                f.write(f"### Judge: {judge}\n\n")
                
                for model in target_models:
                    if model in judge_data:
                        stats = judge_data[model]
                        f.write(f"#### {model}\n\n")
                        
                        # Round-by-round performance table
                        f.write("| Round | Average Score | Std Dev | Questions | Performance vs Best |\n")
                        f.write("|-------|---------------|---------|-----------|---------------------|\n")
                        
                        best_score = stats['best_score']
                        all_round_scores = stats.get('all_round_scores', {})
                        all_round_stats = stats.get('all_round_stats', {})
                        
                        # Sort rounds by number
                        sorted_rounds = sorted(all_round_scores.keys(), key=lambda x: int(x))
                        
                        for round_num in sorted_rounds:
                            round_score = all_round_scores[round_num]
                            round_stat = all_round_stats.get(round_num, {})
                            round_std = round_stat.get('std', 0)
                            round_count = round_stat.get('count', 'N/A')
                            
                            # Calculate performance relative to best
                            if best_score > 0:
                                performance_pct = ((round_score - best_score) / best_score * 100)
                                if performance_pct >= 0:
                                    performance_str = f"+{performance_pct:.1f}%"
                                else:
                                    performance_str = f"{performance_pct:.1f}%"
                            else:
                                performance_str = "N/A"
                            
                            # Mark best round
                            if round_num == stats['best_round']:
                                performance_str += " ⭐"
                            
                            f.write(f"| {round_num} | {round_score:.2f} | {round_std:.2f} | {round_count} | {performance_str} |\n")
                        
                        f.write("\n")
                
                f.write("\n")
            
            # Model Stability Analysis (No Logic/Clarity)
            f.write("## Model Stability Analysis (Excluding Logic/Clarity)\n\n")
            
            # Answer Round Volatility
            f.write("### Answer Round Volatility\n\n")
            f.write("*Measures consistency across different answer rounds using 4 dimensions. Lower CV = more stable.*\n\n")
            
            for judge, judge_data in results["model_stability_no_lc"]["answer_round_volatility"].items():
                f.write(f"#### Judge: {judge}\n\n")
                f.write("| Rank | Model | Mean Score | Std Dev | CV | Stability |\n")
                f.write("|------|-------|------------|---------|----|-----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["coefficient_of_variation"])
                for i, (model, stats) in enumerate(sorted_models, 1):
                    cv = stats["coefficient_of_variation"]
                    stability = "Excellent" if cv < 0.1 else "Good" if cv < 0.2 else "Fair" if cv < 0.3 else "Poor"
                    f.write(f"| {i} | {model} | {stats['mean']:.2f} | {stats['std']:.2f} | {cv:.3f} | {stability} |\n")
                
                f.write("\n")
            
            # Question Volatility  
            f.write("### Question-to-Question Volatility\n\n")
            f.write("*Measures consistency across different questions using 4 dimensions. Lower CV = more consistent.*\n\n")
            
            for judge, judge_data in results["model_stability_no_lc"]["question_volatility"].items():
                f.write(f"#### Judge: {judge}\n\n")
                f.write("| Rank | Model | Mean Score | Std Dev | CV | Consistency |\n")
                f.write("|------|-------|------------|---------|----|-----------|\n")
                
                sorted_models = sorted(judge_data.items(), key=lambda x: x[1]["coefficient_of_variation"])
                for i, (model, stats) in enumerate(sorted_models, 1):
                    cv = stats["coefficient_of_variation"]
                    consistency = "Excellent" if cv < 0.2 else "Good" if cv < 0.3 else "Fair" if cv < 0.4 else "Poor"
                    f.write(f"| {i} | {model} | {stats['mean']:.2f} | {stats['std']:.2f} | {cv:.3f} | {consistency} |\n")
                
                f.write("\n")
            
            # Key Insights Summary
            f.write("## Key Insights Summary (Excluding Logic/Clarity)\n\n")
            
            # Top performers
            f.write("### Top Performing Models\n")
            main_judge = list(results["model_average_scores_no_lc"].keys())[0]
            top_models = sorted(results["model_average_scores_no_lc"][main_judge].items(), 
                              key=lambda x: x[1]["overall_average"], reverse=True)[:3]
            
            for i, (model, stats) in enumerate(top_models, 1):
                f.write(f"{i}. **{model}**: {stats['overall_average']:.2f} ± {stats['overall_std']:.2f}\n")
            f.write("\n")
            
            # Most stable models
            f.write("### Most Stable Models (Answer Round Volatility)\n")
            if main_judge in results["model_stability_no_lc"]["answer_round_volatility"]:
                stable_models = sorted(results["model_stability_no_lc"]["answer_round_volatility"][main_judge].items(), 
                                     key=lambda x: x[1]["coefficient_of_variation"])[:3]
                for i, (model, stats) in enumerate(stable_models, 1):
                    f.write(f"{i}. **{model}**: CV = {stats['coefficient_of_variation']:.3f}\n")
            f.write("\n")
            
            # Most consistent models  
            f.write("### Most Consistent Models (Question-to-Question)\n")
            if main_judge in results["model_stability_no_lc"]["question_volatility"]:
                consistent_models = sorted(results["model_stability_no_lc"]["question_volatility"][main_judge].items(), 
                                         key=lambda x: x[1]["coefficient_of_variation"])[:3]
                for i, (model, stats) in enumerate(consistent_models, 1):
                    f.write(f"{i}. **{model}**: CV = {stats['coefficient_of_variation']:.3f}\n")
            f.write("\n")
            
            # Data quality notes
            f.write("### Data Quality Notes\n")
            f.write(f"- **Analysis scope**: Correctness, Completeness, Theoretical Depth, Rigor and Information Density only\n")
            f.write(f"- **Excluded dimensions**: Logic and Clarity (assumed not provided by judge models)\n")
            f.write(f"- **Total records processed**: {quality['total_records']:,}\n")
            f.write(f"- **Successfully parsed**: {quality['total_records'] - quality['json_parse_errors_count']:,} ({(quality['total_records'] - quality['json_parse_errors_count'])/quality['total_records']*100:.2f}%)\n")
        
        print(f"Summary report (no Logic/Clarity) saved to {output_file}")

def main():
    """Main function to run the analysis."""
    print("Individual Evaluation Data Analysis")
    print("=" * 40)
    
    # Create analyzer
    analyzer = IndividualEvaluationAnalyzer()
    
    # Run analysis
    results = analyzer.run_full_analysis()
    
    # Save results
    analyzer.save_results(results)
    
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()