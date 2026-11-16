package com.example

import com.example.util.Formatters
import com.example.util.OrderStatusTone
import com.example.util.Security
import com.example.util.Validators
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class AsoxBusinessLogicTest {

    @Test
    fun formatPrice_formatsSpaceGroupedSum() {
        assertEquals("85 000 so'm", Formatters.formatPrice(85000.0))
        assertEquals("1 500 000 so'm", Formatters.formatPrice(1500000L))
    }

    @Test
    fun orderStatusDisplay_mapsUzbekLabels() {
        val pending = Formatters.getOrderStatusDisplay("pending")
        assertEquals("⏳ Yangi (Kutilmoqda)", pending.badgeText)
        assertEquals(OrderStatusTone.PENDING, pending.tone)

        val delivered = Formatters.getOrderStatusDisplay("delivered")
        assertEquals("✅ Bajarildi (Yetkazib berildi)", delivered.badgeText)
        assertEquals(OrderStatusTone.DELIVERED, delivered.tone)
    }

    @Test
    fun normalizePhone_handlesUzbekAndInternationalFormats() {
        assertEquals("+998901234567", Validators.normalizePhone("+998901234567"))
        assertEquals("+998901234567", Validators.normalizePhone("998901234567"))
        assertEquals("+998901234567", Validators.normalizePhone("901234567"))
        assertEquals("+998901234567", Validators.normalizePhone("0901234567"))
        assertEquals("+998901234567", Validators.normalizePhone("+998 (90) 123-45-67"))
        assertNull(Validators.normalizePhone("qwerty"))
        assertNull(Validators.normalizePhone("12345"))
    }

    @Test
    fun parsePriceDigits_acceptsFormattedSeparators() {
        assertEquals(1500000L, Validators.parsePriceDigits("1 500 000"))
        assertEquals(1500000L, Validators.parsePriceDigits("1,500,000"))
        assertEquals(45000L, Validators.parsePriceDigits("45000"))
        assertNull(Validators.parsePriceDigits("qimmat"))
    }

    @Test
    fun shopLinkSecurity_verifiesValidHmacAndFailsClosed() {
        val secret = "test_secret"
        val shopId = "shop_samarkand_1"
        val token = Security.makeShopLinkToken(shopId, secret)

        assertEquals(16, token.length)
        assertTrue(Security.verifyShopLinkToken(shopId, token, secret))
        assertFalse(Security.verifyShopLinkToken("shop_boshqa", token, secret))
        assertFalse(Security.verifyShopLinkToken(shopId, token.dropLast(1) + "0", secret))
        assertFalse(Security.verifyShopLinkToken(shopId, token, ""))

        val (parsedId, parsedSig) = Security.parseShopPayload("shop_${shopId}_$token")
        assertEquals(shopId, parsedId)
        assertEquals(token, parsedSig)

        val (noSigId, noSig) = Security.parseShopPayload("shop_samarkand1")
        assertEquals("samarkand1", noSigId)
        assertNull(noSig)
        assertFalse(Security.verifyShopLinkToken(noSigId, noSig, secret))

        val (unsignedId, unsignedSig) = Security.parseShopPayload("shop_$shopId")
        assertFalse(Security.verifyShopLinkToken(unsignedId, unsignedSig, secret))

        val (urlId, urlSig) = Security.parseShopPayload(
            "https://t.me/AsoxUz_Bot?start=shop_${shopId}_$token"
        )
        assertEquals(shopId, urlId)
        assertEquals(token, urlSig)
    }

    @Test
    fun adminAuthorization_checksNumericIdsOnly() {
        val admins = Security.parseAdminIds("111, 222")
        assertTrue(Security.isAdminUser(111L, admins))
        assertFalse(Security.isAdminUser(999L, admins))
    }
}
