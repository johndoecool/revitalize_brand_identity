import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { AnalysisTab } from '../page-objects/AnalysisTab';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Chart Interactions and Data Visualization', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;
  let analysisTab: AnalysisTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    analysisTab = new AnalysisTab(page);
    await dashboardPage.goto();
  });

  test('should load and display charts after analysis setup', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete setup first
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Chart Test Brand', 'BANKING', 'Brand Reputation');
    
    // Navigate to Analysis tab
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Click View Charts if button exists
    await analysisTab.clickViewCharts();
    
    // Wait for charts to load
    await analysisTab.waitForChartsToLoad();
    
    // Verify charts are visible
    await analysisTab.verifyChartsVisible();
    
    await dashboardPage.takeScreenshot('charts-loaded');
  });

  test('should display multiple chart types', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Setup analysis
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Multi Chart Test', 'TECH', 'Digital Innovation');
    
    // Navigate to Analysis
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Check for different chart types
    const canvasElements = await page.locator('canvas').count();
    expect(canvasElements).toBeGreaterThan(0);
    
    console.log(`Found ${canvasElements} chart canvas elements`);
    
    // Verify charts have content
    const hasChartContent = await page.evaluate(() => {
      const canvases = Array.from(document.querySelectorAll('canvas'));
      return canvases.filter(canvas => {
        const context = canvas.getContext('2d');
        if (!context) return false;
        
        // Check if canvas has been drawn on
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        for (let i = 3; i < data.length; i += 4) {
          if (data[i] > 0) return true;
        }
        return false;
      }).length;
    });
    
    expect(hasChartContent).toBeGreaterThan(0);
    
    await dashboardPage.takeScreenshot('multiple-charts');
  });

  test('should handle chart interactions', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Setup and navigate to charts
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Interaction Test', 'HEALTHCARE', 'Product Innovation');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Test chart interactions
    await analysisTab.testAllChartInteractions();
    
    // Verify no errors during interactions
    await dashboardPage.checkConsoleErrors();
    
    await dashboardPage.takeScreenshot('chart-interactions');
  });

  test('should display radar chart correctly', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Radar Test', 'BANKING', 'Brand Reputation');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Interact specifically with radar chart
    await analysisTab.interactWithRadarChart();
    
    // Verify radar chart is present
    const canvases = await page.locator('canvas').all();
    expect(canvases.length).toBeGreaterThan(0);
    
    await dashboardPage.takeScreenshot('radar-chart');
  });

  test('should display line chart for trends', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Line Chart Test', 'TECH', 'Market Position');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Interact with line chart
    await analysisTab.interactWithLineChart();
    
    await dashboardPage.takeScreenshot('line-chart');
  });

  test('should display bar chart for comparisons', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Bar Chart Test', 'HEALTHCARE', 'Financial Performance');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Interact with bar chart
    await analysisTab.interactWithBarChart();
    
    await dashboardPage.takeScreenshot('bar-chart');
  });

  test('should display doughnut chart for data distribution', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Doughnut Test', 'BANKING', 'Customer Experience');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Interact with doughnut chart
    await analysisTab.interactWithDoughnutChart();
    
    await dashboardPage.takeScreenshot('doughnut-chart');
  });

  test('should verify chart animations', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Animation Test', 'TECH', 'Digital Innovation');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Monitor for chart animations
    await analysisTab.verifyChartAnimations();
    
    await dashboardPage.takeScreenshot('chart-animations');
  });

  test('should handle charts on different screen sizes', async ({ page }) => {
    await TestHelpers.testResponsiveBreakpoints(page, async () => {
      await dashboardPage.waitForPageLoad();
      
      // Setup analysis
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      
      if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
        await setupTab.completeSetup('Responsive Test', 'BANKING', 'Brand Reputation');
        await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
        
        // Try to load charts
        await analysisTab.clickViewCharts();
        
        // Verify charts adapt to screen size
        await analysisTab.verifyChartResponsiveness();
      }
    });
  });

  test('should check chart accessibility', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Accessibility Test', 'HEALTHCARE', 'Product Quality');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Check chart accessibility
    await analysisTab.verifyChartAccessibility();
    
    // General accessibility check
    await dashboardPage.checkAccessibility();
  });

  test('should verify chart performance', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Performance Test', 'TECH', 'Performance Metrics');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Check chart loading performance
    await analysisTab.checkChartPerformance();
    
    await dashboardPage.takeScreenshot('chart-performance');
  });

  test('should handle multiple industry chart data', async ({ page }) => {
    const industries = [
      { key: 'BANKING' as const, brand: 'Oriental Bank', area: 'Self Service Portal' },
      { key: 'TECH' as const, brand: 'Microsoft', area: 'Employer Branding' },
      { key: 'HEALTHCARE' as const, brand: 'Pfizer', area: 'Product Innovation' }
    ];
    
    for (const industry of industries) {
      await dashboardPage.waitForPageLoad();
      
      // Setup for each industry
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      await setupTab.completeSetup(industry.brand, industry.key, industry.area);
      
      // View charts
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await analysisTab.clickViewCharts();
      await analysisTab.waitForChartsToLoad();
      
      // Verify charts loaded for this industry
      await analysisTab.verifyChartsVisible();
      
      await dashboardPage.takeScreenshot(`charts-${industry.key.toLowerCase()}`);
      
      // Brief pause between industry tests
      await page.waitForTimeout(1000);
    }
  });

  test('should handle chart error states gracefully', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Try to view charts without completing setup
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Look for loading states or placeholder content
    const analysisContent = await page.locator('*').filter({ 
      hasText: /loading|setup|configure|select/i 
    }).count();
    
    // Should handle gracefully without errors
    await dashboardPage.checkConsoleErrors();
    
    console.log(`Analysis content elements: ${analysisContent}`);
  });

  test('should verify chart data accuracy', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Data Accuracy Test', 'BANKING', 'Brand Reputation');
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    
    // Check for data accuracy
    await analysisTab.verifyChartData();
    
    // Look for data labels or legends
    const dataElements = await page.locator('*').filter({ 
      hasText: /\d+%|\d+\.\d+|score|rating|value/i 
    }).count();
    
    console.log(`Data elements found: ${dataElements}`);
  });
});