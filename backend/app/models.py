from pydantic import BaseModel
from typing import List, Optional, Dict, Literal
import time
from uuid import uuid4

class Message(BaseModel):
    """聊天消息模型"""
    role: Literal["user", "assistant", "system"]
    content: str
    
class ChatMessage(BaseModel):
    """包含ID和时间戳的完整聊天消息"""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: float

class ChatSession(BaseModel):
    """聊天会话，包含多条消息"""
    id: str
    messages: List[ChatMessage] = []
    
    def add_message(self, role: str, content: str) -> ChatMessage:
        """添加新消息到会话"""
        message = ChatMessage(
            id=str(uuid4()),
            role=role,
            content=content,
            timestamp=time.time()
        )
        self.messages.append(message)
        return message

class ChatRequest(BaseModel):
    """用户发送的聊天请求"""
    message: str
    session_id: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None  # 添加此字段接收完整对话历史

class ChatResponse(BaseModel):
    """AI回复的响应"""
    message: str
    session_id: str

# 内存中存储会话
chat_sessions: Dict[str, ChatSession] = {}