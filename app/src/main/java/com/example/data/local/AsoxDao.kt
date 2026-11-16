package com.example.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.data.model.AppUserEntity
import com.example.data.model.BroadcastLogEntity
import com.example.data.model.CategoryEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.data.model.OrderEntity
import com.example.data.model.ProductEntity
import com.example.data.model.ShopEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface AsoxDao {
    // Categories
    @Query("SELECT * FROM categories ORDER BY sortOrder ASC")
    fun observeCategories(): Flow<List<CategoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCategories(categories: List<CategoryEntity>)

    // Products
    @Query("SELECT * FROM products ORDER BY createdAtMillis DESC")
    fun observeProducts(): Flow<List<ProductEntity>>

    @Query("SELECT * FROM products WHERE id = :productId LIMIT 1")
    fun observeProductById(productId: String): Flow<ProductEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: ProductEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProducts(products: List<ProductEntity>)

    // Orders
    @Query("SELECT * FROM orders ORDER BY createdAtMillis DESC")
    fun observeOrders(): Flow<List<OrderEntity>>

    @Query("UPDATE orders SET status = :newStatus WHERE id = :orderId")
    suspend fun updateOrderStatus(orderId: String, newStatus: String): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrders(orders: List<OrderEntity>)

    // Designer requests
    @Query("SELECT * FROM designer_requests ORDER BY createdAtMillis DESC")
    fun observeDesignerRequests(): Flow<List<DesignerRequestEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDesignerRequest(request: DesignerRequestEntity)

    @Query("UPDATE designer_requests SET status = :newStatus WHERE id = :requestId")
    suspend fun updateDesignerRequestStatus(requestId: String, newStatus: String): Int

    // Courier requests
    @Query("SELECT * FROM courier_requests ORDER BY createdAtMillis DESC")
    fun observeCourierRequests(): Flow<List<CourierRequestEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCourierRequest(request: CourierRequestEntity)

    @Query("UPDATE courier_requests SET status = :newStatus WHERE id = :requestId")
    suspend fun updateCourierRequestStatus(requestId: String, newStatus: String): Int

    // Shops
    @Query("SELECT * FROM shops ORDER BY name ASC")
    fun observeShops(): Flow<List<ShopEntity>>

    @Query("SELECT * FROM shops WHERE id = :shopId LIMIT 1")
    suspend fun getShopById(shopId: String): ShopEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertShops(shops: List<ShopEntity>)

    @Query(
        "UPDATE shops SET linkedUserId = :userId, linkedUserHandle = :handle, linkedAtMillis = :linkedAt WHERE id = :shopId"
    )
    suspend fun linkShop(shopId: String, userId: String, handle: String, linkedAt: Long)

    // Users
    @Query("SELECT * FROM app_users ORDER BY lastSeenMillis DESC")
    fun observeUsers(): Flow<List<AppUserEntity>>

    @Query("SELECT * FROM app_users WHERE id = :userId LIMIT 1")
    fun observeUserById(userId: Long): Flow<AppUserEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertUser(user: AppUserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<AppUserEntity>)

    @Query("SELECT id FROM app_users")
    suspend fun getAllUserIds(): List<Long>

    // Broadcast logs
    @Query("SELECT * FROM broadcast_logs ORDER BY sentAtMillis DESC")
    fun observeBroadcastLogs(): Flow<List<BroadcastLogEntity>>

    @Insert
    suspend fun insertBroadcastLog(log: BroadcastLogEntity)
}
