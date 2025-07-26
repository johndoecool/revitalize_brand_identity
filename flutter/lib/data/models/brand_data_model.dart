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

  Map<String, dynamic> toJson() {
    return {
      'brand_id': brandId,
      'news_sentiment': newsSentiment.toJson(),
      'social_media': socialMedia.toJson(),
      'glassdoor': glassdoor.toJson(),
      'website_analysis': websiteAnalysis.toJson(),
    };
  }
}

class NewsSentimentModel {
  final double score;
  final int articlesCount;
  final int positiveArticles;
  final int negativeArticles;
  final int neutralArticles;
  final List<NewsArticleModel> recentArticles;

  NewsSentimentModel({
    required this.score,
    required this.articlesCount,
    required this.positiveArticles,
    required this.negativeArticles,
    required this.neutralArticles,
    required this.recentArticles,
  });

  factory NewsSentimentModel.fromJson(Map<String, dynamic> json) {
    return NewsSentimentModel(
      score: (json['score'] ?? 0.0).toDouble(),
      articlesCount: json['articles_count'] ?? 0,
      positiveArticles: json['positive_articles'] ?? 0,
      negativeArticles: json['negative_articles'] ?? 0,
      neutralArticles: json['neutral_articles'] ?? 0,
      recentArticles: (json['recent_articles'] as List<dynamic>?)
          ?.map((article) => NewsArticleModel.fromJson(article))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'articles_count': articlesCount,
      'positive_articles': positiveArticles,
      'negative_articles': negativeArticles,
      'neutral_articles': neutralArticles,
      'recent_articles': recentArticles.map((article) => article.toJson()).toList(),
    };
  }
}

class NewsArticleModel {
  final String title;
  final String sentiment;
  final String publishedDate;
  final String source;

  NewsArticleModel({
    required this.title,
    required this.sentiment,
    required this.publishedDate,
    required this.source,
  });

  factory NewsArticleModel.fromJson(Map<String, dynamic> json) {
    return NewsArticleModel(
      title: json['title'] ?? '',
      sentiment: json['sentiment'] ?? '',
      publishedDate: json['published_date'] ?? '',
      source: json['source'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'sentiment': sentiment,
      'published_date': publishedDate,
      'source': source,
    };
  }
}

class SocialMediaModel {
  final double overallSentiment;
  final int mentionsCount;
  final double engagementRate;
  final Map<String, SocialPlatformModel> platforms;
  final List<String> trendingTopics;

  SocialMediaModel({
    required this.overallSentiment,
    required this.mentionsCount,
    required this.engagementRate,
    required this.platforms,
    required this.trendingTopics,
  });

