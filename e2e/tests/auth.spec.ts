import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth');
  });

  test('should load auth page', async ({ page }) => {
    // Should see login form by default
    await expect(page.locator('input[name="loginEmail"]')).toBeVisible();
    await expect(page.locator('input[name="loginPassword"]')).toBeVisible();
  });

  test('should switch between login and register tabs', async ({ page }) => {
    // Should start on login tab
    await expect(page.locator('input[name="loginEmail"]')).toBeVisible();
    
    // Switch to register
    await page.click('button:has-text("Register")');
    await expect(page.locator('input[name="regUsername"]')).toBeVisible();
    await expect(page.locator('input[name="regEmail"]')).toBeVisible();
    
    // Switch back to login
    await page.click('button:has-text("Login")');
    await expect(page.locator('input[name="loginEmail"]')).toBeVisible();
  });

  test('should fill registration form', async ({ page }) => {
    await page.click('button:has-text("Register")');
    
    const timestamp = Date.now();
    await page.fill('input[name="regUsername"]', `testuser${timestamp}`);
    await page.fill('input[name="regEmail"]', `test${timestamp}@example.com`);
    await page.fill('input[name="regPassword"]', 'TestPass123!');
    await page.check('input[name="regRole"][value="applicant"]');
    
    // Verify form is filled
    await expect(page.locator('input[name="regUsername"]')).toHaveValue(`testuser${timestamp}`);
    await expect(page.locator('input[name="regRole"][value="applicant"]')).toBeChecked();
  });

  test('should fill login form', async ({ page }) => {
    await page.fill('input[name="loginEmail"]', 'test@example.com');
    await page.fill('input[name="loginPassword"]', 'TestPass123!');
    
    // Verify form is filled
    await expect(page.locator('input[name="loginEmail"]')).toHaveValue('test@example.com');
    await expect(page.locator('input[name="loginPassword"]')).toHaveValue('TestPass123!');
  });
});
