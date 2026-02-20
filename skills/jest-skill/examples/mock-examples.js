/**
 * Mock和Spy使用示例
 * 
 * 展示Jest中各种Mock和Spy的高级用法
 */

// ============================================
// 1. 函数Mock
// ============================================

// 基础mock函数
const mockFn = jest.fn();
mockFn.mockReturnValue('default');
mockFn.mockReturnValueOnce('first call');
mockFn.mockReturnValueOnce('second call');

// Mock实现
const mockWithImpl = jest.fn().mockImplementation((a, b) => a + b);

// 异步mock
const asyncMock = jest.fn().mockResolvedValue({ data: [] });
const asyncMockReject = jest.fn().mockRejectedValue(new Error('API Error'));

// ============================================
// 2. 模块Mock
// ============================================

// 自动mock整个模块
jest.mock('../api/client');

// 手动mock模块
jest.mock('../api/client', () => ({
  get: jest.fn().mockResolvedValue({ data: [] }),
  post: jest.fn().mockResolvedValue({ data: {} }),
  put: jest.fn().mockResolvedValue({ data: {} }),
  delete: jest.fn().mockResolvedValue({ status: 204 })
}));

// 部分mock
jest.mock('../utils', () => ({
  ...jest.requireActual('../utils'),
  expensiveComputation: jest.fn().mockReturnValue(42)
}));

// ============================================
// 3. Spy使用
// ============================================

describe('Spy Examples', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('spy on object method', () => {
    const calculator = {
      add: (a, b) => a + b,
      multiply: (a, b) => a * b
    };

    const addSpy = jest.spyOn(calculator, 'add');
    
    calculator.add(2, 3);
    
    expect(addSpy).toHaveBeenCalledWith(2, 3);
    expect(addSpy).toHaveReturnedWith(5);
  });

  test('spy with mock implementation', () => {
    const userService = {
      getUser: (id) => ({ id, name: 'Real User' })
    };

    jest.spyOn(userService, 'getUser')
      .mockImplementation((id) => ({ id, name: 'Mocked User' }));

    const user = userService.getUser(1);
    
    expect(user.name).toBe('Mocked User');
  });

  test('spy on console methods', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    console.error('Test error');
    
    expect(consoleSpy).toHaveBeenCalledWith('Test error');
    
    consoleSpy.mockRestore();
  });
});

// ============================================
// 4. 定时器Mock
// ============================================

describe('Timer Mocks', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('debounce function', () => {
    const debounce = (fn, delay) => {
      let timeoutId;
      return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
      };
    };

    const callback = jest.fn();
    const debouncedFn = debounce(callback, 1000);

    debouncedFn('first');
    debouncedFn('second');
    debouncedFn('third');

    jest.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith('third');
  });

  test('interval cleanup', () => {
    const pollData = (callback) => {
      const intervalId = setInterval(callback, 5000);
      return () => clearInterval(intervalId);
    };

    const callback = jest.fn();
    const cleanup = pollData(callback);

    jest.advanceTimersByTime(15000);
    expect(callback).toHaveBeenCalledTimes(3);

    cleanup();
    jest.advanceTimersByTime(5000);
    expect(callback).toHaveBeenCalledTimes(3);
  });
});

// ============================================
// 5. 全局对象Mock
// ============================================

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock fetch
global.fetch = jest.fn().mockResolvedValue({
  json: jest.fn().mockResolvedValue({ data: 'test' }),
  ok: true,
  status: 200
});

// Mock Math.random
const mockMath = Object.create(global.Math);
mockMath.random = jest.fn().mockReturnValue(0.5);
global.Math = mockMath;

// ============================================
// 6. 自定义匹配器
// ============================================

expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false
      };
    }
  }
});

test('custom matcher', () => {
  expect(5).toBeWithinRange(1, 10);
});
