import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/insights_models.dart';
import '../../data/services/insights_service.dart';
import '../../data/services/data_collection_service.dart';
import 'glassmorphism_card.dart';

class InsightsTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;
  final AnalysisResult? analysisResult;

  const InsightsTab({
    Key? key,
    this.brandName,
    this.selectedArea,
    this.competitor,
    this.analysisResult,
  }) : super(key: key);

  @override
  State<InsightsTab> createState() => _InsightsTabState();
}

class _InsightsTabState extends State<InsightsTab>
    with TickerProviderStateMixin {
  EnhancedAnalysisResults? _enhancedResults;
  bool _isLoading = false;
  String? _expandedInsight;
  int _currentTabIndex = 0;
  
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
         oldWidget.competitor != widget.competitor ||
         oldWidget.analysisResult != widget.analysisResult)) {
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
      // Layer 1: Try to extract real data from analysis result first
      if (widget.analysisResult != null) {
        print('[InsightsTab] Attempting to extract enhanced insights from real analysis result');
        final enhancedInsights = _extractEnhancedInsightsFromAnalysis(widget.analysisResult!);
        if (enhancedInsights != null) {
          print('[InsightsTab] Successfully using enhanced insights data');
          if (mounted) {
            setState(() {
              _enhancedResults = enhancedInsights;
              _isLoading = false;
            });
            _staggerController.forward();
          }
          return;
        } else {
          print('[InsightsTab] Failed to extract enhanced insights data, falling back to demo data');
        }
      } else {
        print('[InsightsTab] No analysis result available, using demo data');
      }

      // Layer 2: Fallback to demo data
      await _loadDemoData();
      
    } catch (e) {
      print('[InsightsTab] Error loading insights data: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  /// Load demo data as fallback
  Future<void> _loadDemoData() async {
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

      print('[InsightsTab] Loading demo insights data for industry: $industry');
      final results = await DemoInsightsService().getAnalysisResults(industry);
      if (mounted) {
        setState(() {
          _enhancedResults = EnhancedAnalysisResults(
            baseResults: results ?? _createFallbackInsights(),
            competitorAnalyses: [],
            improvementAreas: [],
          );
          _isLoading = false;
        });
        
        if (_enhancedResults != null) {
          _staggerController.forward();
        }
      }
    } catch (e) {
      print('[InsightsTab] Error loading demo data: $e');
      if (mounted) {
        setState(() {
          _enhancedResults = EnhancedAnalysisResults(
            baseResults: _createFallbackInsights(),
            competitorAnalyses: [],
            improvementAreas: [],
          );
          _isLoading = false;
        });
      }
    }
  }

  /// Extract enhanced insights data from real analysis result
  EnhancedAnalysisResults? _extractEnhancedInsightsFromAnalysis(AnalysisResult analysisResult) {
    try {
      // Extract base analysis results
      final analysisData = analysisResult.data['analysis_result'] as Map<String, dynamic>?;
      AnalysisResults? baseResults;
      
      if (analysisData != null) {
        // Validate required fields exist
        final requiredFields = ['overall_comparison', 'detailed_comparison', 'actionable_insights', 'strengths_to_maintain', 'market_positioning'];
        bool hasAllFields = true;
        for (final field in requiredFields) {
          if (!analysisData.containsKey(field)) {
            print('[InsightsTab] Missing required field: $field');
            hasAllFields = false;
          }
        }

        if (hasAllFields) {
          print('[InsightsTab] Successfully found all required insights fields');
          baseResults = AnalysisResults.fromJson(analysisData);
        }
      }

      // Extract competitor analysis data
      final competitorAnalysisData = analysisResult.data['competitor_analysis'] as List<dynamic>?;
      final competitorAnalyses = <CompetitorAnalysis>[];
      
      if (competitorAnalysisData != null) {
        print('[InsightsTab] Found competitor_analysis data with ${competitorAnalysisData.length} competitors');
        for (final competitorData in competitorAnalysisData) {
          if (competitorData is Map<String, dynamic>) {
            competitorAnalyses.add(CompetitorAnalysis.fromJson(competitorData));
          }
        }
      } else {
        print('[InsightsTab] No competitor_analysis found in API response');
      }

      // Extract improvement areas data
      final improvementAreasData = analysisResult.data['improvement_areas'] as List<dynamic>?;
      final improvementAreas = <ImprovementArea>[];
      
      if (improvementAreasData != null) {
        print('[InsightsTab] Found improvement_areas data with ${improvementAreasData.length} areas');
        for (final improvementData in improvementAreasData) {
          if (improvementData is Map<String, dynamic>) {
            improvementAreas.add(ImprovementArea.fromJson(improvementData));
          }
        }
      } else {
        print('[InsightsTab] No improvement_areas found in API response');
      }

      // Create enhanced results if we have at least base results or enhanced data
      if (baseResults != null || competitorAnalyses.isNotEmpty || improvementAreas.isNotEmpty) {
        print('[InsightsTab] Successfully extracted enhanced insights data');
        print('[InsightsTab] Base results: ${baseResults != null}');
        print('[InsightsTab] Competitor analyses: ${competitorAnalyses.length}');
        print('[InsightsTab] Improvement areas: ${improvementAreas.length}');
        
        return EnhancedAnalysisResults(
          baseResults: baseResults ?? _createFallbackInsights(),
          competitorAnalyses: competitorAnalyses,
          improvementAreas: improvementAreas,
        );
      }

      return null;

    } catch (e) {
      print('[InsightsTab] Error extracting enhanced insights from analysis result: $e');
      return null;
    }
  }

  /// Create safe fallback insights data when all else fails
  AnalysisResults _createFallbackInsights() {
    print('[InsightsTab] Using fallback insights data');
    
    return AnalysisResults(
      overallComparison: OverallComparison(
        brandScore: 0.65,
        competitorScore: 0.72,
        gap: -0.07,
        brandRanking: 'second',
        confidenceLevel: 0.85,
      ),
      detailedComparison: {
        'performance': DetailedComparison(
          brandScore: 0.65,
          competitorScore: 0.72,
          difference: -0.07,
          insight: 'Performance analysis shows areas for improvement',
          trend: 'stable',
        ),
      },
      actionableInsights: [
        ActionableInsight(
          priority: InsightPriority.high,
          category: 'Performance',
          title: 'Improve Overall Performance',
          description: 'Focus on key performance metrics to enhance competitive position',
          estimatedEffort: '3-4 months',
          expectedImpact: '10-15% improvement',
          roiEstimate: '\$1.2M annually',
          implementationSteps: [
            'Conduct performance audit',
            'Identify key improvement areas',
            'Implement optimization strategies',
            'Monitor and adjust approach',
          ],
          successMetrics: [
            'Performance score improvement',
            'User satisfaction increase',
            'Market share growth',
          ],
        ),
        ActionableInsight(
          priority: InsightPriority.medium,
          category: 'Strategy',
          title: 'Enhance Strategic Position',
          description: 'Develop strategic initiatives to strengthen market position',
          estimatedEffort: '2-3 months',
          expectedImpact: '5-10% improvement',
          roiEstimate: '\$800K annually',
          implementationSteps: [
            'Strategic assessment',
            'Develop positioning strategy',
            'Execute strategic initiatives',
          ],
          successMetrics: [
            'Strategic KPI improvement',
            'Brand perception enhancement',
          ],
        ),
      ],
      strengthsToMaintain: [
        StrengthToMaintain(
          area: 'Brand Recognition',
          description: 'Strong brand awareness and customer loyalty',
          recommendation: 'Continue building on established brand strengths',
          currentScore: 0.75,
        ),
      ],
      marketPositioning: MarketPositioning(
        brandPosition: '${widget.brandName ?? "Brand"} market position analysis',
        competitorPosition: '${widget.competitor ?? "Competitor"} competitive analysis',
        differentiationOpportunity: 'Opportunities for market differentiation',
        targetAudience: 'Target customer segments and positioning',
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!hasAnalysisData) {
      return _buildEmptyState(context);
    }

    if (_isLoading) {
      return _buildLoadingState(context);
    }

    // Check if we have either real analysis result or loaded results
    if (_enhancedResults == null && widget.analysisResult == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          _buildTabBar(),
          const SizedBox(height: 16),
          _buildTabContent(),
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

  Widget _buildTabBar() {
    final availableTabs = _getAvailableTabs();
    
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: availableTabs.asMap().entries.map((entry) {
          final index = entry.key;
          final tab = entry.value;
          final isSelected = _currentTabIndex == index;
          
          return GestureDetector(
            onTap: () => setState(() => _currentTabIndex = index),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.only(right: 16),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(25),
                border: Border.all(
                  color: isSelected ? AppColors.glowBlue : AppColors.glassBorder,
                  width: 1,
                ),
                color: isSelected 
                  ? AppColors.glowBlue.withOpacity(0.1)
                  : Colors.transparent,
              ),
              child: Text(
                tab['title'],
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isSelected ? AppColors.glowBlue : AppColors.textSecondary,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  List<Map<String, dynamic>> _getAvailableTabs() {
    final tabs = <Map<String, dynamic>>[];
    
    // Always show Overview if we have any data
    if (_enhancedResults != null) {
      tabs.add({'title': 'Overview', 'key': 'overview'});
    }
    
    // Show Competitive Analysis if we have competitor data
    if (_enhancedResults?.hasCompetitorAnalysis == true) {
      tabs.add({'title': 'Competitive Analysis', 'key': 'competitive'});
    }
    
    // Show Improvement Areas if we have improvement data
    if (_enhancedResults?.hasImprovementAreas == true) {
      tabs.add({'title': 'Improvement Areas', 'key': 'improvement'});
    }
    
    return tabs;
  }

  Widget _buildTabContent() {
    final availableTabs = _getAvailableTabs();
    
    if (availableTabs.isEmpty || _enhancedResults == null) {
      return _buildErrorState(context);
    }
    
    // Ensure current tab index is within bounds
    if (_currentTabIndex >= availableTabs.length) {
      _currentTabIndex = 0;
    }
    
    final currentTab = availableTabs[_currentTabIndex];
    
    switch (currentTab['key']) {
      case 'overview':
        return _buildOverviewTab();
      case 'competitive':
        return _buildCompetitiveAnalysisTab();
      case 'improvement':
        return _buildImprovementAreasTab();
      default:
        return _buildOverviewTab();
    }
  }

  Widget _buildOverviewTab() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildOverallScores(),
        const SizedBox(height: 32),
        _buildMergedInsightsGrid(),
        const SizedBox(height: 32),
        _buildStrengthsSection(),
      ],
    );
  }

  Widget _buildCompetitiveAnalysisTab() {
    if (!_enhancedResults!.hasCompetitorAnalysis) {
      return Center(
        child: Text(
          'No competitive analysis data available',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 16,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ..._enhancedResults!.competitorAnalyses.map((competitor) => 
          Container(
            margin: const EdgeInsets.only(bottom: 24),
            child: _buildCompetitorAnalysisCard(competitor),
          )
        ).toList(),
      ],
    );
  }

  Widget _buildImprovementAreasTab() {
    if (!_enhancedResults!.hasImprovementAreas) {
      return Center(
        child: Text(
          'No improvement areas data available',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 16,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Improvement Roadmap',
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
              crossAxisCount = 2;
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
                childAspectRatio: 0.8,
              ),
              itemCount: _enhancedResults!.improvementAreas.length,
              itemBuilder: (context, index) {
                return _buildImprovementAreaCard(_enhancedResults!.improvementAreas[index], index);
              },
            );
          },
        ),
      ],
    );
  }

  Widget _buildOverallScores() {
    final overall = _enhancedResults!.overallComparison;
    
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

  Widget _buildMergedInsightsGrid() {
    final actionableInsights = _enhancedResults!.actionableInsights;
    final improvementAreas = _enhancedResults!.improvementAreas;
    
    // Create a merged list of insights with visual distinction
    final mergedItems = <Map<String, dynamic>>[];
    
    // Add actionable insights
    for (final insight in actionableInsights) {
      mergedItems.add({
        'type': 'actionable',
        'data': insight,
        'priority': insight.priority.index,
      });
    }
    
    // Add improvement areas as insights
    for (final area in improvementAreas) {
      mergedItems.add({
        'type': 'improvement',
        'data': area,
        'priority': area.priorityLevel.index,
      });
    }
    
    // Sort by priority
    mergedItems.sort((a, b) => a['priority'].compareTo(b['priority']));
    
    if (mergedItems.isEmpty) {
      return Text(
        'No insights available',
        style: TextStyle(
          color: AppColors.textSecondary,
          fontSize: 16,
        ),
      );
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Strategic Insights & Improvement Areas',
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
              itemCount: mergedItems.length,
              itemBuilder: (context, index) {
                final item = mergedItems[index];
                if (item['type'] == 'actionable') {
                  return _buildInsightCard(item['data'] as ActionableInsight, index);
                } else {
                  return _buildImprovementAreaCard(item['data'] as ImprovementArea, index);
                }
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
    final strengths = _enhancedResults!.strengthsToMaintain;
    
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

  Widget _buildCompetitorAnalysisCard(CompetitorAnalysis competitor) {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppColors.glowPurple, AppColors.glowBlue],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'COMPETITOR ANALYSIS',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
              Spacer(),
              Text(
                '${(competitor.comparisonScore * 100).toInt()}%',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.glowPurple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Competitor Name
          Text(
            competitor.competitorName,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          
          // Strengths
          _buildCompetitorSection('💪 Strengths', competitor.strengths, AppColors.glowBlue),
          const SizedBox(height: 16),
          
          // Weaknesses
          _buildCompetitorSection('⚠️ Weaknesses', competitor.weaknesses, Color(0xFFff6b6b)),
          const SizedBox(height: 16),
          
          // Opportunities
          _buildCompetitorSection('🎯 Opportunities', competitor.opportunities, Color(0xFF4ecdc4)),
          const SizedBox(height: 16),
          
          // Key Differences
          _buildCompetitorSection('🔍 Key Differences', competitor.keyDifferences, AppColors.glowPurple),
        ],
      ),
    );
  }

  Widget _buildCompetitorSection(String title, List<String> items, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
        const SizedBox(height: 8),
        ...items.take(3).map((item) => Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 4,
                height: 4,
                margin: const EdgeInsets.only(top: 8, right: 8),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color,
                ),
              ),
              Expanded(
                child: Text(
                  item,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        )).toList(),
        if (items.length > 3)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              '+${items.length - 3} more',
              style: TextStyle(
                fontSize: 11,
                color: color.withOpacity(0.7),
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildImprovementAreaCard(ImprovementArea area, int index) {
    final isExpanded = _expandedInsight == area.area;
    final colors = area.priorityLevel.gradientColors;
    
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
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _expandedInsight = isExpanded ? null : area.area;
                });
              },
              child: GlassmorphismCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header with priority badge
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: colors.map((c) => Color(c)).toList(),
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            area.priorityLevel.displayName,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        Spacer(),
                        Text(
                          area.timeline,
                          style: TextStyle(
                            fontSize: 11,
                            color: AppColors.textSecondary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    
                    // Progress indicator
                    _buildProgressIndicator(area),
                    const SizedBox(height: 16),
                    
                    // Area title
                    Text(
                      area.area,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    
                    // Description
                    Text(
                      area.description,
                      style: TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                        height: 1.3,
                      ),
                      maxLines: isExpanded ? null : 3,
                      overflow: isExpanded ? null : TextOverflow.ellipsis,
                    ),
                    
                    // Expanded content
                    if (isExpanded) ...[
                      const SizedBox(height: 16),
                      _buildExpandedImprovementContent(area),
                    ],
                    
                    const SizedBox(height: 12),
                    
                    // Expand button
                    Container(
                      width: double.infinity,
                      height: 32,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: colors.map((c) => Color(c).withOpacity(0.2)).toList(),
                        ),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Color(area.priorityLevel.glowColor).withOpacity(0.5),
                        ),
                      ),
                      child: Center(
                        child: Text(
                          isExpanded ? 'Show Less' : 'View Details',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Color(area.priorityLevel.glowColor),
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
    );
  }

  Widget _buildProgressIndicator(ImprovementArea area) {
    final progressPercentage = area.progressPercentage;
    final currentScore = area.currentScore;
    final targetScore = area.targetScore;
    
    Color progressColor;
    if (progressPercentage < 0.4) {
      progressColor = Color(0xFFff6b6b); // Red
    } else if (progressPercentage < 0.7) {
      progressColor = Color(0xFFfeca57); // Yellow
    } else {
      progressColor = Color(0xFF4ecdc4); // Green
    }
    
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Current: ${(currentScore * 100).toInt()}%',
              style: TextStyle(
                fontSize: 11,
                color: AppColors.textSecondary,
              ),
            ),
            Text(
              'Target: ${(targetScore * 100).toInt()}%',
              style: TextStyle(
                fontSize: 11,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            Expanded(
              child: Container(
                height: 6,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(3),
                  color: AppColors.glassBorder,
                ),
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: progressPercentage.clamp(0.0, 1.0),
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(3),
                      color: progressColor,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: progressColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '${(progressPercentage * 100).toInt()}%',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: progressColor,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildExpandedImprovementContent(ImprovementArea area) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Action Items
        if (area.actionItems.isNotEmpty) ...[
          Text(
            'Action Items:',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          ...area.actionItems.take(3).map((item) => Padding(
            padding: const EdgeInsets.only(bottom: 3),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '• ',
                  style: TextStyle(
                    color: Color(area.priorityLevel.glowColor),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Expanded(
                  child: Text(
                    item,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
          const SizedBox(height: 12),
        ],
        
        // Expected Outcomes
        if (area.expectedOutcomes.isNotEmpty) ...[
          Text(
            'Expected Outcomes:',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          ...area.expectedOutcomes.take(2).map((outcome) => Padding(
            padding: const EdgeInsets.only(bottom: 3),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '✓ ',
                  style: TextStyle(
                    color: Color(0xFF4ecdc4),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Expanded(
                  child: Text(
                    outcome,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
        ],
      ],
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