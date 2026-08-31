from aiogram import Router, F
from aiogram.types import Message

from database.db import db
from utils.formatters import format_price, get_order_status_badge

router = Router()

@router.message(F.text == "📦 Buyurtmalarim")
async def show_user_orders(message: Message):
    user_id = message.from_user.id
    orders = await db.get_user_orders(user_id)

    if not orders:
        await message.answer("📦 Sizda hali hech qanday buyurtmalar mavjud emas.")
        return

    text = "📦 **Sizning buyurtmalaringiz:**\n\n"
    for order in reversed(orders):
        status_badge = get_order_status_badge(order.get("status", "pending"))
        items_summary = ", ".join(
            f"{i.get('name', 'Tovar')} ({i.get('quantity', 1)}x)" for i in order.get("items", [])
        )

        text += (
            f"🆔 **ID:** `{order.get('id', '')}`\n"
            f"📅 **Sana:** {order.get('created_at', '')}\n"
            f"📦 **Mahsulotlar:** {items_summary}\n"
            f"💰 **Jami:** {format_price(order.get('total_amount', 0))}\n"
            f"📊 **Holati:** {status_badge}\n"
            f"-----------------------------------\n"
        )

    await message.answer(text, parse_mode="Markdown")
