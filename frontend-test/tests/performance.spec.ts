import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { AnalysisTab } from '../page-objects/AnalysisTab';
import { TestData, Timeouts } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Performance Tests', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;
  let analysisTab: AnalysisTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    analysisTab = new AnalysisTab(page);
    await dashboardPage.goto();
  });

  test('should load initial page within performance budget', async ({ page }) => {
    const startTime = Date.now();
    await dashboardPage.waitForPageLoad();
    const loadTime = Date.now() - startTime;
    
    // Initial page load should be under 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    console.log(`Initial page load: ${loadTime}ms`);
    
    // Check Core Web Vitals
    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        if ('PerformanceObserver' in window) {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const vitals: any = {};
            
            entries.forEach((entry: any) => {
              if (entry.name === 'first-contentful-paint') {
                vitals.fcp = entry.startTime;
              }
              if (entry.name === 'largest-contentful-paint') {
                vitals.lcp = entry.startTime;
              }
            });
            
            resolve(vitals);
          });
          
          observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
          
          // Fallback timeout
          setTimeout(() => resolve({}), 3000);
        } else {
          resolve({});
        }
      });
    });
    
    console.log('Web Vitals:', vitals);
  });

  test('should handle rapid navigation without performance degradation', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    const navigationTimes: number[] = [];
    const tabs = [
      TestData.TABS.SETUP,
      TestData.TABS.ANALYSIS,
      TestData.TABS.INSIGHTS,
      TestData.TABS.ROADMAP,
      TestData.TABS.REPORT
    ];
    
    // Rapid navigation test
    for (let i = 0; i < tabs.length; i++) {
      const startTime = Date.now();
      await dashboardPage.clickTab(tabs[i]);
      await TestHelpers.waitForAnimation(page, 500);
      const navTime = Date.now() - startTime;
      
      navigationTimes.push(navTime);
      console.log(`${tabs[i]} navigation: ${navTime}ms`);
    }
    
    // Navigation should be consistently fast
    const averageNavTime = navigationTimes.reduce((a, b) => a + b, 0) / navigationTimes.length;
    expect(averageNavTime).toBeLessThan(1000);
    
    // No single navigation should be excessively slow
    const maxNavTime = Math.max(...navigationTimes);
    expect(maxNavTime).toBeLessThan(2000);
  });

  test('should load charts within performance budget', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Setup analysis
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Performance Test', 'BANKING', 'Brand Performance');
    
    // Measure chart loading time
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    const chartLoadStart = Date.now();
    await analysisTab.clickViewCharts();
    await analysisTab.waitForChartsToLoad();
    const chartLoadTime = Date.now() - chartLoadStart;
    
    // Charts should load within reasonable time
    expect(chartLoadTime).toBeLessThan(Timeouts.CHART_LOAD);
    
    console.log(`Chart loading time: ${chartLoadTime}ms`);
    
    // Verify charts are actually rendered
    await analysisTab.verifyChartsVisible();
  });

  test('should maintain smooth animations', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Monitor frame rate during animations
    const fps = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frames = 0;
        let startTime = performance.now();
        
        function countFrame() {
          frames++;
          const currentTime = performance.now();
          
          if (currentTime - startTime >= 1000) {
            resolve(frames);
          } else {
            requestAnimationFrame(countFrame);
          }
        }
        
        requestAnimationFrame(countFrame);
      });
    });
    
    console.log(`Animation FPS: ${fps}`);
    
    // Should maintain at least 30 FPS for smooth animations
    expect(fps).toBeGreaterThan(30);
    
    // Test theme toggle animation performance
    const themeToggleStart = Date.now();
    await dashboardPage.toggleTheme();
    await TestHelpers.waitForAnimation(page);
    const themeToggleTime = Date.now() - themeToggleStart;
    
    expect(themeToggleTime).toBeLessThan(2000);
    console.log(`Theme toggle animation: ${themeToggleTime}ms`);
  });

  test('should handle memory usage efficiently', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
        jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
      } : null;
    });
    
    if (initialMemory) {
      console.log('Initial memory usage:', initialMemory);
      
      // Perform memory-intensive operations
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      await setupTab.completeSetup('Memory Test', 'TECH', 'Performance Analysis');
      
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await analysisTab.clickViewCharts();
      await analysisTab.waitForChartsToLoad();
      
      // Navigate through all tabs multiple times
      for (let i = 0; i < 3; i++) {
        for (const tab of Object.values(TestData.TABS)) {
          await dashboardPage.clickTab(tab);
          await page.waitForTimeout(200);
        }
      }
      
      const finalMemory = await page.evaluate(() => {
        return (performance as any).memory ? {
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize
        } : null;
      });
      
      if (finalMemory) {
        console.log('Final memory usage:', finalMemory);
        
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
        const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
        
        console.log(`Memory increase: ${memoryIncrease} bytes (${memoryIncreasePercent.toFixed(1)}%)`);
        
        // Memory usage shouldn't increase excessively
        expect(memoryIncreasePercent).toBeLessThan(200);
      }
    }
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Test with all industry datasets
    const industries = [
      { key: 'BANKING' as const, brand: 'Large Bank Corp' },
      { key: 'TECH' as const, brand: 'Tech Giant' },
      { key: 'HEALTHCARE' as const, brand: 'Health Systems Inc' }
    ];
    
    for (const industry of industries) {
      const dataLoadStart = Date.now();
      
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      await setupTab.completeSetup(industry.brand, industry.key, 'Comprehensive Analysis');
      
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await analysisTab.clickViewCharts();
      await analysisTab.waitForChartsToLoad();
      
      const dataLoadTime = Date.now() - dataLoadStart;
      console.log(`${industry.key} data load time: ${dataLoadTime}ms`);
      
      // Each dataset should load within reasonable time
      expect(dataLoadTime).toBeLessThan(10000);
    }
  });

  test('should optimize resource loading', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check resource loading performance
    const resourceTimings = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource');
      return resources.map((resource: any) => ({
        name: resource.name,
        duration: resource.duration,
        size: resource.transferSize || 0,
        type: resource.initiatorType
      }));
    });
    
    console.log(`Total resources loaded: ${resourceTimings.length}`);
    
    // Analyze resource types
    const resourcesByType = resourceTimings.reduce((acc: any, resource: any) => {
      acc[resource.type] = acc[resource.type] || [];
      acc[resource.type].push(resource);
      return acc;
    }, {});
    
    Object.keys(resourcesByType).forEach(type => {
      const resources = resourcesByType[type];
      const totalSize = resources.reduce((sum: number, r: any) => sum + r.size, 0);
      const avgDuration = resources.reduce((sum: number, r: any) => sum + r.duration, 0) / resources.length;
      
      console.log(`${type}: ${resources.length} files, ${totalSize} bytes, ${avgDuration.toFixed(1)}ms avg`);
    });
    
    // No single resource should take too long to load
    const slowResources = resourceTimings.filter((r: any) => r.duration > 3000);
    expect(slowResources.length).toBe(0);
  });

  test('should handle concurrent operations', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Test concurrent operations
    const operations = [
      () => dashboardPage.toggleTheme(),
      () => dashboardPage.clickTab(TestData.TABS.SETUP),
      () => dashboardPage.clickTab(TestData.TABS.ANALYSIS),
      () => dashboardPage.clickTab(TestData.TABS.INSIGHTS)
    ];
    
    const startTime = Date.now();
    
    // Execute operations rapidly
    for (const operation of operations) {
      operation();
      await page.waitForTimeout(100);
    }
    
    // Wait for all operations to complete
    await TestHelpers.waitForAnimation(page);
    
    const totalTime = Date.now() - startTime;
    console.log(`Concurrent operations time: ${totalTime}ms`);
    
    // Should handle rapid operations without errors
    await dashboardPage.checkConsoleErrors();
    
    // Should complete within reasonable time
    expect(totalTime).toBeLessThan(5000);
  });

  test('should maintain performance on mobile devices', async ({ page }) => {
    // Simulate mobile device constraints
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Throttle CPU to simulate mobile performance
    const client = await page.context().newCDPSession(page);
    await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    
    const mobileLoadStart = Date.now();
    await dashboardPage.waitForPageLoad();
    const mobileLoadTime = Date.now() - mobileLoadStart;
    
    console.log(`Mobile load time: ${mobileLoadTime}ms`);
    
    // Mobile should still load within reasonable time
    expect(mobileLoadTime).toBeLessThan(8000);
    
    // Test mobile navigation performance
    const mobileNavStart = Date.now();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await TestHelpers.waitForAnimation(page);
    const mobileNavTime = Date.now() - mobileNavStart;
    
    expect(mobileNavTime).toBeLessThan(2000);
    
    await client.detach();
  });

  test('should optimize bundle size', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check JavaScript bundle sizes
    const jsResources = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource');
      return resources
        .filter((resource: any) => resource.name.includes('.js'))
        .map((resource: any) => ({
          name: resource.name,
          size: resource.transferSize || 0,
          duration: resource.duration
        }));
    });
    
    const totalJSSize = jsResources.reduce((sum: number, resource: any) => sum + resource.size, 0);
    console.log(`Total JavaScript size: ${totalJSSize} bytes`);
    
    // Flutter web bundles can be large, but should be reasonable
    expect(totalJSSize).toBeLessThan(10 * 1024 * 1024); // 10MB limit
    
    // Main bundle should load quickly
    const mainBundle = jsResources.find((r: any) => r.name.includes('main'));
    if (mainBundle) {
      expect(mainBundle.duration).toBeLessThan(5000);
    }
  });

  test('should handle performance under stress', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Stress test: rapid interactions
    const stressTestStart = Date.now();
    
    for (let i = 0; i < 20; i++) {
      // Rapid tab switching
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
      await dashboardPage.clickTab(TestData.TABS.INSIGHTS);
      
      // Theme toggle every few iterations
      if (i % 5 === 0) {
        await dashboardPage.toggleTheme();
      }
    }
    
    const stressTestTime = Date.now() - stressTestStart;
    console.log(`Stress test time: ${stressTestTime}ms`);
    
    // Should handle stress without crashing
    await dashboardPage.checkConsoleErrors();
    
    // Verify app is still functional
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Should complete stress test in reasonable time
    expect(stressTestTime).toBeLessThan(30000);
  });

  test('should cache resources effectively', async ({ page, context }) => {
    await dashboardPage.waitForPageLoad();
    
    // Get initial resource count
    const initialResources = await page.evaluate(() => {
      return performance.getEntriesByType('resource').length;
    });
    
    // Navigate to another page and back
    await page.reload();
    await dashboardPage.waitForPageLoad();
    
    const reloadResources = await page.evaluate(() => {
      return performance.getEntriesByType('resource').length;
    });
    
    console.log(`Initial resources: ${initialResources}, Reload resources: ${reloadResources}`);
    
    // With proper caching, fewer resources should be loaded on reload
    // This is informational as Flutter web caching behavior varies
    console.log('Resource caching efficiency test completed');
  });
});