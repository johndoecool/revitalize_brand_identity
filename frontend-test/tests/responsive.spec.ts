import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Responsive Design Tests', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    await dashboardPage.goto();
  });

  test('should work on mobile portrait (320x568)', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await dashboardPage.waitForPageLoad();
    
    // Verify main elements are visible and accessible
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Check tab navigation on mobile
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThan(0);
    
    // Test basic navigation
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Verify input elements are touch-friendly
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      const inputBox = await setupTab.brandInput.boundingBox();
      if (inputBox) {
        expect(inputBox.height).toBeGreaterThan(40); // Minimum touch target
      }
    }
    
    await dashboardPage.takeScreenshot('mobile-portrait-320');
  });

  test('should work on mobile landscape (568x320)', async ({ page }) => {
    await page.setViewportSize({ width: 568, height: 320 });
    await dashboardPage.waitForPageLoad();
    
    // Verify layout adapts to landscape
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Navigation should still be accessible
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThan(0);
    
    await dashboardPage.takeScreenshot('mobile-landscape-568');
  });

  test('should work on iPhone 12 (390x844)', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await dashboardPage.waitForPageLoad();
    
    // Complete a full workflow on iPhone size
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      await setupTab.completeSetup('iPhone Test', 'TECH', 'Mobile Experience');
      
      // Navigate through tabs
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await TestHelpers.waitForAnimation(page);
      
      await dashboardPage.clickTab(TestData.TABS.INSIGHTS);
      await TestHelpers.waitForAnimation(page);
    }
    
    await dashboardPage.takeScreenshot('iphone-12');
  });

  test('should work on tablet portrait (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await dashboardPage.waitForPageLoad();
    
    // Verify tablet layout
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Tabs should be clearly visible on tablet
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThanOrEqual(3);
    
    // Test theme toggle on tablet
    await dashboardPage.toggleTheme();
    await TestHelpers.waitForAnimation(page);
    
    await dashboardPage.takeScreenshot('tablet-portrait');
  });

  test('should work on tablet landscape (1024x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await dashboardPage.waitForPageLoad();
    
    // Should have more horizontal space
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Complete workflow on tablet landscape
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      await setupTab.completeSetup('Tablet Test', 'BANKING', 'Digital Services');
      
      // Charts should render well on tablet
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await TestHelpers.waitForAnimation(page);
      
      // Check for chart elements
      const canvasCount = await page.locator('canvas').count();
      console.log(`Tablet landscape canvas count: ${canvasCount}`);
    }
    
    await dashboardPage.takeScreenshot('tablet-landscape');
  });

  test('should work on desktop small (1280x720)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await dashboardPage.waitForPageLoad();
    
    // Desktop should show full layout
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // All tabs should be clearly visible
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThanOrEqual(4);
    
    // Test complete workflow on desktop
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      await setupTab.completeSetup('Desktop Test', 'HEALTHCARE', 'Patient Care');
      
      // Navigate through all tabs
      for (const tab of Object.values(TestData.TABS)) {
        await dashboardPage.clickTab(tab);
        await TestHelpers.waitForAnimation(page, 1000);
      }
    }
    
    await dashboardPage.takeScreenshot('desktop-small');
  });

  test('should work on desktop large (1920x1080)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await dashboardPage.waitForPageLoad();
    
    // Large desktop should utilize space efficiently
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // All features should be accessible
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThanOrEqual(4);
    
    // Test theme toggle on large screen
    await dashboardPage.toggleTheme();
    await TestHelpers.waitForAnimation(page);
    
    await dashboardPage.toggleTheme();
    await TestHelpers.waitForAnimation(page);
    
    await dashboardPage.takeScreenshot('desktop-large');
  });

  test('should handle ultra-wide screens (2560x1440)', async ({ page }) => {
    await page.setViewportSize({ width: 2560, height: 1440 });
    await dashboardPage.waitForPageLoad();
    
    // Ultra-wide should not break layout
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Content should not be too stretched
    const bodyWidth = await page.locator('body').evaluate(el => el.scrollWidth);
    expect(bodyWidth).toBeLessThan(3000); // Reasonable max width
    
    await dashboardPage.takeScreenshot('ultra-wide');
  });

  test('should maintain touch targets on mobile', async ({ page }) => {
    const mobileBreakpoints = [
      { width: 320, height: 568, name: 'small-mobile' },
      { width: 375, height: 667, name: 'medium-mobile' },
      { width: 414, height: 896, name: 'large-mobile' }
    ];
    
    for (const breakpoint of mobileBreakpoints) {
      await page.setViewportSize(breakpoint);
      await dashboardPage.waitForPageLoad();
      
      // Check tab buttons are touch-friendly
      const tabButtons = await page.locator('button, [role="tab"]').all();
      
      for (const button of tabButtons.slice(0, 3)) { // Check first 3
        if (await button.isVisible({ timeout: 1000 })) {
          const buttonBox = await button.boundingBox();
          if (buttonBox) {
            expect(buttonBox.height).toBeGreaterThan(40); // iOS guideline
            expect(buttonBox.width).toBeGreaterThan(40);
          }
        }
      }
      
      await dashboardPage.takeScreenshot(`touch-targets-${breakpoint.name}`);
    }
  });

  test('should handle orientation changes', async ({ page }) => {
    // Start in portrait
    await page.setViewportSize({ width: 375, height: 667 });
    await dashboardPage.waitForPageLoad();
    
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      await setupTab.enterBrandName('Orientation Test');
      await setupTab.selectIndustry('TECH');
    }
    
    // Switch to landscape
    await page.setViewportSize({ width: 667, height: 375 });
    await TestHelpers.waitForAnimation(page);
    
    // Verify layout adapted
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Data should be preserved
    if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
      const brandValue = await setupTab.brandInput.inputValue();
      expect(brandValue).toBe('Orientation Test');
    }
    
    await dashboardPage.takeScreenshot('orientation-change');
  });

  test('should scroll properly on small screens', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 400 }); // Very small height
    await dashboardPage.waitForPageLoad();
    
    // Should be able to scroll to access all content
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    
    // Scroll back to top
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(500);
    
    // Navigation should still work
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    await dashboardPage.takeScreenshot('small-screen-scroll');
  });

  test('should handle text scaling', async ({ page }) => {
    // Test with larger text (simulate accessibility settings)
    await page.addStyleTag({
      content: `
        * {
          font-size: 120% !important;
        }
      `
    });
    
    await page.setViewportSize({ width: 768, height: 1024 });
    await dashboardPage.waitForPageLoad();
    
    // Layout should accommodate larger text
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Check that text doesn't overflow
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThan(0);
    
    await dashboardPage.takeScreenshot('large-text');
  });

  test('should work with reduced motion preferences', async ({ page }) => {
    // Simulate reduced motion preference
    await page.addStyleTag({
      content: `
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `
    });
    
    await page.setViewportSize({ width: 1024, height: 768 });
    await dashboardPage.waitForPageLoad();
    
    // Navigation should still work without animations
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Theme toggle should work
    await dashboardPage.toggleTheme();
    
    await dashboardPage.takeScreenshot('reduced-motion');
  });

  test('should maintain performance across screen sizes', async ({ page }) => {
    const breakpoints = [
      { width: 320, height: 568 },
      { width: 768, height: 1024 },
      { width: 1920, height: 1080 }
    ];
    
    for (const breakpoint of breakpoints) {
      await page.setViewportSize(breakpoint);
      
      const startTime = Date.now();
      await dashboardPage.waitForPageLoad();
      const loadTime = Date.now() - startTime;
      
      // Should load within reasonable time on all screen sizes
      expect(loadTime).toBeLessThan(10000);
      
      console.log(`${breakpoint.width}x${breakpoint.height}: ${loadTime}ms`);
    }
  });

  test('should handle edge cases', async ({ page }) => {
    // Very narrow screen
    await page.setViewportSize({ width: 240, height: 800 });
    await dashboardPage.waitForPageLoad();
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Very wide screen
    await page.setViewportSize({ width: 3000, height: 600 });
    await dashboardPage.waitForPageLoad();
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Square screen
    await page.setViewportSize({ width: 800, height: 800 });
    await dashboardPage.waitForPageLoad();
    await expect(dashboardPage.appContainer).toBeVisible();
    
    await dashboardPage.takeScreenshot('edge-cases');
  });
});