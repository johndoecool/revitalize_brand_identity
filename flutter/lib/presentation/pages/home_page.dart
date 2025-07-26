import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../widgets/glassmorphism_card.dart';
import 'analysis_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  String selectedIndustry = AppConstants.industryBanking;
  
  final List<IndustryDemo> industryDemos = [
    IndustryDemo(
      id: AppConstants.industryBanking,
      title: '🏦 Banking',
      subtitle: 'Oriental Bank vs Banco Popular',
      description: 'Self Service Portal Comparison',
      colors: AppColors.banking,
    ),
    IndustryDemo(
      id: AppConstants.industryTech,
      title: '💻 Technology', 
      subtitle: 'Microsoft vs Google',
      description: 'Employer Branding Analysis',
      colors: AppColors.tech,
    ),
    IndustryDemo(
      id: AppConstants.industryHealthcare,
      title: '🏥 Healthcare',
      subtitle: 'Pfizer vs Moderna', 
      description: 'Product Innovation Study',
      colors: AppColors.healthcare,
    ),
  ];

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: AppConstants.longAnimation,
      vsync: this,
    );
    
    _slideController = AnimationController(
      duration: AppConstants.mediumAnimation,
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutBack,
    ));
    
    // Start animations
    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.darkBackground,
              Color(0xFF1a1f3a),
              AppColors.darkBackground,
            ],
          ),
        ),
        child: Stack(
          children: [
            // Animated background orbs
            _buildAnimatedBackground(),
            
            // Main content
            SafeArea(
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SlideTransition(
                  position: _slideAnimation,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(AppConstants.defaultPadding),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildHeader(),
                        SizedBox(height: MediaQuery.of(context).size.width < 600 ? 24 : 32),
                        _buildWelcomeCard(),
                        SizedBox(height: MediaQuery.of(context).size.width < 600 ? 24 : 32),
                        _buildIndustrySelector(),
                        SizedBox(height: MediaQuery.of(context).size.width < 600 ? 24 : 32),
                        _buildStartAnalysisButton(),
                        SizedBox(height: MediaQuery.of(context).size.width < 600 ? 24 : 32),
                        _buildFooter(),
                        const SizedBox(height: 32), // Extra bottom padding for small screens
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnimatedBackground() {
    return Stack(
      children: [
        // Floating orb 1
        Positioned(
          top: 100,
          left: -50,
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.glowBlue.withOpacity(0.1),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
        
        // Floating orb 2
        Positioned(
          top: 300,
          right: -50,
          child: Container(
            width: 150,
            height: 150,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.glowPurple.withOpacity(0.1),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
        
        // Floating orb 3
        Positioned(
          bottom: 100,
          left: 50,
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.glowGreen.withOpacity(0.1),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          AppConstants.appName,
          style: Theme.of(context).textTheme.displayLarge?.copyWith(
            fontWeight: FontWeight.w700,
            fontSize: MediaQuery.of(context).size.width < 600 ? 28 : null,
            foreground: Paint()
              ..shader = AppColors.primaryGradient.createShader(
                const Rect.fromLTWH(0, 0, 200, 70),
              ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Powered by ${AppConstants.organizationName}',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildWelcomeCard() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  gradient: AppColors.accentGradient,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.analytics_outlined,
                  color: AppColors.textPrimary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Brand Intelligence Analysis',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'Compare brands, analyze reputation, and gain competitive insights',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.glassBackgroundStrong,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.glassBorder),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: AppColors.glowBlue,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Select an industry demo below to see our AI-powered brand analysis in action',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIndustrySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Choose Industry Demo',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        ...industryDemos.map((demo) => _buildIndustryCard(demo)).toList(),
      ],
    );
  }

  Widget _buildIndustryCard(IndustryDemo demo) {
    final isSelected = selectedIndustry == demo.id;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          selectedIndustry = demo.id;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        child: GlassmorphismCard(
          backgroundColor: isSelected 
              ? demo.colors.primary.withOpacity(0.1)
              : AppColors.glassBackground,
          borderColor: isSelected 
              ? demo.colors.primary
              : AppColors.glassBorder,
          child: Row(
            children: [
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: demo.colors.primary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: demo.colors.primary.withOpacity(0.5),
                  ),
                ),
                child: Center(
                  child: Text(
                    demo.title.split(' ')[0], // Extract emoji
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      demo.title,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: isSelected ? demo.colors.primary : AppColors.textPrimary,
                      ),
                    ),
                    Text(
                      demo.subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      demo.description,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              if (isSelected)
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: demo.colors.primary,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.check,
                    color: AppColors.textPrimary,
                    size: 16,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStartAnalysisButton() {
    final selectedDemo = industryDemos.firstWhere((demo) => demo.id == selectedIndustry);
    
    return GlassmorphismButton(
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => AnalysisPage(
              industryId: selectedDemo.id,
              industryTitle: selectedDemo.title,
              colors: selectedDemo.colors,
            ),
          ),
        );
      },
      width: double.infinity,
      height: 56,
      backgroundColor: selectedDemo.colors.primary.withOpacity(0.2),
      borderColor: selectedDemo.colors.primary,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.play_arrow,
            color: selectedDemo.colors.primary,
            size: 24,
          ),
          const SizedBox(width: 8),
          Text(
            'Launch Analysis',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: selectedDemo.colors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return GlassmorphismCard(
      padding: const EdgeInsets.all(12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.code,
            color: AppColors.textSecondary,
            size: 16,
          ),
          const SizedBox(width: 8),
          Text(
            'Built with Flutter for ${AppConstants.organizationName}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

class IndustryDemo {
  final String id;
  final String title;
  final String subtitle;
  final String description;
  final BrandColorScheme colors;

  IndustryDemo({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.description,
    required this.colors,
  });
}