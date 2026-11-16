package com.example.data.repository

import com.example.data.local.AsoxDao
import com.example.data.local.AsoxDatabase
import com.example.data.model.AppUserEntity
import com.example.data.model.BroadcastLogEntity
import com.example.data.model.CategoryEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.data.model.OrderEntity
import com.example.data.model.ProductEntity
import com.example.data.model.ShopEntity
import com.example.util.Security
import kotlinx.coroutines.flow.Flow
import java.util.UUID

sealed interface ShopLinkResult {
    data class Success(val shop: ShopEntity) : ShopLinkResult
    data object SecretNotConfigured : ShopLinkResult
    data object InvalidSignature : ShopLinkResult
    data object NotFound : ShopLinkResult
    data object AlreadyLinked : ShopLinkResult
}

class AsoxRepository(private val dao: AsoxDao) {
    val categories: Flow<List<CategoryEntity>> = dao.observeCategories()
    val products: Flow<List<ProductEntity>> = dao.observeProducts()
    val orders: Flow<List<OrderEntity>> = dao.observeOrders()
    val designerRequests: Flow<List<DesignerRequestEntity>> = dao.observeDesignerRequests()
    val courierRequests: Flow<List<CourierRequestEntity>> = dao.observeCourierRequests()
    val shops: Flow<List<ShopEntity>> = dao.observeShops()
    val users: Flow<List<AppUserEntity>> = dao.observeUsers()
    val broadcastLogs: Flow<List<BroadcastLogEntity>> = dao.observeBroadcastLogs()

    fun observeProduct(productId: String): Flow<ProductEntity?> = dao.observeProductById(productId)

    fun observeCurrentUser(userId: Long = AsoxDatabase.DEFAULT_USER_ID): Flow<AppUserEntity?> =
        dao.observeUserById(userId)

    suspend fun updateCurrentUser(
        userId: Long,
        fullName: String,
        username: String,
        phoneNumber: String,
    ) {
        dao.upsertUser(
            AppUserEntity(
                id = userId,
                fullName = fullName,
                username = username,
                phoneNumber = phoneNumber,
                lastSeenMillis = System.currentTimeMillis(),
            )
        )
    }

    suspend fun addProduct(
        name: String,
        price: Double,
        description: String,
        categoryId: String,
        imageUrl: String?,
    ): ProductEntity {
        val cleanImage = imageUrl?.trim().takeIf { !it.isNullOrEmpty() }
            ?: AsoxDatabase.DEFAULT_PRODUCT_IMAGE
        val product = ProductEntity(
            id = "prod_${UUID.randomUUID().toString().take(8)}",
            categoryId = categoryId,
            name = name.trim(),
            description = description.trim(),
            price = price,
            imageUrl = cleanImage,
            inStock = true,
            rating = 5.0,
            createdAtMillis = System.currentTimeMillis(),
        )
        dao.insertProduct(product)
        return product
    }

    suspend fun submitDesignerRequest(
        userId: Long,
        fullName: String,
        phoneNumber: String,
        username: String,
        specialty: String,
        portfolioUrl: String,
    ): DesignerRequestEntity {
        val reqId = "des_${System.currentTimeMillis() / 1000}_${UUID.randomUUID().toString().take(6)}"
        val entity = DesignerRequestEntity(
            id = reqId,
            userId = userId.toString(),
            fullName = fullName.trim(),
            phoneNumber = phoneNumber,
            telegramUsername = username.trim(),
            specialty = specialty.trim(),
            portfolioUrl = portfolioUrl.trim(),
            status = "pending",
        )
        dao.insertDesignerRequest(entity)
        return entity
    }

    suspend fun submitCourierRequest(
        userId: Long,
        fullName: String,
        phoneNumber: String,
        username: String,
        city: String,
        vehicle: String,
    ): CourierRequestEntity {
        val reqId = "cou_${System.currentTimeMillis() / 1000}_${UUID.randomUUID().toString().take(6)}"
        val entity = CourierRequestEntity(
            id = reqId,
            userId = userId.toString(),
            fullName = fullName.trim(),
            phoneNumber = phoneNumber,
            telegramUsername = username.trim(),
            city = city.trim(),
            vehicle = vehicle.trim(),
            status = "pending",
        )
        dao.insertCourierRequest(entity)
        return entity
    }

    suspend fun updateOrderStatus(orderId: String, newStatus: String): Boolean {
        return dao.updateOrderStatus(orderId, newStatus) > 0
    }

    suspend fun updateDesignerRequestStatus(requestId: String, newStatus: String): Boolean {
        return dao.updateDesignerRequestStatus(requestId, newStatus) > 0
    }

    suspend fun updateCourierRequestStatus(requestId: String, newStatus: String): Boolean {
        return dao.updateCourierRequestStatus(requestId, newStatus) > 0
    }

    suspend fun linkShopWithToken(
        rawPayload: String,
        secret: String,
        userId: Long,
        username: String,
    ): ShopLinkResult {
        if (secret.isBlank()) {
            return ShopLinkResult.SecretNotConfigured
        }
        val (shopId, signature) = Security.parseShopPayload(rawPayload)
        if (shopId == null || !Security.verifyShopLinkToken(shopId, signature, secret)) {
            return ShopLinkResult.InvalidSignature
        }
        val shop = dao.getShopById(shopId) ?: return ShopLinkResult.NotFound
        val existingOwner = shop.linkedUserId.trim()
        if (existingOwner.isNotEmpty() && existingOwner != userId.toString()) {
            return ShopLinkResult.AlreadyLinked
        }
        val now = System.currentTimeMillis()
        dao.linkShop(shopId, userId.toString(), username, now)
        val updated = shop.copy(
            linkedUserId = userId.toString(),
            linkedUserHandle = username,
            linkedAtMillis = now,
        )
        return ShopLinkResult.Success(updated)
    }

    suspend fun recordBroadcast(messageText: String): BroadcastLogEntity {
        val userIds = dao.getAllUserIds()
        val total = userIds.size
        val log = BroadcastLogEntity(
            messageText = messageText.trim(),
            audienceCount = total,
            deliveredCount = total,
            failedCount = 0,
        )
        dao.insertBroadcastLog(log)
        return log
    }
}
