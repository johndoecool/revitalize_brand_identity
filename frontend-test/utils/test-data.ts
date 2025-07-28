/**
 * Test data constants and selectors for Brand Intelligence Hub
 */

export const TestData = {
  // Application constants
  APP_TITLE: 'Brand Intelligence Hub',
  BASE_URL: 'http://localhost:8080',

  // Industry types
  INDUSTRIES: {
    BANKING: 'banking',
    TECH: 'tech', 
    HEALTHCARE: 'healthcare'
  },

  // Industry demo data
  INDUSTRY_DEMOS: {
    BANKING: {
      title: '🏦 Banking',
      subtitle: 'Oriental Bank vs Banco Popular',
      description: 'Self Service Portal Comparison'
    },
    TECH: {
      title: '💻 Technology',
      subtitle: 'Microsoft vs Google', 
      description: 'Employer Branding Analysis'
    },
    HEALTHCARE: {
      title: '🏥 Healthcare',
      subtitle: 'Pfizer vs Moderna',
      description: 'Product Innovation Study'
    }
  },

  // Tab names
  TABS: {
    SETUP: 'Setup',
    ANALYSIS: 'Analysis', 
    INSIGHTS: 'Insights',
    ROADMAP: 'Roadmap',
    REPORT: 'Report'
  },

  // Sample brand names for testing
  SAMPLE_BRANDS: {
    BANKING: ['Oriental Bank', 'Banco Popular', 'FirstBank'],
    TECH: ['Microsoft', 'Google', 'Apple', 'Amazon'],
    HEALTHCARE: ['Pfizer', 'Moderna', 'Johnson & Johnson']
  },

  // Analysis areas
  ANALYSIS_AREAS: [
    'Brand Reputation',
    'Customer Experience', 
    'Digital Innovation',
    'Market Position',
    'Employee Satisfaction',
    'Product Quality',
    'Social Impact',
    'Financial Performance'
  ],

  // Theme modes
  THEMES: {
    LIGHT: 'light',
    DARK: 'dark'
  }
};

export const Selectors = {
  // Main app selectors
  APP_CONTAINER: '[data-testid="app-container"]',
  LOADING_INDICATOR: '[data-testid="loading-indicator"]',

  // Theme toggle
  THEME_TOGGLE: '[data-testid="theme-toggle"]',
  THEME_TOGGLE_BUTTON: '[data-testid="theme-toggle-button"]',

  // Dashboard tabs
  TAB_CONTAINER: '[data-testid="tab-container"]',
  TAB_BUTTON: (tabName: string) => `[data-testid="tab-${tabName.toLowerCase()}"]`,
  ACTIVE_TAB: '[data-testid="active-tab"]',

  // Setup tab
  SETUP_TAB: {
    BRAND_INPUT: '[data-testid="brand-input"]',
    INDUSTRY_SELECTOR: '[data-testid="industry-selector"]',
    INDUSTRY_CARD: (industry: string) => `[data-testid="industry-card-${industry}"]`,
    ANALYSIS_AREA_DROPDOWN: '[data-testid="analysis-area-dropdown"]',
    COMPETITOR_INPUT: '[data-testid="competitor-input"]',
    START_ANALYSIS_BUTTON: '[data-testid="start-analysis-button"]'
  },

  // Analysis tab
  ANALYSIS_TAB: {
    CHART_CONTAINER: '[data-testid="chart-container"]',
    RADAR_CHART: '[data-testid="radar-chart"]',
    LINE_CHART: '[data-testid="line-chart"]', 
    BAR_CHART: '[data-testid="bar-chart"]',
    DOUGHNUT_CHART: '[data-testid="doughnut-chart"]',
    VIEW_CHARTS_BUTTON: '[data-testid="view-charts-button"]',
    DEEP_DIVE_BUTTON: '[data-testid="deep-dive-button"]'
  },

  // Insights tab
  INSIGHTS_TAB: {
    INSIGHTS_CONTAINER: '[data-testid="insights-container"]',
    INSIGHT_CARD: '[data-testid="insight-card"]',
    HIGH_PRIORITY_INSIGHT: '[data-testid="insight-high"]',
    MEDIUM_PRIORITY_INSIGHT: '[data-testid="insight-medium"]',
    LOW_PRIORITY_INSIGHT: '[data-testid="insight-low"]'
  },

  // Roadmap tab
  ROADMAP_TAB: {
    ROADMAP_CONTAINER: '[data-testid="roadmap-container"]',
    QUARTER_SECTION: '[data-testid="quarter-section"]',
    ROADMAP_ITEM: '[data-testid="roadmap-item"]'
  },

  // Report tab
  REPORT_TAB: {
    REPORT_CONTAINER: '[data-testid="report-container"]',
    GENERATE_PDF_BUTTON: '[data-testid="generate-pdf-button"]',
    EXECUTIVE_SUMMARY: '[data-testid="executive-summary"]',
    DETAILED_METRICS: '[data-testid="detailed-metrics"]'
  },

  // Common UI elements
  GLASSMORPHISM_CARD: '[data-testid="glassmorphism-card"]',
  ANIMATED_ELEMENT: '[data-testid="animated-element"]',
  ERROR_MESSAGE: '[data-testid="error-message"]',
  SUCCESS_MESSAGE: '[data-testid="success-message"]'
};

export const ExpectedTexts = {
  APP_TITLE: 'Brand Intelligence Hub',
  WELCOME_MESSAGE: 'Welcome to Brand Intelligence Hub',
  ANALYSIS_COMPLETE: 'Analysis completed successfully',
  PDF_GENERATED: 'PDF report generated',
  THEME_SWITCHED: 'Theme switched successfully'
};

export const Timeouts = {
  SHORT: 2000,
  MEDIUM: 5000,
  LONG: 10000,
  CHART_LOAD: 15000,
  PDF_GENERATION: 20000,
  ANIMATION: 3000
};