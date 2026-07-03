from pydantic_settings import BaseSettings

class Settings(BaseSettings):
# Project info
    PROJECT_NAME: str
    API_V1_STR: str

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # File upload settings — add these
    UPLOAD_DIR: str
    MAX_FILE_SIZE_MB: int

    CHROMA_DIR: str

    GEMINI_API_KEY: str

    @property
    def DATABASE_URL(self) -> str:
            import urllib.parse
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"


settings = Settings()