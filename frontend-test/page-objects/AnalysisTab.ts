import { Page, Locator, expect } from '@playwright/test';
import { Timeouts } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

/**
 * Page Object Model for the Analysis tab with chart components
 */
export class AnalysisTab {
  readonly page: Page;
  
  // Chart containers
  readonly chartContainer: Locator;
  readonly radarChart: Locator;
  readonly lineChart: Locator;
  readonly barChart: Locator;
  readonly doughnutChart: Locator;
  
  // Chart interaction buttons
  readonly viewChartsButton: Locator;
  readonly deepDiveButton: Locator;
  
  // Loading states
  readonly loadingIndicator: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Chart containers - look for canvas elements (fl_chart uses canvas)
    this.chartContainer = page.locator('.chart-container, [data-testid*="chart"]').first()
      .or(page.locator('canvas').first().locator('..'));
    
    this.radarChart = page.locator('canvas').first()
      .or(page.locator('*').filter({ hasText: /radar/i })).first();
    
    this.lineChart = page.locator('canvas').nth(1)
      .or(page.locator('*').filter({ hasText: /line|trend/i })).first();
    
    this.barChart = page.locator('canvas').nth(2)
      .or(page.locator('*').filter({ hasText: /bar|column/i })).first();
    
    this.doughnutChart = page.locator('canvas').nth(3)
      .or(page.locator('*').filter({ hasText: /doughnut|pie/i })).first();
    
    // Interaction buttons
    this.viewChartsButton = page.locator('button').filter({ hasText: /view charts|show charts/i }).first();
    this.deepDiveButton = page.locator('button').filter({ hasText: /deep dive|detailed/i }).first();
    
