package com.example

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Assignment
import androidx.compose.material.icons.automirrored.outlined.Assignment
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material.icons.outlined.AdminPanelSettings
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.ShoppingCart
import androidx.compose.material.icons.outlined.Storefront
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.toRoute
import com.example.ui.navigation.AsoxRoute
import com.example.ui.screens.AdminScreen
import com.example.ui.screens.ApplicationsScreen
import com.example.ui.screens.CartRedirectScreen
import com.example.ui.screens.CatalogScreen
import com.example.ui.screens.ProductDetailScreen
import com.example.ui.screens.ProfileScreen
import com.example.ui.theme.ASOXMarketTheme
import com.example.ui.viewmodel.AsoxViewModel

private data class TopDestination(
    val route: AsoxRoute,
    val labelRes: Int,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector,
    val testTag: String,
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val initialShopPayload = extractShopPayloadFromIntent(intent)

        setContent {
            ASOXMarketTheme {
                val app = application as AsoxApplication
                val viewModel: AsoxViewModel = viewModel(
                    factory = AsoxViewModel.Factory(app.repository)
                )
                AsoxMarketApp(
                    viewModel = viewModel,
                    initialDeepLinkPayload = initialShopPayload,
                )
            }
        }
    }

    private fun extractShopPayloadFromIntent(intent: Intent?): String? {
        val data = intent?.data ?: return null
        return data.getQueryParameter("payload")
            ?: data.getQueryParameter("start")
            ?: data.toString().takeIf { "shop_" in it }
    }
}

