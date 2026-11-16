package com.example.util

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import com.example.R

object ExternalLinks {
    const val BASE_SITE = "https://asox.uz"
    const val APP_STOREFRONT = "https://asox.uz/app"
    const val TELEGRAM_SUPPORT = "https://t.me/asox_support"
    const val SUPPORT_PHONE_URI = "tel:+998770483763"

    fun productUrl(productId: String): String = "$APP_STOREFRONT/product/$productId"

    fun openUrl(context: Context, url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        runCatching {
            context.startActivity(intent)
        }.onFailure {
            Toast.makeText(
                context,
                context.getString(R.string.error_no_browser),
                Toast.LENGTH_SHORT,
            ).show()
        }
    }
}
