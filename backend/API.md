# API文档和调用示例

## 1. 健康检查 API

**请求类型**: GET  
**URL**: `http://localhost:8000/`

**Postman设置**:
- 选择 `GET` 方法
- 输入URL: `http://localhost:8000/`
- 点击 "Send"

**预期响应**:
```json
{
  "status": "ok",
  "message": "AI Chat API 运行中"
}
```

## 2. 非流式聊天 API

### 2.1 基本聊天请求

**请求类型**: POST  
**URL**: `http://localhost:8000/chat`  
**Headers**: 
- Content-Type: application/json

**Body** (raw, JSON):
```json
{
  "message": "我最近经常头痛，可能是什么原因？",
  "session_id": null
}
```

**Postman设置**:
- 选择 `POST` 方法
- 输入URL: `http://localhost:8000/chat`
- 在 "Headers" 选项卡中添加 `Content-Type: application/json`
- 在 "Body" 选项卡中选择 "raw" 和 "JSON"，然后输入上述JSON
- 点击 "Send"

**预期响应**:
```json
{
  "message": "头痛可能由多种原因引起，包括压力、睡眠不足、脱水、眼睛疲劳、颈部紧张等...",
  "session_id": "生成的会话ID"
}
```

### 2.2 使用现有会话ID的聊天请求

**请求类型**: POST  
**URL**: `http://localhost:8000/chat`  
**Headers**: 
- Content-Type: application/json

**Body** (raw, JSON):
```json
{
  "message": "这种头痛会不会是高血压引起的？",
  "session_id": "由您指定的，或者上一步返回的会话ID"
}
```

**Postman设置**:
- 选择 `POST` 方法
- 输入URL: `http://localhost:8000/chat`
- 在 "Headers" 选项卡中添加 `Content-Type: application/json`
- 在 "Body" 选项卡中选择 "raw" 和 "JSON"，然后输入上述JSON（使用上一步返回的会话ID）
- 点击 "Send"

**预期响应**:
```json
{
  "message": "高血压确实可能导致头痛，特别是后脑勺疼痛...",
  "session_id": "与请求中相同的会话ID"
}
```

### 2.3 使用完整消息历史的聊天请求

**请求类型**: POST  
**URL**: `http://localhost:8000/chat`  
**Headers**: 
- Content-Type: application/json

**Body** (raw, JSON):
```json
{
  "message": "有什么方法可以缓解这种头痛？",
  "session_id": null,
  "messages": [
    {
      "role": "user",
      "content": "我最近经常头痛，可能是什么原因？"
    },
    {
      "role": "assistant",
      "content": "头痛可能由多种原因引起，包括压力、睡眠不足、脱水、眼睛疲劳、颈部紧张等。如果是偶尔发生的轻微头痛，通常不必太担心。但如果头痛频繁、剧烈或伴随其他症状，建议就医检查。您能描述一下头痛的具体情况吗？比如疼痛位置、性质、持续时间等。"
    },
    {
      "role": "user",
      "content": "这种头痛会不会是高血压引起的？"
    },
    {
      "role": "assistant",
      "content": "高血压确实可能导致头痛，特别是后脑勺疼痛。高血压引起的头痛通常在早晨醒来时最为明显，随着一天的进行可能会减轻。不过，许多高血压患者可能没有任何症状，这就是为什么高血压常被称为'沉默的杀手'。如果您怀疑自己可能有高血压，建议测量血压并咨询医生。除了高血压，您是否有其他症状，如头晕、视力模糊或恶心？"
    }
  ]
}
```

**Postman设置**:
- 选择 `POST` 方法
- 输入URL: `http://localhost:8000/chat`
- 在 "Headers" 选项卡中添加 `Content-Type: application/json`
- 在 "Body" 选项卡中选择 "raw" 和 "JSON"，然后输入上述JSON
- 点击 "Send"

**预期响应**:
```json
{
  "message": "缓解头痛的方法有很多，取决于头痛的原因...",
  "session_id": "新生成的会话ID"
}
```

## 3. 获取所有会话 API

**请求类型**: GET  
**URL**: `http://localhost:8000/sessions`

