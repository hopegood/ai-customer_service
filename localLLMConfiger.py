from langchain_community.chat_models import ChatOllama
from langchain_deepseek import ChatDeepSeek
# 初始化本地模型
'''
local_chat_model = ChatOllama(
    model="deepseek-v2",
    base_url="http://192.168.3.35:11434"  # Ollama 默认地址
)# deepseek-v2 deepseek-llm:7b
'''
office_chat_model = ChatDeepSeek(model="deepseek-chat", api_key="DEEPSEEK_API_KEY", temperature=0,max_tokens=2000)


