import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/insights_models.dart';
import '../../data/services/insights_service.dart';
import '../../data/services/data_collection_service.dart';
import 'glassmorphism_card.dart';

class RoadmapTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;
  final AnalysisResult? analysisResult;

  const RoadmapTab({
    Key? key,
    this.brandName,
    this.selectedArea,
    this.competitor,
    this.analysisResult,
  }) : super(key: key);

  @override
  State<RoadmapTab> createState() => _RoadmapTabState();
}

class _RoadmapTabState extends State<RoadmapTab>
    with TickerProviderStateMixin {
  AnalysisResults? _analysisResults;
  RoadmapTimeline? _roadmapTimeline;
  bool _isLoading = false;
  
  late AnimationController _staggerController;
  late AnimationController _progressController;
  late List<AnimationController> _progressControllers;

  @override
  void initState() {
    super.initState();
    
    _staggerController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _progressController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _progressControllers = [];
    
    if (hasAnalysisData) {
      _loadRoadmapData();
    }
  }

  @override
  void dispose() {
    _staggerController.dispose();
    _progressController.dispose();
    for (final controller in _progressControllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  void didUpdateWidget(RoadmapTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (hasAnalysisData && 
        (oldWidget.brandName != widget.brandName || 
         oldWidget.selectedArea != widget.selectedArea || 
         oldWidget.competitor != widget.competitor ||
         oldWidget.analysisResult != widget.analysisResult)) {
      _loadRoadmapData();
    }
  }

  bool get hasAnalysisData => 
      widget.brandName != null && widget.selectedArea != null && widget.competitor != null;

  Future<void> _loadRoadmapData() async {
    if (!hasAnalysisData) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Layer 1: Try to extract real roadmap data from analysis result first
      if (widget.analysisResult != null) {
        print('[RoadmapTab] Attempting to extract roadmap from real analysis result');
        final realRoadmap = _extractRoadmapFromAnalysis(widget.analysisResult!);
        if (realRoadmap != null) {
          print('[RoadmapTab] Successfully using real roadmap data');
          if (mounted) {
            setState(() {
              _roadmapTimeline = realRoadmap;
              _isLoading = false;
            });
            _initializeProgressControllers();
            _staggerController.forward();
            _startProgressAnimations();
          }
          return;
        } else {
          print('[RoadmapTab] Failed to extract real roadmap data, falling back to demo data');
        }
      } else {
        print('[RoadmapTab] No analysis result available, using demo data');
      }

      // Layer 2: Fallback to demo data
      await _loadDemoRoadmapData();
      
    } catch (e) {
      print('[RoadmapTab] Error loading roadmap data: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  /// Load demo roadmap data as fallback
  Future<void> _loadDemoRoadmapData() async {
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

      print('[RoadmapTab] Loading demo roadmap data for industry: $industry');
      final insightsService = DemoInsightsService();
      final results = await insightsService.getAnalysisResults(industry);
      
      if (results != null && mounted) {
        final timeline = await insightsService.generateRoadmap(
          results,
          widget.brandName!,
          widget.competitor!,
        );
        
        setState(() {
          _analysisResults = results;
          _roadmapTimeline = timeline;
          _isLoading = false;
        });
        
        _initializeProgressControllers();
        _staggerController.forward();
        _startProgressAnimations();
      } else {
        // Layer 3: Safe fallback
        if (mounted) {
          setState(() {
            _roadmapTimeline = _createFallbackRoadmap();
            _isLoading = false;
          });
          _initializeProgressControllers();
          _staggerController.forward();
          _startProgressAnimations();
        }
      }
    } catch (e) {
      print('[RoadmapTab] Error loading demo roadmap data: $e');
      if (mounted) {
        setState(() {
          _roadmapTimeline = _createFallbackRoadmap();
          _isLoading = false;
        });
        _initializeProgressControllers();
        _staggerController.forward();
        _startProgressAnimations();
      }
    }
  }

  /// Extract roadmap data from real analysis result
  RoadmapTimeline? _extractRoadmapFromAnalysis(AnalysisResult analysisResult) {
    try {
      // Debug: Print the exact structure we're receiving
      print('[RoadmapTab] ===== DEBUGGING ROADMAP EXTRACTION =====');
      print('[RoadmapTab] analysisResult type: ${analysisResult.runtimeType}');
      print('[RoadmapTab] analysisResult.data type: ${analysisResult.data.runtimeType}');
      print('[RoadmapTab] Analysis result data keys: ${analysisResult.data.keys}');
      
      // Check each key individually
      for (final key in analysisResult.data.keys) {
        print('[RoadmapTab] Key "$key": ${analysisResult.data[key]?.runtimeType}');
        if (key == 'roadmap') {
          print('[RoadmapTab] *** FOUND ROADMAP KEY! ***');
          final roadmapValue = analysisResult.data[key];
          print('[RoadmapTab] Roadmap value type: ${roadmapValue.runtimeType}');
          print('[RoadmapTab] Roadmap value: $roadmapValue');
        }
      }
      
      // First, try to get roadmap directly from root level
      var roadmapData = analysisResult.data['roadmap'] as Map<String, dynamic>?;
      
      if (roadmapData != null) {
        print('[RoadmapTab] ✅ Found roadmap at root level');
        print('[RoadmapTab] Roadmap keys: ${roadmapData.keys}');
      } else {
        print('[RoadmapTab] ❌ No roadmap at root level');
        
        // Try different approaches to access roadmap
        final roadmapDynamic = analysisResult.data['roadmap'];
        print('[RoadmapTab] roadmapDynamic: $roadmapDynamic');
        print('[RoadmapTab] roadmapDynamic type: ${roadmapDynamic.runtimeType}');
        
        if (roadmapDynamic != null) {
          print('[RoadmapTab] 🎉 roadmapDynamic is not null, trying to cast...');
          try {
            roadmapData = roadmapDynamic as Map<String, dynamic>;
            print('[RoadmapTab] ✅ Successfully cast roadmapDynamic to Map<String, dynamic>');
          } catch (e) {
            print('[RoadmapTab] ❌ Failed to cast roadmapDynamic: $e');
          }
        }
        
        // Add comprehensive logging for debugging
        print('[RoadmapTab] 🔍 Complete data structure investigation:');
        print('[RoadmapTab] Full analysisResult.data content: ${analysisResult.data}');
        
        // Check if roadmap exists in any nested location
        void checkForRoadmap(dynamic obj, String path) {
          if (obj is Map<String, dynamic>) {
            obj.forEach((key, value) {
              final currentPath = path.isEmpty ? key : '$path.$key';
              if (key.toLowerCase().contains('roadmap')) {
                print('[RoadmapTab] 🎯 Found roadmap-related key at $currentPath: $value');
              }
              if (value is Map || value is List) {
                checkForRoadmap(value, currentPath);
              }
            });
          } else if (obj is List) {
            for (int i = 0; i < obj.length; i++) {
              checkForRoadmap(obj[i], '${path}[$i]');
            }
          }
        }
        
        checkForRoadmap(analysisResult.data, '');
        print('[RoadmapTab] 🔍 Investigation complete.');
        // Fallback: try inside analysis_result for compatibility
        final analysisData = analysisResult.data['analysis_result'] as Map<String, dynamic>?;
        if (analysisData != null) {
          roadmapData = analysisData['roadmap'] as Map<String, dynamic>?;
          if (roadmapData != null) {
            print('[RoadmapTab] Found roadmap inside analysis_result');
          }
        }
      }
      
      if (roadmapData == null) {
        print('[RoadmapTab] No roadmap found in API response');
        print('[RoadmapTab] Available top-level keys: ${analysisResult.data.keys}');
        
        // Try to generate roadmap from actionable_insights as fallback
        final analysisData = analysisResult.data['analysis_result'] as Map<String, dynamic>?;
        if (analysisData != null) {
          final actionableInsights = analysisData['actionable_insights'] as List<dynamic>?;
          if (actionableInsights != null && actionableInsights.isNotEmpty) {
            print('[RoadmapTab] Generating roadmap from ${actionableInsights.length} actionable insights');
            return _generateRoadmapFromInsights(actionableInsights, analysisData);
          }
        }
        
        print('[RoadmapTab] No actionable insights found either, cannot generate roadmap');
        return null;
      }

      final quarterlyRoadmaps = roadmapData['quarterly_roadmaps'] as List<dynamic>?;
      if (quarterlyRoadmaps == null || quarterlyRoadmaps.isEmpty) {
        print('[RoadmapTab] No quarterly_roadmaps found in roadmap data');
        return null;
      }

      print('[RoadmapTab] Successfully found roadmap with ${quarterlyRoadmaps.length} quarters');
      print('[RoadmapTab] Available roadmap fields: ${roadmapData.keys}');

      // Convert quarterly roadmaps to RoadmapQuarter objects
      final quarters = <RoadmapQuarter>[];
      final currentYear = _getCurrentYear();

      for (int i = 0; i < quarterlyRoadmaps.length; i++) {
        final quarterData = quarterlyRoadmaps[i] as Map<String, dynamic>;
        final quarter = _mapApiQuarterToModel(quarterData, currentYear, i);
        if (quarter != null) {
          quarters.add(quarter);
        }
      }

      if (quarters.isEmpty) {
        print('[RoadmapTab] No valid quarters could be mapped');
        return null;
      }

      final brandName = roadmapData['brand_name']?.toString() ?? widget.brandName ?? 'Brand';
      final competitorName = widget.competitor ?? 'Competitor';

      print('[RoadmapTab] Successfully created roadmap timeline with ${quarters.length} quarters');

      return EnhancedRoadmapTimeline(
        quarters: quarters,
        brandName: brandName,
        competitorName: competitorName,
        roadmapId: roadmapData['roadmap_id']?.toString() ?? '',
        competitorAnalysisSummary: roadmapData['competitor_analysis_summary']?.toString() ?? '',
        strategicVision: roadmapData['strategic_vision']?.toString() ?? '',
        marketOpportunity: roadmapData['market_opportunity']?.toString() ?? '',
        competitiveAdvantages: (roadmapData['competitive_advantages'] as List<dynamic>?)
            ?.map((e) => e.toString()).toList() ?? [],
        totalEstimatedBudget: roadmapData['total_estimated_budget']?.toString() ?? '',
        riskFactors: (roadmapData['risk_factors'] as List<dynamic>?)
            ?.map((e) => e.toString()).toList() ?? [],
        confidenceScore: (roadmapData['confidence_score'] ?? 0.0).toDouble(),
        generatedAt: roadmapData['generated_at']?.toString() ?? '',
      );

    } catch (e) {
      print('[RoadmapTab] Error extracting roadmap from analysis result: $e');
      return null;
    }
  }

  /// Get current year for roadmap quarters
  int _getCurrentYear() {
    return DateTime.now().year;
  }

  /// Format budget string to compact format (e.g., "$15,000 - $25,000" -> "$15K - $25K")
  String _formatBudget(String budget) {
    // Convert "$15,000 - $25,000" to "$15K - $25K"
    return budget
        .replaceAllMapped(RegExp(r'\$(\d+),(\d{3})'), (match) {
          final thousands = int.parse(match.group(1)!);
          return '\$${thousands}K';
        })
        .replaceAllMapped(RegExp(r'\$(\d+)\.(\d+)M'), (match) {
          return '\$${match.group(1)}.${match.group(2)}M';
        });
  }

  /// Format text to title case and replace underscores
  String _formatHeaderText(String text) {
    return text
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word.isEmpty ? '' : '${word[0].toUpperCase()}${word.substring(1).toLowerCase()}')
        .join(' ');
  }

  /// Map API quarter data to RoadmapQuarter model
  RoadmapQuarter? _mapApiQuarterToModel(Map<String, dynamic> quarterData, int baseYear, int index) {
    try {
      final quarter = quarterData['quarter']?.toString() ?? 'Q${index + 1}';
      
      // Calculate year based on quarter progression
      int year = baseYear;
      if (quarter == 'Q1' && index > 0) {
        // If we see Q1 after other quarters, increment year
        year = baseYear + (index ~/ 4);
      } else if (quarter == 'Q2') {
        year = baseYear + (index ~/ 4);
      } else if (quarter == 'Q3') {
        year = baseYear + (index ~/ 4);
      } else if (quarter == 'Q4') {
        year = baseYear + (index ~/ 4);
      }

      final actions = quarterData['actions'] as List<dynamic>? ?? [];
      final items = <RoadmapItem>[];

      for (final actionData in actions) {
        if (actionData is Map<String, dynamic>) {
          final item = _mapApiActionToRoadmapItem(actionData);
          if (item != null) {
            items.add(item);
          }
        }
      }

      // Calculate progress percentage based on quarter position (Q1=25%, Q2=50%, etc.)
      final progressPercentage = ((index + 1) * 25.0).clamp(0.0, 100.0);

      // Extract enhanced quarter data
      final quarterTheme = quarterData['quarter_theme']?.toString();
      final strategicGoals = (quarterData['strategic_goals'] as List<dynamic>?)
          ?.map((e) => e.toString()).toList();
      final quarterBudget = quarterData['quarter_budget']?.toString();
      final successCriteria = (quarterData['success_criteria'] as List<dynamic>?)
          ?.map((e) => e.toString()).toList();

      return RoadmapQuarter(
        quarter: quarter,
        year: year.toString(),
        items: items,
        progressPercentage: progressPercentage,
        quarterTheme: quarterTheme,
        strategicGoals: strategicGoals,
        quarterBudget: quarterBudget,
        successCriteria: successCriteria,
      );

    } catch (e) {
      print('[RoadmapTab] Error mapping quarter data: $e');
      return null;
    }
  }

  /// Map API action to RoadmapItem model
  RoadmapItem? _mapApiActionToRoadmapItem(Map<String, dynamic> actionData) {
    try {
      final title = actionData['title']?.toString() ?? 'Untitled Action';
      final description = actionData['description']?.toString() ?? '';
      final priorityString = actionData['priority']?.toString() ?? 'low';
      final priority = InsightPriority.fromString(priorityString);
      final expectedImpact = actionData['expected_impact']?.toString() ?? '';
      
      // Map success_metrics to tasks (primary source)
      final successMetrics = actionData['success_metrics'] as List<dynamic>? ?? [];
      final tasks = successMetrics.map((metric) => metric.toString()).toList();

      // Extract enhanced action data
      final actionId = actionData['action_id']?.toString();
      final category = actionData['category']?.toString();
      final estimatedEffort = actionData['estimated_effort']?.toString();
      final budgetEstimate = actionData['budget_estimate']?.toString();
      final dependencies = (actionData['dependencies'] as List<dynamic>?)
          ?.map((e) => e.toString()).toList();
      final successMetricsList = (actionData['success_metrics'] as List<dynamic>?)
          ?.map((e) => e.toString()).toList();

      return RoadmapItem(
        title: title,
        description: description,
        priority: priority,
        tasks: tasks,
        expectedImpact: expectedImpact,
        isCompleted: false,
        actionId: actionId,
        category: category,
        estimatedEffort: estimatedEffort,
        budgetEstimate: budgetEstimate,
        successMetrics: successMetricsList,
        dependencies: dependencies,
      );

    } catch (e) {
      print('[RoadmapTab] Error mapping action data: $e');
      return null;
    }
  }

  /// Generate roadmap from actionable insights when roadmap field is missing
  RoadmapTimeline? _generateRoadmapFromInsights(List<dynamic> actionableInsights, Map<String, dynamic> analysisData) {
    try {
      final quarters = <RoadmapQuarter>[];
      final currentYear = _getCurrentYear();
      
      // Parse insights and sort by priority
      final insights = <Map<String, dynamic>>[];
      for (final insight in actionableInsights) {
        if (insight is Map<String, dynamic>) {
          insights.add(insight);
        }
      }
      
      // Sort by priority: high > medium > low
      insights.sort((a, b) {
        final priorityA = (a['priority']?.toString() ?? 'low').toLowerCase();
        final priorityB = (b['priority']?.toString() ?? 'low').toLowerCase();
        
        final priorityOrder = {'high': 0, 'medium': 1, 'low': 2};
        final orderA = priorityOrder[priorityA] ?? 2;
        final orderB = priorityOrder[priorityB] ?? 2;
        
        return orderA.compareTo(orderB);
      });
      
      // Create 4 quarters
      for (int i = 0; i < 4; i++) {
        quarters.add(RoadmapQuarter(
          quarter: 'Q${i + 1}',
          year: currentYear.toString(),
          items: [],
          progressPercentage: ((i + 1) * 25.0).clamp(0.0, 100.0),
        ));
      }
      
      // Distribute insights across quarters
      for (int i = 0; i < insights.length; i++) {
        final insight = insights[i];
        final quarterIndex = i % 4; // Distribute evenly across quarters
        
        final roadmapItem = _mapInsightToRoadmapItem(insight);
        if (roadmapItem != null) {
          quarters[quarterIndex].items.add(roadmapItem);
        }
      }
      
      final brandName = analysisData['brand_name']?.toString() ?? widget.brandName ?? 'Brand';
      final competitorName = analysisData['competitor_name']?.toString() ?? widget.competitor ?? 'Competitor';
      
      print('[RoadmapTab] Generated roadmap with ${quarters.where((q) => q.items.isNotEmpty).length} active quarters');
      
      return RoadmapTimeline(
        quarters: quarters,
        brandName: brandName,
        competitorName: competitorName,
      );
      
    } catch (e) {
      print('[RoadmapTab] Error generating roadmap from insights: $e');
      return null;
    }
  }
  
  /// Map an actionable insight to a roadmap item
  RoadmapItem? _mapInsightToRoadmapItem(Map<String, dynamic> insight) {
    try {
      final title = insight['title']?.toString() ?? 'Strategic Initiative';
      final description = insight['description']?.toString() ?? '';
      final priorityString = insight['priority']?.toString() ?? 'medium';
      final priority = InsightPriority.fromString(priorityString);
      final expectedImpact = insight['expected_impact']?.toString() ?? '';
      
      // Map implementation_steps to tasks
      final implementationSteps = insight['implementation_steps'] as List<dynamic>? ?? [];
      final tasks = implementationSteps.map((step) => step.toString()).toList();
      
      // If no implementation steps, use success_metrics as tasks
      if (tasks.isEmpty) {
        final successMetrics = insight['success_metrics'] as List<dynamic>? ?? [];
        tasks.addAll(successMetrics.map((metric) => metric.toString()));
      }
      
      // If still no tasks, provide default ones
      if (tasks.isEmpty) {
        tasks.addAll([
          'Conduct initial assessment',
          'Develop implementation plan',
          'Execute key activities',
          'Monitor and measure results',
        ]);
      }
      
      return RoadmapItem(
        title: title,
        description: description,
        priority: priority,
        tasks: tasks,
        expectedImpact: expectedImpact,
        isCompleted: false,
      );
      
    } catch (e) {
      print('[RoadmapTab] Error mapping insight to roadmap item: $e');
      return null;
    }
  }

  /// Create safe fallback roadmap when all else fails
  RoadmapTimeline _createFallbackRoadmap() {
    print('[RoadmapTab] Using fallback roadmap data');
    
    final currentYear = _getCurrentYear();
    final quarters = <RoadmapQuarter>[];

    for (int i = 0; i < 4; i++) {
      quarters.add(RoadmapQuarter(
        quarter: 'Q${i + 1}',
        year: currentYear.toString(),
        items: [
          RoadmapItem(
            title: 'Strategic Initiative ${i + 1}',
            description: 'Key strategic initiative for Q${i + 1} focused on competitive improvement',
            priority: i == 0 ? InsightPriority.high : InsightPriority.medium,
            tasks: [
              'Complete initial assessment',
              'Develop implementation plan', 
              'Execute key activities',
              'Monitor progress and results',
            ],
            expectedImpact: 'Enhanced competitive position and market performance',
            isCompleted: false,
          ),
        ],
        progressPercentage: ((i + 1) * 25.0).clamp(0.0, 100.0),
      ));
    }

    return RoadmapTimeline(
      quarters: quarters,
      brandName: widget.brandName ?? 'Brand',
      competitorName: widget.competitor ?? 'Competitor',
    );
  }

  void _initializeProgressControllers() {
    // Dispose existing controllers
    for (final controller in _progressControllers) {
      controller.dispose();
    }
    _progressControllers.clear();
    
    // Create controllers for each quarter
    if (_roadmapTimeline != null) {
      for (int i = 0; i < _roadmapTimeline!.quarters.length; i++) {
        final controller = AnimationController(
          duration: Duration(milliseconds: 1500 + (i * 200)),
          vsync: this,
        );
        _progressControllers.add(controller);
      }
    }
  }

  void _startProgressAnimations() {
    for (int i = 0; i < _progressControllers.length; i++) {
      Future.delayed(Duration(milliseconds: i * 300), () {
        if (mounted) {
          _progressControllers[i].forward();
        }
      });
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

    // Check if we have either real analysis result or loaded roadmap
    if (_roadmapTimeline == null && widget.analysisResult == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          
          // Enhanced header section for EnhancedRoadmapTimeline
          if (_roadmapTimeline is EnhancedRoadmapTimeline) ...[
            _buildRiskFactors(_roadmapTimeline as EnhancedRoadmapTimeline),
            const SizedBox(height: 24),
            _buildSummaryCard(_roadmapTimeline as EnhancedRoadmapTimeline),
            const SizedBox(height: 24),
            _buildStrategicInfoCards(_roadmapTimeline as EnhancedRoadmapTimeline),
            const SizedBox(height: 32),
          ] else ...[
            const SizedBox(height: 8),
          ],
          
          _buildTimeline(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🗺️ Implementation Roadmap',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Strategic timeline for ${widget.brandName} to improve brand reputation and competitive position',
          style: TextStyle(
            fontSize: 16,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildRiskFactors(EnhancedRoadmapTimeline roadmap) {
    if (roadmap.riskFactors.isEmpty) return Container();
    
    return Column(
      children: roadmap.riskFactors.map((risk) => Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.orange.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.orange.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Icon(
              Icons.warning_amber_outlined,
              color: Colors.orange,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                risk,
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      )).toList(),
    );
  }

  Widget _buildSummaryCard(EnhancedRoadmapTimeline roadmap) {
    return GlassmorphismCard(
      child: Row(
        children: [
          Expanded(
            child: _buildSummaryMetric(
              'Total Budget',
              _formatBudget(roadmap.totalEstimatedBudget),
              Icons.account_balance_wallet,
              AppColors.glowBlue,
            ),
          ),
          Container(
            width: 1,
            height: 60,
            color: AppColors.glassBorder,
            margin: const EdgeInsets.symmetric(horizontal: 16),
          ),
          Expanded(
            child: _buildSummaryMetric(
              'Timeline',
              '${roadmap.quarters.length} Quarters',
              Icons.schedule,
              AppColors.glowPurple,
            ),
          ),
          Container(
            width: 1,
            height: 60,
            color: AppColors.glassBorder,
            margin: const EdgeInsets.symmetric(horizontal: 16),
          ),
          Expanded(
            child: _buildSummaryMetric(
              'Confidence',
              '${(roadmap.confidenceScore * 100).toInt()}%',
              Icons.trending_up,
              Color(0xFF4ecdc4),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryMetric(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildStrategicInfoCards(EnhancedRoadmapTimeline roadmap) {
    final infoCards = [
      {
        'title': 'Strategic Vision',
        'content': roadmap.strategicVision,
        'icon': Icons.visibility,
      },
      {
        'title': 'Market Opportunity',
        'content': roadmap.marketOpportunity,
        'icon': Icons.trending_up,
      },
      {
        'title': 'Competitive Advantages',
        'content': roadmap.competitiveAdvantages.join('\n• '),
        'icon': Icons.star,
      },
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth > 1200;
        final isTablet = constraints.maxWidth > 768;
        
        if (isDesktop) {
          return Row(
            children: infoCards.map((card) => Expanded(
              child: Container(
                margin: const EdgeInsets.only(right: 16),
                child: _buildInfoCard(card),
              ),
            )).toList(),
          );
        } else {
          return Column(
            children: infoCards.map((card) => Container(
              margin: const EdgeInsets.only(bottom: 16),
              child: _buildInfoCard(card),
            )).toList(),
          );
        }
      },
    );
  }

  Widget _buildInfoCard(Map<String, dynamic> cardData) {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                cardData['icon'] as IconData,
                color: AppColors.glowBlue,
                size: 20,
              ),
              const SizedBox(width: 12),
              Text(
                cardData['title'] as String,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            cardData['content'] as String,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeline() {
    final quarters = _roadmapTimeline!.quarters;
    
    return Column(
      children: quarters.asMap().entries.map((entry) {
        final index = entry.key;
        final quarter = entry.value;
        return _buildTimelineItem(quarter, index);
      }).toList(),
    );
  }

  Widget _buildTimelineItem(RoadmapQuarter quarter, int index) {
    final isLast = index == _roadmapTimeline!.quarters.length - 1;
    
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: Interval(
              index * 0.1,
              (index * 0.1) + 0.3,
              curve: Curves.easeOut,
            ),
          ),
        );
        
        return Transform.translate(
          offset: Offset(-100 * (1 - animation.value), 0),
          child: Opacity(
            opacity: animation.value,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Timeline marker
                _buildTimelineMarker(quarter, index),
                const SizedBox(width: 24),
                
                // Content
                Expanded(
                  child: Container(
                    margin: EdgeInsets.only(bottom: isLast ? 0 : 32),
                    child: _buildQuarterContent(quarter, index),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTimelineMarker(RoadmapQuarter quarter, int index) {
    return Column(
      children: [
        // Quarter marker
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppColors.glowBlue,
                AppColors.glowPurple,
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.glowBlue.withOpacity(0.3),
                blurRadius: 15,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Center(
            child: Text(
              quarter.quarter,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ),
        ),
        
        // Connecting line
        if (index < _roadmapTimeline!.quarters.length - 1)
          Container(
            width: 2,
            height: 120,
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  AppColors.glowBlue.withOpacity(0.5),
                  AppColors.glowPurple.withOpacity(0.3),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildQuarterContent(RoadmapQuarter quarter, int index) {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Quarter header with theme
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${quarter.quarter} ${quarter.year}',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      if (quarter.quarterTheme != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          quarter.quarterTheme!,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: AppColors.glowBlue,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                    ],
                  ),
                  if (quarter.items.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.glowBlue.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: AppColors.glowBlue.withOpacity(0.5),
                        ),
                      ),
                      child: Text(
                        '${quarter.items.length} initiative${quarter.items.length != 1 ? 's' : ''}',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.glowBlue,
                        ),
                      ),
                    ),
                ],
              ),
              
              // Quarter budget
              if (quarter.quarterBudget != null) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Color(0xFF4ecdc4).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Color(0xFF4ecdc4).withOpacity(0.3)),
                  ),
                  child: Text(
                    'Budget: ${_formatBudget(quarter.quarterBudget!)}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF4ecdc4),
                    ),
                  ),
                ),
              ],
            ],
          ),
          
          // Strategic goals section
          if (quarter.strategicGoals != null && quarter.strategicGoals!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.glowPurple.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.glowPurple.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Strategic Goals',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...quarter.strategicGoals!.map((goal) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 4,
                          height: 4,
                          margin: const EdgeInsets.only(top: 6, right: 8),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: AppColors.glowPurple,
                          ),
                        ),
                        Expanded(
                          child: Text(
                            goal,
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                              height: 1.3,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )).toList(),
                ],
              ),
            ),
          ],
          
          if (quarter.items.isEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.glassBorder.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: AppColors.glassBorder.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.schedule,
                    color: AppColors.textSecondary,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Available for additional initiatives',
                    style: TextStyle(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
          ] else ...[
            const SizedBox(height: 16),
            
            // Progress bar
            _buildProgressBar(index),
            const SizedBox(height: 16),
            
            // Quarter items
            ...quarter.items.asMap().entries.map((entry) {
              final itemIndex = entry.key;
              final item = entry.value;
              return Container(
                margin: EdgeInsets.only(
                  bottom: itemIndex < quarter.items.length - 1 ? 16 : 0,
                ),
                child: _buildRoadmapItemCard(item),
              );
            }).toList(),
          ],
          
          // Success criteria section
          if (quarter.successCriteria != null && quarter.successCriteria!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Color(0xFF4ecdc4).withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Color(0xFF4ecdc4).withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.check_circle_outline,
                        color: Color(0xFF4ecdc4),
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Success Criteria',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ...quarter.successCriteria!.map((criteria) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 4,
                          height: 4,
                          margin: const EdgeInsets.only(top: 6, right: 8),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Color(0xFF4ecdc4),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            criteria,
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                              height: 1.3,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )).toList(),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildProgressBar(int quarterIndex) {
    if (quarterIndex >= _progressControllers.length) {
      return Container();
    }
    
    return AnimatedBuilder(
      animation: _progressControllers[quarterIndex],
      builder: (context, child) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Quarter Progress',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                Text(
                  '${(_progressControllers[quarterIndex].value * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.glowBlue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Container(
              height: 6,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(3),
                color: AppColors.glassBorder.withOpacity(0.3),
              ),
              child: Stack(
                children: [
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(3),
                      color: AppColors.glassBorder.withOpacity(0.1),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: _progressControllers[quarterIndex].value,
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(3),
                        gradient: LinearGradient(
                          colors: [
                            AppColors.glowBlue,
                            AppColors.glowPurple,
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildRoadmapItemCard(RoadmapItem item) {
    final colors = item.priority.gradientColors;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(colors[0]).withOpacity(0.1),
            Color(colors[1]).withOpacity(0.05),
          ],
        ),
        border: Border.all(
          color: Color(item.priority.glowColor).withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Item header with category badge and budget
          Row(
            children: [
              // Priority badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: colors.map((c) => Color(c)).toList(),
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  item.priority.displayName,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
              
              // Category badge
              if (item.category != null) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.glowBlue.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.glowBlue.withOpacity(0.3)),
                  ),
                  child: Text(
                    item.category!,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: AppColors.glowBlue,
                    ),
                  ),
                ),
              ],
              
              const Spacer(),
              
              // Budget
              if (item.budgetEstimate != null) ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Color(0xFF4ecdc4).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _formatBudget(item.budgetEstimate!),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF4ecdc4),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
              ],
              
              if (item.isCompleted)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Completed',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: Colors.green,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          
          // Title and description
          Text(
            item.title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            item.description,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              height: 1.4,
            ),
          ),
          
          // Tasks
          if (item.tasks.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              'Key Tasks:',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            ...item.tasks.take(3).map((task) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 4,
                    height: 4,
                    margin: const EdgeInsets.only(top: 6, right: 8),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Color(item.priority.glowColor),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      task,
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            )).toList(),
            if (item.tasks.length > 3)
              Padding(
                padding: const EdgeInsets.only(left: 12),
                child: Text(
                  '+${item.tasks.length - 3} more tasks',
                  style: TextStyle(
                    fontSize: 11,
                    color: Color(item.priority.glowColor),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
          ],
          
          // Dependencies section
          if (item.dependencies != null && item.dependencies!.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.orange.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.link,
                        size: 14,
                        color: Colors.orange,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        'Dependencies:',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ...item.dependencies!.map((dependency) => Padding(
                    padding: const EdgeInsets.only(bottom: 2),
                    child: Text(
                      '• $dependency',
                      style: TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  )).toList(),
                ],
              ),
            ),
          ],
          
          // Estimated effort
          if (item.estimatedEffort != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.glowPurple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                'Effort: ${item.estimatedEffort}',
                style: TextStyle(
                  fontSize: 11,
                  color: AppColors.glowPurple,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],

          // Expected impact
          if (item.expectedImpact.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Color(item.priority.glowColor).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Color(item.priority.glowColor).withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.trending_up,
                    size: 16,
                    color: Color(item.priority.glowColor),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Expected Impact: ${item.expectedImpact}',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
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
              'Generating Roadmap...',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Creating a strategic implementation timeline based on insights.',
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
              '🗺️',
              style: TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 16),
            Text(
              'Implementation Roadmap',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Strategic implementation timeline and quarterly roadmap will appear here after launching an analysis from the Setup tab.',
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
              'Unable to Load Roadmap',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'There was an error generating the roadmap. Please try again.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadRoadmapData,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}