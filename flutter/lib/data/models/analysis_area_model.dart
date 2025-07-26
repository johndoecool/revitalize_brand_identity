class AnalysisAreaModel {
  final String id;
  final String name;
  final String description;

  AnalysisAreaModel({
    required this.id,
    required this.name,
    required this.description,
  });

  factory AnalysisAreaModel.fromJson(Map<String, dynamic> json) {
    return AnalysisAreaModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
    };
  }

  @override
  String toString() {
    return 'AnalysisAreaModel(id: $id, name: $name)';
  }
}