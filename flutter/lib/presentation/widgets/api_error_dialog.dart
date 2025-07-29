import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import 'glassmorphism_card.dart';

class ApiErrorDialog extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback onRetry;
  final VoidCallback onUseDemoData;
  final bool showRetry;

  const ApiErrorDialog({
    Key? key,
    required this.title,
    required this.message,
    required this.onRetry,
    required this.onUseDemoData,
    this.showRetry = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 400),
        child: GlassmorphismCard(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Error icon
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(
                    color: Colors.red.withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: const Icon(
                  Icons.warning_rounded,
                  color: Colors.red,
                  size: 30,
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Title
              Text(
                title,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 12),
              
              // Message
              Text(
                message,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.4,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 24),
              
              // Action buttons
              Column(
                children: [
                  if (showRetry) ...[
                    // Retry button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.of(context).pop();
                          onRetry();
                        },
                        icon: const Icon(Icons.refresh_rounded),
                        label: const Text('Try Again'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.glowBlue.withOpacity(0.2),
                          foregroundColor: AppColors.glowBlue,
                          side: BorderSide(color: AppColors.glowBlue),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                  ],
                  
                  // Demo data button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pop();
                        onUseDemoData();
                      },
                      icon: const Icon(Icons.storage_rounded),
                      label: const Text('Use Demo Data'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.glowPurple.withOpacity(0.2),
                        foregroundColor: AppColors.glowPurple,
                        side: BorderSide(color: AppColors.glowPurple),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Show error dialog with retry option
  static Future<void> show({
    required BuildContext context,
    required String title,
    required String message,
    required VoidCallback onRetry,
    required VoidCallback onUseDemoData,
    bool showRetry = true,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => ApiErrorDialog(
        title: title,
        message: message,
        onRetry: onRetry,
        onUseDemoData: onUseDemoData,
        showRetry: showRetry,
      ),
    );
  }
}