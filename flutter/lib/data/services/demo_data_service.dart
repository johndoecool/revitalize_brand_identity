import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/chart_data.dart';

class CompleteBrandDataModel {
  final String demoId;
  final String name;
  final String description;
  final BrandModel brand;
  final BrandModel competitor;
  final AreaModel area;
  final BrandDataModel brandData;
  final BrandDataModel competitorData;

  CompleteBrandDataModel({
    required this.demoId,
    required this.name,
    required this.description,
    required this.brand,
    required this.competitor,
    required this.area,
    required this.brandData,
    required this.competitorData,
  });

  factory CompleteBrandDataModel.fromJson(Map<String, dynamic> json) {
    return CompleteBrandDataModel(
      demoId: json['demo_id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      brand: BrandModel.fromJson(json['brand'] ?? {}),
      competitor: BrandModel.fromJson(json['competitor'] ?? {}),
      area: AreaModel.fromJson(json['area'] ?? {}),
      brandData: BrandDataModel.fromJson(json['brand_data'] ?? {}),
      competitorData: BrandDataModel.fromJson(json['competitor_data'] ?? {}),
    );
  }
}

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
}

class AreaModel {
  final String id;
  final String name;
  final String description;

  AreaModel({
    required this.id,
    required this.name,
    required this.description,
  });

  factory AreaModel.fromJson(Map<String, dynamic> json) {
    return AreaModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
    );
  }
}

class BrandDataModel {
  final String brandId;
  final NewsSentimentModel newsSentiment;
  final SocialMediaModel socialMedia;
  final GlassdoorModel glassdoor;
  final WebsiteAnalysisModel websiteAnalysis;

  BrandDataModel({
    required this.brandId,
    required this.newsSentiment,
    required this.socialMedia,
    required this.glassdoor,
    required this.websiteAnalysis,
  });

  factory BrandDataModel.fromJson(Map<String, dynamic> json) {
    return BrandDataModel(
      brandId: json['brand_id'] ?? '',
      newsSentiment: NewsSentimentModel.fromJson(json['news_sentiment'] ?? {}),
      socialMedia: SocialMediaModel.fromJson(json['social_media'] ?? {}),
      glassdoor: GlassdoorModel.fromJson(json['glassdoor'] ?? {}),
      websiteAnalysis: WebsiteAnalysisModel.fromJson(json['website_analysis'] ?? {}),
    );
  }
}

class NewsSentimentModel {
  final double score;
  final int articlesCount;

  NewsSentimentModel({
    required this.score,
    required this.articlesCount,
  });

  factory NewsSentimentModel.fromJson(Map<String, dynamic> json) {
    return NewsSentimentModel(
      score: (json['score'] ?? 0.0).toDouble(),
      articlesCount: json['articles_count'] ?? 0,
    );
  }
}

class SocialMediaModel {
  final double overallSentiment;
  final int mentionsCount;

  SocialMediaModel({
    required this.overallSentiment,
    required this.mentionsCount,
  });

  factory SocialMediaModel.fromJson(Map<String, dynamic> json) {
    return SocialMediaModel(
      overallSentiment: (json['overall_sentiment'] ?? 0.0).toDouble(),
      mentionsCount: json['mentions_count'] ?? 0,
    );
  }
}

class GlassdoorModel {
  final double overallRating;
  final int reviewsCount;

  GlassdoorModel({
    required this.overallRating,
    required this.reviewsCount,
  });

  factory GlassdoorModel.fromJson(Map<String, dynamic> json) {
    return GlassdoorModel(
      overallRating: (json['overall_rating'] ?? 0.0).toDouble(),
      reviewsCount: json['reviews_count'] ?? 0,
    );
  }
}

class WebsiteAnalysisModel {
  final double userExperienceScore;
  final double featureCompleteness;
  final double securityScore;

  WebsiteAnalysisModel({
    required this.userExperienceScore,
    required this.featureCompleteness,
    required this.securityScore,
  });

  factory WebsiteAnalysisModel.fromJson(Map<String, dynamic> json) {
    return WebsiteAnalysisModel(
      userExperienceScore: (json['user_experience_score'] ?? 0.0).toDouble(),
      featureCompleteness: (json['feature_completeness'] ?? 0.0).toDouble(),
      securityScore: (json['security_score'] ?? 0.0).toDouble(),
    );
  }
}

class DemoDataService {
  static final Map<String, CompleteBrandDataModel> _cache = {};

  static Future<CompleteBrandDataModel?> loadDemoData(String industry) async {
    if (_cache.containsKey(industry)) {
      return _cache[industry];
    }

    try {
      String fileName;
      switch (industry.toLowerCase()) {
        case 'banking':
          fileName = 'assets/data/banking-demo.json';
          break;
        case 'technology':
          fileName = 'assets/data/tech-demo.json';
          break;
        case 'healthcare':
          fileName = 'assets/data/healthcare-demo.json';
          break;
        default:
          return null;
      }

      final String jsonString = await rootBundle.loadString(fileName);
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      
      final brandData = CompleteBrandDataModel.fromJson(jsonData);
      _cache[industry] = brandData;
      
      return brandData;
    } catch (e) {
      return null;
    }
  }

