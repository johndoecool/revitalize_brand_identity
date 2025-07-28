import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/insights_models.dart';
import '../../data/services/insights_service.dart';
import '../../data/services/pdf_service.dart';
import 'glassmorphism_card.dart';

class ReportTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;

  const ReportTab({
    Key? key,
    this.brandName,
    this.selectedArea,
    this.competitor,
  }) : super(key: key);

  @override
  State<ReportTab> createState() => _ReportTabState();
}

class _ReportTabState extends State<ReportTab>
    with TickerProviderStateMixin {
  AnalysisResults? _analysisResults;
  RoadmapTimeline? _roadmapTimeline;
  bool _isLoading = false;
  bool _isGeneratingPdf = false;
  String? _shareLink;
  
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
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(
      begin: 0.95,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    _pulseController.repeat(reverse: true);
    
    if (hasAnalysisData) {
      _loadReportData();
    }
  }

  @override
  void dispose() {
    _staggerController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(ReportTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (hasAnalysisData && 
        (oldWidget.brandName != widget.brandName || 
         oldWidget.selectedArea != widget.selectedArea || 
         oldWidget.competitor != widget.competitor)) {
      _loadReportData();
    }
  }

  bool get hasAnalysisData => 
      widget.brandName != null && widget.selectedArea != null && widget.competitor != null;

  Future<void> _loadReportData() async {
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
        
        _staggerController.forward();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
      print('Error loading report data: $e');
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

    if (_analysisResults == null || _roadmapTimeline == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 32),
          _buildExportOptions(),
          const SizedBox(height: 32),
          _buildPreviewCard(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📄 Export & Share Report',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Download and share your brand analysis insights for ${widget.brandName} vs ${widget.competitor}',
          style: TextStyle(
            fontSize: 16,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildExportOptions() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth > 1200;
        final isTablet = constraints.maxWidth > 768;
        
        int crossAxisCount;
        if (isDesktop) {
          crossAxisCount = 4;
        } else if (isTablet) {
          crossAxisCount = 2;
        } else {
          crossAxisCount = 1;
        }
        
        return GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: crossAxisCount,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          childAspectRatio: 0.85,
          children: [
            _buildExportCard(
              icon: '📊',
              title: 'Executive Summary',
              description: 'High-level overview with key metrics and recommendations',
              onTap: () => _generateExecutiveSummary(),
              index: 0,
            ),
            _buildExportCard(
              icon: '📈',
              title: 'Detailed Report',
              description: 'Complete analysis with charts, data sources, and methodology',
              onTap: () => _generateDetailedReport(),
              index: 1,
            ),
            _buildExportCard(
              icon: '📝',
              title: 'Data Export',
              description: 'Raw data and insights in JSON format for further analysis',
              onTap: () => _exportData(),
              index: 2,
            ),
            _buildExportCard(
              icon: '🔗',
              title: 'Share Link',
              description: 'Generate shareable link for stakeholders and team members',
              onTap: () => _generateShareLink(),
              index: 3,
            ),
          ],
        );
      },
    );
  }

  Widget _buildExportCard({
    required String icon,
    required String title,
    required String description,
    required VoidCallback onTap,
    required int index,
  }) {
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: Interval(
              index * 0.15,
              (index * 0.15) + 0.3,
              curve: Curves.easeOut,
            ),
          ),
        );
        
        return Transform.scale(
          scale: animation.value,
          child: Opacity(
            opacity: animation.value,
            child: _ExportCard(
              icon: icon,
              title: title,
              description: description,
              onTap: onTap,
              isGenerating: _isGeneratingPdf && (index == 0 || index == 1),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPreviewCard() {
    return AnimatedBuilder(
      animation: _staggerController,
      builder: (context, child) {
        final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: const Interval(0.6, 1.0, curve: Curves.easeOut),
          ),
        );
        
        return Transform.translate(
          offset: Offset(0, 50 * (1 - animation.value)),
          child: Opacity(
            opacity: animation.value,
            child: GlassmorphismCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Report Preview',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Quick stats
                  Row(
                    children: [
                      Expanded(child: _buildStatCard('Insights', '${_analysisResults!.actionableInsights.length}')),
                      const SizedBox(width: 12),
                      Expanded(child: _buildStatCard('Quarters', '${_roadmapTimeline!.quarters.length}')),
                      const SizedBox(width: 12),
                      Expanded(child: _buildStatCard('Confidence', '${(_analysisResults!.overallComparison.confidenceLevel * 100).toInt()}%')),
                    ],
                  ),
                  const SizedBox(height: 16),
                  
                  // Report contents
                  Text(
                    'Report Contents:',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  ..._getReportContents().map((content) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: AppColors.glowBlue,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            content,
                            style: TextStyle(
                              fontSize: 14,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )).toList(),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.glowBlue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppColors.glowBlue.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: AppColors.glowBlue,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  List<String> _getReportContents() {
    return [
      'Executive Summary with Overall Scores',
      'Brand vs Competitor Analysis',
      'Actionable Insights and Recommendations',
      'Implementation Roadmap Timeline',
      'Detailed Metrics Comparison',
      'Strengths to Maintain',
      'Market Positioning Analysis',
      'Data Sources and Methodology',
    ];
  }

  Future<void> _generateExecutiveSummary() async {
    setState(() {
      _isGeneratingPdf = true;
    });

    try {
      final pdfBytes = await PdfService().generateExecutiveSummary(
        brandName: widget.brandName!,
        competitorName: widget.competitor!,
        analysisArea: widget.selectedArea!,
        analysisResults: _analysisResults!,
      );

      await _savePdf(pdfBytes, 'executive-summary');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Executive Summary generated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error generating PDF: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGeneratingPdf = false;
        });
      }
    }
  }

  Future<void> _generateDetailedReport() async {
    setState(() {
      _isGeneratingPdf = true;
    });

    try {
      final pdfBytes = await PdfService().generateComprehensiveReport(
        brandName: widget.brandName!,
        competitorName: widget.competitor!,
        analysisArea: widget.selectedArea!,
        analysisResults: _analysisResults!,
        roadmapTimeline: _roadmapTimeline!,
      );

      await _savePdf(pdfBytes, 'detailed-report');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Detailed Report generated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error generating PDF: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGeneratingPdf = false;
        });
      }
    }
  }

  Future<void> _exportData() async {
    try {
      final dataExport = PdfService().generateDataExport(
        brandName: widget.brandName!,
        competitorName: widget.competitor!,
        analysisArea: widget.selectedArea!,
        analysisResults: _analysisResults!,
        roadmapTimeline: _roadmapTimeline!,
      );

      final jsonString = JsonEncoder.withIndent('  ').convert(dataExport);
      await _saveJson(jsonString);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Data exported successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error exporting data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _generateShareLink() async {
    try {
      // In a real app, this would generate a shareable link to the report
      final link = 'https://brand-intelligence-hub.com/report/${DateTime.now().millisecondsSinceEpoch}';
      
      setState(() {
        _shareLink = link;
      });
      
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('Share Link Generated'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Your shareable report link:'),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SelectableText(
                    link,
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Note: This is a demo link. In production, this would be a real shareable URL.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('Close'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error generating share link: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _savePdf(Uint8List pdfBytes, String fileName) async {
    if (kIsWeb) {
      // For web, trigger download
      // This would need additional web-specific implementation
      print('PDF generated with ${pdfBytes.length} bytes. Download would trigger on web.');
    } else {
      // For mobile/desktop, save to downloads or documents
      print('PDF generated with ${pdfBytes.length} bytes. Would save to device storage.');
    }
  }

  Future<void> _saveJson(String jsonString) async {
    if (kIsWeb) {
      // For web, trigger download
      print('JSON generated with ${jsonString.length} characters. Download would trigger on web.');
    } else {
      // For mobile/desktop, save to downloads or documents
      print('JSON generated with ${jsonString.length} characters. Would save to device storage.');
    }
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
              'Preparing Report...',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Compiling analysis data and generating export options.',
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
              '📄',
              style: TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 16),
            Text(
              'Export & Share Report',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Professional reports and data exports will be available here after launching an analysis from the Setup tab.',
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
              'Unable to Load Report Data',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'There was an error loading the report data. Please try again.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadReportData,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ExportCard extends StatefulWidget {
  final String icon;
  final String title;
  final String description;
  final VoidCallback onTap;
  final bool isGenerating;

  const _ExportCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.onTap,
    this.isGenerating = false,
  });

  @override
  State<_ExportCard> createState() => _ExportCardState();
}

class _ExportCardState extends State<_ExportCard>
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
    _hoverAnimation = Tween<double>(begin: 1.0, end: 1.05).animate(
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
              onTap: widget.isGenerating ? null : widget.onTap,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppColors.glassBackground.withOpacity(_isHovered ? 0.3 : 0.2),
                      AppColors.glassBackground.withOpacity(_isHovered ? 0.2 : 0.1),
                    ],
                  ),
                  border: Border.all(
                    color: _isHovered 
                        ? AppColors.glowBlue.withOpacity(0.5)
                        : AppColors.glassBorder,
                    width: 1,
                  ),
                  boxShadow: _isHovered ? [
                    BoxShadow(
                      color: AppColors.glowBlue.withOpacity(0.2),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ] : null,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (widget.isGenerating) ...[
                      Shimmer.fromColors(
                        baseColor: AppColors.glassBorder,
                        highlightColor: AppColors.glowBlue.withOpacity(0.3),
                        child: Text(
                          widget.icon,
                          style: TextStyle(fontSize: 48),
                        ),
                      ),
                    ] else ...[
                      Text(
                        widget.icon,
                        style: TextStyle(fontSize: 48),
                      ),
                    ],
                    const SizedBox(height: 16),
                    Text(
                      widget.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.description,
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textSecondary,
                        height: 1.4,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    Container(
                      width: double.infinity,
                      height: 36,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            AppColors.glowBlue.withOpacity(widget.isGenerating ? 0.1 : 0.3),
                            AppColors.glowPurple.withOpacity(widget.isGenerating ? 0.1 : 0.3),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: AppColors.glowBlue.withOpacity(widget.isGenerating ? 0.2 : 0.5),
                        ),
                      ),
                      child: Center(
                        child: widget.isGenerating
                            ? SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
                                ),
                              )
                            : Text(
                                _getButtonText(),
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.glowBlue,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  String _getButtonText() {
    if (widget.title.contains('PDF') || widget.title.contains('Summary') || widget.title.contains('Report')) {
      return 'Download PDF';
    } else if (widget.title.contains('Data')) {
      return 'Download JSON';
    } else if (widget.title.contains('Link')) {
      return 'Generate Link';
    }
    return 'Export';
  }
}