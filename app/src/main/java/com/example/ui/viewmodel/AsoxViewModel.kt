package com.example.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.BuildConfig
import com.example.data.local.AsoxDatabase
import com.example.data.model.AppUserEntity
import com.example.data.model.BroadcastLogEntity
import com.example.data.model.CategoryEntity
import com.example.data.model.CourierRequestEntity
import com.example.data.model.DesignerRequestEntity
import com.example.data.model.OrderEntity
import com.example.data.model.ProductEntity
import com.example.data.model.ShopEntity
import com.example.data.repository.AsoxRepository
import com.example.data.repository.ShopLinkResult
import com.example.util.Formatters
import com.example.util.Security
import com.example.util.Validators
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class CatalogUiState(
    val categories: List<CategoryEntity> = emptyList(),
    val products: List<ProductEntity> = emptyList(),
    val selectedCategoryId: String? = null,
    val searchQuery: String = "",
    val isLoading: Boolean = true,
)

data class AdminStats(
    val usersCount: Int = 0,
    val ordersCount: Int = 0,
    val deliveredRevenue: Double = 0.0,
)

class AsoxViewModel(private val repository: AsoxRepository) : ViewModel() {

    private val _selectedCategoryId = MutableStateFlow<String?>(null)
    private val _searchQuery = MutableStateFlow("")
    private val _adminPreviewEnabled = MutableStateFlow(false)

    private val _snackbarEvents = MutableSharedFlow<String>(extraBufferCapacity = 8)
    val snackbarEvents: SharedFlow<String> = _snackbarEvents.asSharedFlow()

    private val _shopLinkStatus = MutableStateFlow<ShopLinkResult?>(null)
    val shopLinkStatus: StateFlow<ShopLinkResult?> = _shopLinkStatus.asStateFlow()

    val categories: StateFlow<List<CategoryEntity>> = repository.categories.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val catalogUiState: StateFlow<CatalogUiState> = combine(
        repository.categories,
        repository.products,
        _selectedCategoryId,
        _searchQuery,
    ) { cats, prods, selectedCat, query ->
        val trimmedQuery = query.trim().lowercase()
        val filtered = prods.filter { product ->
            val matchesCat = selectedCat == null || product.categoryId == selectedCat
            val matchesQuery = trimmedQuery.isEmpty() ||
                product.name.lowercase().contains(trimmedQuery) ||
                product.description.lowercase().contains(trimmedQuery)
            matchesCat && matchesQuery
        }
        CatalogUiState(
            categories = cats,
            products = filtered,
            selectedCategoryId = selectedCat,
            searchQuery = query,
            isLoading = false,
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = CatalogUiState(),
    )

    val currentUser: StateFlow<AppUserEntity?> = repository
        .observeCurrentUser(AsoxDatabase.DEFAULT_USER_ID)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null,
        )

    val configuredAdminIds: Set<Long> = Security.parseAdminIds(BuildConfig.ADMIN_IDS)

    val isAdminAuthorized: StateFlow<Boolean> = combine(
        currentUser,
        _adminPreviewEnabled,
    ) { user, previewEnabled ->
        val uid = user?.id ?: AsoxDatabase.DEFAULT_USER_ID
        Security.isAdminUser(uid, configuredAdminIds) || previewEnabled
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = Security.isAdminUser(AsoxDatabase.DEFAULT_USER_ID, configuredAdminIds),
    )