  factory SocialMediaModel.fromJson(Map<String, dynamic> json) {
    final platformsJson = json['platforms'] as Map<String, dynamic>? ?? {};
    final platforms = <String, SocialPlatformModel>{};
    
    platformsJson.forEach((key, value) {
      platforms[key] = SocialPlatformModel.fromJson(value);
    });

    return SocialMediaModel(
      overallSentiment: (json['overall_sentiment'] ?? 0.0).toDouble(),
      mentionsCount: json['mentions_count'] ?? 0,
      engagementRate: (json['engagement_rate'] ?? 0.0).toDouble(),
      platforms: platforms,
      trendingTopics: List<String>.from(json['trending_topics'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    final platformsJson = <String, dynamic>{};
    platforms.forEach((key, value) {
      platformsJson[key] = value.toJson();
    });

    return {
      'overall_sentiment': overallSentiment,
      'mentions_count': mentionsCount,
      'engagement_rate': engagementRate,
      'platforms': platformsJson,
      'trending_topics': trendingTopics,
    };
  }
}

class SocialPlatformModel {
  final double sentiment;
  final int mentions;
  final List<String> trendingTopics;

  SocialPlatformModel({
    required this.sentiment,
    required this.mentions,
    required this.trendingTopics,
  });

  factory SocialPlatformModel.fromJson(Map<String, dynamic> json) {
    return SocialPlatformModel(
      sentiment: (json['sentiment'] ?? 0.0).toDouble(),
      mentions: json['mentions'] ?? 0,
      trendingTopics: List<String>.from(json['trending_topics'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'sentiment': sentiment,
      'mentions': mentions,
      'trending_topics': trendingTopics,
    };
  }
}

class GlassdoorModel {
  final double overallRating;
  final int reviewsCount;
  final List<String> pros;
  final List<String> cons;
  final double recommendationRate;
  final double ceoApproval;
  final List<GlassdoorReviewModel> recentReviews;

  GlassdoorModel({
    required this.overallRating,
    required this.reviewsCount,
    required this.pros,
    required this.cons,
    required this.recommendationRate,
    required this.ceoApproval,
    required this.recentReviews,
  });

  factory GlassdoorModel.fromJson(Map<String, dynamic> json) {
    return GlassdoorModel(
      overallRating: (json['overall_rating'] ?? 0.0).toDouble(),
      reviewsCount: json['reviews_count'] ?? 0,
      pros: List<String>.from(json['pros'] ?? []),
      cons: List<String>.from(json['cons'] ?? []),
      recommendationRate: (json['recommendation_rate'] ?? 0.0).toDouble(),
      ceoApproval: (json['ceo_approval'] ?? 0.0).toDouble(),
      recentReviews: (json['recent_reviews'] as List<dynamic>?)
          ?.map((review) => GlassdoorReviewModel.fromJson(review))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'overall_rating': overallRating,
      'reviews_count': reviewsCount,
      'pros': pros,
      'cons': cons,
      'recommendation_rate': recommendationRate,
      'ceo_approval': ceoApproval,
      'recent_reviews': recentReviews.map((review) => review.toJson()).toList(),
    };
  }
}

class GlassdoorReviewModel {
  final int rating;
  final String pros;
  final String cons;
  final String date;

  GlassdoorReviewModel({
    required this.rating,
    required this.pros,
    required this.cons,
    required this.date,
  });

  factory GlassdoorReviewModel.fromJson(Map<String, dynamic> json) {
    return GlassdoorReviewModel(
      rating: json['rating'] ?? 0,
      pros: json['pros'] ?? '',
      cons: json['cons'] ?? '',
      date: json['date'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'rating': rating,
      'pros': pros,
      'cons': cons,
      'date': date,
    };
  }
}

class WebsiteAnalysisModel {
  final double userExperienceScore;
  final double featureCompleteness;
  final double securityScore;
  final double accessibilityScore;
  final double mobileFriendliness;
  final double loadTime;
  final List<String> features;
  final List<String> missingFeatures;

  WebsiteAnalysisModel({
    required this.userExperienceScore,
    required this.featureCompleteness,
    required this.securityScore,
    required this.accessibilityScore,
    required this.mobileFriendliness,
    required this.loadTime,
    required this.features,
    required this.missingFeatures,
  });

  factory WebsiteAnalysisModel.fromJson(Map<String, dynamic> json) {
    return WebsiteAnalysisModel(
      userExperienceScore: (json['user_experience_score'] ?? 0.0).toDouble(),
      featureCompleteness: (json['feature_completeness'] ?? 0.0).toDouble(),
      securityScore: (json['security_score'] ?? 0.0).toDouble(),
      accessibilityScore: (json['accessibility_score'] ?? 0.0).toDouble(),
      mobileFriendliness: (json['mobile_friendliness'] ?? 0.0).toDouble(),
      loadTime: (json['load_time'] ?? 0.0).toDouble(),
      features: List<String>.from(json['features'] ?? []),
      missingFeatures: List<String>.from(json['missing_features'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_experience_score': userExperienceScore,
      'feature_completeness': featureCompleteness,
      'security_score': securityScore,
      'accessibility_score': accessibilityScore,
      'mobile_friendliness': mobileFriendliness,
      'load_time': loadTime,
      'features': features,
      'missing_features': missingFeatures,
    };
  }
}