from __future__ import annotations

# Canonical model names requested by user
CANONICAL_MODELS = [
    "MOSES",
    "o3",
    "GPT-4.1",
    "LightRAG-nano",
    "LightRAG",
    "MOSES-nano",
    "GPT-4.1-nano",
    "GPT-4o",
    "GPT-4o-mini",
]

# Map canonical -> identifiers in human CSV header (model name sentinel cells)
HUMAN_CSV_MODEL_HEADER = {
    "GPT-4.1": "gpt-4.1-final",
    "GPT-4.1-nano": "gpt-4.1-nano-final-815-1",
    "LightRAG": "lightrag-gpt-4_1",
    "LightRAG-nano": "lightrag-gpt-4_1-nano",
    "o3": "o3-final",
    "MOSES": "reordered_MOSES-final",
    "MOSES-nano": "reordered_MOSES-nano-final",
    "GPT-4o": "gpt-4o-final-815-1",
    "GPT-4o-mini": "gpt-4o-mini-final-815-1",
}

# Map canonical -> identifiers in LLM individual JSONL `model_name`
LLM_MODEL_NAME = {
    "GPT-4.1": "gpt-4.1",
    "GPT-4.1-nano": "gpt-4.1-nano",
    # Updated per user-provided names in JSON
    "LightRAG": "lightrag-4.1",
    "LightRAG-nano": "lightrag-4.1-nano",
    "o3": "o3",
    # Updated MOSES names per JSON
    "MOSES": "MOSES",
    "MOSES-nano": "MOSES-nano",
    "GPT-4o": "gpt-4o",
    "GPT-4o-mini": "gpt-4o-mini",
}

# Dimension mappings
# Chinese header -> internal key
ZH_DIM_TO_KEY = {
    "正确性": "correctness",
    "逻辑性": "logic",
    "清晰度": "clarity",
    "完备性": "completeness",
    "理论深度": "theoretical_depth",
    "论述严谨性与信息密度": "rigor_and_information_density",
}

# Internal dimension keys the analysis focuses on (exclude clarity/logic)
TARGET_DIM_KEYS = [
    "correctness",
    "completeness",
    "theoretical_depth",
    "rigor_and_information_density",
]

# Paths (relative to repository root)
HUMAN_CSV_PATH = (
    "test_results/eva_res/human/副本主客体27题论文评测1-27题分数结果（汇总）-0829.csv"
)
LLM_JSONL_PATH = (
    "test_results/eva_res/individual/安全前瞻-化学_82_doubao-seed-1.6_安全与前瞻_1755917139543_individual_evaluation_prompts_5x_18900_v1.json"
)

# Output directory for part 0–1 artifacts (under this folder)
OUT_DIR = "test_results/eva_res/consistency_analysis/out"
