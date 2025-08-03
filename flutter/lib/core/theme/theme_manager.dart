import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_fonts/google_fonts.dart';
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
    fontFamily: GoogleFonts.notoSans().fontFamily,
    textTheme: GoogleFonts.notoSansTextTheme().copyWith(
      displayLarge: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w700),
      displayMedium: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      displaySmall: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      headlineLarge: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      headlineMedium: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      headlineSmall: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      titleLarge: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w600),
      titleMedium: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      titleSmall: GoogleFonts.notoSans(color: AppColors.darkTextPrimary, fontWeight: FontWeight.w500),
      bodyLarge: GoogleFonts.notoSans(color: AppColors.darkTextPrimary),
      bodyMedium: GoogleFonts.notoSans(color: AppColors.darkTextPrimary),
      bodySmall: GoogleFonts.notoSans(color: AppColors.darkTextSecondary),
      labelLarge: GoogleFonts.notoSans(color: AppColors.darkTextPrimary),
      labelMedium: GoogleFonts.notoSans(color: AppColors.darkTextSecondary),
      labelSmall: GoogleFonts.notoSans(color: AppColors.darkTextSecondary),
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
    fontFamily: GoogleFonts.notoSans().fontFamily,
    textTheme: GoogleFonts.notoSansTextTheme().copyWith(
      displayLarge: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w700),
      displayMedium: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      displaySmall: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      headlineLarge: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      headlineMedium: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      headlineSmall: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      titleLarge: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w600),
      titleMedium: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      titleSmall: GoogleFonts.notoSans(color: AppColors.lightTextPrimary, fontWeight: FontWeight.w500),
      bodyLarge: GoogleFonts.notoSans(color: AppColors.lightTextPrimary),
      bodyMedium: GoogleFonts.notoSans(color: AppColors.lightTextPrimary),
      bodySmall: GoogleFonts.notoSans(color: AppColors.lightTextSecondary),
      labelLarge: GoogleFonts.notoSans(color: AppColors.lightTextPrimary),
      labelMedium: GoogleFonts.notoSans(color: AppColors.lightTextSecondary),
      labelSmall: GoogleFonts.notoSans(color: AppColors.lightTextSecondary),
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