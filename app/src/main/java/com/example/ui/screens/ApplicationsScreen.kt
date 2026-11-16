package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Brush
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.DeliveryDining
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.data.model.AppUserEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.ui.components.RequestStatusChip
import com.example.ui.components.SectionHeader
import com.example.ui.theme.JetBrainsMono
import com.example.ui.theme.StatusSuccess
import com.example.util.Validators

private val DESIGNER_SPECIALTIES = listOf(
    "👕 Merch & Kiyimlar",
    "📇 Poligrafiya & Vizitkalar",
    "☕ Suvenirlar & Krujkalar",
    "🎨 Badiiy Illyustratsiya",
)

private val COURIER_CITIES = listOf(
    "Samarqand shahri",
    "Samarqand Poligrafiyasi",
    "Toshkent shahri",
    "Boshqa viloyat",
)

private val COURIER_VEHICLES = listOf(
    "🚗 Avtomobil",
    "🛵 Skuter / Moped",
    "🚲 Velosiped",
    "🚶 Piyoda",
)

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ApplicationsScreen(
    currentUser: AppUserEntity?,
    designerRequests: List<DesignerRequestEntity>,
    courierRequests: List<CourierRequestEntity>,
    onSubmitDesigner: (String, String, String, String, (DesignerRequestEntity) -> Unit) -> Unit,
    onSubmitCourier: (String, String, String, String, (CourierRequestEntity) -> Unit) -> Unit,
    modifier: Modifier = Modifier,
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) } // 0 = Designer, 1 = Courier
    var lastSubmittedId by remember { mutableStateOf<String?>(null) }

    // Designer form fields
    var desName by rememberSaveable(currentUser?.fullName) {
        mutableStateOf(currentUser?.fullName?.takeIf { it != "ASOX Mijoz" } ?: "")
    }
    var desPhone by rememberSaveable(currentUser?.phoneNumber) {
        mutableStateOf(currentUser?.phoneNumber ?: "")
    }
    var desSpecialty by rememberSaveable { mutableStateOf(DESIGNER_SPECIALTIES.first()) }
    var desPortfolio by rememberSaveable { mutableStateOf("") }

    // Courier form fields
    var couName by rememberSaveable(currentUser?.fullName) {
        mutableStateOf(currentUser?.fullName?.takeIf { it != "ASOX Mijoz" } ?: "")
    }
    var couPhone by rememberSaveable(currentUser?.phoneNumber) {
        mutableStateOf(currentUser?.phoneNumber ?: "")
    }
    var couCity by rememberSaveable { mutableStateOf(COURIER_CITIES.first()) }
    var couVehicle by rememberSaveable { mutableStateOf(COURIER_VEHICLES[1]) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .testTag("applications_list"),
        contentPadding = PaddingValues(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = "Hamkorlik Arizalari",
                    style = MaterialTheme.typography.headlineMedium,
                )
                Text(
                    text = "ASOX Market jamoasiga dizayner yoki kuryer sifatida qo'shiling.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                SingleChoiceSegmentedButtonRow(
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    SegmentedButton(
                        selected = selectedTab == 0,
                        onClick = {
                            selectedTab = 0
                            lastSubmittedId = null
                        },
                        shape = SegmentedButtonDefaults.itemShape(index = 0, count = 2),
                        modifier = Modifier.testTag("tab_designer_apply"),
                        icon = {
                            Icon(Icons.Default.Brush, contentDescription = null)
                        },
                    ) {
                        Text("Dizayner bo'lish")
                    }
                    SegmentedButton(
                        selected = selectedTab == 1,
                        onClick = {
                            selectedTab = 1
                            lastSubmittedId = null
                        },
                        shape = SegmentedButtonDefaults.itemShape(index = 1, count = 2),
                        modifier = Modifier.testTag("tab_courier_apply"),
                        icon = {
                            Icon(Icons.Default.DeliveryDining, contentDescription = null)
                        },
                    ) {
                        Text("Kuryer bo'lish")
                    }
                }
            }
        }

        item {
            AnimatedVisibility(visible = lastSubmittedId != null) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .widthIn(max = 640.dp),
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = StatusSuccess.copy(alpha = 0.12f)),
                    border = BorderStroke(1.dp, StatusSuccess.copy(alpha = 0.35f)),
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = StatusSuccess,
                        )
                        Column {
                            Text(
                                text = "Arizangiz muvaffaqiyatli qabul qilindi!",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                            )
                            Text(
                                text = "Ariza raqami: #${lastSubmittedId.orEmpty()}",
                                style = MaterialTheme.typography.labelSmall,
                                fontFamily = JetBrainsMono,
                            )
                        }
                    }
                }
            }
        }

        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            ) {
                if (selectedTab == 0) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        Text(
                            text = "🎨 ASOX Market Dizaynerlar Jamoasiga Qabul",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = "O'z dizaynlaringiz, illyustratsiyalaringiz va mualliflik merchingizni platformamizda soting.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )

                        OutlinedTextField(
                            value = desName,
                            onValueChange = { desName = it },
                            label = { Text("1. Ism va Familiya") },
                            placeholder = { Text("Masalan: Alisher Zokirov") },
                            singleLine = true,
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("designer_name_input"),
                        )

                        val normalizedDesPhone = remember(desPhone) {
                            Validators.normalizePhone(desPhone)
                        }
                        OutlinedTextField(
                            value = desPhone,
                            onValueChange = { desPhone = it },
                            label = { Text("2. Telefon raqam") },
                            placeholder = { Text("+998901234567") },
                            supportingText = {
                                if (desPhone.isNotBlank()) {
                                    Text(
                                        text = if (normalizedDesPhone != null) {
                                            "Formatlandi: $normalizedDesPhone"
                                        } else {
                                            "Raqam +998901234567 ko'rinishida bo'lishi kerak"
                                        },
                                        color = if (normalizedDesPhone != null) StatusSuccess else MaterialTheme.colorScheme.error,
                                    )
                                }
                            },
                            isError = desPhone.isNotBlank() && normalizedDesPhone == null,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                            singleLine = true,
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("designer_phone_input"),
                        )

                        Text(
                            text = "3. Asosiy dizayn yo'nalishingiz:",
                            style = MaterialTheme.typography.labelLarge,
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            DESIGNER_SPECIALTIES.forEach { spec ->
                                FilterChip(
                                    selected = desSpecialty == spec,
                                    onClick = { desSpecialty = spec },
                                    label = { Text(spec) },
                                )
                            }
                        }

                        OutlinedTextField(
                            value = desPortfolio,
                            onValueChange = { desPortfolio = it },
                            label = { Text("4. Portfolio havolasi yoki tajriba") },
                            placeholder = { Text("Behance, Instagram yoki qisqacha tajriba") },
                            minLines = 2,
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("designer_portfolio_input"),
                        )

                        Button(
                            onClick = {
                                onSubmitDesigner(desName, desPhone, desSpecialty, desPortfolio) { created ->
                                    lastSubmittedId = created.id
                                    desPortfolio = ""
                                }
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(50.dp)
                                .testTag("submit_designer_button"),
                            shape = RoundedCornerShape(14.dp),
                        ) {
                            Text("Dizaynerlik arizasini yuborish")
                        }
                    }
                } else {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        Text(
                            text = "🛵 ASOX Market Kuryerlik Xizmatiga Qabul",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = "Samarqand shahri va boshqa hududlar bo'yicha tezkor yetkazib berish xizmati a'zosi bo'ling.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )

                        OutlinedTextField(
                            value = couName,
                            onValueChange = { couName = it },
                            label = { Text("1. Ism va Familiya") },
                            placeholder = { Text("Masalan: Otabek Fayzullayev") },
                            singleLine = true,
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("courier_name_input"),
                        )

                        val normalizedCouPhone = remember(couPhone) {
                            Validators.normalizePhone(couPhone)
                        }
                        OutlinedTextField(
                            value = couPhone,
                            onValueChange = { couPhone = it },
                            label = { Text("2. Telefon raqam") },
                            placeholder = { Text("+998939876543") },
                            supportingText = {
                                if (couPhone.isNotBlank()) {
                                    Text(
                                        text = if (normalizedCouPhone != null) {
                                            "Formatlandi: $normalizedCouPhone"
                                        } else {
                                            "Raqam +998939876543 ko'rinishida bo'lishi kerak"
                                        },
                                        color = if (normalizedCouPhone != null) StatusSuccess else MaterialTheme.colorScheme.error,
                                    )
                                }
                            },
                            isError = couPhone.isNotBlank() && normalizedCouPhone == null,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                            singleLine = true,
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("courier_phone_input"),
                        )

                        Text(
                            text = "3. Qaysi hududda yetkazib bera olasiz?",
                            style = MaterialTheme.typography.labelLarge,
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            COURIER_CITIES.forEach { city ->
                                FilterChip(
                                    selected = couCity == city,
                                    onClick = { couCity = city },
                                    label = { Text("📍 $city") },
                                )
                            }
                        }

                        Text(
                            text = "4. Transport vositangiz turi:",
                            style = MaterialTheme.typography.labelLarge,
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            COURIER_VEHICLES.forEach { vehicle ->
                                FilterChip(
                                    selected = couVehicle == vehicle,
                                    onClick = { couVehicle = vehicle },
                                    label = { Text(vehicle) },
                                )
                            }
                        }

                        Button(
                            onClick = {
                                onSubmitCourier(couName, couPhone, couCity, couVehicle) { created ->
                                    lastSubmittedId = created.id
                                }
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(50.dp)
                                .testTag("submit_courier_button"),
                            shape = RoundedCornerShape(14.dp),
                        ) {
                            Text("Kuryerlik arizasini yuborish")
                        }
                    }
                }
            }
        }

        // Submitted Applications History
        item {
            SectionHeader(
                title = "Yuborilgan arizalar (${designerRequests.size + courierRequests.size})",
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp)
                    .padding(top = 8.dp),
            )
        }

        items(designerRequests, key = { it.id }) { req ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            ) {
                Column(
                    modifier = Modifier.padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "🎨 ${req.fullName}",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                        )
                        RequestStatusChip(status = req.status)
                    }
                    Text(
                        text = "${req.specialty} • ${req.phoneNumber}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        text = "Portfolio: ${req.portfolioUrl}",
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Text(
                        text = "#${req.id}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        items(courierRequests, key = { it.id }) { req ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            ) {
                Column(
                    modifier = Modifier.padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "🛵 ${req.fullName}",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                        )
                        RequestStatusChip(status = req.status)
                    }
                    Text(
                        text = "📍 ${req.city} • ${req.vehicle}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        text = "Tel: ${req.phoneNumber}",
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Text(
                        text = "#${req.id}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}