    val orders: StateFlow<List<OrderEntity>> = repository.orders.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val designerRequests: StateFlow<List<DesignerRequestEntity>> = repository.designerRequests.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val courierRequests: StateFlow<List<CourierRequestEntity>> = repository.courierRequests.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val shops: StateFlow<List<ShopEntity>> = repository.shops.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val broadcastLogs: StateFlow<List<BroadcastLogEntity>> = repository.broadcastLogs.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList(),
    )

    val adminStats: StateFlow<AdminStats> = combine(
        repository.users,
        repository.orders,
    ) { userList, orderList ->
        val deliveredTotal = orderList
            .filter { it.status.equals("delivered", ignoreCase = true) }
            .sumOf { it.totalAmount }
        AdminStats(
            usersCount = userList.size,
            ordersCount = orderList.size,
            deliveredRevenue = deliveredTotal,
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = AdminStats(),
    )

    fun observeProduct(productId: String): Flow<ProductEntity?> = repository.observeProduct(productId)

    fun selectCategory(categoryId: String?) {
        _selectedCategoryId.value = categoryId
    }

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun setAdminPreviewEnabled(enabled: Boolean) {
        _adminPreviewEnabled.value = enabled
    }

    fun updateProfile(fullName: String, username: String, rawPhone: String): Boolean {
        val validName = Validators.requireNonBlank(fullName)
        if (validName == null) {
            _snackbarEvents.tryEmit("Iltimos, ism va familiyangizni kiriting.")
            return false
        }
        val normalizedPhone = if (rawPhone.isBlank()) "" else {
            Validators.normalizePhone(rawPhone) ?: run {
                _snackbarEvents.tryEmit("Telefon raqami noto'g'ri (+998901234567 shaklida kiriting).")
                return false
            }
        }
        viewModelScope.launch {
            val uid = currentUser.value?.id ?: AsoxDatabase.DEFAULT_USER_ID
            repository.updateCurrentUser(
                userId = uid,
                fullName = validName,
                username = username.trim().removePrefix("@"),
                phoneNumber = normalizedPhone,
            )
            _snackbarEvents.emit("Profil ma'lumotlari saqlandi.")
        }
        return true
    }

    fun submitDesignerApplication(
        fullName: String,
        rawPhone: String,
        specialty: String,
        portfolioUrl: String,
        onSuccess: (DesignerRequestEntity) -> Unit,
    ) {
        val validName = Validators.requireNonBlank(fullName)
        val normalizedPhone = Validators.normalizePhone(rawPhone)
        val validSpecialty = Validators.requireNonBlank(specialty)
        val validPortfolio = Validators.requireNonBlank(portfolioUrl)

        when {
            validName == null -> _snackbarEvents.tryEmit("Ism va familiyangizni kiriting.")
            normalizedPhone == null -> _snackbarEvents.tryEmit("Telefon raqam noto'g'ri (+998901234567 shaklida kiriting).")
            validSpecialty == null -> _snackbarEvents.tryEmit("Dizayn yo'nalishini tanlang.")
            validPortfolio == null -> _snackbarEvents.tryEmit("Portfolio havolasi yoki tajribangizni kiriting.")
            else -> {
                viewModelScope.launch {
                    val user = currentUser.value
                    val created = repository.submitDesignerRequest(
                        userId = user?.id ?: AsoxDatabase.DEFAULT_USER_ID,
                        fullName = validName,
                        phoneNumber = normalizedPhone,
                        username = user?.username.orEmpty(),
                        specialty = validSpecialty,
                        portfolioUrl = validPortfolio,
                    )
                    _snackbarEvents.emit("Dizaynerlik arizangiz qabul qilindi: #${created.id}")
                    onSuccess(created)
                }
            }
        }
    }

    fun submitCourierApplication(
        fullName: String,
        rawPhone: String,
        city: String,
        vehicle: String,
        onSuccess: (CourierRequestEntity) -> Unit,
    ) {
        val validName = Validators.requireNonBlank(fullName)
        val normalizedPhone = Validators.normalizePhone(rawPhone)
        val cleanCity = Validators.requireNonBlank(city.replace("📍", ""))
        val validVehicle = Validators.requireNonBlank(vehicle)

        when {
            validName == null -> _snackbarEvents.tryEmit("Ism va familiyangizni kiriting.")
            normalizedPhone == null -> _snackbarEvents.tryEmit("Telefon raqam noto'g'ri (+998901234567 shaklida kiriting).")
            cleanCity == null -> _snackbarEvents.tryEmit("Yetkazib berish hududini tanlang.")
            validVehicle == null -> _snackbarEvents.tryEmit("Transport turini tanlang.")
            else -> {
                viewModelScope.launch {
                    val user = currentUser.value
                    val created = repository.submitCourierRequest(
                        userId = user?.id ?: AsoxDatabase.DEFAULT_USER_ID,
                        fullName = validName,
                        phoneNumber = normalizedPhone,
                        username = user?.username.orEmpty(),
                        city = cleanCity,
                        vehicle = validVehicle,
                    )
                    _snackbarEvents.emit("Kuryerlik arizangiz qabul qilindi: #${created.id}")
                    onSuccess(created)
                }
            }
        }
    }

    fun linkShop(rawPayload: String, overrideSecret: String? = null) {
        val effectiveSecret = overrideSecret?.takeIf { it.isNotBlank() }
            ?: BuildConfig.SHOP_LINK_SECRET
        viewModelScope.launch {
            val user = currentUser.value
            val result = repository.linkShopWithToken(
                rawPayload = rawPayload,
                secret = effectiveSecret,
                userId = user?.id ?: AsoxDatabase.DEFAULT_USER_ID,
                username = user?.username.orEmpty(),
            )
            _shopLinkStatus.value = result
            val msg = when (result) {
                is ShopLinkResult.Success -> "Do'kon muvaffaqiyatli ulandi: ${result.shop.name}"
                ShopLinkResult.SecretNotConfigured -> "SHOP_LINK_SECRET sozlanmagan — do'kon ulash o'chirilgan."
                ShopLinkResult.InvalidSignature -> "Havola imzosi yaroqsiz yoki eskirgan."
                ShopLinkResult.NotFound -> "Bunday do'kon topilmadi."
                ShopLinkResult.AlreadyLinked -> "Bu do'kon allaqachon boshqa akkauntga bog'langan."
            }
            _snackbarEvents.emit(msg)
        }
    }

    fun clearShopLinkStatus() {
        _shopLinkStatus.value = null
    }

    fun updateOrderStatus(orderId: String, newStatus: String) {
        viewModelScope.launch {
            val updated = repository.updateOrderStatus(orderId, newStatus)
            if (updated) {
                val badge = Formatters.getOrderStatusDisplay(newStatus).badgeText
                _snackbarEvents.emit("Buyurtma #$orderId holati o'zgartirildi: $badge")
            } else {
                _snackbarEvents.emit("Buyurtma topilmadi.")
            }
        }
    }

    fun updateDesignerStatus(requestId: String, newStatus: String) {
        viewModelScope.launch {
            val ok = repository.updateDesignerRequestStatus(requestId, newStatus)
            if (ok) {
                val msg = if (newStatus == "approved") "Dizayner arizasi tasdiqlandi!" else "Ariza rad etildi."
                _snackbarEvents.emit(msg)
            }
        }
    }

    fun updateCourierStatus(requestId: String, newStatus: String) {
        viewModelScope.launch {
            val ok = repository.updateCourierRequestStatus(requestId, newStatus)
            if (ok) {
                val msg = if (newStatus == "approved") "Kuryer arizasi tasdiqlandi!" else "Ariza rad etildi."
                _snackbarEvents.emit(msg)
            }
        }
    }

    fun addProduct(
        name: String,
        priceRaw: String,
        description: String,
        categoryId: String,
        imageUrl: String?,
        onSuccess: () -> Unit,
    ) {
        val validName = Validators.requireNonBlank(name)
        val priceDigits = Validators.parsePriceDigits(priceRaw)
        val validDesc = Validators.requireNonBlank(description)
        when {
            validName == null -> _snackbarEvents.tryEmit("Mahsulot nomini kiriting.")
            priceDigits == null || priceDigits <= 0 ->
                _snackbarEvents.tryEmit("Narxni faqat raqam ko'rinishida kiriting (masalan: 150000).")
            validDesc == null -> _snackbarEvents.tryEmit("Mahsulot tavsifini kiriting.")
            categoryId.isBlank() -> _snackbarEvents.tryEmit("Kategoriyani tanlang.")
            else -> {
                viewModelScope.launch {
                    val added = repository.addProduct(
                        name = validName,
                        price = priceDigits.toDouble(),
                        description = validDesc,
                        categoryId = categoryId,
                        imageUrl = imageUrl,
                    )
                    _snackbarEvents.emit("Yangi mahsulot qo'shildi: ${added.name}")
                    onSuccess()
                }
            }
        }
    }

    fun sendBroadcast(messageText: String, onComplete: () -> Unit) {
        val validText = Validators.requireNonBlank(messageText)
        if (validText == null) {
            _snackbarEvents.tryEmit("Xabar matnini kiriting.")
            return
        }
        viewModelScope.launch {
            val log = repository.recordBroadcast(validText)
            _snackbarEvents.emit("Xabarnoma yakunlandi: ${log.deliveredCount}/${log.audienceCount} ta foydalanuvchiga yuborildi.")
            onComplete()
        }
    }

    class Factory(private val repository: AsoxRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return AsoxViewModel(repository) as T
        }
    }
}
