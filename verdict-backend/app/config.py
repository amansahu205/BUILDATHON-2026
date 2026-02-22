from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NODE_ENV: str = "development"
    PORT: int = 4000
    FRONTEND_URL: str = "http://localhost:5173"

    DATABASE_URL: str
    DIRECT_URL: str = ""

    REDIS_URL: str

    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_EXPIRES_IN: str = "8h"
    JWT_REFRESH_EXPIRES_IN: str = "30d"

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "verdict-documents-hackathon"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_INTERROGATOR_VOICE_ID: str = ""
    ELEVENLABS_COACH_VOICE_ID: str = ""

    NEMOTRON_API_KEY: str = ""
    NEMOTRON_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NEMOTRON_MODEL: str = "nvidia/llama-3.1-nemotron-ultra-253b-v1"
    NEMOTRON_TIMEOUT_MS: int = 5000

    NIA_API_KEY: str = ""
    NIA_BASE_URL: str = "https://api.nozomio.com/v1"
    NIA_FRE_CORPUS_INDEX_ID: str = "verdict-fre-rules-v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
