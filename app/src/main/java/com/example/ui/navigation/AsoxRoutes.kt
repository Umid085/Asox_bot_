package com.example.ui.navigation

import kotlinx.serialization.Serializable

@Serializable
sealed interface AsoxRoute {
    @Serializable
    data object Catalog : AsoxRoute

    @Serializable
    data class ProductDetail(val productId: String) : AsoxRoute

    @Serializable
    data object Cart : AsoxRoute

    @Serializable
    data object Applications : AsoxRoute

    @Serializable
    data object Profile : AsoxRoute

    @Serializable
    data object Admin : AsoxRoute
}
