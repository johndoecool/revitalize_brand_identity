class AppConstants {
  // App Info
  static const String appName = 'Brand Intelligence Hub';
  static const String appVersion = '1.0.0';
  static const String organizationName = 'VibeCoding Hackathon';

  // API Configuration
  static const String baseUrl = 'https://api.brandintelligence.com'; // Replace with actual API
  static const String mockApiUrl = 'http://localhost:3000'; // Postman mock server
  static const Duration apiTimeout = Duration(seconds: 30);

  // Asset Paths
  static const String dataPath = 'assets/data/';
  static const String imagesPath = 'assets/images/';
  static const String fontsPath = 'assets/fonts/';

  // Demo Data Files
  static const String bankingDemoFile = '${dataPath}banking-demo.json';
  static const String techDemoFile = '${dataPath}tech-demo.json';
  static const String healthcareDemoFile = '${dataPath}healthcare-demo.json';

  // Industry Types
  static const String industryBanking = 'banking';
  static const String industryTech = 'tech';
  static const String industryHealthcare = 'healthcare';

  // Chart Configuration
  static const double chartHeight = 300.0;
  static const double chartBorderRadius = 12.0;
  static const Duration chartAnimationDuration = Duration(milliseconds: 1500);

  // UI Constants
  static const double defaultPadding = 16.0;
  static const double defaultMargin = 8.0;
  static const double defaultBorderRadius = 12.0;
  static const double glassmorphismBlur = 20.0;
  static const double glassmorphismOpacity = 0.08;

  // Breakpoints for Responsive Design
  static const double mobileBreakpoint = 768.0;
  static const double tabletBreakpoint = 1024.0;
  static const double desktopBreakpoint = 1200.0;

  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 300);
  static const Duration mediumAnimation = Duration(milliseconds: 600);
  static const Duration longAnimation = Duration(milliseconds: 1200);

  // Error Messages
  static const String networkErrorMessage = 'Network error. Please check your connection.';
  static const String serverErrorMessage = 'Server error. Please try again later.';
  static const String dataNotFoundMessage = 'Data not found. Please try again.';
  static const String genericErrorMessage = 'Something went wrong. Please try again.';
}