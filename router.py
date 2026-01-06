from ai_customer_service.app import app
from fastapi.responses import HTMLResponse
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat Demo</title>
</head>
<body>
    <h1>FastAPI WebSocket 聊天室</h1>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off" placeholder="输入消息..."/>
        <button>发送</button>
    </form>
    <ul id='messages'>
    </ul>
    <script>
        // 建立连接到我们的 WebSocket 端点
        var ws = new WebSocket("ws://localhost:8000/ws/10002");
        
        // 监听来自服务器的消息
        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            var content = document.createTextNode(event.data);
            message.appendChild(content);
            messages.appendChild(message);
        };
        
        // 发送消息的函数
        function sendMessage(event) {
            var input = document.getElementById("messageText");
            if (input.value) {
                message = {"type":"text","content":input.value}
                ws.send(JSON.stringify(message));
                input.value = '';
            }
            event.preventDefault();
        }
    </script>
</body>
</html>
"""
'''
@app.get("/")
async def get():
    return HTMLResponse(content="<html><body>this is a body</body></html>")
'''
@app.get("/")
async def get():
    return HTMLResponse(content=html_content)