from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    NVIDIA_API_KEY: str
    
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-ai/deepseek-v4-flash"
    DEEPSEEK_REASONING: str = "high"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
