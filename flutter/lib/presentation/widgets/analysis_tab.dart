import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../data/models/chart_data.dart';
import '../../data/services/demo_data_service.dart';
import '../../data/services/data_collection_service.dart';
import 'charts/radar_chart_widget.dart';
import 'charts/doughnut_chart_widget.dart';
import 'charts/line_chart_widget.dart';
import 'charts/bar_chart_widget.dart';
import 'glassmorphism_card.dart';

class AnalysisTab extends StatefulWidget {
  final String? brandName;
  final String? selectedArea;
  final String? competitor;
  final AnalysisResult? analysisResult;

  const AnalysisTab({
    Key? key,
    this.brandName,
    this.selectedArea,
    this.competitor,
    this.analysisResult,
  }) : super(key: key);

  @override
  State<AnalysisTab> createState() => _AnalysisTabState();
}

class _AnalysisTabState extends State<AnalysisTab> {
  CompleteBrandDataModel? _brandData;
  bool _isLoading = false;

  bool get hasAnalysisData => 
      widget.brandName != null && widget.selectedArea != null && widget.competitor != null;

  @override
  void didUpdateWidget(AnalysisTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (hasAnalysisData && 
        (oldWidget.brandName != widget.brandName || 
         oldWidget.selectedArea != widget.selectedArea || 
         oldWidget.competitor != widget.competitor)) {
      _loadDemoData();
    }
  }

  @override
  void initState() {
    super.initState();
    if (hasAnalysisData) {
      _loadDemoData();
    }
  }

  Future<void> _loadDemoData() async {
    if (!hasAnalysisData) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Map area to industry for demo data
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
          industry = 'banking'; // fallback
      }

      final data = await DemoDataService.loadDemoData(industry);
      if (mounted) {
        setState(() {
          _brandData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
      print('Error loading demo data: $e');
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

    if (_brandData == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Analysis Header
          Text(
            'Brand Analysis Results',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Comparing ${widget.brandName} vs ${widget.competitor} in ${widget.selectedArea}',
            style: TextStyle(
              fontSize: 16,
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 32),

          // Charts Grid
          _buildChartsGrid(context),
        ],
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
              '📊',
              style: TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 16),
            Text(
              'Analysis Dashboard',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Interactive charts and brand comparison data will appear here after launching an analysis from the Setup tab.',
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
                '← Complete Setup First',
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

  Widget _buildLoadingState(BuildContext context) {
    return Center(
      child: GlassmorphismCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
            ),
            const SizedBox(height: 16),
            Text(
              'Loading Analysis Data...',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.glowBlue,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Fetching brand intelligence data and generating insights.',
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
              'Unable to Load Data',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'There was an error loading the analysis data. Please try again.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadDemoData,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartsGrid(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth > 1200;
        final isTablet = constraints.maxWidth > 768;

        if (isDesktop) {
          return Column(
            children: [
              Row(
                children: [
                  Expanded(child: _buildRadarChart()),
                  const SizedBox(width: 24),
                  Expanded(child: _buildDoughnutChart()),
                ],
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: _buildLineChart()),
                  const SizedBox(width: 24),
                  Expanded(child: _buildBarChart()),
                ],
              ),
            ],
          );
        } else if (isTablet) {
          return Column(
            children: [
              Row(
                children: [
                  Expanded(child: _buildRadarChart()),
                  const SizedBox(width: 16),
                  Expanded(child: _buildDoughnutChart()),
                ],
              ),
              const SizedBox(height: 16),
              _buildLineChart(),
              const SizedBox(height: 16),
              _buildBarChart(),
            ],
          );
        } else {
          return Column(
            children: [
              _buildRadarChart(),
              const SizedBox(height: 16),
              _buildDoughnutChart(),
              const SizedBox(height: 16),
              _buildLineChart(),
              const SizedBox(height: 16),
              _buildBarChart(),
            ],
          );
        }
      },
    );
  }

  Widget _buildRadarChart() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Brand Performance Radar',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          RadarChartWidget(
            chartData: DemoDataService.generateRadarChartData(_brandData!),
            height: 280,
          ),
        ],
      ),
    );
  }

  Widget _buildDoughnutChart() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Data Source Distribution',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          DoughnutChartWidget(
            chartData: DemoDataService.generateDoughnutChartData(_brandData!),
            height: 280,
          ),
        ],
      ),
    );
  }

  Widget _buildLineChart() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Sentiment Trends Over Time',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          LineChartWidget(
            chartData: DemoDataService.generateLineChartData(_brandData!),
            height: 280,
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Category Comparison',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          BarChartWidget(
            chartData: DemoDataService.generateBarChartData(_brandData!),
            height: 280,
          ),
        ],
      ),
    );
  }

}