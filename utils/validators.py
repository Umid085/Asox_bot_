"""Kiruvchi Telegram xabarlarini tekshirish yordamchilari."""

from typing import Optional

from aiogram.types import Message

# Foydalanuvchi FSM oqimida matn o'rniga stiker/rasm/video yuborsa,
# `message.text` `None` bo'ladi va `.strip()` AttributeError bilan qulaydi.
NON_TEXT_HINT = "❌ Iltimos, javobni <b>matn ko'rinishida</b> yuboring."


def get_text(message: Message) -> Optional[str]:
    """Xabardan tozalangan matnni qaytaradi; matn bo'lmasa `None`.

    Rasm/hujjat izohi (`caption`) ham matn sifatida qabul qilinadi.
    """
    raw = message.text if message.text is not None else message.caption
    if raw is None:
        return None
    cleaned = raw.strip()
    return cleaned or None


async def require_text(message: Message, hint: str = NON_TEXT_HINT) -> Optional[str]:
    """Matnni qaytaradi yoki foydalanuvchiga ko'rsatma yuborib `None` qaytaradi.

    Chaqiruvchi `None` kelganda FSM holatini o'zgartirmasdan `return` qilishi
    kerak — shunda foydalanuvchi o'sha bosqichda qolib, qayta urinib ko'radi.
    """
    text = get_text(message)
    if text is None:
        await message.answer(hint, parse_mode="HTML")
        return None
    return text
