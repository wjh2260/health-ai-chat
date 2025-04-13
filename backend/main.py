from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import json
import uvicorn
from uuid import uuid4

from app.models import Message, chat_sessions, ChatSession, ChatRequest, ChatResponse
from app.chat import generate_chat_response
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Chat API 运行中"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """用于非流式响应的聊天API接口"""
    
    # 获取或创建会话
    session_id = request.session_id
    if not session_id or session_id not in chat_sessions:
        session_id = str(uuid4())
        chat_sessions[session_id] = ChatSession(id=session_id)
    
    # 创建消息
    message = Message(role="user", content=request.message)
    
    # 获取消息历史(如果前端提供)
    messages_history = getattr(request, 'messages', None)
    messages_to_send = []
    
    if messages_history:
        # 如果前端提供了消息历史，使用它
        messages_to_send = [Message(role=msg["role"], content=msg["content"]) 
                           for msg in messages_history]
    else:
        # 否则只使用当前消息
        messages_to_send = [message]
    
    # 生成回复
    collected_response = ""
    async for chunk in generate_chat_response(messages_to_send, session_id):
        chunk_data = json.loads(chunk)
        if not chunk_data["finished"]:
            collected_response += chunk_data["content"]
    
    return ChatResponse(message=collected_response, session_id=session_id)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """用于流式响应的WebSocket聊天接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # 提取消息、会话ID和历史消息
            user_message = request_data.get("message", "")
            session_id = request_data.get("session_id")
            messages_history = request_data.get("messages", None)
            
            # 创建要发送到AI的消息列表
            if messages_history:
                # 使用前端提供的完整历史
                messages_to_send = [Message(role=msg["role"], content=msg["content"]) 
                                    for msg in messages_history]
            else:
                # 只用当前消息
                messages_to_send = [Message(role="user", content=user_message)]
            
            # 生成并发送流式响应
            async for response_chunk in generate_chat_response(messages_to_send, session_id):
                await websocket.send_text(response_chunk)
                
    except WebSocketDisconnect:
        # 客户端断开连接
        pass
    except Exception as e:
        # 发生其他错误
        error_msg = json.dumps({"error": str(e)})
        await websocket.send_text(error_msg)

@app.get("/sessions", response_model=Dict[str, List[Dict]])
async def get_sessions():
    """获取所有会话"""
    result = {}
    for session_id, session in chat_sessions.items():
        result[session_id] = [msg.dict() for msg in session.messages]
    return result

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """获取特定会话的消息"""
    if session_id not in chat_sessions:
        return {"error": "会话不存在"}
    
    session = chat_sessions[session_id]
    return {"session_id": session_id, "messages": [msg.dict() for msg in session.messages]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)