from typing import Optional, List, Dict, Any
import logging
import httpx
import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from app.models import (
    BrandSearchRequest, 
    BrandSearchResponse, 
    AreaSuggestionsResponse, 
    CompetitorDiscoveryResponse,
    ErrorResponse
)
from app.services import BrandService
from app.cache_service import BrandCacheService
from app.areas_cache_service import BrandAreasCacheService
from app.competitors_cache_service import BrandCompetitorsCacheService
from app.config import config

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])
brand_service = BrandService()
cache_service = BrandCacheService()
areas_cache_service = BrandAreasCacheService()
competitors_cache_service = BrandCompetitorsCacheService()
logger = logging.getLogger('brand_service.api')


@router.post(
    "/search",
    response_model=BrandSearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Search for brands",
    description="Search for brands based on a query string with optional result limit"
)
async def search_brands(request: BrandSearchRequest):
    """
    Search for brands based on the provided query.
    Uses Financial Modeling Prep as primary source, falls back to Alpha Vantage.
    
    - **query**: Search term to find matching brands
    - **limit**: Maximum number of results to return (1-100, default: 10)
    """
    logger.info(f"POST /api/v1/brands/search - Query: '{request.query}', Limit: {request.limit}")
    
    try:
        # Check cache first
        logger.info(f"Checking cache for query: '{request.query}'")
        cached_result = cache_service.get_cached_search(request.query, request.limit)
        
        if cached_result:
            logger.info(f"Cache HIT! Processing cached results for query: '{request.query}'")
            
            # Apply limit filtering to cached data
            final_result_list = []
            cached_data = cached_result.get("data", [])
            total_cached = len(cached_data)
            
            if total_cached <= request.limit:
                # Take all objects if within limit
                final_result_list = cached_data
            else:
                # Sort by confidence_score desc and take first 'limit' objects
                sorted_data = sorted(cached_data, key=lambda x: float(x.get("confidence_score", 0)), reverse=True)
                final_result_list = sorted_data[:request.limit]
            
            # Create final response
            response = {
                "success": True,
                "data": final_result_list,
                "total_results": len(final_result_list)
            }
            
            logger.info(f"Cache processed - Returned {len(final_result_list)} brands for query: '{request.query}'")
            return JSONResponse(content=response)
        
        # STEP 1: Cache miss - try Financial Modeling Prep API first
        logger.info(f"Cache MISS - Fetching fresh data from Financial Modeling Prep for query: '{request.query}'")
        result_list = await _search_financial_modeling_prep_all(request.query)
        
        # If FMP returns results, cache them
        if result_list:
            final_response = {
                "query": request.query,
                "success": True,
                "data": result_list,
                "total_results": len(result_list)
            }
            
            logger.info(f"Financial Modeling Prep success - Caching results for query: '{request.query}' - {len(result_list)} brands found")
            cache_service.cache_search_response(final_response)
        else:
            # STEP 2: FMP failed, try Alpha Vantage as fallback
            logger.info(f"Financial Modeling Prep returned no results - Trying Alpha Vantage for query: '{request.query}'")
            result_list = await _search_alpha_vantage_all(request.query)
            
            # If Alpha Vantage returns results, cache them
            if result_list:
                final_response = {
                    "query": request.query,
                    "success": True,
                    "data": result_list,
                    "total_results": len(result_list)
                }
                
                logger.info(f"Alpha Vantage success - Caching results for query: '{request.query}' - {len(result_list)} brands found")
                cache_service.cache_search_response(final_response)
        
        # Now check cache again and apply limit filtering
        final_result_list = []
        cached_result = cache_service.get_cached_search(request.query, request.limit)
        
        if not cached_result:
            logger.warning(f"No records found for query: '{request.query}' from both APIs")
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "No Records Found",
                    "details": f"No brands found matching query: '{request.query}'"
                }
            )
        
        # Apply limit filtering to cached data
        cached_data = cached_result.get("data", [])
        total_cached = len(cached_data)
        
        if total_cached <= request.limit:
            # Take all objects if within limit
            final_result_list = cached_data
        else:
            # Sort by confidence_score desc and take first 'limit' objects
            sorted_data = sorted(cached_data, key=lambda x: float(x.get("confidence_score", 0)), reverse=True)
            final_result_list = sorted_data[:request.limit]
        
        # Create final response
        response = {
            "success": True,
            "data": final_result_list,
            "total_results": len(final_result_list)
        }
        
        logger.info(f"Search completed successfully - Returned {len(final_result_list)} brands for query: '{request.query}'")
        return JSONResponse(content=response)
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for no records found)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during brand search for query '{request.query}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Internal server error", "details": str(e)}
        )


