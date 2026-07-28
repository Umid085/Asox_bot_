import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN, WEBHOOK_DOMAIN, WEBHOOK_PATH, PORT, ENVIRONMENT
from handlers import start, catalog, cart, checkout, orders, admin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def on_startup(bot: Bot):
    if WEBHOOK_DOMAIN:
        webhook_url = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"
        logging.info(f"Setting webhook to: {webhook_url}")
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    else:
        logging.info("Running in Long Polling mode (No WEBHOOK_DOMAIN set)")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("❌ BOT_TOKEN is missing or not set in .env file!")
        logging.error("Please edit .env file and set your Telegram Bot Token from @BotFather.")
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(checkout.router)
    dp.include_router(orders.router)
    dp.include_router(admin.router)

    if WEBHOOK_DOMAIN:
        # Webhook Mode for Production Server (Render / Railway / VPS)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        dp.startup.register(on_startup)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
        logging.info(f"🚀 Webhook server starting on port {PORT}...")
        await site.start()
        
        # Keep running
        await asyncio.Event().wait()
    else:
        # Polling Mode
        logging.info("🚀 ASOX Market Telegram Bot started in Polling mode...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
