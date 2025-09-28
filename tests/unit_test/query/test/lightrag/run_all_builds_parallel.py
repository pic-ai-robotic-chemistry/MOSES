import asyncio
import sys
import logging
import locale # 导入 locale 模块来获取系统默认编码

# --- CONFIGURATION ---
MODELS_TO_BUILD = ["gpt-4.1-nano", "gpt-4.1"]
# ---------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

async def run_build_process(model_name: str):
    """启动一个独立的 Python 进程来运行构建脚本"""
    python_executable = sys.executable
    script_path = r"tests\unit_test\query\test\lightrag\lighrag_kg.py"
    
    log.info(f"即将为模型 '{model_name}' 启动一个后台构建进程...")
    
    process = await asyncio.create_subprocess_exec(
        python_executable,
        script_path,
        model_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    # 获取系统的首选编码，如果获取失败则默认为 utf-8
    # 这是解决 UnicodeDecodeError 的关键
    encoding = locale.getpreferredencoding(False) or 'utf-8'

    log.info(f"模型 '{model_name}' 的构建进程已结束，返回码: {process.returncode}")
    if stdout:
        # 使用获取到的系统编码进行解码，并替换无法解码的字符
        log.info(f"来自 '{model_name}' 进程的输出:\n--- STDOUT ---\n{stdout.decode(encoding, errors='replace').strip()}\n--------------")
    if stderr:
        # 使用获取到的系统编码进行解码，并替换无法解码的字符
        log.error(f"来自 '{model_name}' 进程的错误:\n--- STDERR ---\n{stderr.decode(encoding, errors='replace').strip()}\n--------------")
        
    return process.returncode == 0

async def main():
    """并行运行所有模型的知识库构建任务"""
    log.info("开始并行构建所有模型的知识库...")
    
    tasks = [run_build_process(model) for model in MODELS_TO_BUILD]
    
    results = await asyncio.gather(*tasks)
    
    log.info("\n" + "="*50)
    if all(results):
        log.info("✅ 任务总结: 所有模型的知识库构建任务均已成功启动并完成！")
        log.info("您现在可以运行 query_models.py 脚本了。")
    else:
        log.warning("⚠️ 任务总结: 部分或全部模型的知识库构建失败。请检查上方的错误日志。")
    log.info("="*50)

if __name__ == "__main__":
    # 在 Windows 上运行 asyncio 需要这一行
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())