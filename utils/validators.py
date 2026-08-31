"""Kiruvchi Telegram xabarlarini tekshirish yordamchilari."""

import re

from aiogram.types import Message

# Foydalanuvchi FSM oqimida matn o'rniga stiker/rasm/video yuborsa,
# `message.text` `None` bo'ladi va `.strip()` AttributeError bilan qulaydi.
NON_TEXT_HINT = "❌ Iltimos, javobni <b>matn ko'rinishida</b> yuboring."


def get_text(message: Message) -> str | None:
    """Xabardan tozalangan matnni qaytaradi; matn bo'lmasa `None`.

    Rasm/hujjat izohi (`caption`) ham matn sifatida qabul qilinadi.
    """
    raw = message.text if message.text is not None else message.caption
    if raw is None:
        return None
    cleaned = raw.strip()
    return cleaned or None


async def require_text(message: Message, hint: str = NON_TEXT_HINT) -> str | None:
    """Matnni qaytaradi yoki foydalanuvchiga ko'rsatma yuborib `None` qaytaradi.

    Chaqiruvchi `None` kelganda FSM holatini o'zgartirmasdan `return` qilishi
    kerak — shunda foydalanuvchi o'sha bosqichda qolib, qayta urinib ko'radi.
    """
    text = get_text(message)
    if text is None:
        await message.answer(hint, parse_mode="HTML")
        return None
    return text


# O'zbekiston raqami: 998 + 9 ta raqam = 12 ta raqam
UZ_COUNTRY_CODE = "998"
UZ_LOCAL_LENGTH = 9
MIN_INTL_DIGITS = 10
MAX_INTL_DIGITS = 15


def normalize_phone(raw: str | None) -> str | None:
    """Telefon raqamini `+998901234567` ko'rinishiga keltiradi.

    Ilgari `if not phone.startswith("+") and not phone.startswith("998")`
    tekshiruvi `998901234567` ga `+` qo'shmasdan o'tkazib yuborardi va
    `901234567` ni `+901234567` (noto'g'ri davlat kodi) qilib qo'yardi.

    Raqam ishonarli bo'lmasa `None` qaytaradi — chaqiruvchi qayta so'raydi.
    """
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None

    if len(digits) == UZ_LOCAL_LENGTH:
        digits = UZ_COUNTRY_CODE + digits
    elif len(digits) == UZ_LOCAL_LENGTH + 1 and digits.startswith("0"):
        # 0901234567 -> 901234567
        digits = UZ_COUNTRY_CODE + digits[1:]
    elif not (MIN_INTL_DIGITS <= len(digits) <= MAX_INTL_DIGITS):
        return None

    return "+" + digits
