"""Ariza bildirishnomalari admin'ga IKKI marta bormasligi.

Bot arizani Firestore'ga yozadi; o'sha yozuv Cloud Functions triggerini
(`onDesignerRequestCreated` / `onCourierRequestCreated`) ishga tushiradi va
adminlarga xabar O'SHA yerdan ketadi. Ilgari bot qo'shimcha ravishda o'zi ham
`_notify_admins()` chaqirardi — natijada admin bitta arizani ikki marta olardi.

Endi bot faqat Firestore yozuvi AMALGA OSHMAGANDA zaxira xabar yuboradi.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys

from _harness import Results  # sys.path ni sozlaydi
from fake_firestore import FakeFirestore

import database.db as dbmod
import handlers.start as start_mod

_r = Results()
check = _r.check


class FakeMessage:
    def __init__(self, text=None, user_id=555, username="sotuvchi"):
        self.text = text
        self.caption = None
        self.contact = None
        self.replies = []

        class _U:
            id = user_id
            full_name = "Ali Valiyev"

        _U.username = username
        self.from_user = _U()

    async def answer(self, text, **kwargs):
        self.replies.append(text)


class FakeState:
    def __init__(self, data):
        self._data = data

    async def get_data(self):
        return dict(self._data)

    async def clear(self):
        self._data = {}


DESIGNER_DATA = {
    "fullName": "Alisher Zokirov",
    "phoneNumber": "+998901234567",
    "specialty": "Merch & Kiyimlar",
}
COURIER_DATA = {
    "fullName": "Otabek Fayzullayev",
    "phoneNumber": "+998939876543",
    "city": "Samarqand shahri",
}


async def _run(handler, state_data, *, firestore_ok):
    """Handlerni bir marta chaqirib, yuborilgan admin xabarlarini qaytaradi."""
    dbmod._db_client = FakeFirestore() if firestore_ok else None
    dbmod.db = dbmod.Database()

    sent = []

    async def fake_notify(text):
        sent.append(text)

    original = start_mod._notify_admins
    start_mod._notify_admins = fake_notify
    original_db = start_mod.db
    start_mod.db = dbmod.db
    try:
        message = FakeMessage(text="https://behance.net/alisher")
        await handler(message, FakeState(state_data))
    finally:
        start_mod._notify_admins = original
        start_mod.db = original_db
    return sent, message.replies


async def main():
    print("\n[Dizayner] Firestore ishlayapti -> CF yuboradi, bot JIM")
    sent, replies = await _run(
        start_mod.designer_apply_finish, DESIGNER_DATA, firestore_ok=True
    )
    check("bot admin'ga xabar YUBORMADI (dublikat yo'q)", sent == [])
    check("foydalanuvchi baribir tasdiq oldi", len(replies) == 1)
    check("tasdiqda ariza raqami bor", "#des_" in replies[0])

    print("\n[Dizayner] Firestore ishlamayapti -> CF ishga tushmaydi, bot ZAXIRA yuboradi")
    sent, replies = await _run(
        start_mod.designer_apply_finish, DESIGNER_DATA, firestore_ok=False
    )
    check("bot zaxira xabar yubordi", len(sent) == 1)
    check("xabar ZAXIRA deb belgilangan", "ZAXIRA XABAR" in sent[0])
    check("adminni qo'lda ko'chirishga ogohlantiradi", "qo'lda" in sent[0])
    check("ariza ma'lumotlari yo'qolmagan", "Alisher Zokirov" in sent[0])
    check("foydalanuvchi baribir tasdiq oldi", len(replies) == 1)

    print("\n[Kuryer] Firestore ishlayapti -> CF yuboradi, bot JIM")
    sent, _ = await _run(
        start_mod.courier_apply_finish, COURIER_DATA, firestore_ok=True
    )
    check("bot admin'ga xabar YUBORMADI (dublikat yo'q)", sent == [])

    print("\n[Kuryer] Firestore ishlamayapti -> bot ZAXIRA yuboradi")
    sent, _ = await _run(
        start_mod.courier_apply_finish, COURIER_DATA, firestore_ok=False
    )
    check("bot zaxira xabar yubordi", len(sent) == 1)
    check("xabar ZAXIRA deb belgilangan", "ZAXIRA XABAR" in sent[0])
    check("ariza ma'lumotlari yo'qolmagan", "Otabek Fayzullayev" in sent[0])

    print("\n[Shartnoma] add_*_request (req_id, saved) qaytaradi")
    dbmod._db_client = FakeFirestore()
    db_ok = dbmod.Database()
    req_id, saved = await db_ok.add_designer_request({"fullName": "X"})
    check("Firestore bor -> saved=True", saved is True)
    check("req_id `des_` bilan boshlanadi", req_id.startswith("des_"))
    dbmod._db_client = None
    db_off = dbmod.Database()
    req_id2, saved2 = await db_off.add_courier_request({"fullName": "Y"})
    check("Firestore yo'q -> saved=False", saved2 is False)
    check("req_id `cou_` bilan boshlanadi", req_id2.startswith("cou_"))

    return _r.summary("Natija")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
