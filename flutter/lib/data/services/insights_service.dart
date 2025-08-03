import '../models/insights_models.dart';
import 'demo_data_service.dart';

// Abstract service interface for future API integration
abstract class InsightsService {
  Future<AnalysisResults?> getAnalysisResults(String industry);
  Future<RoadmapTimeline> generateRoadmap(AnalysisResults analysisResults, String brandName, String competitorName);
}

// Demo implementation using JSON data
class DemoInsightsService implements InsightsService {
  static final DemoInsightsService _instance = DemoInsightsService._internal();
  factory DemoInsightsService() => _instance;
  DemoInsightsService._internal();

  @override
  Future<AnalysisResults?> getAnalysisResults(String industry) async {
    try {
      final demoData = await DemoDataService.loadDemoData(industry);
      if (demoData == null) return null;

      // Extract analysis results from the complete demo data
      final analysisResultsJson = {
        'overall_comparison': {
          'brand_score': 0.76,
          'competitor_score': 0.84,
          'gap': -0.08,
          'brand_ranking': 'second',
          'confidence_level': 0.92,
        },
        'detailed_comparison': _buildDetailedComparison(demoData),
        'actionable_insights': _extractActionableInsights(demoData),
        'strengths_to_maintain': _extractStrengthsToMaintain(demoData),
        'market_positioning': _extractMarketPositioning(demoData),
      };

      return AnalysisResults.fromJson(analysisResultsJson);
    } catch (e) {
      return null;
    }
  }

  Map<String, dynamic> _buildDetailedComparison(CompleteBrandDataModel demoData) {
    final brand = demoData.brandData;
    final competitor = demoData.competitorData;

    return {
      'user_experience': {
        'brand_score': brand.websiteAnalysis.userExperienceScore,
        'competitor_score': competitor.websiteAnalysis.userExperienceScore,
        'difference': brand.websiteAnalysis.userExperienceScore - competitor.websiteAnalysis.userExperienceScore,
        'insight': '${demoData.competitor.name} has superior user interface design with modern UI/UX patterns',
        'trend': 'improving',
      },
      'feature_completeness': {
        'brand_score': brand.websiteAnalysis.featureCompleteness,
        'competitor_score': competitor.websiteAnalysis.featureCompleteness,
        'difference': brand.websiteAnalysis.featureCompleteness - competitor.websiteAnalysis.featureCompleteness,
        'insight': '${demoData.brand.name} lacks advanced features compared to ${demoData.competitor.name}',
        'trend': 'stable',
      },
      'security': {
        'brand_score': brand.websiteAnalysis.securityScore,
        'competitor_score': competitor.websiteAnalysis.securityScore,
        'difference': brand.websiteAnalysis.securityScore - competitor.websiteAnalysis.securityScore,
        'insight': 'Both brands have strong security measures with slight edge to ${demoData.competitor.name}',
        'trend': 'improving',
      },
      'social_sentiment': {
        'brand_score': brand.socialMedia.overallSentiment,
        'competitor_score': competitor.socialMedia.overallSentiment,
        'difference': brand.socialMedia.overallSentiment - competitor.socialMedia.overallSentiment,
        'insight': '${demoData.competitor.name} has better social media presence and engagement',
        'trend': 'stable',
      },
    };
  }

  List<Map<String, dynamic>> _extractActionableInsights(CompleteBrandDataModel demoData) {
    // For demo purposes, return industry-specific insights
    switch (demoData.area.id) {
      case 'self_service_portal':
        return _getBankingInsights();
      case 'employer_branding':
        return _getTechnologyInsights();
      case 'product_innovation':
        return _getHealthcareInsights();
      default:
        return _getBankingInsights();
    }
  }

  List<Map<String, dynamic>> _getBankingInsights() {
    return [
      {
        'priority': 'high',
        'category': 'feature_development',
        'title': 'Implement Advanced Mobile Banking Features',
        'description': 'Develop mobile app features like biometric authentication, real-time notifications, and AI-powered financial insights',
        'estimated_effort': '3-4 months',
        'expected_impact': 'Increase user experience score by 0.15',
        'roi_estimate': '\$2.5M annually',
        'implementation_steps': [
          'Conduct user research for mobile banking needs',
          'Design mobile-first user interface with modern patterns',
          'Implement biometric authentication (fingerprint, face ID)',
          'Add real-time transaction notifications',
          'Integrate AI-powered spending insights',
          'Implement push notifications for security alerts',
        ],
        'success_metrics': [
          'Mobile app adoption rate',
          'User engagement time',
          'Feature usage statistics',
        ],
      },
      {
        'priority': 'medium',
        'category': 'user_experience',
        'title': 'Improve Website Navigation and Performance',
        'description': 'Redesign website navigation for better user flow and optimize performance',
        'estimated_effort': '2-3 months',
        'expected_impact': 'Increase user experience score by 0.08',
        'roi_estimate': '\$1.2M annually',
        'implementation_steps': [
          'Analyze user journey patterns and pain points',
          'Redesign navigation structure with clear hierarchy',
          'Implement A/B testing for new designs',
          'Optimize for mobile responsiveness',
          'Improve page load times',
          'Add progressive web app features',
        ],
        'success_metrics': [
          'Page load time',
          'User session duration',
          'Bounce rate reduction',
        ],
      },
      {
        'priority': 'low',
        'category': 'security',
        'title': 'Enhanced Security Measures',
        'description': 'Implement advanced security features to build customer trust',
        'estimated_effort': '4-6 months',
        'expected_impact': 'Increase security score by 0.05',
        'roi_estimate': '\$800K annually',
        'implementation_steps': [
          'Implement multi-factor authentication',
          'Add fraud detection systems',
          'Enhance encryption protocols',
          'Conduct security audits',
          'Improve customer security education',
        ],
        'success_metrics': [
          'Security incident reduction',
          'Customer trust scores',
          'Compliance ratings',
        ],
      },
    ];
  }

