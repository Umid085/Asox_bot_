import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_BOT_TOKEN, WEBHOOK_DOMAIN, WEBHOOK_PATH, PORT, ENVIRONMENT
from handlers import start, catalog, cart, checkout, orders, admin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def main():
    polling_tasks = []

    # 1. Main User & Seller Bot (@AsoxUz_Bot)
    if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        bot_user = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp_user = Dispatcher()
        dp_user.include_router(start.router)
        dp_user.include_router(catalog.router)
        dp_user.include_router(cart.router)
        dp_user.include_router(checkout.router)
        dp_user.include_router(orders.router)
        await bot_user.delete_webhook(drop_pending_updates=True)
        logging.info("🚀 ASOX Market User Bot (@AsoxUz_Bot) starting...")
        polling_tasks.append(dp_user.start_polling(bot_user))

    # 2. Dedicated Admin Bot (@asox_admin_bot)
    if ADMIN_BOT_TOKEN and ADMIN_BOT_TOKEN != "YOUR_ADMIN_BOT_TOKEN_HERE":
        bot_admin = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp_admin = Dispatcher()
        dp_admin.include_router(admin.router)
        await bot_admin.delete_webhook(drop_pending_updates=True)
        logging.info("👑 ASOX Market Admin Bot (@asox_admin_bot) starting...")
        polling_tasks.append(dp_admin.start_polling(bot_admin))

    if not polling_tasks:
        logging.error("❌ No bot tokens configured in .env!")
        return

    # Background HTTP health-check for web hosting / Render
    async def handle_health_check(request):
        return web.Response(text="ASOX Market Telegram Bots (User + Admin) are running OK!")

    app = web.Application()
    app.router.add_get('/', handle_health_check)
    app.router.add_get('/health', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"🚀 Health check HTTP server running on port {PORT}...")

    await asyncio.gather(*polling_tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bots stopped.")
