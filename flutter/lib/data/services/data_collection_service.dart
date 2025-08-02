import 'dart:io';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter/foundation.dart';
import '../services/brand_api_service.dart';

class DataCollectionService {
  // Use localhost for web, network IP for mobile devices
  static String get baseUrl => kIsWeb 
    ? 'http://localhost:8002/api/v1'
    : 'http://10.0.0.70:8002/api/v1';
  
  static String get analysisEngineUrl => kIsWeb 
    ? 'http://localhost:8003/api/v1'
    : 'http://10.0.0.70:8003/api/v1';
  static const Duration requestTimeout = Duration(minutes: 5);
  static const Duration pollingInterval = Duration(seconds: 8);
  
  late final Dio _dio;
  late final Dio _analysisEngineDio;
  static DataCollectionService? _instance;
  final _uuid = const Uuid();

  DataCollectionService._() {
    _dio = Dio(BaseOptions(
      baseUrl: DataCollectionService.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    _analysisEngineDio = Dio(BaseOptions(
      baseUrl: DataCollectionService.analysisEngineUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // Add interceptor for logging
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => print('[DataCollection] $obj'),
    ));

    _analysisEngineDio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => print('[AnalysisEngine] $obj'),
    ));
  }

  static DataCollectionService get instance {
    _instance ??= DataCollectionService._();
    return _instance!;
  }

  /// Start complete analysis workflow
  Future<ApiResult<AnalysisResult>> startAnalysis({
    required String brandId,
    required String competitorId,
    required String areaId,
    List<String>? sources,
    String? existingRequestId, // Optional: reuse existing request ID for retry
    Function(String)? onStatusUpdate,
  }) async {
    try {
      // Use existing request ID for retry, or generate new one for first attempt
      final requestId = existingRequestId ?? _uuid.v4();
      
      if (existingRequestId != null) {
        print('[DataCollection] Retrying with existing request ID: $requestId');
      } else {
        print('[DataCollection] Starting new analysis with request ID: $requestId');
      }
      
      onStatusUpdate?.call('Starting data collection...');
      
      // Step 1: Start data collection
      final collectResult = await _startDataCollection(
        requestId: requestId,
        brandId: brandId,
        competitorId: competitorId,
        areaId: areaId,
        sources: sources,
      );

      if (!collectResult.isSuccess) {
        return ApiResult.error(collectResult.error ?? 'Failed to start data collection');
      }

      // Step 2: Poll for completion
      final pollResult = await _pollForCompletion(requestId, onStatusUpdate);
      
      if (!pollResult.isSuccess) {
        return ApiResult.error(pollResult.error ?? 'Analysis polling failed');
      }

      final sharedData = pollResult.data!;
      
      // Step 3: Get analysis results
      onStatusUpdate?.call('Retrieving analysis results...');
      final analysisId = sharedData['analysisEngineId'] as String;
      final analysisResult = await _getAnalysisResults(analysisId);
      
      if (!analysisResult.isSuccess) {
        return ApiResult.error(analysisResult.error ?? 'Failed to get analysis results');
      }

      onStatusUpdate?.call('Analysis complete!');
      
      return ApiResult.success(AnalysisResult(
        requestId: requestId,
        analysisId: analysisId,
        data: analysisResult.data!,
        sharedData: sharedData,
      ));

    } catch (e) {
      return ApiResult.error('Unexpected error: $e');
    }
  }