@Composable
fun AsoxMarketApp(
    viewModel: AsoxViewModel,
    initialDeepLinkPayload: String?,
) {
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }

    val catalogState by viewModel.catalogUiState.collectAsStateWithLifecycle()
    val currentUser by viewModel.currentUser.collectAsStateWithLifecycle()
    val orders by viewModel.orders.collectAsStateWithLifecycle()
    val designerRequests by viewModel.designerRequests.collectAsStateWithLifecycle()
    val courierRequests by viewModel.courierRequests.collectAsStateWithLifecycle()
    val shops by viewModel.shops.collectAsStateWithLifecycle()
    val broadcastLogs by viewModel.broadcastLogs.collectAsStateWithLifecycle()
    val adminStats by viewModel.adminStats.collectAsStateWithLifecycle()
    val isAdminAuthorized by viewModel.isAdminAuthorized.collectAsStateWithLifecycle()
    val shopLinkResult by viewModel.shopLinkStatus.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.snackbarEvents.collect { message ->
            snackbarHostState.showSnackbar(message)
        }
    }

    LaunchedEffect(initialDeepLinkPayload) {
        if (!initialDeepLinkPayload.isNullOrBlank()) {
            navController.navigate(AsoxRoute.Profile) {
                launchSingleTop = true
            }
        }
    }

    val destinations = remember(isAdminAuthorized) {
        buildList {
            add(
                TopDestination(
                    route = AsoxRoute.Catalog,
                    labelRes = R.string.nav_catalog,
                    selectedIcon = Icons.Filled.Storefront,
                    unselectedIcon = Icons.Outlined.Storefront,
                    testTag = "nav_catalog",
                )
            )
            add(
                TopDestination(
                    route = AsoxRoute.Cart,
                    labelRes = R.string.nav_cart,
                    selectedIcon = Icons.Filled.ShoppingCart,
                    unselectedIcon = Icons.Outlined.ShoppingCart,
                    testTag = "nav_cart",
                )
            )
            add(
                TopDestination(
                    route = AsoxRoute.Applications,
                    labelRes = R.string.nav_apply,
                    selectedIcon = Icons.AutoMirrored.Filled.Assignment,
                    unselectedIcon = Icons.AutoMirrored.Outlined.Assignment,
                    testTag = "nav_apply",
                )
            )
            add(
                TopDestination(
                    route = AsoxRoute.Profile,
                    labelRes = R.string.nav_profile,
                    selectedIcon = Icons.Filled.Person,
                    unselectedIcon = Icons.Outlined.Person,
                    testTag = "nav_profile",
                )
            )
            if (isAdminAuthorized) {
                add(
                    TopDestination(
                        route = AsoxRoute.Admin,
                        labelRes = R.string.nav_admin,
                        selectedIcon = Icons.Filled.AdminPanelSettings,
                        unselectedIcon = Icons.Outlined.AdminPanelSettings,
                        testTag = "nav_admin",
                    )
                )
            }
        }
    }

    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    val isDetailRoute = currentDestination?.hasRoute<AsoxRoute.ProductDetail>() == true

    fun navigateTopLevel(target: AsoxRoute) {
        navController.navigate(target) {
            popUpTo(navController.graph.findStartDestination().id) {
                saveState = true
            }
            launchSingleTop = true
            restoreState = true
        }
    }

    BoxWithConstraints(modifier = Modifier.fillMaxSize()) {
        val useRail = maxWidth >= 600.dp

        Scaffold(
            contentWindowInsets = WindowInsets.safeDrawing,
            snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
            bottomBar = {
                if (!useRail && !isDetailRoute) {
                    NavigationBar {
                        destinations.forEach { dest ->
                            val selected = currentDestination?.hasRoute(dest.route::class) == true
                            NavigationBarItem(
                                selected = selected,
                                onClick = { navigateTopLevel(dest.route) },
                                icon = {
                                    Icon(
                                        imageVector = if (selected) dest.selectedIcon else dest.unselectedIcon,
                                        contentDescription = stringResource(dest.labelRes),
                                    )
                                },
                                label = { Text(stringResource(dest.labelRes)) },
                                modifier = Modifier.testTag(dest.testTag),
                            )
                        }
                    }
                }
            },
        ) { innerPadding ->
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            ) {
                if (useRail && !isDetailRoute) {
                    NavigationRail {
                        destinations.forEach { dest ->
                            val selected = currentDestination?.hasRoute(dest.route::class) == true
                            NavigationRailItem(
                                selected = selected,
                                onClick = { navigateTopLevel(dest.route) },
                                icon = {
                                    Icon(
                                        imageVector = if (selected) dest.selectedIcon else dest.unselectedIcon,
                                        contentDescription = stringResource(dest.labelRes),
                                    )
                                },
                                label = { Text(stringResource(dest.labelRes)) },
                                modifier = Modifier.testTag(dest.testTag),
                            )
                        }
                    }
                }

                NavHost(
                    navController = navController,
                    startDestination = AsoxRoute.Catalog,
                    modifier = Modifier.weight(1f),
                ) {
                    composable<AsoxRoute.Catalog> {
                        CatalogScreen(
                            uiState = catalogState,
                            onCategorySelected = viewModel::selectCategory,
                            onSearchQueryChanged = viewModel::updateSearchQuery,
                            onProductClick = { productId ->
                                navController.navigate(AsoxRoute.ProductDetail(productId))
                            },
                        )
                    }

                    composable<AsoxRoute.ProductDetail> { backStackEntry ->
                        val route = backStackEntry.toRoute<AsoxRoute.ProductDetail>()
                        val product by viewModel.observeProduct(route.productId)
                            .collectAsStateWithLifecycle(initialValue = null)
                        val category = catalogState.categories
                            .firstOrNull { it.id == product?.categoryId }

                        ProductDetailScreen(
                            product = product,
                            category = category,
                            onBack = { navController.popBackStack() },
                        )
                    }

                    composable<AsoxRoute.Cart> {
                        CartRedirectScreen(
                            onExploreCatalog = { navigateTopLevel(AsoxRoute.Catalog) },
                        )
                    }

                    composable<AsoxRoute.Applications> {
                        ApplicationsScreen(
                            currentUser = currentUser,
                            designerRequests = designerRequests,
                            courierRequests = courierRequests,
                            onSubmitDesigner = viewModel::submitDesignerApplication,
                            onSubmitCourier = viewModel::submitCourierApplication,
                        )
                    }

                    composable<AsoxRoute.Profile> {
                        ProfileScreen(
                            currentUser = currentUser,
                            shops = shops,
                            shopLinkResult = shopLinkResult,
                            isAdminAuthorized = isAdminAuthorized,
                            hasConfiguredAdminIds = viewModel.configuredAdminIds.isNotEmpty(),
                            initialDeepLinkPayload = initialDeepLinkPayload,
                            onUpdateProfile = viewModel::updateProfile,
                            onLinkShop = viewModel::linkShop,
                            onToggleAdminPreview = viewModel::setAdminPreviewEnabled,
                            onNavigateToAdmin = { navigateTopLevel(AsoxRoute.Admin) },
                        )
                    }

                    composable<AsoxRoute.Admin> {
                        AdminScreen(
                            stats = adminStats,
                            orders = orders,
                            designerRequests = designerRequests,
                            courierRequests = courierRequests,
                            categories = catalogState.categories,
                            broadcastLogs = broadcastLogs,
                            onUpdateOrderStatus = viewModel::updateOrderStatus,
                            onUpdateDesignerStatus = viewModel::updateDesignerStatus,
                            onUpdateCourierStatus = viewModel::updateCourierStatus,
                            onAddProduct = viewModel::addProduct,
                            onSendBroadcast = viewModel::sendBroadcast,
                        )
                    }
                }
            }
        }
    }
}
