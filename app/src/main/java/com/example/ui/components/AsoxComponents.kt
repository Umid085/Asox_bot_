package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.ui.theme.StatusError
import com.example.ui.theme.StatusInfo
import com.example.ui.theme.StatusSuccess
import com.example.ui.theme.StatusWarning
import com.example.util.OrderStatusTone

@Composable
fun StatusBadgePill(
    text: String,
    tone: OrderStatusTone,
    modifier: Modifier = Modifier,
) {
    val accent = when (tone) {
        OrderStatusTone.PENDING -> StatusWarning
        OrderStatusTone.PROCESSING -> StatusInfo
        OrderStatusTone.SHIPPED -> Color(0xFF7C3AED)
        OrderStatusTone.DELIVERED -> StatusSuccess
        OrderStatusTone.CANCELLED -> StatusError
    }
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(999.dp),
        color = accent.copy(alpha = 0.12f),
        border = BorderStroke(1.dp, accent.copy(alpha = 0.3f)),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
            color = accent,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
        )
    }
}

@Composable
fun RequestStatusChip(
    status: String,
    modifier: Modifier = Modifier,
) {
    val (label, tone) = when (status.lowercase()) {
        "approved" -> "✅ Tasdiqlangan" to OrderStatusTone.DELIVERED
        "rejected" -> "❌ Rad etilgan" to OrderStatusTone.CANCELLED
        else -> "⏳ Ko'rib chiqilmoqda" to OrderStatusTone.PENDING
    }
    StatusBadgePill(text = label, tone = tone, modifier = modifier)
}

@Composable
fun SectionHeader(
    title: String,
    icon: ImageVector? = null,
    trailing: (@Composable () -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.weight(1f),
        ) {
            if (icon != null) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(modifier = Modifier.width(8.dp))
            }
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.onBackground,
            )
        }
        if (trailing != null) {
            Box { trailing() }
        }
    }
}
