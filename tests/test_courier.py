"""Kuryer dispetcher oqimi.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys

from _harness import Results  # sys.path ni sozlaydi
from fake_firestore import FakeFirestore

import database.db as dbmod

_r = Results()
check = _r.check

SEED = {
    "courier_requests": {
        "cou_1": {
            "userId": "555", "fullName": "Otabek Fayzullayev",
            "phoneNumber": "+998901234567", "telegramUsername": "otabek",
            "city": "Samarqand shahri", "vehicle": "Skuter / Moped",
            "status": "pending",
        },
        # userId yo'q — eski yoki buzilgan ariza
        "cou_bad": {"fullName": "Nomsiz", "status": "pending"},
    },
    "couriers": {},
    "orders": {},
}


async def main():
    fake = FakeFirestore(SEED)
    dbmod._db_client = fake
    db = dbmod.Database()

    print("\n[1] Ariza tasdiqlansa couriers hujjati yaratiladimi?")
    courier = await db.approve_courier_request("cou_1")
    check("kuryer qaytdi", courier is not None)
    check("id = telegramChatId", courier and courier["id"] == "555")
    check("couriers/555 yaratildi", "555" in fake.data["couriers"])
    doc = fake.data["couriers"].get("555", {})
    check("isActive = True", doc.get("isActive") is True)
    check("activeOrderId = None", doc.get("activeOrderId") is None)
    check("completedCount = 0", doc.get("completedCount") == 0)
    check("ism ko'chirildi", doc.get("fullName") == "Otabek Fayzullayev")
    check("telefon ko'chirildi", doc.get("phoneNumber") == "+998901234567")
    check("requestId saqlandi", doc.get("requestId") == "cou_1")
    check("ariza statusi approved",
          fake.data["courier_requests"]["cou_1"]["status"] == "approved")

    print("\n[1] Ikki marta tasdiqlash bitta hujjat qoldiradimi?")
    before = len(fake.data["couriers"])
    again = await db.approve_courier_request("cou_1")
    check("qayta tasdiqlash ishladi", again is not None)
    check("yangi hujjat yaratilmadi", len(fake.data["couriers"]) == before)

    print("\n[1] userId yo'q ariza — hujjat yaratilmaydi, status pending qoladi")
    bad = await db.approve_courier_request("cou_bad")
    check("None qaytdi", bad is None)
    check("couriers ga yozilmadi", len(fake.data["couriers"]) == before)
    check("ariza pending qoldi",
          fake.data["courier_requests"]["cou_bad"]["status"] == "pending")

    print("\n[1] Mavjud bo'lmagan ariza")
    check("None qaytdi", await db.approve_courier_request("yo-q") is None)

    print("\n[1] get_courier")
    found = await db.get_courier("555")
    check("topildi", found is not None and found["fullName"] == "Otabek Fayzullayev")
    check("id maydoni bor", found and found["id"] == "555")
    check("noma'lum chat_id -> None", await db.get_courier("999") is None)

    return _r.summary("Natija")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
