import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../../data/services/brand_api_service.dart';
import '../../data/models/brand_model.dart';
import '../../data/models/analysis_area_model.dart';
import '../../data/models/competitor_model.dart';
import 'glassmorphism_card.dart';
import 'api_error_dialog.dart';
import '../pages/analysis_page.dart';

class SetupTab extends StatefulWidget {
  final Function(String brandName, String selectedArea, String competitor)? onAnalysisLaunched;
  
  const SetupTab({
    Key? key,
    this.onAnalysisLaunched,
  }) : super(key: key);

  @override
  State<SetupTab> createState() => _SetupTabState();
}

class _SetupTabState extends State<SetupTab> {
  final TextEditingController _brandController = TextEditingController();
  final BrandApiService _apiService = BrandApiService.instance;
  
  // Brand search state
  List<BrandModel> _brandSuggestions = [];
  bool _showBrandSuggestions = false;
  bool _isLoadingBrands = false;
  BrandModel? _selectedBrand;
  Timer? _searchDebounce;
  
  // Error handling state
  Timer? _errorDebounce;
  String? _lastErrorQuery;
  int _consecutiveErrors = 0;
  DateTime? _lastErrorTime;
  
  // Error tracking for different operations
  DateTime? _lastAreasErrorTime;
  DateTime? _lastCompetitorsErrorTime;
  bool _hasSearchError = false;
  
  // Areas state
  List<AnalysisAreaModel> _analysisAreas = [];
  bool _isLoadingAreas = false;
  String? _selectedArea;
  
  // Competitors state
  List<CompetitorModel> _competitors = [];
  bool _isLoadingCompetitors = false;
  CompetitorModel? _selectedCompetitor;

  @override
  void dispose() {
    _brandController.dispose();
    _searchDebounce?.cancel();
    _errorDebounce?.cancel();
    super.dispose();
  }

  /// Search for brands with debouncing
  void _searchBrands(String query) {
    if (query.trim().isEmpty) {
      setState(() {
        _brandSuggestions.clear();
        _showBrandSuggestions = false;
        _selectedBrand = null;
        _hasSearchError = false;
      });
      _cancelAllPendingOperations();
      return;
    }

    // Cancel all pending operations when starting new search
    _cancelAllPendingOperations();
    
    // Set up new timer with 500ms delay
    _searchDebounce = Timer(const Duration(milliseconds: 500), () async {
      if (!mounted) return;
      
      setState(() {
        _isLoadingBrands = true;
        _showBrandSuggestions = true;
      });

      try {
        final result = await _apiService.searchBrands(query, limit: 5);
        
        if (!mounted) return;
        
        if (result.isSuccess && result.data != null) {
          setState(() {
            _brandSuggestions = result.data!;
            _isLoadingBrands = false;
          });
          // Reset error state on successful search
          _resetErrorState();
        } else {
          // Show error dialog with retry option
          _handleBrandSearchError(result.error ?? 'Unknown error', query);
        }
      } catch (e) {
        if (!mounted) return;
        _handleBrandSearchError('Network error: $e', query);
      }
    });
  }

  /// Handle brand search errors with smart debouncing
  void _handleBrandSearchError(String error, String query) {
    setState(() {
      _isLoadingBrands = false;
      _brandSuggestions.clear();
      _hasSearchError = true;
    });

    // Check if we should show this error
    if (!_shouldShowError(query)) {
      return;
    }

    // Cancel any pending error dialog
    _errorDebounce?.cancel();
    
    // Debounce error dialogs to prevent spam
    _errorDebounce = Timer(const Duration(milliseconds: 1500), () {
      if (!mounted) return;
      
      // Update error tracking
      _consecutiveErrors++;
      _lastErrorTime = DateTime.now();
      _lastErrorQuery = query;
      
      // Show error with appropriate message based on consecutive errors
      final title = _consecutiveErrors > 2 
          ? 'Repeated Search Issues' 
          : 'Brand Search Failed';
      
      final message = _consecutiveErrors > 2
          ? 'Multiple search attempts failed. Check your connection or try demo data.'
          : 'Unable to search for brands: $error';
      
      ApiErrorDialog.show(
        context: context,
        title: title,
        message: message,
        onRetry: () {
          _resetErrorState();
          // Use current text field content, not the original failed query
          final currentQuery = _brandController.text.trim();
          if (currentQuery.isNotEmpty) {
            _searchBrands(currentQuery);
          }
        },
        onUseDemoData: () {
          _resetErrorState();
          _useDemoBrands();
        },
      );
    });
  }

