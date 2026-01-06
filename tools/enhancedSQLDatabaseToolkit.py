from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool
)
from langchain_community.utilities.sql_database import SQLDatabase
from typing import Any
from langchain.tools import BaseTool
import ast

class EnhancedSQLDatabaseToolkit(SQLDatabaseToolkit):
    """增强的SQLDatabaseToolkit，包含表注释信息"""
    
    def get_tools(self) -> list[BaseTool]:
        """获取工具列表，包含增强的表列表工具"""
        tools = super().get_tools()
        
        # 替换原来的list_tables工具
        enhanced_list_tool = ListSQLDatabaseToolWithComments(db=self.db)
        
        # 找到并替换list_tables工具
        for i, tool in enumerate(tools):
            if tool.name == "sql_db_list_tables":
                tools[i] = enhanced_list_tool
                break
        
        return tools

class ListSQLDatabaseToolWithComments(ListSQLDatabaseTool):
    """带注释的表列表工具"""
    
    name: str = "list_tables"
    description: str = "列出数据库中的所有表及其描述"
    
    def _run(self, *args: Any, **kwargs: Any) -> str:
        """重写运行方法以包含注释"""
        try:
            # 获取原始表名
            table_names = self.db.get_usable_table_names()           
            # 尝试获取表注释
            tables_with_comments = []
            for table_name in table_names:
                comment = self._get_table_comment(table_name)
                tables_with_comments.append({
                    "table_name": table_name,
                    "comment": comment
                })
            
            # 格式化输出
            output = "数据库中的表：\n\n"
            for table in tables_with_comments:
                if table["comment"]:
                    output += f"- {table['table_name']}: {table['comment']}\n"
                else:
                    output += f"- {table['table_name']}\n"
            
            return output
        except Exception as e:
            # 出错时回退到原始方法
            return super()._run(*args, **kwargs)
    
    def _get_table_comment(self, table_name: str) -> str:
        """根据数据库类型获取表注释"""
        try:
            dialect = self.db.dialect.lower()
            
            if "mysql" in dialect or "mariadb" in dialect:
                query = f"""
                SELECT TABLE_COMMENT 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = '{table_name}'
                """
            elif "postgresql" in dialect or "postgres" in dialect:
                query = f"""
                SELECT obj_description(c.oid) as comment
                FROM pg_class c
                WHERE c.relname = '{table_name}'
                """
            else:
                return ""
            
            result = ast.literal_eval(self.db.run_no_throw(query))
            if result and len(result) > 0 and len(result[0]) > 0:
                return result[0][0]
            return ""
        except:
            return ""



 