#!/usr/bin/env python3
"""ASOX Market Telegram Bot — lokal tekshiruv vositasi.

Telegram tokeni bo'lmasa ham botning HAQIQIY kodini ishga tushiradi:
ma'lumot qatlami (Firestore yoki xotiradagi namunalar), do'kon havolasi
imzosi va matn formatlash.

Ilgari bu fayl faqat qattiq yozilgan `print` larni chiqarardi va bironta
ham handler yoki `Database` metodini chaqirmasdi — ya'ni hech narsani
tekshirmasdi.

    python3 local_tester.py            # interaktiv menyu
    python3 local_tester.py --check    # interaktivsiz umumiy holat
    python3 tests/run_all.py           # to'liq regressiya to'plami
"""

import asyncio
import logging
import sys

from config import ADMIN_BOT_TOKEN, ADMIN_IDS, BOT_TOKEN, SHOP_LINK_SECRET
from database.db import _db_client, db
from utils.formatters import format_price, get_order_status_badge
from utils.security import make_shop_link_token
from utils.validators import normalize_phone

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

LINE = "=" * 62


def _status(ok: bool) -> str:
    return "✅" if ok else "❌"


async def show_config() -> None:
    print(f"\n{LINE}\n⚙️  KONFIGURATSIYA\n{LINE}")
    print(f"  {_status(bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'))} BOT_TOKEN")
    print(f"  {_status(bool(ADMIN_BOT_TOKEN))} ADMIN_BOT_TOKEN (bo'sh bo'lsa admin bot ishga tushmaydi)")
    admins = ", ".join(str(x) for x in ADMIN_IDS) or "bo'sh — admin panelga kirish yo'q"
    print(f"  {_status(bool(ADMIN_IDS))} ADMIN_IDS -> {admins}")
    print(f"  {_status(bool(SHOP_LINK_SECRET))} SHOP_LINK_SECRET (bo'sh bo'lsa do'kon ulash o'chiq)")
    print(f"  {_status(_db_client is not None)} Firestore "
          f"{'ulangan' if _db_client else 'ulanmagan — xotiradagi namunalar ishlatiladi'}")


async def show_catalog() -> None:
    print(f"\n{LINE}\n🛍  KATALOG (db.get_categories / get_products_by_category)\n{LINE}")
    categories = await db.get_categories()
    if not categories:
        print("  ❌ Kategoriya topilmadi.")
        return
    for cat in categories:
        products = await db.get_products_by_category(cat["id"])
        print(f"\n  {cat['icon']} {cat['name']}  ({len(products)} ta mahsulot)")
        for p in products[:5]:
            stock = "mavjud" if p["in_stock"] else "tugagan"
            print(f"     • {p['name']} — {format_price(p['price'])} [{stock}]")
            print(f"       https://asox.uz/app/product/{p['id']}")


async def run_search() -> None:
    query = input("\n🔍 Qidiruv so'zi: ").strip()
    if not query:
        return
    results = await db.search_products(query)
    print(f"\n  {len(results)} ta natija (db.search_products):")
    for p in results[:10]:
        print(f"     • {p['name']} — {format_price(p['price'])}")
    if not results:
        print("     (hech narsa topilmadi)")


async def show_orders() -> None:
    print(f"\n{LINE}\n📦 BUYURTMALAR (db.get_all_orders)\n{LINE}")
    orders = await db.get_all_orders()
    if not orders:
        print("  Buyurtmalar yo'q."
              + ("" if _db_client else "  (Firestore ulanmagan — sayt buyurtmalari ko'rinmaydi)"))
        return
    for o in orders[:10]:
        items = ", ".join(f"{i['name']} ({i['quantity']}x)" for i in o["items"]) or "—"
        print(f"\n  🆔 {o['id']}  {get_order_status_badge(o['status'])}")
        print(f"     👤 {o['user_name']}   📱 {o['phone_number']}")
        print(f"     💰 {format_price(o['total_amount'])}   📦 {items}")


async def make_shop_link() -> None:
    shop_id = input("\n🏪 Do'kon ID: ").strip() or "shop_samarkand_1"
    if not SHOP_LINK_SECRET:
        print("\n  ❌ SHOP_LINK_SECRET sozlanmagan — do'kon ulash o'chiq (fail-closed).")
        print("     Yaratish: python3 -c \"import secrets; print(secrets.token_hex(32))\"")
        return
    token = make_shop_link_token(shop_id, SHOP_LINK_SECRET)
    print("\n  ✅ Imzolangan havola (asox.uz shu shaklda generatsiya qilishi kerak):")
    print(f"     https://t.me/AsoxUz_Bot?start=shop_{shop_id}_{token}")


async def check_phone() -> None:
    raw = input("\n📱 Telefon raqami: ").strip()
    result = normalize_phone(raw)
    print(f"  {_status(result is not None)} {raw!r} -> {result!r}")


async def run_all_checks() -> None:
    await show_config()
    await show_catalog()
    await show_orders()
    print(f"\n{LINE}\n📱 TELEFON NORMALIZATSIYASI\n{LINE}")
    for raw in ("+998901234567", "998901234567", "901234567", "qwerty"):
        print(f"  {_status(normalize_phone(raw) is not None)} {raw!r} -> {normalize_phone(raw)!r}")
    print(f"\n{LINE}\nTo'liq regressiya to'plami:  python3 tests/run_all.py\n{LINE}")


MENU = {
    "1": ("⚙️  Konfiguratsiya holati", show_config),
    "2": ("🛍  Katalog va mahsulotlar", show_catalog),
    "3": ("🔍 Mahsulot qidirish", run_search),
    "4": ("📦 Buyurtmalar ro'yxati", show_orders),
    "5": ("🏪 Do'kon ulash havolasini yaratish", make_shop_link),
    "6": ("📱 Telefon raqamini tekshirish", check_phone),
    "7": ("🧪 Hammasini ketma-ket ishga tushirish", run_all_checks),
}


async def main() -> int:
    if "--check" in sys.argv:
        await run_all_checks()
        return 0

    while True:
        print(f"\n{LINE}\n🤖 ASOX MARKET BOT — LOKAL TEKSHIRUV\n{LINE}")
        for key, (label, _) in MENU.items():
            print(f"  {key}. {label}")
        print("  0. 🚪 Chiqish")
        choice = input("\nTanlov: ").strip()
        if choice == "0":
            print("\n👋 Xayr!")
            return 0
        entry = MENU.get(choice)
        if entry is None:
            print("\n❌ Noto'g'ri tanlov.")
            continue
        try:
            await entry[1]()
        except Exception as e:
            print(f"\n❌ Xatolik: {type(e).__name__}: {e}")
        input("\nDavom etish uchun [Enter]...")


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Xayr!")
        sys.exit(0)
