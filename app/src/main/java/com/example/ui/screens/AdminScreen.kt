package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddBox
import androidx.compose.material.icons.filled.Campaign
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Group
import androidx.compose.material.icons.filled.Inventory
import androidx.compose.material.icons.filled.Payments
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.data.model.BroadcastLogEntity
import com.example.data.model.CategoryEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.data.model.OrderEntity
import com.example.ui.components.RequestStatusChip
import com.example.ui.components.StatusBadgePill
import com.example.ui.theme.JetBrainsMono
import com.example.ui.theme.StatusError
import com.example.ui.theme.StatusSuccess
import com.example.ui.viewmodel.AdminStats
import com.example.util.Formatters

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun AdminScreen(
    stats: AdminStats,
    orders: List<OrderEntity>,
    designerRequests: List<DesignerRequestEntity>,
    courierRequests: List<CourierRequestEntity>,
    categories: List<CategoryEntity>,
    broadcastLogs: List<BroadcastLogEntity>,
    onUpdateOrderStatus: (String, String) -> Unit,
    onUpdateDesignerStatus: (String, String) -> Unit,
    onUpdateCourierStatus: (String, String) -> Unit,
    onAddProduct: (String, String, String, String, String?, () -> Unit) -> Unit,
    onSendBroadcast: (String, () -> Unit) -> Unit,
    modifier: Modifier = Modifier,
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
    val tabs = listOf("📦 Buyurtmalar", "📋 Arizalar", "➕ Mahsulot", "📢 Broadcast")

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .testTag("admin_screen_list"),
        contentPadding = PaddingValues(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        // KPI Dashboard
        item {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 720.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Text(
                    text = "ASOX Market Admin Paneli",
                    style = MaterialTheme.typography.headlineMedium,
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    StatKpiCard(
                        title = "Foydalanuvchilar",
                        value = "${stats.usersCount} ta",
                        icon = Icons.Default.Group,
                        modifier = Modifier.weight(1f),
                    )
                    StatKpiCard(
                        title = "Buyurtmalar",
                        value = "${stats.ordersCount} ta",
                        icon = Icons.Default.Inventory,
                        modifier = Modifier.weight(1f),
                    )
                    StatKpiCard(
                        title = "Tushum",
                        value = Formatters.formatPrice(stats.deliveredRevenue),
                        icon = Icons.Default.Payments,
                        modifier = Modifier.weight(1.3f),
                    )
                }

                ScrollableTabRow(
                    selectedTabIndex = selectedTab,
                    edgePadding = 0.dp,
                ) {
                    tabs.forEachIndexed { idx, label ->
                        Tab(
                            selected = selectedTab == idx,
                            onClick = { selectedTab = idx },
                            modifier = Modifier.testTag("admin_tab_$idx"),
                            text = { Text(label) },
                        )
                    }
                }
            }
        }

        when (selectedTab) {
            0 -> {
                if (orders.isEmpty()) {
                    item {
                        Text(
                            text = "Hozircha buyurtmalar yo'q.",
                            style = MaterialTheme.typography.bodyLarge,
                        )
                    }
                } else {
                    items(orders, key = { it.id }) { order ->
                        AdminOrderCard(
                            order = order,
                            onUpdateStatus = { newStatus -> onUpdateOrderStatus(order.id, newStatus) },
                        )
                    }
                }
            }

            1 -> {
                item {
                    Text(
                        text = "🎨 Dizaynerlik arizalari (${designerRequests.size} ta)",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier
                            .fillMaxWidth()
                            .widthIn(max = 720.dp),
                    )
                }
                items(designerRequests, key = { it.id }) { req ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .widthIn(max = 720.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(
                                    text = "🎨 ${req.fullName}",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                )
                                RequestStatusChip(status = req.status)
                            }
                            Text("📞 ${req.phoneNumber} • 🎯 ${req.specialty}", style = MaterialTheme.typography.bodySmall)
                            Text("🌐 ${req.portfolioUrl}", style = MaterialTheme.typography.bodySmall)

                            if (req.status == "pending") {
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    modifier = Modifier.fillMaxWidth(),
                                ) {
                                    Button(
                                        onClick = { onUpdateDesignerStatus(req.id, "approved") },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("approve_des_${req.id}"),
                                        colors = ButtonDefaults.buttonColors(containerColor = StatusSuccess),
                                    ) {
                                        Icon(Icons.Default.Check, contentDescription = null)
                                        Spacer(Modifier.width(4.dp))
                                        Text("Tasdiqlash")
                                    }
                                    OutlinedButton(
                                        onClick = { onUpdateDesignerStatus(req.id, "rejected") },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("reject_des_${req.id}"),
                                        colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusError),
                                    ) {
                                        Icon(Icons.Default.Close, contentDescription = null)
                                        Spacer(Modifier.width(4.dp))
                                        Text("Rad etish")
                                    }
                                }
                            }
                        }
                    }
                }

                item {
                    Text(
                        text = "🛵 Kuryerlik arizalari (${courierRequests.size} ta)",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier
                            .fillMaxWidth()
                            .widthIn(max = 720.dp)
                            .padding(top = 8.dp),
                    )
                }
                items(courierRequests, key = { it.id }) { req ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .widthIn(max = 720.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(
                                    text = "🛵 ${req.fullName}",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                )
                                RequestStatusChip(status = req.status)
                            }
                            Text("📞 ${req.phoneNumber} • 📍 ${req.city}", style = MaterialTheme.typography.bodySmall)
                            Text("🚗 ${req.vehicle}", style = MaterialTheme.typography.bodySmall)

                            if (req.status == "pending") {
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    modifier = Modifier.fillMaxWidth(),
                                ) {
                                    Button(
                                        onClick = { onUpdateCourierStatus(req.id, "approved") },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("approve_cou_${req.id}"),
                                        colors = ButtonDefaults.buttonColors(containerColor = StatusSuccess),
                                    ) {
                                        Icon(Icons.Default.Check, contentDescription = null)
                                        Spacer(Modifier.width(4.dp))
                                        Text("Qo'shish")
                                    }
                                    OutlinedButton(
                                        onClick = { onUpdateCourierStatus(req.id, "rejected") },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("reject_cou_${req.id}"),
                                        colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusError),
                                    ) {
                                        Icon(Icons.Default.Close, contentDescription = null)
                                        Spacer(Modifier.width(4.dp))
                                        Text("Rad etish")
                                    }
                                }
                            }
                        }
                    }
                }
            }

            2 -> {
                item {
                    AddProductAdminCard(
                        categories = categories,
                        onAddProduct = onAddProduct,
                    )
                }
            }

            3 -> {
                item {
                    BroadcastAdminCard(
                        audienceCount = stats.usersCount,
                        onSendBroadcast = onSendBroadcast,
                    )
                }
                items(broadcastLogs, key = { it.id }) { log ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .widthIn(max = 720.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                text = log.messageText,
                                style = MaterialTheme.typography.bodyMedium,
                            )
                            Text(
                                text = "🟢 Yuborildi: ${log.deliveredCount}/${log.audienceCount} • 🔴 Xatolik: ${log.failedCount}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StatKpiCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium.copy(
                    fontFamily = JetBrainsMono,
                    fontWeight = FontWeight.Bold,
                ),
                maxLines = 1,
            )
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
            )
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun AdminOrderCard(
    order: OrderEntity,
    onUpdateStatus: (String) -> Unit,
) {
    val statusDisplay = Formatters.getOrderStatusDisplay(order.status)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .widthIn(max = 720.dp)
            .testTag("admin_order_card_${order.id}"),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column {
                    Text(
                        text = "Order #${order.id}",
                        style = MaterialTheme.typography.titleSmall.copy(
                            fontFamily = JetBrainsMono,
                            fontWeight = FontWeight.Bold,
                        ),
                    )
                    Text(
                        text = order.createdAt,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                StatusBadgePill(
                    text = statusDisplay.badgeText,
                    tone = statusDisplay.tone,
                )
            }

            Text(
                text = "👤 ${order.userName} (${order.phoneNumber})",
                style = MaterialTheme.typography.bodyMedium,
            )
            if (order.address.isNotBlank()) {
                Text(
                    text = "📍 ${order.address}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)

            order.items.forEach { item ->
                Text(
                    text = "• ${item.name} (${item.quantity}x)",
                    style = MaterialTheme.typography.bodySmall,
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = order.paymentMethod.ifBlank { "To'lov" },
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = Formatters.formatPrice(order.totalAmount),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontFamily = JetBrainsMono,
                        fontWeight = FontWeight.Bold,
                    ),
                    color = MaterialTheme.colorScheme.primary,
                )
            }

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                listOf(
                    "processing" to "⚙️ Jarayonda",
                    "shipped" to "🚚 Yetkazilmoqda",
                    "delivered" to "✅ Bajarildi",
                    "cancelled" to "❌ Bekor qilish",
                ).forEach { (statusCode, label) ->
                    FilterChip(
                        selected = order.status == statusCode,
                        onClick = { onUpdateStatus(statusCode) },
                        modifier = Modifier.testTag("order_${order.id}_$statusCode"),
                        label = { Text(label) },
                    )
                }
            }
        }
    }
}