  List<Map<String, dynamic>> _getTechnologyInsights() {
    return [
      {
        'priority': 'high',
        'category': 'employee_benefits',
        'title': 'Enhance Employee Benefits and Perks',
        'description': 'Develop innovative benefits packages to compete with top tech companies',
        'estimated_effort': '4-6 months',
        'expected_impact': 'Increase employee satisfaction score by 0.12',
        'roi_estimate': '\$3.2M annually (reduced turnover)',
        'implementation_steps': [
          'Conduct employee benefits survey',
          'Research innovative tech company perks',
          'Design new benefits package',
          'Implement flexible work arrangements',
          'Add wellness and mental health programs',
          'Create career development initiatives',
        ],
        'success_metrics': [
          'Employee satisfaction scores',
          'Retention rates',
          'Benefits utilization rates',
        ],
      },
      {
        'priority': 'medium',
        'category': 'workplace_culture',
        'title': 'Strengthen Innovation Culture',
        'description': 'Enhance innovation-focused workplace culture to attract top tech talent',
        'estimated_effort': '6-8 months',
        'expected_impact': 'Increase employer brand score by 0.08',
        'roi_estimate': '\$2.1M annually',
        'implementation_steps': [
          'Launch innovation labs and hackathons',
          'Implement 20% time for personal projects',
          'Create innovation recognition programs',
          'Enhance technology showcase events',
          'Develop innovation-focused training programs',
        ],
        'success_metrics': [
          'Innovation project participation',
          'Patent applications',
          'Employee engagement scores',
        ],
      },
      {
        'priority': 'low',
        'category': 'recruitment',
        'title': 'Improve Recruitment Marketing',
        'description': 'Enhance recruitment marketing to better showcase unique advantages',
        'estimated_effort': '3-4 months',
        'expected_impact': 'Increase candidate quality by 15%',
        'roi_estimate': '\$1.8M annually (better hires)',
        'implementation_steps': [
          'Develop compelling employer brand messaging',
          'Create employee testimonial videos',
          'Enhance careers website experience',
          'Implement targeted recruitment campaigns',
          'Build university partnerships',
        ],
        'success_metrics': [
          'Candidate quality scores',
          'Time to hire',
          'Offer acceptance rates',
        ],
      },
    ];
  }

  List<Map<String, dynamic>> _getHealthcareInsights() {
    return [
      {
        'priority': 'high',
        'category': 'technology_investment',
        'title': 'Accelerate mRNA Technology Development',
        'description': 'Invest heavily in mRNA technology to compete with innovative platforms',
        'estimated_effort': '12-18 months',
        'expected_impact': 'Increase innovation capability score by 0.15',
        'roi_estimate': '\$5.2M annually (new product revenue)',
        'implementation_steps': [
          'Establish dedicated mRNA research division',
          'Hire top mRNA technology experts',
          'Invest in mRNA manufacturing capabilities',
          'Develop mRNA technology partnerships',
          'Create mRNA innovation labs',
          'Accelerate mRNA clinical trials',
        ],
        'success_metrics': [
          'mRNA patent applications',
          'mRNA clinical trial progress',
          'mRNA technology partnerships',
        ],
      },
      {
        'priority': 'medium',
        'category': 'research_efficiency',
        'title': 'Streamline R&D Processes',
        'description': 'Improve research efficiency and reduce time-to-market for new products',
        'estimated_effort': '8-12 months',
        'expected_impact': 'Reduce development time by 25%',
        'roi_estimate': '\$3.8M annually',
        'implementation_steps': [
          'Implement agile development methodologies',
          'Enhance cross-functional collaboration',
          'Invest in automation and AI tools',
          'Streamline regulatory processes',
          'Improve clinical trial design',
          'Optimize manufacturing processes',
        ],
        'success_metrics': [
          'Time to market reduction',
          'Clinical trial efficiency',
          'R&D productivity metrics',
        ],
      },
      {
        'priority': 'low',
        'category': 'partnership_strategy',
        'title': 'Strengthen Innovation Partnerships',
        'description': 'Develop strategic partnerships with biotech startups and research institutions',
        'estimated_effort': '6-9 months',
        'expected_impact': 'Access to 15+ new technology platforms',
        'roi_estimate': '\$2.4M annually',
        'implementation_steps': [
          'Establish innovation partnership program',
          'Create startup incubation initiatives',
          'Develop university research partnerships',
          'Invest in biotech venture fund',
          'Create open innovation platform',
          'Establish technology licensing program',
        ],
        'success_metrics': [
          'Number of active partnerships',
          'Technology platforms accessed',
          'Innovation pipeline value',
        ],
      },
    ];
  }

