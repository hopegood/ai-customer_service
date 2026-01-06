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
from localLLMConfiger import office_chat_model as model
from ai_customer_service.tools.sql_tools import tools
from ai_customer_service.agent.sqlAgent import sqlAgent
from ai_customer_service.db import db
from ai_customer_service.tools.enhancedSQLDatabaseToolkit import ListSQLDatabaseToolWithComments

callback = UsageMetadataCallbackHandler()

thread_id_list = []
async def start(connection: Connection,input: InputSchema, thread_id: str):
    """
    接收客户发送的问题
    1：处理客户问题
    2：使用websocket发送客户问题的答案，必须是用流式传输

    备注：流式传输，token不在返回流中
    """
    config = {"callbacks": [callback],"configurable": {"thread_id": thread_id}} 
    init_messages = [HumanMessage(content=input.content)]
    try:   
        if thread_id not in thread_id_list:
            thread_id_list.append(thread_id)
            tool_id = str(uuid.uuid4())
            list_db_table_tool_call = {"name":"sql_db_list_tables", "id": tool_id,"args": {}}
            list_db_table_ai_message = AIMessage(content = f"{input.content},首先，我需要查看数据库中有哪些表。", 
                                                 tool_calls = [list_db_table_tool_call])
            # list_db_table_tool_message = ToolMessage(content = ",".join(db.get_usable_table_names()),  tool_call_id = tool_id)
            listComments = ListSQLDatabaseToolWithComments(db=db)
            list_db_table_tool_message = ToolMessage(content = listComments.run(""),  tool_call_id = tool_id)
            init_messages.append(list_db_table_ai_message)
            init_messages.append(list_db_table_tool_message)
        async for chunk in sqlAgent.astream({"messages": init_messages},
                                config,
                                context = CustomContext(user_id=input.user_id),
                                stream_mode="updates"):
            for step,content in chunk.items():
                if step in ['model','tools']:
                    msg = f"步骤:{step}-----" + content["messages"][-1].content
                    responseSchema = ResponseSchema()
                    responseSchema.data = TextSchema(message=msg,type="text")
                    await connection.send_text(responseSchema.json())
                    if step == 'model':
                        responseSchema = ResponseSchema() #  发送Token使用
                        responseSchema.data = _convertDeepseekToken(callback.usage_metadata).dict()      
                        await connection.send_text(responseSchema.json())   
    except Exception as e: #  兜底错误，不影响前端显示
        responseSchema = ResponseSchema()
        responseSchema.code = 500
        responseSchema.msg = str(e)
        await connection.send_text(responseSchema.json())

def _convertDeepseekToken(deepseekToken: dict[str,dict]) -> TokenSchema:
    print(f"deepseekToken: {deepseekToken}")
    tokenSchema = TokenSchema()
    tokenSchema.type = "token"
    dsToken = deepseekToken["deepseek-chat"]
    tokenSchema.prompt_tokens = dsToken["input_tokens"]
    tokenSchema.complete_tokens = dsToken["output_tokens"]
    tokenSchema.total_tokens = dsToken["total_tokens"]
    tokenSchema.prompt_cache_hit_tokens = dsToken["input_token_details"]["cache_read"]
    print(f"tokenSchema: {tokenSchema}")
    return tokenSchema 




  
  
    
   
    