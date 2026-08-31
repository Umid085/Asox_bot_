# 🤖 ASOX Market Telegram Boti

Ushbu bot **ASOX Market** e-commerce platformasi uchun yaratilgan rasmiy Telegram bot hisoblanadi. Bot orqali foydalanuvchilar mahsulotlarni ko'rishlari, savatga qo'shishlari, lokatsiya va telefon raqamlarini yuborib buyurtma berishlari hamda buyurtma holatini real vaqt rejimida kuzatib borishlari mumkin.

---

## 🛠 Imkoniyatlar va Funksionallik

### 👤 Mijozlar uchun:
* 🛍 **Mahsulotlar katalogi:** Kategoriyalar bo'yicha saralangan mahsulotlar ro'yxati (Rasm, Narx, Tavsif).
* 🔍 **Mahsulotlar qidiruvi:** Kalit so'zlar bo'yicha mahsulotlarni izlash.
* 🛒 **Interaktiv Savat (Cart):** Mahsulot miqdorini oshirish `➕`, kamaytirish `➖`, o'chirish `❌` va tozalash.
* 📦 **Buyurtma berish (Checkout):** 
  * Telefon raqamini ulashish (Telegram tugmasi yoki matn)
  * Yetkazib berish manzilini ulashish (Telegram Geolokatsiya yoki matn)
  * To'lov turini tanlash (Naqd pul, Click, Payme)
* 📦 **Mening Buyurtmalarim:** Buyurtmalar tarixi va ularning joriy holatini kuzatish (Yangi, Jarayonda, Yetkazilmoqda, Bajarildi, Bekor qilindi).
* 👤 **Foydalanuvchi profili va Qo'llab-quvvatlash (Support).**

### ⚙️ Adminlar uchun (Admin Panel):
* 📊 **Tizim statistikasi:** Jami foydalanuvchilar, buyurtmalar soni va jami tushum.
* 📦 **Buyurtmalarni boshqarish:** Yangi buyurtmalardan tezkor ogohlantirish (Notification) va holatini 1 bosishda o'zgartirish.
* ➕ **Yangi mahsulot qo'shish:** Bot orqali yangi mahsulot nomini, narxini va tavsifini kiritish.
* 📢 **Broadcast (Xabarnoma):** Barcha bot foydalanuvchilariga e'lon yoki aksiya xabarlarini yuborish.

---

## 🚀 Mahalliy kompyuterda ishga tushirish (Local Run)

### 1. Bot Tokenini olish:
1. Telegramda **[@BotFather](https://t.me/BotFather)** botiga kiring.
2. `/newbot` buyrug'ini yuboring va botingizga nom berib **API TOKEN** ni oling.
3. Telegram profil `ID` ingizni bilish uchun **[@userinfobot](https://t.me/userinfobot)** dan foydalaning.

### 2. .env faylini sozlash:
`telegram_bot` jildidagi `.env` faylini oching va ma'lumotlarni kiriting:
```env
BOT_TOKEN=7890123456:AAExampleTokenHere_ReplaceWithYourOwn
ADMIN_IDS=123456789
ENVIRONMENT=development
```

### 3. Kutubxonalarni o'rnatish va Ishga tushirish:
```bash
cd telegram_bot

# Virtual muhit yaratish va faollashtirish
python3 -m venv venv
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish (Polling rejimida)
python main.py
```

---

## 🌐 Serverda 24/7 Faol Ishlatish (Deployment Guide)

Botingiz kompyuteringiz o'chiq bo'lsa ham 24/7 uzluksiz ishlashi uchun quyidagi bepul/qulay server xizmatlaridan biriga joylashingiz mumkin:

### 1. Render.com (Tavsiya etiladi - Bepul va Qulay)
1. **[render.com](https://render.com)** saytida ro'yxatdan o'ting.
2. Github-ga loyihangizni yuklang.
3. Render-da **New > Web Service** yoki **Background Worker** tanlang.
4. Github reponizni ulaysiz:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. **Environment Variables** bo'limida `BOT_TOKEN` va `ADMIN_IDS` ni qo'shing.
6. Deploy tugmasini bosing! Botingiz 24/7 avtomatik ishlaydi.

### 2. Railway.app / Koyeb / VPS (Docker orqali)
Agar VPS (masalan Hetzner, DigitalOcean, Ubuntu server) ishlatayotgan bo'lsangiz, Docker yordamida 1 ta buyruq bilan ishga tushirishingiz mumkin:
```bash
docker-compose up -d --build
```

---

## 📁 Loyiha Tuzilishi

```
telegram_bot/
├── main.py              # Asosiy ishga tushirish fayli
├── config.py            # Konfiguratsiyalar va .env yuklash
├── database/            # Ma'lumotlar bazasi modullari va mahsulotlar
│   └── db.py
├── handlers/            # Botning barcha buyruq va menyu ishlovchilari
│   ├── start.py
│   ├── catalog.py
│   ├── cart.py
│   ├── checkout.py
│   ├── orders.py
│   └── admin.py
├── keyboards/           # Tugmalar va menyular (Reply va Inline)
│   ├── reply.py
│   └── inline.py
├── states/              # FSM holatlari (Checkout & Admin)
│   └── states.py
├── utils/               # Narxlarni formatlash va yordamchi funksiyalar
│   └── formatters.py
├── Dockerfile           # Docker konteyner fayli
├── docker-compose.yml   # Docker Compose sozlamalari
├── render.yaml          # Render.com avto-deploy hujjati
├── requirements.txt     # Python kutubxonalari ro'yxati
└── .env                 # Maxfiy kalitlar va sozlamalar
```
