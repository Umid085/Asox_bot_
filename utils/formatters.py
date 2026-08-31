def format_price(amount: float | int) -> str:
    """Format numeric price into human-readable sum string e.g. 150,000 so'm"""
    try:
        val = int(amount)
        return f"{val:,}".replace(",", " ") + " so'm"
    except Exception:
        return f"{amount} so'm"

def get_order_status_badge(status: str) -> str:
    """Return status string with descriptive Uzbek label and emoji"""
    mapping = {
        "pending": "⏳ Yangi (Kutilmoqda)",
        "processing": "⚙️ Jarayonda",
        "shipped": "🚚 Yetkazilmoqda",
        "delivered": "✅ Bajarildi (Yetkazib berildi)",
        "cancelled": "❌ Bekor qilindi"
    }
    return mapping.get(status.lower(), status.capitalize())


def esc(value) -> str:
    """Matnni Telegram HTML uchun xavfsiz holga keltiradi.

    Mahsulot nomi, mijoz ismi, manzil va ariza maydonlari foydalanuvchi yoki
    Firestore tomonidan boshqariladi. Ularni escape qilmasdan yuborish
    Telegram 400 (`can't parse entities`) xatosiga yoki admin xabariga
    begona HTML teglari kirib qolishiga olib keladi.
    """
    import html

    if value is None:
        return ""
    return html.escape(str(value), quote=True)
