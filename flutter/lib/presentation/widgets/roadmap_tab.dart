import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/insights_models.dart';
import '../../data/services/insights_service.dart';
import 'glassmorphism_card.dart';

class RoadmapTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;
  final dynamic analysisResult; // Using dynamic for now

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
         oldWidget.competitor != widget.competitor)) {
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
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
      print('Error loading roadmap data: $e');
    }
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

    if (_roadmapTimeline == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 32),
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
          // Quarter header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${quarter.quarter} ${quarter.year}',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
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
          // Item header
          Row(
            children: [
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
              const Spacer(),
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