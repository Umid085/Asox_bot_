package com.example.util

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

object Security {
    const val SIGNATURE_LENGTH = 16

    /**
     * Generates the 16-char lowercase hex HMAC-SHA256 signature for `shop:<shopId>`.
     */
    fun makeShopLinkToken(shopId: String, secret: String): String {
        require(secret.isNotBlank()) { "SHOP_LINK_SECRET sozlanmagan" }
        val mac = Mac.getInstance("HmacSHA256")
        val keySpec = SecretKeySpec(secret.toByteArray(StandardCharsets.UTF_8), "HmacSHA256")
        mac.init(keySpec)
        val digest = mac.doFinal("shop:$shopId".toByteArray(StandardCharsets.UTF_8))
        val hex = digest.joinToString("") { "%02x".format(it) }
        return hex.take(SIGNATURE_LENGTH)
    }

    /**
     * Timing-safe signature check (fail-closed when secret, shopId, or signature is empty).
     */
    fun verifyShopLinkToken(shopId: String?, signature: String?, secret: String?): Boolean {
        if (secret.isNullOrBlank() || shopId.isNullOrBlank() || signature.isNullOrBlank()) {
            return false
        }
        val expected = runCatching { makeShopLinkToken(shopId, secret) }.getOrNull() ?: return false
        val actual = signature.trim().lowercase()
        return MessageDigest.isEqual(
            expected.toByteArray(StandardCharsets.UTF_8),
            actual.toByteArray(StandardCharsets.UTF_8),
        )
    }

    /**
     * Parses `shop_<shopId>_<sig>` or full URLs containing `?start=shop_<shopId>_<sig>`.
     * Unsigned payloads (`shop_<shopId>`) return signature = null (fail-closed).
     */
    fun parseShopPayload(rawInput: String?): Pair<String?, String?> {
        val raw = rawInput?.trim().orEmpty()
        if (raw.isEmpty()) return null to null

        val extractedPayload = when {
            "start=" in raw -> raw.substringAfter("start=").substringBefore("&").trim()
            "payload=" in raw -> raw.substringAfter("payload=").substringBefore("&").trim()
            else -> raw
        }

        if (!extractedPayload.startsWith("shop_")) return null to null
        val body = extractedPayload.removePrefix("shop_").trim()
        if (body.isEmpty()) return null to null
        val lastUnderscore = body.lastIndexOf('_')
        if (lastUnderscore < 0) {
            return body to null
        }
        val shopId = body.substring(0, lastUnderscore).trim().ifEmpty { null }
        val signature = body.substring(lastUnderscore + 1).trim().ifEmpty { null }
        return shopId to signature
    }

    /**
     * Checks numeric admin ID membership (never trusts mutable usernames).
     */
    fun parseAdminIds(adminIdsRaw: String?): Set<Long> {
        return adminIdsRaw.orEmpty()
            .split(",")
            .mapNotNull { it.trim().toLongOrNull() }
            .toSet()
    }

    fun isAdminUser(userId: Long, adminIds: Set<Long>): Boolean {
        return userId in adminIds
    }
}
