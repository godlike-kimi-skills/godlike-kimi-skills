/**
 * 多浏览器测试示例
 * 
 * 展示Playwright如何同时在多个浏览器上运行测试
 */

const { test, expect } = require('@playwright/test');

// ============================================
// 基础多浏览器配置测试
// ============================================

test.describe('Cross-Browser Testing', () => {
  
  test('homepage should work in all browsers', async ({ page }) => {
    // 这个测试会在 playwright.config.js 中配置的所有浏览器上运行
    await page.goto('https://example.com');
    
    // 验证页面标题
    await expect(page).toHaveTitle(/Example/);
    
    // 验证主要内容存在
    await expect(page.locator('h1')).toBeVisible();
  });
  
  test('navigation should work consistently', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 点击导航链接
    await page.click('nav a[href="/about"]');
    
    // 验证导航成功
    await expect(page).toHaveURL(/about/);
    await expect(page.locator('h1')).toContainText('About');
  });
});

// ============================================
// 浏览器特定测试
// ============================================

test.describe('Chromium-specific tests', () => {
  test.use({ browserName: 'chromium' });
  
  test('Chrome DevTools Protocol features', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 使用 CDP 获取性能指标
    const client = await page.context().newCDPSession(page);
    const metrics = await client.send('Performance.getMetrics');
    
    console.log('Performance Metrics:', metrics);
  });
  
  test('Chrome extension testing', async ({ browser }) => {
    // 加载扩展
    const context = await browser.newContext({
      args: [
        `--disable-extensions-except=/path/to/extension`,
        `--load-extension=/path/to/extension`
      ]
    });
    
    const page = await context.newPage();
    await page.goto('https://example.com');
    
    // 测试扩展功能
    await expect(page.locator('#extension-button')).toBeVisible();
    
    await context.close();
  });
});

test.describe('Firefox-specific tests', () => {
  test.use({ browserName: 'firefox' });
  
  test('Firefox specific features', async ({ page }) => {
    await page.goto('https://example.com');
    
    // Firefox 特定的测试逻辑
    const userAgent = await page.evaluate(() => navigator.userAgent);
    expect(userAgent).toContain('Firefox');
  });
});

test.describe('WebKit-specific tests', () => {
  test.use({ browserName: 'webkit' });
  
  test('Safari-like behavior', async ({ page }) => {
    await page.goto('https://example.com');
    
    // WebKit 特定的测试
    const userAgent = await page.evaluate(() => navigator.userAgent);
    expect(userAgent).toContain('Safari');
  });
});

// ============================================
// 条件执行测试
// ============================================

test.describe('Conditional Browser Tests', () => {
  
  test('runs only on Chromium', async ({ browserName, page }) => {
    test.skip(browserName !== 'chromium', 'Chromium-only test');
    
    await page.goto('https://example.com');
    
    // Chromium 特有的功能测试
    const isChrome = await page.evaluate(() => {
      return 'chrome' in window && window.chrome !== undefined;
    });
    expect(isChrome).toBe(true);
  });
  
  test('runs only on Firefox', async ({ browserName, page }) => {
    test.skip(browserName !== 'firefox', 'Firefox-only test');
    
    await page.goto('https://example.com');
    
    // 测试 Firefox 特有的行为
  });
  
  test('skip on WebKit', async ({ browserName, page }) => {
    test.skip(browserName === 'webkit', 'Not supported on WebKit');
    
    await page.goto('https://example.com');
    
    // 在非 WebKit 浏览器上运行的测试
  });
  
  test('fixme on Firefox', async ({ browserName, page }) => {
    test.fixme(browserName === 'firefox', 'Known issue on Firefox');
    
    await page.goto('https://example.com');
    
    // 在 Firefox 上有已知问题的测试
  });
});

// ============================================
// 视觉回归测试
// ============================================

test.describe('Visual Regression', () => {
  
  test('homepage visual consistency', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 等待所有图片加载
    await page.waitForLoadState('networkidle');
    
    // 全页截图对比
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      threshold: 0.2
    });
  });
  
  test('component visual consistency', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 特定元素截图
    const header = page.locator('header');
    await expect(header).toHaveScreenshot('header.png', {
      threshold: 0.2,
      mask: [page.locator('.current-time')] // 掩码动态内容
    });
  });
  
  test('responsive layouts', async ({ page }) => {
    // 测试不同视口大小
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];
    
    await page.goto('https://example.com');
    
    for (const viewport of viewports) {
      await page.setViewportSize({ 
        width: viewport.width, 
        height: viewport.height 
      });
      
      await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, {
        fullPage: true
      });
    }
  });
});

// ============================================
// 手动创建浏览器实例
// ============================================

test.describe('Manual Browser Management', () => {
  
  test('test across browsers manually', async () => {
    const { chromium, firefox, webkit } = require('@playwright/test');
    
    const browsers = [
      { name: 'Chromium', instance: chromium },
      { name: 'Firefox', instance: firefox },
      { name: 'WebKit', instance: webkit }
    ];
    
    for (const browserInfo of browsers) {
      const browser = await browserInfo.instance.launch();
      const context = await browser.newContext();
      const page = await context.newPage();
      
      await page.goto('https://example.com');
      
      // 在每个浏览器上运行相同的断言
      await expect(page.locator('h1')).toBeVisible();
      
      console.log(`✓ ${browserInfo.name} test passed`);
      
      await context.close();
      await browser.close();
    }
  });
  
  test('compare browser behaviors', async () => {
    const { chromium, firefox } = require('@playwright/test');
    
    const chromiumBrowser = await chromium.launch();
    const firefoxBrowser = await firefox.launch();
    
    const chromiumPage = await chromiumBrowser.newPage();
    const firefoxPage = await firefoxBrowser.newPage();
    
    await chromiumPage.goto('https://example.com');
    await firefoxPage.goto('https://example.com');
    
    // 比较两个浏览器上的元素位置
    const chromiumBox = await chromiumPage.locator('h1').boundingBox();
    const firefoxBox = await firefoxPage.locator('h1').boundingBox();
    
    // 验证位置一致性（允许1像素的差异）
    expect(Math.abs(chromiumBox.x - firefoxBox.x)).toBeLessThanOrEqual(1);
    expect(Math.abs(chromiumBox.y - firefoxBox.y)).toBeLessThanOrEqual(1);
    
    await chromiumBrowser.close();
    await firefoxBrowser.close();
  });
});
