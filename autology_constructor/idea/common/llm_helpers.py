from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 全局LLM实例（可配置参数和复用实例）
llm_instance = ChatOpenAI(model="gpt-4o" ,temperature=0.7)

reasoning_llm_instance = ChatOpenAI(model="o3-mini")
    
