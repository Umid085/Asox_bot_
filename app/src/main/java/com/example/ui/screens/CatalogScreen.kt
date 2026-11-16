package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.OpenInNew
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.outlined.Inventory2
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.example.R
import com.example.data.model.CategoryEntity
import com.example.data.model.ProductEntity
import com.example.ui.theme.JetBrainsMono
import com.example.ui.theme.NavyHeroDeep
import com.example.ui.theme.StatusSuccess
import com.example.ui.viewmodel.CatalogUiState
import com.example.util.ExternalLinks
import com.example.util.Formatters

@Composable
fun CatalogScreen(
    uiState: CatalogUiState,
    onCategorySelected: (String?) -> Unit,
    onSearchQueryChanged: (String) -> Unit,
    onProductClick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current

    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 164.dp),
        modifier = modifier
            .fillMaxSize()
            .testTag("catalog_grid"),
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Hero Banner
        item(span = { GridItemSpan(maxLineSpan) }) {
            HeroBannerCard(
                onOpenWebsite = { ExternalLinks.openUrl(context, ExternalLinks.APP_STOREFRONT) },
            )
        }

        // Search Box
        item(span = { GridItemSpan(maxLineSpan) }) {
            OutlinedTextField(
                value = uiState.searchQuery,
                onValueChange = onSearchQueryChanged,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("catalog_search_input"),
                placeholder = { Text(stringResource(R.string.search_placeholder)) },
                leadingIcon = {
                    Icon(
                        imageVector = Icons.Default.Search,
                        contentDescription = "Qidiruv",
                    )
                },
                trailingIcon = {
                    if (uiState.searchQuery.isNotEmpty()) {
                        IconButton(
                            onClick = { onSearchQueryChanged("") },
                            modifier = Modifier.testTag("clear_search_button"),
                        ) {
                            Icon(
                                imageVector = Icons.Default.Clear,
                                contentDescription = "Tozalash",
                            )
                        }
                    }
                },
                singleLine = true,
                shape = RoundedCornerShape(16.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = MaterialTheme.colorScheme.surface,
                    unfocusedContainerColor = MaterialTheme.colorScheme.surface,
                ),
            )
        }

        // Category Filter Chips
        item(span = { GridItemSpan(maxLineSpan) }) {
            CategoryFilterRow(
                categories = uiState.categories,
                selectedCategoryId = uiState.selectedCategoryId,
                onCategorySelected = onCategorySelected,
            )
        }

        // Section summary
        item(span = { GridItemSpan(maxLineSpan) }) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                val activeCatName = uiState.categories
                    .firstOrNull { it.id == uiState.selectedCategoryId }
                    ?.let { "${it.icon} ${it.name}" }
                    ?: "🛍 Barcha mahsulotlar"
                Text(
                    text = activeCatName,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f),
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "${uiState.products.size} ta",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        // Empty state or products
        if (!uiState.isLoading && uiState.products.isEmpty()) {
            item(span = { GridItemSpan(maxLineSpan) }) {
                EmptyCatalogState(
                    query = uiState.searchQuery,
                    onReset = {
                        onSearchQueryChanged("")
                        onCategorySelected(null)
                    },
                )
            }
        } else {
            items(uiState.products, key = { it.id }) { product ->
                ProductCard(
                    product = product,
                    categoryIcon = uiState.categories
                        .firstOrNull { it.id == product.categoryId }
                        ?.icon ?: "🛍",
                    onClick = { onProductClick(product.id) },
                )
            }
        }
    }
}

