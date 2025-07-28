import { Page, Locator, expect } from '@playwright/test';
import { TestData, Selectors, Timeouts } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

/**
 * Page Object Model for the main Dashboard page
 */
export class DashboardPage {
  readonly page: Page;
  
  // Main containers
  readonly appContainer: Locator;
  readonly tabContainer: Locator;
  
  // Theme toggle
  readonly themeToggle: Locator;
  readonly themeToggleButton: Locator;
  
  // Tab navigation
  readonly setupTab: Locator;
  readonly analysisTab: Locator;
  readonly insightsTab: Locator;
  readonly roadmapTab: Locator;
  readonly reportTab: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Initialize locators with fallback to generic selectors for Flutter web
    this.appContainer = page.locator('body').first();
    this.tabContainer = page.locator('[role="tablist"]').or(page.locator('.tab-container')).first();
    
    // Theme toggle - look for button with sun/moon icons or theme-related text
    this.themeToggle = page.locator('button').filter({ hasText: /theme|dark|light/i }).first()
      .or(page.locator('[aria-label*="theme"]')).first()
      .or(page.locator('button').filter({ has: page.locator('svg') }).first());
    
    this.themeToggleButton = this.themeToggle;
    
    // Tab buttons - look for clickable elements with tab text
    this.setupTab = page.locator('button, [role="tab"]').filter({ hasText: TestData.TABS.SETUP }).first();
    this.analysisTab = page.locator('button, [role="tab"]').filter({ hasText: TestData.TABS.ANALYSIS }).first();
    this.insightsTab = page.locator('button, [role="tab"]').filter({ hasText: TestData.TABS.INSIGHTS }).first();
    this.roadmapTab = page.locator('button, [role="tab"]').filter({ hasText: TestData.TABS.ROADMAP }).first();
    this.reportTab = page.locator('button, [role="tab"]').filter({ hasText: TestData.TABS.REPORT }).first();
  }

  /**
   * Navigate to the dashboard page
   */
  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.waitForPageLoad();
  }

  /**
   * Wait for page to fully load
   */
  async waitForPageLoad(): Promise<void> {
    // Wait for the page to load
    await this.page.waitForLoadState('networkidle', { timeout: Timeouts.LONG });
    
    // Wait for Flutter framework to initialize
    await this.page.waitForFunction(() => {
      return document.querySelector('flt-glass-pane') !== null;
    }, { timeout: Timeouts.LONG });
    
    // Wait for Flutter canvas to be rendered (canvas should exist)
    await this.page.waitForSelector('canvas', { timeout: Timeouts.LONG });
    
    // Wait for Flutter app to be fully rendered by checking HTML content and canvas
    await this.page.waitForFunction(() => {
      const html = document.documentElement.innerHTML;
      const hasCanvas = document.querySelector('canvas') !== null;
      const htmlIncludesBrand = html.includes('Brand Intelligence Hub');
      return hasCanvas && htmlIncludesBrand;
    }, { timeout: Timeouts.LONG });
    
    // Additional wait for Flutter rendering to complete
    await TestHelpers.waitForAnimation(this.page, 3000);
  }

  /**
   * Toggle between light and dark theme
   */
  async toggleTheme(): Promise<void> {
    // For Flutter canvas, click in the top-right area where theme toggle usually is
    const canvas = this.page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible' });
    
    const box = await canvas.boundingBox();
    if (box) {
      // Theme toggle is typically in the top-right corner
      const themeToggleX = box.x + box.width - 100;  // 100px from right edge
      const themeToggleY = box.y + 75;  // 75px from top
      
      await this.page.mouse.click(themeToggleX, themeToggleY);
      await TestHelpers.waitForAnimation(this.page, 2000);
    }
  }

  /**
   * Click on a specific tab
   */
  async clickTab(tabName: string): Promise<void> {
    // For Flutter apps, we need to click on the canvas where the tab is rendered
    // We'll use coordinate-based clicking based on the typical layout
    const canvas = this.page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible' });
    
    const box = await canvas.boundingBox();
    if (box) {
      // Tab positions (approximate based on UI layout)
      const tabPositions = {
        'Setup': { x: box.x + 150, y: box.y + 430 },
        'Analysis': { x: box.x + 400, y: box.y + 430 },
        'Insights': { x: box.x + 650, y: box.y + 430 },
        'Roadmap': { x: box.x + 900, y: box.y + 430 },
        'Report': { x: box.x + 1150, y: box.y + 430 }
      };
      
      const position = tabPositions[tabName as keyof typeof tabPositions];
      if (position) {
        await this.page.mouse.click(position.x, position.y);
        await TestHelpers.waitForAnimation(this.page);
      }
    }
  }

  /**
   * Get tab button by name
   */
  private getTabButton(tabName: string): Locator {
    switch (tabName.toLowerCase()) {
      case 'setup':
        return this.setupTab;
      case 'analysis':
        return this.analysisTab;
      case 'insights':
        return this.insightsTab;
      case 'roadmap':
        return this.roadmapTab;
      case 'report':
        return this.reportTab;
      default:
        // Fallback to finding tab by text
        return this.page.locator('button, [role="tab"]').filter({ hasText: tabName }).first();
    }
  }

  /**
   * Check if specific tab is active
   */
  async isTabActive(tabName: string): Promise<boolean> {
    const tabButton = this.getTabButton(tabName);
    
    // Check for various active states
    const classNames = await tabButton.getAttribute('class') || '';
    const ariaSelected = await tabButton.getAttribute('aria-selected');
    
    return classNames.includes('active') || 
           classNames.includes('selected') || 
           ariaSelected === 'true';
  }

  /**
   * Get all visible tab names
   */
  async getVisibleTabs(): Promise<string[]> {
    // Use more flexible approach to find tabs
    const content = await this.page.textContent('body') || '';
    const possibleTabs = Object.values(TestData.TABS);
    const foundTabs = possibleTabs.filter(tab => content.includes(tab));
    
    return foundTabs;
  }

  /**
   * Check if theme toggle is working
   */
  async verifyThemeToggle(): Promise<void> {
    // Get initial theme state
    const initialBodyClass = await this.page.locator('body').getAttribute('class') || '';
    const isDarkInitially = initialBodyClass.includes('dark');
    
    // Toggle theme
    await this.toggleTheme();
    
    // Verify theme changed
    await this.page.waitForTimeout(1000); // Wait for theme transition
    const newBodyClass = await this.page.locator('body').getAttribute('class') || '';
    const isDarkNow = newBodyClass.includes('dark');
    
    expect(isDarkNow).not.toBe(isDarkInitially);
  }

  /**
   * Verify glassmorphism effects are present
   */
  async verifyGlassmorphismEffects(): Promise<void> {
    // Look for elements with backdrop-filter or blur effects
    const glassmorphElements = await this.page.locator('*').evaluateAll(elements => {
      return elements.filter(el => {
        const style = window.getComputedStyle(el);
        return style.backdropFilter && style.backdropFilter !== 'none';
      }).length;
    });
    
    expect(glassmorphElements).toBeGreaterThan(0);
  }

  /**
   * Check for responsive design
   */
  async verifyResponsiveDesign(): Promise<void> {
    await TestHelpers.testResponsiveBreakpoints(this.page, async () => {
      // Verify main containers are visible and properly sized
      await expect(this.appContainer).toBeVisible();
      
      // Check that tabs are accessible (might stack on mobile)
      const tabCount = await this.getVisibleTabs();
      expect(tabCount.length).toBeGreaterThan(0);
    });
  }

  /**
   * Take a screenshot of current state
   */
  async takeScreenshot(name: string): Promise<void> {
    await TestHelpers.takeScreenshot(this.page, `dashboard-${name}`);
  }

  /**
   * Check for accessibility compliance
   */
  async checkAccessibility(): Promise<void> {
    await TestHelpers.checkAccessibility(this.page);
  }

  /**
   * Verify page performance
   */
  async checkPerformance(): Promise<void> {
    await TestHelpers.checkPerformance(this.page);
  }

  /**
   * Check for console errors
   */
  async checkConsoleErrors(): Promise<void> {
    await TestHelpers.checkConsoleErrors(this.page);
  }
}