  /// Check if we should show an error dialog
  bool _shouldShowError(String query) {
    final now = DateTime.now();
    final currentFieldText = _brandController.text.trim();
    
    // Don't show error if the query doesn't match current field content
    // This prevents stale errors from old searches
    if (query != currentFieldText) {
      return false;
    }
    
    // Don't show error if it's the same query as last error and within 3 seconds
    if (_lastErrorQuery == query && 
        _lastErrorTime != null && 
        now.difference(_lastErrorTime!).inSeconds < 3) {
      return false;
    }
    
    // Don't show more than 3 errors in 10 seconds
    if (_consecutiveErrors >= 3 && 
        _lastErrorTime != null &&
        now.difference(_lastErrorTime!).inSeconds < 10) {
      return false;
    }
    
    return true;
  }

  /// Reset error tracking state
  void _resetErrorState() {
    _consecutiveErrors = 0;
    _lastErrorTime = null;
    _lastErrorQuery = null;
    _hasSearchError = false;
  }

  /// Cancel all pending operations (timers and error states)
  void _cancelAllPendingOperations() {
    _searchDebounce?.cancel();
    _errorDebounce?.cancel();
    setState(() {
      _hasSearchError = false;
    });
  }

  /// Use demo brands as fallback
  void _useDemoBrands() {
    setState(() {
      _brandSuggestions = [
        BrandModel(
          id: 'DEMO_OB',
          name: 'Oriental Bank',
          fullName: 'Oriental Bank',
          industry: 'Banking',
          logoUrl: '',
          description: 'Banking services in Puerto Rico',
          confidenceScore: 0.95,
        ),
        BrandModel(
          id: 'DEMO_CTSH',
          name: 'Cognizant',
          fullName: 'Cognizant Technology Solutions',
          industry: 'IT Services',
          logoUrl: '',
          description: 'Global IT consulting services',
          confidenceScore: 0.95,
        ),
      ];
      _showBrandSuggestions = true;
      _isLoadingBrands = false;
    });
  }

  /// Select a brand and fetch its areas
  void _selectBrand(BrandModel brand) {
    setState(() {
      _selectedBrand = brand;
      _brandController.text = brand.name;
      _showBrandSuggestions = false;
      _selectedArea = null; // Reset area selection
      _selectedCompetitor = null; // Reset competitor selection
    });

    // Hide keyboard
    FocusScope.of(context).unfocus();
    
    // Fetch areas for the selected brand
    _fetchBrandAreas(brand.id);
  }

  /// Fetch areas for a specific brand
  void _fetchBrandAreas(String brandId) async {
    if (!mounted) return;
    
    setState(() {
      _isLoadingAreas = true;
      _analysisAreas.clear();
    });

    try {
      final result = await _apiService.getBrandAreas(brandId);
      
      if (!mounted) return;
      
      if (result.isSuccess && result.data != null) {
        setState(() {
          _analysisAreas = result.data!;
          _isLoadingAreas = false;
        });
      } else {
        _handleAreasError(result.error ?? 'Unknown error', brandId);
      }
    } catch (e) {
      if (!mounted) return;
      _handleAreasError('Network error: $e', brandId);
    }
  }

  /// Handle areas fetch errors with debouncing
  void _handleAreasError(String error, String brandId) {
    setState(() {
      _isLoadingAreas = false;
    });

    // Don't show areas error if one was shown recently (within 2 seconds)
    final now = DateTime.now();
    if (_lastAreasErrorTime != null && 
        now.difference(_lastAreasErrorTime!).inSeconds < 2) {
      return;
    }

    _lastAreasErrorTime = now;

    ApiErrorDialog.show(
      context: context,
      title: 'Areas Loading Failed',
      message: 'Unable to load analysis areas: $error',
      onRetry: () => _fetchBrandAreas(brandId),
      onUseDemoData: () => _useDemoAreas(),
    );
  }

