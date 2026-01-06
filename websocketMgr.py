from ai_customer_service.app import app
from ai_customer_service.connectionManager import ConnectionManager
from fastapi import WebSocket,WebSocketDisconnect
import uuid
from ai_customer_service.config.loggerConfig import logging

# 创建全局连接管理器实例
manager = ConnectionManager()
logger = logging.getLogger(__name__)
logger.info("包已经被加载呢！")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    try:
        client_id = str(uuid.uuid4())[:8]  # 生成短ID
        thread_id = str(uuid.uuid4())[:8]  # 线程ID
        connection = await manager.connect(websocket, client_id)
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"收到数据: {data}",)
                await manager.process_message(connection.client_id, data,user_id, thread_id)
            except WebSocketDisconnect:
                await manager.disconnect(connection.client_id, "客户端主动断开")
                break
            except Exception as e:
                logger.error(f"处理消息时出错: {e}")
                await manager.disconnect(connection.client_id, f"处理错误: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket连接处理失败: {e}")


# 启动应用时开启心跳检查
#@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.start_heartbeat_check())


# 关闭应用时清理资源
@app.on_event("shutdown")
async def shutdown_event():
    manager.stop_heartbeat_check()
    # 断开所有连接
    for client_id in list(manager.active_connections.keys()):
        await manager.disconnect(client_id, "服务关闭")