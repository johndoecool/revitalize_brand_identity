import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/brand_model.dart';
import '../models/analysis_area_model.dart';
import '../models/competitor_model.dart';

class BrandApiService {
  static const String baseUrl = 'http://10.0.0.70:8001/api/v1';
  static const Duration cacheTimeout = Duration(minutes: 2); // For brand search
  static const Duration areasCacheTimeout = Duration(minutes: 5); // For areas
  static const Duration competitorsCacheTimeout = Duration(minutes: 3); // For competitors
  
  late final Dio _dio;
  static BrandApiService? _instance;

  BrandApiService._() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // Add minimal logging for errors only
    _dio.interceptors.add(LogInterceptor(
      requestBody: false,
      responseBody: false,
      logPrint: (obj) {
        // Suppress all logs - errors will still be handled via exceptions
      },
    ));
  }

  static BrandApiService get instance {
    _instance ??= BrandApiService._();
    return _instance!;
  }

  /// Search for brands with caching and uppercase conversion
  Future<ApiResult<List<BrandModel>>> searchBrands(String query, {int limit = 10}) async {
    try {
      // Convert query to uppercase as requested
      final upperQuery = query.toUpperCase();
      final cacheKey = 'brand_search_${upperQuery}_$limit';
      
      // Check cache first
      final cachedResult = await _getCachedData<List<BrandModel>>(
        cacheKey,
        cacheTimeout,
        (json) => (json as List).map((item) => BrandModel.fromJson(item)).toList(),
      );
      
      if (cachedResult.isSuccess) {
        return cachedResult;
      }
      
      final response = await _dio.post('/brands/search', data: {
        'query': upperQuery,
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        if (data['success'] == true) {
          final brands = (data['data'] as List)
              .map((item) => BrandModel.fromJson(item))
              .toList();
          
          // Sort by confidence score (highest first)
          brands.sort((a, b) => b.confidenceScore.compareTo(a.confidenceScore));
          
          // Cache the result
          await _cacheData(cacheKey, brands.map((b) => b.toJson()).toList());
          
          return ApiResult.success(brands);
        } else {
          return ApiResult.error('API returned success: false');
        }
      } else {
        return ApiResult.error('HTTP ${response.statusCode}: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResult.error('Unexpected error: $e');
    }
  }

  /// Get areas for a brand with caching
  Future<ApiResult<List<AnalysisAreaModel>>> getBrandAreas(String brandId) async {
    try {
      final cacheKey = 'brand_areas_$brandId';
      
      // Check cache first
      final cachedResult = await _getCachedData<List<AnalysisAreaModel>>(
        cacheKey,
        areasCacheTimeout,
        (json) => (json as List).map((item) => AnalysisAreaModel.fromJson(item)).toList(),
      );
      
      if (cachedResult.isSuccess) {
        return cachedResult;
      }
      
      final response = await _dio.get('/brands/$brandId/areas');

      if (response.statusCode == 200) {
        final data = response.data;
        if (data['success'] == true) {
          final areas = (data['data'] as List)
              .map((item) => AnalysisAreaModel.fromJson(item))
              .toList();
          
          // Sort by relevance score (highest first)
          areas.sort((a, b) => b.relevanceScore.compareTo(a.relevanceScore));
          
          // Cache the result
          await _cacheData(cacheKey, areas.map((a) => a.toJson()).toList());
          
          return ApiResult.success(areas);
        } else {
          return ApiResult.error('API returned success: false');
        }
      } else {
        return ApiResult.error('HTTP ${response.statusCode}: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResult.error('Unexpected error: $e');
    }
  }

  /// Get competitors for a brand with optional area filter
  Future<ApiResult<List<CompetitorModel>>> getBrandCompetitors(String brandId, {String? areaId}) async {
    try {
      final cacheKey = 'brand_competitors_${brandId}_${areaId ?? 'all'}';
      
      // Check cache first
      final cachedResult = await _getCachedData<List<CompetitorModel>>(
        cacheKey,
        competitorsCacheTimeout,
        (json) => (json as List).map((item) => CompetitorModel.fromJson(item)).toList(),
      );
      
      if (cachedResult.isSuccess) {
        return cachedResult;
      }
      
      final queryParams = areaId != null ? {'area': areaId} : <String, dynamic>{};
      final response = await _dio.get('/brands/$brandId/competitors', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final data = response.data;
        if (data['success'] == true) {
          final competitors = (data['data'] as List)
              .map((item) => CompetitorModel.fromJson(item))
              .toList();
          
          // Sort by competition level (direct first) then by relevance score
          competitors.sort((a, b) {
            // Direct competitors first
            if (a.isDirectCompetitor && !b.isDirectCompetitor) return -1;
            if (!a.isDirectCompetitor && b.isDirectCompetitor) return 1;
            // Then by relevance score (highest first)
            return b.relevanceScore.compareTo(a.relevanceScore);
          });
          
          // Cache the result
          await _cacheData(cacheKey, competitors.map((c) => c.toJson()).toList());
          
          return ApiResult.success(competitors);
        } else {
          return ApiResult.error('API returned success: false');
        }
      } else {
        return ApiResult.error('HTTP ${response.statusCode}: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResult.error('Unexpected error: $e');
    }
  }

  /// Generic method to get cached data
  Future<ApiResult<T>> _getCachedData<T>(
    String cacheKey,
    Duration timeout,
    T Function(dynamic) parser,
  ) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheData = prefs.getString(cacheKey);
      final cacheTimestamp = prefs.getInt('${cacheKey}_timestamp');

      if (cacheData != null && cacheTimestamp != null) {
        final now = DateTime.now().millisecondsSinceEpoch;
        final cachedTime = DateTime.fromMillisecondsSinceEpoch(cacheTimestamp);
        
        if (DateTime.now().difference(cachedTime) < timeout) {
          final parsedData = parser(jsonDecode(cacheData));
          return ApiResult.success(parsedData);
        }
      }
      
      return ApiResult.error('Cache miss or expired');
    } catch (e) {
      return ApiResult.error('Cache error: $e');
    }
  }

  /// Generic method to cache data
  Future<void> _cacheData(String cacheKey, dynamic data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(cacheKey, jsonEncode(data));
      await prefs.setInt('${cacheKey}_timestamp', DateTime.now().millisecondsSinceEpoch);
    } catch (e) {
      // Cache write failed - continue without caching
    }
  }

  /// Handle Dio errors with user-friendly messages
  ApiResult<T> _handleDioError<T>(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiResult.error('Connection timeout. Please check your internet connection.');
      
      case DioExceptionType.connectionError:
        return ApiResult.error('Unable to connect to brand service. Please ensure the service is running on localhost:8001.');
      
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        if (statusCode == 400) {
          final responseData = e.response?.data;
          if (responseData is Map && responseData['detail'] is Map) {
            final detail = responseData['detail'] as Map;
            return ApiResult.error(detail['details'] ?? detail['error'] ?? 'Bad request');
          }
          return ApiResult.error('No records found or invalid request.');
        } else if (statusCode == 500) {
          return ApiResult.error('Server error. Please try again later.');
        }
        return ApiResult.error('HTTP $statusCode error occurred.');
      
      case DioExceptionType.cancel:
        return ApiResult.error('Request was cancelled.');
      
      case DioExceptionType.unknown:
        if (e.error is SocketException) {
          return ApiResult.error('Network error. Please check your connection.');
        }
        return ApiResult.error('An unexpected error occurred: ${e.message}');
      
      default:
        return ApiResult.error('Network error occurred.');
    }
  }

  /// Clear all cache
  Future<void> clearCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys().where((key) => 
        key.startsWith('brand_search_') || 
        key.startsWith('brand_areas_') || 
        key.startsWith('brand_competitors_')
      ).toList();
      
      for (final key in keys) {
        await prefs.remove(key);
        await prefs.remove('${key}_timestamp');
      }
    } catch (e) {
      // Cache clear failed - continue
    }
  }
}

/// Generic API result wrapper
class ApiResult<T> {
  final bool isSuccess;
  final T? data;
  final String? error;

  ApiResult.success(this.data) : isSuccess = true, error = null;
  ApiResult.error(this.error) : isSuccess = false, data = null;
}