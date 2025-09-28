#!/usr/bin/env python3
"""
Script 2: Comparative pairwise evaluation for AI model answers
Generates prompts for LLM judge to compare pairs of answers from different models
using pairwise comparison for ELO rating calculation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re
import itertools

class ComparativeEvaluationGenerator:
    """Generates comparative evaluation prompts for AI model answers."""
    
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
    
    def _organize_answers_by_question(self, model_answers: Dict[str, Dict[str, List[Dict]]]) -> Dict[str, List[Dict]]:
        """Organize all answers by question for pairwise comparison."""
        questions_data = {}
        
        for model_name, rounds_data in model_answers.items():
            for answer_round, qa_pairs in rounds_data.items():
                for qa_pair in qa_pairs:
                    query_id = qa_pair.get('query_id', '')
                    question = qa_pair.get('query', '')
                    answer = qa_pair.get('response', '')
                    
                    if not query_id or not question or not answer:
                        continue
                    
                    if query_id not in questions_data:
                        questions_data[query_id] = {
                            'question': question,
                            'answers': []
                        }
                    
                    # Add answer with metadata
                    questions_data[query_id]['answers'].append({
                        'answer': answer,
                        'model_name': model_name,
                        'answer_round': answer_round,
                        'answer_id': f"{model_name}_round{answer_round}"
                    })
        
        return questions_data
    
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
    
    def _create_comparative_prompt_with_reference(self, question: str, answer_a: str, answer_b: str, 
                                                model_a: str, model_b: str, reference_answer: str) -> str:
        """Create comparative evaluation prompt with reference answer for correctness and completeness."""
        
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
            "Please compare two AI assistant responses to the same question and determine which one is better overall from the perspective of a supramolecular chemistry expert.",
            "",
            "**IMPORTANT NOTE:** Ignore any reference citations, bibliography markers, or source indicators in the answers. Treat them as if they do not exist when evaluating the content.",
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
        
        # Add the question and answers to compare
        prompt_parts.extend([
            "[QUESTION START]",
            question,
            "[QUESTION END]",
            "",
            "[ANSWER A START]",
            answer_a,
            "[ANSWER A END]",
            "",
            "[ANSWER B START]",
            answer_b,
            "[ANSWER B END]",
            "",
            "[OUTPUT FORMAT START]",
            "Compare the two answers based on the evaluation criteria and choose which one is better overall.",
            "Please provide your evaluation in the following JSON format:",
            "",
            "```json",
            "{",
            '  "winner": "A" or "B",',
            '  "reasoning": "Brief explanation of why the chosen answer is better"',
            "}",
            "```",
            "[OUTPUT FORMAT END]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_comparative_prompt_without_reference(self, question: str, answer_a: str, answer_b: str, 
                                                   model_a: str, model_b: str) -> str:
        """Create comparative evaluation prompt without reference answer for logic, clarity, theoretical_depth, rigor."""
        
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
            "Please compare two AI assistant responses to the same question and determine which one is better overall from the perspective of a supramolecular chemistry expert.",
            "",
            "**IMPORTANT NOTE:** Ignore any reference citations, bibliography markers, or source indicators in the answers. Treat them as if they do not exist when evaluating the content.",
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
        
        # Add the question and answers to compare
        prompt_parts.extend([
            "[QUESTION START]",
            question,
            "[QUESTION END]",
            "",
            "[ANSWER A START]",
            answer_a,
            "[ANSWER A END]",
            "",
            "[ANSWER B START]",
            answer_b,
            "[ANSWER B END]",
            "",
            "[OUTPUT FORMAT START]",
            "Compare the two answers based on the evaluation criteria and choose which one is better overall.",
            "Please provide your evaluation in the following JSON format:",
            "",
            "```json",
            "{",
            '  "winner": "A" or "B",',
            '  "reasoning": "Brief explanation of why the chosen answer is better"',
            "}",
            "```",
            "[OUTPUT FORMAT END]"
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_comparative_prompts(self, answers_folder: str = "original_answers", test_mode: bool = False) -> bool:
        """Generate comparative evaluation prompts for all model answers."""
        
        print(f"Loading model answers from: {answers_folder}")
        model_answers = self._load_model_answers(answers_folder)
        
        if not model_answers:
            print("No model answers found!")
            return False
        
        print(f"Found {len(model_answers)} models")
        
        # Organize answers by question
        print("Organizing answers by question...")
        questions_data = self._organize_answers_by_question(model_answers)
        
        print(f"Found {len(questions_data)} questions")
        
        # Calculate expected comparison count
        total_expected_comparisons = 0
        for query_id, question_data in questions_data.items():
            n_answers = len(question_data['answers'])
            if n_answers >= 2:
                comparisons_for_question = n_answers * (n_answers - 1) // 2
                total_expected_comparisons += comparisons_for_question
        
        print(f"Expected total comparisons: {total_expected_comparisons:,}")
        print(f"Expected 5x prompts: {total_expected_comparisons * 2 * 5:,}")
        print(f"Expected 1x prompts: {total_expected_comparisons * 2:,}")
        
        if test_mode:
            print("RUNNING IN TEST MODE - Processing only first 3 questions")
            questions_to_process = list(questions_data.keys())[:3]
        else:
            questions_to_process = list(questions_data.keys())
        
        # Generate prompts for both versions
        prompts_5x = []  # 5 evaluations per comparison
        prompts_1x = []  # 1 evaluation per comparison
        
        total_comparisons = 0
        
        for idx, query_id in enumerate(questions_to_process):
            question_data = questions_data[query_id]
            question = question_data['question']
            answers = question_data['answers']
            
            print(f"Processing {query_id} ({idx+1}/{len(questions_to_process)}): {len(answers)} answers")
            
            if len(answers) < 2:
                print(f"  Skipping {query_id}: not enough answers")
                continue
            
            # Calculate comparisons for this question
            question_comparisons = len(answers) * (len(answers) - 1) // 2
            print(f"  Will generate {question_comparisons} comparisons")
            
            # Find reference answer
            reference_answer = self._find_reference_answer(question, query_id)
            
            comparison_count = 0
            # Generate all pairwise comparisons
            for i, answer_a_data in enumerate(answers):
                for j, answer_b_data in enumerate(answers):
                    if i >= j:  # Skip same pair and reverse pairs
                        continue
                    
                    comparison_count += 1
                    if comparison_count % 100 == 0:
                        print(f"    Progress: {comparison_count}/{question_comparisons} comparisons")
                    
                    answer_a = answer_a_data['answer']
                    answer_b = answer_b_data['answer']
                    model_a = answer_a_data['answer_id']
                    model_b = answer_b_data['answer_id']
                    
                    total_comparisons += 1
                    
                    # Generate prompts for dimensions requiring reference answer (correctness, completeness)
                    if reference_answer:
                        # 5x version
                        for eval_round in range(1, 6):
                            prompt_text = self._create_comparative_prompt_with_reference(
                                question, answer_a, answer_b, model_a, model_b, reference_answer
                            )
                            
                            prompts_5x.append({
                                "query": prompt_text,
                                "question_id": query_id,
                                "answer_a_model": answer_a_data['model_name'],
                                "answer_a_round": answer_a_data['answer_round'],
                                "answer_a_id": model_a,
                                "answer_b_model": answer_b_data['model_name'],
                                "answer_b_round": answer_b_data['answer_round'],
                                "answer_b_id": model_b,
                                "evaluation_round": eval_round,
                                "evaluation_type": "with_reference",
                                "dimensions": ["correctness", "completeness"]
                            })
                        
                        # 1x version
                        prompt_text = self._create_comparative_prompt_with_reference(
                            question, answer_a, answer_b, model_a, model_b, reference_answer
                        )
                        
                        prompts_1x.append({
                            "query": prompt_text,
                            "question_id": query_id,
                            "answer_a_model": answer_a_data['model_name'],
                            "answer_a_round": answer_a_data['answer_round'],
                            "answer_a_id": model_a,
                            "answer_b_model": answer_b_data['model_name'],
                            "answer_b_round": answer_b_data['answer_round'],
                            "answer_b_id": model_b,
                            "evaluation_round": 1,
                            "evaluation_type": "with_reference",
                            "dimensions": ["correctness", "completeness"]
                        })
                    
                    # Generate prompts for dimensions not requiring reference answer
                    # 5x version
                    for eval_round in range(1, 6):
                        prompt_text = self._create_comparative_prompt_without_reference(
                            question, answer_a, answer_b, model_a, model_b
                        )
                        
                        prompts_5x.append({
                            "query": prompt_text,
                            "question_id": query_id,
                            "answer_a_model": answer_a_data['model_name'],
                            "answer_a_round": answer_a_data['answer_round'],
                            "answer_a_id": model_a,
                            "answer_b_model": answer_b_data['model_name'],
                            "answer_b_round": answer_b_data['answer_round'],
                            "answer_b_id": model_b,
                            "evaluation_round": eval_round,
                            "evaluation_type": "without_reference",
                            "dimensions": ["logic", "clarity", "theoretical_depth", "rigor_and_information_density"]
                        })
                    
                    # 1x version
                    prompt_text = self._create_comparative_prompt_without_reference(
                        question, answer_a, answer_b, model_a, model_b
                    )
                    
                    prompts_1x.append({
                        "query": prompt_text,
                        "question_id": query_id,
                        "answer_a_model": answer_a_data['model_name'],
                        "answer_a_round": answer_a_data['answer_round'],
                        "answer_a_id": model_a,
                        "answer_b_model": answer_b_data['model_name'],
                        "answer_b_round": answer_b_data['answer_round'],
                        "answer_b_id": model_b,
                        "evaluation_round": 1,
                        "evaluation_type": "without_reference",
                        "dimensions": ["logic", "clarity", "theoretical_depth", "rigor_and_information_density"]
                    })
        
        print(f"Generated {total_comparisons} pairwise comparisons")
        
        # Save 5x version
        output_path_5x = self.data_folder / "comparative_evaluation_prompts_5x.json"
        with open(output_path_5x, 'w', encoding='utf-8') as f:
            json.dump(prompts_5x, f, indent=2, ensure_ascii=False)
        
        # Save 1x version
        output_path_1x = self.data_folder / "comparative_evaluation_prompts_1x.json"
        with open(output_path_1x, 'w', encoding='utf-8') as f:
            json.dump(prompts_1x, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {len(prompts_5x)} prompts (5x version) -> {output_path_5x}")
        print(f"Generated {len(prompts_1x)} prompts (1x version) -> {output_path_1x}")
        
        return True

def main():
    """Main function to generate comparative evaluation prompts."""
    import sys
    
    print("=== Comparative Pairwise Evaluation Prompt Generator ===")
    
    # Check command line arguments
    test_mode = True  # Default to test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        test_mode = False
        print("Running in FULL mode (all 27 questions)")
    else:
        print("Running in TEST mode (first 3 questions only)")
        print("Use --full argument for full processing")
    
    print(f"\nWARNING: Full processing would generate 650,000+ prompts (5x) and 130,000+ prompts (1x)")
    print("This may take a very long time and create very large files.")
    
    # Create generator
    generator = ComparativeEvaluationGenerator()
    
    # Generate prompts
    success = generator.generate_comparative_prompts(answers_folder="original_answers", test_mode=test_mode)
    
    if success:
        print("\nSUCCESS: Generated comparative evaluation prompts")
        print("Files created:")
        if test_mode:
            print("1. comparative_evaluation_prompts_5x.json - Test version (first 3 questions)")
            print("2. comparative_evaluation_prompts_1x.json - Test version (first 3 questions)")
        else:
            print("1. comparative_evaluation_prompts_5x.json - Each comparison evaluated 5 times")
            print("2. comparative_evaluation_prompts_1x.json - Each comparison evaluated 1 time")
        print("\nNext steps:")
        print("- Use these prompts for pairwise comparison evaluation")
        print("- Calculate ELO ratings from the comparison results")
        print("- The 5x version provides more robust statistical analysis")
    else:
        print("\nFAILED: Could not generate comparative evaluation prompts")

if __name__ == "__main__":
    main()