import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

ADMIN_USERNAMES_RAW = os.getenv("ADMIN_USERNAMES", "shaxzod000001")
ADMIN_USERNAMES = [x.strip().lower().lstrip("@") for x in ADMIN_USERNAMES_RAW.split(",") if x.strip()]

def is_admin_user(user_id: int, username: str = None) -> bool:
    if user_id in ADMIN_IDS:
        return True
    if username and username.lower().lstrip("@") in ADMIN_USERNAMES:
        if user_id not in ADMIN_IDS:
            ADMIN_IDS.append(user_id)
        return True
    return False

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
ORDER_API_KEY = os.getenv("ORDER_API_KEY", "")
MARKET_API_KEY = os.getenv("MARKET_API_KEY", "")

WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN", "").rstrip("/")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
PORT = int(os.getenv("PORT", 8080))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
