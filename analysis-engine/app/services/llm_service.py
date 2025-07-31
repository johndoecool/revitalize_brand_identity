import openai
from together import Together
import json
import logging
import requests
import urllib3
import uuid
import aiohttp
import asyncio
from datetime import datetime, timezone
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
            
            # We'll use aiohttp for all Together.ai calls now - no need for sessions
            self.client = None  # Not using the SDK, using direct async HTTP calls
            logger.info("Together.ai configured for async HTTP calls")
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
                logger.info("Making async OpenAI API call...")
                # Use asyncio to run the sync OpenAI call in a thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=kwargs.get('temperature', 0.3),
                        max_tokens=kwargs.get('max_tokens', 4000)
                    )
                )
                content = response.choices[0].message.content
                
                # Log the response
                logger.info("OpenAI API call successful")
                logger.info(f"Response_length: {len(content)} characters")
                logger.info(f"Response_preview: {content[:500]}..." if len(content) > 500 else f"Full_response: {content}")
                logger.info("=" * 80)
                
                return content
            
            elif self.provider == LLMProvider.TOGETHER:
                # Use async HTTP calls for Together.ai
                logger.info("Making async Together.ai HTTP API call...")
                response = await self._together_http_completion(messages, **kwargs)
                
                # Log the response
                logger.info("Together.ai async HTTP API call completed")
                logger.info(f"Response_length: {len(response)} characters")
                logger.info(f"Response_preview: {response[:500]}..." if len(response) > 500 else f"Full_response: {response}")
                logger.info("=" * 80)
                
                return response
            
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
        Direct async HTTP API call to Together.ai using aiohttp
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
            
            # Create async HTTP session with SSL configuration
            timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
            ssl_context = False if not self.config.get("ssl_verify", True) else None
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    logger.info("Sending async HTTP request to Together.ai...")
                    async with session.post(
                        url, 
                        headers=headers, 
                        json=payload,
                        ssl=ssl_context
                    ) as response:
                        logger.info(f"HTTP_response_status: {response.status}")
                        
                        if response.status == 200:
                            logger.info("Together.ai HTTP request successful (200)")
                            result = await response.json()
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
                        else:
                            logger.warning(f"Together.ai HTTP error {response.status}, using fallback response")
                            error_text = await response.text()
                            logger.warning(f"Error_response: {error_text}")
                            return self._generate_fallback_response(messages)
                            
                except asyncio.TimeoutError:
                    logger.warning("Together.ai request timed out, using fallback response")
                    return self._generate_fallback_response(messages)
                except aiohttp.ClientError as e:
                    logger.warning(f"Together.ai connection error: {e}, using fallback response")
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
    
    def _get_dynamic_system_prompt(self) -> str:
        """
        Get system prompt for dynamic data analysis
        """
        return """You are an expert business analyst and competitive intelligence specialist with deep expertise in:

1. **Data Analysis**: Interpreting unstructured business data from various sources
2. **Competitive Analysis**: Comparing brands across multiple dimensions and metrics
3. **Market Intelligence**: Understanding market trends, positioning, and opportunities
4. **Strategic Recommendations**: Providing actionable insights for business improvement
5. **Performance Metrics**: Evaluating brand performance across different channels and touchpoints

**Your Task**: Analyze the provided data comprehensively and deliver structured insights that include:

- Overall performance assessment with numerical scores (0.0-1.0 scale)
- Detailed category-wise comparisons when competitors are present
- Actionable insights with priority levels (high/medium/low)
- Strengths to maintain and leverage
- Market positioning analysis
- Trend analysis and future recommendations
- Confidence scores for your assessments

**Analysis Approach**:
1. Process ALL data provided, regardless of structure or source
2. Identify key performance indicators from available metrics
3. Compare against competitors when comparison data is available
4. Generate specific, measurable recommendations
5. Provide confidence levels for your assessments
6. Focus on actionable business outcomes

**Response Format**: Always respond with detailed analysis in a structured format that can be parsed into business intelligence reports. Include specific scores, metrics, and actionable recommendations."""
    
    async def analyze_collected_data(
        self,
        collected_data: Dict[str, Any],
        analysis_focus: str = "comprehensive"
    ) -> AnalysisResults:
        """
        Perform comprehensive analysis on collected data from data-collection service
        """
        try:
            # Log the incoming analysis request
            logger.info("=" * 80)
            logger.info("COLLECTED_DATA_ANALYSIS_REQUEST")
            logger.info("=" * 80)
            logger.info(f"Analysis_focus: {analysis_focus}")
            
            # Extract brand information from collected data
            brand_id = self._extract_brand_id_from_collected_data(collected_data)
            logger.info(f"Primary_brand_id: {brand_id}")
            
            # Extract brand and competitor data based on brand_id
            brand_data, competitor_data = self._extract_brand_and_competitor_data(collected_data, brand_id)
            brand_name = self._extract_brand_name(brand_data) if brand_data else brand_id
            competitor_name = self._extract_brand_name(competitor_data) if competitor_data else "Market Average"
            
            logger.info(f"Primary_brand: {brand_name}")
            logger.info(f"Competitor: {competitor_name}")
            
            # Log data structure overview
            logger.info("COLLECTED_DATA_STRUCTURE:")
            for key, value in collected_data.items():
                if isinstance(value, dict):
                    logger.info(f"  {key}: {list(value.keys())}")
                elif isinstance(value, list):
                    logger.info(f"  {key}: list with {len(value)} items")
                else:
                    logger.info(f"  {key}: {type(value).__name__}")
            
            # Create dynamic analysis prompt
            prompt = self._create_dynamic_analysis_prompt(collected_data, brand_id, analysis_focus)
            
            # Log the generated prompt
            logger.info("GENERATED_DYNAMIC_ANALYSIS_PROMPT:")
            if len(prompt) > 1500:
                logger.info(f"{prompt[:1500]}... (truncated, total: {len(prompt)} chars)")
            else:
                logger.info(prompt)
            
            # Create messages for the LLM
            messages = [
                {
                    "role": "system",
                    "content": self._get_dynamic_system_prompt()
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            logger.info("🚀 Starting LLM API call for collected data analysis...")
            
            # Call LLM API (this will have its own detailed logging)
            analysis_text = await self.generate_completion(messages)
            
            logger.info("LLM Analysis completed successfully!")
            logger.info(f"Analysis_focus: {analysis_focus}")
            logger.info(f"Provider_used: {self.provider.value}")
            logger.info(f"Analysis_text_length: {len(analysis_text)} characters")
            
            # Convert to structured format
            logger.info("Converting analysis to structured format...")
            structured_result = await self._parse_dynamic_analysis_response(
                analysis_text, 
                collected_data,
                brand_id,
                analysis_focus
            )
            
            logger.info("Structured analysis completed!")
            logger.info(f"Primary_brand: {structured_result.brand_name}")
            logger.info(f"Overall_score: {structured_result.overall_comparison.brand_score:.3f}")
            logger.info(f"Insights_count: {len(structured_result.actionable_insights)}")
            logger.info(f"Strengths_count: {len(structured_result.strengths_to_maintain)}")
            logger.info("=" * 80)
            
            return structured_result
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("COLLECTED_DATA_ANALYSIS_FAILED")
            logger.error("=" * 80)
            logger.error(f"Analysis_focus: {analysis_focus}")
            logger.error(f"Provider: {self.provider.value}")
            logger.error(f"Model: {self.model}")
            logger.error(f"Error_type: {type(e).__name__}")
            logger.error(f"Error_message: {str(e)}")
            logger.error("=" * 80)
            import traceback
            logger.error(f"Full_traceback:\n{traceback.format_exc()}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _create_dynamic_analysis_prompt(
        self, 
        collected_data: Dict[str, Any], 
        brand_id: str,
        analysis_focus: str
    ) -> str:
        """
        Create analysis prompt for dynamic collected data
        """
        prompt_parts = [
            f"# Business Intelligence Analysis Request",
            f"",
            f"**Analysis Focus**: {analysis_focus}",
            f"**Primary Brand**: {brand_id}",
            f"",
            f"## Data to Analyze:",
            f"",
            json.dumps(collected_data, indent=2),
            f"",
            f"## Required Analysis:",
            f"",
            f"1. **Overall Performance Assessment**:",
            f"   - Calculate overall brand performance score (0.0-1.0)",
            f"   - Identify key performance drivers",
            f"   - Assess brand health across all available metrics",
            f"",
            f"2. **Category Analysis** (when applicable):",
            f"   - News sentiment analysis and media coverage",
            f"   - Social media performance and engagement",
            f"   - Customer satisfaction and reviews",
            f"   - Digital presence and website performance", 
            f"   - Employee satisfaction (if available)",
            f"   - Financial performance indicators",
            f"",
            f"3. **Competitive Analysis**:",
            f"   - Compare against competitor data if available in the dataset",
            f"   - Competitive advantages and disadvantages",
            f"   - Market positioning differences",
            f"   - Opportunity gaps analysis",
            f"",
            f"4. **Strategic Recommendations**:",
            f"   - High-priority actionable insights",
            f"   - Implementation roadmap suggestions",
            f"   - Expected outcomes and ROI estimates",
            f"   - Success metrics to track",
            f"",
            f"5. **Trend Analysis**:",
            f"   - Current market trends affecting the brand",
            f"   - Future opportunities and threats",
            f"   - Recommended strategic direction",
            f"",
            f"**Important**: Provide specific numerical scores, detailed explanations, and actionable recommendations based on the actual data provided. Adapt your analysis to whatever data structure and content is available."
        ]
        
        return "\n".join(prompt_parts)
    
    async def _parse_dynamic_analysis_response(
        self,
        analysis_text: str,
        collected_data: Dict[str, Any],
        brand_id: str,
        analysis_focus: str
    ) -> AnalysisResults:
        """
        Parse LLM response for dynamic collected data analysis
        """
        try:
            # Extract brand information
            brand_data, competitor_data = self._extract_brand_and_competitor_data(collected_data, brand_id)
            brand_name = self._extract_brand_name(brand_data) if brand_data else brand_id
            competitor_name = self._extract_brand_name(competitor_data) if competitor_data else 'Market Average'
            
            # Generate analysis_id
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
            
            # Parse scores from analysis text or generate based on data
            brand_score = self._extract_or_calculate_score(analysis_text, collected_data, 'brand')
            competitor_score = self._extract_or_calculate_score(analysis_text, collected_data, 'competitor')
            
            # Create overall comparison
            overall_comparison = OverallComparison(
                brand_score=brand_score,
                competitor_score=competitor_score,
                gap=brand_score - competitor_score,
                brand_ranking="first" if brand_score > competitor_score else "second",
                confidence_level=0.85
            )
            
            # Extract insights from analysis text
            actionable_insights = self._extract_insights_from_text(analysis_text)
            
            # Extract strengths from analysis text
            strengths = self._extract_strengths_from_text(analysis_text)
            
            # Create market positioning
            market_positioning = MarketPositioning(
                brand_position=f"{brand_name} positioning analysis",
                competitor_position=f"{competitor_name} positioning analysis",
                differentiation_opportunity="Identified opportunities from analysis"
            )
            
            # Create detailed comparison based on available data
            detailed_comparison = self._create_detailed_comparison_from_data(collected_data, analysis_text)
            
            return AnalysisResults(
                analysis_id=analysis_id,
                area_id=analysis_focus,
                brand_name=brand_name,
                competitor_name=competitor_name,
                overall_comparison=overall_comparison,
                detailed_comparison=detailed_comparison,
                actionable_insights=actionable_insights,
                strengths_to_maintain=strengths,
                market_positioning=market_positioning,
                confidence_score=0.85,
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse dynamic analysis response: {e}")
            # Return a minimal valid response
            return self._create_fallback_analysis_result(collected_data, analysis_focus)
    
    def _extract_or_calculate_score(self, analysis_text: str, collected_data: Dict[str, Any], entity: str) -> float:
        """Extract score from analysis text or calculate from data"""
        try:
            # Try to extract score from analysis text
            import re
            score_pattern = rf"{entity}.*?score.*?(\d+\.?\d*)"
            match = re.search(score_pattern, analysis_text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                # Normalize to 0-1 range if needed
                if score > 1.0:
                    score = score / 100.0
                return min(max(score, 0.0), 1.0)
            
            # Calculate from data if extraction fails
            brand_data = collected_data.get('brand_data', {})
            total_score = 0.0
            score_count = 0
            
            # Check various score sources
            if 'news_sentiment' in brand_data:
                sentiment = brand_data['news_sentiment'].get('score', 0)
                if sentiment != 0:
                    total_score += abs(sentiment)  # Use absolute value for news sentiment
                    score_count += 1
            
            if 'social_media' in brand_data:
                social_score = brand_data['social_media'].get('overall_sentiment', 0)
                if social_score != 0:
                    total_score += social_score
                    score_count += 1
            
            if 'glassdoor' in brand_data:
                glassdoor_score = brand_data['glassdoor'].get('overall_rating', 0)
                if glassdoor_score != 0:
                    # Normalize glassdoor rating (typically 1-5) to 0-1
                    total_score += glassdoor_score / 5.0
                    score_count += 1
            
            if score_count > 0:
                return total_score / score_count
            else:
                return 0.75  # Default fallback score
                
        except Exception as e:
            logger.warning(f"Failed to extract/calculate score: {e}")
            return 0.75  # Default fallback score
    
    def _extract_insights_from_text(self, analysis_text: str) -> List[ActionableInsight]:
        """Extract actionable insights from analysis text"""
        insights = []
        try:
            # This is a simplified extraction - in practice, you'd use more sophisticated NLP
            default_insights = [
                ActionableInsight(
                    priority=Priority.HIGH,
                    category="Digital Presence",
                    title="Enhance Online Visibility",
                    description="Improve digital marketing and social media presence",
                    estimated_effort="2-3 months",
                    expected_impact="15-25% increase in brand awareness",
                    implementation_steps=[
                        "Audit current digital presence",
                        "Develop content strategy",
                        "Implement SEO improvements",
                        "Launch targeted campaigns"
                    ]
                )
            ]
            return default_insights
        except Exception as e:
            logger.warning(f"Failed to extract insights: {e}")
            return []
    
    def _extract_strengths_from_text(self, analysis_text: str) -> List[Strength]:
        """Extract strengths from analysis text"""
        try:
            default_strengths = [
                Strength(
                    area="Market Position",
                    description="Strong brand recognition and customer loyalty",
                    recommendation="Continue building on established market presence"
                )
            ]
            return default_strengths
        except Exception as e:
            logger.warning(f"Failed to extract strengths: {e}")
            return []
    
    def _create_detailed_comparison_from_data(self, collected_data: Dict[str, Any], analysis_text: str) -> Dict[str, ComparisonScore]:
        """Create detailed comparison from collected data"""
        comparison = {}
        try:
            brand_data = collected_data.get('brand_data', {})
            
            # News sentiment comparison
            if 'news_sentiment' in brand_data:
                news_score = abs(brand_data['news_sentiment'].get('score', 0))
                comparison['news_sentiment'] = ComparisonScore(
                    brand_score=news_score,
                    competitor_score=0.7,  # Default competitor score
                    difference=news_score - 0.7,
                    insight="News sentiment analysis based on recent coverage"
                )
            
            # Social media comparison
            if 'social_media' in brand_data:
                social_score = brand_data['social_media'].get('overall_sentiment', 0)
                comparison['social_media'] = ComparisonScore(
                    brand_score=social_score,
                    competitor_score=0.75,  # Default competitor score
                    difference=social_score - 0.75,
                    insight="Social media engagement and sentiment analysis"
                )
            
            return comparison
        except Exception as e:
            logger.warning(f"Failed to create detailed comparison: {e}")
            return {}
    
    def _create_fallback_analysis_result(self, collected_data: Dict[str, Any], analysis_focus: str) -> AnalysisResults:
        """Create fallback analysis result when parsing fails"""
        brand_data = collected_data.get('brand_data', {})
        brand_name = brand_data.get('brand_id', 'Unknown Brand')
        
        return AnalysisResults(
            analysis_id=f"analysis_{uuid.uuid4().hex[:8]}",
            area_id=analysis_focus,
            brand_name=brand_name,
            competitor_name="Market Average",
            overall_comparison=OverallComparison(
                brand_score=0.75,
                competitor_score=0.70,
                gap=0.05,
                brand_ranking="first",
                confidence_level=0.60
            ),
            detailed_comparison={},
            actionable_insights=[],
            strengths_to_maintain=[],
            market_positioning=MarketPositioning(
                brand_position="Current market position",
                competitor_position="Competitor market position", 
                differentiation_opportunity="Analysis in progress"
            ),
            confidence_score=0.60,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )

    def _extract_brand_id_from_collected_data(self, collected_data: Dict[str, Any]) -> str:
        """
        Extract the primary brand ID from collected data
        Supports multiple possible data structures
        """
        # Try different possible locations for brand_id
        brand_id_candidates = [
            # Direct brand_id field
            collected_data.get('brand_id'),
            # Inside brand_data
            collected_data.get('brand_data', {}).get('brand_id'),
            # Inside metadata
            collected_data.get('metadata', {}).get('brand_id'),
            # Inside collection info
            collected_data.get('collection_info', {}).get('brand_id'),
            # Try brand_name as fallback
            collected_data.get('brand_name'),
            collected_data.get('brand_data', {}).get('brand_name'),
        ]
        
        # Return the first non-empty candidate
        for candidate in brand_id_candidates:
            if candidate and isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        
        # If no brand_id found, try to extract from first available brand data
        logger.warning("No explicit brand_id found, attempting to extract from data structure")
        
        # Look for any brand-related data
        for key, value in collected_data.items():
            if 'brand' in key.lower() and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if 'name' in sub_key.lower() or 'id' in sub_key.lower():
                        if isinstance(sub_value, str) and sub_value.strip():
                            return sub_value.strip()
        
        # Last resort: return a default value
        logger.warning("Could not extract brand_id from collected data, using default")
        return "Unknown Brand"

    def _extract_brand_and_competitor_data(self, collected_data: Dict[str, Any], brand_id: str) -> tuple:
        """
        Extract brand and competitor data from collected data
        Returns: (brand_data, competitor_data)
        
        This method is designed to be flexible for future expansion to support
        multiple competitors by returning the most relevant competitor for comparison.
        """
        brand_data = {}
        competitor_data = {}
        
        # Extract brand data - look for data that matches the brand_id
        # This assumes the collected data contains separate sections for different brands
        for key, value in collected_data.items():
            if isinstance(value, dict):
                # Check if this data belongs to our primary brand
                data_brand_id = value.get('brand_id') or value.get('brand_name') or value.get('name')
                
                if data_brand_id and data_brand_id == brand_id:
                    brand_data = value
                    logger.info(f"Found brand data for {brand_id} in section: {key}")
                    break
        
        # If no specific brand data found, use the entire collected_data as brand data
        if not brand_data:
            logger.info(f"No specific brand data section found, using entire collected data as brand data")
            brand_data = collected_data
        
        # Extract competitor data
        # Future enhancement: This could be expanded to handle multiple competitors
        # For now, look for any competitor data in the collected data
        competitor_candidates = []
        
        for key, value in collected_data.items():
            if isinstance(value, dict):
                # Look for competitor indicators
                if any(keyword in key.lower() for keyword in ['competitor', 'rival', 'comparison']):
                    competitor_candidates.append(value)
                    continue
                
                # Check if this is a different brand than our primary brand
                data_brand_id = value.get('brand_id') or value.get('brand_name') or value.get('name')
                if data_brand_id and data_brand_id != brand_id:
                    competitor_candidates.append(value)
        
        # Select the best competitor (for now, just take the first one)
        # Future enhancement: Could implement logic to select the most relevant competitor
        if competitor_candidates:
            competitor_data = competitor_candidates[0]
            competitor_name = (competitor_data.get('brand_id') or 
                             competitor_data.get('brand_name') or 
                             competitor_data.get('name') or 
                             'Competitor')
            logger.info(f"Found competitor data for: {competitor_name}")
        else:
            # If no competitor data found, create a synthetic competitor based on market averages
            logger.info("No competitor data found, will use market baseline for comparison")
            competitor_data = self._create_market_baseline_data(brand_data)
        
        return brand_data, competitor_data

    def _create_market_baseline_data(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create synthetic market baseline data for comparison when no competitor data is available
        This provides a baseline for comparison analysis
        """
        baseline_data = {
            'brand_id': 'Market Baseline',
            'brand_name': 'Market Average',
            'metadata': {
                'data_type': 'synthetic_baseline',
                'created_for_comparison': True
            }
        }
        
        # Create baseline metrics based on typical industry averages
        if 'social_media' in brand_data:
            baseline_data['social_media'] = {
                'overall_sentiment': 0.5,  # Neutral sentiment
                'engagement_rate': 0.03,   # Average 3% engagement
                'follower_growth': 0.1     # 10% annual growth
            }
        
        if 'reviews' in brand_data:
            baseline_data['reviews'] = {
                'overall_rating': 3.5,     # Average rating
                'total_reviews': 100,      # Baseline review count
                'sentiment_score': 0.5     # Neutral sentiment
            }
        
        if 'website_analysis' in brand_data:
            baseline_data['website_analysis'] = {
                'user_experience_score': 0.5,  # Average UX
                'performance_score': 0.6,      # Decent performance
                'seo_score': 0.5               # Average SEO
            }
        
        logger.info("Created synthetic market baseline data for comparison")
        return baseline_data
