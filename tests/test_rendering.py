"""HTML escaping, matn bo'lmagan xabarlar himoyasi va global error handler.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys
from datetime import datetime

from _harness import Results  # sys.path ni sozlaydi
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.methods import SendMessage
from aiogram.types import Chat, ErrorEvent, Message, Update, User

import handlers.errors as errors_mod
from utils.formatters import esc
from utils.validators import get_text, require_text

_r = Results()
check = _r.check

DUMMY_TOKEN = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"


class FakeMessage:
    """require_text() faqat .text / .caption / .answer() dan foydalanadi."""
    def __init__(self, text=None, caption=None):
        self.text, self.caption, self.replies = text, caption, []
    async def answer(self, text, **kwargs):
        self.replies.append(text)


def make_update(update_id=1, text="/start"):
    user = User(id=555, is_bot=False, first_name="Test")
    chat = Chat(id=555, type="private")
    msg = Message(message_id=update_id, date=datetime.now(), chat=chat, from_user=user, text=text)
    return Update(update_id=update_id, message=msg)


async def main():
    print("\n[A] HTML escaping — Telegram 400 va teg ineksiyasi")
    danger = "Futbolka **Premium** <b>hack</b> & <a href='x'>link</a>"
    out = esc(danger)
    check("`<` va `>` escape qilindi", "<b>" not in out and "&lt;b&gt;" in out)
    check("`&` escape qilindi", "&amp;" in out)
    check("Markdown `**` endi zararsiz (HTML rejimida)", "**" in out)
    check("bo'sh qiymat -> bo'sh satr", esc(None) == "" and esc("") == "")

    print("\n[A] Kodda Markdown parse_mode qolmadimi?")
    import pathlib
    repo = pathlib.Path(__file__).resolve().parents[1]
    offenders = [
        f.relative_to(repo).as_posix()
        for f in repo.glob("**/*.py")
        if "tests" not in f.parts and 'parse_mode="Markdown"' in f.read_text(encoding="utf-8")
    ]
    check(f"hech bir handler Markdown ishlatmaydi (topildi: {offenders or 'yoq'})", not offenders)

    print("\n[A] Foydalanuvchi ma'lumoti escape qilinmasdan qolmadimi?")
    admin_src = (repo / "handlers" / "admin.py").read_text(encoding="utf-8")
    for field in ("order.get('user_name', '')", "order.get('address', '')", "req.get(\"fullName\")"):
        check(f"{field} esc() ichida", f"esc({field}" in admin_src)

    print("\n[B] Matn bo'lmagan xabar handler'ni qulatmaydimi?")
    photo = FakeMessage(text=None)                    # stiker/rasm izohsiz
    check("get_text(rasm) -> None (AttributeError emas)", get_text(photo) is None)
    check("get_text(bo'sh satr) -> None", get_text(FakeMessage(text="   ")) is None)
    check("get_text(izoh) -> caption o'qiladi", get_text(FakeMessage(caption=" Salom ")) == "Salom")
    got = await require_text(photo)
    check("require_text(rasm) -> None", got is None)
    check("foydalanuvchiga ko'rsatma yuborildi", len(photo.replies) == 1)
    ok_msg = FakeMessage(text="  Alisher Zokirov  ")
    check("require_text(matn) -> tozalangan matn", await require_text(ok_msg) == "Alisher Zokirov")
    check("to'g'ri matnda ortiqcha javob yo'q", ok_msg.replies == [])

    print("\n[B] Haqiqiy handlerlar rasm bilan qulaydimi?")
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.base import StorageKey
    from aiogram.fsm.storage.memory import MemoryStorage

    import handlers.admin as admin_mod
    import handlers.start as start_mod

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=StorageKey(bot_id=1, chat_id=555, user_id=555))
    photo_msg = FakeMessage(text=None)
    photo_msg.contact = None
    photo_msg.from_user = User(id=555, is_bot=False, first_name="Test")
    for label, fn in (
        ("designer_apply_name", start_mod.designer_apply_name),
        ("courier_apply_name", start_mod.courier_apply_name),
        ("designer_apply_phone", start_mod.designer_apply_phone),
        ("process_prod_name", admin_mod.process_prod_name),
        ("process_prod_price", admin_mod.process_prod_price),
        ("process_prod_desc", admin_mod.process_prod_desc),
    ):
        photo_msg.replies.clear()
        try:
            await fn(photo_msg, state)
            check(f"{label}(rasm) qulamadi va ko'rsatma berdi", len(photo_msg.replies) == 1)
        except Exception as e:
            check(f"{label}(rasm) qulamadi — {type(e).__name__}: {e}", False)
    check("FSM holati saqlanib qoldi (foydalanuvchi bosqichda qoldi)",
          await state.get_state() is None)

    print("\n[B] Narx: bo'sh joyli/ajratgichli raqam qabul qilinadimi?")
    for raw, expect in (("1 500 000", 1500000), ("1,500,000", 1500000), ("45000", 45000)):
        m = FakeMessage(text=raw)
        st = FSMContext(storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=1, user_id=1))
        await admin_mod.process_prod_price(m, st)
        check(f"narx '{raw}' -> {expect}", (await st.get_data()).get("price") == expect)
    m = FakeMessage(text="qimmat")
    st = FSMContext(storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=1, user_id=1))
    await admin_mod.process_prod_price(m, st)
    check("raqam bo'lmasa rad etiladi", "price" not in (await st.get_data()))

    print("\n[C] Global error handler")
    probe = Dispatcher()
    errors_mod.setup_errors(probe)
    check("setup_errors() ushlagichni ro'yxatdan o'tkazadi", len(probe.errors.handlers) == 1)
    probe2 = Dispatcher()
    errors_mod.setup_errors(probe2)
    check("ikkinchi Dispatcher'ga ham ulanadi (Router konflikti yo'q)",
          len(probe2.errors.handlers) == 1)

    # jim o'tkaziladigan xatoliklar
    quiet = TelegramBadRequest(method=SendMessage(chat_id=1, text="x"),
                               message="Bad Request: message is not modified")
    notified = []
    async def fake_notify(event): notified.append(event)
    errors_mod._notify_user = fake_notify

    handled = await errors_mod.handle_error(ErrorEvent(update=make_update(), exception=quiet))
    check("'message is not modified' jim o'tkazildi", handled and not notified)
    blocked = TelegramForbiddenError(method=SendMessage(chat_id=1, text="x"),
                                     message="Forbidden: bot was blocked by the user")
    handled = await errors_mod.handle_error(ErrorEvent(update=make_update(), exception=blocked))
    check("bloklagan foydalanuvchi jim o'tkazildi", handled and not notified)
    handled = await errors_mod.handle_error(ErrorEvent(update=make_update(), exception=ValueError("boom")))
    check("kutilmagan xato -> foydalanuvchi ogohlantirildi", handled and len(notified) == 1)

    print("\n[C] Dispatcher haqiqatan handler xatosini ushlaydimi? (uchdan-uchgacha)")
    caught = []
    async def spy(event):
        caught.append(type(event.exception).__name__)
    errors_mod._notify_user = spy

    boom_router = Router()
    @boom_router.message()
    async def boom(message: Message):
        raise RuntimeError("ataylab qulatildi")

    dp = Dispatcher()
    dp.include_router(boom_router)
    errors_mod.setup_errors(dp)
    bot = Bot(token=DUMMY_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await dp.feed_update(bot, make_update(update_id=7, text="salom"))
        check("handler istisnosi error handler'ga yetdi", caught == ["RuntimeError"])
        check("istisno tashqariga chiqmadi (bot to'xtamadi)", True)
    except Exception as e:
        check(f"istisno tashqariga chiqib ketdi: {type(e).__name__}: {e}", False)
    finally:
        await bot.session.close()

    return _r.summary("Natija")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
