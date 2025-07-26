import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../widgets/glassmorphism_card.dart';
import '../widgets/setup_tab.dart';
import '../widgets/analysis_tab.dart';
import '../widgets/insights_tab.dart';
import '../widgets/roadmap_tab.dart';
import '../widgets/report_tab.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({Key? key}) : super(key: key);

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;
  
  int _selectedTabIndex = 0;
  
  // Analysis data state
  String? _analysisData_brandName;
  String? _analysisData_selectedArea;
  String? _analysisData_competitor;
  
  // Loading state
  bool _isLoadingAnalysis = false;
  String _loadingStatus = '';
  String _loadingDetail = '';
  
  final List<TabItem> _tabs = [
    TabItem(icon: '🎯', title: 'Setup', id: 'setup'),
    TabItem(icon: '📊', title: 'Analysis', id: 'analysis'),
    TabItem(icon: '💡', title: 'Insights', id: 'insights'),
    TabItem(icon: '🗺️', title: 'Roadmap', id: 'roadmap'),
    TabItem(icon: '📄', title: 'Report', id: 'report'),
  ];

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: AppConstants.longAnimation,
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));
    
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        color: Color(0xFF0a0e1a), // Exact dark-bg color from HTML
        child: Stack(
          children: [
            _buildAnimatedBackground(),
            SafeArea(
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SingleChildScrollView(
                  child: Center(
                    child: Container(
                      constraints: BoxConstraints(maxWidth: 1600), // Match HTML container
                      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 768 ? 15 : 20), // Match HTML responsive padding
                      child: Column(
                        children: [
                          _buildHeader(),
                          _buildTabNavigation(),
                          _buildTabContent(),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
            // Loading overlay
            if (_isLoadingAnalysis) _buildLoadingOverlay(),
          ],
        ),
      ),
    );
  }

  Widget _buildAnimatedBackground() {
    return Stack(
      children: [
        Positioned(
          top: 150,
          right: -100,
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.glowBlue.withOpacity(0.1),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
        Positioned(
          bottom: 100,
          left: -50,
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.glowPurple.withOpacity(0.1),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Container(
      margin: const EdgeInsets.only(bottom: 40), // Match HTML margin-bottom
      padding: const EdgeInsets.all(40), // Match HTML padding
      decoration: BoxDecoration(
        color: Color.fromRGBO(255, 255, 255, 0.08), // Exact --glass-bg from HTML
        borderRadius: BorderRadius.circular(24), // Match HTML border-radius
        border: Border.all(
          color: Color.fromRGBO(255, 255, 255, 0.1), // Exact --border-color from HTML
          width: 1,
        ),
      ),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20), // Match HTML backdrop-filter
        child: Column(
          children: [
            // Gradient top border (::before pseudo-element)
            Container(
              width: double.infinity,
              height: 2,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight, // 45deg angle like HTML --accent-gradient
                  colors: [Color(0xFFff6b6b), Color(0xFF4ecdc4)], // Exact --accent-gradient
                ),
              ),
            ),
            const SizedBox(height: 32),
            
            // Main title - HTML background-clip: text approach
            ShaderMask(
              shaderCallback: (bounds) => LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight, // 45deg like HTML
                colors: [Color(0xFFff6b6b), Color(0xFF4ecdc4)], // Exact --accent-gradient
              ).createShader(bounds),
              child: Text(
                AppConstants.appName,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 768 ? 40 : 56, // 2.5rem mobile, 3.5rem desktop
                  fontWeight: FontWeight.w800,
                  letterSpacing: -2,
                  color: Colors.white, // Base color for ShaderMask
                ),
              ),
            ),
            const SizedBox(height: 15),
            
            // Subtitle - exact HTML styling
            Text(
              'AI-Powered Brand Reputation Analysis & Competitive Intelligence',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 20.8, // 1.3rem = 20.8px (exact HTML match)
                color: Color.fromRGBO(255, 255, 255, 0.7), // Exact --text-secondary
                fontWeight: FontWeight.w300,
              ),
            ),
            const SizedBox(height: 20),
            
            // Hackathon badge - exact HTML styling
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF667eea), Color(0xFF764ba2)], // Exact --primary-gradient
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Color(0xFF667eea).withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '🚀',
                    style: TextStyle(fontSize: 16),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'VibeCoding Hackathon 2025',
                    style: TextStyle(
                      color: Color(0xFFffffff), // Exact --text-primary
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabNavigation() {
    return Container(
      child: GlassmorphismCard(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: _tabs.asMap().entries.map((entry) {
            final index = entry.key;
            final tab = entry.value;
            final isSelected = index == _selectedTabIndex;
            
            return Expanded(
              child: GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedTabIndex = index;
                  });
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: isSelected 
                        ? AppColors.glowBlue.withOpacity(0.2)
                        : Colors.transparent,
                    border: isSelected
                        ? Border.all(color: AppColors.glowBlue.withOpacity(0.5))
                        : null,
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        tab.icon,
                        style: TextStyle(fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        tab.title,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: isSelected ? AppColors.glowBlue : AppColors.textSecondary,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                          fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 12,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildTabContent() {
    return Container(
      margin: const EdgeInsets.only(top: 20),
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: _getTabContent(_selectedTabIndex),
      ),
    );
  }

  void _onAnalysisLaunched(String brandName, String selectedArea, String competitor) {
    setState(() {
      _analysisData_brandName = brandName;
      _analysisData_selectedArea = selectedArea;
      _analysisData_competitor = competitor;
      _isLoadingAnalysis = true;
    });
    
    _simulateAnalysisProgress();
  }

  void _simulateAnalysisProgress() {
    final steps = [
      {'status': 'Initializing AI Analysis...', 'detail': 'Setting up data collection pipelines', 'duration': 800},
      {'status': 'Collecting News Data...', 'detail': 'Analyzing 15,000+ news articles', 'duration': 1200},
      {'status': 'Scraping Social Media...', 'detail': 'Processing 89,500+ social posts', 'duration': 1000},
      {'status': 'Analyzing Glassdoor Reviews...', 'detail': 'Extracting insights from employee feedback', 'duration': 900},
      {'status': 'Processing Financial Data...', 'detail': 'Analyzing market performance metrics', 'duration': 700},
      {'status': 'Running LLM Analysis...', 'detail': 'Generating competitive insights with GPT-4', 'duration': 1100},
      {'status': 'Generating Recommendations...', 'detail': 'Creating actionable strategic plan', 'duration': 600},
      {'status': 'Analysis Complete!', 'detail': 'Preparing comprehensive dashboard', 'duration': 500},
    ];

    int currentStep = 0;

    void processStep() {
      if (currentStep < steps.length && mounted) {
        final step = steps[currentStep];
        setState(() {
          _loadingStatus = step['status'] as String;
          _loadingDetail = step['detail'] as String;
        });

        Future.delayed(Duration(milliseconds: step['duration'] as int), () {
          currentStep++;
          processStep();
        });
      } else {
        _completeAnalysis();
      }
    }

    processStep();
  }

  void _completeAnalysis() {
    if (mounted) {
      setState(() {
        _isLoadingAnalysis = false;
        _selectedTabIndex = 1; // Switch to Analysis tab
      });
    }
  }

  Widget _getTabContent(int index) {
    switch (index) {
      case 0:
        return SetupTab(
          key: ValueKey('setup'),
          onAnalysisLaunched: _onAnalysisLaunched,
        );
      case 1:
        return AnalysisTab(
          key: ValueKey('analysis'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
        );
      case 2:
        return InsightsTab(
          key: ValueKey('insights'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
        );
      case 3:
        return RoadmapTab(
          key: ValueKey('roadmap'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
        );
      case 4:
        return ReportTab(
          key: ValueKey('report'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
        );
      default:
        return SetupTab(
          key: ValueKey('setup'),
          onAnalysisLaunched: _onAnalysisLaunched,
        );
    }
  }

  Widget _buildLoadingOverlay() {
    return Container(
      color: Colors.black.withOpacity(0.7),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Center(
          child: Container(
            constraints: BoxConstraints(maxWidth: 400),
            margin: EdgeInsets.all(24),
            padding: EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: AppColors.glassBackground,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: AppColors.glassBorder),
              boxShadow: [
                BoxShadow(
                  color: AppColors.glowBlue.withOpacity(0.2),
                  blurRadius: 20,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Loading icon with animation
                Container(
                  width: 80,
                  height: 80,
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
                    strokeWidth: 3,
                  ),
                ),
                
                SizedBox(height: 24),
                
                // Main status
                Text(
                  _loadingStatus,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                SizedBox(height: 12),
                
                // Detail status
                Text(
                  _loadingDetail,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                SizedBox(height: 32),
                
                // Progress indicator with glow effect
                Container(
                  width: double.infinity,
                  height: 4,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(2),
                    color: AppColors.glassBackground,
                  ),
                  child: Stack(
                    children: [
                      Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(2),
                          gradient: LinearGradient(
                            colors: [
                              AppColors.glowBlue,
                              AppColors.glowPurple,
                            ],
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.glowBlue.withOpacity(0.5),
                              blurRadius: 8,
                              offset: Offset(0, 0),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                
                SizedBox(height: 16),
                
                // "Powered by AI" text
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '🤖',
                      style: TextStyle(fontSize: 16),
                    ),
                    SizedBox(width: 8),
                    Text(
                      'Powered by Advanced AI Analysis',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

}

class TabItem {
  final String icon;
  final String title;
  final String id;
  
  TabItem({
    required this.icon,
    required this.title,
    required this.id,
  });
}