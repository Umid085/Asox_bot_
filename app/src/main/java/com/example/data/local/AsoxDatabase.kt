package com.example.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import androidx.sqlite.db.SupportSQLiteDatabase
import com.example.data.model.AppUserEntity
import com.example.data.model.BroadcastLogEntity
import com.example.data.model.CategoryEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.data.model.OrderConverters
import com.example.data.model.OrderEntity
import com.example.data.model.OrderItem
import com.example.data.model.ProductEntity
import com.example.data.model.ShopEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

@Database(
    entities = [
        CategoryEntity::class,
        ProductEntity::class,
        OrderEntity::class,
        DesignerRequestEntity::class,
        CourierRequestEntity::class,
        ShopEntity::class,
        AppUserEntity::class,
        BroadcastLogEntity::class,
    ],
    version = 1,
    exportSchema = false,
)
@TypeConverters(OrderConverters::class)
abstract class AsoxDatabase : RoomDatabase() {
    abstract fun asoxDao(): AsoxDao

    companion object {
        const val DEFAULT_USER_ID: Long = 1001L
        const val DEFAULT_PRODUCT_IMAGE = "https://asox.uz/icons/icon-512x512.png"

        @Volatile
        private var INSTANCE: AsoxDatabase? = null

        fun getInstance(context: Context): AsoxDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: buildDatabase(context.applicationContext).also { INSTANCE = it }
            }
        }

        private fun buildDatabase(context: Context): AsoxDatabase {
            val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
            return Room.databaseBuilder(
                context,
                AsoxDatabase::class.java,
                "asox_market.db",
            )
                .addCallback(object : Callback() {
                    override fun onCreate(db: SupportSQLiteDatabase) {
                        super.onCreate(db)
                        scope.launch {
                            seedInitialData(getInstance(context).asoxDao())
                        }
                    }
                })
                .build()
        }

        private suspend fun seedInitialData(dao: AsoxDao) {
            val now = System.currentTimeMillis()

            dao.insertCategories(
                listOf(
                    CategoryEntity("cat_merch", "Kiyimlar & Merch (Futbolka, Kepka, Panama)", "👕", 1),
                    CategoryEntity("cat_poligraphy", "Vizitkalar & Kichik Poligrafiya", "📇", 2),
                    CategoryEntity("cat_large_format", "Keng formatli bosma (Banner, Roll-up)", "🖼️", 3),
                    CategoryEntity("cat_souvenirs", "Suvenirlar (Krujka, Stiker, Ruchka)", "☕", 4),
                    CategoryEntity("cat_packaging", "Qadoqlash & Sumkalar", "📦", 5),
                )
            )

            dao.insertProducts(
                listOf(
                    ProductEntity(
                        id = "prod_kepka",
                        categoryId = "cat_merch",
                        name = "Kepka ASOX Premium (Bosma bilan)",
                        description = "100% paxta, metall fiksator, yuqori sifatli DTF yoki kashta bosma.",
                        price = 85000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.9,
                        createdAtMillis = now - 600_000L,
                    ),
                    ProductEntity(
                        id = "prod_panama",
                        categoryId = "cat_merch",
                        name = "Panama ASOX Yozgi Merch",
                        description = "Qulay va zamonaviy yozgi bosh kiyim, brending uchun tayyor.",
                        price = 95000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.8,
                        createdAtMillis = now - 500_000L,
                    ),
                    ProductEntity(
                        id = "prod_futbolka",
                        categoryId = "cat_merch",
                        name = "Futbolka Oversize Premium",
                        description = "Kompakt penye paxta 240g, yuvilganda o'chmaydigan bosma.",
                        price = 120000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 5.0,
                        createdAtMillis = now - 400_000L,
                    ),
                    ProductEntity(
                        id = "prod_vizitka",
                        categoryId = "cat_poligraphy",
                        name = "Vizitkalar to'plami (100 dona)",
                        description = "350g bo'rli qog'oz, ikki tomonlama to'liq rangli bosma + mot laminatsiya.",
                        price = 60000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.9,
                        createdAtMillis = now - 300_000L,
                    ),
                    ProductEntity(
                        id = "prod_banner",
                        categoryId = "cat_large_format",
                        name = "Banner bosish (Frontlit 440g, 1 m²)",
                        description = "Tashqi reklama uchun yomg'ir va quyoshga chidamli banner bosma.",
                        price = 35000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.8,
                        createdAtMillis = now - 200_000L,
                    ),
                    ProductEntity(
                        id = "prod_krujka",
                        categoryId = "cat_souvenirs",
                        name = "Logotipli Keramika Krujka (330ml)",
                        description = "Sublimatsion sifatli bosma, idish yuvish mashinasiga chidamli.",
                        price = 45000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.9,
                        createdAtMillis = now - 100_000L,
                    ),
                    ProductEntity(
                        id = "prod_eko_sumka",
                        categoryId = "cat_packaging",
                        name = "Eko Shoper Sumka (Brendli)",
                        description = "Mustahkam byaz mato, korporativ tadbirlar va do'konlar uchun logotipli qadoqlash.",
                        price = 42000.0,
                        imageUrl = DEFAULT_PRODUCT_IMAGE,
                        inStock = true,
                        rating = 4.7,
                        createdAtMillis = now - 50_000L,
                    ),
                )
            )

            dao.insertUsers(
                listOf(
                    AppUserEntity(
                        id = DEFAULT_USER_ID,
                        fullName = "ASOX Mijoz",
                        username = "asox_user",
                        phoneNumber = "+998901234567",
                        isAdmin = false,
                        lastSeenMillis = now,
                    ),
                    AppUserEntity(
                        id = 1002L,
                        fullName = "Ali Valiyev",
                        username = "ali_v",
                        phoneNumber = "+998901112233",
                        lastSeenMillis = now - 3_600_000L,
                    ),
                    AppUserEntity(
                        id = 1003L,
                        fullName = "Dilnoza Karimova",
                        username = "dilnoza_k",
                        phoneNumber = "+998935556677",
                        lastSeenMillis = now - 7_200_000L,
                    ),
                )
            )

            dao.insertOrders(
                listOf(
                    OrderEntity(
                        id = "ASOX-2050",
                        userId = 1003L,
                        userName = "Dilnoza Karimova",
                        phoneNumber = "+998935556677",
                        address = "Samarqand shahri, Mirzo Ulug'bek ko'chasi, 18",
                        paymentMethod = "💳 Payme",
                        items = listOf(
                            OrderItem("Banner bosish (Frontlit 440g, 1 m²)", 3, 35000.0),
                            OrderItem("Vizitkalar to'plami (100 dona)", 2, 60000.0),
                        ),
                        totalAmount = 225000.0,
                        status = "processing",
                        createdAt = "2026-11-16 11:40",
                        createdAtMillis = now - 1_800_000L,
                    ),
                    OrderEntity(
                        id = "ASOX-2049",
                        userId = 1002L,
                        userName = "Ali Valiyev",
                        phoneNumber = "+998901112233",
                        address = "Samarqand, Gagarin ko'chasi, 60",
                        paymentMethod = "💳 Click",
                        items = listOf(
                            OrderItem("Kepka ASOX Premium (Bosma bilan)", 2, 85000.0),
                        ),
                        totalAmount = 170000.0,
                        status = "delivered",
                        createdAt = "2026-11-15 16:20",
                        createdAtMillis = now - 86_400_000L,
                    ),
                    OrderEntity(
                        id = "ASOX-2048",
                        userId = DEFAULT_USER_ID,
                        userName = "Sardorbek Rustamov",
                        phoneNumber = "+998914445566",
                        address = "Toshkent shahri, Chilonzor 9-kvartal",
                        paymentMethod = "💵 Naqd",
                        items = listOf(
                            OrderItem("Futbolka Oversize Premium", 2, 120000.0),
                            OrderItem("Logotipli Keramika Krujka (330ml)", 3, 45000.0),
                        ),
                        totalAmount = 375000.0,
                        status = "pending",
                        createdAt = "2026-11-16 09:15",
                        createdAtMillis = now - 900_000L,
                    ),
                )
            )

            dao.insertShops(
                listOf(
                    ShopEntity(
                        id = "shop_samarkand_1",
                        name = "ASOX Samarqand Poligrafiya",
                        city = "Samarqand",
                    ),
                    ShopEntity(
                        id = "shop_tashkent_merch",
                        name = "Toshkent Merch Studiyasi",
                        city = "Toshkent",
                    ),
                    ShopEntity(
                        id = "shop_bukhara_print",
                        name = "Buxoro Print Hub",
                        city = "Buxoro",
                        linkedUserId = "9999",
                        linkedUserHandle = "@bukhara_owner",
                        linkedAtMillis = now - 172_800_000L,
                    ),
                )
            )

            dao.insertDesignerRequest(
                DesignerRequestEntity(
                    id = "des_1763290000_a1b2c3",
                    userId = "1002",
                    fullName = "Alisher Zokirov",
                    phoneNumber = "+998901234567",
                    telegramUsername = "alisher_design",
                    specialty = "👕 Merch & Kiyimlar",
                    portfolioUrl = "https://behance.net/alisher_art",
                    status = "pending",
                    createdAtMillis = now - 4_000_000L,
                )
            )

            dao.insertCourierRequest(
                CourierRequestEntity(
                    id = "cou_1763290100_d4e5f6",
                    userId = "1003",
                    fullName = "Otabek Fayzullayev",
                    phoneNumber = "+998939876543",
                    telegramUsername = "otabek_delivery",
                    city = "Samarqand shahri",
                    vehicle = "🛵 Skuter / Moped",
                    status = "pending",
                    createdAtMillis = now - 3_000_000L,
                )
            )
        }
    }
}
