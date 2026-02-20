/**
 * k6高级使用示例
 * 
 * 展示k6的高级功能：场景配置、自定义指标、阈值等
 */

import http from 'k6/http';
import { check, sleep, group, fail } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';

// ============================================
// 自定义指标
// ============================================

// 错误率指标
const errorRate = new Rate('errors');

// API响应时间趋势
const apiTrend = new Trend('api_response_time');

// 订单计数器
const orderCounter = new Counter('orders_created');

// 活跃用户数
const activeUsers = new Gauge('active_users');

// 自定义检查
const checkFailureRate = new Rate('check_failures');

// ============================================
// 测试配置
// ============================================

export const options = {
  // 场景配置
  scenarios: {
    // 冒烟测试
    smoke: {
      executor: 'constant-vus',
      vus: 10,
      duration: '1m',
      tags: { test_type: 'smoke' },
      exec: 'smokeTest'
    },
    
    // 负载测试
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // 逐步增加到50用户
        { duration: '5m', target: 50 },   // 保持50用户
        { duration: '2m', target: 100 },  // 增加到100用户
        { duration: '5m', target: 100 },  // 保持100用户
        { duration: '2m', target: 0 },    // 逐步减少
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'load' },
      exec: 'loadTest'
    },
    
    // 压力测试
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 100 },
        { duration: '2m', target: 200 },
        { duration: '5m', target: 200 },
        { duration: '2m', target: 400 },
        { duration: '5m', target: 400 },
        { duration: '2m', target: 0 },
      ],
      tags: { test_type: 'stress' },
      exec: 'stressTest'
    },
    
    // 峰值测试
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 1000 },
        { duration: '1m', target: 1000 },
        { duration: '10s', target: 0 },
      ],
      tags: { test_type: 'spike' },
      exec: 'spikeTest'
    },
    
    // 浸泡测试
    soak: {
      executor: 'constant-vus',
      vus: 100,
      duration: '4h',
      tags: { test_type: 'soak' },
      exec: 'soakTest'
    },
    
    // 基于到达率的测试
    arrival_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { target: 50, duration: '2m' },
        { target: 100, duration: '5m' },
        { target: 50, duration: '2m' },
      ],
      tags: { test_type: 'arrival_rate' },
      exec: 'arrivalRateTest'
    }
  },
  
  // 阈值配置
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.05'],
    'api_response_time': ['p(95)<400'],
    checks: ['rate>0.95'],
  },
  
  // 系统标签
  systemTags: ['status', 'method', 'url', 'scenario', 'check'],
  
  // 摘要趋势统计
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// ============================================
// 测试数据
// ============================================

// 从JSON文件加载测试数据
const users = new SharedArray('users', function () {
  return JSON.parse(open('./data/users.json'));
});

const products = new SharedArray('products', function () {
  return JSON.parse(open('./data/products.json'));
});

// ============================================
// 设置和清理
// ============================================

export function setup() {
  console.log('Test setup starting...');
  
  // 登录获取token
  const loginRes = http.post('https://api.example.com/auth/login', {
    username: 'admin',
    password: 'password'
  });
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });
  
  const authToken = loginRes.json('token');
  
  console.log(`Setup complete. Token obtained: ${authToken ? 'Yes' : 'No'}`);
  
  return { authToken };
}

export function teardown(data) {
  console.log('Test teardown starting...');
  
  // 清理操作
  http.post('https://api.example.com/auth/logout', null, {
    headers: { 'Authorization': `Bearer ${data.authToken}` }
  });
  
  console.log('Teardown complete.');
}

// ============================================
// 测试场景函数
// ============================================

export function smokeTest() {
  group('Smoke Test', () => {
    const res = http.get('https://api.example.com/health');
    
    const checkRes = check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 200ms': (r) => r.timings.duration < 200,
    });
    
    checkFailureRate.add(!checkRes);
    errorRate.add(res.status !== 200);
    
    sleep(1);
  });
}