  /// Use demo areas as fallback
  void _useDemoAreas() {
    setState(() {
      _analysisAreas = [
        AnalysisAreaModel(
          id: 'self_service_portal',
          name: 'Self Service Portal',
          description: 'Online banking and customer self-service capabilities',
          relevanceScore: 0.92,
          metrics: ['user_experience', 'feature_completeness', 'security'],
        ),
        AnalysisAreaModel(
          id: 'employer_branding',
          name: 'Employer Branding',
          description: 'Company reputation as an employer',
          relevanceScore: 0.78,
          metrics: ['employee_satisfaction', 'compensation', 'work_life_balance'],
        ),
        AnalysisAreaModel(
          id: 'customer_experience',
          name: 'Customer Experience',
          description: 'Service quality and customer satisfaction',
          relevanceScore: 0.85,
          metrics: ['customer_retention', 'net_promoter_score', 'complaint_resolution'],
        ),
      ];
      _isLoadingAreas = false;
    });
  }

  /// Select an analysis area and fetch competitors
  void _selectArea(String areaId) {
    setState(() {
      _selectedArea = areaId;
      _selectedCompetitor = null; // Reset competitor selection
    });

    // Fetch competitors for the selected brand and area
    if (_selectedBrand != null) {
      _fetchCompetitors(_selectedBrand!.id, areaId);
    }
  }

  /// Fetch competitors for the selected brand and area
  void _fetchCompetitors(String brandId, String? areaId) async {
    if (!mounted) return;
    
    setState(() {
      _isLoadingCompetitors = true;
      _competitors.clear();
    });

    try {
      final result = await _apiService.getBrandCompetitors(brandId, areaId: areaId);
      
      if (!mounted) return;
      
      if (result.isSuccess && result.data != null) {
        setState(() {
          _competitors = result.data!;
          _isLoadingCompetitors = false;
        });
      } else {
        _handleCompetitorsError(result.error ?? 'Unknown error', brandId, areaId);
      }
    } catch (e) {
      if (!mounted) return;
      _handleCompetitorsError('Network error: $e', brandId, areaId);
    }
  }

  /// Handle competitors fetch errors with debouncing
  void _handleCompetitorsError(String error, String brandId, String? areaId) {
    setState(() {
      _isLoadingCompetitors = false;
    });

    // Don't show competitors error if one was shown recently (within 2 seconds)
    final now = DateTime.now();
    if (_lastCompetitorsErrorTime != null && 
        now.difference(_lastCompetitorsErrorTime!).inSeconds < 2) {
      return;
    }

    _lastCompetitorsErrorTime = now;

    ApiErrorDialog.show(
      context: context,
      title: 'Competitors Loading Failed',
      message: 'Unable to load competitors: $error',
      onRetry: () => _fetchCompetitors(brandId, areaId),
      onUseDemoData: () => _useDemoCompetitors(),
    );
  }