async def _search_financial_modeling_prep_all(query: str) -> List[Dict[str, Any]]:
    """Search using Financial Modeling Prep API - process all results"""
    result_list = []
    
    try:
        # Step 1: Get search results
        search_url = config.get_fmp_search_url(query)
        logger.debug(f"Financial Modeling Prep search URL: {search_url}")
        
        async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
            response = await client.get(search_url)
            response.raise_for_status()
            
            search_data = response.json()
            logger.debug(f"Financial Modeling Prep search response: {search_data}")
            
            if not search_data or not isinstance(search_data, list):
                logger.info(f"No search results found in Financial Modeling Prep for query: '{query}'")
                return []
            
            # Process all results (no limit)
            logger.info(f"Found {len(search_data)} FMP matches, processing all results")
            
            # Step 2: Get detailed information for each symbol
            for result in search_data:
                symbol = result.get("symbol", "")
                
                if not symbol:
                    continue
                
                try:
                    # Get company profile
                    profile_url = config.get_fmp_profile_url(symbol)
                    profile_response = await client.get(profile_url)
                    profile_response.raise_for_status()
                    
                    profile_data = profile_response.json()
                    logger.debug(f"Financial Modeling Prep profile response for {symbol}: {profile_data}")
                    
                    if not profile_data or not isinstance(profile_data, list) or len(profile_data) == 0:
                        logger.warning(f"No company profile found for symbol: '{symbol}'")
                        continue
                    
                    # FMP returns array, take first element
                    company_data = profile_data[0]
                    
                    # Create brand object
                    brand_obj = {
                        "id": company_data.get("symbol", symbol),
                        "name": company_data.get("companyName", ""),
                        "full_name": company_data.get("companyName", ""),
                        "industry": company_data.get("industry", ""),
                        "logo_url": config.get_logo_url(symbol),
                        "description": company_data.get("description", ""),
                        "confidence_score": 0.9  # Fixed confidence score for FMP results
                    }
                    
                    result_list.append(brand_obj)
                    logger.debug(f"Successfully created brand object for symbol: {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing FMP symbol '{symbol}': {str(e)}")
                    continue
            
            logger.info(f"Financial Modeling Prep successfully created {len(result_list)} brand objects")
            return result_list
            
    except httpx.ConnectError as e:
        logger.error(f"Network connection error during FMP search for '{query}': {str(e)}")
        return []
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error during FMP search for '{query}': {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during FMP search for '{query}': {str(e)}")
        return []


async def _search_alpha_vantage_all(query: str) -> List[Dict[str, Any]]:
    """Search using Alpha Vantage API - process all results"""
    result_list = []
    
    try:
        # Step 1: Get symbol search results
        search_url = config.get_alpha_vantage_symbol_search_url(query)
        logger.debug(f"Alpha Vantage search URL: {search_url}")
        
        async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
            response = await client.get(search_url)
            response.raise_for_status()
            
            search_data = response.json()
            logger.debug(f"Alpha Vantage search response: {search_data}")
            
            # Check for rate limit response
            if "Information" in search_data and "rate limit" in search_data["Information"].lower():
                logger.warning(f"Alpha Vantage rate limit reached: {search_data['Information']}")
                return []
            
            # Extract best matches
            best_matches = search_data.get("bestMatches", [])
            if not best_matches:
                logger.info(f"No symbol matches found in Alpha Vantage for query: '{query}'")
                return []
            
            # Process all results (no limit)
            logger.info(f"Found {len(best_matches)} Alpha Vantage matches, processing all results")
            
            # Step 2: Get detailed information for each symbol
            for match in best_matches:
                symbol = match.get("1. symbol", "")
                match_score = float(match.get("9. matchScore", "0.0"))
                
                if not symbol:
                    continue
                
                try:
                    # Get company overview
                    overview_url = config.get_alpha_vantage_overview_url(symbol)
                    overview_response = await client.get(overview_url)
                    overview_response.raise_for_status()
                    
                    overview_data = overview_response.json()
                    logger.debug(f"Alpha Vantage overview response for {symbol}: {overview_data}")
                    
                    # Check for rate limit or empty response
                    if "Information" in overview_data and "rate limit" in overview_data.get("Information", "").lower():
                        logger.warning(f"Alpha Vantage rate limit reached for symbol '{symbol}'")
                        continue
                    
                    if not overview_data or "Symbol" not in overview_data:
                        logger.warning(f"No company data found for symbol: '{symbol}'")
                        continue
                    
                    # Create brand object
                    brand_obj = {
                        "id": overview_data.get("Symbol", symbol),
                        "name": overview_data.get("Name", ""),
                        "full_name": overview_data.get("Name", ""),
                        "industry": overview_data.get("Industry", ""),
                        "logo_url": config.get_logo_url(symbol),
                        "description": overview_data.get("Description", ""),
                        "confidence_score": match_score
                    }
                    
                    result_list.append(brand_obj)
                    logger.debug(f"Successfully created brand object for symbol: {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing Alpha Vantage symbol '{symbol}': {str(e)}")
                    continue
            
            logger.info(f"Alpha Vantage successfully created {len(result_list)} brand objects")
            return result_list
            
    except httpx.ConnectError as e:
        logger.error(f"Network connection error during Alpha Vantage search for '{query}': {str(e)}")
        return []
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error during Alpha Vantage search for '{query}': {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during Alpha Vantage search for '{query}': {str(e)}")
        return []


@router.get(
    "/{brand_id}/areas",
    response_model=AreaSuggestionsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Brand not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Get area suggestions for a brand",
    description="Retrieve suggested analysis areas for a specific brand using AI-powered analysis"
)
async def get_brand_areas(brand_id: str):
    """
    Get area suggestions for a specific brand.
    Uses Together.ai to generate relevant comparison categories.
    
    - **brand_id**: Unique identifier of the brand (stock symbol)
    """
    logger.info(f"GET /api/v1/brands/{brand_id}/areas")
    
    try:
        # Step 1: Check cache first
        logger.info(f"Checking areas cache for brand_id: '{brand_id}'")
        cached_result = areas_cache_service.get_cached_areas(brand_id)
        
        if cached_result:
            logger.info(f"Areas cache HIT! Returning cached results for brand_id: '{brand_id}'")
            # Return cached data in the expected format
            return JSONResponse(
                status_code=200,
                content={
                    "success": cached_result.get("success", True),
                    "data": cached_result.get("data", [])
                }
            )
        
        # Step 2: Cache miss - call Together.ai
        logger.info(f"Areas cache MISS - Fetching fresh data from Together.ai for brand_id: '{brand_id}'")
        areas_result = await _generate_areas_with_together_ai(brand_id)
        
        if areas_result and areas_result.get("success") and areas_result.get("data"):
            # Step 3: Cache the result
            logger.info(f"Together.ai success - Caching areas for brand_id: '{brand_id}' - {len(areas_result['data'])} areas found")
            areas_cache_service.cache_areas_response(brand_id, areas_result)
            
            # Step 4: Return the result
            logger.info(f"Areas retrieved successfully - Returned {len(areas_result['data'])} areas for brand_id: '{brand_id}'")
            return JSONResponse(status_code=200, content=areas_result)
        
        # Step 5: No results found
        logger.warning(f"No areas found for brand_id: '{brand_id}' from Together.ai")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "No Records Found",
                "details": f"No areas found for brand_id: '{brand_id}'"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for no records found)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during areas retrieval for brand_id '{brand_id}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Internal server error", "details": str(e)}
        )