export function loadTest() {
  const user = users[exec.scenario.iterationInTest % users.length];
  
  activeUsers.add(exec.instance.vusActive);
  
  group('Authentication', () => {
    const loginRes = http.post('https://api.example.com/auth/login', {
      username: user.username,
      password: user.password
    });
    
    check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'has access token': (r) => r.json('token') !== undefined,
    });
    
    if (loginRes.status !== 200) {
      errorRate.add(1);
      return;
    }
    
    const token = loginRes.json('token');
    
    group('API Calls', () => {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // 获取用户资料
      const profileRes = http.get('https://api.example.com/profile', { headers });
      apiTrend.add(profileRes.timings.duration);
      
      check(profileRes, {
        'profile status is 200': (r) => r.status === 200,
      });
      
      // 获取产品列表
      const productsRes = http.get('https://api.example.com/products', { headers });
      apiTrend.add(productsRes.timings.duration);
      
      // 查看产品详情
      const product = products[Math.floor(Math.random() * products.length)];
      const productRes = http.get(`https://api.example.com/products/${product.id}`, { headers });
      apiTrend.add(productRes.timings.duration);
      
      // 添加到购物车
      const cartRes = http.post('https://api.example.com/cart', {
        product_id: product.id,
        quantity: Math.floor(Math.random() * 5) + 1
      }, { headers });
      
      check(cartRes, {
        'cart add successful': (r) => r.status === 200 || r.status === 201,
      });
    });
    
    // 登出
    http.post('https://api.example.com/auth/logout', null, { headers });
  });
  
  sleep(Math.random() * 3 + 1);
}

export function stressTest() {
  const payload = JSON.stringify({
    data: 'x'.repeat(1000), // 大payload
  });
  
  const res = http.post('https://api.example.com/process', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(res, {
    'process successful': (r) => r.status === 200,
    'response time < 2000ms': (r) => r.timings.duration < 2000,
  });
  
  errorRate.add(res.status !== 200);
  
  sleep(0.5);
}

export function spikeTest() {
  // 快速连续的请求
  const requests = [
    { method: 'GET', url: 'https://api.example.com/data' },
    { method: 'GET', url: 'https://api.example.com/status' },
    { method: 'POST', url: 'https://api.example.com/action', payload: {} },
  ];
  
  const responses = http.batch(requests);
  
  responses.forEach((res, i) => {
    check(res, {
      [`request ${i} successful`]: (r) => r.status === 200,
    });
    
    errorRate.add(res.status !== 200);
  });
  
  sleep(0.1);
}

export function soakTest() {
  // 长时间运行的简单测试
  const res = http.get('https://api.example.com/ping');
  
  check(res, {
    'ping successful': (r) => r.status === 200,
  });
  
  // 记录内存使用
  if (exec.scenario.iterationInTest % 100 === 0) {
    console.log(`Soak test iteration: ${exec.scenario.iterationInTest}`);
  }
  
  sleep(5);
}

export function arrivalRateTest() {
  // 模拟固定到达率的请求
  const res = http.get('https://api.example.com/api/data');
  
  check(res, {
    'data retrieved': (r) => r.status === 200,
    'response has data': (r) => r.json('data') !== undefined,
  });
}

// ============================================
// 默认测试函数
// ============================================

export default function() {
  // 默认执行负载测试
  loadTest();
}

// ============================================
// 辅助函数
// ============================================

function randomString(length) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ============================================
// 生命周期钩子
// ============================================

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'results/summary.json': JSON.stringify(data, null, 2),
    'results/summary.html': generateHTMLReport(data),
  };
}

function textSummary(data, options) {
  // 简单的文本摘要
  const indent = options.indent || '';
  return Object.entries(data.metrics)
    .map(([key, metric]) => {
      if (metric.values) {
        return `${indent}${key}: ${JSON.stringify(metric.values)}`;
      }
      return `${indent}${key}: ${metric}`;
    })
    .join('\n');
}

function generateHTMLReport(data) {
  // 生成HTML报告
  return `<!DOCTYPE html>
<html>
<head><title>k6 Test Report</title></head>
<body>
  <h1>Load Test Results</h1>
  <pre>${JSON.stringify(data, null, 2)}</pre>
</body>
</html>`;
}

/**
 * 运行k6:
 * 
 * 1. 运行所有场景:
 *    k6 run script.js
 * 
 * 2. 只运行特定场景:
 *    k6 run --env K6_SCENARIO=smoke script.js
 * 
 * 3. 指定输出格式:
 *    k6 run --out json=results.json script.js
 *    k6 run --out influxdb=http://localhost:8086/k6 script.js
 * 
 * 4. 使用Docker运行:
 *    docker run -v $(pwd):/scripts grafana/k6 run /scripts/script.js
 * 
 * 5. 云端运行:
 *    k6 cloud script.js
 * 
 * 6. 分布式运行:
 *    k6 run --execution-segment=0:1/4 --execution-segment-sequence=4 script.js
 */
