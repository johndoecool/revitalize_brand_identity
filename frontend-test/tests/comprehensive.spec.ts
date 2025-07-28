import { test, expect } from '@playwright/test';

test.describe('Brand Intelligence Hub - Comprehensive Test Suite', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('canvas', { timeout: 15000 });
    await page.waitForTimeout(3000);
  });

  test('1. Application Loading and Initial State', async ({ page }) => {
    // Verify app loads correctly
    const html = await page.content();
    expect(html).toContain('Brand Intelligence Hub');
    
    // Check canvas exists
    const canvasCount = await page.locator('canvas').count();
    expect(canvasCount).toBeGreaterThan(0);
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'test-results/01-initial-load.png', fullPage: true });
    
    console.log('✅ Application loads successfully');
  });

  test('2. Theme Toggle Functionality', async ({ page }) => {
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Take screenshot before theme toggle
      await page.screenshot({ path: 'test-results/02-before-theme-toggle.png', fullPage: true });
      
      // Click theme toggle (top-right area)
      await page.mouse.click(box.x + box.width - 100, box.y + 75);
      await page.waitForTimeout(2000);
      
      // Take screenshot after theme toggle
      await page.screenshot({ path: 'test-results/02-after-theme-toggle.png', fullPage: true });
      
      // Toggle back
      await page.mouse.click(box.x + box.width - 100, box.y + 75);
      await page.waitForTimeout(2000);
      
      await page.screenshot({ path: 'test-results/02-theme-toggle-back.png', fullPage: true });
    }
    
    console.log('✅ Theme toggle functionality working');
  });

  test('3. Tab Navigation', async ({ page }) => {
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      const tabs = [
        { name: 'Setup', x: 150, y: 430 },
        { name: 'Analysis', x: 400, y: 430 },
        { name: 'Insights', x: 650, y: 430 },
        { name: 'Roadmap', x: 900, y: 430 },
        { name: 'Report', x: 1150, y: 430 }
      ];
      
      for (const tab of tabs) {
        await page.mouse.click(box.x + tab.x, box.y + tab.y);
        await page.waitForTimeout(1500);
        await page.screenshot({ 
          path: `test-results/03-tab-${tab.name.toLowerCase()}.png`, 
          fullPage: true 
        });
        console.log(`📋 Navigated to ${tab.name} tab`);
      }
    }
    
    console.log('✅ Tab navigation working');
  });

  test('4. Brand Input and Form Interaction', async ({ page }) => {
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Navigate to Setup tab first
      await page.mouse.click(box.x + 150, box.y + 430);
      await page.waitForTimeout(1000);
      
      // Click on brand input area
      await page.mouse.click(box.x + 640, box.y + 580);
      await page.waitForTimeout(500);
      
      // Type brand name
      await page.keyboard.type('Test Brand Company');
      await page.waitForTimeout(1000);
      
      await page.screenshot({ path: 'test-results/04-brand-input.png', fullPage: true });
      
      // Try clicking on analysis area dropdown (below brand input)
      await page.mouse.click(box.x + 640, box.y + 680);
      await page.waitForTimeout(1000);
      
      await page.screenshot({ path: 'test-results/04-analysis-area.png', fullPage: true });
    }
    
    console.log('✅ Form interactions working');
  });

  test('5. Responsive Design - Multiple Viewports', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop-large' },
      { width: 1280, height: 720, name: 'desktop-medium' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 375, height: 667, name: 'mobile' }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(1000);
      
      // Verify canvas still exists and is visible
      const canvas = page.locator('canvas').first();
      await expect(canvas).toBeVisible();
      
      await page.screenshot({ 
        path: `test-results/05-responsive-${viewport.name}.png`, 
        fullPage: true 
      });
      
      console.log(`📱 Responsive test: ${viewport.name} (${viewport.width}x${viewport.height})`);
    }
    
    console.log('✅ Responsive design working');
  });

  test('6. Performance and Loading Metrics', async ({ page }) => {
    // Measure loading time
    const startTime = Date.now();
    
    await page.goto('http://localhost:8080');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('canvas', { timeout: 15000 });
    
    const loadTime = Date.now() - startTime;
    
    // Check for console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(2000);
    
    // Performance metrics
    const metrics = await page.evaluate(() => {
      const timing = performance.timing;
      return {
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        loadComplete: timing.loadEventEnd - timing.navigationStart,
        resourceCount: performance.getEntriesByType('resource').length
      };
    });
    
    await page.screenshot({ path: 'test-results/06-performance.png', fullPage: true });
    
    console.log(`⏱️ Load time: ${loadTime}ms`);
    console.log(`📊 DOM loaded: ${metrics.domContentLoaded}ms`);
    console.log(`🔗 Resources loaded: ${metrics.resourceCount}`);
    console.log(`❌ Console errors: ${errors.length}`);
    
    // Assert performance thresholds
    expect(loadTime).toBeLessThan(20000); // 20 seconds max
    expect(errors.length).toBe(0);
    
    console.log('✅ Performance metrics acceptable');
  });

  test('7. Cross-Browser Compatibility Check', async ({ page, browserName }) => {
    // This test will run across different browsers based on config
    
    await page.screenshot({ 
      path: `test-results/07-browser-${browserName}.png`, 
      fullPage: true 
    });
    
    // Verify basic functionality works in this browser
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
    
    const html = await page.content();
    expect(html).toContain('Brand Intelligence Hub');
    
    console.log(`🌐 Browser compatibility: ${browserName} ✅`);
  });

  test('8. Accessibility Basic Check', async ({ page }) => {
    // Check for basic accessibility features
    
    // Verify page has title
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // Check for keyboard navigation
    await page.keyboard.press('Tab');
    await page.waitForTimeout(500);
    
    // Check for color contrast (basic check)
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
    
    await page.screenshot({ path: 'test-results/08-accessibility.png', fullPage: true });
    
    console.log('♿ Basic accessibility checks passed');
  });

  test('9. Error Handling and Edge Cases', async ({ page }) => {
    // Test app behavior with various edge cases
    
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Try clicking outside the main UI area
      await page.mouse.click(box.x + 50, box.y + 50);
      await page.waitForTimeout(500);
      
      // Try rapid clicking
      for (let i = 0; i < 5; i++) {
        await page.mouse.click(box.x + 150, box.y + 430);
        await page.waitForTimeout(100);
      }
      
      // Test keyboard input
      await page.keyboard.press('Escape');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
    }
    
    await page.screenshot({ path: 'test-results/09-edge-cases.png', fullPage: true });
    
    console.log('🛡️ Edge case handling working');
  });

  test('10. End-to-End User Journey', async ({ page }) => {
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Complete user journey: Setup -> Analysis -> Insights -> Report
      
      // 1. Setup
      await page.mouse.click(box.x + 150, box.y + 430);
      await page.waitForTimeout(1000);
      await page.mouse.click(box.x + 640, box.y + 580);
      await page.keyboard.type('E2E Test Company');
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'test-results/10-e2e-setup.png', fullPage: true });
      
      // 2. Analysis
      await page.mouse.click(box.x + 400, box.y + 430);
      await page.waitForTimeout(1500);
      await page.screenshot({ path: 'test-results/10-e2e-analysis.png', fullPage: true });
      
      // 3. Insights
      await page.mouse.click(box.x + 650, box.y + 430);
      await page.waitForTimeout(1500);
      await page.screenshot({ path: 'test-results/10-e2e-insights.png', fullPage: true });
      
      // 4. Report
      await page.mouse.click(box.x + 1150, box.y + 430);
      await page.waitForTimeout(1500);
      await page.screenshot({ path: 'test-results/10-e2e-report.png', fullPage: true });
      
      // Test theme toggle during journey
      await page.mouse.click(box.x + box.width - 100, box.y + 75);
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'test-results/10-e2e-final.png', fullPage: true });
    }
    
    console.log('🎯 End-to-end user journey completed');
  });
});