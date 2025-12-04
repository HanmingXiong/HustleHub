import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should load home page', async ({ page }) => {
    await page.goto('/');
    // Should redirect to auth or show home
    await page.waitForLoadState('networkidle');
    expect(page.url()).toMatch(/\/(auth|home)/);
  });

  test('should load auth page', async ({ page }) => {
    await page.goto('/auth');
    await expect(page.locator('h2:has-text("Login")')).toBeVisible();
  });

  test('should load financial literacy page', async ({ page }) => {
    await page.goto('/financial-literacy');
    await page.waitForLoadState('networkidle');
    // Page should load (may redirect to auth if protected)
    expect(page.url()).toMatch(/\/(financial-literacy|auth)/);
  });
});
