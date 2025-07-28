import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SetupTab } from '../page-objects/SetupTab';
import { TestData } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

test.describe('Accessibility Tests', () => {
  let dashboardPage: DashboardPage;
  let setupTab: SetupTab;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    setupTab = new SetupTab(page);
    await dashboardPage.goto();
  });

  test('should have proper heading structure', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check for heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
    
    // Should have at least one h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
    
    console.log('Headings found:', headings);
  });

  test('should support keyboard navigation', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Start keyboard navigation
    await page.keyboard.press('Tab');
    
    // Track focus progression
    const focusPath: string[] = [];
    
    for (let i = 0; i < 10; i++) {
      const focusedElement = await page.evaluate(() => {
        const focused = document.activeElement;
        if (focused) {
          return {
            tagName: focused.tagName,
            className: focused.className,
            textContent: focused.textContent?.trim().slice(0, 50),
            type: focused.getAttribute('type'),
            role: focused.getAttribute('role')
          };
        }
        return null;
      });
      
      if (focusedElement) {
        focusPath.push(`${focusedElement.tagName}${focusedElement.role ? `[${focusedElement.role}]` : ''}`);
      }
      
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }
    
    console.log('Focus path:', focusPath);
    expect(focusPath.length).toBeGreaterThan(0);
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check for interactive elements with proper labels
    const interactiveElements = await page.locator('button, input, select, [role="button"], [role="tab"]').all();
    
    let labeledElements = 0;
    
    for (const element of interactiveElements) {
      const ariaLabel = await element.getAttribute('aria-label');
      const ariaLabelledby = await element.getAttribute('aria-labelledby');
      const title = await element.getAttribute('title');
      const textContent = await element.textContent();
      const placeholder = await element.getAttribute('placeholder');
      
      const hasLabel = ariaLabel || ariaLabelledby || title || 
                      (textContent && textContent.trim().length > 0) || 
                      placeholder;
      
      if (hasLabel) {
        labeledElements++;
      }
    }
    
    const labelPercentage = (labeledElements / interactiveElements.length) * 100;
    console.log(`Labeled interactive elements: ${labeledElements}/${interactiveElements.length} (${labelPercentage.toFixed(1)}%)`);
    
    // At least 70% of interactive elements should have labels
    expect(labelPercentage).toBeGreaterThan(70);
  });

  test('should have proper contrast ratios', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Test both light and dark themes
    const themes = ['light', 'dark'];
    
    for (const theme of themes) {
      // Set theme
      if (theme === 'dark') {
        await dashboardPage.toggleTheme();
        await TestHelpers.waitForAnimation(page);
      }
      
      // Check text contrast
      const textElements = await page.locator('p, span, div, button, h1, h2, h3, h4, h5, h6')
        .filter({ hasText: /.+/ })
        .first();
      
      if (await textElements.isVisible({ timeout: 2000 })) {
        const styles = await textElements.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            color: computed.color,
            backgroundColor: computed.backgroundColor,
            fontSize: computed.fontSize
          };
        });
        
        console.log(`${theme} theme text styles:`, styles);
        
        // Basic check: color should not be same as background
        expect(styles.color).not.toBe(styles.backgroundColor);
      }
    }
  });

  test('should support screen reader navigation', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check for landmarks
    const landmarks = await page.locator('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"]').count();
    console.log(`Landmarks found: ${landmarks}`);
    
    // Check for tab structure
    const tabList = await page.locator('[role="tablist"]').count();
    const tabs = await page.locator('[role="tab"]').count();
    const tabPanels = await page.locator('[role="tabpanel"]').count();
    
    console.log(`Tab structure - Lists: ${tabList}, Tabs: ${tabs}, Panels: ${tabPanels}`);
    
    // If tabs exist, they should have proper structure
    if (tabs > 0) {
      expect(tabList).toBeGreaterThan(0);
    }
  });

  test('should handle focus management', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Navigate to Setup tab and check focus
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Focus should move to tab content
    const focusedAfterClick = await page.evaluate(() => {
      const focused = document.activeElement;
      return focused ? focused.tagName : null;
    });
    
    console.log('Focus after tab click:', focusedAfterClick);
    
    // Focus should be managed (not lost)
    expect(focusedAfterClick).toBeTruthy();
  });

  test('should provide text alternatives for images', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check all images have alt text
    const images = await page.locator('img').all();
    
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      const ariaLabel = await img.getAttribute('aria-label');
      const ariaLabelledby = await img.getAttribute('aria-labelledby');
      
      const hasTextAlternative = alt !== null || ariaLabel || ariaLabelledby;
      
      if (!hasTextAlternative) {
        const src = await img.getAttribute('src');
        console.warn(`Image without text alternative: ${src}`);
      }
    }
    
    // All images should have text alternatives
    const imagesWithAlt = await page.locator('img[alt], img[aria-label], img[aria-labelledby]').count();
    const totalImages = images.length;
    
    if (totalImages > 0) {
      expect(imagesWithAlt).toBe(totalImages);
    }
  });

  test('should support high contrast mode', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Simulate high contrast mode
    await page.addStyleTag({
      content: `
        @media (prefers-contrast: high) {
          * {
            background: white !important;
            color: black !important;
            border: 1px solid black !important;
          }
        }
      `
    });
    
    // Verify content is still visible and functional
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Navigation should still work
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    await dashboardPage.takeScreenshot('high-contrast');
  });

  test('should handle reduced motion preferences', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Navigation should still work without animations
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    await dashboardPage.clickTab(TestData.TABS.ANALYSIS);
    
    // Theme toggle should work
    await dashboardPage.toggleTheme();
    
    // Verify no console errors
    await dashboardPage.checkConsoleErrors();
  });

  test('should support voice control', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Check that clickable elements have proper click targets
    const clickableElements = await page.locator('button, [role="button"], [role="tab"], a').all();
    
    let properSizedElements = 0;
    
    for (const element of clickableElements) {
      if (await element.isVisible({ timeout: 1000 })) {
        const box = await element.boundingBox();
        if (box) {
          // WCAG recommendation: minimum 44x44px touch target
          if (box.width >= 44 && box.height >= 44) {
            properSizedElements++;
          }
        }
      }
    }
    
    const properSizePercentage = (properSizedElements / clickableElements.length) * 100;
    console.log(`Properly sized click targets: ${properSizedElements}/${clickableElements.length} (${properSizePercentage.toFixed(1)}%)`);
    
    // At least 80% should meet size requirements
    expect(properSizePercentage).toBeGreaterThan(80);
  });

  test('should handle form accessibility', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Check form inputs have proper labels
    const inputs = await page.locator('input, select, textarea').all();
    
    for (const input of inputs) {
      if (await input.isVisible({ timeout: 2000 })) {
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledby = await input.getAttribute('aria-labelledby');
        const placeholder = await input.getAttribute('placeholder');
        
        let hasLabel = false;
        
        if (id) {
          const label = await page.locator(`label[for="${id}"]`).count();
          hasLabel = label > 0;
        }
        
        hasLabel = hasLabel || !!ariaLabel || !!ariaLabelledby || !!placeholder;
        
        if (!hasLabel) {
          const inputType = await input.getAttribute('type');
          console.warn(`Input without label: type=${inputType}`);
        }
      }
    }
  });

  test('should provide error messaging', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    // Try to submit form without required fields
    const submitButton = page.locator('button').filter({ hasText: /start|submit|analyze/i }).first();
    
    if (await submitButton.isVisible({ timeout: 5000 })) {
      await submitButton.click();
      await page.waitForTimeout(1000);
      
      // Look for error messages
      const errorMessages = await page.locator('[role="alert"], .error, .invalid, [aria-invalid="true"]').count();
      
      console.log(`Error message elements: ${errorMessages}`);
      
      // If validation occurs, it should be accessible
      if (errorMessages > 0) {
        const alertElements = await page.locator('[role="alert"]').count();
        expect(alertElements).toBeGreaterThan(0);
      }
    }
  });

  test('should support zoom up to 200%', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Simulate 200% zoom
    await page.setViewportSize({ width: 640, height: 360 }); // Half size = 200% zoom effect
    
    // Content should still be accessible
    await expect(dashboardPage.appContainer).toBeVisible();
    
    // Navigation should work at high zoom
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThan(0);
    
    // Try basic interaction
    await dashboardPage.clickTab(TestData.TABS.SETUP);
    
    await dashboardPage.takeScreenshot('200-percent-zoom');
  });

  test('should have proper skip links', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Look for skip navigation links
    const skipLinks = await page.locator('a[href*="#"], [role="button"]')
      .filter({ hasText: /skip|jump to|go to main/i })
      .count();
    
    console.log(`Skip links found: ${skipLinks}`);
    
    // While not required, skip links improve accessibility
    // This is more informational than a strict requirement
  });

  test('should complete accessibility workflow', async ({ page }) => {
    await dashboardPage.waitForPageLoad();
    
    // Complete workflow using only keyboard
    await page.keyboard.press('Tab');
    
    // Navigate to setup (find setup tab and activate)
    let tabFound = false;
    for (let i = 0; i < 15; i++) {
      const focusedText = await page.evaluate(() => {
        const focused = document.activeElement;
        return focused?.textContent?.trim().toLowerCase() || '';
      });
      
      if (focusedText.includes('setup')) {
        await page.keyboard.press('Enter');
        tabFound = true;
        break;
      }
      
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }
    
    console.log(`Setup tab found via keyboard: ${tabFound}`);
    
    // If setup was found, try to interact with form
    if (tabFound) {
      await TestHelpers.waitForAnimation(page);
      
      // Find and fill brand input
      for (let i = 0; i < 10; i++) {
        await page.keyboard.press('Tab');
        
        const isInput = await page.evaluate(() => {
          const focused = document.activeElement;
          return focused?.tagName === 'INPUT' || focused?.tagName === 'TEXTAREA';
        });
        
        if (isInput) {
          await page.keyboard.type('Accessibility Test Brand');
          break;
        }
      }
    }
    
    await dashboardPage.takeScreenshot('keyboard-accessibility');
  });
});