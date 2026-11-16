package com.example.util

object Validators {
    private const val UZ_COUNTRY_CODE = "998"
    private const val UZ_LOCAL_LENGTH = 9
    private const val MIN_INTL_DIGITS = 10
    private const val MAX_INTL_DIGITS = 15

    fun requireNonBlank(raw: String?): String? {
        val trimmed = raw?.trim().orEmpty()
        return trimmed.ifEmpty { null }
    }

    /**
     * Normalizes Uzbekistan and international phone numbers to +998901234567 format.
     * Returns null when input is not a plausible phone number.
     */
    fun normalizePhone(raw: String?): String? {
        val digitsOnly = raw.orEmpty().filter { it.isDigit() }
        if (digitsOnly.isEmpty()) return null

        val normalizedDigits = when {
            digitsOnly.length == UZ_LOCAL_LENGTH -> UZ_COUNTRY_CODE + digitsOnly
            digitsOnly.length == UZ_LOCAL_LENGTH + 1 && digitsOnly.startsWith("0") ->
                UZ_COUNTRY_CODE + digitsOnly.drop(1)
            digitsOnly.length in MIN_INTL_DIGITS..MAX_INTL_DIGITS -> digitsOnly
            else -> return null
        }

        return "+$normalizedDigits"
    }

    /**
     * Parses price inputs such as "1 500 000", "1,500,000", "45_000", or "45000".
     */
    fun parsePriceDigits(raw: String?): Long? {
        val cleaned = raw.orEmpty()
            .trim()
            .replace(" ", "")
            .replace(",", "")
            .replace("_", "")
        if (cleaned.isEmpty() || !cleaned.all { it.isDigit() }) return null
        return cleaned.toLongOrNull()
    }
}
