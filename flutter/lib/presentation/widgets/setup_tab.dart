import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import 'glassmorphism_card.dart';
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
  final TextEditingController _competitorController = TextEditingController();
  String? _selectedArea;
  bool _showSuggestions = false;
  
  final List<AnalysisArea> _analysisAreas = [
    AnalysisArea(
      id: 'self-service',
      icon: '🏦',
      title: 'Self Service Portal',
      description: 'Digital banking capabilities, user experience, mobile app features',
      colors: AppColors.banking,
    ),
    AnalysisArea(
      id: 'employer-choice',
      icon: '👥',
      title: 'Employer of Choice',
      description: 'Work culture, compensation, career growth, work-life balance',
      colors: AppColors.tech,
    ),
    AnalysisArea(
      id: 'customer-experience',
      icon: '⭐',
      title: 'Customer Experience',
      description: 'Service quality, support responsiveness, customer satisfaction',
      colors: AppColors.healthcare,
    ),
    AnalysisArea(
      id: 'innovation',
      icon: '💡',
      title: 'Innovation Leadership',
      description: 'R&D investment, product innovation, technology adoption',
      colors: AppColors.tech,
    ),
    AnalysisArea(
      id: 'sustainability',
      icon: '🌱',
      title: 'Sustainability',
      description: 'Environmental impact, CSR initiatives, ESG compliance',
      colors: AppColors.healthcare,
    ),
    AnalysisArea(
      id: 'market-position',
      icon: '📈',
      title: 'Market Position',
      description: 'Market share, brand recognition, competitive advantage',
      colors: AppColors.banking,
    ),
  ];

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
              border: Border.all(color: AppColors.glassBorder),
              color: AppColors.glassBackground,
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
                setState(() {
                  _showSuggestions = value.isNotEmpty;
                });
              },
              onTap: () {
                setState(() {
                  _showSuggestions = _brandController.text.isNotEmpty;
                });
              },
            ),
          ),
          if (_showSuggestions && _brandController.text.isNotEmpty) ...[
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
      child: Column(
        children: [
          _buildSuggestionItem('OB', 'Oriental Bank', 'Banking • Puerto Rico'),
          Divider(color: AppColors.glassBorder, height: 1),
          _buildSuggestionItem('C', 'Cognizant', 'IT Services • Global'),
        ],
      ),
    );
  }

  Widget _buildSuggestionItem(String logo, String name, String subtitle) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          setState(() {
            _brandController.text = name;
            _showSuggestions = false;
            // Hide suggestions after selection by clearing focus
            FocusScope.of(context).unfocus();
          });
        },
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: AppColors.glowBlue,
            child: Text(
              logo,
              style: TextStyle(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          title: Text(
            name,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          subtitle: Text(
            subtitle,
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
          _buildAnalysisAreaGrid(),
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
        childAspectRatio: MediaQuery.of(context).size.width < 600 ? 4 : 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: _analysisAreas.length,
      itemBuilder: (context, index) {
        final area = _analysisAreas[index];
        final isSelected = _selectedArea == area.id;
        
        return GestureDetector(
          onTap: () {
            setState(() {
              _selectedArea = isSelected ? null : area.id;
            });
          },
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected 
                    ? area.colors.primary 
                    : AppColors.glassBorder,
                width: isSelected ? 2 : 1,
              ),
              color: isSelected 
                  ? area.colors.primary.withOpacity(0.1)
                  : AppColors.glassBackground,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      area.icon,
                      style: TextStyle(fontSize: 24),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        area.title,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: isSelected ? area.colors.primary : AppColors.textPrimary,
                        ),
                      ),
                    ),
                    if (isSelected)
                      Icon(
                        Icons.check_circle,
                        color: area.colors.primary,
                        size: 20,
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  area.description,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary,
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
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.glassBorder),
              color: AppColors.glassBackground,
            ),
            child: TextField(
              controller: _competitorController,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textPrimary,
              ),
              decoration: InputDecoration(
                hintText: 'Select or enter competitor...',
                hintStyle: TextStyle(color: AppColors.textSecondary),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.all(16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLaunchButton() {
    final canLaunch = _brandController.text.isNotEmpty && 
                     _selectedArea != null && 
                     _competitorController.text.isNotEmpty;
    
    // Debug info
    print('Launch button state:');
    print('  Brand: "${_brandController.text}" (${_brandController.text.isNotEmpty})');
    print('  Area: $_selectedArea (${_selectedArea != null})');
    print('  Competitor: "${_competitorController.text}" (${_competitorController.text.isNotEmpty})');
    print('  Can launch: $canLaunch');
    
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
                if (_brandController.text.isEmpty)
                  Text('• Enter brand name', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                if (_selectedArea == null)
                  Text('• Select analysis area', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                if (_competitorController.text.isEmpty)
                  Text('• Enter competitor name', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
              ],
            ),
          ),
        
        Center(
          child: GlassmorphismButton(
            onPressed: canLaunch ? _launchAnalysis : () {
              print('Button pressed but launch disabled');
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
    print('Launching analysis...');
    print('  Brand: ${_brandController.text}');
    print('  Area: $_selectedArea');
    print('  Competitor: ${_competitorController.text}');
    
    final selectedAreaData = _analysisAreas.firstWhere(
      (area) => area.id == _selectedArea,
    );
    
    print('  Selected area data: ${selectedAreaData.title}');
    
    // Call the callback if provided
    if (widget.onAnalysisLaunched != null) {
      widget.onAnalysisLaunched!(
        _brandController.text,
        selectedAreaData.title,
        _competitorController.text,
      );
    } else {
      // Fallback: Navigate to separate analysis page if no callback
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => AnalysisPage(
            industryId: _selectedArea!,
            industryTitle: '${_brandController.text} vs ${_competitorController.text}',
            colors: selectedAreaData.colors,
          ),
        ),
      ).then((_) {
        print('Returned from analysis page');
      });
    }
  }

  @override
  void dispose() {
    _brandController.dispose();
    _competitorController.dispose();
    super.dispose();
  }
}

class AnalysisArea {
  final String id;
  final String icon;
  final String title;
  final String description;
  final BrandColorScheme colors;
  
  AnalysisArea({
    required this.id,
    required this.icon,
    required this.title,
    required this.description,
    required this.colors,
  });
}