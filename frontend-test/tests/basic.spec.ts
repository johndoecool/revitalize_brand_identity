import { test, expect } from '@playwright/test';

test.describe('Basic App Loading', () => {
  test('should load Flutter web app', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:8080');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Wait for Flutter to initialize
    await page.waitForFunction(() => {
      return document.querySelector('flt-glass-pane') !== null;
    }, { timeout: 15000 });
    
    // Wait for app content
    await page.waitForFunction(() => {
      const content = document.body.textContent || '';
      return content.includes('Brand Intelligence Hub') || content.includes('Setup');
    }, { timeout: 15000 });
    
    // Take a screenshot
    await page.screenshot({ path: 'test-results/basic-app-loading.png' });
    
    // Check page title
    await expect(page).toHaveTitle(/Brand Intelligence Hub|brand_intelligence_hub/i);
    
    // Verify content is present
    const content = await page.textContent('body');
    expect(content).toContain('Setup');
    
    console.log('Page content includes:', content?.slice(0, 200));
  });
});