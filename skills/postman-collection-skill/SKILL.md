# Postman Collection Skill

Postman集合管理工具。Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.

## 功能特性

- 📦 创建和管理Postman集合
- 🔄 OpenAPI/Swagger转Postman集合
- 🌍 环境变量管理
- 🧪 自动生成测试脚本
- 📤 导入/导出集合文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 创建Postman集合

```python
from main import PostmanCollectionBuilder, PostmanHeader, export_collection

# 创建集合构建器
builder = PostmanCollectionBuilder(
    name="Pet Store API",
    description="API for managing pets"
)

# 添加集合变量
builder.add_variable("baseUrl", "https://api.petstore.com")
builder.add_variable("apiKey", "your-api-key", "string", "API Key for authentication")

# 设置认证
builder.set_auth("bearer", token="{{apiKey}}")

# 添加请求
builder.add_request(
    name="Get All Pets",
    method="GET",
    url="{{baseUrl}}/pets",
    headers=[
        PostmanHeader(key="Accept", value="application/json")
    ],
    description="Retrieve a list of all pets"
)

# 添加带测试的请求
builder.add_request(
    name="Create Pet",
    method="POST",
    url="{{baseUrl}}/pets",
    headers=[
        PostmanHeader(key="Content-Type", value="application/json")
    ],
    body={
        "mode": "raw",
        "raw": '{"name": "Fluffy", "type": "cat"}',
        "options": {"raw": {"language": "json"}}
    },
    tests="""
pm.test('Status code is 201', function () {
    pm.response.to.have.status(201);
});
pm.test('Response has pet ID', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
""",
    folder="Pets"
)

# 添加文件夹
builder.add_folder(
    name="Users",
    description="User management endpoints"
)

# 构建集合并导出
collection = builder.build()
export_collection(collection, "petstore.postman_collection.json")
```

### 2. 创建环境配置

```python
from main import PostmanEnvironmentBuilder, export_collection

# 创建环境
env_builder = PostmanEnvironmentBuilder(
    name="Production",
    environment_type="environment"
)

# 添加环境变量
env_builder.add_variable("baseUrl", "https://api.petstore.com", "string")
env_builder.add_variable("apiKey", "prod-key-123", "string")
env_builder.add_variable("timeout", 5000, "number")

# 构建并导出
environment = env_builder.build()
export_collection(environment, "production.postman_environment.json")
```

### 3. OpenAPI转Postman集合

```python
from main import OpenAPIToPostmanConverter, export_collection
import json

# 加载OpenAPI规范
with open("openapi.json") as f:
    openapi_spec = json.load(f)

# 转换
converter = OpenAPIToPostmanConverter(openapi_spec)
collection = converter.convert(base_url="https://api.example.com")

# 导出
export_collection(collection, "api.postman_collection.json")
```

### 4. 生成测试脚本

```python
from main import generate_test_script

# 生成测试脚本
tests = generate_test_script(
    assertions=["status_ok", "is_json", "response_time"],
    variables=["userId", "token"]
)

print(tests)
```

输出：
```javascript
// Auto-generated test script

pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

pm.test('Response is JSON', function () {
    pm.response.to.be.json;
});

pm.test('Response time is acceptable', function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Set environment variable: userId
pm.environment.set('userId', pm.response.json().userId);

// Set environment variable: token
pm.environment.set('token', pm.response.json().token);
```

### 5. 命令行使用

```bash
# 创建新集合
python main.py create --name "My API" --url "https://api.example.com" --output myapi.postman_collection.json

# 从OpenAPI转换
python main.py convert --input openapi.json --output api.postman_collection.json

# 导出环境配置
python main.py export --name "Development" --url "http://localhost:3000" --output dev.postman_environment.json

# 生成测试脚本
python main.py test --output tests.js
```

## API参考

### PostmanCollectionBuilder

