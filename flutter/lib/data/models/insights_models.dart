import '../services/demo_data_service.dart';

// Analysis Results Models for Insights
class AnalysisResults {
  final OverallComparison overallComparison;
  final Map<String, DetailedComparison> detailedComparison;
  final List<ActionableInsight> actionableInsights;
  final List<StrengthToMaintain> strengthsToMaintain;
  final MarketPositioning marketPositioning;

  AnalysisResults({
    required this.overallComparison,
    required this.detailedComparison,
    required this.actionableInsights,
    required this.strengthsToMaintain,
    required this.marketPositioning,
  });

  factory AnalysisResults.fromJson(Map<String, dynamic> json) {
    final detailedComparisonJson = json['detailed_comparison'] as Map<String, dynamic>? ?? {};
    final detailedComparison = <String, DetailedComparison>{};
    
    detailedComparisonJson.forEach((key, value) {
      detailedComparison[key] = DetailedComparison.fromJson(value);
    });

    return AnalysisResults(
      overallComparison: OverallComparison.fromJson(json['overall_comparison'] ?? {}),
      detailedComparison: detailedComparison,
      actionableInsights: (json['actionable_insights'] as List<dynamic>?)
          ?.map((insight) => ActionableInsight.fromJson(insight))
          .toList() ?? [],
      strengthsToMaintain: (json['strengths_to_maintain'] as List<dynamic>?)
          ?.map((strength) => StrengthToMaintain.fromJson(strength))
          .toList() ?? [],
      marketPositioning: MarketPositioning.fromJson(json['market_positioning'] ?? {}),
    );
  }
}

class OverallComparison {
  final double brandScore;
  final double competitorScore;
  final double gap;
  final String brandRanking;
  final double confidenceLevel;

  OverallComparison({
    required this.brandScore,
    required this.competitorScore,
    required this.gap,
    required this.brandRanking,
    required this.confidenceLevel,
  });

  factory OverallComparison.fromJson(Map<String, dynamic> json) {
    return OverallComparison(
      brandScore: (json['brand_score'] ?? 0.0).toDouble(),
      competitorScore: (json['competitor_score'] ?? 0.0).toDouble(),
      gap: (json['gap'] ?? 0.0).toDouble(),
      brandRanking: json['brand_ranking'] ?? '',
      confidenceLevel: (json['confidence_level'] ?? 0.0).toDouble(),
    );
  }
}

class DetailedComparison {
  final double brandScore;
  final double competitorScore;
  final double difference;
  final String insight;
  final String trend;

  DetailedComparison({
    required this.brandScore,
    required this.competitorScore,
    required this.difference,
    required this.insight,
    required this.trend,
  });

  factory DetailedComparison.fromJson(Map<String, dynamic> json) {
    return DetailedComparison(
      brandScore: (json['brand_score'] ?? 0.0).toDouble(),
      competitorScore: (json['competitor_score'] ?? 0.0).toDouble(),
      difference: (json['difference'] ?? 0.0).toDouble(),
      insight: json['insight'] ?? '',
      trend: json['trend'] ?? '',
    );
  }
}

class ActionableInsight {
  final InsightPriority priority;
  final String category;
  final String title;
  final String description;
  final String estimatedEffort;
  final String expectedImpact;
  final String roiEstimate;
  final List<String> implementationSteps;
  final List<String> successMetrics;

  ActionableInsight({
    required this.priority,
    required this.category,
    required this.title,
    required this.description,
    required this.estimatedEffort,
    required this.expectedImpact,
    required this.roiEstimate,
    required this.implementationSteps,
    required this.successMetrics,
  });

  factory ActionableInsight.fromJson(Map<String, dynamic> json) {
    return ActionableInsight(
      priority: InsightPriority.fromString(json['priority'] ?? 'low'),
      category: json['category'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      estimatedEffort: json['estimated_effort'] ?? '',
      expectedImpact: json['expected_impact'] ?? '',
      roiEstimate: json['roi_estimate'] ?? '',
      implementationSteps: List<String>.from(json['implementation_steps'] ?? []),
      successMetrics: List<String>.from(json['success_metrics'] ?? []),
    );
  }

  // Extract quarters needed from estimated effort
  int get quartersNeeded {
    final effort = estimatedEffort.toLowerCase();
    if (effort.contains('12-18') || effort.contains('18') || effort.contains('year')) {
      return 6; // 18 months = 6 quarters
    } else if (effort.contains('8-12') || effort.contains('12')) {
      return 4; // 12 months = 4 quarters
    } else if (effort.contains('6-9') || effort.contains('9')) {
      return 3; // 9 months = 3 quarters
    } else if (effort.contains('4-6') || effort.contains('6')) {
      return 2; // 6 months = 2 quarters
    } else {
      return 1; // Default to 1 quarter for shorter efforts
    }
  }

  // Get numerical ROI value for sorting
  double get roiValue {
    final roi = roiEstimate.toLowerCase();
    final match = RegExp(r'[\d.]+').firstMatch(roi);
    if (match != null) {
      return double.tryParse(match.group(0)!) ?? 0.0;
    }
    return 0.0;
  }
}

enum InsightPriority {
  high,
  medium,
  low;

