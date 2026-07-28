from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import db
from keyboards.inline import get_cart_keyboard
from utils.formatters import format_price

router = Router()

async def render_cart_message(user_id: int):
    cart_items = await db.get_cart(user_id)
    
    if not cart_items:
        text = "🛒 **Savat xush kelibsiz!**\n\nHozirda savatingiz bo'sh. Mahsulotlar katalogidan biror narsa tanlang."
        return text, get_cart_keyboard([])

    total_amount = 0
    items_text = ""
    for idx, item in enumerate(cart_items, 1):
        prod = item["product"]
        qty = item["quantity"]
        subtotal = prod["price"] * qty
        total_amount += subtotal
        items_text += f"{idx}. **{prod['name']}**\n   {qty} dona x {format_price(prod['price'])} = **{format_price(subtotal)}**\n\n"

    text = (
        f"🛒 **Sizning savatingiz:**\n\n"
        f"{items_text}"
        f"💵 **Jami summasi:** **{format_price(total_amount)}**"
    )
    return text, get_cart_keyboard(cart_items)

@router.message(F.text == "🛒 Savat")
async def show_cart_msg(message: Message):
    text, kb = await render_cart_message(message.from_user.id)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "view_cart")
async def view_cart_cb(callback: CallbackQuery):
    text, kb = await render_cart_message(callback.from_user.id)
    await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart_cb(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    product = await db.get_product_by_id(product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return

    await db.add_to_cart(user_id, product_id, quantity=1)
    await callback.answer(f"✅ {product['name']} savatga qo'shildi!", show_alert=True)

@router.callback_query(F.data.startswith("cart_inc:"))
async def cart_inc_cb(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    cart_items = await db.get_cart(user_id)
    item = next((i for i in cart_items if i["product"]["id"] == product_id), None)
    if item:
        await db.update_cart_quantity(user_id, product_id, item["quantity"] + 1)

    text, kb = await render_cart_message(user_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("cart_dec:"))
async def cart_dec_cb(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    cart_items = await db.get_cart(user_id)
    item = next((i for i in cart_items if i["product"]["id"] == product_id), None)
    if item:
        await db.update_cart_quantity(user_id, product_id, item["quantity"] - 1)

    text, kb = await render_cart_message(user_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("cart_del:"))
async def cart_del_cb(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    await db.update_cart_quantity(user_id, product_id, 0)
    text, kb = await render_cart_message(user_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer("Mahsulot olib tashlandi")

@router.callback_query(F.data == "clear_cart")
async def clear_cart_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    await db.clear_cart(user_id)
    text, kb = await render_cart_message(user_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer("Savat tozalandi")

@router.callback_query(F.data == "ignore")
async def ignore_cb(callback: CallbackQuery):
    await callback.answer()
