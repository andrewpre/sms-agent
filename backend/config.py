import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "")
    mongo_database: str = os.getenv("MONGO_DATABASE", "dev")
    vonage_api_key: str = os.getenv("VONAGE_API_KEY", "")
    vonage_api_secret: str = os.getenv("VONAGE_API_SECRET", "")
    vonage_from_number: str = os.getenv("VONAGE_FROM_NUMBER", "")
    model_name: str = os.getenv("AGENT_MODEL", "gpt-5-nano")


settings = Settings()
print("Settings:",settings)