async def _generate_areas_with_together_ai(brand_id: str) -> Optional[Dict[str, Any]]:
    """Generate areas using Together.ai"""
    
    try:
        # Prepare the prompt
        prompt = f"""You are an expert business analyst. Given a company represented by its stock symbol, identify the most relevant categories for comparing it with its direct competitors. The categories should reflect areas such as business performance, employee experience, public sentiment, and market position. Include max 10 records order by relevance_score dec

Input: {brand_id}

Output: Return the output as a JSON list of categories in below format. json should not include any additional attribute. Also output should include only json.

{{
  "success": true,
  "data": [
    {{
      "id": "self_service_portal",
      "name": "Self Service Portal",
      "description": "Online banking and customer self-service capabilities",
      "relevance_score": 0.92,
      "metrics": ["user_experience", "feature_completeness", "security"]
    }},
    {{
      "id": "employer_branding",
      "name": "Employer Branding",
      "description": "Company reputation as an employer",
      "relevance_score": 0.78,
      "metrics": ["employee_satisfaction", "compensation", "work_life_balance"]
    }}
  ]
}}"""
        
        # Prepare Together.ai API request
        url = config.get_together_ai_chat_url()
        headers = {
            "Authorization": f"Bearer {config.TOGETHER_AI_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": config.TOGETHER_AI_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        logger.debug(f"Together.ai request URL: {url}")
        logger.debug(f"Together.ai model: {config.TOGETHER_AI_MODEL}")
        
        # Make the API call
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Together.ai response: {result}")
            
            # Extract the generated content
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '').strip()
                
                logger.debug(f"Together.ai generated content: {content}")
                
                # Try to parse the JSON response
                try:
                    # Clean up the content (remove any markdown formatting)
                    json_content = content
                    if content.startswith('```json'):
                        json_content = content.replace('```json', '').replace('```', '').strip()
                    elif content.startswith('```'):
                        json_content = content.replace('```', '').strip()
                    
                    areas_data = json.loads(json_content)
                    
                    # Validate the structure
                    if isinstance(areas_data, dict) and "success" in areas_data and "data" in areas_data:
                        logger.info(f"Successfully parsed areas data from Together.ai for brand_id: '{brand_id}'")
                        return areas_data
                    else:
                        logger.warning(f"Invalid areas data structure from Together.ai for brand_id: '{brand_id}'")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Together.ai response for brand_id '{brand_id}': {str(e)}")
                    logger.error(f"Content that failed to parse: {content[:500]}...")
                    return None
            else:
                logger.warning(f"No choices found in Together.ai response for brand_id: '{brand_id}'")
                return None
                
    except httpx.HTTPStatusError as e:
        logger.error(f"Together.ai HTTP error for brand_id '{brand_id}': {e.response.status_code} - {e.response.text}")
        return None
    except httpx.ConnectError as e:
        logger.error(f"Together.ai connection error for brand_id '{brand_id}': {str(e)}")
        return None
    except httpx.TimeoutException as e:
        logger.error(f"Together.ai timeout error for brand_id '{brand_id}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Together.ai for brand_id '{brand_id}': {str(e)}")
        return None