@Composable
private fun HeroBannerCard(onOpenWebsite: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(176.dp),
        shape = RoundedCornerShape(24.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp),
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            Image(
                painter = painterResource(id = R.drawable.img_hero_banner),
                contentDescription = "ASOX Market studio banner",
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize(),
            )
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.horizontalGradient(
                            colors = listOf(
                                NavyHeroDeep.copy(alpha = 0.92f),
                                NavyHeroDeep.copy(alpha = 0.68f),
                                NavyHeroDeep.copy(alpha = 0.28f),
                            )
                        )
                    )
            )
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(18.dp),
                verticalArrangement = Arrangement.SpaceBetween,
            ) {
                Surface(
                    shape = RoundedCornerShape(999.dp),
                    color = Color.White.copy(alpha = 0.16f),
                    border = BorderStroke(1.dp, Color.White.copy(alpha = 0.25f)),
                ) {
                    Text(
                        text = "Samarqand • O'zbekiston bo'ylab",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    )
                }

                Column {
                    Text(
                        text = stringResource(R.string.catalog_hero_title),
                        style = MaterialTheme.typography.headlineMedium,
                        color = Color.White,
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = stringResource(R.string.catalog_hero_subtitle),
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.White.copy(alpha = 0.88f),
                        maxLines = 2,
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    AssistChip(
                        onClick = onOpenWebsite,
                        modifier = Modifier.testTag("hero_open_website_button"),
                        label = {
                            Text(
                                text = "asox.uz/app",
                                style = MaterialTheme.typography.labelMedium,
                                color = Color.White,
                            )
                        },
                        trailingIcon = {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.OpenInNew,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(16.dp),
                            )
                        },
                        colors = androidx.compose.material3.AssistChipDefaults.assistChipColors(
                            containerColor = MaterialTheme.colorScheme.primary,
                        ),
                        border = null,
                    )
                }
            }
        }
    }
}

@Composable
private fun CategoryFilterRow(
    categories: List<CategoryEntity>,
    selectedCategoryId: String?,
    onCategorySelected: (String?) -> Unit,
) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        item {
            FilterChip(
                selected = selectedCategoryId == null,
                onClick = { onCategorySelected(null) },
                modifier = Modifier.testTag("category_chip_all"),
                label = { Text("🛍 ${stringResource(R.string.all_categories)}") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = MaterialTheme.colorScheme.primary,
                    selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
                ),
            )
        }
        items(categories, key = { it.id }) { cat ->
            val shortName = cat.name.substringBefore("(").trim()
            FilterChip(
                selected = selectedCategoryId == cat.id,
                onClick = {
                    onCategorySelected(if (selectedCategoryId == cat.id) null else cat.id)
                },
                modifier = Modifier.testTag("category_chip_${cat.id}"),
                label = { Text("${cat.icon} $shortName") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = MaterialTheme.colorScheme.primary,
                    selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
                ),
            )
        }
    }
}

@Composable
private fun ProductCard(
    product: ProductEntity,
    categoryIcon: String,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .clickable(onClick = onClick)
            .testTag("product_card_${product.id}"),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(4f / 3f)
                    .background(MaterialTheme.colorScheme.surfaceVariant),
            ) {
                AsyncImage(
                    model = product.imageUrl,
                    contentDescription = product.name,
                    placeholder = painterResource(id = R.drawable.img_merch_placeholder),
                    error = painterResource(id = R.drawable.img_merch_placeholder),
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize(),
                )
                Surface(
                    modifier = Modifier
                        .align(Alignment.TopStart)
                        .padding(8.dp),
                    shape = CircleShape,
                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                ) {
                    Text(
                        text = categoryIcon,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                    )
                }
                if (product.rating > 0) {
                    Surface(
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .padding(8.dp),
                        shape = RoundedCornerShape(999.dp),
                        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                imageVector = Icons.Default.Star,
                                contentDescription = "Reyting",
                                tint = MaterialTheme.colorScheme.secondary,
                                modifier = Modifier.size(13.dp),
                            )
                            Spacer(modifier = Modifier.width(3.dp))
                            Text(
                                text = String.format("%.1f", product.rating),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                    }
                }
            }

            Column(
                modifier = Modifier.padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text(
                    text = product.name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 2,
                    minLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = product.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = Formatters.formatPrice(product.price),
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontFamily = JetBrainsMono,
                            fontWeight = FontWeight.Bold,
                        ),
                        color = MaterialTheme.colorScheme.primary,
                    )
                    if (product.inStock) {
                        Text(
                            text = "Mavjud",
                            style = MaterialTheme.typography.labelSmall,
                            color = StatusSuccess,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun EmptyCatalogState(
    query: String,
    onReset: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 20.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f)),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Icon(
                imageVector = Icons.Outlined.Inventory2,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(42.dp),
            )
            Text(
                text = if (query.isNotBlank()) {
                    "'$query' bo'yicha hech qanday mahsulot topilmadi."
                } else {
                    "Ushbu kategoriyada hali mahsulotlar mavjud emas."
                },
                style = MaterialTheme.typography.titleMedium,
            )
            AssistChip(
                onClick = onReset,
                label = { Text("Filtrni tozalash") },
            )
        }
    }
}
