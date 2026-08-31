"""Global xatolik ushlagichi.

Ilgari handler ichidagi har qanday istisno faqat aiogram logiga tushardi va
foydalanuvchi hech qanday javob olmasdi — bot "o'lib qolgandek" ko'rinardi.
`setup_errors(dp)` orqali har bir Dispatcher'ga alohida ulanadi — bitta
Router obyektini ikkita Dispatcher'ga biriktirib bo'lmaydi
(`RuntimeError: Router is already attached`).
"""

import logging

from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

USER_MESSAGE = (
    "⚠️ <b>Kutilmagan xatolik yuz berdi.</b>\n"
    "Iltimos, qaytadan urinib ko'ring yoki /start bosing."
)

# Bu xatoliklar odatiy va foydalanuvchiga ko'rsatilmaydi:
#  - "message is not modified": edit_text bir xil matn bilan chaqirilgan
#  - "query is too old": foydalanuvchi eski xabardagi tugmani bosgan
QUIET_BAD_REQUESTS = (
    "message is not modified",
    "query is too old",
    "message to edit not found",
    "message can't be deleted",
)


async def handle_error(event: ErrorEvent) -> bool:
    exception = event.exception

    if isinstance(exception, TelegramForbiddenError):
        # Foydalanuvchi botni bloklagan — javob yuborishning iloji yo'q
        logger.info("Foydalanuvchi botni bloklagan: %s", exception)
        return True

    if isinstance(exception, TelegramRetryAfter):
        logger.warning("Telegram flood limiti: %s sekund kutish kerak", exception.retry_after)
        return True

    if isinstance(exception, TelegramBadRequest):
        text = str(exception).lower()
        if any(fragment in text for fragment in QUIET_BAD_REQUESTS):
            logger.debug("E'tiborsiz Telegram xatosi: %s", exception)
            return True

    logger.exception("Handler xatosi: %s", exception)
    await _notify_user(event)
    return True


async def _notify_user(event: ErrorEvent) -> None:
    """Foydalanuvchiga xabar berishga harakat qiladi (o'zi ham qulamasin)."""
    update = event.update
    try:
        if getattr(update, "callback_query", None) is not None:
            await update.callback_query.answer(
                "⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", show_alert=True
            )
        elif getattr(update, "message", None) is not None:
            await update.message.answer(USER_MESSAGE, parse_mode="HTML")
    except Exception as e:
        logger.warning("Xatolik haqida xabar yuborib bo'lmadi: %s", e)


def setup_errors(dispatcher: Dispatcher) -> None:
    """Global xatolik ushlagichini dispatcher'ga ulaydi."""
    dispatcher.errors.register(handle_error)
