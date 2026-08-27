import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# Optional Firebase Firestore integration
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"projectId": "asox-market-prod-2e4bb"})
        else:
            firebase_admin.initialize_app(options={"projectId": "asox-market-prod-2e4bb"})
    _db_client = firestore.client()
except Exception as _e:
    _db_client = None

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
        self._categories: List[Dict[str, Any]] = list(CATEGORIES)
        self._products: List[Dict[str, Any]] = list(SAMPLE_PRODUCTS)
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
                    data = d.to_dict()
                    data["id"] = d.id
                    cats.append(data)
                if cats:
                    return cats
            except Exception:
                pass
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
                    data = d.to_dict()
                    if data.get("isDeleted") is True:
                        continue
                    cat = (data.get("category") or "").lower()
                    cat_id_clean = cat_id.lower().replace("cat_", "")
                    if cat_id_clean in cat or cat_id == data.get("category"):
                        data["id"] = d.id
                        data["price"] = data.get("effectivePrice") or data.get("price") or 0
                        data["category_id"] = cat_id
                        data["in_stock"] = True
                        data["image_url"] = (data.get("images") or [None])[0] or "https://asox.uz/icons/icon-512x512.png"
                        products.append(data)
                if products:
                    return products
            except Exception:
                pass
        return [p for p in self._products if p["category_id"] == cat_id]

    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        if _db_client:
            try:
                doc = _db_client.collection("products").document(product_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    data["id"] = doc.id
                    data["price"] = data.get("effectivePrice") or data.get("price") or 0
                    data["in_stock"] = True
                    data["image_url"] = (data.get("images") or [None])[0] or "https://asox.uz/icons/icon-512x512.png"
                    return data
            except Exception:
                pass
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        all_prods = list(self._products)
        if _db_client:
            try:
                docs = _db_client.collection("products").where("isActive", "==", True).limit(50).stream()
                for d in docs:
                    data = d.to_dict()
                    if data.get("isDeleted") is True:
                        continue
                    data["id"] = d.id
                    data["price"] = data.get("effectivePrice") or data.get("price") or 0
                    data["image_url"] = (data.get("images") or [None])[0] or "https://asox.uz/icons/icon-512x512.png"
                    all_prods.append(data)
            except Exception:
                pass
        return [p for p in all_prods if q in str(p.get("name", "")).lower() or q in str(p.get("description", "")).lower()]

    async def add_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            product_id = f"prod_{len(self._products) + 1}"
            product_data["id"] = product_id
            product_data["in_stock"] = True
            product_data["rating"] = 5.0
            self._products.append(product_data)
            return product_data

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
            order = {
                "id": order_id,
                "orderNumber": order_id,
                "user_id": user_id,
                "userId": f"tg_{user_id}",
                "telegramUserId": user_id,
                "customerName": user_name,
                "customerPhone": phone_number,
                "address": address_or_location,
                "paymentMethod": payment_method,
                "items": cart_items,
                "total": total_amount,
                "totalAmount": total_amount,
                "status": "pending",
                "source": "telegram_bot",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            # Write to Firestore if connected
            if _db_client:
                try:
                    _db_client.collection("orders").document(order_id).set({
                        **order,
                        "createdAt": firestore.SERVER_TIMESTAMP,
                    })
                except Exception:
                    pass

            self._orders.append(order)
            self._carts[user_id] = []
            return order

    async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        return [o for o in self._orders if o["user_id"] == user_id]

    async def get_all_orders(self) -> List[Dict[str, Any]]:
        return list(reversed(self._orders))

    async def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        for o in self._orders:
            if o["id"] == order_id:
                return o
        return None

    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        async with self._lock:
            for o in self._orders:
                if o["id"] == order_id:
                    o["status"] = new_status
                    if _db_client:
                        try:
                            _db_client.collection("orders").document(order_id).update({
                                "status": new_status,
                                "updatedAt": firestore.SERVER_TIMESTAMP
                            })
                        except Exception:
                            pass
                    return True
            return False

    async def link_shop_telegram(self, shop_id: str, telegram_chat_id: int, telegram_username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if _db_client:
            try:
                doc_ref = _db_client.collection("shops").document(shop_id)
                doc = doc_ref.get()
                if doc.exists:
                    doc_ref.update({
                        "telegramChatId": str(telegram_chat_id),
                        "telegramUsername": telegram_username or "",
                        "telegramLinkedAt": firestore.SERVER_TIMESTAMP
                    })
                    data = doc.to_dict()
                    data["id"] = doc.id
                    return data
            except Exception as e:
                print(f"Error linking shop {shop_id}: {e}")
        return None

# Global database instance
db = Database()
