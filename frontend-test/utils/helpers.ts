import { Page, Locator, expect } from '@playwright/test';
import { Timeouts } from './test-data';

/**
 * Common helper functions for Playwright tests
 */
export class TestHelpers {
  
  /**
   * Wait for element to be visible and stable
   */
  static async waitForElement(page: Page, selector: string, timeout = Timeouts.MEDIUM): Promise<Locator> {
    const element = page.locator(selector);
    await element.waitFor({ state: 'visible', timeout });
    return element;
  }

  /**
   * Wait for animation to complete
   */
  static async waitForAnimation(page: Page, duration = Timeouts.ANIMATION): Promise<void> {
    await page.waitForTimeout(duration);
  }

  /**
   * Check if element has specific CSS class
   */
  static async hasClass(element: Locator, className: string): Promise<boolean> {
    const classValue = await element.getAttribute('class');
    return classValue?.includes(className) || false;
  }

  /**
   * Wait for chart to load by checking canvas elements
   */
  static async waitForChartLoad(page: Page, chartSelector: string): Promise<void> {
    const chart = page.locator(chartSelector);
    await chart.waitFor({ state: 'visible', timeout: Timeouts.CHART_LOAD });
    
    // Wait for canvas elements to render (fl_chart uses canvas)
    await page.waitForSelector(`${chartSelector} canvas`, { timeout: Timeouts.CHART_LOAD });
    
    // Additional wait for chart animation to complete
    await this.waitForAnimation(page);
  }

  /**
   * Take screenshot with timestamp
   */
  static async takeScreenshot(page: Page, name: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await page.screenshot({ 
      path: `test-results/screenshots/${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Check responsive design by testing multiple viewport sizes
   */
  static async testResponsiveBreakpoints(page: Page, testFn: () => Promise<void>): Promise<void> {
    const breakpoints = [
      { width: 320, height: 568, name: 'mobile-small' },
      { width: 375, height: 667, name: 'mobile-medium' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1024, height: 768, name: 'tablet-landscape' },
      { width: 1280, height: 720, name: 'desktop-small' },
      { width: 1920, height: 1080, name: 'desktop-large' }
    ];

    for (const breakpoint of breakpoints) {
      await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
      await page.waitForTimeout(500); // Wait for responsive changes
      await testFn();
    }
  }

  /**
   * Check for accessibility violations
   */
  static async checkAccessibility(page: Page): Promise<void> {
    // Check for basic accessibility requirements
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
    expect(headings).toBeGreaterThan(0);

    // Check for alt text on images
    const images = page.locator('img');
    const imageCount = await images.count();
    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }

    // Check for keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  }

  /**
   * Wait for network requests to complete
   */
  static async waitForNetworkIdle(page: Page, timeout = Timeouts.MEDIUM): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Check if element is visible in viewport
   */
  static async isInViewport(element: Locator): Promise<boolean> {
    return await element.isVisible();
  }

  /**
   * Scroll element into view
   */
  static async scrollIntoView(element: Locator): Promise<void> {
    await element.scrollIntoViewIfNeeded();
    await element.page().waitForTimeout(500);
  }

  /**
   * Get computed style property
   */
  static async getComputedStyle(element: Locator, property: string): Promise<string> {
    return await element.evaluate((el, prop) => {
      return window.getComputedStyle(el).getPropertyValue(prop);
    }, property);
  }

  /**
   * Check if theme is applied correctly
   */
  static async verifyTheme(page: Page, expectedTheme: 'light' | 'dark'): Promise<void> {
    const bodyClass = await page.locator('body').getAttribute('class');
    if (expectedTheme === 'dark') {
      expect(bodyClass).toContain('dark');
    } else {
      expect(bodyClass).not.toContain('dark');
    }
  }

  /**
   * Wait for PDF download
   */
  static async waitForDownload(page: Page, triggerFn: () => Promise<void>): Promise<void> {
    const downloadPromise = page.waitForEvent('download');
    await triggerFn();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.pdf');
  }

  /**
   * Check performance metrics
   */
  static async checkPerformance(page: Page): Promise<void> {
    const performanceTiming = await page.evaluate(() => {
      const timing = performance.timing;
      return {
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        loadComplete: timing.loadEventEnd - timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
      };
    });

    // Assert reasonable performance thresholds
    expect(performanceTiming.domContentLoaded).toBeLessThan(5000); // 5 seconds
    expect(performanceTiming.loadComplete).toBeLessThan(10000); // 10 seconds
  }

  /**
   * Check for console errors
   */
  static async checkConsoleErrors(page: Page): Promise<void> {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Allow some time for potential errors to surface
    await page.waitForTimeout(1000);
    
    // Filter out known Flutter/framework errors that are not critical
    const criticalErrors = errors.filter(error => 
      !error.includes('Flutter') && 
      !error.includes('DevTools') &&
      !error.includes('source-map')
    );
    
    expect(criticalErrors).toHaveLength(0);
  }
}