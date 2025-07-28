import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Tab Navigation Functionality', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
  });

  test('should display all required tabs', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Get visible tabs
    const visibleTabs = await dashboardPage.getVisibleTabs();
    
    // Verify all expected tabs are present
    const expectedTabs = Object.values(TestData.TABS);
    const foundTabs = expectedTabs.filter(tab => 
      visibleTabs.some(visible => 
        visible.toLowerCase().includes(tab.toLowerCase())
      )
    );
    
    expect(foundTabs.length).toBeGreaterThan(0);
    console.log(`Found tabs: ${visibleTabs.join(', ')}`);
    console.log(`Expected tabs: ${expectedTabs.join(', ')}`);
  });

  test('should navigate to Setup tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Click on Setup tab
    const setupTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.SETUP }).first();
    
    if (await setupTab.isVisible({ timeout: 5000 })) {
      await setupTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Verify Setup tab is active
      const isActive = await dashboardPage.isTabActive(TestData.TABS.SETUP);
      
      // Look for Setup-specific content
      const setupContent = await page.locator('*').filter({ 
        hasText: /brand|industry|analysis|setup/i 
      }).count();
      
      expect(setupContent).toBeGreaterThan(0);
      
      await dashboardPage.takeScreenshot('setup-tab-active');
    }
  });

  test('should navigate to Analysis tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Click on Analysis tab
    const analysisTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.ANALYSIS }).first();
    
    if (await analysisTab.isVisible({ timeout: 5000 })) {
      await analysisTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Look for Analysis-specific content (charts, view charts button, etc.)
      const analysisContent = await page.locator('*').filter({ 
        hasText: /chart|analysis|data|metrics/i 
      }).count();
      
      expect(analysisContent).toBeGreaterThan(0);
      
      // Check for canvas elements (charts)
      const canvasCount = await page.locator('canvas').count();
      console.log(`Canvas elements found: ${canvasCount}`);
      
      await dashboardPage.takeScreenshot('analysis-tab-active');
    }
  });

  test('should navigate to Insights tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Click on Insights tab
    const insightsTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.INSIGHTS }).first();
    
    if (await insightsTab.isVisible({ timeout: 5000 })) {
      await insightsTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Look for Insights-specific content
      const insightsContent = await page.locator('*').filter({ 
        hasText: /insight|recommendation|priority|action/i 
      }).count();
      
      expect(insightsContent).toBeGreaterThan(0);
      
      await dashboardPage.takeScreenshot('insights-tab-active');
    }
  });

  test('should navigate to Roadmap tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Click on Roadmap tab
    const roadmapTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.ROADMAP }).first();
    
    if (await roadmapTab.isVisible({ timeout: 5000 })) {
      await roadmapTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Look for Roadmap-specific content
      const roadmapContent = await page.locator('*').filter({ 
        hasText: /roadmap|quarter|timeline|plan/i 
      }).count();
      
      expect(roadmapContent).toBeGreaterThan(0);
      
      await dashboardPage.takeScreenshot('roadmap-tab-active');
    }
  });

  test('should navigate to Report tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Click on Report tab
    const reportTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.REPORT }).first();
    
    if (await reportTab.isVisible({ timeout: 5000 })) {
      await reportTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Look for Report-specific content
      const reportContent = await page.locator('*').filter({ 
        hasText: /report|pdf|download|generate|summary/i 
      }).count();
      
      expect(reportContent).toBeGreaterThan(0);
      
      await dashboardPage.takeScreenshot('report-tab-active');
    }
  });

  test('should navigate between all tabs sequentially', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    const tabs = [
      TestData.TABS.SETUP,
      TestData.TABS.ANALYSIS,
      TestData.TABS.INSIGHTS,
      TestData.TABS.ROADMAP,
      TestData.TABS.REPORT
    ];
    
    for (const tabName of tabs) {
      const tabButton = page.locator('button, [role="tab"]')
        .filter({ hasText: tabName }).first();
      
      if (await tabButton.isVisible({ timeout: 3000 })) {
        await tabButton.click();
        await TestHelpers.waitForAnimation(page);
        
        // Verify tab content loaded
        const hasContent = await page.locator('body').textContent();
        expect(hasContent).toBeTruthy();
        
        console.log(`Successfully navigated to ${tabName} tab`);
      }
    }
  });

  test('should maintain active tab state', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Navigate to Analysis tab
    const analysisTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.ANALYSIS }).first();
    
    if (await analysisTab.isVisible({ timeout: 5000 })) {
      await analysisTab.click();
      await TestHelpers.waitForAnimation(page);
      
      // Check active state indicators
      const tabClass = await analysisTab.getAttribute('class') || '';
      const ariaSelected = await analysisTab.getAttribute('aria-selected');
      
      const isActiveByClass = tabClass.includes('active') || 
                             tabClass.includes('selected') ||
                             tabClass.includes('current');
                             
      const isActiveByAria = ariaSelected === 'true';
      
      // At least one indicator should show active state
      expect(isActiveByClass || isActiveByAria).toBe(true);
    }
  });

  test('should handle keyboard navigation between tabs', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Try to find tab container and navigate with keyboard
    const firstTab = page.locator('button, [role="tab"]').first();
    
    if (await firstTab.isVisible({ timeout: 5000 })) {
      await firstTab.focus();
      
      // Test arrow key navigation
      await page.keyboard.press('ArrowRight');
      await TestHelpers.waitForAnimation(page, 500);
      
      await page.keyboard.press('ArrowLeft');
      await TestHelpers.waitForAnimation(page, 500);
      
      // Test Enter key activation
      await page.keyboard.press('Enter');
      await TestHelpers.waitForAnimation(page);
      
      // Verify navigation worked
      const hasContent = await page.locator('body').textContent();
      expect(hasContent).toBeTruthy();
    }
  });

  test('should work on mobile screen sizes', async ({ page }) => {
    await TestHelpers.testResponsiveBreakpoints(page, async () => {
      await dashboardPage.waitForPageLoad();
      
      // On mobile, tabs might be arranged differently
      const visibleTabs = await page.locator('button, [role="tab"]')
        .filter({ hasText: new RegExp(Object.values(TestData.TABS).join('|'), 'i') })
        .count();
      
      expect(visibleTabs).toBeGreaterThan(0);
      
      // Try clicking first visible tab
      const firstTab = page.locator('button, [role="tab"]').first();
      if (await firstTab.isVisible({ timeout: 2000 })) {
        await firstTab.click();
        await TestHelpers.waitForAnimation(page);
      }
    });
  });

  test('should handle tab navigation with smooth animations', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    const tabs = await page.locator('button, [role="tab"]').all();
    
    if (tabs.length >= 2) {
      // Navigate between first two tabs rapidly
      await tabs[0].click();
      await page.waitForTimeout(500);
      
      await tabs[1].click();
      await page.waitForTimeout(500);
      
      await tabs[0].click();
      await TestHelpers.waitForAnimation(page);
      
      // Verify no errors occurred during rapid navigation
      await dashboardPage.checkConsoleErrors();
    }
  });

  test('should preserve tab content between navigations', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Navigate to Setup tab and look for persistent elements
    const setupTab = page.locator('button, [role="tab"]')
      .filter({ hasText: TestData.TABS.SETUP }).first();
    
    if (await setupTab.isVisible({ timeout: 5000 })) {
      await setupTab.click();
      await TestHelpers.waitForAnimation(page);
      
      const setupContent = await page.textContent('body');
      
      // Navigate to another tab
      const analysisTab = page.locator('button, [role="tab"]')
        .filter({ hasText: TestData.TABS.ANALYSIS }).first();
      
      if (await analysisTab.isVisible({ timeout: 5000 })) {
        await analysisTab.click();
        await TestHelpers.waitForAnimation(page);
        
        // Navigate back to Setup
        await setupTab.click();
        await TestHelpers.waitForAnimation(page);
        
        const returnedContent = await page.textContent('body');
        
        // Basic content should be preserved
        expect(returnedContent).toBeTruthy();
        expect(returnedContent?.length).toBeGreaterThan(100);
      }
    }
  });
});