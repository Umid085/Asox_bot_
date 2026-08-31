from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any
from utils.formatters import format_price

def get_categories_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        icon = cat.get('icon') or "🛍"
        name = cat.get('name') or "Kategoriya"
        buttons.append([InlineKeyboardButton(text=f"{icon} {name}", callback_data=f"cat:{cat.get('id', '')}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_products_keyboard(products: List[Dict[str, Any]], cat_id: str) -> InlineKeyboardMarkup:
    buttons = []
    for p in products:
        price_str = format_price(p.get('price', 0))
        name = p.get('name') or "Mahsulot"
        buttons.append([InlineKeyboardButton(text=f"{name} - {price_str}", callback_data=f"prod:{p.get('id', '')}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Kategoriyalarga qaytish", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_product_detail_keyboard(product_id: str, cat_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Saytda ko'rish va xarid qilish", url=f"https://asox.uz/app/product/{product_id}")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"cat:{cat_id}")]
        ]
    )

def get_cart_keyboard(cart_items: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for item in cart_items:
        prod = item["product"]
        pid = prod["id"]
        qty = item["quantity"]
        buttons.append([
            InlineKeyboardButton(text=f"{prod['name'][:20]}...", callback_data=f"prod:{pid}"),
            InlineKeyboardButton(text="➖", callback_data=f"cart_dec:{pid}"),
            InlineKeyboardButton(text=f"{qty} dona", callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"cart_inc:{pid}"),
            InlineKeyboardButton(text="❌", callback_data=f"cart_del:{pid}")
        ])

    if cart_items:
        buttons.append([InlineKeyboardButton(text="🚀 Buyurtma berish", callback_data="checkout")])
        buttons.append([InlineKeyboardButton(text="🗑 Savatni tozalash", callback_data="clear_cart")])
    
    buttons.append([InlineKeyboardButton(text="🛍 Katalogni ko'rish", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Click orqali to'lov", callback_data="pay:click")],
            [InlineKeyboardButton(text="💳 Payme orqali to'lov", callback_data="pay:payme")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_checkout")]
        ]
    )

def get_admin_order_keyboard(order_id: str, current_status: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="⚙️ Jarayonda", callback_data=f"adm_ord:{order_id}:processing"),
            InlineKeyboardButton(text="🚚 Yetkazilmoqda", callback_data=f"adm_ord:{order_id}:shipped")
        ],
        [
            InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"adm_ord:{order_id}:delivered"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"adm_ord:{order_id}:cancelled")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
