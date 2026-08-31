from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.db import DEFAULT_PRODUCT_IMAGE, db
from keyboards.inline import get_categories_keyboard, get_product_detail_keyboard, get_products_keyboard
from states.states import AdminStates
from utils.formatters import esc, format_price
from utils.validators import require_text

router = Router()

CATEGORIES_TEXT = "📂 <b>Barcha kategoriyalar:</b>\nKerakli bo'limni tanlang:"

@router.message(F.text == "🛍 Mahsulotlar Katalogi")
async def show_categories_msg(message: Message):
    categories = await db.get_categories()
    await message.answer(
        CATEGORIES_TEXT,
        reply_markup=get_categories_keyboard(categories),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_cb(callback: CallbackQuery):
    categories = await db.get_categories()
    await callback.message.edit_text(
        CATEGORIES_TEXT,
        reply_markup=get_categories_keyboard(categories),
        parse_mode="HTML"
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

    cat_name = (cat or {}).get("name") or "Mahsulotlar"
    await callback.message.edit_text(
        f"📱 <b>Kategoriya:</b> {esc(cat_name)}\n\nQuyidagi mahsulotlardan birini tanlang:",
        reply_markup=get_products_keyboard(products),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail_cb(callback: CallbackQuery):
    prod_id = callback.data.split(":")[1]
    product = await db.get_product_by_id(prod_id)

    if not product:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return

    price_fmt = format_price(product.get('price', 0))
    rating = product.get('rating') or 0
    rating_line = f"⭐ <b>Reyting:</b> {rating}/5.0\n" if rating else ""
    description = product.get('description') or "Tavsif kiritilmagan."
    detail_text = (
        f"📦 <b>{esc(product.get('name', 'Mahsulot'))}</b>\n\n"
        f"📝 <b>Tavsif:</b> {esc(description)}\n"
        f"{rating_line}"
        f"💰 <b>Narxi:</b> <b>{price_fmt}</b>\n\n"
        f"🛒 <i>Xarid qilish va buyurtma berish uchun quyidagi havola orqali saytga o'ting:</i>"
    )

    kb = get_product_detail_keyboard(product.get('id', ''), product.get('category_id', ''))

    # Try sending photo if available, otherwise text
    try:
        await callback.message.answer_photo(
            photo=product.get('image_url') or DEFAULT_PRODUCT_IMAGE,
            caption=detail_text,
            reply_markup=kb,
            parse_mode="HTML"
        )
        await callback.message.delete()
    except Exception:
        await callback.message.edit_text(
            detail_text,
            reply_markup=kb,
            parse_mode="HTML"
        )
    await callback.answer()

# Search functionality
@router.message(F.text == "🔍 Qidiruv")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_search_query)
    await message.answer("🔍 Qidirmoqchi bo'lgan mahsulot nomini kiritishingiz mumkin:")

@router.message(AdminStates.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    query = await require_text(message, "❌ Qidiruv uchun <b>matn</b> yuboring:")
    if query is None:
        return  # holat saqlanadi — foydalanuvchi qayta urinib ko'radi

    results = await db.search_products(query)
    await state.clear()

    if not results:
        await message.answer(
            f"❌ '{esc(query)}' bo'yicha hech qanday mahsulot topilmadi.",
            parse_mode="HTML"
        )
        return

    text = f"🔍 <b>'{esc(query)}' bo'yicha qidiruv natijalari:</b>"
    keyboard = get_products_keyboard(results)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
