import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../widgets/glassmorphism_card.dart';
import '../widgets/setup_tab.dart';
import '../widgets/analysis_tab.dart';
import '../widgets/insights_tab.dart';
import '../widgets/roadmap_tab.dart';
import '../widgets/report_tab.dart';
import '../widgets/theme_toggle.dart';
import '../widgets/api_error_dialog.dart';
import '../../data/services/data_collection_service.dart';

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
  String? _analysisData_requestId; // Store request ID for retry functionality
  AnalysisResult? _analysisResult;
  
  // Loading state
  bool _isLoadingAnalysis = false;
  String _loadingStatus = '';
  String _loadingDetail = '';
  
  // Services
  final DataCollectionService _dataCollectionService = DataCollectionService.instance;
  
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
        color: AppColors.background, // Dynamic background color
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
        color: AppColors.glassBackground, // Dynamic glass background
        borderRadius: BorderRadius.circular(24), // Match HTML border-radius
        border: Border.all(
          color: AppColors.glassBorder, // Dynamic border color
          width: 1,
        ),
      ),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20), // Match HTML backdrop-filter
        child: Column(
          children: [
            // Header top row with gradient border and theme toggle
            Row(
              children: [
                // Gradient top border (::before pseudo-element)
                Expanded(
                  child: Container(
                    height: 2,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight, // 45deg angle like HTML --accent-gradient
                        colors: [Color(0xFFff6b6b), Color(0xFF4ecdc4)], // Exact --accent-gradient
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Theme toggle in top-right
                const ThemeToggle(),
              ],
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
                color: AppColors.textSecondary, // Dynamic text secondary color
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
                      color: Colors.white, // Keep white for badge contrast
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

  void _onAnalysisLaunched(String brandName, String selectedArea, String competitor) async {
    // Check if this is a new analysis (different parameters) - if so, clear request ID
    if (_analysisData_brandName != brandName || 
        _analysisData_selectedArea != selectedArea || 
        _analysisData_competitor != competitor) {
      _analysisData_requestId = null; // Clear request ID for new analysis
      print('[Dashboard] New analysis detected - clearing request ID');
    }
    
    setState(() {
      _analysisData_brandName = brandName;
      _analysisData_selectedArea = selectedArea;
      _analysisData_competitor = competitor;
      _isLoadingAnalysis = true;
      _loadingStatus = 'Checking services...';
      _loadingDetail = 'Verifying backend services are running';
    });
    
    await _startRealAnalysis(brandName, selectedArea, competitor);
  }

  Future<void> _startRealAnalysis(String brandName, String selectedArea, String competitor) async {
    try {
      // Check services health first
      final servicesHealthy = await _dataCollectionService.checkServicesHealth();
      
      if (!servicesHealthy) {
        setState(() {
          _loadingStatus = 'Service Error';
          _loadingDetail = 'Backend services are not responding';
        });
        
        await Future.delayed(const Duration(seconds: 2));
        setState(() {
          _isLoadingAnalysis = false;
        });
        await _showErrorAndFallback(
          'Backend services are not available.',
          'Please ensure all services are running on ports 8001, 8002, 8003'
        );
        return;
      }
      
      // Generate or reuse request ID before starting analysis
      if (_analysisData_requestId == null) {
        // First attempt - generate new request ID
        _analysisData_requestId = const Uuid().v4();
        print('[Dashboard] Starting new analysis with request ID: $_analysisData_requestId');
      } else {
        // Retry attempt - reuse existing request ID
        print('[Dashboard] Retrying analysis with existing request ID: $_analysisData_requestId');
      }
      
      // Start real analysis (use stored request ID for both first attempt and retry)
      final result = await _dataCollectionService.startAnalysis(
        brandId: brandName,
        competitorId: competitor,
        areaId: selectedArea,
        existingRequestId: _analysisData_requestId,
        onStatusUpdate: (status) {
          if (mounted) {
            setState(() {
              _loadingStatus = status;
              _loadingDetail = _getDetailForStatus(status);
            });
          }
        },
      );
      
      if (result.isSuccess) {
        print('[Dashboard] Analysis completed successfully, setting result');
        print('[Dashboard] Analysis result data keys: ${result.data!.data.keys}');
        setState(() {
          _analysisResult = result.data;
          // Request ID is already stored from before the analysis started
        });
        _completeAnalysis();
      } else {
        setState(() {
          _isLoadingAnalysis = false;
        });
        await _showErrorAndFallback(
          result.error ?? 'Analysis failed',
          'Falling back to demo data for demonstration'
        );
      }
      
    } catch (e) {
      setState(() {
        _isLoadingAnalysis = false;
      });
      await _showErrorAndFallback(
        'Unexpected error: $e',
        'Using demo data instead'
      );
    }
  }
  
  String _getDetailForStatus(String status) {
    switch (status.toLowerCase()) {
      case 'starting data collection...':
        return 'Initializing data collection pipelines';
      case 'collecting data from multiple sources...':
        return 'Gathering news, social media, and review data';
      case 'data collection complete, starting analysis...':
        return 'Processing collected data with AI analysis';
      case 'running ai analysis...':
        return 'Generating insights with GPT-4 and competitive analysis';
      case 'retrieving analysis results...':
        return 'Preparing comprehensive dashboard and reports';
      case 'analysis complete!':
        return 'Ready to view results and actionable recommendations';
      default:
        return 'Processing analysis pipeline...';
    }
  }
  
  Future<void> _showErrorAndFallback(String error, String fallbackMessage) async {
    if (!mounted) return;
    
    await ApiErrorDialog.show(
      context: context,
      title: 'Analysis Service Error',
      message: '$error\n\n$fallbackMessage',
      onRetry: () {
        // Retry the analysis with the same parameters
        if (_analysisData_brandName != null && 
            _analysisData_selectedArea != null && 
            _analysisData_competitor != null) {
          _onAnalysisLaunched(
            _analysisData_brandName!,
            _analysisData_selectedArea!,
            _analysisData_competitor!,
          );
        }
      },
      onUseDemoData: () {
        // Continue with demo data
        _simulateAnalysisProgress();
      },
      showRetry: true, // Enable retry option
    );
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
        print('[Dashboard] Creating AnalysisTab with analysisResult: ${_analysisResult != null ? "PRESENT" : "NULL"}');
        if (_analysisResult != null) {
          print('[Dashboard] AnalysisResult data keys: ${_analysisResult!.data.keys}');
        }
        return AnalysisTab(
          key: ValueKey('analysis'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
          analysisResult: _analysisResult,
        );
      case 2:
        return InsightsTab(
          key: ValueKey('insights'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
          analysisResult: _analysisResult,
        );
      case 3:
        return RoadmapTab(
          key: ValueKey('roadmap'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
          analysisResult: _analysisResult,
        );
      case 4:
        print('[Dashboard] Creating ReportTab with:');
        print('[Dashboard] brandName: $_analysisData_brandName');
        print('[Dashboard] selectedArea: $_analysisData_selectedArea');
        print('[Dashboard] competitor: $_analysisData_competitor');
        print('[Dashboard] analysisResult != null: ${_analysisResult != null}');
        if (_analysisResult != null) {
          print('[Dashboard] analysisResult.analysisId: ${_analysisResult!.analysisId}');
          print('[Dashboard] analysisResult.data keys: ${_analysisResult!.data.keys}');
        }
        return ReportTab(
          key: ValueKey('report'),
          brandName: _analysisData_brandName,
          selectedArea: _analysisData_selectedArea,
          competitor: _analysisData_competitor,
          analysisResult: _analysisResult,
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