  factory InsightPriority.fromString(String priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return InsightPriority.high;
      case 'medium':
        return InsightPriority.medium;
      case 'low':
        return InsightPriority.low;
      default:
        return InsightPriority.low;
    }
  }

  String get displayName {
    switch (this) {
      case InsightPriority.high:
        return 'High Priority';
      case InsightPriority.medium:
        return 'Medium Priority';
      case InsightPriority.low:
        return 'Low Priority';
    }
  }

  // Priority-based gradient colors
  List<int> get gradientColors {
    switch (this) {
      case InsightPriority.high:
        return [0xFFff6b6b, 0xFFff9500]; // Red to orange gradient
      case InsightPriority.medium:
        return [0xFFfeca57, 0xFFff6348]; // Yellow to amber gradient
      case InsightPriority.low:
        return [0xFF4ecdc4, 0xFF44a08d]; // Blue to cyan gradient
    }
  }

  int get glowColor {
    switch (this) {
      case InsightPriority.high:
        return 0xFFff6b6b;
      case InsightPriority.medium:
        return 0xFFfeca57;
      case InsightPriority.low:
        return 0xFF4ecdc4;
    }
  }
}

class StrengthToMaintain {
  final String area;
  final String description;
  final String recommendation;
  final double currentScore;

  StrengthToMaintain({
    required this.area,
    required this.description,
    required this.recommendation,
    required this.currentScore,
  });

  factory StrengthToMaintain.fromJson(Map<String, dynamic> json) {
    return StrengthToMaintain(
      area: json['area'] ?? '',
      description: json['description'] ?? '',
      recommendation: json['recommendation'] ?? '',
      currentScore: (json['current_score'] ?? 0.0).toDouble(),
    );
  }
}

class MarketPositioning {
  final String brandPosition;
  final String competitorPosition;
  final String differentiationOpportunity;
  final String targetAudience;

  MarketPositioning({
    required this.brandPosition,
    required this.competitorPosition,
    required this.differentiationOpportunity,
    required this.targetAudience,
  });

  factory MarketPositioning.fromJson(Map<String, dynamic> json) {
    return MarketPositioning(
      brandPosition: json['brand_position'] ?? '',
      competitorPosition: json['competitor_position'] ?? '',
      differentiationOpportunity: json['differentiation_opportunity'] ?? '',
      targetAudience: json['target_audience'] ?? '',
    );
  }
}

// Roadmap Models
class RoadmapTimeline {
  final List<RoadmapQuarter> quarters;
  final String brandName;
  final String competitorName;

  RoadmapTimeline({
    required this.quarters,
    required this.brandName,
    required this.competitorName,
  });
}

// Enhanced roadmap timeline with full API data
class EnhancedRoadmapTimeline extends RoadmapTimeline {
  final String roadmapId;
  final String competitorAnalysisSummary;
  final String strategicVision;
  final String marketOpportunity;
  final List<String> competitiveAdvantages;
  final String totalEstimatedBudget;
  final List<String> riskFactors;
  final double confidenceScore;
  final String generatedAt;

  EnhancedRoadmapTimeline({
    required super.quarters,
    required super.brandName,
    required super.competitorName,
    required this.roadmapId,
    required this.competitorAnalysisSummary,
    required this.strategicVision,
    required this.marketOpportunity,
    required this.competitiveAdvantages,
    required this.totalEstimatedBudget,
    required this.riskFactors,
    required this.confidenceScore,
    required this.generatedAt,
  });
}

class RoadmapQuarter {
  final String quarter;
  final String year;
  final List<RoadmapItem> items;
  final double progressPercentage;
  final String? quarterTheme;
  final List<String>? strategicGoals;
  final String? quarterBudget;
  final List<String>? successCriteria;

  RoadmapQuarter({
    required this.quarter,
    required this.year,
    required this.items,
    this.progressPercentage = 0.0,
    this.quarterTheme,
    this.strategicGoals,
    this.quarterBudget,
    this.successCriteria,
  });

