"""Anti-spam throttling va telefon normalizatsiyasi.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys

from _harness import Results  # sys.path ni sozlaydi

from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Chat, Message, User

from middlewares.throttling import ThrottlingMiddleware, setup_throttling
from utils.validators import normalize_phone

_r = Results()
check = _r.check


def make_message(user_id: int = 1) -> Message:
    """Haqiqiy aiogram Message — middleware isinstance() tekshiruvidan o'tsin."""
    return Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=user_id, type="private"),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        text="salom",
    )


class Outbox:
    """Message.answer() ni sinf darajasida ushlab qoladi (tarmoqqa chiqmasin)."""
    def __init__(self):
        self.sent = []
        self._original = None

    def __enter__(self):
        self._original = Message.answer
        outbox = self

        async def fake_answer(self, text, **kwargs):
            outbox.sent.append(text)

        Message.answer = fake_answer
        return self

    def __exit__(self, *exc):
        Message.answer = self._original
        return False


async def main():
    print("\n[Telefon] Normalizatsiya")
    cases = [
        ("+998901234567", "+998901234567", "xalqaro shakl o'zgarmaydi"),
        ("998901234567", "+998901234567", "998... ga + qo'shiladi (ilgari qo'shilmasdi)"),
        ("901234567", "+998901234567", "9 xonali raqamga 998 qo'shiladi (ilgari +901234567 edi)"),
        ("0901234567", "+998901234567", "0 bilan boshlanuvchi lokal shakl"),
        ("+998 90 123 45 67", "+998901234567", "bo'sh joylar tozalanadi"),
        ("998-90-123-45-67", "+998901234567", "chiziqchalar tozalanadi"),
        ("+1 415 555 0123", "+14155550123", "boshqa davlat raqami qabul qilinadi"),
        ("12345", None, "juda qisqa raqam rad etiladi"),
        ("qwerty", None, "matn rad etiladi"),
        ("", None, "bo'sh satr rad etiladi"),
        (None, None, "None rad etiladi"),
    ]
    for raw, expected, label in cases:
        check(f"{label}: {raw!r} -> {expected!r}", normalize_phone(raw) == expected)

    print("\n[Throttling] Tez ketma-ket so'rovlar")
    mw = ThrottlingMiddleware(rate_limit=0.25, warn_every=10.0)
    calls = []

    async def handler(event, data):
        calls.append(data["event_from_user"].id)
        return "ok"

    user_a = {"event_from_user": User(id=1, is_bot=False, first_name="A")}
    user_b = {"event_from_user": User(id=2, is_bot=False, first_name="B")}

    ev = make_message(1)
    with Outbox() as outbox:
        check("birinchi so'rov o'tadi", await mw(handler, ev, user_a) == "ok")
        check("darhol kelgan ikkinchi so'rov to'xtatildi", await mw(handler, ev, user_a) is None)
        check("handler faqat 1 marta chaqirildi", calls == [1])
        check("foydalanuvchi ogohlantirildi", outbox.sent == ["⏳ Biroz sekinroq, iltimos."])

        check("boshqa foydalanuvchi ta'sirlanmaydi",
              await mw(handler, make_message(2), user_b) == "ok")

        await asyncio.sleep(0.3)
        check("interval o'tgach yana o'tadi", await mw(handler, ev, user_a) == "ok")

    print("\n[Throttling] Spamga javoban spam qilmaydi")
    mw2 = ThrottlingMiddleware(rate_limit=0.5, warn_every=10.0)
    with Outbox() as outbox2:
        await mw2(handler, ev, user_a)
        for _ in range(5):
            await mw2(handler, ev, user_a)
        check("5 ta bloklangan so'rovga faqat 1 ta ogohlantirish", len(outbox2.sent) == 1)

    print("\n[Throttling] Xotira cheksiz o'smaydi")
    mw3 = ThrottlingMiddleware(rate_limit=0.0, max_tracked=50)
    for uid in range(500):
        mw3._remember(uid, float(uid))
    check(f"kuzatilayotgan foydalanuvchilar {len(mw3._last_seen)} <= 50", len(mw3._last_seen) == 50)
    check("eng eskisi chiqarib tashlandi", 0 not in mw3._last_seen and 499 in mw3._last_seen)

    print("\n[Throttling] Dispatcher'ga ulanishi")
    dp1, dp2 = Dispatcher(), Dispatcher()
    setup_throttling(dp1)
    setup_throttling(dp2, rate_limit=0.3)
    check("ikkala dispatcher'ga ham ulanadi (umumiy obyekt konflikti yo'q)", True)
    check("message oqimiga ulandi", len(dp1.message.middleware) >= 1)
    check("callback_query oqimiga ulandi", len(dp1.callback_query.middleware) >= 1)

    return _r.summary("Natija")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
