import os
import asyncio
import json
from glob import glob
import numpy as np
import logging
from tqdm import tqdm
import math

# 假设您已通过 pypi 安装 lightrag
from lightrag import LightRAG
from lightrag.llm.openai import openai_embed, openai_complete_if_cache
from lightrag.kg.shared_storage import initialize_pipeline_status


# --------------------------------------------------------------------------- #
# ---                           CONFIGURATION                             --- #
# --------------------------------------------------------------------------- #

# 1. 文件和路径配置
WORKING_DIR_BASE = r"tests\unit_test\query\test\lightrag\temp_rag_storage"
CHUNKS_DIR = r"tests\unit_test\query\test\lightrag\test_chunks"

# 2. 模型配置
# MODELS_TO_RUN = ["gpt-4.1-nano", "gpt-4.1"]
MODELS_TO_RUN = [ "gpt-4.1"]

EMBEDDING_MODEL = "text-embedding-3-large"

# 3. LightRAG 配置
MAX_PARALLEL_INSERT = 10

# --------------------------------------------------------------------------- #

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        "gpt-4.1",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    """Embedding 函数，将文本转换为向量"""
    return await openai_embed(
        texts,
        model=EMBEDDING_MODEL,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

async def build_knowledge_base_for_model(model_name: str):
    """为单个模型构建并填充知识库"""
    log.info(f"--- 开始为模型: {model_name} 构建知识库 ---")

    model_working_dir = os.path.join(WORKING_DIR_BASE, model_name.replace(".", "_"))
    if not os.path.exists(model_working_dir):
        os.makedirs(model_working_dir)
        log.info(f"已创建独立目录: {model_working_dir}")

    # 为了构建知识库，llm_model_func 不是必需的，可以传入一个空函数
    rag = LightRAG(
        working_dir=model_working_dir,
        llm_model_func=llm_model_func,
        embedding_func=openai_embed,
        max_parallel_insert=MAX_PARALLEL_INSERT,
        # 在V0.1.2及更高版本中，llm_model_func是可选的
        # llm_model_func=lambda prompt, **kwargs: "" 
    )

    log.info(f"[{model_name}] 正在初始化存储...")
    await rag.initialize_storages()
    log.info(f"[{model_name}] 存储初始化完成。")
    await initialize_pipeline_status()

    log.info(f"[{model_name}] 正在从 '{CHUNKS_DIR}' 加载文档...")
    all_contents = []
    if os.path.exists(CHUNKS_DIR):
        for file_path in tqdm(glob(os.path.join(CHUNKS_DIR, "*.json"))):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in tqdm(data):
                    if "content" in item:
                        all_contents.append(item["content"])
        
        if all_contents:
            log.info(f"[{model_name}] 找到 {len(all_contents)} 个内容块待插入。正在分批执行 ainsert...")
            batch_size = MAX_PARALLEL_INSERT
            num_batches = math.ceil(len(all_contents) / batch_size)
            for i in tqdm(range(num_batches), desc=f"[{model_name}] 插入进度", unit="batch"):
                batch = all_contents[i * batch_size : (i + 1) * batch_size]
                await rag.ainsert(batch)
            log.info(f"[{model_name}] 文档插入成功，知识库构建完成。")
        else:
            log.warning(f"[{model_name}] 在 '{CHUNKS_DIR}' 中未找到任何内容。")
    else:
         log.error(f"[{model_name}] 目录 '{CHUNKS_DIR}' 不存在，无法构建知识库。")

async def main():
    """主函数，只为指定的单个模型构建知识库"""
    if not os.getenv("OPENAI_API_KEY"):
        log.error("致命错误: 环境变量 OPENAI_API_KEY 未设置。")
        return

    # 从命令行参数获取模型名
    import sys
    if len(sys.argv) < 2:
        log.error("请在命令行中指定模型名称，例如: python lighrag_kg.py gpt-4.1-nano")
        return
    model_name = sys.argv[1]

    await build_knowledge_base_for_model(model_name)
    
    log.info(f"\n✅ 模型 {model_name} 的知识库已构建完成。")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())