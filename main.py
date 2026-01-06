import os
import sys
# 获取项目根目录（ai_customer_service的上级目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(ROOT_DIR))  # 关键：添加上级目录到Python路径

import uvicorn
import router
import websocketMgr
from ai_customer_service.app import app

if __name__ == "__main__":
    uvicorn.run(
        "ai_customer_service.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )