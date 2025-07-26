import 'package:flutter/material.dart';

class AppColors {
  // Base Colors
  static const Color darkBackground = Color(0xFF0a0e1a);
  static const Color cardBackground = Color.fromRGBO(255, 255, 255, 0.05);
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color.fromRGBO(255, 255, 255, 0.7);
  static const Color borderColor = Color.fromRGBO(255, 255, 255, 0.1);

  // Glassmorphism Colors
  static const Color glassBackground = Color.fromRGBO(255, 255, 255, 0.08);
  static const Color glassBackgroundStrong = Color.fromRGBO(255, 255, 255, 0.12);
  static const Color glassBorder = Color.fromRGBO(255, 255, 255, 0.18);
  static const Color surfacePrimary = Color(0xFF1e1e2e);

  // Glow Colors
  static const Color glowBlue = Color(0xFF00d4ff);
  static const Color glowPurple = Color(0xFF8b5cf6);
  static const Color glowRed = Color(0xFFff6b6b);
  static const Color glowGreen = Color(0xFF4ecdc4);

  // Industry Color Schemes
  static const BrandColorScheme banking = BrandColorScheme(
    primary: Color(0xFF1e40af),
    secondary: Color(0xFF3b82f6),
    accent: Color(0xFF60a5fa),
  );

  static const BrandColorScheme tech = BrandColorScheme(
    primary: Color(0xFF7c3aed),
    secondary: Color(0xFF8b5cf6),
    accent: Color(0xFFa78bfa),
  );

  static const BrandColorScheme healthcare = BrandColorScheme(
    primary: Color(0xFF059669),
    secondary: Color(0xFF10b981),
    accent: Color(0xFF34d399),
  );

  // Success/Warning/Error Colors
  static const Color success = Color(0xFF00c9ff);
  static const Color warning = Color(0xFFfc466b);
  static const Color error = Color(0xFFf87171);
  static const Color info = Color(0xFF3b82f6);

  // Chart Colors (complementary palette)
  static const List<Color> chartColors = [
    Color(0xFF00d4ff), // Blue
    Color(0xFF8b5cf6), // Purple
    Color(0xFF4ecdc4), // Teal
    Color(0xFFff6b6b), // Red
    Color(0xFF34d399), // Green
    Color(0xFFfbbf24), // Yellow
    Color(0xFFf472b6), // Pink
    Color(0xFF6366f1), // Indigo
  ];

  // Gradient Definitions
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF667eea), Color(0xFF764ba2)],
  );

  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFff6b6b), Color(0xFF4ecdc4)],
  );

  static const LinearGradient successGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF00c9ff), Color(0xFF92fe9d)],
  );
}

class BrandColorScheme {
  final Color primary;
  final Color secondary;
  final Color accent;

  const BrandColorScheme({
    required this.primary,
    required this.secondary,
    required this.accent,
  });

  // Helper methods for opacity variations
  Color get primary20 => primary.withOpacity(0.2);
  Color get primary10 => primary.withOpacity(0.1);
  Color get secondary20 => secondary.withOpacity(0.2);
  Color get secondary10 => secondary.withOpacity(0.1);
  Color get accent20 => accent.withOpacity(0.2);
  Color get accent10 => accent.withOpacity(0.1);
}