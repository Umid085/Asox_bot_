import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_BOT_TOKEN, WEBHOOK_DOMAIN, WEBHOOK_PATH, PORT, ENVIRONMENT
from handlers import start, catalog, cart, admin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

import json
from database.db import Database, CATEGORIES, SAMPLE_PRODUCTS

async def safe_start_polling(bot: Bot, dp: Dispatcher, bot_name: str):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info(f"🚀 {bot_name} polling started...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"⚠️ {bot_name} ishga tushmadi: {e}. (Telegram tokenini tekshiring)")
    finally:
        try:
            await bot.session.close()
        except Exception:
            pass

async def main():
    # 1. HTTP Server for Health Check & Local Testing
    async def handle_health_check(request):
        return web.Response(text="ASOX Market Telegram Bot Service is running locally OK! (Port: 8080)\n")

    async def handle_categories(request):
        return web.json_response({"ok": True, "categories": CATEGORIES})

    async def handle_products(request):
        return web.json_response({"ok": True, "products": SAMPLE_PRODUCTS})

    async def handle_simulate_start(request):
        return web.json_response({
            "ok": True,
            "bot": "@AsoxUz_Bot",
            "message": "👋 Assalomu alaykum! ASOX Market katalog botiga xush kelibsiz!",
            "buttons": ["🛍 Mahsulotlar Katalogi", "🔍 Qidiruv", "🌐 ASOX Market sayti", "👤 Profilim"]
        })

    app = web.Application()
    app.router.add_get('/', handle_health_check)
    app.router.add_get('/health', handle_health_check)
    app.router.add_get('/api/categories', handle_categories)
    app.router.add_get('/api/products', handle_products)
    app.router.add_get('/api/test/start', handle_simulate_start)

    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
        await site.start()
        logging.info(f"🚀 Local Bot Server & Health Check running on http://localhost:{PORT}...")
    except Exception as e:
        logging.warning(f"⚠️ Health check HTTP server could not start on port {PORT}: {e}")

    polling_tasks = []

    # 2. Main User & Seller Bot (@AsoxUz_Bot)
    if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        bot_user = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp_user = Dispatcher()
        dp_user.include_router(start.router)
        dp_user.include_router(catalog.router)
        dp_user.include_router(cart.router)
        polling_tasks.append(safe_start_polling(bot_user, dp_user, "ASOX Market User Bot (@AsoxUz_Bot)"))

    # 3. Dedicated Admin Bot (@asox_admin_bot)
    if ADMIN_BOT_TOKEN and ADMIN_BOT_TOKEN != "YOUR_ADMIN_BOT_TOKEN_HERE":
        bot_admin = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp_admin = Dispatcher()
        dp_admin.include_router(admin.router)
        polling_tasks.append(safe_start_polling(bot_admin, dp_admin, "ASOX Market Admin Bot (@asox_admin_bot)"))

    if polling_tasks:
        try:
            await asyncio.gather(*polling_tasks)
        except Exception as e:
            logging.error(f"Polling tasks error: {e}")

    # Keep server running locally
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bots stopped.")
