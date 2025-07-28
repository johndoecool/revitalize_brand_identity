import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../widgets/glassmorphism_card.dart';

class AnalysisPage extends StatefulWidget {
  final String industryId;
  final String industryTitle;
  final BrandColorScheme colors;

  const AnalysisPage({
    Key? key,
    required this.industryId,
    required this.industryTitle,
    required this.colors,
  }) : super(key: key);

  @override
  State<AnalysisPage> createState() => _AnalysisPageState();
}

class _AnalysisPageState extends State<AnalysisPage>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;
  
  bool _isLoading = true;
  int _currentStep = 0;
  
  final List<String> _analysisSteps = [
    'Initializing Brand Intelligence Engine...',
    'Collecting brand data and mentions...',
    'Analyzing social media sentiment...',
    'Processing competitor comparisons...',
    'Generating insights and recommendations...',
    'Finalizing comprehensive report...',
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
    _startAnalysisSimulation();
  }

  void _startAnalysisSimulation() {
    _simulateStep();
  }

  void _simulateStep() {
    if (_currentStep < _analysisSteps.length) {
      Future.delayed(Duration(milliseconds: 1500 + (_currentStep * 200)), () {
        if (mounted) {
          setState(() {
            _currentStep++;
          });
          _simulateStep();
        }
      });
    } else {
      Future.delayed(const Duration(milliseconds: 800), () {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      });
    }
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
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.darkBackground,
              Color(0xFF1a1f3a),
              AppColors.darkBackground,
            ],
          ),
        ),
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnimation,
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  const SizedBox(height: 32),
                  if (_isLoading) ...[
                    _buildLoadingSection(),
                  ] else ...[
                    _buildAnalysisResults(),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        GlassmorphismButton(
          onPressed: () => Navigator.pop(context),
          width: 48,
          height: 48,
          backgroundColor: AppColors.glassBackground,
          borderColor: AppColors.glassBorder,
          child: Icon(
            Icons.arrow_back,
            color: AppColors.textPrimary,
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.industryTitle,
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  fontSize: MediaQuery.of(context).size.width < 600 ? 24 : null,
                  color: widget.colors.primary,
                ),
              ),
              Text(
                'Brand Intelligence Analysis',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingSection() {
    return Center(
      child: GlassmorphismCard(
        child: Column(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [
                    widget.colors.primary,
                    widget.colors.secondary,
                  ],
                ),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      AppColors.textPrimary,
                    ),
                    strokeWidth: 2,
                  ),
                  Icon(
                    Icons.analytics,
                    color: AppColors.textPrimary,
                    size: 32,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Analyzing Brand Intelligence',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Processing comprehensive brand data and competitive analysis...',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 32),
            _buildProgressSteps(),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressSteps() {
    return Column(
      children: _analysisSteps.asMap().entries.map((entry) {
        final index = entry.key;
        final step = entry.value;
        final isActive = index == _currentStep;
        final isCompleted = index < _currentStep;

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          child: Row(
            children: [
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isCompleted
                      ? widget.colors.primary
                      : isActive
                          ? widget.colors.primary.withOpacity(0.3)
                          : AppColors.glassBackground,
                  border: Border.all(
                    color: isCompleted || isActive
                        ? widget.colors.primary
                        : AppColors.glassBorder,
                  ),
                ),
                child: isCompleted
                    ? Icon(
                        Icons.check,
                        size: 14,
                        color: AppColors.textPrimary,
                      )
                    : isActive
                        ? SizedBox(
                            width: 12,
                            height: 12,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                widget.colors.primary,
                              ),
                            ),
                          )
                        : null,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  step,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: isCompleted || isActive
                        ? AppColors.textPrimary
                        : AppColors.textSecondary,
                    fontWeight: isActive ? FontWeight.w500 : FontWeight.normal,
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildAnalysisResults() {
    return Column(
      children: [
        GlassmorphismCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          widget.colors.primary,
                          widget.colors.secondary,
                        ],
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.check_circle,
                      color: AppColors.textPrimary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Analysis Complete!',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w600,
                            color: widget.colors.primary,
                          ),
                        ),
                        Text(
                          'Your comprehensive brand intelligence report is ready',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: widget.colors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: widget.colors.primary.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '📊 Ready to Explore:',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: widget.colors.primary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildFeatureList(),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        _buildActionButtons(),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildFeatureList() {
    final features = [
      'Interactive brand comparison charts',
      'Sentiment analysis and social media insights',
      'Competitive positioning matrix',
      'Reputation score breakdown',
      'Actionable recommendations',
    ];

    return Column(
      children: features.map((feature) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 6,
                height: 6,
                margin: const EdgeInsets.only(top: 6),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: widget.colors.primary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  feature,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildActionButtons() {
    final isSmallScreen = MediaQuery.of(context).size.width < 600;
    
    if (isSmallScreen) {
      return Column(
        children: [
          GlassmorphismButton(
            onPressed: () {
              // Navigate back to dashboard and show charts
              Navigator.pop(context);
            },
            width: double.infinity,
            height: 56,
            backgroundColor: widget.colors.primary.withOpacity(0.2),
            borderColor: widget.colors.primary,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.bar_chart,
                  color: widget.colors.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'View Charts',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: widget.colors.primary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          GlassmorphismButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Click "View Charts" to see interactive analysis dashboard! 📈'),
                  backgroundColor: widget.colors.primary,
                  duration: Duration(seconds: 3),
                ),
              );
            },
            width: double.infinity,
            height: 56,
            backgroundColor: widget.colors.secondary.withOpacity(0.2),
            borderColor: widget.colors.secondary,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.insights,
                  color: widget.colors.secondary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Deep Dive',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: widget.colors.secondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      );
    } else {
      return Row(
        children: [
          Expanded(
            child: GlassmorphismButton(
              onPressed: () {
                // Navigate back to dashboard and show charts
                Navigator.pop(context);
              },
              height: 56,
              backgroundColor: widget.colors.primary.withOpacity(0.2),
              borderColor: widget.colors.primary,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.bar_chart,
                    color: widget.colors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'View Charts',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: widget.colors.primary,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: GlassmorphismButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Click "View Charts" to see interactive analysis dashboard! 📈'),
                    backgroundColor: widget.colors.primary,
                    duration: Duration(seconds: 3),
                  ),
                );
              },
              height: 56,
              backgroundColor: widget.colors.secondary.withOpacity(0.2),
              borderColor: widget.colors.secondary,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.insights,
                    color: widget.colors.secondary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Deep Dive',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: widget.colors.secondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }
  }
}