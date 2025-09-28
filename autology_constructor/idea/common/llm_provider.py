import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
# from langchain_anthropic import ChatAnthropic


try:
    from config.settings import LLM_CONFIG, OPENAI_API_KEY
except ImportError as e:
    print(f"Error: Could not import configuration from config.settings: {e}. ")


def get_default_llm():
    """Instantiates and returns the default LLM based on configuration."""
    model_name = LLM_CONFIG.get('model', 'gpt-4.1-mini')
    temperature = LLM_CONFIG.get('temperature', 0)
    openai_api_key_to_use = OPENAI_API_KEY if OPENAI_API_KEY and OPENAI_API_KEY != "default_api_key" else None

    if model_name:
        if not openai_api_key_to_use:
            # Check env var as a last resort if needed, or raise error
            openai_api_key_to_use = os.getenv("OPENAI_API_KEY")
            if not openai_api_key_to_use:
                 raise ValueError("OpenAI API Key is not configured in  environment variables.")
        llm_params = {k: v for k, v in LLM_CONFIG.items() if k not in ['model', 'temperature']}
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key_to_use,
            **llm_params
        )
    else:
        raise ValueError(f"Only support OpenAI models, model name specified in LLM_CONFIG: {model_name}")

def get_qwen_llm():
    # return ChatOllama(
    #         model="myaniu/qwen2.5-1m:14b",
    #         base_url="https://30a6-36-5-153-246.ngrok-free.app",
    #         temperature=0,
    #         max_tokens=8192,
    #     )
    return ChatTongyi(
            model_name="qwen3-14b",
            model_kwargs={
                "temperature": 0,
                "enable_thinking": False,
                "max_tokens": 8192,
            }
        )
# Cached instance logic
DEFAULT_LLM_INSTANCE = None
def get_cached_default_llm(qwen=False):
    """Returns a cached instance of the default LLM."""
    global DEFAULT_LLM_INSTANCE
    if DEFAULT_LLM_INSTANCE is None:
        if qwen:
            DEFAULT_LLM_INSTANCE = get_qwen_llm()
        else:
            DEFAULT_LLM_INSTANCE = get_default_llm()
    return DEFAULT_LLM_INSTANCE 