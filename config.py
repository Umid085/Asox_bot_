import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

if not ADMIN_IDS:
    logger.warning(
        "⚠️ ADMIN_IDS bo'sh — admin panelga hech kim kira olmaydi. "
        "@userinfobot orqali ID oling va ADMIN_IDS ga yozing."
    )


def is_admin_user(user_id: int, username: str = None) -> bool:
    """Adminlikni FAQAT raqamli Telegram ID bo'yicha tekshiradi.

    Ilgari bu yerda username bo'yicha tekshiruv ham bor edi va mos kelgan
    foydalanuvchi ID si global ADMIN_IDS ro'yxatiga qo'shib qo'yilardi.
    Telegram username'lari bo'shatilib boshqa odam tomonidan qayta ro'yxatdan
    o'tkazilishi mumkin bo'lgani uchun bu doimiy admin huquqini egallab olishga
    imkon berardi. `username` parametri chaqiruv joylari buzilmasligi uchun
    saqlanib qolgan, lekin e'tiborga olinmaydi.
    """
    return user_id in ADMIN_IDS


ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
ORDER_API_KEY = os.getenv("ORDER_API_KEY", "")
MARKET_API_KEY = os.getenv("MARKET_API_KEY", "")

# `/start shop_<id>_<sig>` deep-link havolalarini imzolash kaliti.
# Xuddi shu qiymat asox.uz backendida ham bo'lishi shart.
SHOP_LINK_SECRET = os.getenv("SHOP_LINK_SECRET", "")

WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN", "").rstrip("/")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
PORT = int(os.getenv("PORT", 8080))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
