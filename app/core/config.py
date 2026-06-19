from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/reviews"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application
    APP_NAME: str = "Review Intelligence Platform"
    DEBUG: bool = True
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()