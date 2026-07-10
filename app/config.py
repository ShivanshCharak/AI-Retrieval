from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Config
    ENV: str = "development"
    PROJECT_NAME: str = "AI Engine"
    
    # API Keys (Pydantic will throw an error on startup if these are missing)
    OPENAI_API_KEY: str
    
    # Vector DB (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    
    # Graph DB (Neo4j)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str
    
    # Cache (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Automatically load values from the .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore" # Ignores extra environment variables not listed above
    )

# Instantiate a single cached instance to use everywhere
settings = Settings()