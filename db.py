# db.py

from langchain_community.utilities import SQLDatabase
from urllib.parse import quote_plus

# 配置MySQL数据库连接
db_user = "kitchen"
db_password = "123456"
db_host = "192.168.3.35"  # 或你的数据库主机
db_name = "loveKitchen"

# 对密码进行 URL 编码（处理特殊字符）
encoded_password = quote_plus(db_password)


# 创建数据库连接URI
db_uri = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}/{db_name}"

# 创建SQLDatabase实例
db = SQLDatabase.from_uri(db_uri,
                          sample_rows_in_table_info=0  # 不包含示例数据行
                          )
#print(f"Dialect: {db.dialect}")
#print(f"Available tables: {db.get_usable_table_names()}")
#print(f'Sample output: {db.run("SELECT * FROM sys_canteen LIMIT 5;")}')