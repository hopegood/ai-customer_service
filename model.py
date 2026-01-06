'''模型初始化操作，支持两个模型(deepseek,通义千问)
'''
#deepseek模型
from langchain_deepseek import ChatDeepSeek
deepSeekModel = ChatDeepSeek(model="deepseek-chat", api_key="DEEPSEEK_API_KEY", temperature=0,max_tokens=2000)

#通义千问模型
from langchain_openai import ChatOpenAI
import os
os.environ["DASHSCOPE_API_KEY"] = "QW_API_KEY"
qwenModel = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
)