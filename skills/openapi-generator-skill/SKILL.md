# OpenAPI Generator Skill

OpenAPI/Swagger文档生成工具。Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.

## 功能特性

- 📝 从Python代码自动生成OpenAPI规范
- 🎨 支持JSON和YAML格式导出
- 🔧 客户端SDK代码生成（Python/JavaScript）
- ✅ OpenAPI规范验证
- 🏗️ 程序化构建API规范

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 从代码生成OpenAPI规范

```python
from main import generate_from_code, export_spec
import my_api_module

# 从模块生成规范
spec = generate_from_code(
    module=my_api_module,
    title="My API",
    version="1.0.0",
    base_url="https://api.example.com"
)

# 导出为JSON
export_spec(spec, "openapi.json", "json")

# 或导出为YAML
export_spec(spec, "openapi.yaml", "yaml")
```

### 2. 程序化构建API规范

```python
from main import OpenAPISpecBuilder, OpenAPIInfo, OpenAPIServer, APIOperation, APIParameter, APIResponse

builder = OpenAPISpecBuilder(openapi_version="3.0.3")

# 设置基本信息
builder.set_info(OpenAPIInfo(
    title="Pet Store API",
    version="1.0.0",
    description="A sample API for pet store management"
))

# 添加服务器
builder.add_server(OpenAPIServer(
    url="https://api.petstore.com/v1",
    description="Production server"
))

# 添加安全方案
builder.add_security_scheme(
    name="bearerAuth",
    type_="http",
    scheme="bearer",
    bearer_format="JWT"
)

# 添加Schema
builder.add_schema("Pet", {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "status": {"type": "string", "enum": ["available", "pending", "sold"]}
    },
    "required": ["name"]
})

# 添加API操作
builder.add_operation(APIOperation(
    method="GET",
    path="/pets",
    summary="List all pets",
    operation_id="listPets",
    tags=["pets"],
    parameters=[
        APIParameter(name="limit", in_="query", type_="integer", description="Maximum number of results")
    ],
    responses=[
        APIResponse(code="200", description="List of pets", schema={"type": "array", "items": {"$ref": "#/components/schemas/Pet"}}),
        APIResponse(code="default", description="Error response")
    ]
))

# 构建规范
spec = builder.build()
```

### 3. 验证OpenAPI规范

```python
from main import validate_spec

errors = validate_spec(spec)
if errors:
    print("Validation errors:", errors)
else:
    print("Specification is valid!")
```

### 4. 生成客户端代码

```python
from main import ClientGenerator

# 加载规范
with open("openapi.json") as f:
    spec = json.load(f)

# 生成Python客户端
generator = ClientGenerator(spec)
python_code = generator.generate("python", client_name="PetStoreClient")

# 保存客户端代码
with open("petstore_client.py", "w") as f:
    f.write(python_code)

# 生成JavaScript客户端
js_code = generator.generate("javascript", client_name="PetStoreClient")
```

### 5. 命令行使用

```bash
# 从代码生成规范
python main.py generate --input my_module.py --output openapi.json --format json --title "My API" --version 1.0.0

# 验证规范
python main.py validate --input openapi.json

# 转换格式
python main.py export --input openapi.json --output openapi.yaml --format yaml

# 生成客户端代码
python main.py client --input openapi.json --output client.py --language python
python main.py client --input openapi.json --output client.js --language javascript
```

## API参考

### OpenAPISpecBuilder

构建OpenAPI 3.0规范的核心类。

| 方法 | 描述 |
|------|------|
| `set_info(info)` | 设置API基本信息 |
| `add_server(server)` | 添加服务器URL |
| `add_tag(name, description)` | 添加API标签 |
| `add_schema(name, schema)` | 添加组件Schema |
| `add_security_scheme(...)` | 添加认证方案 |
| `add_operation(operation)` | 添加API操作 |
| `build()` | 生成完整规范 |

### ClientGenerator

生成多语言客户端SDK。

| 方法 | 描述 |
|------|------|
| `generate(language, client_name)` | 生成指定语言的客户端 |

## 示例

### 创建Pet Store API

```python
from main import *

builder = OpenAPISpecBuilder()
builder.set_info(OpenAPIInfo(
    title="Swagger Petstore",
    version="1.0.0",
    description="This is a sample Pet Store Server"
))
builder.add_server(OpenAPIServer(url="https://petstore.swagger.io/v2"))

# 添加Schema
builder.add_schema("Category", {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "name": {"type": "string"}
    }
})

builder.add_schema("Pet", {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "category": {"$ref": "#/components/schemas/Category"},
        "name": {"type": "string", "example": "doggie"},
        "status": {"type": "string", "description": "pet status", "enum": ["available", "pending", "sold"]}
    },
    "required": ["name"]
})

# 添加操作
builder.add_operation(APIOperation(
    method="POST",
    path="/pet",
    summary="Add a new pet",
    operation_id="addPet",
    tags=["pet"],
    request_body={
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Pet"}
            }
        }
    },
    responses=[
        APIResponse(code="200", description="Successful operation"),
        APIResponse(code="405", description="Invalid input")
    ]
))

builder.add_operation(APIOperation(
    method="GET",
    path="/pet/{petId}",
    summary="Find pet by ID",
    operation_id="getPetById",
    tags=["pet"],
    parameters=[
        APIParameter(name="petId", in_="path", required=True, type_="integer", description="Pet ID")
    ],
    responses=[
        APIResponse(code="200", description="Successful operation", schema={"$ref": "#/components/schemas/Pet"}),
        APIResponse(code="400", description="Invalid ID supplied"),
        APIResponse(code="404", description="Pet not found")
    ]
))

spec = builder.build()
export_spec(spec, "petstore_openapi.json", "json")
```

## 输出示例

生成的OpenAPI JSON规范示例：

```json
{
  "openapi": "3.0.3",
  "info": {
    "title": "Swagger Petstore",
    "version": "1.0.0",
    "description": "This is a sample Pet Store Server"
  },
  "servers": [
    {"url": "https://petstore.swagger.io/v2"}
  ],
  "paths": {
    "/pet": {
      "post": {
        "summary": "Add a new pet",
        "operationId": "addPet",
        "tags": ["pet"],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {"$ref": "#/components/schemas/Pet"}
            }
          }
        },
        "responses": {
          "200": {"description": "Successful operation"},
          "405": {"description": "Invalid input"}
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Pet": {
        "type": "object",
        "properties": {
          "id": {"type": "integer", "format": "int64"},
          "name": {"type": "string", "example": "doggie"}
        },
        "required": ["name"]
      }
    }
  }
}
```

## 配置选项

在 `skill.json` 中配置默认选项：

```json
{
  "config": {
    "default_version": "3.0.3",
    "output_format": "json",
    "include_examples": true
  }
}
```

## 注意事项

1. 确保Python代码包含类型注解以获得更好的生成效果
2. 使用docstrings为API操作添加描述
3. 定期验证生成的规范确保合规性
4. 客户端生成目前支持Python和JavaScript

## 许可证

MIT License
