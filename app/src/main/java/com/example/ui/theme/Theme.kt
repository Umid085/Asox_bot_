package com.example.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

private val LightColors = lightColorScheme(
    primary = AsoxPrimary,
    onPrimary = AsoxOnPrimary,
    primaryContainer = AsoxPrimaryContainer,
    onPrimaryContainer = AsoxOnPrimaryContainer,
    secondary = AsoxSecondary,
    onSecondary = AsoxOnSecondary,
    secondaryContainer = AsoxSecondaryContainer,
    onSecondaryContainer = AsoxOnSecondaryContainer,
    tertiary = AsoxTertiary,
    onTertiary = AsoxOnTertiary,
    tertiaryContainer = AsoxTertiaryContainer,
    onTertiaryContainer = AsoxOnTertiaryContainer,
    background = AsoxBackground,
    onBackground = AsoxOnBackground,
    surface = AsoxSurface,
    onSurface = AsoxOnSurface,
    surfaceVariant = AsoxSurfaceVariant,
    onSurfaceVariant = AsoxOnSurfaceVariant,
    outline = AsoxOutline,
    outlineVariant = AsoxOutlineVariant,
    error = StatusError,
)

private val DarkColors = darkColorScheme(
    primary = AsoxDarkPrimary,
    onPrimary = AsoxDarkOnPrimary,
    primaryContainer = AsoxDarkPrimaryContainer,
    onPrimaryContainer = AsoxDarkOnPrimaryContainer,
    secondary = AsoxDarkSecondary,
    onSecondary = AsoxDarkOnSecondary,
    secondaryContainer = AsoxDarkSecondaryContainer,
    onSecondaryContainer = AsoxDarkOnSecondaryContainer,
    background = AsoxDarkBackground,
    onBackground = AsoxDarkOnBackground,
    surface = AsoxDarkSurface,
    onSurface = AsoxDarkOnSurface,
    surfaceVariant = AsoxDarkSurfaceVariant,
    onSurfaceVariant = AsoxDarkOnSurfaceVariant,
    outline = AsoxDarkOutline,
    error = StatusError,
)

val AsoxShapes = Shapes(
    small = RoundedCornerShape(10.dp),
    medium = RoundedCornerShape(16.dp),
    large = RoundedCornerShape(24.dp),
)

@Composable
fun ASOXMarketTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val context = LocalContext.current
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColors
        else -> LightColors
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AsoxTypography,
        shapes = AsoxShapes,
        content = content,
    )
}
