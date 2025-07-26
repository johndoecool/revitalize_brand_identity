import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'presentation/pages/dashboard_page.dart';

void main() {
  runApp(const BrandIntelligenceHubApp());
}

class BrandIntelligenceHubApp extends StatelessWidget {
  const BrandIntelligenceHubApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConstants.appName,
      theme: AppTheme.darkTheme,
      debugShowCheckedModeBanner: false,
      home: const DashboardPage(),
    );
  }
}
