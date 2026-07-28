from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database.db import db
from config import ADMIN_IDS
from states.states import AdminStates
from keyboards.inline import get_admin_order_keyboard, get_categories_keyboard
from utils.formatters import format_price, get_order_status_badge

router = Router()

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Barcha buyurtmalar", callback_data="admin_view_orders")],
            [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="📊 Tizim statistikasi", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Xabar tarqatish (Broadcast)", callback_data="admin_broadcast")]
        ]
    )

@router.message(F.text == "⚙️ Admin Panel")
async def show_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Kechirasiz, sizda admin huquqlari yo'q.")
        return

    await message.answer("⚙️ **ASOX Market Admin Paneli**", reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def admin_stats_cb(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    users_count = await db.get_users_count()
    all_orders = await db.get_all_orders()
    total_revenue = sum(o["total_amount"] for o in all_orders if o["status"] == "delivered")

    stats_text = (
        f"📊 **ASOX Market Statistikasi**\n\n"
        f"👥 **Foydalanuvchilar soni:** {users_count} ta\n"
        f"📦 **Jami buyurtmalar:** {len(all_orders)} ta\n"
        f"💰 **Jami tushum (Bajarilgan):** {format_price(total_revenue)}"
    )
    await callback.message.edit_text(stats_text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_view_orders")
async def admin_view_orders_cb(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    orders = await db.get_all_orders()
    if not orders:
        await callback.answer("Hozircha buyurtmalar yo'q.", show_alert=True)
        return

    await callback.answer()
    for order in orders[:5]: # Show latest 5
        items_summary = "".join(f"• {i['product']['name']} ({i['quantity']}x)\n" for i in order["items"])
        text = (
            f"🆔 **Order #{order['id']}** ({order['created_at']})\n"
            f"👤 **Mijoz:** {order['user_name']} (`{order['user_id']}`)\n"
            f"📱 **Tel:** {order['phone_number']}\n"
            f"📍 **Manzil:** {order['address']}\n"
            f"💰 **Summa:** {format_price(order['total_amount'])}\n"
            f"📊 **Holati:** {get_order_status_badge(order['status'])}\n\n"
            f"📦 **Mahsulotlar:**\n{items_summary}"
        )
        await callback.message.answer(
            text,
            reply_markup=get_admin_order_keyboard(order['id'], order['status']),
            parse_mode="Markdown"
        )

@router.callback_query(F.data.startswith("adm_ord:"))
async def admin_change_order_status(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        return

    _, order_id, new_status = callback.data.split(":")
    success = await db.update_order_status(order_id, new_status)

    if success:
        order = await db.get_order_by_id(order_id)
        status_badge = get_order_status_badge(new_status)
        await callback.answer(f"Buyurtma #{order_id} holati o'zgartirildi: {status_badge}")
        
        # Update user about status change
        if order:
            try:
                await bot.send_message(
                    chat_id=order["user_id"],
                    text=f"🔔 **Buyurtmangiz holati o'zgardi!**\n\nBuyurtma ID: `{order_id}`\nYangi holat: **{status_badge}**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
    else:
        await callback.answer("Buyurtma topilmadi", show_alert=True)

# Add product flow
@router.callback_query(F.data == "admin_add_product")
async def admin_add_product_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(AdminStates.waiting_for_product_name)
    await callback.message.answer("📝 **Yangi mahsulot nomini kiriting:**", parse_mode="Markdown")
    await callback.answer()

@router.message(AdminStates.waiting_for_product_name)
async def process_prod_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.waiting_for_product_price)
    await message.answer("💰 **Mahsulot narxini kiriting (faqat raqam, masalan: 1500000):**", parse_mode="Markdown")

@router.message(AdminStates.waiting_for_product_price)
async def process_prod_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting:")
        return

    await state.update_data(price=int(message.text))
    await state.set_state(AdminStates.waiting_for_product_description)
    await message.answer("📝 **Mahsulot haqida qisqacha tavsif (description) kiriting:**", parse_mode="Markdown")

@router.message(AdminStates.waiting_for_product_description)
async def process_prod_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    categories = await db.get_categories()
    await state.set_state(AdminStates.waiting_for_product_category)
    await message.answer("📂 **Mahsulot qaysi kategoriyaga tegishli?**", reply_markup=get_categories_keyboard(categories), parse_mode="Markdown")

@router.callback_query(AdminStates.waiting_for_product_category, F.data.startswith("cat:"))
async def process_prod_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.split(":")[1]
    await state.update_data(category_id=cat_id)
    
    await state.set_state(AdminStates.waiting_for_product_image)
    await callback.message.answer(
        "🖼 **Mahsulot rasmini yuboring (fayl yoki rasm ko'rinishida) yoki standat rasm ishlatish uchun 'otish' deb yozing:**",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_product_image)
async def process_prod_image(message: Message, state: FSMContext):
    image_url = "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800"
    if message.photo:
        image_url = message.photo[-1].file_id

    data = await state.get_data()
    new_prod = await db.add_product({
        "category_id": data.get("category_id", "cat_phones"),
        "name": data["name"],
        "price": data["price"],
        "description": data["description"],
        "image_url": image_url
    })

    await state.clear()
    await message.answer(
        f"✅ **Yangi mahsulot qo'shildi!**\n\n"
        f"ID: `{new_prod['id']}`\n"
        f"Nomi: **{new_prod['name']}**\n"
        f"Narxi: {format_price(new_prod['price'])}",
        parse_mode="Markdown"
    )

# Broadcast functionality
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.message.answer(
        "📢 **Barcha foydalanuvchilarga yuboriladigan xabarni yuboring:**\n\n"
        "(Matn, rasm yoki media yuborishingiz mumkin. Bekor qilish uchun ❌ Bekor qilish tugmasini bosing)",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Xabar tarqatish bekor qilindi.")
        return

    users = db._users.keys()
    count_success = 0
    count_fail = 0

    status_msg = await message.answer("⏳ Xabar yuborilmoqda...")

    for user_id in list(users):
        try:
            await message.copy_to(chat_id=user_id)
            count_success += 1
        except Exception:
            count_fail += 1

    await state.clear()
    await status_msg.edit_text(
        f"✅ **Xabarnoma yakunlandi!**\n\n"
        f"🟢 Yuborildi: {count_success} ta\n"
        f"🔴 Xatolik (Bloklangan): {count_fail} ta",
        parse_mode="Markdown"
    )

