import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/theme_manager.dart';
import 'core/constants/app_constants.dart';
import 'presentation/pages/dashboard_page.dart';

void main() {
  runApp(const BrandIntelligenceHubApp());
}

class BrandIntelligenceHubApp extends StatelessWidget {
  const BrandIntelligenceHubApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => ThemeManager(),
      child: Consumer<ThemeManager>(
        builder: (context, themeManager, child) {
          return MaterialApp(
            title: AppConstants.appName,
            theme: ThemeManager.lightTheme,
            darkTheme: ThemeManager.darkTheme,
            themeMode: themeManager.themeMode,
            debugShowCheckedModeBanner: false,
            home: const DashboardPage(),
          );
        },
      ),
    );
  }
}