**Postman设置**:
- 选择 `GET` 方法
- 输入URL: `http://localhost:8000/sessions`
- 点击 "Send"

**预期响应**:
```json
{
  "会话ID1": [
    {
      "id": "消息ID",
      "role": "user",
      "content": "我最近经常头痛，可能是什么原因？",
      "timestamp": 1681234567.89
    },
    {
      "id": "消息ID",
      "role": "assistant",
      "content": "头痛可能由多种原因引起，包括压力、睡眠不足...",
      "timestamp": 1681234568.89
    }
  ],
  "会话ID2": [
    // 另一个会话的消息...
  ]
}
```

## 4. 获取特定会话 API

**请求类型**: GET  
**URL**: `http://localhost:8000/session/{session_id}`

**Postman设置**:
- 选择 `GET` 方法
- 输入URL: `http://localhost:8000/session/上面获取的某个会话ID`
- 点击 "Send"

**预期响应**:
```json
{
  "session_id": "请求的会话ID",
  "messages": [
    {
      "id": "消息ID",
      "role": "user",
      "content": "我最近经常头痛，可能是什么原因？",
      "timestamp": 1681234567.89
    },
    {
      "id": "消息ID",
      "role": "assistant",
      "content": "头痛可能由多种原因引起，包括压力、睡眠不足...",
      "timestamp": 1681234568.89
    }
  ]
}
```

## 5. WebSocket流式聊天 API

### 方法1：使用Postman的WebSocket请求

**Postman设置**:
1. 点击 "New" > "WebSocket Request"
2. 输入URL: `ws://localhost:8000/ws/chat`
3. 点击 "Connect"
4. 连接成功后，在 "Message" 输入框中输入以下JSON：
   ```json
   {
     "message": "我最近经常头痛，可能是什么原因？",
     "session_id": null
   }
   ```
5. 点击 "Send"

**预期响应**:
将收到多个消息，每个消息包含一小段回复内容，最后一个消息的`finished`字段为`true`。

### 方法2：使用简单的HTML页面测试

创建一个HTML文件，使用JavaScript WebSocket API进行测试：

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket测试</title>
    <style>
        #messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h2>WebSocket聊天测试</h2>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="输入消息...">
    <button onclick="sendMessage()">发送</button>
    <script>
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        let socket;
        let sessionId = null;
        let fullResponse = '';

        // 连接WebSocket
        function connect() {
            socket = new WebSocket('ws://localhost:8000/ws/chat');
            
            socket.onopen = function(e) {
                addMessage('系统', '连接已建立');
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.session_id) {
                    sessionId = data.session_id;
                }
                
                if (data.error) {
                    addMessage('错误', data.error);
                    return;
                }
                
                if (data.finished) {
                    addMessage('完成', '回复已完成');
                    addMessage('完整回复', fullResponse);
                    fullResponse = '';
                } else {
                    fullResponse += data.content;
                    addMessage('收到片段', data.content);
                }
            };
            
            socket.onclose = function(event) {
                if (event.wasClean) {
                    addMessage('系统', `连接已关闭，代码=${event.code} 原因=${event.reason}`);
                } else {
                    addMessage('系统', '连接中断');
                }
            };
            
            socket.onerror = function(error) {
                addMessage('错误', `${error.message}`);
            };
        }
        
        function sendMessage() {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                addMessage('系统', '未连接，正在尝试重新连接...');
                connect();
                setTimeout(sendMessage, 1000);
                return;
            }
            
            const message = messageInput.value;
            if (!message) return;
            
            const payload = {
                message: message,
                session_id: sessionId
            };
            
            socket.send(JSON.stringify(payload));
            addMessage('发送', message);
            messageInput.value = '';
        }
        
        function addMessage(sender, message) {
            const messageElement = document.createElement('div');
            messageElement.textContent = `[${sender}] ${message}`;
            messagesDiv.appendChild(messageElement);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // 初始连接
        connect();
    </script>
</body>
</html>
```

将此HTML文件保存到本地，然后在浏览器中打开它来测试WebSocket连接。
