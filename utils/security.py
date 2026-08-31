"""Do'kon ulash (deep-link) havolalari uchun HMAC imzo yordamchilari.

`/start shop_<shopId>` havolasi imzosiz bo'lsa, uni bilgan HAR KIM do'konning
Telegram bildirishnoma kanalini o'ziga o'zlashtirib olishi mumkin edi. Shuning
uchun havola endi imzo bilan keladi:

    https://t.me/AsoxUz_Bot?start=shop_<shopId>_<sig>

`<sig>` — `SHOP_LINK_SECRET` kaliti bilan hisoblangan HMAC-SHA256 ning dastlabki
16 ta hex belgisi. Xuddi shu kalit asox.uz backendida ham bo'lishi va havolani
o'sha yerda `make_shop_link_token()` mantig'i bilan yaratishi shart.
"""

import hashlib
import hmac

SIGNATURE_LENGTH = 16


def make_shop_link_token(shop_id: str, secret: str) -> str:
    """`shop_<shopId>_<sig>` havolasi uchun imzo hosil qiladi."""
    if not secret:
        raise ValueError("SHOP_LINK_SECRET sozlanmagan")
    digest = hmac.new(
        secret.encode("utf-8"),
        f"shop:{shop_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return digest[:SIGNATURE_LENGTH]


def verify_shop_link_token(shop_id: str, signature: str, secret: str) -> bool:
    """Imzoni doimiy vaqtda (timing-safe) solishtiradi."""
    if not secret or not shop_id or not signature:
        return False
    try:
        expected = make_shop_link_token(shop_id, secret)
    except ValueError:
        return False
    return hmac.compare_digest(expected, signature.strip().lower())


def parse_shop_payload(payload: str):
    """`shop_<shopId>_<sig>` -> `(shop_id, signature)`.

    Imzo topilmasa `signature` `None` bo'ladi va chaqiruvchi havolani rad etadi
    (fail-closed): imzosiz eski havolalar endi qabul qilinmaydi.
    """
    if not payload or not payload.startswith("shop_"):
        return None, None
    body = payload[len("shop_"):].strip()
    if not body:
        return None, None
    if "_" not in body:
        return body, None
    shop_id, signature = body.rsplit("_", 1)
    return (shop_id.strip() or None), (signature.strip() or None)
