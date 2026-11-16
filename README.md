# ASOX Market (Android)

**ASOX Market** — maxsus bosma, merch va poligrafiya mahsulotlari platformasining Kotlin va Jetpack Compose asosidagi Android ilovasi.

## Imkoniyatlar

### Mijozlar uchun
- **Mahsulotlar katalogi:** Kategoriyalar bo'yicha saralash (`Kiyimlar & Merch`, `Vizitkalar & Poligrafiya`, `Keng formatli bosma`, `Suvenirlar`, `Qadoqlash`), real vaqtda qidiruv va batafsil mahsulot sahifasi.
- **Xarid oqimi:** Mahsulotlarni tanlash va [asox.uz/app](https://asox.uz/app) rasmiy veb-platformasiga xavfsiz yo'naltirish.
- **Hamkorlik arizalari:**
  - **Dizayner bo'lish:** Ism-familiya, `+998...` formatidagi telefon raqam tekshiruvi, dizayn yo'nalishi va portfolio havolasi.
  - **Kuryer bo'lish:** Ism-familiya, telefon raqami, yetkazib berish hududi va transport turi.
- **Sotuvchi do'konini ulash:** `shop_<id>_<imzo>` havolalarini HMAC-SHA256 imzo bilan tekshirish (fail-closed xavfsizlik modeli).
- **Profil va Qo'llab-quvvatlash:** Foydalanuvchi profilini tahrirlash va Samarqanddagi qo'llab-quvvatlash xizmati bilan tezkor aloqa.

### Adminlar uchun
- **Tizim statistikasi:** Foydalanuvchilar soni, jami buyurtmalar va bajarilgan buyurtmalar tushumi.
- **Buyurtmalarni boshqarish:** Buyurtma tafsilotlari va holatini 1 bosishda yangilash (`pending`, `processing`, `shipped`, `delivered`, `cancelled`).
- **Arizalarni ko'rib chiqish:** Dizayner va kuryer arizalarini tasdiqlash yoki rad etish.
- **Yangi mahsulot qo'shish:** Katalogga bevosita yangi mahsulot qo'shish.
- **Xabar tarqatish (Broadcast):** Ro'yxatdan o'tgan foydalanuvchilarga e'lon yuborish va tarixni ko'rish.

## Texnologiyalar
- **UI:** Kotlin, Jetpack Compose, Material Design 3, adaptive `NavigationBar` / `NavigationRail`
- **Arxitektura:** MVVM (`ViewModel` + `StateFlow`), Repository Pattern, Type-safe Navigation Compose
- **Ma'lumotlar bazasi:** Room (SQLite) + KSP
- **Konfiguratsiya:** `.env` / `.env.example` orqali `SHOP_LINK_SECRET` va `ADMIN_IDS` (`BuildConfig`)

## Qurish va Testlar

```bash
gradle assembleDebug
gradle :app:testDebugUnitTest
```
