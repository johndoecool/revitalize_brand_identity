import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import '../models/insights_models.dart';
import '../models/chart_data.dart';

class PdfService {
  static final PdfService _instance = PdfService._internal();
  factory PdfService() => _instance;
  PdfService._internal();

  // Generate comprehensive PDF report
  Future<Uint8List> generateComprehensiveReport({
    required String brandName,
    required String competitorName,
    required String analysisArea,
    required AnalysisResults analysisResults,
    required RoadmapTimeline roadmapTimeline,
    List<Uint8List>? chartImages,
  }) async {
    final pdf = pw.Document();
    
    // Load fonts for better typography
    final fontRegular = await _loadFont('fonts/Inter-Regular.ttf');
    final fontBold = await _loadFont('fonts/Inter-Bold.ttf');
    
    final theme = pw.ThemeData.withFont(
      base: fontRegular,
      bold: fontBold,
    );

    // Cover Page
    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildCoverPage(
          brandName,
          competitorName,
          analysisArea,
        ),
      ),
    );

    // Executive Summary
    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildExecutiveSummary(
          brandName,
          competitorName,
          analysisResults,
        ),
      ),
    );

    // Charts Section
    if (chartImages != null && chartImages.isNotEmpty) {
      pdf.addPage(
        pw.Page(
          pageFormat: PdfPageFormat.a4,
          theme: theme,
          build: (pw.Context context) => _buildChartsSection(chartImages),
        ),
      );
    }

    // Insights Section
    for (int i = 0; i < analysisResults.actionableInsights.length; i += 2) {
      pdf.addPage(
        pw.Page(
          pageFormat: PdfPageFormat.a4,
          theme: theme,
          build: (pw.Context context) => _buildInsightsSection(
            analysisResults.actionableInsights.skip(i).take(2).toList(),
            i + 1,
          ),
        ),
      );
    }

    // Roadmap Section
    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildRoadmapSection(roadmapTimeline),
      ),
    );

    // Appendix
    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildAppendix(analysisResults),
      ),
    );

    return pdf.save();
  }

  // Generate executive summary PDF
  Future<Uint8List> generateExecutiveSummary({
    required String brandName,
    required String competitorName,
    required String analysisArea,
    required AnalysisResults analysisResults,
  }) async {
    final pdf = pw.Document();
    
    final fontRegular = await _loadFont('fonts/Inter-Regular.ttf');
    final fontBold = await _loadFont('fonts/Inter-Bold.ttf');
    
    final theme = pw.ThemeData.withFont(
      base: fontRegular,
      bold: fontBold,
    );

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildCoverPage(
          brandName,
          competitorName,
          analysisArea,
        ),
      ),
    );

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        theme: theme,
        build: (pw.Context context) => _buildExecutiveSummary(
          brandName,
          competitorName,
          analysisResults,
        ),
      ),
    );

    return pdf.save();
  }

  // Generate data export JSON
  Map<String, dynamic> generateDataExport({
    required String brandName,
    required String competitorName,
    required String analysisArea,
    required AnalysisResults analysisResults,
    required RoadmapTimeline roadmapTimeline,
  }) {
    return {
      'export_metadata': {
        'generated_at': DateTime.now().toIso8601String(),
        'brand_name': brandName,
        'competitor_name': competitorName,
        'analysis_area': analysisArea,
        'version': '1.0.0',
      },
      'overall_comparison': {
        'brand_score': analysisResults.overallComparison.brandScore,
        'competitor_score': analysisResults.overallComparison.competitorScore,
        'gap': analysisResults.overallComparison.gap,
        'confidence_level': analysisResults.overallComparison.confidenceLevel,
      },
      'detailed_metrics': analysisResults.detailedComparison.map((key, value) => MapEntry(key, {
        'brand_score': value.brandScore,
        'competitor_score': value.competitorScore,
        'difference': value.difference,
        'insight': value.insight,
        'trend': value.trend,
      })),
      'actionable_insights': analysisResults.actionableInsights.map((insight) => {
        'priority': insight.priority.name,
        'category': insight.category,
        'title': insight.title,
        'description': insight.description,
        'estimated_effort': insight.estimatedEffort,
        'expected_impact': insight.expectedImpact,
        'roi_estimate': insight.roiEstimate,
        'implementation_steps': insight.implementationSteps,
        'success_metrics': insight.successMetrics,
      }).toList(),
      'roadmap_timeline': {
        'brand_name': roadmapTimeline.brandName,
        'competitor_name': roadmapTimeline.competitorName,
        'quarters': roadmapTimeline.quarters.map((quarter) => {
          'quarter': quarter.quarter,
          'year': quarter.year,
          'progress_percentage': quarter.progressPercentage,
          'items': quarter.items.map((item) => {
            'title': item.title,
            'description': item.description,
            'priority': item.priority.name,
            'tasks': item.tasks,
            'expected_impact': item.expectedImpact,
            'is_completed': item.isCompleted,
          }).toList(),
        }).toList(),
      },
      'strengths_to_maintain': analysisResults.strengthsToMaintain.map((strength) => {
        'area': strength.area,
        'description': strength.description,
        'recommendation': strength.recommendation,
        'current_score': strength.currentScore,
      }).toList(),
      'market_positioning': {
        'brand_position': analysisResults.marketPositioning.brandPosition,
        'competitor_position': analysisResults.marketPositioning.competitorPosition,
        'differentiation_opportunity': analysisResults.marketPositioning.differentiationOpportunity,
        'target_audience': analysisResults.marketPositioning.targetAudience,
      },
    };
  }

  // Helper method to load fonts
  Future<pw.Font> _loadFont(String fontPath) async {
    try {
      final fontData = await rootBundle.load('assets/$fontPath');
      return pw.Font.ttf(fontData);
    } catch (e) {
      // Fallback to default font if custom font fails
      return pw.Font.helvetica();
    }
  }

  // Build cover page
  pw.Widget _buildCoverPage(String brandName, String competitorName, String analysisArea) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Spacer(flex: 2),
        
        // Main title
        pw.Text(
          'Brand Intelligence Report',
          style: pw.TextStyle(
            fontSize: 32,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Subtitle
        pw.Text(
          'Comprehensive Analysis & Strategic Recommendations',
          style: pw.TextStyle(
            fontSize: 18,
            color: PdfColors.grey600,
          ),
        ),
        pw.SizedBox(height: 40),
        
        // Analysis details
        pw.Container(
          padding: const pw.EdgeInsets.all(20),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.grey300),
            borderRadius: pw.BorderRadius.circular(8),
          ),
          child: pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              _buildInfoRow('Brand Analyzed:', brandName),
              pw.SizedBox(height: 10),
              _buildInfoRow('Competitor:', competitorName),
              pw.SizedBox(height: 10),
              _buildInfoRow('Analysis Area:', analysisArea),
              pw.SizedBox(height: 10),
              _buildInfoRow('Generated:', _formatDate(DateTime.now())),
            ],
          ),
        ),
        
        pw.Spacer(flex: 3),
        
        // Footer
        pw.Row(
          mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
          children: [
            pw.Text(
              'Brand Intelligence Hub',
              style: pw.TextStyle(
                fontSize: 14,
                color: PdfColors.grey600,
              ),
            ),
            pw.Text(
              'VibeCoding Hackathon 2025',
              style: pw.TextStyle(
                fontSize: 14,
                color: PdfColors.grey600,
              ),
            ),
          ],
        ),
      ],
    );
  }

  // Build executive summary
  pw.Widget _buildExecutiveSummary(String brandName, String competitorName, AnalysisResults results) {
    final overall = results.overallComparison;
    
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Executive Summary',
          style: pw.TextStyle(
            fontSize: 24,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Overall scores
        pw.Container(
          padding: const pw.EdgeInsets.all(16),
          decoration: pw.BoxDecoration(
            color: PdfColors.grey100,
            borderRadius: pw.BorderRadius.circular(8),
          ),
          child: pw.Row(
            mainAxisAlignment: pw.MainAxisAlignment.spaceAround,
            children: [
              _buildScoreCard(brandName, overall.brandScore),
              _buildScoreCard(competitorName, overall.competitorScore),
            ],
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Key insights
        pw.Text(
          'Key Findings',
          style: pw.TextStyle(
            fontSize: 18,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 12),
        
        ...results.actionableInsights.take(3).map((insight) => pw.Container(
          margin: const pw.EdgeInsets.only(bottom: 12),
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.grey300),
            borderRadius: pw.BorderRadius.circular(6),
          ),
          child: pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    insight.title,
                    style: pw.TextStyle(
                      fontSize: 14,
                      fontWeight: pw.FontWeight.bold,
                    ),
                  ),
                  pw.Container(
                    padding: const pw.EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: pw.BoxDecoration(
                      color: _getPriorityColor(insight.priority),
                      borderRadius: pw.BorderRadius.circular(4),
                    ),
                    child: pw.Text(
                      insight.priority.displayName,
                      style: pw.TextStyle(
                        fontSize: 10,
                        color: PdfColors.white,
                        fontWeight: pw.FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              pw.SizedBox(height: 6),
              pw.Text(
                insight.description,
                style: pw.TextStyle(fontSize: 12, color: PdfColors.grey600),
              ),
              pw.SizedBox(height: 6),
              pw.Text(
                'ROI: ${insight.roiEstimate} | Timeline: ${insight.estimatedEffort}',
                style: pw.TextStyle(fontSize: 11, color: PdfColors.grey500),
              ),
            ],
          ),
        )).toList(),
        
        pw.Spacer(),
        
        // Confidence level
        pw.Text(
          'Analysis Confidence: ${(overall.confidenceLevel * 100).toInt()}%',
          style: pw.TextStyle(
            fontSize: 12,
            color: PdfColors.grey600,
          ),
        ),
      ],
    );
  }

  // Build charts section
  pw.Widget _buildChartsSection(List<Uint8List> chartImages) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Data Visualization',
          style: pw.TextStyle(
            fontSize: 24,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Display chart images in a grid
        pw.Wrap(
          spacing: 10,
          runSpacing: 10,
          children: chartImages.take(4).map((imageBytes) => 
            pw.Container(
              width: 250,
              height: 180,
              child: pw.Image(pw.MemoryImage(imageBytes)),
            ),
          ).toList(),
        ),
      ],
    );
  }

  // Build insights section
  pw.Widget _buildInsightsSection(List<ActionableInsight> insights, int startIndex) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Actionable Insights (${startIndex}-${startIndex + insights.length - 1})',
          style: pw.TextStyle(
            fontSize: 24,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        ...insights.map((insight) => pw.Container(
          margin: const pw.EdgeInsets.only(bottom: 20),
          padding: const pw.EdgeInsets.all(16),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.grey300),
            borderRadius: pw.BorderRadius.circular(8),
          ),
          child: pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              // Header
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    insight.title,
                    style: pw.TextStyle(
                      fontSize: 16,
                      fontWeight: pw.FontWeight.bold,
                    ),
                  ),
                  pw.Container(
                    padding: const pw.EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: pw.BoxDecoration(
                      color: _getPriorityColor(insight.priority),
                      borderRadius: pw.BorderRadius.circular(4),
                    ),
                    child: pw.Text(
                      insight.priority.displayName,
                      style: pw.TextStyle(
                        fontSize: 10,
                        color: PdfColors.white,
                        fontWeight: pw.FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              pw.SizedBox(height: 8),
              
              // Description
              pw.Text(
                insight.description,
                style: pw.TextStyle(fontSize: 12, color: PdfColors.grey600),
              ),
              pw.SizedBox(height: 12),
              
              // Metrics
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text('Timeline: ${insight.estimatedEffort}', style: pw.TextStyle(fontSize: 11)),
                  pw.Text('ROI: ${insight.roiEstimate}', style: pw.TextStyle(fontSize: 11)),
                  pw.Text('Impact: ${insight.expectedImpact}', style: pw.TextStyle(fontSize: 11)),
                ],
              ),
              pw.SizedBox(height: 12),
              
              // Implementation steps
              pw.Text(
                'Implementation Steps:',
                style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold),
              ),
              pw.SizedBox(height: 4),
              ...insight.implementationSteps.take(5).map((step) => pw.Padding(
                padding: const pw.EdgeInsets.only(left: 8, bottom: 2),
                child: pw.Text(
                  '• $step',
                  style: pw.TextStyle(fontSize: 10, color: PdfColors.grey600),
                ),
              )).toList(),
              if (insight.implementationSteps.length > 5)
                pw.Padding(
                  padding: const pw.EdgeInsets.only(left: 8),
                  child: pw.Text(
                    '+ ${insight.implementationSteps.length - 5} more steps',
                    style: pw.TextStyle(fontSize: 10, color: PdfColors.grey500),
                  ),
                ),
            ],
          ),
        )).toList(),
      ],
    );
  }

  // Build roadmap section
  pw.Widget _buildRoadmapSection(RoadmapTimeline timeline) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Implementation Roadmap',
          style: pw.TextStyle(
            fontSize: 24,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Timeline overview
        ...timeline.quarters.take(6).map((quarter) => pw.Container(
          margin: const pw.EdgeInsets.only(bottom: 16),
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(
            color: PdfColors.grey50,
            border: pw.Border.all(color: PdfColors.grey300),
            borderRadius: pw.BorderRadius.circular(6),
          ),
          child: pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    '${quarter.quarter} ${quarter.year}',
                    style: pw.TextStyle(
                      fontSize: 14,
                      fontWeight: pw.FontWeight.bold,
                    ),
                  ),
                  pw.Text(
                    '${quarter.items.length} initiative${quarter.items.length != 1 ? 's' : ''}',
                    style: pw.TextStyle(fontSize: 12, color: PdfColors.grey600),
                  ),
                ],
              ),
              if (quarter.items.isNotEmpty) ...[
                pw.SizedBox(height: 8),
                ...quarter.items.map((item) => pw.Padding(
                  padding: const pw.EdgeInsets.only(bottom: 4),
                  child: pw.Text(
                    '• ${item.title}',
                    style: pw.TextStyle(fontSize: 11, color: PdfColors.grey600),
                  ),
                )).toList(),
              ],
            ],
          ),
        )).toList(),
      ],
    );
  }

  // Build appendix
  pw.Widget _buildAppendix(AnalysisResults results) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Appendix',
          style: pw.TextStyle(
            fontSize: 24,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.grey800,
          ),
        ),
        pw.SizedBox(height: 20),
        
        // Detailed comparison
        pw.Text(
          'Detailed Metrics Comparison',
          style: pw.TextStyle(
            fontSize: 16,
            fontWeight: pw.FontWeight.bold,
          ),
        ),
        pw.SizedBox(height: 12),
        
        ...results.detailedComparison.entries.map((entry) => pw.Container(
          margin: const pw.EdgeInsets.only(bottom: 8),
          padding: const pw.EdgeInsets.all(8),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.grey300),
            borderRadius: pw.BorderRadius.circular(4),
          ),
          child: pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Text(
                entry.key.replaceAll('_', ' ').toUpperCase(),
                style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold),
              ),
              pw.SizedBox(height: 4),
              pw.Text(
                entry.value.insight,
                style: pw.TextStyle(fontSize: 10, color: PdfColors.grey600),
              ),
              pw.SizedBox(height: 4),
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    'Brand: ${(entry.value.brandScore * 100).toInt()}%',
                    style: pw.TextStyle(fontSize: 10),
                  ),
                  pw.Text(
                    'Competitor: ${(entry.value.competitorScore * 100).toInt()}%',
                    style: pw.TextStyle(fontSize: 10),
                  ),
                  pw.Text(
                    'Gap: ${(entry.value.difference * 100).toStringAsFixed(1)}%',
                    style: pw.TextStyle(fontSize: 10),
                  ),
                ],
              ),
            ],
          ),
        )).toList(),
        
        pw.Spacer(),
        
        // Generated timestamp
        pw.Text(
          'Report generated on ${_formatDate(DateTime.now())} by Brand Intelligence Hub',
          style: pw.TextStyle(fontSize: 10, color: PdfColors.grey500),
        ),
      ],
    );
  }

  // Helper methods
  pw.Widget _buildInfoRow(String label, String value) {
    return pw.Row(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.SizedBox(
          width: 120,
          child: pw.Text(
            label,
            style: pw.TextStyle(
              fontSize: 14,
              fontWeight: pw.FontWeight.bold,
              color: PdfColors.grey600,
            ),
          ),
        ),
        pw.Expanded(
          child: pw.Text(
            value,
            style: pw.TextStyle(
              fontSize: 14,
              color: PdfColors.grey800,
            ),
          ),
        ),
      ],
    );
  }

  pw.Widget _buildScoreCard(String name, double score) {
    return pw.Column(
      children: [
        pw.Text(
          name,
          style: pw.TextStyle(
            fontSize: 16,
            fontWeight: pw.FontWeight.bold,
          ),
          textAlign: pw.TextAlign.center,
        ),
        pw.SizedBox(height: 8),
        pw.Container(
          width: 60,
          height: 60,
          decoration: pw.BoxDecoration(
            shape: pw.BoxShape.circle,
            border: pw.Border.all(color: PdfColors.grey400, width: 2),
          ),
          child: pw.Center(
            child: pw.Text(
              '${(score * 100).toInt()}',
              style: pw.TextStyle(
                fontSize: 20,
                fontWeight: pw.FontWeight.bold,
                color: PdfColors.grey800,
              ),
            ),
          ),
        ),
        pw.SizedBox(height: 4),
        pw.Text(
          'Overall Score',
          style: pw.TextStyle(
            fontSize: 12,
            color: PdfColors.grey600,
          ),
        ),
      ],
    );
  }

  PdfColor _getPriorityColor(InsightPriority priority) {
    switch (priority) {
      case InsightPriority.high:
        return PdfColors.red400;
      case InsightPriority.medium:
        return PdfColors.orange400;
      case InsightPriority.low:
        return PdfColors.blue400;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}