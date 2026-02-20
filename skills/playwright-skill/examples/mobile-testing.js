/**
 * 移动端测试示例
 * 
 * 展示Playwright如何测试移动设备
 */

const { test, expect, devices } = require('@playwright/test');

// ============================================
// 预定义设备测试
// ============================================

// iPhone 14
test.use({ ...devices['iPhone 14'] });

test.describe('iPhone 14 Tests', () => {
  test('homepage on iPhone 14', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 验证视口大小
    const viewport = page.viewportSize();
    expect(viewport.width).toBe(390);
    expect(viewport.height).toBe(844);
    
    // 验证移动端布局
    await expect(page.locator('.mobile-menu-btn')).toBeVisible();
    await expect(page.locator('.desktop-nav')).not.toBeVisible();
  });
  
  test('touch interactions', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 模拟触摸滑动
    await page.touchscreen.tap(100, 200);
    
    // 模拟滑动手势
    await page.evaluate(() => {
      const touch = new Touch({
        identifier: Date.now(),
        target: document,
        clientX: 100,
        clientY: 200
      });
      
      const touchEvent = new TouchEvent('touchstart', {
        bubbles: true,
        touches: [touch]
      });
      
      document.dispatchEvent(touchEvent);
    });
  });
  
  test('orientation change', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 竖屏模式
    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page.locator('.portrait-only')).toBeVisible();
    
    // 横屏模式
    await page.setViewportSize({ width: 844, height: 390 });
    await expect(page.locator('.landscape-only')).toBeVisible();
  });
});

// ============================================
// 多个设备对比测试
// ============================================

const testDevices = [
  { name: 'iPhone 14', device: devices['iPhone 14'] },
  { name: 'iPhone 14 Pro Max', device: devices['iPhone 14 Pro Max'] },
  { name: 'Pixel 7', device: devices['Pixel 7'] },
  { name: 'iPad Pro 11', device: devices['iPad Pro 11'] }
];

for (const deviceInfo of testDevices) {
  test.describe(`${deviceInfo.name} Responsive Tests`, () => {
    test.use({ ...deviceInfo.device });
    
    test(`homepage on ${deviceInfo.name}`, async ({ page }) => {
      await page.goto('https://example.com');
      
      // 截图对比
      await expect(page).toHaveScreenshot(`homepage-${deviceInfo.name}.png`, {
        fullPage: true
      });
    });
    
    test(`navigation on ${deviceInfo.name}`, async ({ page }) => {
      await page.goto('https://example.com');
      
      // 测试移动端导航
      const menuButton = page.locator('[data-testid="mobile-menu-button"]');
      
      if (await menuButton.isVisible().catch(() => false)) {
        await menuButton.click();
        await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      }
    });
  });
}

// ============================================
// 手势和触摸测试
// ============================================

test.describe('Touch Gestures', () => {
  test.use({ ...devices['Pixel 7'] });
  
  test('swipe carousel', async ({ page }) => {
    await page.goto('https://example.com');
    
    const carousel = page.locator('.carousel');
    const box = await carousel.boundingBox();
    
    // 从右向左滑动
    await page.mouse.move(box.x + box.width * 0.8, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * 0.2, box.y + box.height / 2);
    await page.mouse.up();
    
    // 验证滑动后的状态
    await expect(page.locator('.carousel-item.active')).toHaveAttribute('data-index', '1');
  });
  
  test('pinch to zoom', async ({ page }) => {
    await page.goto('https://example.com/gallery');
    
    const image = page.locator('.zoomable-image');
    
    // 模拟双指缩放
    await page.evaluate(() => {
      const ev = new Event('gesturestart');
      document.dispatchEvent(ev);
    });
    
    await expect(image).toHaveClass(/zoomed/);
  });
  
  test('pull to refresh', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 模拟下拉刷新
    await page.mouse.move(200, 100);
    await page.mouse.down();
    await page.mouse.move(200, 300);
    await page.mouse.up();
    
    await expect(page.locator('.refresh-indicator')).toBeVisible();
  });
});

// ============================================
// 地理位置和权限测试
// ============================================

test.describe('Mobile Permissions', () => {
  test.use({ ...devices['iPhone 14'] });
  
  test('geolocation permission', async ({ page, context }) => {
    // 授予地理位置权限
    await context.grantPermissions(['geolocation']);
    
    // 设置模拟位置
    await context.setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
    
    await page.goto('https://example.com/location');
    
    await expect(page.locator('.location-display')).toContainText('San Francisco');
  });
  
  test('camera permission', async ({ page, context }) => {
    // 授予摄像头权限
    await context.grantPermissions(['camera']);
    
    await page.goto('https://example.com/camera');
    
    await expect(page.locator('video')).toBeVisible();
  });
  
  test('notifications permission', async ({ page, context }) => {
    // 授予通知权限
    await context.grantPermissions(['notifications']);
    
    await page.goto('https://example.com');
    
    await page.click('[data-testid="enable-notifications"]');
    
    await expect(page.locator('.notification-enabled')).toBeVisible();
  });
});

// ============================================
// PWA测试
// ============================================

test.describe('PWA Tests', () => {
  test.use({ ...devices['Pixel 7'] });
  
  test('add to home screen prompt', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 验证 manifest 存在
    const manifest = await page.locator('link[rel="manifest"]').getAttribute('href');
    expect(manifest).toBeDefined();
    
    // 验证 service worker 注册
    const swRegistered = await page.evaluate(() => {
      return navigator.serviceWorker.ready.then(() => true);
    });
    expect(swRegistered).toBe(true);
  });
  
  test('offline functionality', async ({ page, context }) => {
    await page.goto('https://example.com');
    
    // 等待 service worker 激活
    await page.waitForTimeout(2000);
    
    // 离线模式
    await context.setOffline(true);
    
    // 重新加载页面
    await page.reload();
    
    // 验证离线页面显示
    await expect(page.locator('.offline-indicator')).toBeVisible();
    
    // 恢复网络
    await context.setOffline(false);
  });
  
  test('standalone mode detection', async ({ page }) => {
    // 模拟 standalone 模式
    await page.addInitScript(() => {
      Object.defineProperty(window.navigator, 'standalone', {
        get: () => true
      });
    });
    
    await page.goto('https://example.com');
    
    await expect(page.locator('body')).toHaveClass(/standalone/);
  });
});

// ============================================
// 性能测试
// ============================================

test.describe('Mobile Performance', () => {
  test.use({ ...devices['iPhone 14'] });
  
  test('page load performance', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 获取性能指标
    const performanceMetrics = await page.evaluate(() => {
      return JSON.stringify(performance.getEntriesByType('navigation'));
    });
    
    const navigation = JSON.parse(performanceMetrics)[0];
    
    // 验证加载时间
    expect(navigation.loadEventEnd - navigation.startTime).toBeLessThan(3000);
    expect(navigation.domContentLoadedEventEnd - navigation.startTime).toBeLessThan(1500);
  });
  
  test('memory usage', async ({ page }) => {
    await page.goto('https://example.com');
    
    // 模拟用户交互
    await page.click('[data-testid="load-more"]');
    await page.click('[data-testid="load-more"]');
    await page.click('[data-testid="load-more"]');
    
    // 检查内存使用
    const memory = await page.evaluate(() => {
      return (performance as any).memory;
    });
    
    if (memory) {
      console.log(`Used JS Heap: ${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`);
    }
  });
});
