import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = "asox-market-prod-2e4bb"
DEFAULT_PRODUCT_IMAGE = "https://asox.uz/icons/icon-512x512.png"
DEFAULT_CATEGORY_ICON = "🛍"

# ADC (Application Default Credentials) qidiruvi GCP tashqarisida metadata
# serverga 3 marta urinib ~13 soniya kutadi. Shuning uchun uni faqat GCP
# muhitida yoki aniq so'ralganda ishlatamiz.
_GCP_ENV_HINTS = (
    "GOOGLE_APPLICATION_CREDENTIALS",  # ADC fayli aniq ko'rsatilgan
    "GOOGLE_CLOUD_PROJECT",
    "GCE_METADATA_HOST",
    "K_SERVICE",                       # Cloud Run
    "GAE_ENV",                         # App Engine
    "FUNCTION_TARGET",                 # Cloud Functions
)


class _NoCredentials(Exception):
    """Firebase credential umuman berilmagan — bu xato emas, kutilgan holat."""


def _adc_available() -> bool:
    """ADC ni sinab ko'rishga arziydimi?"""
    if os.getenv("FIREBASE_USE_ADC", "").strip().lower() in ("1", "true", "yes"):
        return True
    return any(os.getenv(name) for name in _GCP_ENV_HINTS)


def _load_firebase_credentials():
    """Service account'ni fayldan yoki to'g'ridan-to'g'ri env o'zgaruvchisidan oladi.

    Render/Railway kabi platformalarda fayl yuklash noqulay, shuning uchun
    `FIREBASE_SERVICE_ACCOUNT_JSON` orqali JSON ni bevosita berish mumkin.
    Ikkalasi ham bo'lmasa `None` qaytadi va ADC (Application Default
    Credentials) bo'yicha urinib ko'riladi.
    """
    from firebase_admin import credentials

    raw_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw_json:
        return credentials.Certificate(json.loads(raw_json)), "FIREBASE_SERVICE_ACCOUNT_JSON"

    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "").strip()
    if cred_path:
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"FIREBASE_SERVICE_ACCOUNT fayli topilmadi: {cred_path}")
        return credentials.Certificate(cred_path), f"fayl: {cred_path}"

    if _adc_available():
        return None, "Application Default Credentials"

    return None, None  # credential umuman yo'q


IN_MEMORY_NOTICE = (
    "Bot xotiradagi namuna ma'lumotlar bilan ishlaydi: sayt buyurtmalari "
    "ko'rinmaydi va restartda hamma narsa yo'qoladi."
)

