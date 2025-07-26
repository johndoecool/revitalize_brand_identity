import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/insights_models.dart';
import '../../data/services/insights_service.dart';
import 'glassmorphism_card.dart';

class InsightsTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;

  const InsightsTab({
    Key? key,
    this.brandName,
    this.selectedArea,
    this.competitor,
  }) : super(key: key);

  @override
  State<InsightsTab> createState() => _InsightsTabState();
}

class _InsightsTabState extends State<InsightsTab>
    with TickerProviderStateMixin {
  AnalysisResults? _analysisResults;
  bool _isLoading = false;
  String? _expandedInsight;
  
  late AnimationController _staggerController;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    
    _staggerController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    _pulseController.repeat(reverse: true);
    
    if (hasAnalysisData) {
      _loadAnalysisResults();
    }
  }

  @override
  void dispose() {
    _staggerController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(InsightsTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (hasAnalysisData && 
        (oldWidget.brandName != widget.brandName || 
         oldWidget.selectedArea != widget.selectedArea || 
         oldWidget.competitor != widget.competitor)) {
      _loadAnalysisResults();
    }
  }

  bool get hasAnalysisData => 
      widget.brandName != null && widget.selectedArea != null && widget.competitor != null;

  Future<void> _loadAnalysisResults() async {
    if (!hasAnalysisData) return;

    setState(() {
      _isLoading = true;
    });

    try {
      String industry;
      switch (widget.selectedArea?.toLowerCase()) {
        case 'self service portal':
        case 'banking':
          industry = 'banking';
          break;
        case 'employer branding':
        case 'technology':
          industry = 'technology';
          break;
        case 'product innovation':
        case 'healthcare':
          industry = 'healthcare';
          break;
        default:
          industry = 'banking';
      }

      final results = await DemoInsightsService().getAnalysisResults(industry);
      if (mounted) {
        setState(() {
          _analysisResults = results;
          _isLoading = false;
        });
        
        if (results != null) {
          _staggerController.forward();
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
      print('Error loading analysis results: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!hasAnalysisData) {
      return _buildEmptyState(context);
    }

    if (_isLoading) {
      return _buildLoadingState(context);
    }

    if (_analysisResults == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 32),
          _buildOverallScores(),
          const SizedBox(height: 32),
          _buildInsightsGrid(),
          const SizedBox(height: 32),
          _buildStrengthsSection(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '💡 Strategic Insights & Recommendations',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'AI-powered actionable insights comparing ${widget.brandName} vs ${widget.competitor}',
          style: TextStyle(
            fontSize: 16,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildOverallScores() {
    final overall = _analysisResults!.overallComparison;
    
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: const Interval(0.0, 0.3, curve: Curves.easeOut),
          ),
        );
        
        return Transform.translate(
          offset: Offset(0, 50 * (1 - animation.value)),
          child: Opacity(
            opacity: animation.value,
            child: GlassmorphismCard(
              child: Row(
                children: [
                  Expanded(
                    child: _buildScoreCard(
                      widget.brandName!,
                      overall.brandScore,
                      AppColors.glowBlue,
                    ),
                  ),
                  Container(
                    width: 1,
                    height: 80,
                    color: AppColors.glassBorder,
                    margin: const EdgeInsets.symmetric(horizontal: 24),
                  ),
                  Expanded(
                    child: _buildScoreCard(
                      widget.competitor!,
                      overall.competitorScore,
                      AppColors.glowPurple,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildScoreCard(String name, double score, Color color) {
    return Column(
      children: [
        Text(
          name,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _pulseAnimation.value,
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      color.withOpacity(0.3),
                      color.withOpacity(0.1),
                      Colors.transparent,
                    ],
                  ),
                ),
                child: Center(
                  child: Text(
                    '${(score * 100).toInt()}',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                      color: color,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 8),
        Text(
          'Overall Score',
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildInsightsGrid() {
    final insights = _analysisResults!.actionableInsights;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Actionable Insights',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 16),
        LayoutBuilder(
          builder: (context, constraints) {
            final isDesktop = constraints.maxWidth > 1200;
            final isTablet = constraints.maxWidth > 768;
            
            int crossAxisCount;
            if (isDesktop) {
              crossAxisCount = 3;
            } else if (isTablet) {
              crossAxisCount = 2;
            } else {
              crossAxisCount = 1;
            }
            
            return GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.75,
              ),
              itemCount: insights.length,
              itemBuilder: (context, index) {
                return _buildInsightCard(insights[index], index);
              },
            );
          },
        ),
      ],
    );
  }

  Widget _buildInsightCard(ActionableInsight insight, int index) {
    final isExpanded = _expandedInsight == insight.title;
    
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: Interval(
              0.3 + (index * 0.1),
              0.7 + (index * 0.1),
              curve: Curves.easeOut,
            ),
          ),
        );
        
        return Transform.translate(
          offset: Offset(0, 100 * (1 - animation.value)),
          child: Opacity(
            opacity: animation.value,
            child: _InsightCard(
              insight: insight,
              isExpanded: isExpanded,
              onTap: () {
                setState(() {
                  _expandedInsight = isExpanded ? null : insight.title;
                });
              },
            ),
          ),
        );
      },
    );
  }

  Widget _buildStrengthsSection() {
    final strengths = _analysisResults!.strengthsToMaintain;
    
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: const Interval(0.8, 1.0, curve: Curves.easeOut),
          ),
        );
        
        return Transform.translate(
          offset: Offset(0, 50 * (1 - animation.value)),
          child: Opacity(
            opacity: animation.value,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Strengths to Maintain',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                ...strengths.map((strength) => Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: GlassmorphismCard(
                    child: Row(
                      children: [
                        Container(
                          width: 4,
                          height: 40,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                Color(0xFF4ecdc4),
                                Color(0xFF44a08d),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                strength.area.replaceAll('_', ' ').toUpperCase(),
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF4ecdc4),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                strength.description,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Color(0xFF4ecdc4).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '${(strength.currentScore * 100).toInt()}%',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF4ecdc4),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                )).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildLoadingState(BuildContext context) {
    return Center(
      child: GlassmorphismCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Shimmer.fromColors(
              baseColor: AppColors.glassBorder,
              highlightColor: AppColors.glowBlue.withOpacity(0.3),
              child: Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.glassBorder,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Analyzing Brand Insights...',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Generating actionable recommendations and strategic insights.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: GlassmorphismCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '💡',
              style: TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 16),
            Text(
              'Strategic Insights',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'AI-powered actionable insights and recommendations will appear here after launching an analysis from the Setup tab.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(25),
                border: Border.all(color: AppColors.glowPurple.withOpacity(0.5)),
                color: AppColors.glowPurple.withOpacity(0.1),
              ),
              child: Text(
                '← Complete Analysis First',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.glowPurple,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context) {
    return Center(
      child: GlassmorphismCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '⚠️',
              style: TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 16),
            Text(
              'Unable to Load Insights',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'There was an error loading the insights data. Please try again.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadAnalysisResults,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _InsightCard extends StatefulWidget {
  final ActionableInsight insight;
  final bool isExpanded;
  final VoidCallback onTap;

  const _InsightCard({
    required this.insight,
    required this.isExpanded,
    required this.onTap,
  });

  @override
  State<_InsightCard> createState() => _InsightCardState();
}

class _InsightCardState extends State<_InsightCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _hoverController;
  late Animation<double> _hoverAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _hoverController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _hoverAnimation = Tween<double>(begin: 1.0, end: 1.02).animate(
      CurvedAnimation(parent: _hoverController, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    _hoverController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = widget.insight.priority.gradientColors;
    
    return MouseRegion(
      onEnter: (_) {
        setState(() => _isHovered = true);
        _hoverController.forward();
      },
      onExit: (_) {
        setState(() => _isHovered = false);
        _hoverController.reverse();
      },
      child: AnimatedBuilder(
        animation: _hoverAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _hoverAnimation.value,
            child: GestureDetector(
              onTap: widget.onTap,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(colors[0]).withOpacity(_isHovered ? 0.3 : 0.2),
                      Color(colors[1]).withOpacity(_isHovered ? 0.2 : 0.1),
                    ],
                  ),
                  border: Border.all(
                    color: Color(widget.insight.priority.glowColor).withOpacity(0.5),
                    width: 1,
                  ),
                  boxShadow: _isHovered ? [
                    BoxShadow(
                      color: Color(widget.insight.priority.glowColor).withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ] : null,
                ),
                child: Container(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Priority Badge
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: colors.map((c) => Color(c)).toList(),
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          widget.insight.priority.displayName,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      
                      // ROI Display
                      Text(
                        widget.insight.roiEstimate,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(widget.insight.priority.glowColor),
                        ),
                      ),
                      const SizedBox(height: 8),
                      
                      // Title
                      Text(
                        widget.insight.title,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      
                      // Description
                      Text(
                        widget.insight.description,
                        style: TextStyle(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                          height: 1.4,
                        ),
                        maxLines: widget.isExpanded ? null : 3,
                        overflow: widget.isExpanded ? null : TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 12),
                      
                      // Metrics
                      Row(
                        children: [
                          _buildMetric('⏱️', widget.insight.estimatedEffort),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _buildMetric('📈', widget.insight.expectedImpact),
                          ),
                        ],
                      ),
                      
                      // Expanded Content
                      if (widget.isExpanded) ...[
                        const SizedBox(height: 16),
                        Text(
                          'Implementation Steps:',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        ...widget.insight.implementationSteps.map((step) => 
                          Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '• ',
                                  style: TextStyle(
                                    color: Color(widget.insight.priority.glowColor),
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Expanded(
                                  child: Text(
                                    step,
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ).toList(),
                      ],
                      
                      const SizedBox(height: 12),
                      
                      // Expand/Collapse Button
                      Container(
                        width: double.infinity,
                        height: 36,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: colors.map((c) => Color(c).withOpacity(0.3)).toList(),
                          ),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: Color(widget.insight.priority.glowColor).withOpacity(0.5),
                          ),
                        ),
                        child: Center(
                          child: Text(
                            widget.isExpanded ? 'Show Less' : 'View Details',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(widget.insight.priority.glowColor),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMetric(String icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          icon,
          style: TextStyle(fontSize: 12),
        ),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            text,
            style: TextStyle(
              fontSize: 11,
              color: AppColors.textSecondary,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}