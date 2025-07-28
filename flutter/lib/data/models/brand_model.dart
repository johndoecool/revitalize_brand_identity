class BrandModel {
  final String id;
  final String name;
  final String fullName;
  final String industry;
  final String logoUrl;
  final String description;
  final String website;

  BrandModel({
    required this.id,
    required this.name,
    required this.fullName,
    required this.industry,
    required this.logoUrl,
    required this.description,
    required this.website,
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
    };
  }

  @override
  String toString() {
    return 'BrandModel(id: $id, name: $name, industry: $industry)';
  }
}