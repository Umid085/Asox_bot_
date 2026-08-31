from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def get_website_redirect_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 ASOX Market Saytiga o'tish", url="https://asox.uz/app")]
        ]
    )

@router.message(F.text.in_(["🛒 Savat", "/cart"]))
async def show_cart_msg(message: Message):
    await message.answer(
        "🛒 <b>ASOX Market Xaridlar Bo'limi</b>\n\n"
        "Mahsulotlarni xavfsiz xarid qilish, to'lovlarni amalga oshirish va buyurtma berish rasmiy <a href='https://asox.uz'>asox.uz</a> saytimiz orqali amalga oshiriladi.\n\n"
        "👇 Saytga o'tish uchun quyidagi tugmani bosing:",
        reply_markup=get_website_redirect_kb(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.in_(["view_cart", "checkout"]))
async def view_cart_cb(callback: CallbackQuery):
    await callback.message.answer(
        "🛒 Mahsulotlarni xarid qilish uchun rasmiy saytimizga o'ting:\nhttps://asox.uz/app",
        reply_markup=get_website_redirect_kb()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart_cb(callback: CallbackQuery):
    await callback.answer("Mahsulotlarni https://asox.uz sayti orqali xarid qilishingiz mumkin.", show_alert=True)

# Eski savat/checkout callbacklari (cart_inc / cart_dec / cart_del / clear_cart /
# cancel_checkout / pay:*) endi ishlatilmaydi — xarid oqimi to'liq asox.uz
# saytiga ko'chirilgan va handlers/checkout.py o'chirilgan.
# Eski xabarlardagi tugmalar bosilsa, foydalanuvchini saytga yo'naltiramiz.
@router.callback_query(
    F.data.startswith("cart_inc:")
    | F.data.startswith("cart_dec:")
    | F.data.startswith("cart_del:")
    | F.data.startswith("pay:")
    | (F.data == "clear_cart")
    | (F.data == "cancel_checkout")
)
async def legacy_cart_cb(callback: CallbackQuery):
    await callback.message.answer(
        "🛒 Savat va buyurtma berish rasmiy saytimizga ko'chirildi:\nhttps://asox.uz/app",
        reply_markup=get_website_redirect_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "ignore")
async def ignore_cb(callback: CallbackQuery):
    await callback.answer()
