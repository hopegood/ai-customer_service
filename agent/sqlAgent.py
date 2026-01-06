from ai_customer_service.exception.stopAgentError import StopAgentError
from ai_customer_service.schema import responseSchema
from ai_customer_service.schema.inputSchema import InputSchema
from ai_customer_service.schema.textSchema import TextSchema
from ai_customer_service.schema.tokenSchema import TokenSchema
import json
from langchain_core.callbacks import UsageMetadataCallbackHandler
from fastapi.responses import HTMLResponse
from ai_customer_service.connection import Connection
from langchain.messages import HumanMessage,AIMessage,ToolMessage
import uuid
from ai_customer_service.schema.responseSchema import ResponseSchema
from ai_customer_service.schema.customContext import CustomContext
from langchain.agents import create_agent
from langgraph.store.redis import RedisStore  
from ai_customer_service.prompt.system_prompt import sql_system_prompt
from localLLMConfiger import office_chat_model as deepseek_model
#from localLLMConfiger import qwenLLM as model
from ai_customer_service.tools.sql_tools import tools
from langgraph.checkpoint.memory import InMemorySaver # 增加上下文记忆功能
from ai_customer_service.agent.modelMiddleware import ModelMiddleware


'''
from langchain_qwq import ChatQwen
import os
os.environ["DASHSCOPE_API_KEY"] = "QW_API_KEY"
model = ChatQwen(model="qwen-plus",temperature=0,max_tokens=2000)
'''

#通义千问模型
from langchain_openai import ChatOpenAI
import os
os.environ["DASHSCOPE_API_KEY"] = "QW_API_KEY"
qwen_model = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max",  # deepseek-v3.2，此处以qwen-max,qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
)

DB_URI = "redis://192.168.3.2:5000"
with (RedisStore.from_conn_string(DB_URI) as redis_store):
        redis_store.setup()
        sqlAgent = create_agent(
                deepseek_model,
                tools,
                system_prompt = sql_system_prompt,
                context_schema = CustomContext,
                checkpointer = InMemorySaver(), 
                store = redis_store,
                middleware = [ModelMiddleware()]
            ) 