  static RadarChartData generateRadarChartData(CompleteBrandDataModel brandData) {
    final brand = brandData.brand;
    final competitor = brandData.competitor;
    final brandAnalysis = brandData.brandData;
    final competitorAnalysis = brandData.competitorData;

    // Convert website analysis scores to radar chart values (0-100 scale)
    final brandValues = [
      brandAnalysis.websiteAnalysis.userExperienceScore * 100,
      brandAnalysis.newsSentiment.score * 100,
      brandAnalysis.websiteAnalysis.featureCompleteness * 100,
      brandAnalysis.websiteAnalysis.securityScore * 100,
      brandAnalysis.socialMedia.overallSentiment * 100,
      brandAnalysis.glassdoor.overallRating * 20, // Convert 5-star to 100 scale
    ];

    final competitorValues = [
      competitorAnalysis.websiteAnalysis.userExperienceScore * 100,
      competitorAnalysis.newsSentiment.score * 100,
      competitorAnalysis.websiteAnalysis.featureCompleteness * 100,
      competitorAnalysis.websiteAnalysis.securityScore * 100,
      competitorAnalysis.socialMedia.overallSentiment * 100,
      competitorAnalysis.glassdoor.overallRating * 20,
    ];

    return RadarChartData(
      labels: ['UX Score', 'News Sentiment', 'Features', 'Security', 'Social Media', 'Employee Rating'],
      dataPoints: [
        RadarDataPoint(
          brand: brand.name,
          values: brandValues,
          color: 0xFF4ecdc4,
        ),
        RadarDataPoint(
          brand: competitor.name,
          values: competitorValues,
          color: 0xFFff6b6b,
        ),
      ],
    );
  }

  static DoughnutChartData generateDoughnutChartData(CompleteBrandDataModel brandData) {
    final brandAnalysis = brandData.brandData;
    
    // Calculate distribution based on social media platforms and other sources
    final socialMediaTotal = brandAnalysis.socialMedia.mentionsCount;
    final newsArticles = brandAnalysis.newsSentiment.articlesCount;
    final glassdoorReviews = brandAnalysis.glassdoor.reviewsCount;
    
    final total = socialMediaTotal + newsArticles + glassdoorReviews;
    
    return DoughnutChartData(
      segments: [
        DoughnutSegment(
          label: 'Social Media', 
          value: (socialMediaTotal / total * 100).round().toDouble(), 
          color: 0xFF4ecdc4
        ),
        DoughnutSegment(
          label: 'News Articles', 
          value: (newsArticles / total * 100).round().toDouble(), 
          color: 0xFFff6b6b
        ),
        DoughnutSegment(
          label: 'Employee Reviews', 
          value: (glassdoorReviews / total * 100).round().toDouble(), 
          color: 0xFF45b7d1
        ),
      ],
    );
  }

  static LineChartData generateLineChartData(CompleteBrandDataModel brandData) {
    final brand = brandData.brand;
    final competitor = brandData.competitor;
    
    // Generate trend data based on sentiment scores with some variation
    final brandSentiment = brandData.brandData.socialMedia.overallSentiment;
    final competitorSentiment = brandData.competitorData.socialMedia.overallSentiment;
    
    // Generate 6 months of data with slight variations
    final brandValues = List.generate(6, (index) {
      final variation = (index * 0.02) - 0.06; // Small trend variation
      return ((brandSentiment + variation) * 100).clamp(0, 100).toDouble();
    });
    
    final competitorValues = List.generate(6, (index) {
      final variation = (index * 0.015) - 0.045; // Different trend
      return ((competitorSentiment + variation) * 100).clamp(0, 100).toDouble();
    });

    return LineChartData(
      xLabels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      series: [
        LineDataSeries(
          brand: brand.name,
          values: brandValues,
          color: 0xFF4ecdc4,
        ),
        LineDataSeries(
          brand: competitor.name,
          values: competitorValues,
          color: 0xFFff6b6b,
        ),
      ],
    );
  }

  static BarChartData generateBarChartData(CompleteBrandDataModel brandData) {
    final brand = brandData.brand;
    final competitor = brandData.competitor;
    final brandAnalysis = brandData.brandData;
    final competitorAnalysis = brandData.competitorData;

    // Use website analysis metrics for comparison
    final brandValues = [
      brandAnalysis.websiteAnalysis.userExperienceScore * 100,
      brandAnalysis.glassdoor.overallRating * 20,
      brandAnalysis.websiteAnalysis.securityScore * 100,
      brandAnalysis.socialMedia.overallSentiment * 100,
    ];

    final competitorValues = [
      competitorAnalysis.websiteAnalysis.userExperienceScore * 100,
      competitorAnalysis.glassdoor.overallRating * 20,
      competitorAnalysis.websiteAnalysis.securityScore * 100,
      competitorAnalysis.socialMedia.overallSentiment * 100,
    ];

    return BarChartData(
      categories: ['User Experience', 'Employee Rating', 'Security', 'Social Sentiment'],
      series: [
        BarDataSeries(
          brand: brand.name,
          values: brandValues,
          color: 0xFF4ecdc4,
        ),
        BarDataSeries(
          brand: competitor.name,
          values: competitorValues,
          color: 0xFFff6b6b,
        ),
      ],
    );
  }

  static void clearCache() {
    _cache.clear();
  }
}