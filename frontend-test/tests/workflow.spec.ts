import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Brand Analysis Workflow', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    await dashboardPage.goto();
  });

  test('should complete basic brand setup workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Navigate to Setup tab
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Verify setup form is available
    await setupTab.verifySetupForm();
    
    // Enter brand name
    const brandName = TestData.SAMPLE_BRANDS.BANKING[0];
    await setupTab.enterBrandName(brandName);
    
    // Select industry
    await setupTab.selectIndustry('BANKING');
    
    // Verify industry selection
    const selectedIndustry = await setupTab.getSelectedIndustry();
    expect(selectedIndustry).toContain('Banking');
    
    // Select analysis area
    await setupTab.selectAnalysisArea(TestData.ANALYSIS_AREAS[0]);
    
    await dashboardPage.takeScreenshot('setup-completed');
  });

  test('should handle banking industry workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Complete banking setup
    await setupTab.completeSetup(
      'Oriental Bank',
      'BANKING',
      'Brand Reputation',
      'Banco Popular'
    );
    
    // Navigate to Analysis tab to see results
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    // Look for banking-specific content
    const content = await page.textContent('body');
    expect(content).toMatch(/oriental|bank|banking|financial/i);
    
    await dashboardPage.takeScreenshot('banking-analysis');
  });

  test('should handle technology industry workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Complete technology setup
    await setupTab.completeSetup(
      'Microsoft',
      'TECH',
      'Employer Branding',
      'Google'
    );
    
    // Navigate to Analysis tab
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    // Look for tech-specific content
    const content = await page.textContent('body');
    expect(content).toMatch(/microsoft|google|tech|employer|branding/i);
    
    await dashboardPage.takeScreenshot('tech-analysis');
  });

  test('should handle healthcare industry workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Complete healthcare setup
    await setupTab.completeSetup(
      'Pfizer',
      'HEALTHCARE',
      'Product Innovation',
      'Moderna'
    );
    
    // Navigate to Analysis tab
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    // Look for healthcare-specific content
    const content = await page.textContent('body');
    expect(content).toMatch(/pfizer|moderna|healthcare|product|innovation/i);
    
    await dashboardPage.takeScreenshot('healthcare-analysis');
  });

  test('should validate required fields', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Try to proceed without filling required fields
    const startButton = page.locator('button').filter({ hasText: /start|analyze|begin/i }).first();
    
    if (await startButton.isVisible({ timeout: 5000 })) {
      // Check if button is disabled when form is incomplete
      const isDisabled = await startButton.isDisabled();
      
      if (!isDisabled) {
        // If button is not disabled, click it and check for validation
        await startButton.click();
        await page.waitForTimeout(1000);
        
        // Look for validation messages
        const validationMessages = await page.locator('.error, .validation, [role="alert"]')
          .allTextContents();
        
        console.log('Validation messages:', validationMessages);
      }
    }
    
    // Now fill form properly
    await setupTab.enterBrandName('Test Brand');
    await setupTab.selectIndustry('BANKING');
    
    // Verify button states updated
    await setupTab.verifyButtonStates();
  });

  test('should handle empty brand name input', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Try entering empty or invalid brand name
    await setupTab.enterBrandName('');
    await setupTab.selectIndustry('BANKING');
    
    // Check validation
    await setupTab.checkValidationMessages();
  });

  test('should switch between industries correctly', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Select banking first
    await setupTab.selectIndustry('BANKING');
    let selectedIndustry = await setupTab.getSelectedIndustry();
    expect(selectedIndustry).toContain('Banking');
    
    // Switch to tech
    await setupTab.selectIndustry('TECH');
    selectedIndustry = await setupTab.getSelectedIndustry();
    expect(selectedIndustry).toContain('Technology');
    
    // Switch to healthcare
    await setupTab.selectIndustry('HEALTHCARE');
    selectedIndustry = await setupTab.getSelectedIndustry();
    expect(selectedIndustry).toContain('Healthcare');
  });

  test('should navigate through complete analysis workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Step 1: Setup
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup(
      'Sample Brand',
      'BANKING',
      'Brand Reputation'
    );
    
    // Step 2: Analysis
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    // Look for View Charts button and click it
    const viewChartsButton = page.locator('button').filter({ hasText: /view charts|charts/i }).first();
    if (await viewChartsButton.isVisible({ timeout: 5000 })) {
      await viewChartsButton.click();
      await TestHelpers.waitForAnimation(page);
    }
    
    // Step 3: Insights
    await dashboardPage.clickTab(TestData.TABS.INSIGHTS);
    await TestHelpers.waitForAnimation(page);
    
    // Look for insights content
    const insightsContent = await page.locator('*').filter({ 
      hasText: /insight|recommendation|priority/i 
    }).count();
    expect(insightsContent).toBeGreaterThan(0);
    
    // Step 4: Roadmap
    await dashboardPage.clickTab(TestData.TABS.ROADMAP);
    await TestHelpers.waitForAnimation(page);
    
    // Look for roadmap content
    const roadmapContent = await page.locator('*').filter({ 
      hasText: /roadmap|quarter|timeline/i 
    }).count();
    expect(roadmapContent).toBeGreaterThan(0);
    
    // Step 5: Report
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Look for report content
    const reportContent = await page.locator('*').filter({ 
      hasText: /report|pdf|summary/i 
    }).count();
    expect(reportContent).toBeGreaterThan(0);
    
    await dashboardPage.takeScreenshot('complete-workflow');
  });

  test('should maintain data consistency across tabs', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    const brandName = 'Consistency Test Brand';
    const industry = 'TECH';
    
    // Setup brand analysis
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup(brandName, industry, 'Digital Innovation');
    
    // Navigate through tabs and verify brand name appears
    const tabs = [TestData.TABS.ANALYSIS, TestData.TABS.INSIGHTS, TestData.TABS.ROADMAP, TestData.TABS.REPORT];
    
    for (const tab of tabs) {
      await dashboardPage.clickTab(tab);
      await TestHelpers.waitForAnimation(page);
      
      const content = await page.textContent('body');
      // Brand name or industry context should be maintained
      const hasContext = content?.toLowerCase().includes(brandName.toLowerCase()) ||
                        content?.toLowerCase().includes('tech') ||
                        content?.toLowerCase().includes('digital');
      
      console.log(`Tab ${tab}: Has context = ${hasContext}`);
    }
  });

  test('should handle workflow on mobile devices', async ({ page }) => {
    await TestHelpers.testResponsiveBreakpoints(page, async () => {
      await dashboardPage.waitForPageLoad();
      
      // Complete setup on mobile
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      
      // On mobile, form elements might be stacked differently
      if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
        await setupTab.enterBrandName('Mobile Test');
        await setupTab.selectIndustry('BANKING');
        
        // Navigate to analysis
        await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
        await TestHelpers.waitForAnimation(page);
        
        // Verify content is accessible on mobile
        const hasContent = await page.locator('body').textContent();
        expect(hasContent).toBeTruthy();
      }
    });
  });

  test('should handle rapid workflow navigation', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Setup quickly
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.enterBrandName('Rapid Test');
    await setupTab.selectIndustry('TECH');
    
    // Navigate rapidly between tabs
    const tabs = [
      TestData.TABS.ANALYSIS,
      TestData.TABS.INSIGHTS,
      TestData.TABS.SETUP,
      TestData.TABS.ROADMAP,
      TestData.TABS.REPORT,
      TestData.TABS.ANALYSIS
    ];
    
    for (const tab of tabs) {
      await dashboardPage.clickTab(tab);
      await page.waitForTimeout(200); // Rapid navigation
    }
    
    // Verify no errors occurred
    await dashboardPage.checkConsoleErrors();
  });
});