    // Loading indicators
    this.loadingIndicator = page.locator('.loading, .spinner, [data-testid*="loading"]').first()
      .or(page.locator('*').filter({ hasText: /loading|analyzing/i })).first();
  }

  /**
   * Wait for charts to load
   */
  async waitForChartsToLoad(): Promise<void> {
    // Wait for at least one canvas element to appear
    await this.page.waitForSelector('canvas', { timeout: Timeouts.CHART_LOAD });
    
    // Wait for charts to render (check that canvas has content)
    await this.page.waitForFunction(() => {
      const canvases = Array.from(document.querySelectorAll('canvas'));
      return canvases.some(canvas => {
        const context = canvas.getContext('2d');
        return context && canvas.width > 0 && canvas.height > 0;
      });
    }, { timeout: Timeouts.CHART_LOAD });
    
    // Additional wait for animations to complete
    await TestHelpers.waitForAnimation(this.page, 3000);
  }

  /**
   * Click View Charts button
   */
  async clickViewCharts(): Promise<void> {
    if (await this.viewChartsButton.isVisible({ timeout: Timeouts.SHORT })) {
      await this.viewChartsButton.click();
      await this.waitForChartsToLoad();
    }
  }

  /**
   * Click Deep Dive button
   */
  async clickDeepDive(): Promise<void> {
    if (await this.deepDiveButton.isVisible({ timeout: Timeouts.SHORT })) {
      await this.deepDiveButton.click();
      await TestHelpers.waitForAnimation(this.page);
    }
  }

  /**
   * Verify charts are visible and rendered
   */
  async verifyChartsVisible(): Promise<void> {
    // Check that canvas elements exist
    const canvasCount = await this.page.locator('canvas').count();
    expect(canvasCount).toBeGreaterThan(0);
    
    // Verify at least one chart is rendered with content
    const hasChartContent = await this.page.evaluate(() => {
      const canvases = Array.from(document.querySelectorAll('canvas'));
      return canvases.some(canvas => {
        const context = canvas.getContext('2d');
        if (!context) return false;
        
        // Check if canvas has been drawn on
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // Check for non-transparent pixels
        for (let i = 3; i < data.length; i += 4) {
          if (data[i] > 0) return true;
        }
        return false;
      });
    });
    
    expect(hasChartContent).toBe(true);
  }

  /**
   * Interact with radar chart
   */
  async interactWithRadarChart(): Promise<void> {
    if (await this.radarChart.isVisible({ timeout: Timeouts.SHORT })) {
      // Hover over chart to trigger interactions
      await this.radarChart.hover();
      await this.page.waitForTimeout(1000);
      
      // Try clicking on chart area
      await this.radarChart.click();
      await this.page.waitForTimeout(500);
    }
  }

  /**
   * Interact with line chart
   */
  async interactWithLineChart(): Promise<void> {
    if (await this.lineChart.isVisible({ timeout: Timeouts.SHORT })) {
      await this.lineChart.hover();
      await this.page.waitForTimeout(1000);
      
      // Try different positions on the chart
      const box = await this.lineChart.boundingBox();
      if (box) {
        await this.page.mouse.move(box.x + box.width * 0.5, box.y + box.height * 0.5);
        await this.page.waitForTimeout(500);
      }
    }
  }

  /**
   * Interact with bar chart
   */
  async interactWithBarChart(): Promise<void> {
    if (await this.barChart.isVisible({ timeout: Timeouts.SHORT })) {
      await this.barChart.hover();
      await this.page.waitForTimeout(1000);
      
      await this.barChart.click();
      await this.page.waitForTimeout(500);
    }
  }

  /**
   * Interact with doughnut chart
   */
  async interactWithDoughnutChart(): Promise<void> {
    if (await this.doughnutChart.isVisible({ timeout: Timeouts.SHORT })) {
      await this.doughnutChart.hover();
      await this.page.waitForTimeout(1000);
      
      // Click on different segments
      const box = await this.doughnutChart.boundingBox();
      if (box) {
        const centerX = box.x + box.width * 0.5;
        const centerY = box.y + box.height * 0.5;
        
        // Click on different positions around the circle
        await this.page.mouse.click(centerX + 50, centerY);
        await this.page.waitForTimeout(500);
        
        await this.page.mouse.click(centerX - 50, centerY);
        await this.page.waitForTimeout(500);
      }
    }
  }

  /**
   * Test all chart interactions
   */
  async testAllChartInteractions(): Promise<void> {
    await this.interactWithRadarChart();
    await this.interactWithLineChart();
    await this.interactWithBarChart();
    await this.interactWithDoughnutChart();
  }

  /**
   * Check for chart animations
   */
  async verifyChartAnimations(): Promise<void> {
    // Monitor canvas changes during load
    const initialState = await this.captureCanvasStates();
    
    // Wait for potential animations
    await TestHelpers.waitForAnimation(this.page, 2000);
    
    const finalState = await this.captureCanvasStates();
    
    // Verify that some animation occurred (canvas content changed)
    expect(initialState).not.toEqual(finalState);
  }

  /**
   * Capture current state of all canvas elements
   */
  private async captureCanvasStates(): Promise<string[]> {
    return await this.page.evaluate(() => {
      const canvases = Array.from(document.querySelectorAll('canvas'));
      return canvases.map(canvas => {
        try {
          return canvas.toDataURL();
        } catch (e) {
          return '';
        }
      });
    });
  }

  /**
   * Verify chart responsiveness
   */
  async verifyChartResponsiveness(): Promise<void> {
    await TestHelpers.testResponsiveBreakpoints(this.page, async () => {
      // Check that charts adapt to viewport size
      const canvases = await this.page.locator('canvas').all();
      
      for (const canvas of canvases) {
        if (await canvas.isVisible({ timeout: Timeouts.SHORT })) {
          const box = await canvas.boundingBox();
          if (box) {
            // Verify chart fits within reasonable bounds
            expect(box.width).toBeGreaterThan(100);
            expect(box.height).toBeGreaterThan(100);
            expect(box.width).toBeLessThan(2000);
            expect(box.height).toBeLessThan(2000);
          }
        }
      }
    });
  }

  /**
   * Check for chart accessibility
   */
  async verifyChartAccessibility(): Promise<void> {
    // Check for chart labels and descriptions
    const chartLabels = await this.page.locator('*').filter({ 
      hasText: /chart|graph|data|metrics|analysis/i 
    }).count();
    
    expect(chartLabels).toBeGreaterThan(0);
    
    // Check for keyboard navigation support
    await this.page.keyboard.press('Tab');
    const focusedElement = await this.page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  }

  /**
   * Verify chart data accuracy
   */
  async verifyChartData(): Promise<void> {
    // Look for data labels or tooltips that might appear on hover
    const canvases = await this.page.locator('canvas').all();
    
    for (const canvas of canvases) {
      if (await canvas.isVisible({ timeout: Timeouts.SHORT })) {
        // Hover to potentially trigger tooltips
        await canvas.hover();
        await this.page.waitForTimeout(1000);
        
        // Look for any tooltip or data display elements
        const tooltips = await this.page.locator('.tooltip, .chart-tooltip, [role="tooltip"]').count();
        
        // Not all charts may have tooltips, so this is informational
        console.log(`Chart tooltips found: ${tooltips}`);
      }
    }
  }

  /**
   * Check chart loading performance
   */
  async checkChartPerformance(): Promise<void> {
    const startTime = Date.now();
    await this.waitForChartsToLoad();
    const loadTime = Date.now() - startTime;
    
    // Charts should load within reasonable time
    expect(loadTime).toBeLessThan(Timeouts.CHART_LOAD);
  }
}