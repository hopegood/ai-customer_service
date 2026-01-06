from  connection import Connection
from fastapi import WebSocket, WebSocketDisconnect
from constants import _welcome
import json
from ai_customer_service.agent.serviceAPI import start
from ai_customer_service.schema.inputSchema import InputSchema
import logging
from datetime import datetime
from ai_customer_service.schema.responseSchema import ResponseSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """增强版的连接管理器"""
    
    def __init__(self):
        self.active_connections: dict[str, Connection] = {}
        self.running = False
        
    async def connect(self, websocket: WebSocket, client_id: str = None) -> Connection:
        """建立新连接"""
        try:
            await websocket.accept()
            connection = Connection(websocket, client_id)
            self.active_connections[connection.client_id] = connection
            
            logger.info(f"客户端 {connection.client_id} 已连接，当前连接数: {len(self.active_connections)}")
            responseSchema = ResponseSchema()
            responseSchema.data = {
                "type": "system",
                "message": _welcome,
                "client_id": connection.client_id,
                "timestamp": datetime.now().isoformat()
            }
            # 发送欢迎消息
            await connection.send_text(responseSchema.json())
            
            return connection
            
        except Exception as e:
            logger.error(f"建立连接失败: {e}")
            raise
    
    async def disconnect(self, client_id: str, reason: str = "正常断开"):
        """断开连接"""
        if client_id in self.active_connections:
            connection = self.active_connections.pop(client_id)
            try:
                await connection.websocket.close()
            except:
                pass
            
            logger.info(f"客户端 {client_id} 已断开，原因: {reason}")
            return True
        return False
    
    async def send_to_client(self, client_id: str, message: str) -> bool:
        """向指定客户端发送消息"""
        if client_id in self.active_connections:
            connection = self.active_connections[client_id]
            return await connection.send_text(message)
        logger.warning(f"尝试向不存在的客户端 {client_id} 发送消息")
        return False
    
    async def broadcast(self, message: str, exclude_client_id: str = None) -> int:
        """广播消息给所有客户端，返回成功发送的数量"""
        success_count = 0
        dead_connections = []
        
        for client_id, connection in list(self.active_connections.items()):
            if exclude_client_id and client_id == exclude_client_id:
                continue
            
            if await connection.send_text(message):
                success_count += 1
            else:
                dead_connections.append(client_id)
        
        # 清理已死亡的连接
        for dead_client_id in dead_connections:
            await self.disconnect(dead_client_id, "连接已失效")
        
        return success_count
    
    async def broadcast_json(self, data: dict, exclude_client_id: str = None) -> int:
        """广播JSON消息"""
        message = json.dumps(data, ensure_ascii=False)
        return await self.broadcast(message, exclude_client_id)
    
    async def broadcast_system_message(self, message: str):
        """广播系统消息"""
        system_msg = {
            "type": "system",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_json(system_msg)
    
    async def process_message(self, client_id: str, message: str, user_id: str, thread_id: str):
        """处理接收到的消息"""
        if client_id not in self.active_connections:
            logger.warning(f"收到不存在的客户端 {client_id} 的消息")
            return
        connection = self.active_connections[client_id]
        try:
            # 尝试解析JSON消息
            data = json.loads(message)
            message_type = data.get("type", "text")
            
            if message_type == "heartbeat":
                # 心跳响应
                await connection.send_json({
                    "type": "heartbeat_ack",
                    "timestamp": datetime.now().isoformat()
                })
            elif message_type == "text":
                # 普通聊天消息
                chat_msg = {
                    "type": "message",
                    "client_id": client_id,
                    "message": data.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                await start(connection,InputSchema(content=data.get("content",""),user_id = user_id), thread_id)
            elif message_type == "private":
                # 私聊消息
                target_client_id = data.get("to")
                if target_client_id and target_client_id in self.active_connections:
                    await self.active_connections[target_client_id].send_json({
                        "type": "private",
                        "from": client_id,
                        "message": data.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    })
            
        except json.JSONDecodeError:
            # 如果不是JSON，当作普通文本处理
            chat_msg = {
                "type": "message",
                "client_id": client_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            await self.broadcast_json(chat_msg, exclude_client_id=client_id)
    
    def get_connection_info(self) -> dict:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "active_connections": [conn.client_id for conn in self.active_connections.values() if conn.is_alive],
            "connections": [
                {
                    "client_id": conn.client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_heartbeat": conn.last_heartbeat.isoformat(),
                    "is_alive": conn.is_alive
                }
                for conn in self.active_connections.values()
            ]
        }
    
    async def start_heartbeat_check(self, interval_seconds: int = 60):
        """启动心跳检查任务"""
        self.running = True
        while self.running:
            await asyncio.sleep(interval_seconds)
            
            stale_clients = []
            for client_id, connection in self.active_connections.items():
                if connection.is_connection_stale(timeout_seconds=interval_seconds * 2):
                    stale_clients.append(client_id)
            
            for stale_client_id in stale_clients:
                logger.warning(f"客户端 {stale_client_id} 心跳超时，强制断开")
                await self.disconnect(stale_client_id, "心跳超时")
    
    def stop_heartbeat_check(self):
        """停止心跳检查"""
        self.running = False

