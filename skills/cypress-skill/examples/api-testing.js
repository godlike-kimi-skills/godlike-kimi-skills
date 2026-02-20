/**
 * API测试示例
 * 
 * 展示Cypress如何拦截和测试API请求
 */

// ============================================
// API拦截和Mock
// ============================================

describe('API Testing with cy.intercept', () => {
  beforeEach(() => {
    // 基础拦截
    cy.intercept('GET', '/api/users').as('getUsers');
    
    // 带响应的拦截
    cy.intercept('GET', '/api/users/1', {
      statusCode: 200,
      body: {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com'
      }
    }).as('getUser');
    
    // 动态响应
    cy.intercept('POST', '/api/users', (req) => {
      const { body } = req;
      req.reply({
        statusCode: 201,
        body: {
          id: Math.floor(Math.random() * 1000),
          ...body,
          createdAt: new Date().toISOString()
        }
      });
    }).as('createUser');
    
    // 网络错误模拟
    cy.intercept('GET', '/api/error', {
      forceNetworkError: true
    }).as('networkError');
    
    // 延迟响应
    cy.intercept('GET', '/api/slow', {
      delay: 2000,
      statusCode: 200,
      body: { message: 'Slow response' }
    }).as('slowRequest');
  });

  it('should fetch users list', () => {
    cy.visit('/users');
    cy.wait('@getUsers').its('response.statusCode').should('eq', 200);
  });

  it('should create a new user', () => {
    cy.visit('/users/new');
    
    cy.get('[data-testid="name-input"]').type('Jane Doe');
    cy.get('[data-testid="email-input"]').type('jane@example.com');
    cy.get('[data-testid="submit-button"]').click();
    
    cy.wait('@createUser').then((interception) => {
      expect(interception.response.statusCode).to.eq(201);
      expect(interception.response.body).to.have.property('id');
      expect(interception.response.body.name).to.eq('Jane Doe');
    });
  });

  it('should handle network errors gracefully', () => {
    cy.visit('/error-page');
    cy.wait('@networkError');
    cy.get('[data-testid="error-message"]').should('contain', 'Network error');
  });

  it('should show loading state for slow requests', () => {
    cy.visit('/slow-page');
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
    cy.wait('@slowRequest');
    cy.get('[data-testid="loading-spinner"]').should('not.exist');
  });
});

// ============================================
// GraphQL测试
// ============================================

describe('GraphQL API Testing', () => {
  beforeEach(() => {
    // GraphQL查询拦截
    cy.intercept('POST', '/graphql', (req) => {
      if (req.body.operationName === 'GetUsers') {
        req.reply({
          data: {
            users: [
              { id: '1', name: 'User 1', email: 'user1@example.com' },
              { id: '2', name: 'User 2', email: 'user2@example.com' }
            ]
          }
        });
      }
      
      if (req.body.operationName === 'CreateUser') {
        const { input } = req.body.variables;
        req.reply({
          data: {
            createUser: {
              id: '3',
              ...input
            }
          }
        });
      }
    }).as('graphql');
  });

  it('should fetch users via GraphQL', () => {
    cy.visit('/users');
    cy.wait('@graphql');
    cy.get('[data-testid="user-list"] > li').should('have.length', 2);
  });
});

// ============================================
// 文件上传测试
// ============================================

describe('File Upload Testing', () => {
  beforeEach(() => {
    cy.intercept('POST', '/api/upload').as('fileUpload');
  });

  it('should upload a file', () => {
    cy.fixture('example.json').then((fileContent) => {
      cy.get('[data-testid="file-input"]').attachFile({
        fileContent: JSON.stringify(fileContent),
        fileName: 'example.json',
        mimeType: 'application/json'
      });
    });

    cy.get('[data-testid="upload-button"]').click();

    cy.wait('@fileUpload').its('request.body').should('include', 'example.json');
  });
});

// ============================================
// 认证和授权测试
// ============================================

describe('Authentication & Authorization', () => {
  it('should attach auth token to requests', () => {
    // 设置token
    window.localStorage.setItem('auth_token', 'fake-token');

    cy.intercept('GET', '/api/protected', (req) => {
      expect(req.headers).to.have.property('authorization', 'Bearer fake-token');
      req.reply({ statusCode: 200, body: { data: 'protected' } });
    }).as('protectedRequest');

    cy.visit('/protected');
    cy.wait('@protectedRequest');
  });

  it('should handle 401 unauthorized', () => {
    cy.intercept('GET', '/api/protected', {
      statusCode: 401,
      body: { message: 'Unauthorized' }
    }).as('unauthorized');

    cy.visit('/protected');
    cy.wait('@unauthorized');
    cy.url().should('include', '/login');
  });
});

// ============================================
// 分页和过滤测试
// ============================================

describe('Pagination and Filtering', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/users?page=*', (req) => {
      const page = req.query.page || 1;
      const limit = req.query.limit || 10;
      
      const users = Array.from({ length: limit }, (_, i) => ({
        id: (page - 1) * limit + i + 1,
        name: `User ${(page - 1) * limit + i + 1}`
      }));
      
      req.reply({
        data: users,
        meta: { total: 100, page: parseInt(page), limit: parseInt(limit) }
      });
    }).as('getUsersWithPagination');
  });

  it('should navigate through pages', () => {
    cy.visit('/users');
    cy.wait('@getUsersWithPagination');
    
    // 点击下一页
    cy.get('[data-testid="next-page"]').click();
    cy.wait('@getUsersWithPagination').its('request.query').should('include', { page: '2' });
  });
});
