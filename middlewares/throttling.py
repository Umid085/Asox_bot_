"""Anti-spam: har bir foydalanuvchi uchun minimal interval.

Ariza oqimlari (dizayner / kuryer) va katalog tugmalari hech qanday
cheklovsiz edi — bitta foydalanuvchi soniyada o'nlab ariza yuborib
Firestore'ni to'ldirib tashlashi mumkin edi.
"""

import logging
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)

THROTTLE_MESSAGE = "⏳ Biroz sekinroq, iltimos."


class ThrottlingMiddleware(BaseMiddleware):
    """Interval ichida kelgan ikkinchi so'rovni handlerga o'tkazmaydi.

    `rate_limit` — ketma-ket ikki so'rov orasidagi minimal vaqt (sekund).
    `warn_every` — foydalanuvchini qanchalik tez-tez ogohlantirish (spamga
    javoban spam qilmaslik uchun).
    `max_tracked` — xotirada saqlanadigan foydalanuvchilar soni chegarasi;
    eng eskisi chiqarib tashlanadi (cheksiz o'sishning oldini oladi).
    """

    def __init__(
        self,
        rate_limit: float = 0.6,
        warn_every: float = 3.0,
        max_tracked: int = 10_000,
    ) -> None:
        self.rate_limit = rate_limit
        self.warn_every = warn_every
        self.max_tracked = max_tracked
        self._last_seen: "OrderedDict[int, float]" = OrderedDict()
        self._last_warn: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        previous = self._last_seen.get(user.id)
        self._remember(user.id, now)

        if previous is not None and (now - previous) < self.rate_limit:
            logger.debug("Throttled: user=%s", user.id)
            await self._warn(event, user.id, now)
            return None  # handler chaqirilmaydi — FSM holati o'zgarmaydi

        return await handler(event, data)

    def _remember(self, user_id: int, now: float) -> None:
        self._last_seen[user_id] = now
        self._last_seen.move_to_end(user_id)
        while len(self._last_seen) > self.max_tracked:
            evicted, _ = self._last_seen.popitem(last=False)
            self._last_warn.pop(evicted, None)

    async def _warn(self, event: TelegramObject, user_id: int, now: float) -> None:
        # Callback uchun javob berish shart — aks holda tugma "aylanib" qoladi
        if isinstance(event, CallbackQuery):
            try:
                await event.answer(THROTTLE_MESSAGE)
            except Exception:
                pass
            return

        last_warn = self._last_warn.get(user_id)
        if last_warn is not None and (now - last_warn) < self.warn_every:
            return
        self._last_warn[user_id] = now
        if isinstance(event, Message):
            try:
                await event.answer(THROTTLE_MESSAGE)
            except Exception:
                pass


def setup_throttling(
    dispatcher: Dispatcher,
    rate_limit: float = 0.6,
    middleware: Optional[ThrottlingMiddleware] = None,
) -> ThrottlingMiddleware:
    """Throttling'ni message va callback_query oqimlariga ulaydi."""
    middleware = middleware or ThrottlingMiddleware(rate_limit=rate_limit)
    dispatcher.message.middleware(middleware)
    dispatcher.callback_query.middleware(middleware)
    return middleware
