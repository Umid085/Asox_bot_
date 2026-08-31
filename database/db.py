import logging
import os
import asyncio
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = "asox-market-prod-2e4bb"
DEFAULT_PRODUCT_IMAGE = "https://asox.uz/icons/icon-512x512.png"
DEFAULT_CATEGORY_ICON = "🛍"

# Optional Firebase Firestore integration
_db_client = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": FIREBASE_PROJECT_ID})
    _db_client = firestore.client()
    logger.info("✅ Firestore ulandi (project: %s)", FIREBASE_PROJECT_ID)
except Exception as _e:
    _db_client = None
    logger.warning(
        "⚠️ Firestore ulanmadi (%s) — bot xotiradagi namuna ma'lumotlar bilan ishlaydi. "
        "FIREBASE_SERVICE_ACCOUNT ni tekshiring.", _e
    )


# ----------------------------------------------------------------------------
# Normalizatsiya: Firestore hujjatlari va xotiradagi namunalar bir xil kalitlar
# to'plamiga keltiriladi, shunda handlerlar KeyError bilan qulamaydi.
# ----------------------------------------------------------------------------

def _first(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
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


def normalize_category(data: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
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
    data: Dict[str, Any],
    doc_id: Optional[str] = None,
    cat_id: Optional[str] = None,
) -> Dict[str, Any]:
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


def normalize_order_item(item: Dict[str, Any]) -> Dict[str, Any]:
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


def normalize_order(raw: Dict[str, Any]) -> Dict[str, Any]:
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
    {"id": "cat_merch", "name": "👕 Kiyimlar & Merch (Futbolka, Kepka, Panama)", "icon": "👕"},
    {"id": "cat_poligraphy", "name": "📇 Vizitkalar & Kichik Poligrafiya", "icon": "📇"},
    {"id": "cat_large_format", "name": "🖼️ Keng formatli bosma (Banner, Roll-up)", "icon": "🖼️"},
    {"id": "cat_souvenirs", "name": "☕ Suvenirlar (Krujka, Stiker, Ruchka)", "icon": "☕"},
    {"id": "cat_packaging", "name": "📦 Qadoqlash & Sumkalar", "icon": "📦"},
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

class Database:
    def __init__(self):
        self._categories: List[Dict[str, Any]] = [normalize_category(c) for c in CATEGORIES]
        self._products: List[Dict[str, Any]] = [normalize_product(p) for p in SAMPLE_PRODUCTS]
        self._users: Dict[int, Dict[str, Any]] = {}
        self._carts: Dict[int, List[Dict[str, Any]]] = {} # user_id -> [{product_id, quantity}]
        self._orders: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def get_categories(self) -> List[Dict[str, Any]]:
        if _db_client:
            try:
                cats = []
                docs = _db_client.collection("categories").where("isActive", "==", True).stream()
                for d in docs:
                    cats.append(normalize_category(d.to_dict(), d.id))
                if cats:
                    return cats
            except Exception as e:
                logger.warning("Kategoriyalarni Firestore'dan olishda xato: %s", e)
        return self._categories

    async def get_category_by_id(self, cat_id: str) -> Optional[Dict[str, Any]]:
        categories = await self.get_categories()
        for cat in categories:
            if cat["id"] == cat_id:
                return cat
        return None

    async def get_products_by_category(self, cat_id: str) -> List[Dict[str, Any]]:
        if _db_client:
            try:
                products = []
                docs = _db_client.collection("products").where("isActive", "==", True).limit(50).stream()
                for d in docs:
                    data = d.to_dict() or {}
                    if data.get("isDeleted") is True:
                        continue
                    cat = (data.get("category") or "").lower()
                    cat_id_clean = cat_id.lower().replace("cat_", "")
                    if cat_id_clean in cat or cat_id == data.get("category"):
                        products.append(normalize_product(data, d.id, cat_id))
                if products:
                    return products
            except Exception as e:
                logger.warning("Mahsulotlarni Firestore'dan olishda xato: %s", e)
        return [p for p in self._products if p["category_id"] == cat_id]

    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        if _db_client:
            try:
                doc = _db_client.collection("products").document(product_id).get()
                if doc.exists:
                    return normalize_product(doc.to_dict(), doc.id)
            except Exception as e:
                logger.warning("Mahsulot %s ni olishda xato: %s", product_id, e)
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        all_prods: List[Dict[str, Any]] = []
        firestore_ok = False
        if _db_client:
            try:
                docs = _db_client.collection("products").where("isActive", "==", True).limit(50).stream()
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

    async def add_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            product_id = f"prod_{len(self._products) + 1}"
            product = normalize_product(product_data, product_id)
            product["rating"] = product.get("rating") or 5.0
            product["in_stock"] = True
            self._products.append(product)
            return product

    # User Management
    async def get_or_create_user(self, user_id: int, username: Optional[str] = None, full_name: Optional[str] = None) -> Dict[str, Any]:
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

            # Broadcast auditoriyasi: admin bot shu ro'yxatga e'lon yuboradi
            if _db_client:
                try:
                    _db_client.collection("bot_users").document(str(user_id)).set({
                        "telegramId": user_id,
                        "username": username or "",
                        "fullName": full_name or "",
                        "lastSeenAt": firestore.SERVER_TIMESTAMP,
                    }, merge=True)
                except Exception as e:
                    logger.warning("bot_users yozuvida xato (%s): %s", user_id, e)

            return self._users[user_id]

    async def update_user_phone(self, user_id: int, phone: str):
        async with self._lock:
            if user_id in self._users:
                self._users[user_id]["phone_number"] = phone

    async def get_users_count(self) -> int:
        return len(self._users)

    # Cart Management
    async def get_cart(self, user_id: int) -> List[Dict[str, Any]]:
        async with self._lock:
            items = self._carts.get(user_id, [])
            result = []
            for item in items:
                prod = await self.get_product_by_id(item["product_id"])
                if prod:
                    result.append({
                        "product": prod,
                        "quantity": item["quantity"]
                    })
            return result

    async def add_to_cart(self, user_id: int, product_id: str, quantity: int = 1):
        async with self._lock:
            if user_id not in self._carts:
                self._carts[user_id] = []

            cart = self._carts[user_id]
            for item in cart:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    return
            cart.append({"product_id": product_id, "quantity": quantity})

    async def update_cart_quantity(self, user_id: int, product_id: str, quantity: int):
        async with self._lock:
            if user_id not in self._carts:
                return
            cart = self._carts[user_id]
            if quantity <= 0:
                self._carts[user_id] = [i for i in cart if i["product_id"] != product_id]
            else:
                for item in cart:
                    if item["product_id"] == product_id:
                        item["quantity"] = quantity
                        break

    async def clear_cart(self, user_id: int):
        async with self._lock:
            self._carts[user_id] = []

    # Order Management
    async def create_order(
        self,
        user_id: int,
        user_name: str,
        phone_number: str,
        address_or_location: str,
        payment_method: str,
        cart_items: List[Dict[str, Any]],
        total_amount: float
    ) -> Dict[str, Any]:
        async with self._lock:
            order_id = f"ASOX-{len(self._orders) + 1001}"
            items = [normalize_order_item(i) for i in cart_items]

            # Firestore (sayt) sxemasi — camelCase maydonlar saqlanib qoladi
            firestore_payload = {
                "id": order_id,
                "orderNumber": order_id,
                "userId": f"tg_{user_id}",
                "telegramUserId": user_id,
                "customerName": user_name,
                "customerPhone": phone_number,
                "address": address_or_location,
                "paymentMethod": payment_method,
                "items": items,
                "total": total_amount,
                "totalAmount": total_amount,
                "status": "pending",
                "source": "telegram_bot",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

            if _db_client:
                try:
                    _db_client.collection("orders").document(order_id).set({
                        **firestore_payload,
                        "createdAt": firestore.SERVER_TIMESTAMP,
                    })
                except Exception as e:
                    logger.error("Buyurtma %s ni Firestore'ga yozib bo'lmadi: %s", order_id, e)

            # Bot ichida esa yagona snake_case sxema ishlatiladi
            order = normalize_order(firestore_payload)
            self._orders.append(order)
            self._carts[user_id] = []
            return order

    async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        return [normalize_order(o) for o in self._orders if o.get("user_id") == user_id]

    async def get_all_orders(self) -> List[Dict[str, Any]]:
        return [normalize_order(o) for o in reversed(self._orders)]

    async def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        for o in self._orders:
            if o.get("id") == order_id:
                return normalize_order(o)
        return None

    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        async with self._lock:
            for o in self._orders:
                if o.get("id") == order_id:
                    o["status"] = new_status
                    if _db_client:
                        try:
                            _db_client.collection("orders").document(order_id).update({
                                "status": new_status,
                                "updatedAt": firestore.SERVER_TIMESTAMP
                            })
                        except Exception as e:
                            logger.error("Buyurtma %s statusini yangilashda xato: %s", order_id, e)
                    return True
            return False

    async def link_shop_telegram(
        self,
        shop_id: str,
        telegram_chat_id: int,
        telegram_username: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
        except Exception as e:
            logger.error("Do'kon %s ni ulashda xato: %s", shop_id, e)
            return None, "error"

    async def get_designer_requests(self) -> List[Dict[str, Any]]:
        requests = []
        if _db_client:
            try:
                docs = _db_client.collection("designer_requests").order_by("createdAt", direction=firestore.Query.DESCENDING).limit(20).stream()
                for d in docs:
                    data = d.to_dict()
                    data["id"] = d.id
                    requests.append(data)
            except Exception as e:
                logger.error("Dizayner arizalarini olishda xato: %s", e)
        return requests

    async def get_courier_requests(self) -> List[Dict[str, Any]]:
        requests = []
        if _db_client:
            try:
                docs = _db_client.collection("courier_requests").order_by("createdAt", direction=firestore.Query.DESCENDING).limit(20).stream()
                for d in docs:
                    data = d.to_dict()
                    data["id"] = d.id
                    requests.append(data)
            except Exception as e:
                logger.error("Kuryer arizalarini olishda xato: %s", e)
        return requests

    async def update_designer_request_status(self, req_id: str, new_status: str) -> bool:
        if _db_client:
            try:
                _db_client.collection("designer_requests").document(req_id).update({
                    "status": new_status,
                    "updatedAt": firestore.SERVER_TIMESTAMP
                })
                return True
            except Exception as e:
                logger.error("Dizayner arizasi %s ni yangilashda xato: %s", req_id, e)
        return False

    async def update_courier_request_status(self, req_id: str, new_status: str) -> bool:
        if _db_client:
            try:
                _db_client.collection("courier_requests").document(req_id).update({
                    "status": new_status,
                    "updatedAt": firestore.SERVER_TIMESTAMP
                })
                return True
            except Exception as e:
                logger.error("Kuryer arizasi %s ni yangilashda xato: %s", req_id, e)
        return False

    async def add_designer_request(self, data: Dict[str, Any]) -> str:
        req_id = f"des_{int(datetime.now().timestamp())}_{uuid4().hex[:6]}"
        if _db_client:
            try:
                _db_client.collection("designer_requests").document(req_id).set({
                    **data,
                    "status": "pending",
                    "createdAt": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                logger.error("Dizayner arizasini yaratishda xato: %s", e)
        return req_id

    async def add_courier_request(self, data: Dict[str, Any]) -> str:
        req_id = f"cou_{int(datetime.now().timestamp())}_{uuid4().hex[:6]}"
        if _db_client:
            try:
                _db_client.collection("courier_requests").document(req_id).set({
                    **data,
                    "status": "pending",
                    "createdAt": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                logger.error("Kuryer arizasini yaratishda xato: %s", e)
        return req_id

# Global database instance
db = Database()
