import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_VIDEO_BUCKET: str
    SUPABASE_FRAMES_BUCKET: str = "scene-frames"
    SUPABASE_DB_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        extra="ignore"
    )

settings = Settings()