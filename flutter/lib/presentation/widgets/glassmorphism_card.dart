import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';

class GlassmorphismCard extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final double opacity;
  final double blur;
  final Color? backgroundColor;
  final Color? borderColor;
  final VoidCallback? onTap;
  final bool hasBorder;
  final bool hasShadow;

  const GlassmorphismCard({
    Key? key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.borderRadius = AppConstants.defaultBorderRadius,
    this.opacity = AppConstants.glassmorphismOpacity,
    this.blur = AppConstants.glassmorphismBlur,
    this.backgroundColor,
    this.borderColor,
    this.onTap,
    this.hasBorder = true,
    this.hasShadow = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: margin,
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(borderRadius),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(borderRadius),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(borderRadius),
              boxShadow: hasShadow
                  ? [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ]
                  : null,
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(borderRadius),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
                child: Container(
                  decoration: BoxDecoration(
                    color: backgroundColor ?? AppColors.glassBackground,
                    borderRadius: BorderRadius.circular(borderRadius),
                    border: hasBorder
                        ? Border.all(
                            color: borderColor ?? AppColors.glassBorder,
                            width: 1,
                          )
                        : null,
                  ),
                  padding: padding ?? const EdgeInsets.all(AppConstants.defaultPadding),
                  child: child,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class GlassmorphismContainer extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final Color? backgroundColor;
  final Color? borderColor;
  final Gradient? gradient;

  const GlassmorphismContainer({
    Key? key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.borderRadius = AppConstants.defaultBorderRadius,
    this.backgroundColor,
    this.borderColor,
    this.gradient,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: margin,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: borderColor ?? AppColors.glassBorder,
          width: 1,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: Container(
            decoration: BoxDecoration(
              color: backgroundColor ?? AppColors.glassBackground,
              borderRadius: BorderRadius.circular(borderRadius),
            ),
            padding: padding ?? const EdgeInsets.all(AppConstants.defaultPadding),
            child: child,
          ),
        ),
      ),
    );
  }
}

class GlassmorphismButton extends StatelessWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final double? width;
  final double? height;
  final Color? backgroundColor;
  final Color? borderColor;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;
  final bool isEnabled;

  const GlassmorphismButton({
    Key? key,
    required this.child,
    this.onPressed,
    this.width,
    this.height,
    this.backgroundColor,
    this.borderColor,
    this.borderRadius = AppConstants.defaultBorderRadius,
    this.padding,
    this.isEnabled = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(borderRadius),
        child: InkWell(
          onTap: isEnabled ? onPressed : null,
          borderRadius: BorderRadius.circular(borderRadius),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(borderRadius),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(borderRadius),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                child: Container(
                  decoration: BoxDecoration(
                    color: isEnabled
                        ? (backgroundColor ?? AppColors.glassBackgroundStrong)
                        : AppColors.glassBackground,
                    borderRadius: BorderRadius.circular(borderRadius),
                    border: Border.all(
                      color: isEnabled
                          ? (borderColor ?? AppColors.glowBlue)
                          : AppColors.glassBorder,
                      width: 1,
                    ),
                  ),
                  padding: padding ?? const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                  child: Center(child: child),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}