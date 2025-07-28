import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';

test.describe('Smoke Tests', () => {
  test('should load application successfully', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    
    // Basic smoke test - app should load
    await expect(page).toHaveTitle(/Brand Intelligence Hub/i);
    await expect(dashboardPage.appContainer).toBeVisible({ timeout: 15000 });
    
    // Should not have critical console errors
    await dashboardPage.checkConsoleErrors();
  });

  test('should have working navigation', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    
    // Should be able to navigate between tabs
    const visibleTabs = await dashboardPage.getVisibleTabs();
    expect(visibleTabs.length).toBeGreaterThan(0);
    
    // Try clicking first tab
    if (visibleTabs.length > 0) {
      await dashboardPage.clickTab(visibleTabs[0]);
    }
  });

  test('should handle basic theme functionality', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    
    // Theme toggle should be available
    if (await dashboardPage.themeToggle.isVisible({ timeout: 5000 })) {
      await dashboardPage.toggleTheme();
    }
  });
});