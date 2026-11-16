package com.example

import android.app.Application
import com.example.data.local.AsoxDatabase
import com.example.data.repository.AsoxRepository

class AsoxApplication : Application() {
    val database: AsoxDatabase by lazy { AsoxDatabase.getInstance(this) }
    val repository: AsoxRepository by lazy { AsoxRepository(database.asoxDao()) }
}
