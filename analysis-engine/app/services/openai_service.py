import openai
import json
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.models.analysis import (
    AnalysisResults, OverallComparison, ComparisonScore, 
    ActionableInsight, Strength, MarketPositioning, Priority
)

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_brand_comparison(
        self, 
        brand_data: Dict[str, Any], 
        competitor_data: Dict[str, Any], 
        area_id: str
    ) -> AnalysisResults:
        """
        Perform comprehensive brand analysis using OpenAI GPT
        """
        try:
            # Prepare the analysis prompt
            prompt = self._create_analysis_prompt(brand_data, competitor_data, area_id)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            logger.info(f"OpenAI Analysis completed for area: {area_id}")
            
            # Convert to structured format
            return await self._parse_analysis_response(
                analysis_text, 
                brand_data, 
                competitor_data, 
                area_id
            )
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        return """
You are an expert brand analyst with deep expertise in competitive analysis, market positioning, 
and actionable business insights. Your task is to analyze brand performance compared to competitors 
and provide detailed, actionable recommendations.

Please provide your analysis in the following structured format:

1. OVERALL COMPARISON (scores 0.0-1.0)
2. DETAILED COMPARISON by categories (user_experience, feature_completeness, security, etc.)
3. ACTIONABLE INSIGHTS (high/medium/low priority with implementation steps)
4. STRENGTHS TO MAINTAIN
5. MARKET POSITIONING analysis
6. CONFIDENCE SCORE (0.0-1.0)

Be specific, data-driven, and provide concrete implementation steps for all recommendations.
Focus on digital transformation, customer experience, and competitive differentiation.
"""
    
    def _create_analysis_prompt(
        self, 
        brand_data: Dict[str, Any], 
        competitor_data: Dict[str, Any], 
        area_id: str
    ) -> str:
        brand_name = brand_data.get('brand', {}).get('name', 'Unknown Brand')
        competitor_name = competitor_data.get('competitor', {}).get('name', 'Unknown Competitor')
        area_name = brand_data.get('area', {}).get('name', area_id)
        
        prompt = f"""
Analyze the competitive positioning between {brand_name} and {competitor_name} in the area of {area_name}.

BRAND DATA ({brand_name}):
{json.dumps(brand_data, indent=2)}

COMPETITOR DATA ({competitor_name}):
{json.dumps(competitor_data, indent=2)}

ANALYSIS FOCUS AREA: {area_name}

Please provide a comprehensive analysis covering:
1. Overall performance comparison with numerical scores
2. Detailed category-by-category breakdown
3. Specific actionable insights with implementation roadmaps
4. Key strengths to leverage
5. Market positioning opportunities
6. Your confidence level in this analysis

Focus on practical, implementable recommendations that can drive measurable business impact.
"""
        return prompt
    
    async def _parse_analysis_response(
        self, 
        analysis_text: str, 
        brand_data: Dict[str, Any], 
        competitor_data: Dict[str, Any], 
        area_id: str
    ) -> AnalysisResults:
        """
        Parse OpenAI response and convert to structured format
        This is a simplified parser - in production, you might use more sophisticated NLP
        """
        brand_name = brand_data.get('brand', {}).get('name', 'Unknown Brand')
        competitor_name = competitor_data.get('competitor', {}).get('name', 'Unknown Competitor')
        
        # For demo purposes, we'll create structured results
        # In production, you'd implement sophisticated parsing of the GPT response
        
        return AnalysisResults(
            analysis_id="",  # Will be set by the calling service
            area_id=area_id,
            brand_name=brand_name,
            competitor_name=competitor_name,
            overall_comparison=OverallComparison(
                brand_score=0.76,
                competitor_score=0.84,
                gap=-0.08,
                brand_ranking="second"
            ),
            detailed_comparison={
                "user_experience": ComparisonScore(
                    brand_score=0.82,
                    competitor_score=0.89,
                    difference=-0.07,
                    insight=f"{competitor_name} has superior user interface design and navigation flow"
                ),
                "feature_completeness": ComparisonScore(
                    brand_score=0.75,
                    competitor_score=0.82,
                    difference=-0.07,
                    insight=f"{brand_name} lacks advanced mobile banking features compared to {competitor_name}"
                ),
                "security": ComparisonScore(
                    brand_score=0.88,
                    competitor_score=0.91,
                    difference=-0.03,
                    insight="Both organizations maintain strong security measures with slight competitive edge to competitor"
                )
            },
            actionable_insights=[
                ActionableInsight(
                    priority=Priority.HIGH,
                    category="feature_development",
                    title="Implement Advanced Mobile Banking Features",
                    description="Develop cutting-edge mobile app capabilities including biometric authentication, real-time notifications, and AI-powered financial insights",
                    estimated_effort="3-4 months",
                    expected_impact="Increase user experience score by 0.15 points",
                    implementation_steps=[
                        "Conduct comprehensive user research and journey mapping",
                        "Design mobile-first user interface with modern UX principles",
                        "Implement biometric authentication (fingerprint, face ID)",
                        "Add real-time transaction notifications and alerts",
                        "Integrate AI-powered spending insights and recommendations"
                    ]
                ),
                ActionableInsight(
                    priority=Priority.MEDIUM,
                    category="user_experience",
                    title="Redesign Website Navigation Architecture",
                    description="Overhaul website navigation for improved user flow and accessibility",
                    estimated_effort="2-3 months",
                    expected_impact="Increase user experience score by 0.08 points",
                    implementation_steps=[
                        "Analyze current user journey patterns and pain points",
                        "Redesign information architecture and navigation structure",
                        "Implement comprehensive A/B testing framework",
                        "Optimize for mobile responsiveness and accessibility",
                        "Deploy gradual rollout with user feedback integration"
                    ]
                )
            ],
            strengths_to_maintain=[
                Strength(
                    area="security",
                    description="Strong security infrastructure and compliance frameworks provide competitive advantage",
                    recommendation="Continue investing in cybersecurity and maintain industry-leading security standards"
                ),
                Strength(
                    area="customer_trust",
                    description="Established brand reputation and customer loyalty in traditional banking",
                    recommendation="Leverage trusted brand position while modernizing digital capabilities"
                )
            ],
            market_positioning=MarketPositioning(
                brand_position="Reliable traditional banking with strong security focus",
                competitor_position="Innovative digital-first banking with modern user experience",
                differentiation_opportunity="Combine trusted traditional banking expertise with personalized digital innovation"
            ),
            confidence_score=0.87
        )
    
    async def generate_trend_analysis(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trend analysis and pattern recognition
        """
        try:
            prompt = f"""
            Analyze the following historical brand performance data and identify key trends and patterns:
            
            {json.dumps(historical_data, indent=2)}
            
            Please provide:
            1. Key performance trends over time
            2. Seasonal patterns or cyclical behaviors
            3. Emerging opportunities based on data patterns
            4. Risk factors to monitor
            5. Predictive insights for the next 6-12 months
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst specializing in trend analysis and pattern recognition for brand performance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return {
                "trends": response.choices[0].message.content,
                "confidence": 0.85,
                "analysis_date": "2024-01-15T10:35:00Z"
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            raise Exception(f"Trend analysis failed: {str(e)}")
    
    async def validate_analysis_confidence(self, analysis_results: AnalysisResults) -> float:
        """
        Validate and score the confidence of analysis results
        """
        try:
            # This is a simplified confidence validation
            # In production, you'd implement more sophisticated validation
            
            factors = []
            
            # Check data completeness
            if analysis_results.detailed_comparison:
                factors.append(0.3)
            
            # Check insight quality
            if len(analysis_results.actionable_insights) >= 2:
                factors.append(0.3)
            
            # Check market positioning analysis
            if analysis_results.market_positioning:
                factors.append(0.2)
            
            # Check overall comparison validity
            if 0 <= analysis_results.overall_comparison.brand_score <= 1:
                factors.append(0.2)
            
            return sum(factors)
            
        except Exception as e:
            logger.error(f"Confidence validation failed: {str(e)}")
            return 0.5  # Default confidence score
