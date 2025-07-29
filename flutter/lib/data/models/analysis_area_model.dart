class AnalysisAreaModel {
  final String id;
  final String name;
  final String description;
  final double relevanceScore;
  final List<String> metrics;

  AnalysisAreaModel({
    required this.id,
    required this.name,
    required this.description,
    this.relevanceScore = 0.0,
    this.metrics = const [],
  });

  factory AnalysisAreaModel.fromJson(Map<String, dynamic> json) {
    return AnalysisAreaModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      relevanceScore: (json['relevance_score'] ?? 0.0).toDouble(),
      metrics: (json['metrics'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'relevance_score': relevanceScore,
      'metrics': metrics,
    };
  }

  /// Get relevance percentage as integer (0-100)
  int get relevancePercentage => (relevanceScore * 100).round();

  /// Get relevance level for UI styling
  String get relevanceLevel {
    if (relevanceScore >= 0.8) return 'high';
    if (relevanceScore >= 0.6) return 'medium';
    return 'low';
  }

  @override
  String toString() {
    return 'AnalysisAreaModel(id: $id, name: $name, relevance: ${relevancePercentage}%)';
  }
}