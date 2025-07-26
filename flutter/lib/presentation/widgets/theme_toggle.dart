import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/theme_manager.dart';
import '../../core/theme/app_colors.dart';

class ThemeToggle extends StatefulWidget {
  const ThemeToggle({Key? key}) : super(key: key);

  @override
  State<ThemeToggle> createState() => _ThemeToggleState();
}

class _ThemeToggleState extends State<ThemeToggle> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeManager>(
      builder: (context, themeManager, child) {
        // Sync animation with theme state
        if (themeManager.isDarkMode) {
          _animationController.forward();
        } else {
          _animationController.reverse();
        }

        return GestureDetector(
          onTap: () {
            themeManager.toggleTheme();
          },
          child: Container(
            width: 56,
            height: 28,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: AppColors.glassBorder,
                width: 1,
              ),
              color: AppColors.glassBackground,
            ),
            child: Stack(
              children: [
                // Background gradient
                Container(
                  width: double.infinity,
                  height: double.infinity,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(14),
                    gradient: LinearGradient(
                      colors: [
                        AppColors.glowBlue.withOpacity(0.1),
                        AppColors.glowPurple.withOpacity(0.1),
                      ],
                    ),
                  ),
                ),
                
                // Sliding circle
                AnimatedBuilder(
                  animation: _animation,
                  builder: (context, child) {
                    return Positioned(
                      left: _animation.value * 28 + 2,
                      top: 2,
                      child: Container(
                        width: 24,
                        height: 24,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: themeManager.isDarkMode 
                              ? AppColors.glowBlue.withOpacity(0.8)
                              : AppColors.glowPurple.withOpacity(0.8),
                          border: Border.all(
                            color: AppColors.textPrimary.withOpacity(0.2),
                            width: 0.5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: (themeManager.isDarkMode 
                                  ? AppColors.glowBlue 
                                  : AppColors.glowPurple).withOpacity(0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Icon(
                          themeManager.isDarkMode ? Icons.dark_mode : Icons.light_mode,
                          size: 14,
                          color: Colors.white,
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}