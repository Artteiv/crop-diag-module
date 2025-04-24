from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    openai_api_key: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
