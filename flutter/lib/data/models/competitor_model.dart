class CompetitorModel {
  final String id;
  final String name;
  final String logoUrl;
  final String industry;
  final double relevanceScore;
  final String competitionLevel;
  final String symbol;

  CompetitorModel({
    required this.id,
    required this.name,
    required this.logoUrl,
    required this.industry,
    this.relevanceScore = 0.0,
    this.competitionLevel = 'indirect',
    this.symbol = '',
  });

  factory CompetitorModel.fromJson(Map<String, dynamic> json) {
    return CompetitorModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      logoUrl: json['logo_url'] ?? '',
      industry: json['industry'] ?? '',
      relevanceScore: (json['relevance_score'] ?? 0.0).toDouble(),
      competitionLevel: json['competition_level'] ?? 'indirect',
      symbol: json['symbol'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'logo_url': logoUrl,
      'industry': industry,
      'relevance_score': relevanceScore,
      'competition_level': competitionLevel,
      'symbol': symbol,
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

  /// Check if this is a direct competitor
  bool get isDirectCompetitor => competitionLevel.toLowerCase() == 'direct';

  @override
  String toString() {
    return 'CompetitorModel(id: $id, name: $name, relevance: ${relevancePercentage}%, level: $competitionLevel)';
  }
}