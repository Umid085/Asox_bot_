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

def get_products_keyboard(products: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Mahsulotlar ro'yxati. Ortga tugmasi doim kategoriyalar menyusiga qaytaradi."""
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
