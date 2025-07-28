import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app_colors.dart';

class ThemeManager extends ChangeNotifier {
  static const String _themeKey = 'theme_mode';
  bool _isDarkMode = true;
  
  bool get isDarkMode => _isDarkMode;
  ThemeMode get themeMode => _isDarkMode ? ThemeMode.dark : ThemeMode.light;

  ThemeManager() {
    _loadTheme();
  }

  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    _isDarkMode = prefs.getBool(_themeKey) ?? true; // Default to dark
    AppColors.setThemeMode(_isDarkMode);
    notifyListeners();
  }

  Future<void> toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    AppColors.setThemeMode(_isDarkMode);
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_themeKey, _isDarkMode);
    
    notifyListeners();
  }

  // Dark Theme Data
  static ThemeData get darkTheme => ThemeData(
    brightness: Brightness.dark,
    primarySwatch: Colors.blue,
    scaffoldBackgroundColor: AppColors.darkBackground,
    cardColor: AppColors.darkGlassBackground,
    dividerColor: AppColors.darkBorderColor,
    textTheme: const TextTheme(
      displayLarge: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w700),
      displayMedium: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      displaySmall: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      headlineLarge: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      headlineMedium: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      headlineSmall: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      titleLarge: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      titleSmall: TextStyle(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      bodyLarge: TextStyle(color: AppColors.darkTextPrimary),
      bodyMedium: TextStyle(color: AppColors.darkTextPrimary),
      bodySmall: TextStyle(color: AppColors.darkTextSecondary),
      labelLarge: TextStyle(color: AppColors.darkTextPrimary),
      labelMedium: TextStyle(color: AppColors.darkTextSecondary),
      labelSmall: TextStyle(color: AppColors.darkTextSecondary),
    ),
    iconTheme: const IconThemeData(color: AppColors.darkTextPrimary),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      iconTheme: IconThemeData(color: AppColors.darkTextPrimary),
      titleTextStyle: TextStyle(color: AppColors.darkTextPrimary, fontSize: 20, fontWeight: FontWeight.w600),
    ),
  );

  // Light Theme Data  
  static ThemeData get lightTheme => ThemeData(
    brightness: Brightness.light,
    primarySwatch: Colors.blue,
    scaffoldBackgroundColor: AppColors.lightBackground,
    cardColor: AppColors.lightGlassBackground,
    dividerColor: AppColors.lightBorderColor,
    textTheme: const TextTheme(
      displayLarge: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w700),
      displayMedium: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      displaySmall: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      headlineLarge: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      headlineMedium: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      headlineSmall: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      titleLarge: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      titleSmall: TextStyle(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      bodyLarge: TextStyle(color: AppColors.lightTextPrimary),
      bodyMedium: TextStyle(color: AppColors.lightTextPrimary),
      bodySmall: TextStyle(color: AppColors.lightTextSecondary),
      labelLarge: TextStyle(color: AppColors.lightTextPrimary),
      labelMedium: TextStyle(color: AppColors.lightTextSecondary),
      labelSmall: TextStyle(color: AppColors.lightTextSecondary),
    ),
    iconTheme: const IconThemeData(color: AppColors.lightTextPrimary),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      iconTheme: IconThemeData(color: AppColors.lightTextPrimary),
      titleTextStyle: TextStyle(color: AppColors.lightTextPrimary, fontSize: 20, fontWeight: FontWeight.w600),
    ),
  );
}