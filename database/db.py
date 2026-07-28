import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# In-memory Async Store initialized with rich sample data matching ASOX Market products

CATEGORIES = [
    {"id": "cat_phones", "name": "📱 Smartfonlar va Gadjetlar", "icon": "📱"},
    {"id": "cat_laptops", "name": "💻 Noutbuklar va Kompyuterlar", "icon": "💻"},
    {"id": "cat_audio", "name": "🎧 Maishiy audio va Quloqchinlar", "icon": "🎧"},
    {"id": "cat_home", "name": "🏠 Maishiy texnika", "icon": "🏠"},
    {"id": "cat_accessories", "name": "🔌 Aksessuarlar", "icon": "🔌"},
]

SAMPLE_PRODUCTS = [
    {
        "id": "prod_1",
        "category_id": "cat_phones",
        "name": "iPhone 15 Pro Max 256GB Natural Titanium",
        "description": "A17 Pro chip, Titandan ishlangan korpus, 48MP kamera, 120Hz Super Retina XDR ekran.",
        "price": 14500000,
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?q=80&w=800",
        "in_stock": True,
        "rating": 4.9
    },
    {
        "id": "prod_2",
        "category_id": "cat_phones",
        "name": "Samsung Galaxy S24 Ultra 512GB",
        "description": "Galaxy AI funksiyalari, Snapdragon 8 Gen 3, 200MP kamera va o'rnatilgan S-Pen.",
        "price": 13800000,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=800",
        "in_stock": True,
        "rating": 4.8
    },
    {
        "id": "prod_3",
        "category_id": "cat_laptops",
        "name": "MacBook Pro 14 M3 Pro 18GB/512GB",
        "description": "M3 Pro chipi, Liquid Retina XDR displey, 18 soatgacha batareya ishlash vaqti.",
        "price": 24000000,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=800",
        "in_stock": True,
        "rating": 5.0
    },
    {
        "id": "prod_4",
        "category_id": "cat_audio",
        "name": "AirPods Pro (2-avlod) Type-C",
        "description": "Faol shovqinni bekor qilish (ANC), Shaffoflik rejimi, MagSafe qutisi.",
        "price": 2800000,
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?q=80&w=800",
        "in_stock": True,
        "rating": 4.9
    },
    {
        "id": "prod_5",
        "category_id": "cat_home",
        "name": "Dyson V15 Detect Absolute changyutgich",
        "description": "Lazerli chang aniqlash tizimi, 240 AW kuchli tortish, HEPA filtratsiyasi.",
        "price": 9200000,
        "image_url": "https://images.unsplash.com/photo-1558317374-067fb5f30001?q=80&w=800",
        "in_stock": True,
        "rating": 4.7
    },
    {
        "id": "prod_6",
        "category_id": "cat_accessories",
        "name": "Anker PowerBank 24000mAh 140W",
        "description": "Noutbuk va telefonlar uchun o'ta tezkor quvvatlash moslamasi, OLED displey.",
        "price": 1400000,
        "image_url": "https://images.unsplash.com/photo-1609592424074-9844208a0d78?q=80&w=800",
        "in_stock": True,
        "rating": 4.8
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
        return self._categories

    async def get_category_by_id(self, cat_id: str) -> Optional[Dict[str, Any]]:
        for cat in self._categories:
            if cat["id"] == cat_id:
                return cat
        return None

    async def get_products_by_category(self, cat_id: str) -> List[Dict[str, Any]]:
        return [p for p in self._products if p["category_id"] == cat_id]

    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        return [p for p in self._products if q in p["name"].lower() or q in p["description"].lower()]

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
            # Hydrate with product details
            result = []
            for item in items:
                prod = next((p for p in self._products if p["id"] == item["product_id"]), None)
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
                "user_id": user_id,
                "user_name": user_name,
                "phone_number": phone_number,
                "address": address_or_location,
                "payment_method": payment_method,
                "items": cart_items,
                "total_amount": total_amount,
                "status": "pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
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
                    return True
            return False

# Global database instance
db = Database()
