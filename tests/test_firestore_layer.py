"""Firestore yagona manba sifatida + event loop bloklanmasligi.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys
import time

from _harness import Results  # sys.path ni sozlaydi
from fake_firestore import FakeFirestore

import database.db as dbmod

_r = Results()
check = _r.check

SEED = {
    "orders": {
        # saytdan tushgan buyurtma — camelCase, telegramUserId yo'q
        "WEB-900": {"orderNumber": "WEB-900", "customerName": "Web Mijoz", "customerPhone": "+998901000000",
                    "totalAmount": 500000, "status": "pending", "createdAt": "2026-08-30 10:00",
                    "items": [{"name": "Roll-up", "quantity": 1, "price": 500000}]},
        # botdan tushgan buyurtma
        "ASOX-1001": {"orderNumber": "ASOX-1001", "telegramUserId": 555, "customerName": "Ali",
                      "customerPhone": "+998901112233", "totalAmount": 170000, "status": "delivered",
                      "createdAt": "2026-08-31 09:00",
                      "items": [{"name": "Kepka", "quantity": 2, "price": 85000}]},
    },
    "bot_users": {"555": {"telegramId": 555}, "777": {"telegramId": 777}, "888": {"telegramId": 888}},
    "shops": {"shop_a": {"name": "Samarqand Poligrafiya"},
              "shop_b": {"name": "Band do'kon", "telegramChatId": "111"}},
    "products": {"p1": {"name": "Futbolka", "effectivePrice": 120000, "category": "merch",
                        "isActive": True, "images": ["https://asox.uz/p1.jpg"]}},
    "categories": {"c1": {"name": "Kiyimlar", "isActive": True}},
}

async def main():
    fake = FakeFirestore(SEED)
    dbmod._db_client = fake
    db = dbmod.Database()

    print("\n[5] Admin bot SAYTDAN tushgan buyurtmalarni ko'radimi?")
    orders = await db.get_all_orders()
    ids = [o["id"] for o in orders]
    check("Firestore'dan o'qildi (xotira emas)", len(orders) == 2)
    check("saytdagi WEB-900 ko'rinadi", "WEB-900" in ids)
    check("yangi buyurtma birinchi (createdAt DESC)", ids[0] == "ASOX-1001")
    web = next(o for o in orders if o["id"] == "WEB-900")
    check("sayt buyurtmasi normallashgan (user_name)", web["user_name"] == "Web Mijoz")
    check("sayt buyurtmasi normallashgan (total_amount)", web["total_amount"] == 500000.0)
    check("statistika endi real summani beradi",
          sum(o["total_amount"] for o in orders if o["status"] == "delivered") == 170000.0)

    print("\n[5] Sayt buyurtmasining statusini o'zgartirib bo'ladimi?")
    check("update_order_status(WEB-900) -> True (ilgari False edi)",
          await db.update_order_status("WEB-900", "processing"))
    check("Firestore'da yozildi", fake.data["orders"]["WEB-900"]["status"] == "processing")
    check("mavjud bo'lmagan buyurtma -> False", not await db.update_order_status("YO-Q", "shipped"))
    check("get_order_by_id Firestore'dan o'qiydi",
          (await db.get_order_by_id("WEB-900"))["user_name"] == "Web Mijoz")
    check("bot endi buyurtma yaratmaydi (create_order olib tashlangan)",
          not hasattr(db, "create_order"))
    check("savat qatlami ham olib tashlangan", not hasattr(db, "get_cart"))

    print("\n[5] Broadcast auditoriyasi Firestore'danmi?")
    audience = sorted(await db.get_broadcast_user_ids())
    check("bot_users dan 3 ta ID (xotira bo'sh bo'lsa ham)", audience == [555, 777, 888])
    check("get_users_count() = 3", await db.get_users_count() == 3)

    print("\n[5] Admin qo'shgan mahsulot Firestore'ga tushadimi?")
    p = await db.add_product({"name": "Yangi krujka", "price": 45000,
                              "description": "Test", "category_id": "cat_souvenirs",
                              "image_url": "https://asox.uz/k.jpg"})
    check("Firestore ID berildi (prod_N emas)", not p["id"].startswith("prod_"))
    check("products kolleksiyasiga yozildi", p["id"] in fake.data["products"])
    check("isActive=True bilan yozildi", fake.data["products"][p["id"]]["isActive"] is True)
    check("effectivePrice ham yozildi", fake.data["products"][p["id"]]["effectivePrice"] == 45000.0)

    print("\n[2] Do'kon ulash (band do'kon himoyasi)")
    shop, err = await db.link_shop_telegram("shop_a", 999, "seller")
    check("bo'sh do'kon ulanadi", err is None and shop["id"] == "shop_a")
    check("Firestore'da telegramChatId yozildi", fake.data["shops"]["shop_a"]["telegramChatId"] == "999")
    _, err2 = await db.link_shop_telegram("shop_b", 999, "hujumchi")
    check("BAND do'kon o'zlashtirilmaydi -> already_linked", err2 == "already_linked")
    check("band do'kon chatId o'zgarmadi", fake.data["shops"]["shop_b"]["telegramChatId"] == "111")
    _, err3 = await db.link_shop_telegram("yoq_shop", 999, None)
    check("mavjud bo'lmagan do'kon -> not_found", err3 == "not_found")
    _, err4 = await db.link_shop_telegram("shop_a", 999, "seller")
    check("o'sha egasi qayta ulay oladi", err4 is None)

    print("\n[6] Event loop bloklanadimi? (har bir I/O = 120ms)")
    slow = FakeFirestore(SEED, block_ms=0.12)
    dbmod._db_client = slow
    db2 = dbmod.Database()
    ticks = 0
    async def heartbeat():
        nonlocal ticks
        while True:
            await asyncio.sleep(0.01)
            ticks += 1
    hb = asyncio.create_task(heartbeat())
    t0 = time.perf_counter()
    await asyncio.gather(db2.get_all_orders(), db2.get_categories(), db2.get_broadcast_user_ids())
    elapsed = time.perf_counter() - t0
    hb.cancel()
    print(f"     -> 3 ta sekin so'rov {elapsed*1000:.0f}ms; heartbeat {ticks} marta ishladi")
    check("so'rovlar parallel ketdi (~120ms, ketma-ket 360ms emas)", elapsed < 0.25)
    check("event loop bloklanmadi (heartbeat ishladi)", ticks >= 8)

    print("\n[6] `where()` eskirgan pozitsion shaklda emasmi?")
    check("FieldFilter ishlatilmoqda", dbmod._FieldFilter is not None)
    q = dbmod._where(slow.collection("products"), "isActive", "==", True)
    check("_where() natijasi filtrlaydi", len(q.stream()) == 1)

    return _r.summary("Natija")

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
