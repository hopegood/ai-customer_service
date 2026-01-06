from fastapi import FastAPI
#创建FastAPI应用实例
app = FastAPI()
from fastapi.responses import HTMLResponse
from ai_customer_service import websocketMgr