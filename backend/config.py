"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Centralized settings loaded from .env."""

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Streamlit
    streamlit_port: int = 8501
    streamlit_host: str = "0.0.0.0"

    # CORS: 허용 오리진 (쉼표 구분)
    cors_origins: str = "http://localhost:8501,http://127.0.0.1:8501"

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    # 독립성 검토용 모델
    independence_extraction_model: str = "gpt-4o-mini"
    independence_analysis_model: str = "gpt-4o"
    independence_temperature_structured: float = 0.0
    independence_temperature_creative: float = 0.3

    # App
    debug: bool = False
    log_level: str = "INFO"

    # 법령 CSV 경로 (비우면 루트 기본)
    law_csv_path: str = ""
    # 국가법령정보센터 API 키 (OC 파라미터)
    law_go_kr_oc: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
