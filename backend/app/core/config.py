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


settings = Settings()
