from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # PostgreSQL
    postgres_db: str = Field("maadb", env="POSTGRES_DB")
    postgres_user: str = Field("postgres", env="POSTGRES_USER")
    postgres_password: str = Field("password", env="POSTGRES_PASSWORD")
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")

    # MongoDB
    mongodb_uri: str = Field("mongodb://localhost:27017/maadb", env="MONGODB_URI")
    mongo_initdb_root_username: str | None = Field(None, env="MONGO_INITDB_ROOT_USERNAME")
    mongo_initdb_root_password: str | None = Field(None, env="MONGO_INITDB_ROOT_PASSWORD")

    # Neo4j
    neo4j_uri: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field("neo4j", env="NEO4J_USER")
    neo4j_password: str = Field("password", env="NEO4J_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()