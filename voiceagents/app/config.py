from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elevenlabs_api_key: str = ""
    agent_id: str = "agent_5201khzcc407fhntbvdsabc0txr5"
    elevenlabs_base_url: str = "https://api.elevenlabs.io/v1"
    cases_file: Path = Path(__file__).resolve().parent.parent.parent / "data" / "verdict_cases.json"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
