"""
核心配置模块
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """系统配置"""
    
    # 应用配置
    APP_NAME: str = "Aletheia"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # LLM配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 搜索配置
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "serpapi")
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    
    # Agent配置
    MAX_CONCURRENT_ANGLES: int = 3  # 最多同时激活的角度数量
    ANGLE_TIMEOUT: int = 120  # 角度Agent超时时间（秒）
    
    # 输出配置
    OUTPUT_LANGUAGE: str = "zh"  # 输出语言
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
