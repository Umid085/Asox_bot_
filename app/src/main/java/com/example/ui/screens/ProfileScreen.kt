package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.OpenInNew
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material.icons.filled.SupportAgent
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.BuildConfig
import com.example.R
import com.example.data.model.AppUserEntity
import com.example.data.model.ShopEntity
import com.example.data.repository.ShopLinkResult
import com.example.ui.theme.JetBrainsMono
import com.example.ui.theme.StatusError
import com.example.ui.theme.StatusSuccess
import com.example.ui.theme.StatusWarning
import com.example.util.ExternalLinks
import com.example.util.Security

@Composable
fun ProfileScreen(
    currentUser: AppUserEntity?,
    shops: List<ShopEntity>,
    shopLinkResult: ShopLinkResult?,
    isAdminAuthorized: Boolean,
    hasConfiguredAdminIds: Boolean,
    initialDeepLinkPayload: String?,
    onUpdateProfile: (String, String, String) -> Boolean,
    onLinkShop: (String, String?) -> Unit,
    onToggleAdminPreview: (Boolean) -> Unit,
    onNavigateToAdmin: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var showEditDialog by remember { mutableStateOf(false) }

    var shopPayloadInput by rememberSaveable(initialDeepLinkPayload) {
        mutableStateOf(initialDeepLinkPayload.orEmpty())
    }
    var showSecurityTester by rememberSaveable { mutableStateOf(false) }
    var testSecretInput by rememberSaveable { mutableStateOf("") }
    var generatedTokenSample by remember { mutableStateOf<String?>(null) }

    val hasBuildSecret = BuildConfig.SHOP_LINK_SECRET.isNotBlank()

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .testTag("profile_screen_list"),
        contentPadding = PaddingValues(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // User Profile Card
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            Surface(
                                modifier = Modifier.size(52.dp),
                                shape = CircleShape,
                                color = MaterialTheme.colorScheme.primaryContainer,
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Person,
                                    contentDescription = "Foydalanuvchi profili",
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.padding(12.dp),
                                )
                            }
                            Column {
                                Text(
                                    text = currentUser?.fullName ?: "ASOX Mijoz",
                                    style = MaterialTheme.typography.titleLarge,
                                )
                                Text(
                                    text = "ID: ${currentUser?.id ?: 1001L}" +
                                        (currentUser?.username?.takeIf { it.isNotBlank() }
                                            ?.let { " • @$it" } ?: ""),
                                    style = MaterialTheme.typography.labelSmall,
                                    fontFamily = JetBrainsMono,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }

                        IconButton(
                            onClick = { showEditDialog = true },
                            modifier = Modifier.testTag("edit_profile_button"),
                        ) {
                            Icon(
                                imageVector = Icons.Default.Edit,
                                contentDescription = "Profilni tahrirlash",
                            )
                        }
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text(
                            text = "📱 Telefon",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            text = currentUser?.phoneNumber?.ifBlank { "Kiritilmagan" } ?: "Kiritilmagan",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium,
                        )
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "🌐 Rasmiy sayt",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        TextButton(
                            onClick = { ExternalLinks.openUrl(context, ExternalLinks.BASE_SITE) },
                        ) {
                            Text("asox.uz")
                            Spacer(modifier = Modifier.width(4.dp))
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.OpenInNew,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp),
                            )
                        }
                    }
                }
            }
        }

        // Seller Shop Linking (HMAC-SHA256 fail-closed)
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
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
                        Icon(
                            imageVector = Icons.Default.Storefront,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Text(
                            text = "Sotuvchi do'konini ulash",
                            style = MaterialTheme.typography.titleMedium,
                        )
                    }

                    Text(
                        text = "asox.uz sotuvchi kabinetidan olingan HMAC-imzoli havola (shop_<id>_<imzo>) orqali do'koningizni ulang.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )

                    if (!hasBuildSecret) {
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = StatusWarning.copy(alpha = 0.12f),
                            border = BorderStroke(1.dp, StatusWarning.copy(alpha = 0.3f)),
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Security,
                                    contentDescription = null,
                                    tint = StatusWarning,
                                    modifier = Modifier.size(18.dp),
                                )
                                Text(
                                    text = "SHOP_LINK_SECRET .env da sozlanmagan (fail-closed). Sinov uchun quyida lokal imzo kalitini kiritishingiz mumkin.",
                                    style = MaterialTheme.typography.bodySmall,
                                )
                            }
                        }
                    }

                    OutlinedTextField(
                        value = shopPayloadInput,
                        onValueChange = { shopPayloadInput = it },
                        label = { Text("Do'kon payload yoki havolasi") },
                        placeholder = { Text("shop_shop_samarkand_1_<16-hex-imzo>") },
                        singleLine = true,
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("shop_payload_input"),
                    )

                    Button(
                        onClick = {
                            onLinkShop(
                                shopPayloadInput,
                                testSecretInput.takeIf { !hasBuildSecret && it.isNotBlank() },
                            )
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp)
                            .testTag("link_shop_button"),
                        shape = RoundedCornerShape(12.dp),
                    ) {
                        Icon(Icons.Default.Link, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Do'konni ulash")
                    }

                    AnimatedVisibility(visible = shopLinkResult != null) {
                        val (msg, isOk) = when (shopLinkResult) {
                            is ShopLinkResult.Success ->
                                "✅ Do'koningiz muvaffaqiyatli ulandi: ${shopLinkResult.shop.name} (${shopLinkResult.shop.id})" to true
                            ShopLinkResult.SecretNotConfigured ->
                                "⚠️ SHOP_LINK_SECRET sozlanmagan — imzosiz ulash taqiqlangan (fail-closed)." to false
                            ShopLinkResult.InvalidSignature ->
                                "❌ Havola imzosi yaroqsiz. Faqat asox.uz kabinetidan olingan imzoli havola qabul qilinadi." to false
                            ShopLinkResult.NotFound ->
                                "❌ Bunday do'kon topilmadi." to false
                            ShopLinkResult.AlreadyLinked ->
                                "⛔️ Bu do'kon allaqachon boshqa akkauntga bog'langan." to false
                            null -> "" to false
                        }
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = (if (isOk) StatusSuccess else StatusError).copy(alpha = 0.1f),
                        ) {
                            Text(
                                text = msg,
                                style = MaterialTheme.typography.bodySmall,
                                color = if (isOk) StatusSuccess else StatusError,
                                modifier = Modifier.padding(12.dp),
                            )
                        }
                    }

                    TextButton(
                        onClick = { showSecurityTester = !showSecurityTester },
                        modifier = Modifier.testTag("toggle_hmac_helper"),
                    ) {
                        Text(if (showSecurityTester) "HMAC tekshiruv vositasini yopish" else "🔧 HMAC havola generatori (Lokal test)")
                    }

                    AnimatedVisibility(visible = showSecurityTester) {
                        Column(
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            if (!hasBuildSecret) {
                                OutlinedTextField(
                                    value = testSecretInput,
                                    onValueChange = { testSecretInput = it },
                                    label = { Text("Sinov SHOP_LINK_SECRET") },
                                    placeholder = { Text("masalan: test_secret") },
                                    singleLine = true,
                                    modifier = Modifier.fillMaxWidth(),
                                )
                            }
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                OutlinedButton(
                                    onClick = {
                                        val secret = BuildConfig.SHOP_LINK_SECRET.ifBlank { testSecretInput }
                                        if (secret.isNotBlank()) {
                                            val sig = Security.makeShopLinkToken("shop_samarkand_1", secret)
                                            val payload = "shop_shop_samarkand_1_$sig"
                                            shopPayloadInput = payload
                                            generatedTokenSample = payload
                                        }
                                    },
                                    modifier = Modifier.weight(1f),
                                ) {
                                    Text("Namuna imzo yaratish")
                                }
                            }
                            if (generatedTokenSample != null) {
                                Text(
                                    text = "Payload: $generatedTokenSample",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontFamily = JetBrainsMono,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                    Text(
                        text = "Platformadagi do'konlar:",
                        style = MaterialTheme.typography.labelLarge,
                    )
                    shops.forEach { shop ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(shop.name, style = MaterialTheme.typography.bodyMedium)
                                Text(
                                    text = "${shop.id} • ${shop.city}",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                            val linked = shop.linkedUserId.isNotBlank()
                            Text(
                                text = if (linked) "Ulangan (#${shop.linkedUserId})" else "Bo'sh",
                                style = MaterialTheme.typography.labelMedium,
                                color = if (linked) StatusSuccess else MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }

        // Contact / Support Card
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Icon(
                            imageVector = Icons.Default.SupportAgent,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Text(
                            text = "ASOX Market Qo'llab-quvvatlash",
                            style = MaterialTheme.typography.titleMedium,
                        )
                    }

                    SupportRow(
                        icon = Icons.Default.Phone,
                        label = stringResource(R.string.support_phone),
                        onClick = { ExternalLinks.openUrl(context, ExternalLinks.SUPPORT_PHONE_URI) },
                    )
                    SupportRow(
                        icon = Icons.AutoMirrored.Filled.OpenInNew,
                        label = "Telegram Support: ${stringResource(R.string.support_telegram)}",
                        onClick = { ExternalLinks.openUrl(context, ExternalLinks.TELEGRAM_SUPPORT) },
                    )
                    SupportRow(
                        icon = Icons.Default.LocationOn,
                        label = stringResource(R.string.support_address),
                        onClick = { ExternalLinks.openUrl(context, ExternalLinks.BASE_SITE) },
                    )
                }
            }
        }

        // Admin Access Card
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = 640.dp),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.35f),
                ),
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            modifier = Modifier.weight(1f),
                        ) {
                            Icon(
                                imageVector = Icons.Default.AdminPanelSettings,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                            )
                            Column {
                                Text(
                                    text = "Admin Boshqaruv Paneli",
                                    style = MaterialTheme.typography.titleSmall,
                                )
                                Text(
                                    text = if (hasConfiguredAdminIds) {
                                        "ADMIN_IDS bo'yicha raqamli tekshiruv faol."
                                    } else {
                                        "Demo rejim orqali admin boshqaruvini sinab ko'ring."
                                    },
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }

                        if (!hasConfiguredAdminIds) {
                            Switch(
                                checked = isAdminAuthorized,
                                onCheckedChange = onToggleAdminPreview,
                                modifier = Modifier.testTag("admin_preview_switch"),
                            )
                        }
                    }

                    if (isAdminAuthorized) {
                        Button(
                            onClick = onNavigateToAdmin,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(48.dp)
                                .testTag("open_admin_panel_button"),
                            shape = RoundedCornerShape(12.dp),
                        ) {
                            Text("⚙️ Admin Panelni ochish")
                        }
                    }
                }
            }
        }
    }

    if (showEditDialog) {
        var nameInput by remember { mutableStateOf(currentUser?.fullName.orEmpty()) }
        var usernameInput by remember { mutableStateOf(currentUser?.username.orEmpty()) }
        var phoneInput by remember { mutableStateOf(currentUser?.phoneNumber.orEmpty()) }

        AlertDialog(
            onDismissRequest = { showEditDialog = false },
            title = { Text("Profilni tahrirlash") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = nameInput,
                        onValueChange = { nameInput = it },
                        label = { Text("Ism va Familiya") },
                        singleLine = true,
                    )
                    OutlinedTextField(
                        value = usernameInput,
                        onValueChange = { usernameInput = it },
                        label = { Text("Username") },
                        singleLine = true,
                    )
                    OutlinedTextField(
                        value = phoneInput,
                        onValueChange = { phoneInput = it },
                        label = { Text("Telefon raqam") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                        singleLine = true,
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (onUpdateProfile(nameInput, usernameInput, phoneInput)) {
                            showEditDialog = false
                        }
                    }
                ) {
                    Text("Saqlash")
                }
            },
            dismissButton = {
                TextButton(onClick = { showEditDialog = false }) {
                    Text("Bekor qilish")
                }
            },
        )
    }
}

@Composable
private fun SupportRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(18.dp),
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}
