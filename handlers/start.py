import html
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database.db import db
from config import ADMIN_IDS
from keyboards.reply import get_main_keyboard
from utils.formatters import format_price

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name or "Foydalanuvchi"

    await db.get_or_create_user(user_id, username, full_name)
    is_admin = user_id in ADMIN_IDS

    welcome_text = (
        f"👋 <b>Xush kelibsiz, {html.escape(full_name)}!</b>\n\n"
        f"🛒 <b>ASOX Market</b> rasmiy botiga xush kelibsiz.\n"
        f"Bu yerda siz eng zamonaviy smartfonlar, noutbuklar, maishiy texnika va aksessuarlarni qulay narxlarda buyurtma qilishingiz mumkin!\n\n"
        f"👇 Kerakli bo'limni tanlash uchun pastdagi menyudan foydalaning."
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(is_admin=is_admin), parse_mode="HTML")

@router.message(F.text == "❌ Bekor qilish")
async def process_cancel(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer("Amal bekor qilindi.", reply_markup=get_main_keyboard(is_admin=is_admin))

@router.message(F.text == "👤 Profilim")
async def process_profile(message: Message):
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    orders = await db.get_user_orders(user_id)

    phone = user.get("phone_number") or "Kiritilmagan"
    full_name = html.escape(user.get('full_name') or 'Mavjud emas')
    profile_text = (
        f"👤 <b>Foydalanuvchi Profili</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Ism:</b> {full_name}\n"
        f"📱 <b>Telefon:</b> {html.escape(str(phone))}\n"
        f"📦 <b>Jami buyurtmalar:</b> {len(orders)} ta\n"
    )
    await message.answer(profile_text, parse_mode="HTML")

@router.message(F.text.in_(["📞 Biz bilan bog'lanish", "📞 Biz bilan aloqa", "Biz bilan bog'lanish", "Biz bilan aloqa"]))
async def process_contact(message: Message):
    contact_text = (
        f"📞 <b>ASOX Market Qo'llab-quvvatlash Xizmati</b>\n\n"
        f"❓ Savollaringiz yoki takliflaringiz bormi? Biz bilan bog'laning:\n\n"
        f"☎️ <b>Telefon:</b> +998 (77) 048-37-63\n"
        f"💬 <b>Telegram Support:</b> @asox_support\n"
        f"🌐 <b>Veb-sayt:</b> <a href='https://asox.uz'>asox.uz</a>\n"
        f"📍 <b>Manzil:</b> Oʻzbekiston, Samarqand shahri, Sadaf MFY, Gagarin ko'chasi, 60"
    )
    await message.answer(contact_text, parse_mode="HTML", disable_web_page_preview=True)