@Composable
private fun AddProductAdminCard(
    categories: List<CategoryEntity>,
    onAddProduct: (String, String, String, String, String?, () -> Unit) -> Unit,
) {
    var name by rememberSaveable { mutableStateOf("") }
    var price by rememberSaveable { mutableStateOf("") }
    var description by rememberSaveable { mutableStateOf("") }
    var imageUrl by rememberSaveable { mutableStateOf("") }
    var selectedCatId by rememberSaveable(categories) {
        mutableStateOf(categories.firstOrNull()?.id ?: "cat_merch")
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .widthIn(max = 720.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(Icons.Default.AddBox, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                Text("Yangi mahsulot qo'shish", style = MaterialTheme.typography.titleMedium)
            }

            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Mahsulot nomi") },
                placeholder = { Text("Masalan: Hudi ASOX Oversize") },
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("admin_prod_name_input"),
            )

            OutlinedTextField(
                value = price,
                onValueChange = { price = it },
                label = { Text("Narxi (so'm)") },
                placeholder = { Text("Masalan: 185000") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("admin_prod_price_input"),
            )

            OutlinedTextField(
                value = description,
                onValueChange = { description = it },
                label = { Text("Qisqacha tavsif") },
                minLines = 2,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("admin_prod_desc_input"),
            )

            Text("Kategoriya:", style = MaterialTheme.typography.labelLarge)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(categories, key = { it.id }) { cat ->
                    FilterChip(
                        selected = selectedCatId == cat.id,
                        onClick = { selectedCatId = cat.id },
                        label = { Text("${cat.icon} ${cat.name.substringBefore("(").trim()}") },
                    )
                }
            }

            OutlinedTextField(
                value = imageUrl,
                onValueChange = { imageUrl = it },
                label = { Text("Rasm URL (ixtiyoriy)") },
                placeholder = { Text("Bo'sh qoldirilsa standart rasm ishlatiladi") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )

            Button(
                onClick = {
                    onAddProduct(name, price, description, selectedCatId, imageUrl) {
                        name = ""
                        price = ""
                        description = ""
                        imageUrl = ""
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("admin_add_product_submit"),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text("Katalogga qo'shish")
            }
        }
    }
}

@Composable
private fun BroadcastAdminCard(
    audienceCount: Int,
    onSendBroadcast: (String, () -> Unit) -> Unit,
) {
    var message by rememberSaveable { mutableStateOf("") }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .widthIn(max = 720.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(Icons.Default.Campaign, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                Text("Xabar tarqatish (Broadcast)", style = MaterialTheme.typography.titleMedium)
            }
            Text(
                text = "Barcha ro'yxatdan o'tgan foydalanuvchilarga ($audienceCount ta) e'lon yoki aksiya xabarini yuboring.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            OutlinedTextField(
                value = message,
                onValueChange = { message = it },
                label = { Text("Xabar matni") },
                placeholder = { Text("Masalan: Yangi yil aksiyasi! Barcha merchga 20% chegirma...") },
                minLines = 3,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("admin_broadcast_input"),
            )

            Button(
                onClick = {
                    onSendBroadcast(message) {
                        message = ""
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("admin_send_broadcast_button"),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text("Xabarni tarqatish")
            }
        }
    }
}
