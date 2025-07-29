class BrandModel {
  final String id;
  final String name;
  final String fullName;
  final String industry;
  final String logoUrl;
  final String description;
  final String website;
  final double confidenceScore;

  BrandModel({
    required this.id,
    required this.name,
    required this.fullName,
    required this.industry,
    required this.logoUrl,
    required this.description,
    this.website = '',
    this.confidenceScore = 0.0,
  });

  factory BrandModel.fromJson(Map<String, dynamic> json) {
    return BrandModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      fullName: json['full_name'] ?? '',
      industry: json['industry'] ?? '',
      logoUrl: json['logo_url'] ?? '',
      description: json['description'] ?? '',
      website: json['website'] ?? '',
      confidenceScore: (json['confidence_score'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'full_name': fullName,
      'industry': industry,
      'logo_url': logoUrl,
      'description': description,
      'website': website,
      'confidence_score': confidenceScore,
    };
  }

  /// Get confidence percentage as integer (0-100)
  int get confidencePercentage => (confidenceScore * 100).round();

  /// Get confidence color based on score
  /// Green for high (80%+), Yellow for medium (60%+), Red for low
  String get confidenceLevel {
    if (confidenceScore >= 0.8) return 'high';
    if (confidenceScore >= 0.6) return 'medium';
    return 'low';
  }

  @override
  String toString() {
    return 'BrandModel(id: $id, name: $name, industry: $industry, confidence: ${confidencePercentage}%)';
  }
}