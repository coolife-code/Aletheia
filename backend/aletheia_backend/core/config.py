import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
        # 优先使用环境变量
        env_prefix=""
    )

    # 应用配置
    APP_NAME: str = "Aletheia"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # LLM 配置 - 从环境变量读取，如果没有则使用默认值
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    # Verdict Agent 专用配置
    VERDICT_LLM_MODEL: Optional[str] = os.getenv("VERDICT_LLM_MODEL")
    VERDICT_LLM_TEMPERATURE: float = float(os.getenv("VERDICT_LLM_TEMPERATURE", "0.1"))

    # 搜索配置
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "serpapi")
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    GOOGLE_SEARCH_API_KEY: Optional[str] = os.getenv("GOOGLE_SEARCH_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    BING_SEARCH_API_KEY: Optional[str] = os.getenv("BING_SEARCH_API_KEY")
    NEWSAPI_KEY: Optional[str] = os.getenv("NEWSAPI_KEY")

    # Embedding 配置
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # 数据库配置
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")


# 创建设置实例
settings = Settings()