@router.get(
    "/{brand_id}/competitors",
    response_model=CompetitorDiscoveryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Brand not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Get competitors for a brand",
    description="Discover competitors for a specific brand, optionally filtered by analysis area using AI-powered analysis"
)
async def get_brand_competitors(
    brand_id: str,
    area: Optional[str] = Query(None, description="Area ID to filter competitors by")
):
    """
    Get competitors for a specific brand, optionally filtered by area.
    Uses Together.ai to generate relevant competitors.
    
    - **brand_id**: Unique identifier of the brand (stock symbol)
    - **area**: Optional area ID to filter competitors by specific analysis area
    """
    logger.info(f"GET /api/v1/brands/{brand_id}/competitors - Area: {area}")
    
    try:
        # Step 1: Check cache first
        logger.info(f"Checking competitors cache for brand_id: '{brand_id}', area: '{area}'")
        cached_result = competitors_cache_service.get_cached_competitors(brand_id, area)
        
        if cached_result:
            logger.info(f"Competitors cache HIT! Returning cached results for brand_id: '{brand_id}', area: '{area}'")
            # Return cached data in the expected format
            return JSONResponse(
                status_code=200,
                content={
                    "success": cached_result.get("success", True),
                    "data": cached_result.get("data", [])
                }
            )
        
        # Step 2: Cache miss - call Together.ai
        logger.info(f"Competitors cache MISS - Fetching fresh data from Together.ai for brand_id: '{brand_id}', area: '{area}'")
        competitors_result = await _generate_competitors_with_together_ai(brand_id, area)
        
        if competitors_result and competitors_result.get("success") and competitors_result.get("data"):
            # Step 3: Cache the result
            logger.info(f"Together.ai success - Caching competitors for brand_id: '{brand_id}', area: '{area}' - {len(competitors_result['data'])} competitors found")
            competitors_cache_service.cache_competitors_response(brand_id, area, competitors_result)
            
            # Step 4: Return the result
            logger.info(f"Competitors retrieved successfully - Returned {len(competitors_result['data'])} competitors for brand_id: '{brand_id}'" + 
                       (f" in area: '{area}'" if area else ""))
            return JSONResponse(status_code=200, content=competitors_result)
        
        # Step 5: No results found
        logger.warning(f"No competitors found for brand_id: '{brand_id}', area: '{area}' from Together.ai")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "No Records Found",
                "details": f"No competitors found for brand_id: '{brand_id}'" + (f" in area: '{area}'" if area else "")
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for no records found)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during competitors retrieval for brand_id '{brand_id}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Internal server error", "details": str(e)}
        )