  /// Start data collection job
  Future<ApiResult<Map<String, dynamic>>> _startDataCollection({
    required String requestId,
    required String brandId,
    required String competitorId,
    required String areaId,
    List<String>? sources,
  }) async {
    try {
      final requestData = <String, dynamic>{
        'request_id': requestId,
        'brand_id': brandId,
        'competitor_id': competitorId,
        'area_id': areaId,
      };

      // Add sources if provided, otherwise service will use defaults
      if (sources != null && sources.isNotEmpty) {
        requestData['sources'] = sources;
      }

      print('[DataCollection] Starting collection with request: $requestData');

      final response = await _dio.post('/collect', data: requestData);

      if (response.statusCode == 200) {
        final data = response.data;
        if (data['success'] == true) {
          print('[DataCollection] Collection started successfully');
          return ApiResult.success(data['data'] ?? {});
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

  /// Poll shared database until analysis is complete
  Future<ApiResult<Map<String, dynamic>>> _pollForCompletion(
    String requestId, 
    Function(String)? onStatusUpdate,
  ) async {
    final startTime = DateTime.now();
    
    while (DateTime.now().difference(startTime) < requestTimeout) {
      try {
        print('[DataCollection] Polling status for request: $requestId');
        
        final response = await _dio.get('/shared-data/$requestId');
        
        if (response.statusCode == 200) {
          final data = response.data;
          if (data['success'] == true) {
            final sharedData = data['data'] as Map<String, dynamic>;
            
            final dataCollectionStatus = sharedData['dataCollectionStatus'] ?? 'PENDING';
            final analysisEngineStatus = sharedData['analysisEngineStatus'] ?? 'PENDING';
            
            // Update status
            if (analysisEngineStatus == 'COMPLETED') {
              onStatusUpdate?.call('Analysis complete!');
              return ApiResult.success(sharedData);
            } else if (analysisEngineStatus == 'RUNNING') {
              onStatusUpdate?.call('Running AI analysis...');
            } else if (dataCollectionStatus == 'COMPLETED') {
              onStatusUpdate?.call('Data collection complete, starting analysis...');
            } else if (dataCollectionStatus == 'RUNNING') {
              onStatusUpdate?.call('Collecting data from multiple sources...');
            } else {
              onStatusUpdate?.call('Initializing analysis...');
            }
            
            // Check for errors
            if (dataCollectionStatus == 'FAILED' || analysisEngineStatus == 'FAILED') {
              return ApiResult.error('Analysis failed. Please try again.');
            }
            
          } else {
            return ApiResult.error('API returned success: false');
          }
        } else if (response.statusCode == 404) {
          onStatusUpdate?.call('Waiting for job initialization...');
        } else {
          return ApiResult.error('HTTP ${response.statusCode}: ${response.statusMessage}');
        }
        
        // Wait before next poll
        await Future.delayed(pollingInterval);
        
      } on DioException catch (e) {
        if (e.response?.statusCode == 404) {
          // Job not found yet, continue polling
          onStatusUpdate?.call('Waiting for job initialization...');
          await Future.delayed(pollingInterval);
          continue;
        }
        return _handleDioError(e);
      } catch (e) {
        return ApiResult.error('Polling error: $e');
      }
    }
    
    return ApiResult.error('Analysis timeout. The process took longer than expected.');
  }

  /// Get analysis results from analysis engine
  Future<ApiResult<Map<String, dynamic>>> _getAnalysisResults(String analysisId) async {
    try {
      print('[AnalysisEngine] Getting results for analysis: $analysisId');
      
      final response = await _analysisEngineDio.get('/analyze/$analysisId/status');
      
      if (response.statusCode == 200) {
        final data = response.data;
        if (data['success'] == true) {
          print('[AnalysisEngine] Results retrieved successfully');
          // Include all root-level fields from the API response
          final result = Map<String, dynamic>.from(data['data'] ?? {});
          
          // Add charts if available
          if (data['charts'] != null) {
            result['charts'] = data['charts'];
            print('[AnalysisEngine] Including ${(data['charts'] as List).length} charts in result');
          }
          
          // Add roadmap if available
          if (data['roadmap'] != null) {
            result['roadmap'] = data['roadmap'];
            print('[AnalysisEngine] Including roadmap in result');
          }
          
          // Add competitor_analysis if available
          if (data['competitor_analysis'] != null) {
            result['competitor_analysis'] = data['competitor_analysis'];
            print('[AnalysisEngine] Including competitor_analysis in result');
          }
          
          // Add improvement_areas if available
          if (data['improvement_areas'] != null) {
            result['improvement_areas'] = data['improvement_areas'];
            print('[AnalysisEngine] Including improvement_areas in result');
          }
          
          print('[AnalysisEngine] Final result keys: ${result.keys}');
          return ApiResult.success(result);
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

  /// Get report download URL
  Future<String?> getReportUrl(String analysisId, String reportType) async {
    try {
      // For PDF reports, we return the direct URL
      final url = '${DataCollectionService.analysisEngineUrl}/analyze/$analysisId/report?reportType=$reportType';
      print('[AnalysisEngine] Report URL generated: $url');
      return url;
    } catch (e) {
      print('[AnalysisEngine] Error generating report URL: $e');
      return null;
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
        return ApiResult.error('Unable to connect to data collection service. Please ensure services are running.');
      
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        if (statusCode == 400) {
          final responseData = e.response?.data;
          if (responseData is Map && responseData['detail'] != null) {
            return ApiResult.error(responseData['detail'].toString());
          }
          return ApiResult.error('Invalid request. Please check your input.');
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

  /// Check if services are healthy
  Future<bool> checkServicesHealth() async {
    try {
      // Check data collection service - health endpoint is at root level, not /api/v1/health
      final dataCollectionHealthUrl = kIsWeb 
        ? 'http://localhost:8002/health'
        : 'http://10.0.0.70:8002/health';
      final dataCollectionResponse = await Dio().get(dataCollectionHealthUrl, 
        options: Options(sendTimeout: const Duration(seconds: 5))
      );
      
      // Check analysis engine service - health endpoint is at root level, not /api/v1/health  
      final analysisEngineHealthUrl = kIsWeb 
        ? 'http://localhost:8003/health'
        : 'http://10.0.0.70:8003/health';
      final analysisEngineResponse = await Dio().get(analysisEngineHealthUrl,
        options: Options(sendTimeout: const Duration(seconds: 5))
      );
      
      return dataCollectionResponse.statusCode == 200 && 
             analysisEngineResponse.statusCode == 200;
    } catch (e) {
      print('[Services] Health check failed: $e');
      return false;
    }
  }
}

/// Analysis result wrapper
class AnalysisResult {
  final String requestId;
  final String analysisId;
  final Map<String, dynamic> data;
  final Map<String, dynamic> sharedData;

  AnalysisResult({
    required this.requestId,
    required this.analysisId,
    required this.data,
    required this.sharedData,
  });

  /// Get analysis data for charts and insights
  Map<String, dynamic>? get analysisData => data['analysis'];
  
  /// Get insights data
  Map<String, dynamic>? get insightsData => data['insights'];
  
  /// Get roadmap data
  List<dynamic>? get roadmapData => data['roadmap'];
  
  /// Get competitive analysis data
  Map<String, dynamic>? get competitiveAnalysis => data['competitive_analysis'];
  
  /// Check if specific data sections are available
  bool get hasAnalysis => analysisData != null;
  bool get hasInsights => insightsData != null;
  bool get hasRoadmap => roadmapData != null;
  bool get hasCompetitiveAnalysis => competitiveAnalysis != null;
}