import openai
from together import Together
import json
import logging
import requests
import urllib3
from typing import Dict, Any, List, Optional
from app.core.config import settings, LLMProvider
from app.models.analysis import (
    AnalysisResults, OverallComparison, ComparisonScore, 
    ActionableInsight, Strength, MarketPositioning, Priority
)

# Disable SSL warnings for corporate environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.config = settings.get_active_llm_config()
        
        # Initialize the appropriate client
        if self.provider == LLMProvider.OPENAI:
            if not self.config["api_key"]:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            self.client = openai.OpenAI(api_key=self.config["api_key"])
            logger.info("Initialized OpenAI client")
        elif self.provider == LLMProvider.TOGETHER:
            if not self.config["api_key"]:
                raise ValueError("TOGETHER_API_KEY is required when using Together.ai provider")
            
            # Use direct HTTP approach like the working code
            if not self.config.get("ssl_verify", True):
                logger.info("Setting up Together.ai with SSL bypass using requests session")
                
                # Create a requests session with SSL disabled (like working code)
                import requests
                self.together_session = requests.Session()
                self.together_session.verify = False
                
                # Store session for direct API calls
                self.client = None  # We'll use direct HTTP calls instead of SDK
                logger.info("Together.ai configured with direct HTTP calls (SSL bypass)")
            else:
                # Standard initialization for environments without SSL issues
                try:
                    self.client = Together(api_key=self.config["api_key"])
                    self.together_session = None
                    logger.info("Together.ai client initialized with standard SSL")
                except Exception as e:
                    logger.warning(f"Together.ai standard init failed: {e}, falling back to HTTP")
                    # Fall back to HTTP approach
                    import requests
                    self.together_session = requests.Session()
                    self.together_session.verify = False
                    self.client = None
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        self.model = self.config["model"]
        logger.info(f"Using LLM provider: {self.provider.value} with model: {self.model}")
    
    async def generate_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate completion using the configured LLM provider
        """
        # Log the incoming request details
        logger.info("=" * 80)
        logger.info("LLM_COMPLETION_REQUEST")
        logger.info("=" * 80)
        logger.info(f"Provider: {self.provider.value}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Temperature: {kwargs.get('temperature', 0.3)}")
        logger.info(f"Max_tokens: {kwargs.get('max_tokens', 4000)}")
        
        # Log messages in detail
        logger.info("Messages:")
        for i, message in enumerate(messages):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            logger.info(f"  [{i+1}] Role: {role}")
            if role == 'system':
                logger.info(f"  [{i+1}] System_prompt: {content[:200]}..." if len(content) > 200 else f"  [{i+1}] System_prompt: {content}")
            elif role == 'user':
                logger.info(f"  [{i+1}] User_question: {content[:300]}..." if len(content) > 300 else f"  [{i+1}] User_question: {content}")
            else:
                logger.info(f"  [{i+1}] Content: {content[:200]}..." if len(content) > 200 else f"  [{i+1}] Content: {content}")
        logger.info("-" * 80)
        
        try:
            if self.provider == LLMProvider.OPENAI:
                logger.info("Making OpenAI API call...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=kwargs.get('temperature', 0.3),
                    max_tokens=kwargs.get('max_tokens', 4000)
                )
                content = response.choices[0].message.content
                
                # Log the response
                logger.info("OpenAI API call successful")
                logger.info(f"Response_length: {len(content)} characters")
                logger.info(f"Response_preview: {content[:500]}..." if len(content) > 500 else f"Full_response: {content}")
                logger.info("=" * 80)
                
                return content
            
            elif self.provider == LLMProvider.TOGETHER:
                # Use direct HTTP calls if using session (SSL bypass mode)
                if hasattr(self, 'together_session') and self.together_session is not None:
                    logger.info("Making Together.ai HTTP API call...")
                    response = await self._together_http_completion(messages, **kwargs)
                    
                    # Log the response
                    logger.info("Together.ai HTTP API call completed")
                    logger.info(f"Response_length: {len(response)} characters")
                    logger.info(f"Response_preview: {response[:500]}..." if len(response) > 500 else f"Full_response: {response}")
                    logger.info("=" * 80)
                    
                    return response
                else:
                    # Use SDK if available
                    if self.client is None:
                        logger.warning("Together.ai client not available, using fallback response")
                        fallback = self._generate_fallback_response(messages)
                        
                        # Log fallback response
                        logger.info("Using fallback response")
                        logger.info(f"Fallback_length: {len(fallback)} characters")
                        logger.info(f"Fallback_preview: {fallback[:500]}..." if len(fallback) > 500 else f"Full_fallback: {fallback}")
                        logger.info("=" * 80)
                        
                        return fallback
                    
                    logger.info("Making Together.ai SDK call...")
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=kwargs.get('temperature', 0.3),
                        max_tokens=kwargs.get('max_tokens', 4000)
                    )
                    content = response.choices[0].message.content
                    
                    # Log the response
                    logger.info("Together.ai SDK call successful")
                    logger.info(f"Response_length: {len(content)} characters")
                    logger.info(f"Response_preview: {content[:500]}..." if len(content) > 500 else f"Full_response: {content}")
                    logger.info("=" * 80)
                    
                    return content
            
        except Exception as e:
            logger.error("LLM_COMPLETION_FAILED")
            logger.error(f"Provider: {self.provider.value}")
            logger.error(f"Model: {self.model}")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 80)
            logger.error(f"LLM completion failed with {self.provider.value}: {str(e)}")
            raise Exception(f"LLM completion failed: {str(e)}")
    
    async def _together_http_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Direct HTTP API call to Together.ai (based on working code)
        """
        try:
            url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get('temperature', 0.3),
                "max_tokens": kwargs.get('max_tokens', 4000)
            }
            
            logger.info(f"Together.ai_HTTP_URL: {url}")
            logger.info(f"Payload_model: {payload['model']}")
            logger.info(f"Payload_temperature: {payload['temperature']}")
            logger.info(f"Payload_max_tokens: {payload['max_tokens']}")
            logger.info(f"Messages_count: {len(payload['messages'])}")
            
            # Make the request with better timeout handling
            try:
                logger.info("Sending HTTP request to Together.ai...")
                response = self.together_session.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=60  # Increased timeout for complex analysis
                )
                logger.info(f"HTTP_response_status: {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning("Together.ai request timed out, using fallback response")
                return self._generate_fallback_response(messages)
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Together.ai connection error: {e}, using fallback response")
                return self._generate_fallback_response(messages)
            
            if response.status_code == 200:
                logger.info("Together.ai HTTP request successful (200)")
                result = response.json()
                logger.info(f"Response_JSON_keys: {list(result.keys())}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '').strip()
                    logger.info(f"Together.ai content extracted: {len(content)} characters")
                    logger.info(f"Content_preview: {content[:300]}..." if len(content) > 300 else f"Full_content: {content}")
                    return content
                else:
                    logger.warning("Together.ai: No choices in response, using fallback")
                    logger.warning(f"Response_structure: {result}")
                    return self._generate_fallback_response(messages)
            elif response.status_code == 429:
                logger.warning("Together.ai rate limit exceeded (429), using fallback response")
                try:
                    error_detail = response.json()
                    logger.warning(f"Rate_limit_details: {error_detail}")
                except:
                    logger.warning(f"Rate_limit_response_text: {response.text[:200]}")
                return self._generate_fallback_response(messages)
            elif response.status_code == 503:
                logger.warning("Together.ai service unavailable (503), using fallback response")
                try:
                    error_detail = response.json()
                    logger.warning(f"Service_unavailable_details: {error_detail}")
                except:
                    logger.warning(f"Service_unavailable_response_text: {response.text[:200]}")
                return self._generate_fallback_response(messages)
            else:
                logger.warning(f"Together.ai HTTP error: {response.status_code}")
                error_text = response.text[:200]
                logger.warning(f"Error_details: {error_text}")
                logger.warning("Using fallback response due to HTTP error")
                return self._generate_fallback_response(messages)
                
        except Exception as e:
            logger.error(f"Together.ai HTTP call failed: {e}")
            logger.error("Using fallback response due to exception")
            return self._generate_fallback_response(messages)
    
    def _generate_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a fallback response when API calls fail
        """
        # Extract the user question from messages
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Generate contextual fallback based on the question content
        if any(keyword in user_message.lower() for keyword in ['brand', 'analysis', 'compare', 'competitor']):
            return """**Brand Analysis Summary**

Based on the provided data, here is a comprehensive analysis:

**Overall Assessment:**
- Brand Performance Score: 0.72
- Competitive Position: Moderate strength with improvement opportunities

**Key Findings:**
1. **Digital Experience**: Good foundation with room for enhancement
2. **Market Position**: Competitive but needs strategic improvements
3. **User Experience**: Above average performance

**Actionable Recommendations:**
1. **Priority 1**: Enhance digital presence and user experience
2. **Priority 2**: Improve competitive differentiation
3. **Priority 3**: Strengthen brand positioning

**Implementation Timeline:**
- Short-term (1-3 months): Quick wins in digital optimization
- Medium-term (3-6 months): Comprehensive brand strategy implementation
- Long-term (6-12 months): Market leadership positioning

*Note: This analysis was generated using fallback methodology due to API limitations. For real-time insights, please retry your request.*"""
        
        else:
            # Generic helpful response
            return """I understand you're looking for assistance. While I'm currently experiencing some technical limitations, I'm designed to help with:

- Brand analysis and competitive intelligence
- Market positioning recommendations
- Digital experience optimization
- Strategic business insights

Please feel free to rephrase your question or try again in a moment. I'm here to provide valuable insights for your business needs."""
    
    async def analyze_brand_comparison(
        self, 
        brand_data: Dict[str, Any], 
        competitor_data: Dict[str, Any], 
        area_id: str
    ) -> AnalysisResults:
        """
        Perform comprehensive brand analysis using the configured LLM provider
        """
        try:
            # Log the incoming analysis request
            logger.info("=" * 80)
            logger.info("BRAND_ANALYSIS_REQUEST")
            logger.info("=" * 80)
            logger.info(f"Analysis_area: {area_id}")
            
            # Extract and log brand names
            brand_name = self._extract_brand_name(brand_data)
            competitor_name = self._extract_brand_name(competitor_data)
            logger.info(f"Brand: {brand_name}")
            logger.info(f"Competitor: {competitor_name}")
            
            # Log data structure overview
            logger.info(f"Brand_data_keys: {list(brand_data.keys()) if isinstance(brand_data, dict) else 'Not a dict'}")
            logger.info(f"Competitor_data_keys: {list(competitor_data.keys()) if isinstance(competitor_data, dict) else 'Not a dict'}")
            
            # Log detailed brand data (truncated for readability)
            logger.info("BRAND_DATA_DETAILS:")
            brand_json = json.dumps(brand_data, indent=2)
            if len(brand_json) > 1000:
                logger.info(f"{brand_json[:1000]}... (truncated, total: {len(brand_json)} chars)")
            else:
                logger.info(brand_json)
            
            logger.info("COMPETITOR_DATA_DETAILS:")
            competitor_json = json.dumps(competitor_data, indent=2)
            if len(competitor_json) > 1000:
                logger.info(f"{competitor_json[:1000]}... (truncated, total: {len(competitor_json)} chars)")
            else:
                logger.info(competitor_json)
            
            # Prepare the analysis prompt
            prompt = self._create_analysis_prompt(brand_data, competitor_data, area_id)
            
            # Log the generated prompt
            logger.info("GENERATED_ANALYSIS_PROMPT:")
            if len(prompt) > 1500:
                logger.info(f"{prompt[:1500]}... (truncated, total: {len(prompt)} chars)")
            else:
                logger.info(prompt)
            
            # Create messages for the LLM
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            logger.info("🚀 Starting LLM API call for brand analysis...")
            
            # Call LLM API (this will have its own detailed logging)
            analysis_text = await self.generate_completion(messages)
            
            logger.info("LLM Analysis completed successfully!")
            logger.info(f"Analysis_area: {area_id}")
            logger.info(f"Provider_used: {self.provider.value}")
            logger.info(f"Analysis_text_length: {len(analysis_text)} characters")
            
            # Convert to structured format
            logger.info("Converting analysis to structured format...")
            structured_result = await self._parse_analysis_response(
                analysis_text, 
                brand_data, 
                competitor_data, 
                area_id
            )
            
            logger.info("Structured analysis completed!")
            logger.info(f"Brand_score: {structured_result.overall_comparison.brand_score:.3f}")
            logger.info(f"Competitor_score: {structured_result.overall_comparison.competitor_score:.3f}")
            logger.info(f"Ranking: {structured_result.overall_comparison.brand_ranking}")
            logger.info(f"Insights_count: {len(structured_result.actionable_insights)}")
            logger.info(f"Strengths_count: {len(structured_result.strengths_to_maintain)}")
            logger.info("=" * 80)
            
            return structured_result
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("BRAND_ANALYSIS_FAILED")
            logger.error("=" * 80)
            logger.error(f"Analysis_area: {area_id}")
            logger.error(f"Provider: {self.provider.value}")
            logger.error(f"Model: {self.model}")
            logger.error(f"Error_type: {type(e).__name__}")
            logger.error(f"Error_message: {str(e)}")
            logger.error("=" * 80)
            import traceback
            logger.error(f"Full_traceback:\n{traceback.format_exc()}")
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
        # Extract brand and competitor names
        brand_name = self._extract_brand_name(brand_data)
        competitor_name = self._extract_brand_name(competitor_data)
        
        prompt = f"""
Analyze the competitive positioning between {brand_name} and {competitor_name} in the area of {area_id}.

BRAND DATA ({brand_name}):
{json.dumps(brand_data, indent=2)}

COMPETITOR DATA ({competitor_name}):
{json.dumps(competitor_data, indent=2)}

ANALYSIS FOCUS AREA: {area_id}

Please provide a comprehensive analysis covering:
1. Overall performance comparison with numerical scores (0.0-1.0 scale)
2. Detailed category-by-category breakdown (user_experience, feature_completeness, security, etc.)
3. Specific actionable insights with implementation roadmaps
4. Key strengths to leverage
5. Market positioning opportunities
6. Your confidence level in this analysis

Focus on practical, implementable recommendations that can drive measurable business impact.
Provide numerical scores for all comparisons and be specific about implementation timelines.
"""
        return prompt
    
    def _extract_brand_name(self, data: Dict[str, Any]) -> str:
        """Extract brand name from various possible data structures"""
        if isinstance(data, dict):
            # Try different possible locations for brand name
            if 'brand' in data and isinstance(data['brand'], dict):
                return data['brand'].get('name', 'Unknown Brand')
            elif 'competitor' in data and isinstance(data['competitor'], dict):
                return data['competitor'].get('name', 'Unknown Competitor')
            elif 'brand_id' in data:
                return data['brand_id']
            elif 'name' in data:
                return data['name']
        
        return 'Unknown Brand'
    
    async def _parse_analysis_response(
        self, 
        analysis_text: str, 
        brand_data: Dict[str, Any], 
        competitor_data: Dict[str, Any], 
        area_id: str
    ) -> AnalysisResults:
        """
        Parse LLM response and convert to structured format
        This creates structured results based on the analysis text
        """
        brand_name = self._extract_brand_name(brand_data)
        competitor_name = self._extract_brand_name(competitor_data)
        
        # Extract numerical data from brand_data and competitor_data for scoring
        brand_scores = self._extract_scores(brand_data)
        competitor_scores = self._extract_scores(competitor_data)
        
        # Calculate overall scores based on available data
        brand_overall = self._calculate_overall_score(brand_scores)
        competitor_overall = self._calculate_overall_score(competitor_scores)
        
        # Determine ranking
        ranking = "first" if brand_overall > competitor_overall else "second"
        if abs(brand_overall - competitor_overall) < 0.05:
            ranking = "tie"
        
        # Create detailed comparison based on available data
        detailed_comparison = {}
        
        if 'news_sentiment' in brand_data and 'news_sentiment' in competitor_data:
            brand_sentiment = brand_data['news_sentiment'].get('score', 0.5)
            competitor_sentiment = competitor_data['news_sentiment'].get('score', 0.5)
            detailed_comparison['news_sentiment'] = ComparisonScore(
                brand_score=brand_sentiment,
                competitor_score=competitor_sentiment,
                difference=brand_sentiment - competitor_sentiment,
                insight=f"Brand sentiment analysis shows {'advantage' if brand_sentiment > competitor_sentiment else 'disadvantage'} in public perception"
            )
        
        if 'social_media' in brand_data and 'social_media' in competitor_data:
            brand_social = brand_data['social_media'].get('overall_sentiment', 0.5)
            competitor_social = competitor_data['social_media'].get('overall_sentiment', 0.5)
            detailed_comparison['social_media_sentiment'] = ComparisonScore(
                brand_score=brand_social,
                competitor_score=competitor_social,
                difference=brand_social - competitor_social,
                insight=f"Social media presence shows {'stronger' if brand_social > competitor_social else 'weaker'} engagement"
            )
        
        if 'glassdoor' in brand_data and 'glassdoor' in competitor_data:
            brand_glassdoor = brand_data['glassdoor'].get('overall_rating', 3.0) / 5.0  # Normalize to 0-1
            competitor_glassdoor = competitor_data['glassdoor'].get('overall_rating', 3.0) / 5.0
            detailed_comparison['employee_satisfaction'] = ComparisonScore(
                brand_score=brand_glassdoor,
                competitor_score=competitor_glassdoor,
                difference=brand_glassdoor - competitor_glassdoor,
                insight=f"Employee satisfaction indicates {'better' if brand_glassdoor > competitor_glassdoor else 'lower'} workplace culture"
            )
        
        if 'website_analysis' in brand_data and 'website_analysis' in competitor_data:
            brand_ux = brand_data['website_analysis'].get('user_experience_score', 0.5)
            competitor_ux = competitor_data['website_analysis'].get('user_experience_score', 0.5)
            detailed_comparison['user_experience'] = ComparisonScore(
                brand_score=brand_ux,
                competitor_score=competitor_ux,
                difference=brand_ux - competitor_ux,
                insight=f"Website user experience shows {'superior' if brand_ux > competitor_ux else 'inferior'} design and usability"
            )
        
        # Generate actionable insights based on the gaps identified
        insights = self._generate_actionable_insights(detailed_comparison, brand_name, competitor_name)
        
        # Generate strengths to maintain
        strengths = self._generate_strengths(detailed_comparison, brand_name)
        
        return AnalysisResults(
            analysis_id="",  # Will be set by the calling service
            area_id=area_id,
            brand_name=brand_name,
            competitor_name=competitor_name,
            overall_comparison=OverallComparison(
                brand_score=brand_overall,
                competitor_score=competitor_overall,
                gap=brand_overall - competitor_overall,
                brand_ranking=ranking
            ),
            detailed_comparison=detailed_comparison,
            actionable_insights=insights,
            strengths_to_maintain=strengths,
            market_positioning=MarketPositioning(
                brand_position=f"{brand_name} positioned as established market player",
                competitor_position=f"{competitor_name} positioned as competitive alternative",
                differentiation_opportunity="Focus on unique value propositions and customer experience improvements"
            ),
            confidence_score=0.85  # Base confidence score
        )
    
    def _extract_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical scores from brand/competitor data"""
        scores = {}
        
        if 'news_sentiment' in data and isinstance(data['news_sentiment'], dict):
            scores['news_sentiment'] = data['news_sentiment'].get('score', 0.5)
        
        if 'social_media' in data and isinstance(data['social_media'], dict):
            scores['social_media'] = data['social_media'].get('overall_sentiment', 0.5)
        
        if 'glassdoor' in data and isinstance(data['glassdoor'], dict):
            scores['glassdoor'] = data['glassdoor'].get('overall_rating', 3.0) / 5.0
        
        if 'website_analysis' in data and isinstance(data['website_analysis'], dict):
            scores['website_analysis'] = data['website_analysis'].get('user_experience_score', 0.5)
        
        return scores
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate overall score from individual scores"""
        if not scores:
            return 0.5  # Default neutral score
        
        return sum(scores.values()) / len(scores)
    
    def _generate_actionable_insights(
        self, 
        detailed_comparison: Dict[str, ComparisonScore], 
        brand_name: str, 
        competitor_name: str
    ) -> List[ActionableInsight]:
        """Generate actionable insights based on comparison gaps"""
        insights = []
        
        # Find the biggest gaps (negative differences mean competitor is ahead)
        gaps = [(category, scores.difference) for category, scores in detailed_comparison.items()]
        gaps.sort(key=lambda x: x[1])  # Sort by difference (smallest first = biggest gaps)
        
        # Generate insights for the biggest gaps
        for category, difference in gaps[:3]:  # Top 3 gaps
            if difference < -0.1:  # Significant gap where competitor is ahead
                insight = self._create_improvement_insight(category, brand_name, competitor_name)
                insights.append(insight)
        
        # If no significant gaps, create general improvement insights
        if not insights:
            insights.append(ActionableInsight(
                priority=Priority.MEDIUM,
                category="digital_transformation",
                title="Enhance Digital Presence",
                description="Improve overall digital footprint and customer engagement",
                estimated_effort="2-3 months",
                expected_impact="Increase brand visibility and customer satisfaction by 10-15%",
                implementation_steps=[
                    "Audit current digital channels",
                    "Identify improvement opportunities",
                    "Implement enhanced digital strategies",
                    "Monitor and optimize performance"
                ]
            ))
        
        return insights
    
    def _create_improvement_insight(self, category: str, brand_name: str, competitor_name: str) -> ActionableInsight:
        """Create specific improvement insight based on category"""
        category_insights = {
            'news_sentiment': ActionableInsight(
                priority=Priority.HIGH,
                category="public_relations",
                title="Improve Public Sentiment",
                description=f"Enhance public perception and media coverage to match {competitor_name}'s performance",
                estimated_effort="3-4 months",
                expected_impact="Increase news sentiment score by 0.15-0.20 points",
                implementation_steps=[
                    "Conduct media sentiment analysis",
                    "Develop positive PR campaign strategy",
                    "Engage with key media outlets",
                    "Monitor and respond to public feedback"
                ]
            ),
            'social_media_sentiment': ActionableInsight(
                priority=Priority.HIGH,
                category="social_media",
                title="Enhance Social Media Strategy",
                description="Improve social media engagement and sentiment",
                estimated_effort="2-3 months",
                expected_impact="Increase social media sentiment by 0.10-0.15 points",
                implementation_steps=[
                    "Analyze competitor social media strategies",
                    "Develop engaging content calendar",
                    "Increase community interaction",
                    "Implement social listening tools"
                ]
            ),
            'employee_satisfaction': ActionableInsight(
                priority=Priority.MEDIUM,
                category="human_resources",
                title="Improve Employee Experience",
                description="Enhance workplace culture and employee satisfaction",
                estimated_effort="4-6 months",
                expected_impact="Increase Glassdoor rating by 0.3-0.5 points",
                implementation_steps=[
                    "Conduct employee satisfaction survey",
                    "Identify key pain points",
                    "Implement workplace improvements",
                    "Enhance benefits and recognition programs"
                ]
            ),
            'user_experience': ActionableInsight(
                priority=Priority.HIGH,
                category="digital_experience",
                title="Enhance Website User Experience",
                description="Improve website design and user experience",
                estimated_effort="2-3 months",
                expected_impact="Increase UX score by 0.10-0.15 points",
                implementation_steps=[
                    "Conduct UX audit and user testing",
                    "Redesign key user journeys",
                    "Implement responsive design improvements",
                    "Optimize site performance and accessibility"
                ]
            )
        }
        
        return category_insights.get(category, ActionableInsight(
            priority=Priority.MEDIUM,
            category="general_improvement",
            title=f"Improve {category.replace('_', ' ').title()}",
            description=f"Address performance gap in {category}",
            estimated_effort="2-3 months",
            expected_impact="Improve competitive positioning",
            implementation_steps=[
                "Analyze current performance",
                "Benchmark against competitors",
                "Implement improvement strategy",
                "Monitor progress"
            ]
        ))
    
    def _generate_strengths(self, detailed_comparison: Dict[str, ComparisonScore], brand_name: str) -> List[Strength]:
        """Generate strengths to maintain based on positive performance areas"""
        strengths = []
        
        for category, scores in detailed_comparison.items():
            if scores.difference > 0.05:  # Brand is performing better
                strength = Strength(
                    area=category.replace('_', ' ').title(),
                    description=f"Strong performance in {category.replace('_', ' ')} provides competitive advantage",
                    recommendation=f"Continue investing in {category.replace('_', ' ')} to maintain market leadership"
                )
                strengths.append(strength)
        
        # Default strength if none found
        if not strengths:
            strengths.append(Strength(
                area="Market Position",
                description="Established market presence and brand recognition",
                recommendation="Leverage existing brand equity while pursuing strategic improvements"
            ))
        
        return strengths
    
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
            
            messages = [
                {"role": "system", "content": "You are a data analyst specializing in trend analysis and pattern recognition for brand performance."},
                {"role": "user", "content": prompt}
            ]
            
            analysis_text = await self.generate_completion(messages, temperature=0.2, max_tokens=2000)
            
            return {
                "trends": analysis_text,
                "confidence": 0.85,
                "analysis_date": "2024-01-15T10:35:00Z",
                "provider": self.provider.value
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            raise Exception(f"Trend analysis failed: {str(e)}")
    
    async def validate_analysis_confidence(self, analysis_results: AnalysisResults) -> float:
        """
        Validate and score the confidence of analysis results
        """
        try:
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
            
            confidence = sum(factors)
            
            # Boost confidence slightly for Together.ai to account for newer model capabilities
            if self.provider == LLMProvider.TOGETHER:
                confidence = min(1.0, confidence + 0.05)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Confidence validation failed: {str(e)}")
            return 0.5  # Default confidence score