async def _generate_competitors_with_together_ai(brand_id: str, area_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Generate competitors using Together.ai"""
    
    try:
        # Prepare the prompt
        area_text = area_id if area_id else "General Business Competition"
        prompt = f"""You are an expert business analyst. Given a company represented by its stock symbol, identify the most relevant competitors along with symbol for comparing, The categories should reflect areas as input provided. Include max 10 records order by competition_level and relevance_score. here competition_level = Direct should be higher precedence. Then relevance_score should be desc order.

Input Company: {brand_id}
Input Category: {area_text}

Output: Return the output as a JSON list of categories in below format. json should not include any additional attribute. Also output should include only json.

{{
  "success": true,
  "data": [
    {{
      "id": "ACN",
      "name": "Accenture",
      "logo_url": "https://img.logo.dev/ticker/ACN?token={config.LOGO_DEV_API_KEY}",
      "industry": "IT Consulting",
      "relevance_score": 0.92,
      "competition_level": "direct",
      "symbol": "ACN"
    }}
  ]
}}"""
        
        # Prepare Together.ai API request
        url = config.get_together_ai_chat_url()
        headers = {
            "Authorization": f"Bearer {config.TOGETHER_AI_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": config.TOGETHER_AI_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        logger.debug(f"Together.ai request URL: {url}")
        logger.debug(f"Together.ai model: {config.TOGETHER_AI_MODEL}")
        
        # Make the API call
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Together.ai response: {result}")
            
            # Extract the generated content
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '').strip()
                
                logger.debug(f"Together.ai generated content: {content}")
                
                # Try to parse the JSON response
                try:
                    # Clean up the content (remove any markdown formatting)
                    json_content = content
                    if content.startswith('```json'):
                        json_content = content.replace('```json', '').replace('```', '').strip()
                    elif content.startswith('```'):
                        json_content = content.replace('```', '').strip()
                    
                    competitors_data = json.loads(json_content)
                    
                    # Validate the structure
                    if isinstance(competitors_data, dict) and "success" in competitors_data and "data" in competitors_data:
                        # Update logo URLs for each competitor using the configurable token
                        if "data" in competitors_data and isinstance(competitors_data["data"], list):
                            for competitor in competitors_data["data"]:
                                if "symbol" in competitor:
                                    competitor["logo_url"] = config.get_logo_url(competitor["symbol"])
                        
                        logger.info(f"Successfully parsed competitors data from Together.ai for brand_id: '{brand_id}', area: '{area_id}'")
                        return competitors_data
                    else:
                        logger.warning(f"Invalid competitors data structure from Together.ai for brand_id: '{brand_id}', area: '{area_id}'")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Together.ai response for brand_id '{brand_id}', area '{area_id}': {str(e)}")
                    logger.error(f"Content that failed to parse: {content[:500]}...")
                    return None
            else:
                logger.warning(f"No choices found in Together.ai response for brand_id: '{brand_id}', area: '{area_id}'")
                return None
                
    except httpx.HTTPStatusError as e:
        logger.error(f"Together.ai HTTP error for brand_id '{brand_id}', area '{area_id}': {e.response.status_code} - {e.response.text}")
        return None
    except httpx.ConnectError as e:
        logger.error(f"Together.ai connection error for brand_id '{brand_id}', area '{area_id}': {str(e)}")
        return None
    except httpx.TimeoutException as e:
        logger.error(f"Together.ai timeout error for brand_id '{brand_id}', area '{area_id}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Together.ai for brand_id '{brand_id}', area '{area_id}': {str(e)}")
        return None
