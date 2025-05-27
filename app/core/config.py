from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str = "neo4j"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    openai_api_key: str
    gemini_api_key: str

    load_clip_model: bool = True
    load_gemini_model: bool = True
    load_data_mapper: bool = True
    load_knowledge_graph: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