  /// Use demo competitors as fallback
  void _useDemoCompetitors() {
    setState(() {
      _competitors = [
        CompetitorModel(
          id: 'DEMO_BAC',
          name: 'Bank of America',
          logoUrl: '',
          industry: 'Banking',
          relevanceScore: 0.92,
          competitionLevel: 'direct',
          symbol: 'BAC',
        ),
        CompetitorModel(
          id: 'DEMO_JPM',
          name: 'JPMorgan Chase',
          logoUrl: '',
          industry: 'Banking',
          relevanceScore: 0.89,
          competitionLevel: 'direct',
          symbol: 'JPM',
        ),
      ];
      _isLoadingCompetitors = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildBrandInputSection(),
          const SizedBox(height: 24),
          _buildAnalysisAreaSection(),
          const SizedBox(height: 24),
          _buildCompetitorInputSection(),
          const SizedBox(height: 32),
          _buildLaunchButton(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildBrandInputSection() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Brand Name',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.glowBlue,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _hasSearchError 
                    ? AppColors.error.withOpacity(0.5) 
                    : AppColors.glassBorder,
                width: _hasSearchError ? 2 : 1,
              ),
              color: _hasSearchError 
                  ? AppColors.error.withOpacity(0.05)
                  : AppColors.glassBackground,
            ),
            child: TextField(
              controller: _brandController,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textPrimary,
              ),
              decoration: InputDecoration(
                hintText: 'Enter brand name (e.g., Oriental Bank, Cognizant)...',
                hintStyle: TextStyle(color: AppColors.textSecondary),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.all(16),
              ),
              onChanged: (value) {
                // Clear error state immediately when user starts typing
                if (_hasSearchError) {
                  setState(() {
                    _hasSearchError = false;
                  });
                }
                _searchBrands(value);
              },
              onTap: () {
                if (_brandController.text.isNotEmpty) {
                  setState(() {
                    _showBrandSuggestions = true;
                  });
                }
              },
            ),
          ),
          if (_showBrandSuggestions && (_isLoadingBrands || _brandSuggestions.isNotEmpty)) ...[
            const SizedBox(height: 12),
            _buildBrandSuggestions(),
          ],
        ],
      ),
    );
  }

  Widget _buildBrandSuggestions() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.glassBorder),
        color: AppColors.glassBackgroundStrong,
      ),
      child: _isLoadingBrands
          ? Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Leveraging advanced AI to find brands...',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            )
          : Column(
              children: _brandSuggestions.asMap().entries.map((entry) {
                final index = entry.key;
                final brand = entry.value;
                return Column(
                  children: [
                    if (index > 0) Divider(color: AppColors.glassBorder, height: 1),
                    _buildBrandSuggestionItem(brand),
                  ],
                );
              }).toList(),
            ),
    );
  }

  Widget _buildBrandSuggestionItem(BrandModel brand) {
    // Get color based on confidence level
    Color getConfidenceColor() {
      switch (brand.confidenceLevel) {
        case 'high':
          return Colors.green;
        case 'medium':
          return Colors.orange;
        case 'low':
          return Colors.red;
        default:
          return AppColors.textSecondary;
      }
    }

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _selectBrand(brand),
        child: ListTile(
          leading: brand.logoUrl.isNotEmpty
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Image.network(
                    brand.logoUrl,
                    width: 40,
                    height: 40,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return CircleAvatar(
                        backgroundColor: AppColors.glowBlue,
                        child: Text(
                          brand.name.isNotEmpty ? brand.name[0].toUpperCase() : '?',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      );
                    },
                  ),
                )
              : CircleAvatar(
                  backgroundColor: AppColors.glowBlue,
                  child: Text(
                    brand.name.isNotEmpty ? brand.name[0].toUpperCase() : '?',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
          title: Row(
            children: [
              Expanded(
                child: Text(
                  brand.name,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
              // Confidence indicator
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: getConfidenceColor().withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(
                    color: getConfidenceColor().withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Text(
                  '${brand.confidencePercentage}%',
                  style: TextStyle(
                    color: getConfidenceColor(),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          subtitle: Text(
            '${brand.industry} • ${brand.id}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAnalysisAreaSection() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Select Analysis Area',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.glowBlue,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: AppColors.glowPurple.withOpacity(0.2),
                  border: Border.all(color: AppColors.glowPurple.withOpacity(0.5)),
                ),
                child: Text(
                  'Maximum 1',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.glowPurple,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _selectedBrand == null
              ? Container(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Icon(
                        Icons.search_rounded,
                        size: 48,
                        color: AppColors.textSecondary.withOpacity(0.5),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Select a brand first to discover strategic areas',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.textSecondary,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                )
              : _isLoadingAreas
                  ? Container(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'Discovering strategic areas...',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    )
                  : _analysisAreas.isEmpty
                      ? Container(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            children: [
                              Icon(
                                Icons.error_outline_rounded,
                                size: 48,
                                color: Colors.orange,
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'No analysis areas found for this brand',
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        )
                      : _buildAnalysisAreaGrid(),
        ],
      ),
    );
  }

  Widget _buildAnalysisAreaGrid() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: MediaQuery.of(context).size.width < 600 ? 1 : 2,
        childAspectRatio: MediaQuery.of(context).size.width < 600 ? 4.0 : 3.5,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: _analysisAreas.length,
      itemBuilder: (context, index) {
        final area = _analysisAreas[index];
        final isSelected = _selectedArea == area.id;
        
        // Get color based on relevance level
        Color getRelevanceColor() {
          switch (area.relevanceLevel) {
            case 'high':
              return AppColors.glowBlue;
            case 'medium':
              return AppColors.glowPurple;
            case 'low':
              return Colors.orange;
            default:
              return AppColors.textSecondary;
          }
        }
        
        return GestureDetector(
          onTap: () {
            if (isSelected) {
              setState(() {
                _selectedArea = null;
                _selectedCompetitor = null;
              });
            } else {
              _selectArea(area.id);
            }
          },
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected 
                    ? getRelevanceColor()
                    : AppColors.glassBorder,
                width: isSelected ? 2 : 1,
              ),
              color: isSelected 
                  ? getRelevanceColor().withOpacity(0.1)
                  : AppColors.glassBackground,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color: getRelevanceColor().withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: getRelevanceColor().withOpacity(0.3),
                        ),
                      ),
                      child: Icon(
                        Icons.analytics_rounded,
                        color: getRelevanceColor(),
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            area.name,
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                              color: isSelected ? getRelevanceColor() : AppColors.textPrimary,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                decoration: BoxDecoration(
                                  color: getRelevanceColor().withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                child: Text(
                                  '${area.relevancePercentage}%',
                                  style: TextStyle(
                                    color: getRelevanceColor(),
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 6),
                              Text(
                                'relevance',
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 10,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    if (isSelected)
                      Icon(
                        Icons.check_circle,
                        color: getRelevanceColor(),
                        size: 20,
                      ),
                  ],
                ),
                const SizedBox(height: 6),
                Expanded(
                  child: Text(
                    area.description,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.3,
                    ),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCompetitorInputSection() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Competitor',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.glowBlue,
            ),
          ),
          const SizedBox(height: 12),
          
          // Show different states based on data availability
          if (_selectedBrand == null || _selectedArea == null)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.glassBorder),
                color: AppColors.glassBackground,
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.people_outline_rounded,
                    size: 48,
                    color: AppColors.textSecondary.withOpacity(0.5),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Select a brand and area to identify key competitors',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            )
          else if (_isLoadingCompetitors)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.glassBorder),
                color: AppColors.glassBackground,
              ),
              child: Column(
                children: [
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.glowBlue),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Identifying key competitors...',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            )
          else if (_competitors.isEmpty)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.glassBorder),
                color: AppColors.glassBackground,
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.error_outline_rounded,
                    size: 48,
                    color: Colors.orange,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'No competitors found for this combination',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            )
          else
            // Competitor selection button with custom popup
            GestureDetector(
              onTap: () => _showCompetitorSelectionModal(),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.glassBorder),
                  color: AppColors.glassBackground,
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: _selectedCompetitor != null
                          ? Row(
                              children: [
                                // Logo or initial
                                _selectedCompetitor!.logoUrl.isNotEmpty
                                    ? ClipRRect(
                                        borderRadius: BorderRadius.circular(12),
                                        child: Image.network(
                                          _selectedCompetitor!.logoUrl,
                                          width: 24,
                                          height: 24,
                                          fit: BoxFit.cover,
                                          errorBuilder: (context, error, stackTrace) {
                                            return CircleAvatar(
                                              radius: 12,
                                              backgroundColor: AppColors.glowBlue.withOpacity(0.2),
                                              child: Text(
                                                _selectedCompetitor!.name.isNotEmpty 
                                                    ? _selectedCompetitor!.name[0].toUpperCase() 
                                                    : '?',
                                                style: TextStyle(
                                                  color: AppColors.glowBlue,
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 10,
                                                ),
                                              ),
                                            );
                                          },
                                        ),
                                      )
                                    : CircleAvatar(
                                        radius: 12,
                                        backgroundColor: AppColors.glowBlue.withOpacity(0.2),
                                        child: Text(
                                          _selectedCompetitor!.name.isNotEmpty 
                                              ? _selectedCompetitor!.name[0].toUpperCase() 
                                              : '?',
                                          style: TextStyle(
                                            color: AppColors.glowBlue,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 10,
                                          ),
                                        ),
                                      ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        _selectedCompetitor!.name,
                                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                          fontWeight: FontWeight.w600,
                                          color: AppColors.textPrimary,
                                        ),
                                      ),
                                      Text(
                                        '${_selectedCompetitor!.industry} • ${_selectedCompetitor!.relevancePercentage}% relevance',
                                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: AppColors.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            )
                          : Text(
                              'Select a competitor...',
                              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                    ),
                    Icon(
                      Icons.keyboard_arrow_down,
                      color: AppColors.textSecondary,
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  /// Show competitor selection modal
  void _showCompetitorSelectionModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      isDismissible: true,
      enableDrag: true,
      builder: (context) => BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: BoxDecoration(
          color: AppColors.darkBackground.withOpacity(0.95),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(24),
            topRight: Radius.circular(24),
          ),
          border: Border.all(color: AppColors.glowBlue.withOpacity(0.3), width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 20,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: Column(
          children: [
            // Handle bar
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 50,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.glowBlue.withOpacity(0.4),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
              child: Row(
                children: [
                  Text(
                    'Select Competitor',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const Spacer(),
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.glassBackground,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppColors.glassBorder),
                      ),
                      child: Icon(
                        Icons.close,
                        size: 20,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            Container(
              height: 1,
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.transparent,
                    AppColors.glowBlue.withOpacity(0.3),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
            
            // Competitors list
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
                itemCount: _competitors.length,
                itemBuilder: (context, index) {
                  final competitor = _competitors[index];
                  final isSelected = _selectedCompetitor?.id == competitor.id;
                  
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        _selectedCompetitor = competitor;
                      });
                      Navigator.pop(context);
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        gradient: isSelected 
                            ? LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  AppColors.glowBlue.withOpacity(0.2),
                                  AppColors.glowPurple.withOpacity(0.1),
                                ],
                              )
                            : LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  AppColors.glassBackground,
                                  AppColors.glassBackground.withOpacity(0.5),
                                ],
                              ),
                        border: Border.all(
                          color: isSelected 
                              ? AppColors.glowBlue.withOpacity(0.6)
                              : AppColors.glassBorder,
                          width: isSelected ? 2 : 1,
                        ),
                        boxShadow: [
                          if (isSelected) ...[
                            BoxShadow(
                              color: AppColors.glowBlue.withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                            BoxShadow(
                              color: AppColors.glowBlue.withOpacity(0.1),
                              blurRadius: 20,
                              offset: const Offset(0, 8),
                            ),
                          ] else ...[
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ],
                      ),
                      child: _buildCompetitorListItem(competitor),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
        ),
      ),
    );
  }

  Widget _buildCompetitorListItem(CompetitorModel competitor) {
    // Get color based on relevance level
    Color getRelevanceColor() {
      switch (competitor.relevanceLevel) {
        case 'high':
          return AppColors.glowGreen;
        case 'medium':
          return AppColors.glowBlue;
        case 'low':
          return Colors.orange;
        default:
          return AppColors.textSecondary;
      }
    }

    // Get competition level color with better contrast
    Color getCompetitionLevelColor() {
      switch (competitor.competitionLevel.toLowerCase()) {
        case 'direct':
          return AppColors.glowRed;
        case 'indirect':
          return AppColors.glowBlue; // Changed from purple to blue for better visibility
        default:
          return AppColors.textSecondary;
      }
    }

    return Row(
      children: [
        // Enhanced logo with gradient border
        Container(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                getRelevanceColor().withOpacity(0.3),
                getRelevanceColor().withOpacity(0.1),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: getRelevanceColor().withOpacity(0.2),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          padding: const EdgeInsets.all(2),
          child: competitor.logoUrl.isNotEmpty
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(22),
                  child: Image.network(
                    competitor.logoUrl,
                    width: 44,
                    height: 44,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return CircleAvatar(
                        radius: 22,
                        backgroundColor: AppColors.glassBackground,
                        child: Text(
                          competitor.name.isNotEmpty ? competitor.name[0].toUpperCase() : '?',
                          style: TextStyle(
                            color: getRelevanceColor(),
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      );
                    },
                  ),
                )
              : CircleAvatar(
                  radius: 22,
                  backgroundColor: AppColors.glassBackground,
                  child: Text(
                    competitor.name.isNotEmpty ? competitor.name[0].toUpperCase() : '?',
                    style: TextStyle(
                      color: getRelevanceColor(),
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
        ),
        
        const SizedBox(width: 16),
        
        // Name and details
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Company name and competition level
              Row(
                children: [
                  Expanded(
                    child: Text(
                      competitor.name,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  // Enhanced competition level badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          getCompetitionLevelColor().withOpacity(0.3), // Increased opacity for better visibility
                          getCompetitionLevelColor().withOpacity(0.2), // Increased opacity for better visibility
                        ],
                      ),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: getCompetitionLevelColor().withOpacity(0.6), // Increased border opacity
                        width: 1.5, // Slightly thicker border
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: getCompetitionLevelColor().withOpacity(0.3), // Stronger shadow
                          blurRadius: 4,
                          offset: const Offset(0, 1),
                        ),
                      ],
                    ),
                    child: Text(
                      competitor.competitionLevel.toUpperCase(),
                      style: TextStyle(
                        color: getCompetitionLevelColor(),
                        fontSize: 11,
                        fontWeight: FontWeight.w800, // Increased font weight for better visibility
                        letterSpacing: 0.5,
                        shadows: [
                          // Add text shadow for better contrast against background
                          Shadow(
                            color: Colors.black.withOpacity(0.3),
                            offset: const Offset(0, 1),
                            blurRadius: 2,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              // Industry and relevance information
              Row(
                children: [
                  Expanded(
                    child: Text(
                      competitor.industry,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  Text(
                    '${competitor.relevancePercentage}%',
                    style: TextStyle(
                      color: getRelevanceColor(),
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              // Enhanced relevance progress bar
              Row(
                children: [
                  Text(
                    'Relevance',
                    style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 4,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(2),
                        color: AppColors.glassBorder,
                      ),
                      child: FractionallySizedBox(
                        alignment: Alignment.centerLeft,
                        widthFactor: competitor.relevanceScore,
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(2),
                            gradient: LinearGradient(
                              colors: [
                                getRelevanceColor(),
                                getRelevanceColor().withOpacity(0.7),
                              ],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: getRelevanceColor().withOpacity(0.3),
                                blurRadius: 2,
                                offset: const Offset(0, 1),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLaunchButton() {
    final canLaunch = _selectedBrand != null && 
                     _selectedArea != null && 
                     _selectedCompetitor != null;
    
    // Debug info
    
    return Column(
      children: [
        // Debug info card
        if (!canLaunch)
          Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: AppColors.glowPurple.withOpacity(0.1),
              border: Border.all(color: AppColors.glowPurple.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                Text(
                  '📋 Required Steps:',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: AppColors.glowPurple,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                if (_selectedBrand == null)
                  Text('• Select a brand', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                if (_selectedArea == null)
                  Text('• Select analysis area', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                if (_selectedCompetitor == null)
                  Text('• Select a competitor', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
              ],
            ),
          ),
        
        Center(
          child: GlassmorphismButton(
            onPressed: canLaunch ? _launchAnalysis : () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Please complete all required fields'),
                  backgroundColor: AppColors.glowPurple,
                ),
              );
            },
            width: double.infinity,
            height: 64,
            backgroundColor: canLaunch 
                ? AppColors.glowBlue.withOpacity(0.2)
                : AppColors.glassBackground,
            borderColor: canLaunch 
                ? AppColors.glowBlue
                : AppColors.glassBorder,
            isEnabled: canLaunch,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  '🚀',
                  style: TextStyle(fontSize: 24),
                ),
                const SizedBox(width: 12),
                Text(
                  'LAUNCH ANALYSIS',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: canLaunch ? AppColors.glowBlue : AppColors.textSecondary,
                    letterSpacing: 1.2,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _launchAnalysis() {
    if (_selectedBrand == null || _selectedArea == null || _selectedCompetitor == null) {
      return;
    }
    
    final selectedAreaData = _analysisAreas.firstWhere(
      (area) => area.id == _selectedArea,
      orElse: () => AnalysisAreaModel(
        id: _selectedArea!,
        name: 'Selected Area',
        description: 'Analysis area',
      ),
    );
    
    
    // Call the callback if provided
    if (widget.onAnalysisLaunched != null) {
      widget.onAnalysisLaunched!(
        _selectedBrand!.name,
        selectedAreaData.name,
        _selectedCompetitor!.name,
      );
    } else {
      // Fallback: Navigate to separate analysis page if no callback
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => AnalysisPage(
            industryId: _selectedArea!,
            industryTitle: '${_selectedBrand!.name} vs ${_selectedCompetitor!.name}',
            colors: BrandColorScheme( // Using a default color scheme
              primary: AppColors.glowBlue,
              secondary: AppColors.glowPurple,
              accent: AppColors.textPrimary,
            ),
          ),
        ),
      );
    }
  }

}