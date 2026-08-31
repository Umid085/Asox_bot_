from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import db
from config import ADMIN_IDS, is_admin_user
from states.states import CheckoutStates
from keyboards.reply import get_phone_keyboard, get_location_keyboard, get_main_keyboard
from keyboards.inline import get_payment_methods_keyboard, get_admin_order_keyboard
from utils.formatters import format_price, get_order_status_badge

router = Router()

@router.callback_query(F.data == "checkout")
async def start_checkout_cb(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart_items = await db.get_cart(user_id)

    if not cart_items:
        await callback.answer("Savatingiz bo'sh!", show_alert=True)
        return

    # Check if user already has saved phone
    user = await db.get_or_create_user(user_id)
    if user.get("phone_number"):
        await state.update_data(phone_number=user["phone_number"])
        await state.set_state(CheckoutStates.waiting_for_location)
        await callback.message.answer(
            "📍 Buyurtma yetkazib beriladigan **manzilni kiriting** yoki **lokatsiyangizni ulashing**:",
            reply_markup=get_location_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await state.set_state(CheckoutStates.waiting_for_phone)
        await callback.message.answer(
            "📱 Buyurtma rasmiylashtirish uchun **telefon raqamingizni kiriting** yoki quyidagi tugmani bosing:",
            reply_markup=get_phone_keyboard(),
            parse_mode="Markdown"
        )

    await callback.answer()

@router.message(CheckoutStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    if not phone or len(phone) < 7:
        await message.answer("❌ Iltimos, to'g'ri telefon raqamini kiriting:")
        return

    await db.update_user_phone(message.from_user.id, phone)
    await state.update_data(phone_number=phone)

    await state.set_state(CheckoutStates.waiting_for_location)
    await message.answer(
        "📍 Rahmat! Endi buyurtma yetkazib beriladigan **manzilni kiriting** yoki **lokatsiyangizni ulashing**:",
        reply_markup=get_location_keyboard(),
        parse_mode="Markdown"
    )

@router.message(CheckoutStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    if message.location:
        address = f"Lat: {message.location.latitude}, Lon: {message.location.longitude}"
    else:
        address = message.text

    if not address:
        await message.answer("❌ Iltimos, manzilni kiriting yoki lokatsiyani yuboring:")
        return

    await state.update_data(address=address)
    await state.set_state(CheckoutStates.waiting_for_payment)

    user_id = message.from_user.id
    cart_items = await db.get_cart(user_id)
    total_amount = sum(item["product"]["price"] * item["quantity"] for item in cart_items)

    await message.answer(
        f"💳 **To'lov turini tanlang:**\n\nBuyurtma summasi: **{format_price(total_amount)}**",
        reply_markup=get_payment_methods_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(CheckoutStates.waiting_for_payment, F.data.startswith("pay:"))
async def process_payment_and_finish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    payment_code = callback.data.split(":")[1]
    payment_map = {"click": "💳 Click", "payme": "💳 Payme"}
    payment_method = payment_map.get(payment_code, "💳 Payme")

    data = await state.get_data()
    phone = data.get("phone_number", "Kiritilmagan")
    address = data.get("address", "Kiritilmagan")

    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    cart_items = await db.get_cart(user_id)

    if not cart_items:
        await callback.answer("Savatingiz bo'sh!", show_alert=True)
        await state.clear()
        return

    total_amount = sum(item["product"]["price"] * item["quantity"] for item in cart_items)

    order = await db.create_order(
        user_id=user_id,
        user_name=user_name,
        phone_number=phone,
        address_or_location=address,
        payment_method=payment_method,
        cart_items=cart_items,
        total_amount=total_amount
    )

    await state.clear()

    # User confirmation message
    items_summary = "".join(
        f"• {i.get('name', 'Tovar')} ({i.get('quantity', 1)} dona)\n" for i in order.get("items", [])
    )
    user_confirm_text = (
        f"🎉 **Buyurtmangiz muvaffaqiyatli qabul qilindi!**\n\n"
        f"🆔 **Buyurtma ID:** `{order.get('id', '')}`\n"
        f"📦 **Mahsulotlar:**\n{items_summary}\n"
        f"💰 **Jami summa:** **{format_price(total_amount)}**\n"
        f"💳 **To'lov usuli:** {payment_method}\n"
        f"📍 **Manzil:** {address}\n"
        f"📱 **Telefon:** {phone}\n\n"
        f"⚡️ Operatorimiz tez orada siz bilan bog'lanadi!"
    )

    await callback.message.answer(user_confirm_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

    # Notify Admins about new order
    admin_notify_text = (
        f"🚨 **YANGI BUYURTMA # {order['id']}**\n\n"
        f"👤 **Mijoz:** {user_name} (`{user_id}`)\n"
        f"📱 **Tel:** `{phone}`\n"
        f"📍 **Manzil:** {address}\n"
        f"💳 **To'lov:** {payment_method}\n"
        f"💰 **Summa:** **{format_price(total_amount)}**\n\n"
        f"📦 **Tarkibi:**\n{items_summary}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_notify_text,
                reply_markup=get_admin_order_keyboard(order['id'], order['status']),
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer()

@router.callback_query(F.data == "cancel_checkout")
async def cancel_checkout_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Buyurtma berish bekor qilindi.", reply_markup=get_main_keyboard())
    await callback.answer()
