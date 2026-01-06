# tools/sql_tools.py

from ai_customer_service.db import db
from ai_customer_service.localLLMConfiger import office_chat_model as model
#  from langchain_community.agent_toolkits import SQLDatabaseToolkit
from ai_customer_service.tools.enhancedSQLDatabaseToolkit import EnhancedSQLDatabaseToolkit
toolkit = EnhancedSQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()

for tool in tools:
    print(f"{tool.name}: {tool.description}\n")

__all__ = [ 
    "tools"
]

