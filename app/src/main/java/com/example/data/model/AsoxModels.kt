package com.example.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverter
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

@Serializable
data class OrderItem(
    val name: String,
    val quantity: Int = 1,
    val price: Double = 0.0,
)

class OrderConverters {
    private val json = Json { ignoreUnknownKeys = true }

    @TypeConverter
    fun fromOrderItems(items: List<OrderItem>): String = json.encodeToString(items)

    @TypeConverter
    fun toOrderItems(raw: String): List<OrderItem> =
        runCatching { json.decodeFromString<List<OrderItem>>(raw) }.getOrDefault(emptyList())
}

@Entity(tableName = "categories")
@Serializable
data class CategoryEntity(
    @PrimaryKey val id: String,
    val name: String,
    val icon: String = "🛍",
    val sortOrder: Int = 0,
)

@Entity(tableName = "products")
@Serializable
data class ProductEntity(
    @PrimaryKey val id: String,
    val categoryId: String,
    val name: String,
    val description: String,
    val price: Double,
    val imageUrl: String,
    val inStock: Boolean = true,
    val rating: Double = 4.9,
    val createdAtMillis: Long = System.currentTimeMillis(),
)

@Entity(tableName = "orders")
@Serializable
data class OrderEntity(
    @PrimaryKey val id: String,
    val userId: Long,
    val userName: String,
    val phoneNumber: String,
    val address: String,
    val paymentMethod: String,
    val items: List<OrderItem>,
    val totalAmount: Double,
    val status: String = "pending",
    val createdAt: String,
    val createdAtMillis: Long = System.currentTimeMillis(),
)

@Entity(tableName = "designer_requests")
@Serializable
data class DesignerRequestEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val fullName: String,
    val phoneNumber: String,
    val telegramUsername: String = "",
    val specialty: String,
    val portfolioUrl: String,
    val status: String = "pending",
    val createdAtMillis: Long = System.currentTimeMillis(),
)

@Entity(tableName = "courier_requests")
@Serializable
data class CourierRequestEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val fullName: String,
    val phoneNumber: String,
    val telegramUsername: String = "",
    val city: String,
    val vehicle: String,
    val status: String = "pending",
    val createdAtMillis: Long = System.currentTimeMillis(),
)

@Entity(tableName = "shops")
@Serializable
data class ShopEntity(
    @PrimaryKey val id: String,
    val name: String,
    val city: String,
    val linkedUserId: String = "",
    val linkedUserHandle: String = "",
    val linkedAtMillis: Long? = null,
)

@Entity(tableName = "app_users")
@Serializable
data class AppUserEntity(
    @PrimaryKey val id: Long,
    val fullName: String,
    val username: String = "",
    val phoneNumber: String = "",
    val isAdmin: Boolean = false,
    val lastSeenMillis: Long = System.currentTimeMillis(),
)

@Entity(tableName = "broadcast_logs")
@Serializable
data class BroadcastLogEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val messageText: String,
    val audienceCount: Int,
    val deliveredCount: Int,
    val failedCount: Int,
    val sentAtMillis: Long = System.currentTimeMillis(),
)
