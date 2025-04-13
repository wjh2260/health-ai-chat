from openai import AsyncOpenAI
from typing import List, AsyncGenerator
import json
from uuid import uuid4

from .config import settings
from .models import Message, ChatSession, chat_sessions

# 初始化OpenAI客户端
client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url
)

async def generate_chat_response(messages: List[Message], session_id: str = None) -> AsyncGenerator[str, None]:
    """生成聊天回复，流式输出"""
    # 如果没有提供session_id，创建新会话
    if not session_id or session_id not in chat_sessions:
        session_id = str(uuid4())
        chat_sessions[session_id] = ChatSession(id=session_id)
    
    session = chat_sessions[session_id]
    
    # 记录用户消息
    user_message = messages[-1]
    session.add_message(user_message.role, user_message.content)
    
    # 转换消息格式，只保留role和content
    api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # 在消息列表开头添加系统提示词
    if not any(msg["role"] == "system" for msg in api_messages):
        api_messages.insert(0, {"role": "system", "content": settings.system_prompt})
    
    # 调用OpenAI流式API
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=api_messages,
            stream=True
        )
        
        collected_content = ""
        
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected_content += content
                yield json.dumps({
                    "session_id": session_id,
                    "content": content,
                    "finished": False
                })
        
        # 当响应完成时，将消息保存到会话
        session.add_message("assistant", collected_content)
        
        # 发送完成标志
        yield json.dumps({
            "session_id": session_id,
            "content": "",
            "finished": True
        })
        
    except Exception as e:
        error_message = f"发生错误: {str(e)}"
        session.add_message("assistant", error_message)
        yield json.dumps({
            "session_id": session_id,
            "content": error_message,
            "finished": True
        })