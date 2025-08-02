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
         oldWidget.competitor != widget.competitor ||
         oldWidget.analysisResult != widget.analysisResult)) {
      _loadData();
    }
  }

  @override
  void initState() {
    super.initState();
    if (hasAnalysisData) {
      _loadData();
    }
  }

  /// Load data from real analysis result or fallback to demo data
  Future<void> _loadData() async {
    if (!hasAnalysisData) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Check if we have real analysis result first
      if (widget.analysisResult != null) {
        print('[AnalysisTab] Using real analysis result data');
        print('[AnalysisTab] Analysis result contains: ${widget.analysisResult!.data.keys}');
        
        // Check if charts exist in the analysis result
        final charts = widget.analysisResult!.data['charts'];
        if (charts != null) {
          print('[AnalysisTab] Found ${(charts as List).length} charts in analysis result');
        } else {
          print('[AnalysisTab] No charts found in analysis result data');
          print('[AnalysisTab] Available keys in analysis result: ${widget.analysisResult!.data.keys}');
        }
        
        // We have real data, no need to load anything else
        // The charts will automatically use real data via _getRadarChartData()
        if (mounted) {
          setState(() {
            _isLoading = false;
            // Don't set _brandData since we're using real data
          });
        }
        return;
      }

      // Fallback to demo data if no real analysis result
      print('[AnalysisTab] No real analysis result, loading demo data');
      await _loadDemoData();
      
    } catch (e) {
      print('[AnalysisTab] Error loading data: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
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

    // Check if we have either real analysis result or demo data
    if (_brandData == null && widget.analysisResult == null) {
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
            chartData: _getRadarChartData(),
            height: 280,
          ),
        ],
      ),
    );
  }

  /// Get radar chart data from real analysis or fallback to demo data
  RadarChartData _getRadarChartData() {
    // Try to get real data from analysis result first
    if (widget.analysisResult != null) {
      print('[RadarChart] Attempting to extract radar data from analysis result');
      final realRadarData = _extractRadarChartFromAnalysis(widget.analysisResult!);
      if (realRadarData != null) {
        print('[RadarChart] Successfully using real radar data');
        return realRadarData;
      } else {
        print('[RadarChart] Failed to extract real radar data, using demo data');
      }
    } else {
      print('[RadarChart] No analysis result available, using demo data');
    }
    
    // Fallback to demo data if no real data available
    if (_brandData != null) {
      try {
        final demoData = DemoDataService.generateRadarChartData(_brandData!);
        print('[RadarChart] Successfully generated demo radar data with ${demoData.labels.length} labels');
        return demoData;
      } catch (e) {
        print('[RadarChart] Error generating demo radar data: $e');
      }
    }
    
    // Return safe fallback data if nothing available - with exactly 3 points as required by fl_chart
    print('[RadarChart] Using fallback radar data with minimum 3 points');
    return RadarChartData(
      dataPoints: [
        RadarDataPoint(
          brand: widget.brandName ?? 'Brand',
          values: [60.0, 55.0, 70.0],
          color: 0xFF4ecdc4,
        ),
        RadarDataPoint(
          brand: widget.competitor ?? 'Competitor',
          values: [65.0, 60.0, 75.0],
          color: 0xFFff6b6b,
        ),
      ],
      labels: ['Performance', 'Quality', 'Innovation'],
    );
  }

  /// Extract radar chart data from analysis result
  RadarChartData? _extractRadarChartFromAnalysis(AnalysisResult analysisResult) {
    try {
      // The analysis result contains the data from /api/v1/analyze/{analysis_id}/status
      // Charts are at the root level of the API response, stored in analysisResult.data
      final charts = analysisResult.data['charts'] as List<dynamic>?;
      if (charts == null) {
        print('[RadarChart] No charts found in analysis result data');
        return null;
      }

      // Find the radar chart
      Map<String, dynamic>? radarChart;
      for (final chart in charts) {
        if (chart is Map<String, dynamic> && chart['chart_type'] == 'radar') {
          radarChart = chart;
          break;
        }
      }

      if (radarChart == null) return null;

      // Extract chart data
      final chartData = radarChart['data'] as Map<String, dynamic>?;
      if (chartData == null) return null;

      final labels = (chartData['labels'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList();
      final datasets = chartData['datasets'] as List<dynamic>?;

      if (labels == null || datasets == null) return null;

      // fl_chart radar chart requires at least 3 data points
      if (labels.length < 3) {
        print('[RadarChart] Radar chart needs at least 3 data points, got ${labels.length}. Falling back to demo data.');
        return null;
      }

      // Convert datasets to RadarDataPoint objects
      final dataPoints = <RadarDataPoint>[];
      for (final dataset in datasets) {
        if (dataset is Map<String, dynamic>) {
          final brandName = dataset['label']?.toString() ?? 'Unknown';
          final values = (dataset['data'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList();
          
          // Validate that values length matches labels length
          if (values == null || values.length != labels.length) {
            print('[RadarChart] Values length (${values?.length}) does not match labels length (${labels.length})');
            continue;
          }
          
          // Convert hex color to int (fallback to blue if parsing fails)
          int color = 0xFF3B82F6; // Default blue
          final borderColor = dataset['borderColor']?.toString();
          if (borderColor != null && borderColor.startsWith('#')) {
            try {
              color = int.parse('0xFF${borderColor.substring(1)}');
            } catch (e) {
              print('[RadarChart] Failed to parse color: $borderColor, using default');
            }
          }

          dataPoints.add(RadarDataPoint(
            brand: brandName,
            values: values,
            color: color,
          ));
        }
      }

      if (dataPoints.isNotEmpty) {
        print('[RadarChart] Successfully extracted real radar data with ${dataPoints.length} datasets');
        return RadarChartData(
          dataPoints: dataPoints,
          labels: labels,
        );
      }

    } catch (e) {
      print('[RadarChart] Error extracting radar chart data: $e');
    }

    return null;
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
            chartData: _getDoughnutChartData(),
            height: 280,
          ),
        ],
      ),
    );
  }

  /// Get doughnut chart data from real analysis or fallback to demo data
  DoughnutChartData _getDoughnutChartData() {
    // Try to get real data from analysis result first
    if (widget.analysisResult != null) {
      final realDoughnutData = _extractDoughnutChartFromAnalysis(widget.analysisResult!);
      if (realDoughnutData != null) {
        return realDoughnutData;
      }
    }
    
    // Fallback to demo data if no real data available or _brandData is null
    if (_brandData != null) {
      return DemoDataService.generateDoughnutChartData(_brandData!);
    }
    
    // Return empty data if nothing available
    return DoughnutChartData(segments: []);
  }

  /// Extract doughnut chart data from analysis result
  DoughnutChartData? _extractDoughnutChartFromAnalysis(AnalysisResult analysisResult) {
    try {
      final charts = analysisResult.data['charts'] as List<dynamic>?;
      if (charts == null) return null;

      // Find the doughnut/pie chart
      Map<String, dynamic>? doughnutChart;
      for (final chart in charts) {
        if (chart is Map<String, dynamic> && 
            (chart['chart_type'] == 'doughnut' || chart['chart_type'] == 'pie')) {
          doughnutChart = chart;
          break;
        }
      }

      if (doughnutChart == null) return null;

      final chartData = doughnutChart['data'] as Map<String, dynamic>?;
      if (chartData == null) return null;

      final labels = (chartData['labels'] as List<dynamic>?)?.map((e) => e.toString()).toList();
      final datasets = chartData['datasets'] as List<dynamic>?;

      if (labels == null || datasets == null || datasets.isEmpty) return null;

      // Use first dataset for doughnut chart
      final dataset = datasets[0] as Map<String, dynamic>?;
      if (dataset == null) return null;

      final values = (dataset['data'] as List<dynamic>?)?.map((e) => (e as num).toDouble()).toList();
      final colors = (dataset['backgroundColor'] as List<dynamic>?)?.map((e) => e.toString()).toList();

      if (values == null || labels.length != values.length) return null;

      final segments = <DoughnutSegment>[];

      for (int i = 0; i < labels.length; i++) {
        final value = values[i];
        
        // Convert color or use default
        int color = 0xFF3B82F6; // Default blue
        if (colors != null && i < colors.length) {
          final colorStr = colors[i];
          if (colorStr.startsWith('#')) {
            try {
              color = int.parse('0xFF${colorStr.substring(1)}');
            } catch (e) {
              // Use default color if parsing fails
            }
          }
        }

        segments.add(DoughnutSegment(
          label: labels[i],
          value: value,
          color: color,
        ));
      }

      if (segments.isNotEmpty) {
        print('[DoughnutChart] Successfully extracted real doughnut data with ${segments.length} segments');
        return DoughnutChartData(segments: segments);
      }

    } catch (e) {
      print('[DoughnutChart] Error extracting doughnut chart data: $e');
    }

    return null;
  }

  /// Extract line chart data from analysis result
  LineChartData? _extractLineChartFromAnalysis(AnalysisResult analysisResult) {
    try {
      final charts = analysisResult.data['charts'] as List<dynamic>?;
      if (charts == null) return null;

      // Find the line chart
      Map<String, dynamic>? lineChart;
      for (final chart in charts) {
        if (chart is Map<String, dynamic> && chart['chart_type'] == 'line') {
          lineChart = chart;
          break;
        }
      }

      if (lineChart == null) return null;

      final chartData = lineChart['data'] as Map<String, dynamic>?;
      if (chartData == null) return null;

      final labels = (chartData['labels'] as List<dynamic>?)?.map((e) => e.toString()).toList();
      final datasets = chartData['datasets'] as List<dynamic>?;

      if (labels == null || datasets == null) return null;

      final series = <LineDataSeries>[];
      for (final dataset in datasets) {
        if (dataset is Map<String, dynamic>) {
          final brandName = dataset['label']?.toString() ?? 'Unknown';
          final values = (dataset['data'] as List<dynamic>?)?.map((e) => (e as num).toDouble()).toList();
          
          // Convert color
          int color = 0xFF3B82F6;
          final borderColor = dataset['borderColor']?.toString();
          if (borderColor != null && borderColor.startsWith('#')) {
            try {
              color = int.parse('0xFF${borderColor.substring(1)}');
            } catch (e) {
              // Use default color
            }
          }

          if (values != null) {
            series.add(LineDataSeries(
              brand: brandName,
              values: values,
              color: color,
            ));
          }
        }
      }

      if (series.isNotEmpty) {
        print('[LineChart] Successfully extracted real line data with ${series.length} series');
        return LineChartData(series: series, xLabels: labels);
      }

    } catch (e) {
      print('[LineChart] Error extracting line chart data: $e');
    }

    return null;
  }

  /// Get line chart data from real analysis or fallback to demo data
  LineChartData _getLineChartData() {
    // Try to extract real line chart data first
    if (widget.analysisResult != null) {
      final realLineData = _extractLineChartFromAnalysis(widget.analysisResult!);
      if (realLineData != null) {
        print('[LineChart] Using real line chart data');
        return realLineData;
      }
    }
    
    // Fallback to demo data 
    if (_brandData != null) {
      print('[LineChart] Using demo line chart data');
      return DemoDataService.generateLineChartData(_brandData!);
    }
    
    // Return basic fallback if no data available
    print('[LineChart] Using fallback line chart data');
    return LineChartData(
      series: [
        LineDataSeries(
          brand: widget.brandName ?? 'Brand',
          values: [60, 65, 70, 72, 75, 78],
          color: 0xFF4ecdc4,
        ),
        LineDataSeries(
          brand: widget.competitor ?? 'Competitor', 
          values: [65, 68, 71, 73, 76, 80],
          color: 0xFFff6b6b,
        ),
      ],
      xLabels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    );
  }

  /// Get bar chart data from real analysis or fallback to demo data  
  BarChartData _getBarChartData() {
    // Try to extract real bar chart data first
    if (widget.analysisResult != null) {
      final realBarData = _extractBarChartFromAnalysis(widget.analysisResult!);
      if (realBarData != null) {
        print('[BarChart] Using real bar chart data');
        return realBarData;
      }
    }
    
    // Fallback to demo data
    if (_brandData != null) {
      print('[BarChart] Using demo bar chart data');
      return DemoDataService.generateBarChartData(_brandData!);
    }
    
    // Return basic fallback if no data available
    print('[BarChart] Using fallback bar chart data');
    return BarChartData(
      categories: ['Performance', 'Quality', 'Innovation', 'Customer Satisfaction'],
      series: [
        BarDataSeries(
          brand: widget.brandName ?? 'Brand',
          values: [75, 68, 82, 70],
          color: 0xFF4ecdc4,
        ),
        BarDataSeries(
          brand: widget.competitor ?? 'Competitor',
          values: [80, 72, 85, 78],
          color: 0xFFff6b6b,
        ),
      ],
    );
  }

  /// Extract bar chart data from analysis result
  BarChartData? _extractBarChartFromAnalysis(AnalysisResult analysisResult) {
    try {
      final charts = analysisResult.data['charts'] as List<dynamic>?;
      if (charts == null) return null;

      // Find the bar chart
      Map<String, dynamic>? barChart;
      for (final chart in charts) {
        if (chart is Map<String, dynamic> && chart['chart_type'] == 'bar') {
          barChart = chart;
          break;
        }
      }

      if (barChart == null) return null;

      final chartData = barChart['data'] as Map<String, dynamic>?;
      if (chartData == null) return null;

      final labels = (chartData['labels'] as List<dynamic>?)?.map((e) => e.toString()).toList();
      final datasets = chartData['datasets'] as List<dynamic>?;

      if (labels == null || datasets == null) return null;

      final series = <BarDataSeries>[];
      for (final dataset in datasets) {
        if (dataset is Map<String, dynamic>) {
          final brandName = dataset['label']?.toString() ?? 'Unknown';
          final values = (dataset['data'] as List<dynamic>?)?.map((e) => (e as num).toDouble()).toList();
          
          // Convert color or use default
          int color = 0xFF3B82F6;
          final backgroundColor = dataset['backgroundColor'];
          if (backgroundColor is List && backgroundColor.isNotEmpty) {
            final colorStr = backgroundColor[0].toString();
            if (colorStr.startsWith('#')) {
              try {
                color = int.parse('0xFF${colorStr.substring(1)}');
              } catch (e) {
                // Use default color
              }
            }
          }

          if (values != null) {
            series.add(BarDataSeries(
              brand: brandName,
              values: values,
              color: color,
            ));
          }
        }
      }

      if (series.isNotEmpty) {
        print('[BarChart] Successfully extracted real bar data with ${series.length} series');
        return BarChartData(categories: labels, series: series);
      }

    } catch (e) {
      print('[BarChart] Error extracting bar chart data: $e');
    }

    return null;
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
            chartData: _getLineChartData(),
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
            chartData: _getBarChartData(),
            height: 280,
          ),
        ],
      ),
    );
  }

}