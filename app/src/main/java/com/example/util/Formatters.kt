package com.example.util

import java.text.DecimalFormat
import java.text.DecimalFormatSymbols
import java.util.Locale

enum class OrderStatusTone {
    PENDING,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED,
}

data class OrderStatusDisplay(
    val code: String,
    val label: String,
    val badgeText: String,
    val tone: OrderStatusTone,
)

object Formatters {
    private val spaceGroupingFormat: DecimalFormat by lazy {
        val symbols = DecimalFormatSymbols(Locale.US).apply {
            groupingSeparator = ' '
        }
        DecimalFormat("#,###", symbols).apply {
            isGroupingUsed = true
        }
    }

    /** Format numeric price into human-readable sum string e.g. "150 000 so'm". */
    fun formatPrice(amount: Double): String {
        val whole = amount.toLong()
        return "${spaceGroupingFormat.format(whole)} so'm"
    }

    fun formatPrice(amount: Long): String {
        return "${spaceGroupingFormat.format(amount)} so'm"
    }

    fun getOrderStatusDisplay(status: String): OrderStatusDisplay {
        return when (status.lowercase(Locale.ROOT)) {
            "pending" -> OrderStatusDisplay(
                code = "pending",
                label = "Yangi (Kutilmoqda)",
                badgeText = "⏳ Yangi (Kutilmoqda)",
                tone = OrderStatusTone.PENDING,
            )
            "processing" -> OrderStatusDisplay(
                code = "processing",
                label = "Jarayonda",
                badgeText = "⚙️ Jarayonda",
                tone = OrderStatusTone.PROCESSING,
            )
            "shipped" -> OrderStatusDisplay(
                code = "shipped",
                label = "Yetkazilmoqda",
                badgeText = "🚚 Yetkazilmoqda",
                tone = OrderStatusTone.SHIPPED,
            )
            "delivered" -> OrderStatusDisplay(
                code = "delivered",
                label = "Bajarildi (Yetkazib berildi)",
                badgeText = "✅ Bajarildi (Yetkazib berildi)",
                tone = OrderStatusTone.DELIVERED,
            )
            "cancelled" -> OrderStatusDisplay(
                code = "cancelled",
                label = "Bekor qilindi",
                badgeText = "❌ Bekor qilindi",
                tone = OrderStatusTone.CANCELLED,
            )
            else -> OrderStatusDisplay(
                code = status,
                label = status.replaceFirstChar { it.uppercase() },
                badgeText = status.replaceFirstChar { it.uppercase() },
                tone = OrderStatusTone.PENDING,
            )
        }
    }

    fun getRequestStatusLabel(status: String): String {
        return when (status.lowercase(Locale.ROOT)) {
            "pending" -> "⏳ Ko'rib chiqilmoqda"
            "approved" -> "✅ Tasdiqlangan"
            "rejected" -> "❌ Rad etilgan"
            else -> status
        }
    }
}