  String get displayName => '$quarter $year';
}

class RoadmapItem {
  final String title;
  final String description;
  final InsightPriority priority;
  final List<String> tasks;
  final String expectedImpact;
  final bool isCompleted;
  final String? actionId;
  final String? category;
  final String? estimatedEffort;
  final String? budgetEstimate;
  final List<String>? successMetrics;
  final List<String>? dependencies;

  RoadmapItem({
    required this.title,
    required this.description,
    required this.priority,
    required this.tasks,
    required this.expectedImpact,
    this.isCompleted = false,
    this.actionId,
    this.category,
    this.estimatedEffort,
    this.budgetEstimate,
    this.successMetrics,
    this.dependencies,
  });
}

// Enhanced Analysis Models for New API Data
class CompetitorAnalysis {
  final String competitorName;
  final double comparisonScore;
  final List<String> strengths;
  final List<String> weaknesses;
  final List<String> opportunities;
  final List<String> keyDifferences;

  CompetitorAnalysis({
    required this.competitorName,
    required this.comparisonScore,
    required this.strengths,
    required this.weaknesses,
    required this.opportunities,
    required this.keyDifferences,
  });

  factory CompetitorAnalysis.fromJson(Map<String, dynamic> json) {
    return CompetitorAnalysis(
      competitorName: json['competitor_name'] ?? '',
      comparisonScore: (json['comparison_score'] ?? 0.0).toDouble(),
      strengths: List<String>.from(json['strengths'] ?? []),
      weaknesses: List<String>.from(json['weaknesses'] ?? []),
      opportunities: List<String>.from(json['opportunities'] ?? []),
      keyDifferences: List<String>.from(json['key_differences'] ?? []),
    );
  }
}

class ImprovementArea {
  final String area;
  final double currentScore;
  final double targetScore;
  final String priority;
  final String description;
  final List<String> actionItems;
  final List<String> expectedOutcomes;
  final String timeline;
  final List<String> resourcesNeeded;

  ImprovementArea({
    required this.area,
    required this.currentScore,
    required this.targetScore,
    required this.priority,
    required this.description,
    required this.actionItems,
    required this.expectedOutcomes,
    required this.timeline,
    required this.resourcesNeeded,
  });

  factory ImprovementArea.fromJson(Map<String, dynamic> json) {
    return ImprovementArea(
      area: json['area'] ?? '',
      currentScore: (json['current_score'] ?? 0.0).toDouble(),
      targetScore: (json['target_score'] ?? 0.0).toDouble(),
      priority: json['priority'] ?? 'medium',
      description: json['description'] ?? '',
      actionItems: List<String>.from(json['action_items'] ?? []),
      expectedOutcomes: List<String>.from(json['expected_outcomes'] ?? []),
      timeline: json['timeline'] ?? '',
      resourcesNeeded: List<String>.from(json['resources_needed'] ?? []),
    );
  }

  // Calculate improvement gap percentage
  double get improvementGap => targetScore - currentScore;
  
  // Calculate progress percentage (current score as percentage of target)
  double get progressPercentage => targetScore > 0 ? (currentScore / targetScore).clamp(0.0, 1.0) : 0.0;
  
  // Get priority level for UI styling
  InsightPriority get priorityLevel {
    switch (priority.toLowerCase()) {
      case 'high':
        return InsightPriority.high;
      case 'medium':
        return InsightPriority.medium;
      case 'low':
        return InsightPriority.low;
      default:
        return InsightPriority.medium;
    }
  }
}

// Enhanced Analysis Results with new data
class EnhancedAnalysisResults {
  final AnalysisResults baseResults;
  final List<CompetitorAnalysis> competitorAnalyses;
  final List<ImprovementArea> improvementAreas;

  EnhancedAnalysisResults({
    required this.baseResults,
    required this.competitorAnalyses,
    required this.improvementAreas,
  });

  // Convenience getters to access base results
  OverallComparison get overallComparison => baseResults.overallComparison;
  Map<String, DetailedComparison> get detailedComparison => baseResults.detailedComparison;
  List<ActionableInsight> get actionableInsights => baseResults.actionableInsights;
  List<StrengthToMaintain> get strengthsToMaintain => baseResults.strengthsToMaintain;
  MarketPositioning get marketPositioning => baseResults.marketPositioning;

  // Check if enhanced data is available
  bool get hasCompetitorAnalysis => competitorAnalyses.isNotEmpty;
  bool get hasImprovementAreas => improvementAreas.isNotEmpty;
  bool get hasEnhancedData => hasCompetitorAnalysis || hasImprovementAreas;
}