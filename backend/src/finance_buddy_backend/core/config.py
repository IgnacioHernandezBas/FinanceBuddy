from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finance_buddy:finance_buddy@localhost:5432/finance_buddy"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3-flash-preview"
    langsearch_api_key: str | None = None

    agent_enabled: bool = False
    agent_use_separate_endpoint: bool = True
    agent_graph_version: str = "agentic_v1"
    agent_web_access_mode: str = "allowed" # disabled,fallback_only,allowed
    agent_require_web_search_consent: bool = True 
    agent_web_search_provider: str = "langsearch"
    agent_web_search_api_key: str | None = None
    agent_web_search_max_results: int = 5
    agent_web_search_allowed_domains: str = "agenciatributaria.gob.es,cnmv.es,bde.es"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "financebuddy-end-to-end-rag"
    mlflow_enabled: bool = True
    mlflow_langgraph_autolog_enabled: bool = True

settings = Settings()
