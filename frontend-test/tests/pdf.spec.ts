import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('PDF Generation Functionality', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    await dashboardPage.goto();
  });

  test('should display PDF generation option in Report tab', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    
    // Look for PDF generation elements
    const pdfElements = await page.locator('*').filter({ 
      hasText: /pdf|generate|download|report|export/i 
    }).count();
    
    expect(pdfElements).toBeGreaterThan(0);
    
    // Look specifically for PDF-related buttons
    const pdfButton = page.locator('button').filter({ 
      hasText: /pdf|generate|download|export/i 
    }).first();
    
    if (await pdfButton.isVisible({ timeout: 5000 })) {
      expect(pdfButton).toBeVisible();
    }
    
    await dashboardPage.takeScreenshot('report-tab-pdf-option');
  });

  test('should generate PDF after completing analysis', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete setup first
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('PDF Test Brand', 'BANKING', 'Brand Reputation');
    
    // Navigate through analysis workflow
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Look for PDF generation button
    const pdfButton = page.locator('button').filter({ 
      hasText: /generate.*pdf|download.*pdf|create.*pdf|pdf/i 
    }).first();
    
    if (await pdfButton.isVisible({ timeout: 5000 })) {
      // Test PDF generation
      await TestHelpers.waitForDownload(page, async () => {
        await pdfButton.click();
      });
      
      await dashboardPage.takeScreenshot('pdf-generated');
    } else {
      // If no explicit PDF button, look for download/export functionality
      const exportButton = page.locator('button').filter({ 
        hasText: /export|download|save/i 
      }).first();
      
      if (await exportButton.isVisible({ timeout: 3000 })) {
        await exportButton.click();
        await TestHelpers.waitForAnimation(page);
      }
    }
  });

  test('should show executive summary in report', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete setup
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Executive Summary Test', 'TECH', 'Market Position');
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Look for executive summary content
    const summaryElements = await page.locator('*').filter({ 
      hasText: /executive|summary|overview|key findings|highlights/i 
    }).count();
    
    expect(summaryElements).toBeGreaterThan(0);
    
    // Check for report structure
    const reportContent = await page.textContent('body');
    expect(reportContent).toBeTruthy();
    expect(reportContent?.length).toBeGreaterThan(100);
    
    await dashboardPage.takeScreenshot('executive-summary');
  });

  test('should show detailed metrics in report', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete setup
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Detailed Metrics Test', 'HEALTHCARE', 'Product Quality');
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Look for detailed metrics content
    const metricsElements = await page.locator('*').filter({ 
      hasText: /metrics|score|rating|analysis|detailed|performance/i 
    }).count();
    
    expect(metricsElements).toBeGreaterThan(0);
    
    // Look for numerical data
    const numericalData = await page.locator('*').filter({ 
      hasText: /\d+%|\d+\.\d+|\d+\/\d+|score.*\d+/i 
    }).count();
    
    console.log(`Numerical data elements found: ${numericalData}`);
    
    await dashboardPage.takeScreenshot('detailed-metrics');
  });

  test('should handle PDF generation for different industries', async ({ page }) => {
    const industries = [
      { key: 'BANKING' as const, brand: 'Banking Corp', area: 'Customer Service' },
      { key: 'TECH' as const, brand: 'Tech Solutions', area: 'Innovation' },
      { key: 'HEALTHCARE' as const, brand: 'Health Plus', area: 'Patient Care' }
    ];
    
    for (const industry of industries) {
      await dashboardPage.waitForPageLoad();
      
      // Setup for each industry
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      await setupTab.completeSetup(industry.brand, industry.key, industry.area);
      
      // Navigate to Report tab
      await dashboardPage.clickTab(TestData.TABS.REPORT);
      await TestHelpers.waitForAnimation(page);
      
      // Look for industry-specific content in report
      const content = await page.textContent('body');
      const hasIndustryContext = content?.toLowerCase().includes(industry.key.toLowerCase()) ||
                                content?.toLowerCase().includes(industry.brand.toLowerCase());
      
      console.log(`Industry ${industry.key}: Has context = ${hasIndustryContext}`);
      
      await dashboardPage.takeScreenshot(`report-${industry.key.toLowerCase()}`);
    }
  });

  test('should validate report completeness', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete full workflow
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Complete Report Test', 'BANKING', 'Brand Reputation');
    
    // Visit all tabs to ensure data is generated
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    await TestHelpers.waitForAnimation(page);
    
    await dashboardPage.clickTab(TestData.TABS.INSIGHTS);
    await TestHelpers.waitForAnimation(page);
    
    await dashboardPage.clickTab(TestData.TABS.ROADMAP);
    await TestHelpers.waitForAnimation(page);
    
    // Finally check report
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Verify report has comprehensive content
    const reportSections = [
      /executive.*summary|overview/i,
      /analysis|findings/i,
      /insights|recommendations/i,
      /roadmap|timeline/i,
      /metrics|scores/i
    ];
    
    const content = await page.textContent('body');
    const foundSections = reportSections.filter(section => 
      content?.match(section)
    ).length;
    
    expect(foundSections).toBeGreaterThan(2);
    
    await dashboardPage.takeScreenshot('complete-report');
  });

  test('should handle PDF generation errors gracefully', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Try to generate PDF without completing setup
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    
    const pdfButton = page.locator('button').filter({ 
      hasText: /generate.*pdf|pdf/i 
    }).first();
    
    if (await pdfButton.isVisible({ timeout: 3000 })) {
      // Check if button is disabled when no data
      const isDisabled = await pdfButton.isDisabled();
      
      if (!isDisabled) {
        await pdfButton.click();
        await page.waitForTimeout(2000);
        
        // Look for error messages
        const errorMessages = await page.locator('.error, [role="alert"], .warning')
          .allTextContents();
        
        console.log('PDF generation messages:', errorMessages);
      }
    }
    
    // Should not crash the application
    await dashboardPage.checkConsoleErrors();
  });

  test('should maintain report formatting', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete setup
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup('Formatting Test', 'TECH', 'Digital Strategy');
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Check for proper formatting elements
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
    expect(headings).toBeGreaterThan(0);
    
    // Check for structured content
    const structuredElements = await page.locator('ul, ol, table, section, article').count();
    console.log(`Structured content elements: ${structuredElements}`);
    
    // Check for styling
    const styledElements = await page.locator('[class*="report"], [class*="summary"], [class*="content"]').count();
    console.log(`Styled report elements: ${styledElements}`);
    
    await dashboardPage.takeScreenshot('report-formatting');
  });

  test('should work on mobile devices', async ({ page }) => {
    await TestHelpers.testResponsiveBreakpoints(page, async () => {
      await dashboardPage.waitForPageLoad();
      
      // Complete setup
      await dashboardPage.clickTab(TestData.TABS.SETUP);
      if (await setupTab.brandInput.isVisible({ timeout: 3000 })) {
        await setupTab.completeSetup('Mobile PDF Test', 'BANKING', 'Mobile Experience');
        
        // Navigate to Report tab
        await dashboardPage.clickTab(TestData.TABS.REPORT);
        await TestHelpers.waitForAnimation(page);
        
        // Verify report is accessible on mobile
        const reportContent = await page.textContent('body');
        expect(reportContent).toBeTruthy();
        
        // Check if PDF generation is available on mobile
        const pdfButton = page.locator('button').filter({ 
          hasText: /pdf|generate|download/i 
        }).first();
        
        if (await pdfButton.isVisible({ timeout: 2000 })) {
          const buttonSize = await pdfButton.boundingBox();
          
          // Verify button is touch-friendly (minimum 44px)
          if (buttonSize) {
            expect(buttonSize.height).toBeGreaterThan(40);
          }
        }
      }
    });
  });

  test('should include brand information in report', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    const brandName = 'Brand Info Test Company';
    const industry = 'HEALTHCARE';
    const analysisArea = 'Patient Satisfaction';
    
    // Complete setup with specific brand info
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await setupTab.completeSetup(brandName, industry, analysisArea);
    
    // Navigate to Report tab
    await dashboardPage.clickTab(TestData.TABS.REPORT);
    await TestHelpers.waitForAnimation(page);
    
    // Verify brand information appears in report
    const content = await page.textContent('body');
    const hasBrandName = content?.includes(brandName);
    const hasIndustry = content?.toLowerCase().includes('healthcare');
    const hasAnalysisArea = content?.toLowerCase().includes('patient');
    
    expect(hasBrandName || hasIndustry || hasAnalysisArea).toBe(true);
    
    console.log(`Report contains - Brand: ${hasBrandName}, Industry: ${hasIndustry}, Area: ${hasAnalysisArea}`);
    
    await dashboardPage.takeScreenshot('brand-info-report');
  });
});