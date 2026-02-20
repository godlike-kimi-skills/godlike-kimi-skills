/**
 * 登录流程测试示例
 * 
 * 展示Cypress E2E测试的完整实战案例
 */

// ============================================
// Page Object模式
// ============================================

class LoginPage {
  constructor() {
    this.url = '/login';
    this.selectors = {
      username: '[data-testid="username-input"]',
      password: '[data-testid="password-input"]',
      loginButton: '[data-testid="login-button"]',
      errorMessage: '[data-testid="error-message"]',
      rememberMe: '[data-testid="remember-me"]'
    };
  }

  visit() {
    cy.visit(this.url);
    return this;
  }

  fillUsername(value) {
    cy.get(this.selectors.username).clear().type(value);
    return this;
  }

  fillPassword(value) {
    cy.get(this.selectors.password).clear().type(value);
    return this;
  }

  clickLogin() {
    cy.get(this.selectors.loginButton).click();
    return this;
  }

  checkRememberMe() {
    cy.get(this.selectors.rememberMe).check();
    return this;
  }

  getErrorMessage() {
    return cy.get(this.selectors.errorMessage);
  }

  login(username, password) {
    this.fillUsername(username)
        .fillPassword(password)
        .clickLogin();
    return this;
  }
}

class DashboardPage {
  constructor() {
    this.url = '/dashboard';
    this.selectors = {
      welcomeMessage: '[data-testid="welcome-message"]',
      userMenu: '[data-testid="user-menu"]',
      logoutButton: '[data-testid="logout-button"]'
    };
  }

  getWelcomeMessage() {
    return cy.get(this.selectors.welcomeMessage);
  }

  logout() {
    cy.get(this.selectors.userMenu).click();
    cy.get(this.selectors.logoutButton).click();
    return this;
  }
}

// ============================================
// 测试套件
// ============================================

describe('Authentication Flow', () => {
  const loginPage = new LoginPage();
  const dashboardPage = new DashboardPage();

  beforeEach(() => {
    // 清除认证状态
    cy.clearCookies();
    cy.clearLocalStorage();
    
    // 拦截API请求
    cy.intercept('POST', '/api/auth/login').as('loginRequest');
    cy.intercept('GET', '/api/user/profile').as('userProfile');
  });

  describe('Successful Login', () => {
    beforeEach(() => {
      // 设置成功的登录响应
      cy.intercept('POST', '/api/auth/login', {
        statusCode: 200,
        body: {
          token: 'fake-jwt-token',
          user: {
            id: 1,
            username: 'testuser',
            email: 'test@example.com'
          }
        }
      }).as('successfulLogin');
    });

    it('should login with valid credentials', () => {
      // Arrange
      loginPage.visit();

      // Act
      loginPage.login('testuser', 'password123');

      // Assert
      cy.wait('@successfulLogin').its('response.statusCode').should('eq', 200);
      cy.url().should('include', '/dashboard');
      dashboardPage.getWelcomeMessage().should('contain.text', 'Welcome, testuser');
    });

    it('should persist login with "Remember Me"', () => {
      // Arrange & Act
      loginPage.visit()
        .fillUsername('testuser')
        .fillPassword('password123')
        .checkRememberMe()
        .clickLogin();

      // Assert
      cy.wait('@successfulLogin');
      cy.getCookie('remember_token').should('exist');
    });
  });

  describe('Failed Login', () => {
    it('should show error with invalid credentials', () => {
      // Arrange
      cy.intercept('POST', '/api/auth/login', {
        statusCode: 401,
        body: { message: 'Invalid username or password' }
      }).as('failedLogin');

      loginPage.visit();

      // Act
      loginPage.login('wronguser', 'wrongpassword');

      // Assert
      cy.wait('@failedLogin');
      loginPage.getErrorMessage()
        .should('be.visible')
        .and('contain.text', 'Invalid username or password');
      cy.url().should('include', '/login');
    });

    it('should validate required fields', () => {
      // Arrange
      loginPage.visit();

      // Act
      loginPage.clickLogin();

      // Assert
      cy.get('[data-testid="username-input"]:invalid').should('exist');
      cy.get('[data-testid="password-input"]:invalid').should('exist');
    });
  });

  describe('Session Management', () => {
    it('should logout successfully', () => {
      // Arrange - login first
      cy.login('testuser', 'password123'); // 使用自定义命令
      cy.visit('/dashboard');

      // Act
      dashboardPage.logout();

      // Assert
      cy.url().should('include', '/login');
      cy.getCookie('auth_token').should('not.exist');
    });

    it('should redirect to login when accessing protected route without auth', () => {
      // Act
      cy.visit('/dashboard');

      // Assert
      cy.url().should('include', '/login');
      cy.get('[data-testid="redirect-message"]')
        .should('contain.text', 'Please log in to continue');
    });
  });
});

// ============================================
// 数据驱动测试
// ============================================

describe('Login with Fixture Data', () => {
  beforeEach(() => {
    cy.fixture('users').as('users');
  });

  it('should login with different user types', function() {
    const loginPage = new LoginPage();

    // 测试多个用户
    cy.wrap(this.users.valid).each((user) => {
      loginPage.visit().login(user.username, user.password);
      cy.url().should('include', '/dashboard');
      
      // 登出为下一个测试做准备
      cy.logout();
    });
  });
});

// ============================================
// 视觉回归测试
// ============================================

describe('Login Page Visual Tests', () => {
  it('should match login page screenshot', () => {
    cy.visit('/login');
    cy.get('[data-testid="login-form"]').matchImageSnapshot('login-form');
  });

  it('should match error state screenshot', () => {
    cy.visit('/login');
    cy.get('[data-testid="login-button"]').click();
    cy.get('[data-testid="login-form"]').matchImageSnapshot('login-form-error');
  });
});

// ============================================
// 性能测试
// ============================================

describe('Login Performance', () => {
  it('should load login page within 3 seconds', () => {
    cy.visit('/login', {
      onBeforeLoad: (win) => {
        win.performance.mark('start');
      },
      onLoad: (win) => {
        win.performance.mark('end');
        win.performance.measure('pageLoad', 'start', 'end');
      }
    });

    cy.window().then((win) => {
      const measure = win.performance.getEntriesByName('pageLoad')[0];
      expect(measure.duration).to.be.lessThan(3000);
    });
  });
});
