import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Aletheia"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # LLM 配置
    LLM_PROVIDER: str = "openai"  # openai | claude
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Verdict Agent 专用配置
    VERDICT_LLM_MODEL: Optional[str] = None
    VERDICT_LLM_TEMPERATURE: float = 0.1

    # 搜索配置
    SEARCH_PROVIDER: str = "serpapi"  # serpapi | google | bing
    SERPAPI_KEY: Optional[str] = None
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    BING_SEARCH_API_KEY: Optional[str] = None
    NEWSAPI_KEY: Optional[str] = None

    # Embedding 配置
    EMBEDDING_PROVIDER: str = "openai"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 数据库配置
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        # 支持从环境变量读取
        env_file_encoding = 'utf-8'


# 创建设置实例
settings = Settings()

# 如果环境变量中有配置，覆盖默认值（用于ModelScope Space部署）
# ModelScope Space会将Secrets注入为环境变量
if os.getenv("OPENAI_API_KEY"):
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_BASE_URL"):
    settings.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
if os.getenv("OPENAI_MODEL"):
    settings.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
if os.getenv("ANTHROPIC_API_KEY"):
    settings.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if os.getenv("LLM_PROVIDER"):
    settings.LLM_PROVIDER = os.getenv("LLM_PROVIDER")
if os.getenv("VERDICT_LLM_MODEL"):
    settings.VERDICT_LLM_MODEL = os.getenv("VERDICT_LLM_MODEL")
if os.getenv("VERDICT_LLM_TEMPERATURE"):
    try:
        settings.VERDICT_LLM_TEMPERATURE = float(os.getenv("VERDICT_LLM_TEMPERATURE"))
    except ValueError:
        pass
