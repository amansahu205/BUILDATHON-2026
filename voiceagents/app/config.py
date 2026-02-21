from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elevenlabs_api_key: str = ""
    agent_id: str = "agent_5201khzcc407fhntbvdsabc0txr5"
    elevenlabs_base_url: str = "https://api.elevenlabs.io/v1"

    # Voice profiles
    interrogator_voice_id: str = "pNInz6obpgDQGcFmaJgB"   # Adam
    coach_voice_id: str = "21m00Tcm4TlvDq8ikWAM"           # Rachel
    tts_model_id: str = "eleven_turbo_v2_5"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    cases_file: Path = Path(__file__).resolve().parent.parent.parent / "data" / "verdict_cases.json"
    reports_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "reports"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.lovable.app",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