  List<Map<String, dynamic>> _extractStrengthsToMaintain(CompleteBrandDataModel demoData) {
    return [
      {
        'area': 'security',
        'description': 'Strong security measures are competitive advantage',
        'recommendation': 'Continue investing in security infrastructure and staff training',
        'current_score': demoData.brandData.websiteAnalysis.securityScore,
      },
      {
        'area': 'customer_service',
        'description': 'High customer satisfaction in traditional services',
        'recommendation': 'Leverage existing customer relationships for digital transformation',
        'current_score': 0.83,
      },
    ];
  }

  Map<String, dynamic> _extractMarketPositioning(CompleteBrandDataModel demoData) {
    return {
      'brand_position': 'Reliable traditional provider with strong security',
      'competitor_position': 'Innovative digital leader with modern features',
      'differentiation_opportunity': 'Focus on personalized service and security excellence',
      'target_audience': 'Customers who value security and reliability',
    };
  }

  @override
  Future<RoadmapTimeline> generateRoadmap(AnalysisResults analysisResults, String brandName, String competitorName) async {
    final quarters = <RoadmapQuarter>[];
    final currentYear = DateTime.now().year;
    final currentQuarter = ((DateTime.now().month - 1) ~/ 3) + 1;

    // Sort insights by priority and ROI
    final sortedInsights = List<ActionableInsight>.from(analysisResults.actionableInsights);
    sortedInsights.sort((a, b) {
      // First sort by priority
      final priorityComparison = a.priority.index.compareTo(b.priority.index);
      if (priorityComparison != 0) return priorityComparison;
      
      // Then by ROI (descending)
      return b.roiValue.compareTo(a.roiValue);
    });

    // Create quarters for the next 2 years (8 quarters)
    var quarterNum = currentQuarter;
    var year = currentYear;
    
    for (int i = 0; i < 8; i++) {
      final quarterName = 'Q$quarterNum';
      final yearStr = year.toString();
      
      quarters.add(RoadmapQuarter(
        quarter: quarterName,
        year: yearStr,
        items: [],
        progressPercentage: 0.0,
      ));
      
      quarterNum++;
      if (quarterNum > 4) {
        quarterNum = 1;
        year++;
      }
    }

    // Distribute insights across quarters based on priority and effort
    int currentQuarterIndex = 0;
    
    for (final insight in sortedInsights) {
      final quartersNeeded = insight.quartersNeeded;
      
      // Find the best starting quarter based on priority
      int startQuarter = currentQuarterIndex;
      if (insight.priority == InsightPriority.high) {
        // High priority items start earlier
        startQuarter = currentQuarterIndex;
      } else if (insight.priority == InsightPriority.medium) {
        // Medium priority items can start a bit later
        startQuarter = (currentQuarterIndex + 1).clamp(0, quarters.length - quartersNeeded);
      } else {
        // Low priority items start later
        startQuarter = (currentQuarterIndex + 2).clamp(0, quarters.length - quartersNeeded);
      }

      // Add the insight to the appropriate quarters
      for (int q = startQuarter; q < startQuarter + quartersNeeded && q < quarters.length; q++) {
        final quarterProgress = (q - startQuarter + 1) / quartersNeeded;
        final isFirst = q == startQuarter;
        
        quarters[q].items.add(RoadmapItem(
          title: isFirst ? insight.title : '${insight.title} (continued)',
          description: isFirst ? insight.description : 'Continue implementation of ${insight.title.toLowerCase()}',
          priority: insight.priority,
          tasks: isFirst ? insight.implementationSteps : ['Continue previous quarter tasks'],
          expectedImpact: insight.expectedImpact,
          isCompleted: false,
        ));
      }
      
      // Update current quarter index for next insight (allow parallel execution)
      if (insight.priority == InsightPriority.high) {
        currentQuarterIndex = (currentQuarterIndex + 1).clamp(0, quarters.length - 1);
      }
    }

    return RoadmapTimeline(
      quarters: quarters,
      brandName: brandName,
      competitorName: competitorName,
    );
  }
}

// Future API implementation
class ApiInsightsService implements InsightsService {
  @override
  Future<AnalysisResults?> getAnalysisResults(String industry) async {
    // TODO: Implement actual API calls
    // The API should return the same JSON structure as our demo data
    throw UnimplementedError('API service not yet implemented');
  }

  @override
  Future<RoadmapTimeline> generateRoadmap(AnalysisResults analysisResults, String brandName, String competitorName) async {
    // TODO: Implement API-based roadmap generation
    throw UnimplementedError('API service not yet implemented');
  }
}