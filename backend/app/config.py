from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """应用程序配置"""
    # OpenAI API配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 系统提示词配置
    system_prompt: str = os.getenv("SYSTEM_PROMPT", "你是一个有用的AI助手，回答用户问题时尽量简洁明了。")
    
    # 应用配置
    app_name: str = "AI Chat API"
    app_version: str = "0.1.0"

# 创建全局设置实例
settings = Settings()