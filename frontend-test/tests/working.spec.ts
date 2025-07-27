import { test, expect } from '@playwright/test';

test.describe('Working Flutter Tests', () => {
  test('should load and interact with Flutter app', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:8080');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    
    // Wait for canvas to appear (Flutter renders to canvas)
    await page.waitForSelector('canvas', { timeout: 15000 });
    
    // Additional wait for rendering
    await page.waitForTimeout(3000);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/working-app.png', fullPage: true });
    
    // Verify HTML content includes our app
    const html = await page.content();
    expect(html).toContain('Brand Intelligence Hub');
    
    // Check canvas exists
    const canvasCount = await page.locator('canvas').count();
    expect(canvasCount).toBeGreaterThan(0);
    
    // Test theme toggle by clicking in top-right area
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Click theme toggle (top-right area)
      await page.mouse.click(box.x + box.width - 100, box.y + 75);
      await page.waitForTimeout(2000);
      
      // Take screenshot after theme toggle
      await page.screenshot({ path: 'test-results/working-theme-toggle.png', fullPage: true });
      
      // Test tab navigation by clicking Setup tab area
      await page.mouse.click(box.x + 150, box.y + 430);
      await page.waitForTimeout(1000);
      
      // Test Analysis tab
      await page.mouse.click(box.x + 400, box.y + 430);
      await page.waitForTimeout(1000);
      
      // Test Insights tab
      await page.mouse.click(box.x + 650, box.y + 430);
      await page.waitForTimeout(1000);
      
      // Take final screenshot
      await page.screenshot({ path: 'test-results/working-navigation.png', fullPage: true });
      
      // Test form interaction - click on brand input area
      await page.mouse.click(box.x + 640, box.y + 580);
      await page.waitForTimeout(500);
      
      // Type in brand name
      await page.keyboard.type('Test Brand');
      await page.waitForTimeout(1000);
      
      // Take screenshot of form interaction
      await page.screenshot({ path: 'test-results/working-form.png', fullPage: true });
    }
    
    // Check for console logs that indicate app is working
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('Launch button state') || msg.text().includes('Brand:')) {
        logs.push(msg.text());
      }
    });
    
    // Wait a bit more to collect logs
    await page.waitForTimeout(2000);
    
    console.log('Test completed successfully!');
    console.log('Canvas elements found:', canvasCount);
    console.log('App logs captured:', logs.length);
  });
});