| 方法 | 描述 |
|------|------|
| `add_folder(name, description, items)` | 添加文件夹 |
| `add_request(name, method, url, ...)` | 添加请求 |
| `add_variable(key, value, type, ...)` | 添加集合变量 |
| `set_auth(type, **kwargs)` | 设置认证方式 |
| `add_prerequest_script(script)` | 添加前置脚本 |
| `build()` | 构建集合并返回字典 |

### PostmanEnvironmentBuilder

| 方法 | 描述 |
|------|------|
| `add_variable(key, value, type, enabled)` | 添加环境变量 |
| `build()` | 构建环境配置 |

### OpenAPIToPostmanConverter

| 方法 | 描述 |
|------|------|
| `convert(base_url)` | 将OpenAPI转换为Postman集合 |

## 示例：完整API集合

```python
from main import *

# 创建集合
builder = PostmanCollectionBuilder(
    name="E-commerce API",
    description="Complete e-commerce API collection"
)

# 添加全局变量
builder.add_variable("baseUrl", "https://api.shop.com/v1")
builder.add_variable("authToken", "", "string")

# 设置Bearer认证
builder.set_auth("bearer", token="{{authToken}}")

# 添加前置脚本获取token
builder.add_prerequest_script("""
// Get auth token if not present
if (!pm.environment.get('authToken')) {
    pm.sendRequest({
        url: pm.environment.get('baseUrl') + '/auth/login',
        method: 'POST',
        body: {
            mode: 'raw',
            raw: JSON.stringify({email: 'test@example.com', password: 'password'})
        }
    }, function (err, response) {
        var jsonData = response.json();
        pm.environment.set('authToken', jsonData.token);
    });
}
""")

# Products文件夹
builder.add_request(
    name="List Products",
    method="GET",
    url="{{baseUrl}}/products?page=1&limit=20",
    description="Get paginated product list",
    folder="Products"
)

builder.add_request(
    name="Get Product",
    method="GET",
    url="{{baseUrl}}/products/:id",
    description="Get single product details",
    folder="Products"
)

# Orders文件夹  
builder.add_request(
    name="Create Order",
    method="POST",
    url="{{baseUrl}}/orders",
    headers=[PostmanHeader(key="Content-Type", value="application/json")],
    body={
        "mode": "raw",
        "raw": json.dumps({
            "items": [{"productId": "123", "quantity": 2}],
            "shippingAddress": {"street": "123 Main St", "city": "NYC"}
        }),
        "options": {"raw": {"language": "json"}}
    },
    tests="""
pm.test('Order created successfully', function () {
    pm.response.to.have.status(201);
    pm.expect(pm.response.json()).to.have.property('orderId');
    pm.environment.set('lastOrderId', pm.response.json().orderId);
});
""",
    folder="Orders"
)

# 导出
collection = builder.build()
export_collection(collection, "ecommerce.postman_collection.json")
```

## 集合文件结构

生成的Postman集合文件结构：

```json
{
  "info": {
    "_postman_id": "uuid",
    "name": "API Name",
    "description": "API Description",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Folder Name",
      "description": "Folder description",
      "item": [
        {
          "name": "Request Name",
          "request": {
            "method": "GET",
            "url": "{{baseUrl}}/endpoint",
            "header": [],
            "body": {}
          },
          "response": [],
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": ["pm.test('Test name', function () {...})"]
              }
            }
          ]
        }
      ]
    }
  ],
  "variable": [
    {"key": "baseUrl", "value": "https://api.example.com", "type": "string"}
  ],
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{authToken}}"}]
  }
}
```

## 配置选项

在 `skill.json` 中配置默认选项：

```json
{
  "config": {
    "default_schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "include_responses": true,
    "auto_generate_tests": false
  }
}
```

## 注意事项

1. Postman集合使用JSON格式，版本为v2.1.0
2. 变量使用双花括号语法：`{{variableName}}`
3. 测试脚本使用Postman的测试语法
4. 认证信息会被转换为Postman的auth格式
5. 文件夹用于组织相关请求

## 许可证

MIT License
