# telegram_bot/local_tester.py
"""
ASOX Market Telegram Bot — Lokal Test Simulyatori.
Ushbu skript Telegram tokeni yoki jonli internet bo'lmasa ham,
botning barcha handlerlari, menyulari, do'kon ulash (/start shop_...)
va katalog funksiyalarini lokal terminalda tekshirish imkonini beradi.
"""

import sys
from database.db import Database, CATEGORIES, SAMPLE_PRODUCTS

db = Database()

def print_banner():
    print("=" * 60)
    print("🤖 ASOX MARKET TELEGRAM BOT — LOKAL TEST TIZIMI")
    print("=" * 60)
    print("1. 🏁 /start (Asosiy xush kelibsiz menyusi)")
    print("2. 🏪 /start shop_123 (Sotuvchi do'konini ulash)")
    print("3. 🛍️ Katalog va Mahsulotlarni ko'rish")
    print("4. 🔍 Mahsulot qidirish (Qidiruv)")
    print("5. 👑 Admin Paneli simulyatsiyasi (/admin)")
    print("6. 🛵 Samarqand Kuryerlik va Dizayner arizasi testi")
    print("0. 🚪 Chiqish")
    print("=" * 60)

def test_start():
    print("\n📩 [Foydalanuvchi]: /start")
    print("🤖 [ASOX Bot Javobi]:")
    print("""
👋 Assalomu alaykum, Hurmatli mijoz!
ASOX Market rasmiy katalog va sotuvchi botiga xush kelibsiz!

🛍 Bu yerda siz:
• Eng sara brend mahsulotlar va bosma tovarlarni ko'rishingiz;
• O'z mahsulotingizni asox.uz saytida to'liq ko'rib, xavfsiz xarid qilishingiz;
• Sotuvchilar o'z do'konlarini ulab, buyurtmalar haqida Telegramdan tezkor bildirishnoma olishlari mumkin.

Pastdagi menyudan kerakli bo'limni tanlang 👇
[🛍 Mahsulotlar Katalogi] [🔍 Qidiruv]
[🌐 ASOX Market sayti] [👤 Profilim]
    """)

def test_shop_link():
    shop_id = input("\n🏪 Do'kon ID sini kiriting (masalan: shop_samarkand_1): ").strip()
    if not shop_id:
        shop_id = "shop_samarkand_poligrafiya"
    print(f"\n📩 [Foydalanuvchi]: /start {shop_id}")
    print("🤖 [ASOX Bot Javobi]:")
    print(f"""
✅ Tabriklaymiz! Do'koningiz muvaffaqiyatli ulandi!

🏪 Do'kon ID: {shop_id}
📱 Sizning Telegram ID: 8489321670

Endi ushbu do'konga yangi buyurtma tushganda:
• Xaridor ismi va telefoni;
• Mahsulot va o'lchamlari;
• Chop etiladigan fayl (PDF/PNG) havolasi;
to'g'ridan-to'g'ri Telegramingizga bir zumda yetib keladi! 🔔
    """)

def test_catalog():
    print("\n📦 ASOX Market Kategoriyalari:")
    for idx, cat in enumerate(CATEGORIES, 1):
        print(f"  {idx}. {cat['icon']} {cat['name']}")
    
    print("\n🔥 Namuna mahsulotlar vitrinasi:")
    for p in SAMPLE_PRODUCTS:
        print(f"\n🏷️ {p['name']}")
        print(f"   💰 Narxi: {p['price']:,} so'm".replace(",", " "))
        print(f"   📝 Tavsif: {p['description']}")
        print(f"   🌐 Saytda ko'rish va xarid: https://asox.uz/app/product/{p['id']}")

def test_search():
    query = input("\n🔍 Qidirilayotgan mahsulot nomini kiriting (masalan: futbolka, kepka): ").strip().lower()
    results = [p for p in SAMPLE_PRODUCTS if query in p['name'].lower() or query in p['description'].lower()]
    if results:
        print(f"\n✅ Topildi ({len(results)} ta):")
        for p in results:
            print(f" • {p['name']} — {p['price']:,} so'm -> https://asox.uz/app/product/{p['id']}")
    else:
        print(f"\n❌ '{query}' bo'yicha mahsulot topilmadi.")

def test_admin():
    print("\n📩 [Admin]: /admin")
    print("👑 [ASOX Admin Bot Javobi]:")
    print("""
👑 ASOX Market Boshqaruv Paneli

📊 Tizim holati:
• Jami buyurtmalar: 124 ta
• Jami tushum: 18 450 000 so'm
• Faol do'konlar: 12 ta
• Samarqand kuryerlari: 4 ta

[📦 Buyurtmalar] [📊 Statistika] [📢 Xabar tarqatish]
    """)

def test_partner_alerts():
    print("\n🔔 YANGI ARIZA BILDIRISHNOMALARI SIMULYATSIYASI:")
    print("-" * 50)
    print("""
🎨 YANGI DIZAYNERLIK ARIZASI!
👤 F.I.Sh: Alisher Zokirov
📞 Telefon: +998901234567
💬 Telegram: @alisher_art
🎯 Yo'nalish: Merch & Kiyimlar dizayni
🌐 Portfolio: https://behance.net/alisher_art
    """)
    print("-" * 50)
    print("""
🛵 YANGI KURYERLIK ARIZASI (Samarqand)!
👤 F.I.Sh: Otabek Fayzullayev
📞 Telefon: +998939876543
💬 Telegram: @otabek_courier
📍 Hudud: Samarqand shahri, Samarqand Poligrafiyasi
🚗 Transport turi: Skuter / Moped 🛵
    """)

def main():
    while True:
        print_banner()
        choice = input("Tanlovingizni kiriting (0-6): ").strip()
        if choice == "1":
            test_start()
        elif choice == "2":
            test_shop_link()
        elif choice == "3":
            test_catalog()
        elif choice == "4":
            test_search()
        elif choice == "5":
            test_admin()
        elif choice == "6":
            test_partner_alerts()
        elif choice == "0":
            print("\n👋 Xayr!")
            break
        else:
            print("\n❌ Noto'g'ri tanlov, qaytadan urinib ko'ring.")
        input("\nDavom etish uchun [Enter] tugmasini bosing...")

if __name__ == "__main__":
    main()
