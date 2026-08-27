from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🛍 Mahsulotlar Katalogi"), KeyboardButton(text="🛒 Savat")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="👤 Profilim")],
        [KeyboardButton(text="📞 Biz bilan bog'lanish"), KeyboardButton(text="🔍 Qidiruv")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        persistent=True
    )

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📦 Barcha buyurtmalar"), KeyboardButton(text="📊 Tizim statistikasi")],
        [KeyboardButton(text="➕ Yangi mahsulot qo'shish"), KeyboardButton(text="📢 Xabar tarqatish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        persistent=True
    )

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
