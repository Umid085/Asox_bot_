# 🤖 ASOX Market Telegram Boti

Ushbu bot **ASOX Market** e-commerce platformasi uchun yaratilgan rasmiy Telegram bot hisoblanadi. Bot orqali foydalanuvchilar mahsulotlarni ko'rishlari, savatga qo'shishlari, lokatsiya va telefon raqamlarini yuborib buyurtma berishlari hamda buyurtma holatini real vaqt rejimida kuzatib borishlari mumkin.

---

## 🛠 Imkoniyatlar va Funksionallik

### 👤 Mijozlar uchun:
* 🛍 **Mahsulotlar katalogi:** Kategoriyalar bo'yicha saralangan mahsulotlar ro'yxati (Rasm, Narx, Tavsif).
* 🔍 **Mahsulotlar qidiruvi:** Kalit so'zlar bo'yicha mahsulotlarni izlash.
* 🛒 **Xarid:** savat, to'lov va buyurtma berish to'liq [asox.uz](https://asox.uz/app) saytida amalga oshiriladi — bot foydalanuvchini o'sha yerga yo'naltiradi.
* 🎨 **Dizayner bo'lish arizasi:** ism, telefon, yo'nalish va portfolio havolasi.
* 🛵 **Kuryer bo'lish arizasi:** ism, telefon, hudud va transport turi.
* 🏪 **Sotuvchi do'konini ulash:** imzolangan `/start shop_<id>_<imzo>` havolasi orqali; ulangach do'konga tushgan buyurtmalar Telegramga keladi.
* 👤 **Foydalanuvchi profili va Qo'llab-quvvatlash (Support).**

### ⚙️ Adminlar uchun (Admin Panel):
* 📊 **Tizim statistikasi:** Jami foydalanuvchilar, buyurtmalar soni va jami tushum.
* 📦 **Buyurtmalarni boshqarish:** Sayt va bot orqali tushgan barcha buyurtmalar ro'yxati; holatini 1 bosishda o'zgartirish.
* 🎨🛵 **Dizayner va kuryer arizalarini** ko'rish, tasdiqlash yoki rad etish.
* ➕ **Yangi mahsulot qo'shish:** Bot orqali yangi mahsulot nomini, narxini va tavsifini kiritish.
* 📢 **Broadcast (Xabarnoma):** Barcha bot foydalanuvchilariga e'lon yoki aksiya xabarlarini yuborish.

---

## 🚀 Mahalliy kompyuterda ishga tushirish (Local Run)

### 1. Bot Tokenini olish:
1. Telegramda **[@BotFather](https://t.me/BotFather)** botiga kiring.
2. `/newbot` buyrug'ini yuboring va botingizga nom berib **API TOKEN** ni oling.
3. Telegram profil `ID` ingizni bilish uchun **[@userinfobot](https://t.me/userinfobot)** dan foydalaning.

### 2. .env faylini sozlash:
`cp .env.example .env` qiling va qiymatlarni to'ldiring:
```env
BOT_TOKEN=7890123456:AAExampleTokenHere_ReplaceWithYourOwn
ADMIN_IDS=123456789
SHOP_LINK_SECRET=<python3 -c "import secrets; print(secrets.token_hex(32))">
ADMIN_BOT_TOKEN=            # ixtiyoriy: alohida admin bot
FIREBASE_SERVICE_ACCOUNT=   # ixtiyoriy: service account fayli yo'li
ENVIRONMENT=development
```

> ⚠️ **`SHOP_LINK_SECRET` majburiy.** Do'kon ulash havolalari HMAC bilan
> imzolanadi va bu kalit asox.uz backendidagi bilan **bir xil** bo'lishi shart.
> Kalit bo'lmasa do'kon ulash butunlay o'chadi (fail-closed) — imzosiz havola
> orqali begona odam do'kon bildirishnomalarini o'zlashtira olmasin.
>
> Sayt havolani shunday yaratadi:
> ```js
> const sig = crypto.createHmac('sha256', process.env.SHOP_LINK_SECRET)
>                   .update(`shop:${shopId}`).digest('hex').slice(0, 16);
> const link = `https://t.me/AsoxUz_Bot?start=shop_${shopId}_${sig}`;
> ```

### 2.1. Tokensiz lokal tekshirish:
```bash
python3 local_tester.py --check   # konfiguratsiya, katalog, buyurtmalar
python3 tests/run_all.py          # to'liq regressiya to'plami
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
5. **Environment Variables** bo'limida quyidagilarni qo'shing
   (to'liq ro'yxat `render.yaml` da):
   - `BOT_TOKEN`, `ADMIN_IDS`, `SHOP_LINK_SECRET` — majburiy
   - `ADMIN_BOT_TOKEN` — admin boti uchun (bo'lmasa u ishga tushmaydi)
   - `FIREBASE_SERVICE_ACCOUNT_JSON` — service account JSON ini **to'liq matn**
     sifatida (Render'da fayl yuklash noqulay). Bo'lmasa bot xotiradagi namuna
     ma'lumotlar bilan ishlaydi va restartda hammasi yo'qoladi.
6. Deploy tugmasini bosing! Botingiz 24/7 avtomatik ishlaydi.

> Bot **long-polling** rejimida ishlaydi — webhook qo'llab-quvvatlanmaydi.
> `PORT` dagi HTTP server faqat health-check uchun.

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
│   ├── admin.py
│   └── errors.py        # Global xatolik ushlagichi
├── keyboards/           # Tugmalar va menyular (Reply va Inline)
│   ├── reply.py
│   └── inline.py
├── states/              # FSM holatlari (Admin & arizalar)
│   └── states.py
├── middlewares/         # Anti-spam (throttling)
│   └── throttling.py
├── utils/               # Yordamchi funksiyalar
│   ├── formatters.py    # Narx, status va HTML escaping
│   ├── security.py      # Do'kon havolasi HMAC imzosi
│   └── validators.py    # Matn va telefon tekshiruvi
├── tests/               # Regressiya testlari (python3 tests/run_all.py)
├── Dockerfile           # Docker konteyner fayli
├── docker-compose.yml   # Docker Compose sozlamalari
├── render.yaml          # Render.com avto-deploy hujjati
├── requirements.txt     # Python kutubxonalari ro'yxati
└── .env                 # Maxfiy kalitlar va sozlamalar
```
