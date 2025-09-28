#!/usr/bin/env python3
"""
Script 1: Individual 6-dimensional evaluation for AI model answers
Generates prompts for LLM judge to evaluate each model's answers individually
using 6 evaluation dimensions (correctness, logic, clarity, completeness, theoretical depth, format rigor)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re

class IndividualEvaluationGenerator:
    """Generates individual evaluation prompts for AI model answers."""
    
    def __init__(self, data_folder: str = "."):
        self.data_folder = Path(data_folder)
        self.evaluation_criteria = self._load_evaluation_criteria()
        self.reference_answers = self._load_reference_answers()
        
    def _load_evaluation_criteria(self) -> Dict[str, Any]:
        """Load evaluation criteria from JSON file."""
        criteria_path = self.data_folder / "evaluation_criteria_english.json"
        with open(criteria_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_reference_answers(self) -> Dict[str, Any]:
        """Load reference answers from JSON file."""
        answers_path = self.data_folder / "questions_answers_27.json"
        with open(answers_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_model_answers(self, answers_folder: str) -> Dict[str, Dict[str, List[Dict]]]:
        """Load all model answers from the specified folder structure."""
        answers_path = Path(answers_folder)
        model_answers = {}
        
        if not answers_path.exists():
            print(f"Warning: Answer folder {answers_folder} not found")
            return model_answers
        
        # Look for model folders
        for model_folder in answers_path.iterdir():
            if not model_folder.is_dir():
                continue
                
            model_name = model_folder.name
            model_answers[model_name] = {}
            
            json_files = list(model_folder.glob("*.json"))
            
            if len(json_files) == 1:
                # New format: single JSONL file with infer_wave field
                json_file = json_files[0]
                print(f"  Processing single file format: {json_file.name}")
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Parse each line as JSON
                    questions_by_round = {}
                    question_counter = {}
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            data = json.loads(line)
                            question = data.get('query', '')
                            answer = data.get('predict', '')
                            infer_wave = str(data.get('infer_wave', '1'))
                            
                            if not question or not answer:
                                continue
                            
                            # Generate question ID based on order within each round
                            if infer_wave not in question_counter:
                                question_counter[infer_wave] = 1
                            else:
                                question_counter[infer_wave] += 1
                            
                            query_id = f"q_{question_counter[infer_wave]}"
                            
                            if infer_wave not in questions_by_round:
                                questions_by_round[infer_wave] = []
                            
                            questions_by_round[infer_wave].append({
                                'query': question,
                                'response': answer,
                                'query_id': query_id
                            })
                            
                        except json.JSONDecodeError as e:
                            print(f"    Error parsing line in {json_file.name}: {e}")
                            continue
                    
                    # Store organized data
                    model_answers[model_name] = questions_by_round
                    
                    # Check question counts for each round
                    for round_num, qa_pairs in questions_by_round.items():
                        if len(qa_pairs) != 27:
                            print(f"  WARNING: File '{json_file.name}' (model '{model_name}', round {round_num}) has {len(qa_pairs)} Q&A pairs, expected 27")
                        else:
                            print(f"  OK: File '{json_file.name}' (model '{model_name}', round {round_num}) has complete 27 Q&A pairs")
                    
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
                    
            else:
                # Original format: multiple files, one per round
                print(f"  Processing multiple file format: {len(json_files)} files")
                
                for json_file in json_files:
                    try:
                        # Extract answer round from filename (last character or run number)
                        filename = json_file.stem
                        
                        # Try different patterns for round extraction
                        answer_round = None
                        if filename[-1].isdigit():
                            # Pattern: filename ends with digit
                            answer_round = filename[-1]
                        elif 'run' in filename.lower():
                            # Pattern: filename contains 'run' followed by number
                            import re
                            match = re.search(r'run(\d+)', filename.lower())
                            if match:
                                answer_round = match.group(1)
                        
                        if answer_round is None:
                            answer_round = "1"  # Default
                        
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Handle different JSON structures
                        standardized_pairs = []
                        
                        if isinstance(data, dict):
                            # Case 1: {"model_name": [{"question": ..., "answer": ...}]}
                            for key, qa_pairs in data.items():
                                if isinstance(qa_pairs, list):
                                    for i, qa in enumerate(qa_pairs):
                                        if isinstance(qa, dict):
                                            standardized_pairs.append({
                                                'query': qa.get('question', qa.get('query', '')),
                                                'response': qa.get('answer', qa.get('response', '')),
                                                'query_id': f"q_{i + 1}"
                                            })
                                            
                        elif isinstance(data, list):
                            # Case 2: [{"query": ..., "response": ...}] or [{"question": ..., "answer": ...}]
                            for i, qa in enumerate(data):
                                if isinstance(qa, dict):
                                    standardized_pairs.append({
                                        'query': qa.get('question', qa.get('query', '')),
                                        'response': qa.get('answer', qa.get('response', '')),
                                        'query_id': f"q_{i + 1}"
                                    })
                        
                        model_answers[model_name][answer_round] = standardized_pairs
                        
                        # Check if we have expected 27 Q&A pairs
                        if len(standardized_pairs) != 27:
                            print(f"  WARNING: File '{json_file.name}' (model '{model_name}', round {answer_round}) has {len(standardized_pairs)} Q&A pairs, expected 27")
                        else:
                            print(f"  OK: File '{json_file.name}' (model '{model_name}', round {answer_round}) has complete 27 Q&A pairs")
                            
                    except Exception as e:
                        print(f"Error loading {json_file}: {e}")
        
        return model_answers
    
    def _create_evaluation_prompt_with_reference(self, question: str, answer: str, reference_answer: str) -> str:
        """Create evaluation prompt for dimensions requiring reference answer (correctness, completeness)."""
        
        criteria = self.evaluation_criteria["evaluation_criteria"]
        instructions = self.evaluation_criteria["instructions"]
        
        # Only include correctness and completeness
        relevant_criteria = {
            "correctness": criteria["correctness"],
            "completeness": criteria["completeness"]
        }
        
        prompt_parts = [
            instructions["role"],
            "",
            "Please evaluate the following AI assistant's response from the perspective of a supramolecular chemistry expert using the specified criteria:",
            "",
            "**IMPORTANT NOTE:** Ignore any reference citations, bibliography markers, or source indicators in the answer. Treat them as if they do not exist when evaluating the content.",
            "",
            "[EVALUATION CRITERIA START]",
            ""
        ]
        
        # Add criteria descriptions
        for criterion_key, criterion_data in relevant_criteria.items():
            prompt_parts.extend([
                f"### {criterion_data['name']} ({criterion_data['total_score']} points)",
                criterion_data["description"],
                "",
                "**Scoring Standards:**"
            ])
            
            for score_range, description in criterion_data["scoring_standards"].items():
                prompt_parts.append(f"- {score_range} points: {description}")
            
            prompt_parts.append("")
        
        prompt_parts.append("[EVALUATION CRITERIA END]")
        prompt_parts.append("")
        
        # Add reference answer
        prompt_parts.extend([
            "[REFERENCE ANSWER START]",
            reference_answer,
            "[REFERENCE ANSWER END]",
            "",
            "**Note:** Use the reference answer to help evaluate correctness and completeness.",
            ""
        ])
        
        # Add the question and answer to evaluate
        prompt_parts.extend([
            "[QUESTION START]",
            question,
            "[QUESTION END]",
            "",
            "[ANSWER TO EVALUATE START]",
            answer,
            "[ANSWER TO EVALUATE END]",
            "",
            "[OUTPUT FORMAT START]",
            "Please provide your evaluation in the following JSON format:",
            "",
            "```json",
            "{",
            '  "correctness": [score],',
            '  "completeness": [score]',
            "}",
            "```",
            "[OUTPUT FORMAT END]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_evaluation_prompt_without_reference(self, question: str, answer: str) -> str:
        """Create evaluation prompt for dimensions not requiring reference answer (logic, clarity, theoretical_depth, rigor)."""
        
        criteria = self.evaluation_criteria["evaluation_criteria"]
        instructions = self.evaluation_criteria["instructions"]
        
        # Only include logic, clarity, theoretical_depth, rigor_and_information_density
        relevant_criteria = {
            "logic": criteria["logic"],
            "clarity": criteria["clarity"],
            "theoretical_depth": criteria["theoretical_depth"],
            "rigor_and_information_density": criteria["rigor_and_information_density"]
        }
        
        prompt_parts = [
            instructions["role"],
            "",
            "Please evaluate the following AI assistant's response from the perspective of a supramolecular chemistry expert using the specified criteria:",
            "",
            "**IMPORTANT NOTE:** Ignore any reference citations, bibliography markers, or source indicators in the answer. Treat them as if they do not exist when evaluating the content.",
            "",
            "[EVALUATION CRITERIA START]",
            ""
        ]
        
        # Add criteria descriptions
        for criterion_key, criterion_data in relevant_criteria.items():
            prompt_parts.extend([
                f"### {criterion_data['name']} ({criterion_data['total_score']} points)",
                criterion_data["description"],
                "",
                "**Scoring Standards:**"
            ])
            
            for score_range, description in criterion_data["scoring_standards"].items():
                prompt_parts.append(f"- {score_range} points: {description}")
            
            prompt_parts.append("")
        
        prompt_parts.append("[EVALUATION CRITERIA END]")
        prompt_parts.append("")
        
        # Add the question and answer to evaluate
        prompt_parts.extend([
            "[QUESTION START]",
            question,
            "[QUESTION END]",
            "",
            "[ANSWER TO EVALUATE START]",
            answer,
            "[ANSWER TO EVALUATE END]",
            "",
            "[OUTPUT FORMAT START]",
            "Please provide your evaluation in the following JSON format:",
            "",
            "```json",
            "{",
            '  "logic": [score],',
            '  "clarity": [score],',
            '  "theoretical_depth": [score],',
            '  "rigor_and_information_density": [score]',
            "}",
            "```",
            "[OUTPUT FORMAT END]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _find_reference_answer(self, question: str, query_id: str = None) -> str:
        """Find matching reference answer for a given question."""
        if not self.reference_answers or not isinstance(self.reference_answers, list):
            return None
        
        # Try to find by query_id first (if it's a number)
        if query_id:
            try:
                question_num = int(re.search(r'\d+', query_id).group())
                for ref_qa in self.reference_answers:
                    if ref_qa.get("question_number") == question_num:
                        return ref_qa.get("answer", "")
            except:
                pass
        
        # Try to find by question similarity
        question_lower = question.lower().strip()
        for ref_qa in self.reference_answers:
            ref_question_lower = ref_qa.get("question", "").lower().strip()
            
            # Exact match or very close match
            if question_lower == ref_question_lower:
                return ref_qa.get("answer", "")
            
            # Partial match - look for key words
            if len(question_lower.split()) > 2:
                key_words = [word for word in question_lower.split() if len(word) > 3]
                if key_words and any(word in ref_question_lower for word in key_words[:3]):
                    return ref_qa.get("answer", "")
        
        return None
    
    def generate_evaluation_prompts(self, answers_folder: str = "original_answers") -> bool:
        """Generate evaluation prompts for all model answers."""
        
        print(f"Loading model answers from: {answers_folder}")
        model_answers = self._load_model_answers(answers_folder)
        
        if not model_answers:
            print("No model answers found!")
            return False
        
        print(f"Found {len(model_answers)} models")
        
        # Generate prompts for both versions
        prompts_5x = []  # 5 evaluations per answer
        prompts_1x = []  # 1 evaluation per answer
        
        for model_name, rounds_data in model_answers.items():
            print(f"Processing model: {model_name} ({len(rounds_data)} rounds)")
            
            for answer_round, qa_pairs in rounds_data.items():
                print(f"  Processing round {answer_round}: {len(qa_pairs)} Q&A pairs")
                
                for qa_pair in qa_pairs:
                    question = qa_pair.get('query', '')
                    answer = qa_pair.get('response', '')
                    query_id = qa_pair.get('query_id', '')
                    
                    if not question or not answer:
                        continue
                    
                    # Find reference answer
                    reference_answer = self._find_reference_answer(question, query_id)
                    
                    # Generate prompts for dimensions requiring reference answer (correctness, completeness)
                    if reference_answer:
                        # 5x version
                        for eval_round in range(1, 6):
                            prompt_text = self._create_evaluation_prompt_with_reference(
                                question, answer, reference_answer
                            )
                            
                            prompts_5x.append({
                                "query": prompt_text,
                                "model_name": model_name,
                                "answer_round": answer_round,
                                "question_id": query_id,
                                "evaluation_round": eval_round,
                                "evaluation_type": "with_reference",
                                "dimensions": ["correctness", "completeness"]
                            })
                        
                        # 1x version
                        prompt_text = self._create_evaluation_prompt_with_reference(
                            question, answer, reference_answer
                        )
                        
                        prompts_1x.append({
                            "query": prompt_text,
                            "model_name": model_name,
                            "answer_round": answer_round,
                            "question_id": query_id,
                            "evaluation_round": 1,
                            "evaluation_type": "with_reference",
                            "dimensions": ["correctness", "completeness"]
                        })
                    
                    # Generate prompts for dimensions not requiring reference answer
                    # 5x version
                    for eval_round in range(1, 6):
                        prompt_text = self._create_evaluation_prompt_without_reference(
                            question, answer
                        )
                        
                        prompts_5x.append({
                            "query": prompt_text,
                            "model_name": model_name,
                            "answer_round": answer_round,
                            "question_id": query_id,
                            "evaluation_round": eval_round,
                            "evaluation_type": "without_reference",
                            "dimensions": ["logic", "clarity", "theoretical_depth", "rigor_and_information_density"]
                        })
                    
                    # 1x version
                    prompt_text = self._create_evaluation_prompt_without_reference(
                        question, answer
                    )
                    
                    prompts_1x.append({
                        "query": prompt_text,
                        "model_name": model_name,
                        "answer_round": answer_round,
                        "question_id": query_id,
                        "evaluation_round": 1,
                        "evaluation_type": "without_reference",
                        "dimensions": ["logic", "clarity", "theoretical_depth", "rigor_and_information_density"]
                    })
        
        # Save 5x version
        output_path_5x = self.data_folder / "individual_evaluation_prompts_5x.json"
        with open(output_path_5x, 'w', encoding='utf-8') as f:
            json.dump(prompts_5x, f, indent=2, ensure_ascii=False)
        
        # Save 1x version
        output_path_1x = self.data_folder / "individual_evaluation_prompts_1x.json"
        with open(output_path_1x, 'w', encoding='utf-8') as f:
            json.dump(prompts_1x, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {len(prompts_5x)} prompts (5x version) -> {output_path_5x}")
        print(f"Generated {len(prompts_1x)} prompts (1x version) -> {output_path_1x}")
        
        return True

def main():
    """Main function to generate individual evaluation prompts."""
    print("=== Individual 6-Dimensional Evaluation Prompt Generator ===")
    
    # Create generator
    generator = IndividualEvaluationGenerator()
    
    # Generate prompts
    success = generator.generate_evaluation_prompts(answers_folder="original_answers")
    
    if success:
        print("\nSUCCESS: Generated individual evaluation prompts")
        print("Files created:")
        print("1. individual_evaluation_prompts_5x.json - Each answer evaluated 5 times")
        print("2. individual_evaluation_prompts_1x.json - Each answer evaluated 1 time")
        print("\nNext steps:")
        print("- Use the 5x version for comprehensive evaluation with statistical analysis")
        print("- Use the 1x version for faster, single-pass evaluation")
    else:
        print("\nFAILED: Could not generate evaluation prompts")

if __name__ == "__main__":
    main()