# Optional Firebase Firestore integration
_db_client = None
try:
    import firebase_admin
    from firebase_admin import firestore

    if not firebase_admin._apps:
        _cred, _source = _load_firebase_credentials()
        if _source is None:
            raise _NoCredentials()
        if _cred is not None:
            firebase_admin.initialize_app(_cred, {"projectId": FIREBASE_PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": FIREBASE_PROJECT_ID})
        logger.info("Firebase credential manbai: %s", _source)
    _db_client = firestore.client()
    logger.info("✅ Firestore ulandi (project: %s)", FIREBASE_PROJECT_ID)
except _NoCredentials:
    logger.warning(
        "⚠️ Firebase credential sozlanmagan (FIREBASE_SERVICE_ACCOUNT_JSON yoki "
        "FIREBASE_SERVICE_ACCOUNT). %s", IN_MEMORY_NOTICE
    )
except Exception as _e:
    _db_client = None
    logger.warning("⚠️ Firestore ulanmadi: %s. %s", _e, IN_MEMORY_NOTICE)



try:  # firebase-admin >= 6.2 / google-cloud-firestore >= 2.11
    from google.cloud.firestore_v1.base_query import FieldFilter as _FieldFilter
except Exception:  # pragma: no cover - eski kutubxona versiyalari
    _FieldFilter = None


def _where(collection, field: str, op: str, value: Any):
    """`where()` ning eskirgan pozitsion shaklidan qochadi."""
    if _FieldFilter is not None:
        return collection.where(filter=_FieldFilter(field, op, value))
    return collection.where(field, op, value)


async def _in_thread(fn, *args, **kwargs):
    """Sinxron (bloklovchi) Firestore chaqiruvini alohida oqimda bajaradi.

    `firebase-admin` sinxron SDK — uni to'g'ridan-to'g'ri `async def` ichida
    chaqirish har bir so'rovda butun botni (ikkala pollingni ham) muzlatardi.
    """
    return await asyncio.to_thread(fn, *args, **kwargs)

# ----------------------------------------------------------------------------
# Normalizatsiya: Firestore hujjatlari va xotiradagi namunalar bir xil kalitlar
# to'plamiga keltiriladi, shunda handlerlar KeyError bilan qulamaydi.
# ----------------------------------------------------------------------------

def _first(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Berilgan kalitlardan birinchi bo'sh bo'lmaganini qaytaradi."""
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _format_created_at(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    if hasattr(value, "strftime"):
        try:
            return value.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    return ""


def normalize_category(data: dict[str, Any], doc_id: str | None = None) -> dict[str, Any]:
    """Kategoriyani `id` / `name` / `icon` kalitlari kafolatlangan holga keltiradi.

    Firestore hujjatlarida `icon` maydoni yo'q — ilgari bu
    `keyboards.inline.get_categories_keyboard()` da KeyError bilan qulardi.
    """
    data = dict(data or {})
    data["id"] = doc_id or _first(data, "id", default="")
    data["name"] = _first(data, "name", "title", default="Kategoriya")
    data["icon"] = _first(data, "icon", "emoji", default=DEFAULT_CATEGORY_ICON)
    return data


def normalize_product(
    data: dict[str, Any],
    doc_id: str | None = None,
    cat_id: str | None = None,
) -> dict[str, Any]:
    """Mahsulotni handlerlar kutadigan barcha kalitlar bilan to'ldiradi.

    Firestore `get_product_by_id()` ilgari `rating` va `category_id` ni
    qo'ymasdi — `handlers/catalog.py` da real mahsulot ochilganda KeyError
    yuz berardi.
    """
    data = dict(data or {})
    images = data.get("images") or []
    if not isinstance(images, list):
        images = []

    data["id"] = doc_id or _first(data, "id", default="")
    data["name"] = _first(data, "name", "title", default="Mahsulot")
    data["description"] = _first(data, "description", "shortDescription", default="")
    data["price"] = _to_float(_first(data, "effectivePrice", "price", default=0))
    data["image_url"] = _first(
        data, "image_url", default=(images[0] if images else None)
    ) or DEFAULT_PRODUCT_IMAGE
    data["category_id"] = cat_id or _first(data, "category_id", "category", default="")
    data["rating"] = _to_float(_first(data, "rating", "averageRating", default=0))
    in_stock = _first(data, "in_stock", "inStock", default=True)
    data["in_stock"] = bool(in_stock) if in_stock is not None else True
    return data


def normalize_order_item(item: dict[str, Any]) -> dict[str, Any]:
    """Buyurtma qatorini `{name, quantity, price}` ko'rinishiga keltiradi.

    Bot `{"product": {...}, "quantity": n}` yozadi, sayt esa tekis
    `{"name": ..., "price": ...}` yozadi — ikkalasi ham qo'llab-quvvatlanadi.
    """
    item = dict(item or {})
    product = item.get("product")
    if not isinstance(product, dict):
        product = {}
    name = _first(item, "name", "productName", "title") or _first(
        product, "name", "title", default="Mahsulot"
    )
    price = _first(item, "price", "unitPrice") or _first(
        product, "effectivePrice", "price", default=0
    )
    return {
        "name": str(name),
        "quantity": _to_int(_first(item, "quantity", "qty", default=1), 1),
        "price": _to_float(price),
    }


def normalize_order(raw: dict[str, Any]) -> dict[str, Any]:
    """Buyurtmani botning yagona (snake_case) sxemasiga keltiradi.

    `create_order()` Firestore uchun camelCase (`totalAmount`, `customerName`,
    `customerPhone`) yozadi, handlerlar esa `total_amount` / `user_name` /
    `phone_number` so'raydi — bu KeyError va "0 so'm" statistikaga olib kelardi.
    """
    raw = dict(raw or {})
    items = [normalize_order_item(i) for i in (raw.get("items") or [])]

    total = _first(raw, "total_amount", "totalAmount", "total")
    if total is None:
        total = sum(i["price"] * i["quantity"] for i in items)

    raw["id"] = _first(raw, "id", "orderNumber", default="")
    raw["user_id"] = _to_int(_first(raw, "user_id", "telegramUserId", default=0))
    raw["user_name"] = _first(raw, "user_name", "customerName", default="Noma'lum")
    raw["phone_number"] = _first(raw, "phone_number", "customerPhone", default="")
    raw["address"] = _first(raw, "address", "deliveryAddress", default="")
    raw["payment_method"] = _first(raw, "payment_method", "paymentMethod", default="")
    raw["items"] = items
    raw["total_amount"] = _to_float(total)
    raw["status"] = raw.get("status") or "pending"
    raw["created_at"] = _format_created_at(_first(raw, "created_at", "createdAt"))
    return raw


# ASOX Market Category presets
CATEGORIES = [
    {"id": "cat_merch", "name": "Kiyimlar & Merch (Futbolka, Kepka, Panama)", "icon": "👕"},
    {"id": "cat_poligraphy", "name": "Vizitkalar & Kichik Poligrafiya", "icon": "📇"},
    {"id": "cat_large_format", "name": "Keng formatli bosma (Banner, Roll-up)", "icon": "🖼️"},
    {"id": "cat_souvenirs", "name": "Suvenirlar (Krujka, Stiker, Ruchka)", "icon": "☕"},
    {"id": "cat_packaging", "name": "Qadoqlash & Sumkalar", "icon": "📦"},
]

SAMPLE_PRODUCTS = [
    {
        "id": "prod_kepka",
        "category_id": "cat_merch",
        "name": "Kepka ASOX Premium (Bosma bilan)",
        "description": "100% paxta, metall fiksator, yuqori sifatli DTF yoki kashta bosma.",
        "price": 85000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 4.9
    },
    {
        "id": "prod_panama",
        "category_id": "cat_merch",
        "name": "Panama ASOX Yozgi Merch",
        "description": "Qulay va zamonaviy yozgi bosh kiyim, brending uchun tayyor.",
        "price": 95000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 4.8
    },
    {
        "id": "prod_futbolka",
        "category_id": "cat_merch",
        "name": "Futbolka Oversize Premium",
        "description": "Kompakt penye paxta 240g, yuvilganda o'chmaydigan bosma.",
        "price": 120000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 5.0
    },
    {
        "id": "prod_vizitka",
        "category_id": "cat_poligraphy",
        "name": "Vizitkalar to'plami (100 dona)",
        "description": "350g bo'rli qog'oz, ikki tomonlama to'liq rangli bosma + mot laminatsiya.",
        "price": 60000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 4.9
    },
    {
        "id": "prod_banner",
        "category_id": "cat_large_format",
        "name": "Banner bosish (Frontlit 440g, 1 m²)",
        "description": "Tashqi reklama uchun yomg'ir va quyoshga chidamli banner bosma.",
        "price": 35000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 4.8
    },
    {
        "id": "prod_krujka",
        "category_id": "cat_souvenirs",
        "name": "Logotipli Keramika Krujka (330ml)",
        "description": "Sublimatsion sifatli bosma, idish yuvish mashinasiga chidamli.",
        "price": 45000,
        "image_url": "https://asox.uz/icons/icon-512x512.png",
        "in_stock": True,
        "rating": 4.9
    }
]

ORDERS_PAGE_SIZE = 50


class Database:
    """ASOX Market ma'lumotlar qatlami.

    Firestore ulangan bo'lsa — u yagona haqiqat manbai (single source of truth).
    Ulanmagan bo'lsa, bot xotiradagi namuna ma'lumotlar bilan ishlashda davom
    etadi, lekin bu holat endi logga aniq yozib qo'yiladi.

    Barcha Firestore chaqiruvlari `_in_thread()` orqali alohida oqimda
    bajariladi — event loop bloklanmaydi.
    """

    def __init__(self):
        self._categories: list[dict[str, Any]] = [normalize_category(c) for c in CATEGORIES]
        self._products: list[dict[str, Any]] = [normalize_product(p) for p in SAMPLE_PRODUCTS]
        self._users: dict[int, dict[str, Any]] = {}
        # Firestore ulanmagan holat uchun zaxira ro'yxat (sayt buyurtmalari emas)
        self._orders: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Kategoriyalar
    # ------------------------------------------------------------------
    def _sync_get_categories(self) -> list[dict[str, Any]]:
        docs = _where(_db_client.collection("categories"), "isActive", "==", True).stream()
        return [normalize_category(d.to_dict(), d.id) for d in docs]

    async def get_categories(self) -> list[dict[str, Any]]:
        if _db_client:
            try:
                cats = await _in_thread(self._sync_get_categories)
                if cats:
                    return cats
            except Exception as e:
                logger.warning("Kategoriyalarni Firestore'dan olishda xato: %s", e)
        return self._categories

    async def get_category_by_id(self, cat_id: str) -> dict[str, Any] | None:
        categories = await self.get_categories()
        for cat in categories:
            if cat["id"] == cat_id:
                return cat
        return None

    # ------------------------------------------------------------------
    # Mahsulotlar
    # ------------------------------------------------------------------
    def _sync_active_products(self, limit: int = 200) -> list[Any]:
        query = _where(_db_client.collection("products"), "isActive", "==", True).limit(limit)
        return list(query.stream())

    async def get_products_by_category(self, cat_id: str) -> list[dict[str, Any]]:
        if _db_client:
            try:
                docs = await _in_thread(self._sync_active_products)
                products = []
                cat_id_clean = cat_id.lower().replace("cat_", "")
                for d in docs:
                    data = d.to_dict() or {}
                    if data.get("isDeleted") is True:
                        continue
                    cat = (data.get("category") or "").lower()
                    if cat_id_clean in cat or cat_id == data.get("category"):
                        products.append(normalize_product(data, d.id, cat_id))
                if products:
                    return products
            except Exception as e:
                logger.warning("Mahsulotlarni Firestore'dan olishda xato: %s", e)
        return [p for p in self._products if p["category_id"] == cat_id]

    def _sync_get_product(self, product_id: str):
        return _db_client.collection("products").document(product_id).get()

    async def get_product_by_id(self, product_id: str) -> dict[str, Any] | None:
        if _db_client:
            try:
                doc = await _in_thread(self._sync_get_product, product_id)
                if doc.exists:
                    return normalize_product(doc.to_dict(), doc.id)
            except Exception as e:
                logger.warning("Mahsulot %s ni olishda xato: %s", product_id, e)
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    async def search_products(self, query: str) -> list[dict[str, Any]]:
        q = query.lower().strip()
        all_prods: list[dict[str, Any]] = []
        firestore_ok = False
        if _db_client:
            try:
                docs = await _in_thread(self._sync_active_products)
                for d in docs:
                    data = d.to_dict() or {}
                    if data.get("isDeleted") is True:
                        continue
                    all_prods.append(normalize_product(data, d.id))
                firestore_ok = True
            except Exception as e:
                logger.warning("Qidiruvda Firestore xatosi: %s", e)
        # Firestore ishlayotgan bo'lsa, namuna (demo) mahsulotlar aralashtirilmaydi
        if not firestore_ok:
            all_prods = list(self._products)
        return [
            p for p in all_prods
            if q in str(p.get("name", "")).lower() or q in str(p.get("description", "")).lower()
        ]

    def _sync_add_product(self, product: dict[str, Any]) -> str:
        doc_ref = _db_client.collection("products").document()
        doc_ref.set({
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "effectivePrice": product["price"],
            "category": product["category_id"],
            "images": [product["image_url"]] if product.get("image_url") else [],
            "isActive": True,
            "isDeleted": False,
            "source": "telegram_admin_bot",
            "createdAt": firestore.SERVER_TIMESTAMP,
        })
        return doc_ref.id

    async def add_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        """Yangi mahsulot qo'shadi. Firestore ulangan bo'lsa — saytda ham ko'rinadi."""
        product = normalize_product(product_data)
        product["rating"] = product.get("rating") or 5.0
        product["in_stock"] = True

        if _db_client:
            try:
                doc_id = await _in_thread(self._sync_add_product, product)
                product["id"] = doc_id
                logger.info("Yangi mahsulot Firestore'ga qo'shildi: %s", doc_id)
                return product
            except Exception as e:
                logger.error("Mahsulotni Firestore'ga yozib bo'lmadi: %s", e)

        async with self._lock:
            product["id"] = f"prod_{len(self._products) + 1}"
            self._products.append(product)
            return product

    # ------------------------------------------------------------------
    # Foydalanuvchilar
    # ------------------------------------------------------------------
    def _sync_touch_bot_user(self, user_id: int, username: str, full_name: str) -> None:
        _db_client.collection("bot_users").document(str(user_id)).set({
            "telegramId": user_id,
            "username": username or "",
            "fullName": full_name or "",
            "lastSeenAt": firestore.SERVER_TIMESTAMP,
        }, merge=True)

    async def get_or_create_user(self, user_id: int, username: str | None = None, full_name: str | None = None) -> dict[str, Any]:
        async with self._lock:
            if user_id not in self._users:
                self._users[user_id] = {
                    "id": user_id,
                    "username": username,
                    "full_name": full_name,
                    "phone_number": None,
                    "created_at": datetime.now().isoformat()
                }
            else:
                if username:
                    self._users[user_id]["username"] = username
                if full_name:
                    self._users[user_id]["full_name"] = full_name
            user = self._users[user_id]

        # Broadcast auditoriyasi: `bot_users` kolleksiyasi qayta ishga tushirishdan
        # keyin ham saqlanadi (xotiradagi ro'yxat esa yo'qoladi).
        if _db_client:
            try:
                await _in_thread(self._sync_touch_bot_user, user_id, username, full_name)
            except Exception as e:
                logger.warning("bot_users yozuvida xato (%s): %s", user_id, e)

        return user

    def _sync_bot_user_ids(self) -> list[int]:
        collection = _db_client.collection("bot_users")
        try:  # faqat hujjat ID lari kerak — trafikni tejaymiz
            docs = collection.select([]).stream()
        except Exception:
            docs = collection.stream()
        ids = []
        for d in docs:
            try:
                ids.append(int(d.id))
            except (TypeError, ValueError):
                continue
        return ids

    async def get_broadcast_user_ids(self) -> list[int]:
        """Xabar tarqatish auditoriyasi — Firestore `bot_users` dan.

        Ilgari bu `db._users` (xotira) dan olinardi va har qayta ishga
        tushirishdan keyin bo'shab qolardi.
        """
        if _db_client:
            try:
                ids = await _in_thread(self._sync_bot_user_ids)
                if ids:
                    return ids
            except Exception as e:
                logger.error("bot_users ro'yxatini olishda xato: %s", e)
        return list(self._users.keys())

    async def get_users_count(self) -> int:
        return len(await self.get_broadcast_user_ids())

    # ------------------------------------------------------------------
    # Buyurtmalar
    # ------------------------------------------------------------------
    def _sync_all_orders(self) -> list[dict[str, Any]]:
        docs = (
            _db_client.collection("orders")
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
            .limit(ORDERS_PAGE_SIZE)
            .stream()
        )
        return [normalize_order({**(d.to_dict() or {}), "id": d.id}) for d in docs]

    async def get_all_orders(self) -> list[dict[str, Any]]:
        """Barcha buyurtmalar — sayt orqali tushganlari ham shu yerda ko'rinadi."""
        if _db_client:
            try:
                orders = await _in_thread(self._sync_all_orders)
                if orders:
                    return orders
            except Exception as e:
                logger.warning("Buyurtmalar ro'yxatini olishda xato: %s", e)
        return [normalize_order(o) for o in reversed(self._orders)]

    def _sync_get_order(self, order_id: str):
        return _db_client.collection("orders").document(order_id).get()

    async def get_order_by_id(self, order_id: str) -> dict[str, Any] | None:
        if _db_client:
            try:
                doc = await _in_thread(self._sync_get_order, order_id)
                if doc.exists:
                    return normalize_order({**(doc.to_dict() or {}), "id": doc.id})
            except Exception as e:
                logger.warning("Buyurtma %s ni olishda xato: %s", order_id, e)
        for o in self._orders:
            if o.get("id") == order_id:
                return normalize_order(o)
        return None

    def _sync_update_order_status(self, order_id: str, new_status: str) -> bool:
        doc_ref = _db_client.collection("orders").document(order_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.update({"status": new_status, "updatedAt": firestore.SERVER_TIMESTAMP})
        return True

    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Statusni yangilaydi — sayt orqali tushgan buyurtmalar uchun ham ishlaydi."""
        updated = False
        if _db_client:
            try:
                updated = await _in_thread(self._sync_update_order_status, order_id, new_status)
            except Exception as e:
                logger.error("Buyurtma %s statusini yangilashda xato: %s", order_id, e)

        async with self._lock:
            for o in self._orders:
                if o.get("id") == order_id:
                    o["status"] = new_status
                    updated = True
                    break
        return updated

    # ------------------------------------------------------------------
    # Do'konlar
    # ------------------------------------------------------------------
    def _sync_link_shop(
        self, shop_id: str, telegram_chat_id: int, telegram_username: str | None
    ) -> tuple[dict[str, Any] | None, str | None]:
        doc_ref = _db_client.collection("shops").document(shop_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None, "not_found"

        data = doc.to_dict() or {}
        existing = str(data.get("telegramChatId") or "").strip()
        if existing and existing != str(telegram_chat_id):
            logger.warning(
                "Do'kon %s allaqachon %s chatiga bog'langan; %s so'rovi rad etildi",
                shop_id, existing, telegram_chat_id,
            )
            return None, "already_linked"

        doc_ref.update({
            "telegramChatId": str(telegram_chat_id),
            "telegramUsername": telegram_username or "",
            "telegramLinkedAt": firestore.SERVER_TIMESTAMP
        })
        data["id"] = doc.id
        data["telegramChatId"] = str(telegram_chat_id)
        return data, None

    async def link_shop_telegram(
        self,
        shop_id: str,
        telegram_chat_id: int,
        telegram_username: str | None = None,
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Do'konni Telegram chatiga bog'laydi.

        `(shop, error_code)` qaytaradi. `error_code`:
        `no_db` | `not_found` | `already_linked` | `error` | `None` (muvaffaqiyat).

        Do'kon allaqachon BOSHQA chatga bog'langan bo'lsa, qayta yozishga yo'l
        qo'yilmaydi — aks holda imzolangan havola sizib chiqsa ham do'konning
        bildirishnomalarini o'zlashtirib olish mumkin bo'lardi.
        """
        if not _db_client:
            return None, "no_db"
        try:
            return await _in_thread(
                self._sync_link_shop, shop_id, telegram_chat_id, telegram_username
            )
        except Exception as e:
            logger.error("Do'kon %s ni ulashda xato: %s", shop_id, e)
            return None, "error"

    # ------------------------------------------------------------------
    # Dizayner / kuryer arizalari
    # ------------------------------------------------------------------
    def _sync_requests(self, collection: str, limit: int = 20) -> list[dict[str, Any]]:
        docs = (
            _db_client.collection(collection)
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [{**(d.to_dict() or {}), "id": d.id} for d in docs]

    async def get_designer_requests(self) -> list[dict[str, Any]]:
        if _db_client:
            try:
                return await _in_thread(self._sync_requests, "designer_requests")
            except Exception as e:
                logger.error("Dizayner arizalarini olishda xato: %s", e)
        return []

    async def get_courier_requests(self) -> list[dict[str, Any]]:
        if _db_client:
            try:
                return await _in_thread(self._sync_requests, "courier_requests")
            except Exception as e:
                logger.error("Kuryer arizalarini olishda xato: %s", e)
        return []

    def _sync_update_request(self, collection: str, req_id: str, new_status: str) -> None:
        _db_client.collection(collection).document(req_id).update({
            "status": new_status,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

    async def update_designer_request_status(self, req_id: str, new_status: str) -> bool:
        if _db_client:
            try:
                await _in_thread(self._sync_update_request, "designer_requests", req_id, new_status)
                return True
            except Exception as e:
                logger.error("Dizayner arizasi %s ni yangilashda xato: %s", req_id, e)
        return False

    async def update_courier_request_status(self, req_id: str, new_status: str) -> bool:
        if _db_client:
            try:
                await _in_thread(self._sync_update_request, "courier_requests", req_id, new_status)
                return True
            except Exception as e:
                logger.error("Kuryer arizasi %s ni yangilashda xato: %s", req_id, e)
        return False

    def _sync_add_request(self, collection: str, req_id: str, data: dict[str, Any]) -> None:
        _db_client.collection(collection).document(req_id).set({
            **data,
            "status": "pending",
            "createdAt": firestore.SERVER_TIMESTAMP
        })

    async def add_designer_request(self, data: dict[str, Any]) -> tuple[str, bool]:
        """`(req_id, firestore_ga_yozildi)` qaytaradi.

        Ikkinchi qiymat MUHIM: yozuv muvaffaqiyatli bo'lsa Cloud Functions
        (`onDesignerRequestCreated`) adminlarga xabar yuboradi va bot
        qo'shimcha xabar yubormasligi kerak — aks holda admin bitta arizani
        IKKI marta oladi. Yozilmagan bo'lsa esa CF umuman ishga tushmaydi va
        ariza izsiz yo'qoladi, shuning uchun bot zaxira xabar yuboradi.
        """
        req_id = f"des_{int(datetime.now().timestamp())}_{uuid4().hex[:6]}"
        if not _db_client:
            logger.warning(
                "Dizayner arizasi %s Firestore'ga yozilmadi: ulanish yo'q", req_id
            )
            return req_id, False
        try:
            await _in_thread(self._sync_add_request, "designer_requests", req_id, data)
            return req_id, True
        except Exception as e:
            logger.error("Dizayner arizasini yaratishda xato: %s", e)
            return req_id, False

    async def add_courier_request(self, data: dict[str, Any]) -> tuple[str, bool]:
        """`(req_id, firestore_ga_yozildi)` qaytaradi.

        Ikkinchi qiymat MUHIM: yozuv muvaffaqiyatli bo'lsa Cloud Functions
        (`onCourierRequestCreated`) adminlarga xabar yuboradi va bot
        qo'shimcha xabar yubormasligi kerak — aks holda admin bitta arizani
        IKKI marta oladi. Yozilmagan bo'lsa esa CF umuman ishga tushmaydi va
        ariza izsiz yo'qoladi, shuning uchun bot zaxira xabar yuboradi.
        """
        req_id = f"cou_{int(datetime.now().timestamp())}_{uuid4().hex[:6]}"
        if not _db_client:
            logger.warning(
                "Kuryer arizasi %s Firestore'ga yozilmadi: ulanish yo'q", req_id
            )
            return req_id, False
        try:
            await _in_thread(self._sync_add_request, "courier_requests", req_id, data)
            return req_id, True
        except Exception as e:
            logger.error("Kuryer arizasini yaratishda xato: %s", e)
            return req_id, False



    # ------------------------------------------------------------------
    # Kuryerlar
    # ------------------------------------------------------------------
    # Hujjat ID si sifatida kuryerning Telegram chat ID si ishlatiladi:
    # bitta Telegram akkaunt = bitta kuryer, shu sababli takroriy tasdiqlash
    # yangi hujjat yaratmaydi, va callback kelganda couriers/{from_user.id}
    # bo'yicha to'g'ridan-to'g'ri topiladi — qidiruv so'rovi kerak emas.

    def _sync_get_doc(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        snap = _db_client.collection(collection).document(doc_id).get()
        if not snap.exists:
            return None
        return {**(snap.to_dict() or {}), "id": snap.id}

    def _sync_create_courier(self, courier_id: str, data: dict[str, Any]) -> None:
        # Qayta tasdiqlashda ish tarixi yo'qolmasligi kerak: mavjud hujjatning
        # activeOrderId va completedCount qiymatlari saqlanadi, createdAt esa
        # qaytadan yozilmaydi.
        doc_ref = _db_client.collection("couriers").document(courier_id)
        existing = doc_ref.get()
        base = {
            "isActive": True,
            "activeOrderId": None,
            "completedCount": 0,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
        if existing.exists:
            current = existing.to_dict() or {}
            base["activeOrderId"] = current.get("activeOrderId")
            base["completedCount"] = current.get("completedCount", 0)
            base.pop("createdAt")
        doc_ref.set({**data, **base}, merge=True)

    async def approve_courier_request(self, req_id: str) -> dict[str, Any] | None:
        """Arizani kuryerga aylantiradi.

        Tartib MUHIM: avval `couriers` hujjati yaratiladi, keyingina ariza
        statusi `approved` ga o'tadi. Teskarisi bo'lsa hujjat yaratilmay
        qolganda ariza "tasdiqlangan" ko'rinib turardi, kuryer esa hech
        qachon zakas olmasdi — jimgina yo'qoladigan xatoning aynan o'zi.

        Yaratilgan kuryerni (`id` maydoni bilan) yoki `None` qaytaradi.
        """
        if not _db_client:
            logger.warning("Kuryer arizasi %s tasdiqlanmadi: Firestore yo'q", req_id)
            return None
        try:
            req = await _in_thread(self._sync_get_doc, "courier_requests", req_id)
            if not req:
                logger.warning("Kuryer arizasi %s topilmadi", req_id)
                return None

            # `userId` — arizani topshirgan Telegram foydalanuvchi ID si
            # (handlers/start.py:550 da yoziladi). Usiz kuryerga xabar
            # yuborib bo'lmaydi, demak hujjat ham yaratilmaydi.
            chat_id = str(req.get("userId") or "").strip()
            if not chat_id:
                logger.error(
                    "Kuryer arizasi %s da userId yo'q — hujjat yaratilmadi", req_id
                )
                return None

            courier = {
                "fullName": req.get("fullName") or "Kuryer",
                "phoneNumber": req.get("phoneNumber") or "",
                "telegramChatId": chat_id,
                "telegramUsername": req.get("telegramUsername") or "",
                "vehicle": req.get("vehicle") or "",
                "city": req.get("city") or "",
                "requestId": req_id,
            }
            await _in_thread(self._sync_create_courier, chat_id, courier)
            await _in_thread(
                self._sync_update_request, "courier_requests", req_id, "approved"
            )
            return {**courier, "id": chat_id}
        except Exception as e:
            logger.error("Kuryer arizasi %s ni tasdiqlashda xato: %s", req_id, e)
            return None

    async def get_courier(self, chat_id: str | int) -> dict[str, Any] | None:
        if not _db_client:
            return None
        try:
            return await _in_thread(self._sync_get_doc, "couriers", str(chat_id))
        except Exception as e:
            logger.error("Kuryer %s ni olishda xato: %s", chat_id, e)
            return None


# Global database instance
db = Database()
