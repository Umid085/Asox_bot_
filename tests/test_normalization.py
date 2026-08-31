"""Normalizatsiya, buyurtma sxemasi, do'kon havolasi imzosi va admin autentifikatsiyasi.

Ishga tushirish:  python3 tests/run_all.py
"""
import asyncio
import sys

from _harness import Results  # sys.path ni sozlaydi

import config
from database.db import Database, normalize_category, normalize_order, normalize_product
from keyboards.inline import get_categories_keyboard, get_products_keyboard
from utils.formatters import format_price, get_order_status_badge
from utils.security import make_shop_link_token, parse_shop_payload, verify_shop_link_token

_r = Results()
check = _r.check

async def main():
    print("\n[3] Buyurtma sxemasi — kalitlar mos keladimi?")
    db = Database()
    o = await db.create_order(555, "Ali Valiyev", "+998901112233", "Samarqand, Gagarin 60",
                              "💳 Payme", [{"product": {"name": "Kepka", "price": 85000}, "quantity": 2}], 170000)
    for k in ("total_amount", "user_name", "phone_number", "address", "payment_method", "created_at"):
        check(f"order['{k}'] mavjud", k in o)
    check("total_amount = 170000.0", o["total_amount"] == 170000.0)
    check("items tekis shaklda {name,quantity,price}", o["items"] == [{"name": "Kepka", "quantity": 2, "price": 85000.0}])
    check("Firestore camelCase saqlanib qolgan (totalAmount)", o.get("totalAmount") == 170000)

    print("\n[3] Handler ifodalari qulamaydimi?")
    all_orders = await db.get_all_orders()
    try:
        rev = sum(x.get("total_amount", 0) for x in all_orders if x.get("status") == "delivered")
        line = (f"{all_orders[0]['user_name']} {all_orders[0]['phone_number']} "
                f"{format_price(all_orders[0]['total_amount'])} "
                f"{get_order_status_badge(all_orders[0]['status'])}")
        summ = "".join(f"• {i.get('name')} ({i.get('quantity')}x)" for i in all_orders[0]["items"])
        check("admin/orders ifodalari ishlaydi", True)
        print(f"     -> {line} | {summ}")
    except Exception as e:
        check(f"admin/orders ifodalari ishlaydi ({type(e).__name__}: {e})", False)
    await db.update_order_status(o["id"], "delivered")
    orders2 = await db.get_all_orders()
    check("statistika 170 000 so'm ko'rsatadi (ilgari 0 edi)",
          sum(x.get("total_amount", 0) for x in orders2 if x.get("status") == "delivered") == 170000.0)

    print("\n[3] Saytdan (Firestore camelCase) kelgan buyurtma ham normallashadimi?")
    web = normalize_order({"orderNumber": "ASOX-2050", "telegramUserId": 777,
                           "customerName": "Dilnoza", "customerPhone": "+998935556677",
                           "totalAmount": 240000, "status": "processing",
                           "items": [{"name": "Banner", "quantity": 3, "price": 80000}]})
    check("id <- orderNumber", web["id"] == "ASOX-2050")
    check("user_name <- customerName", web["user_name"] == "Dilnoza")
    check("phone_number <- customerPhone", web["phone_number"] == "+998935556677")
    check("total_amount <- totalAmount", web["total_amount"] == 240000.0)

    print("\n[4] Firestore mahsuloti/kategoriyasi — KeyError yo'qmi?")
    fp = normalize_product({"name": "Futbolka", "effectivePrice": 120000,
                            "images": ["https://asox.uz/p/1.jpg"], "isActive": True}, "fsDoc123")
    for k in ("id", "category_id", "rating", "in_stock", "image_url", "description", "price"):
        check(f"product['{k}'] mavjud", k in fp)
    check("price <- effectivePrice", fp["price"] == 120000.0)
    check("image_url <- images[0]", fp["image_url"] == "https://asox.uz/p/1.jpg")
    try:
        get_categories_keyboard([normalize_category({"name": "Kiyimlar", "isActive": True}, "c1")])
        get_products_keyboard([fp], "c1")
        check("icon'siz kategoriya klaviaturasi qurildi", True)
    except Exception as e:
        check(f"icon'siz kategoriya klaviaturasi ({e})", False)
    # catalog.py detail ifodasi
    try:
        _ = (fp.get('name'), fp.get('description'), fp.get('rating'), fp.get('price'),
             fp.get('id'), fp.get('category_id'), fp.get('image_url'))
        check("catalog.py mahsulot detali ifodasi ishlaydi", True)
    except Exception as e:
        check(f"catalog.py detali ({e})", False)

    print("\n[2] Do'kon havolasi imzosi")
    SEC = "test_secret"
    sid = "shop_samarkand_1"
    tok = make_shop_link_token(sid, SEC)
    check("to'g'ri imzo qabul qilinadi", verify_shop_link_token(sid, tok, SEC))
    check("imzosiz havola RAD etiladi", not verify_shop_link_token(*parse_shop_payload(f"shop_{sid}"), SEC))
    check("boshqa do'kon imzosi RAD etiladi", not verify_shop_link_token("shop_boshqa", tok, SEC))
    check("buzilgan imzo RAD etiladi", not verify_shop_link_token(sid, tok[:-1] + "0", SEC))
    check("kalit yo'q -> RAD etiladi (fail-closed)", not verify_shop_link_token(sid, tok, ""))
    check("parse to'g'ri ajratadi", parse_shop_payload(f"shop_{sid}_{tok}") == (sid, tok))

    print("\n[2] Admin autentifikatsiyasi")
    config.ADMIN_IDS = [111]
    check("ADMIN_IDS dagi ID -> admin", config.is_admin_user(111, None))
    check("begona ID + admin username -> RAD", not config.is_admin_user(999, "shaxzod000001"))
    check("ADMIN_IDS o'zgarmadi (global mutatsiya yo'q)", config.ADMIN_IDS == [111])
    check("ADMIN_USERNAMES butunlay olib tashlangan", not hasattr(config, "ADMIN_USERNAMES"))

    return _r.summary("Natija")

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
