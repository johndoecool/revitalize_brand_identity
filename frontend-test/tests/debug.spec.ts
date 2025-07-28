import { test, expect } from '@playwright/test';

test('Debug Flutter loading', async ({ page }) => {
  // Monitor console messages
  page.on('console', msg => console.log('CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  // Navigate to the app
  await page.goto('http://localhost:8080');
  
  // Wait a bit
  await page.waitForTimeout(5000);
  
  // Check what's in the DOM
  const html = await page.content();
  console.log('HTML length:', html.length);
  console.log('HTML includes Brand:', html.includes('Brand Intelligence Hub'));
  console.log('HTML includes Setup:', html.includes('Setup'));
  
  // Check for flt-glass-pane
  const glassPane = await page.locator('flt-glass-pane').count();
  console.log('Glass pane elements:', glassPane);
  
  // Check body text content
  const bodyText = await page.textContent('body');
  console.log('Body text content:', bodyText?.slice(0, 500));
  
  // Check for canvas elements
  const canvasCount = await page.locator('canvas').count();
  console.log('Canvas elements:', canvasCount);
  
  // Take screenshot
  await page.screenshot({ path: 'test-results/debug-flutter.png', fullPage: true });
  
  // Try to wait for network idle
  await page.waitForLoadState('networkidle');
  
  // Check again after network idle
  const bodyTextAfter = await page.textContent('body');
  console.log('Body text after network idle:', bodyTextAfter?.slice(0, 500));
});