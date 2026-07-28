from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import db
from keyboards.inline import (
    get_categories_keyboard,
    get_products_keyboard,
    get_product_detail_keyboard
)
from states.states import AdminStates
from utils.formatters import format_price

router = Router()

@router.message(F.text == "🛍 Mahsulotlar Katalogi")
async def show_categories_msg(message: Message):
    categories = await db.get_categories()
    await message.answer(
        "📂 **Barcha kategoriyalar:**\nKerakli bo'limni tanlang:",
        reply_markup=get_categories_keyboard(categories),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_cb(callback: CallbackQuery):
    categories = await db.get_categories()
    await callback.message.edit_text(
        "📂 **Barcha kategoriyalar:**\nKerakli bo'limni tanlang:",
        reply_markup=get_categories_keyboard(categories),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cat:"))
async def show_category_products_cb(callback: CallbackQuery):
    cat_id = callback.data.split(":")[1]
    cat = await db.get_category_by_id(cat_id)
    products = await db.get_products_by_category(cat_id)

    if not products:
        await callback.answer("Ushbu kategoriyada hali mahsulotlar mavjud emas.", show_alert=True)
        return

    cat_name = cat['name'] if cat else "Mahsulotlar"
    await callback.message.edit_text(
        f"📱 **Kategoriya:** {cat_name}\n\nQuyidagi mahsulotlardan birini tanlang:",
        reply_markup=get_products_keyboard(products, cat_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail_cb(callback: CallbackQuery):
    prod_id = callback.data.split(":")[1]
    product = await db.get_product_by_id(prod_id)

    if not product:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return

    price_fmt = format_price(product['price'])
    detail_text = (
        f"📦 **{product['name']}**\n\n"
        f"📝 **Tavsif:** {product['description']}\n"
        f"⭐ **Reyting:** {product['rating']}/5.0\n"
        f"💰 **Narxi:** **{price_fmt}**\n"
        f"✅ **Mavjudligi:** Omborimizda bor"
    )

    kb = get_product_detail_keyboard(product['id'], product['category_id'])
    
    # Try sending photo if available, otherwise text
    try:
        await callback.message.answer_photo(
            photo=product['image_url'],
            caption=detail_text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await callback.message.delete()
    except Exception:
        await callback.message.edit_text(
            detail_text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    await callback.answer()

# Search functionality
@router.message(F.text == "🔍 Qidiruv")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_search_query)
    await message.answer("🔍 Qidirmoqchi bo'lgan mahsulot nomini kiritishingiz mumkin:")

@router.message(AdminStates.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text
    results = await db.search_products(query)
    await state.clear()

    if not results:
        await message.answer(f"❌ '{query}' bo'yicha hech qanday mahsulot topilmadi.")
        return

    text = f"🔍 **'{query}' bo'yicha qidiruv natijalari:**\n\n"
    keyboard = get_products_keyboard(results, "cat_phones")
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
