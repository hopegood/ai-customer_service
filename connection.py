import asyncio
import json
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Connection:
    """封装单个连接的相关信息"""
    def __init__(self, websocket: WebSocket, client_id: str = None):
        self.websocket = websocket
        self.client_id = client_id or str(uuid.uuid4())[:8]  # 生成短ID
        self.connected_at = datetime.now()
        
    async def send_text(self, message: str):
        """发送消息，带有异常处理"""
        try:
            await self.websocket.send_text(message)
            return True
        except Exception as e:
            logger.error(f"发送消息到客户端 {self.client_id} 失败: {e}")
            return False
    
    async def send_json(self, data: dict):
        """发送JSON消息"""
        try:
            await self.websocket.send_json(data)
            return True
        except Exception as e:
            logger.error(f"发送JSON到客户端 {self.client_id} 失败: {e}")
            return False
    
    
    def is_connection_stale(self, timeout_seconds: int = 30) -> bool:
        """检查连接是否已过期"""
        return (datetime.now() - self.last_heartbeat).seconds > timeout_seconds


