# API Blueprint Skill

API Blueprint文档工具。Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.

## 功能特性

- 📝 API Blueprint文档编写
- 🔄 OpenAPI转API Blueprint
- 🎭 Mock服务器生成
- ✅ 文档验证
- 🏗️ 结构化文档构建

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 创建API Blueprint文档

```python
from main import APIBlueprintBuilder, ResourceGroup, HttpMethod, Parameter, ParameterType

# 创建构建器
builder = APIBlueprintBuilder(
    name="My API",
    description="A sample API for demonstration",
    host="https://api.example.com"
)

# 添加元数据
builder.add_metadata("VERSION", "1.0.0")
builder.add_metadata("AUTHOR", "API Team")

# 创建资源组
group = builder.add_resource_group("Users", "User management operations")

# 添加资源
resource = builder.add_resource(
    name="User",
    uri_template="/users/{id}",
    description="A single user resource",
    group=group
)

# 添加GET操作
action = builder.add_action(
    resource=resource,
    name="Get User",
    method=HttpMethod.GET,
    description="Retrieve a single user by ID"
)

# 添加请求参数
builder.add_request(
    action=action,
    parameters=[
        Parameter(name="id", type_=ParameterType.STRING, required=True, description="User ID")
    ]
)

# 添加响应
builder.add_response(
    action=action,
    status_code=200,
    description="User found successfully",
    example='''{
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
}'''
)

# 添加404响应
builder.add_response(
    action=action,
    status_code=404,
    description="User not found"
)

# 构建文档
blueprint = builder.build()
print(blueprint)

# 保存到文件
with open("api.apib", "w") as f:
    f.write(blueprint)
```

### 2. 从OpenAPI转换

```python
from main import OpenAPIToBlueprintConverter, export_blueprint
import json

# 加载OpenAPI规范
with open("openapi.json") as f:
    spec = json.load(f)

# 转换
converter = OpenAPIToBlueprintConverter(spec)
blueprint = converter.convert()

# 导出
export_blueprint(blueprint, "api.apib")
```

### 3. 生成Mock服务器

```python
from main import MockServerGenerator

# 读取Blueprint
with open("api.apib") as f:
    blueprint = f.read()

# 生成Flask Mock服务器
generator = MockServerGenerator(blueprint)
flask_code = generator.generate_flask_app()

with open("mock_server.py", "w") as f:
    f.write(flask_code)

# 或生成Express Mock服务器
express_code = generator.generate_express_app()

with open("mock_server.js", "w") as f:
    f.write(express_code)
```

运行Mock服务器：

```bash
# Flask
python mock_server.py

# Express
node mock_server.js
```

### 4. 验证Blueprint文档

```python
from main import validate_blueprint

# 读取文档
with open("api.apib") as f:
    blueprint = f.read()

# 验证
errors = validate_blueprint(blueprint)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Blueprint is valid!")
```

### 5. 命令行使用

```bash
# 创建新的Blueprint
python main.py create --name "My API" --host "https://api.example.com" --output api.apib

# 从OpenAPI转换
python main.py convert --input openapi.json --output api.apib

# 生成Mock服务器
python main.py mock --input api.apib --output mock_server.py --framework flask

# 验证文档
python main.py validate --input api.apib
```

## API参考

### APIBlueprintBuilder

构建API Blueprint文档的核心类。

| 方法 | 描述 |
|------|------|
| `add_metadata(key, value)` | 添加元数据 |
| `add_resource_group(name, description)` | 添加资源组 |
| `add_resource(name, uri_template, ...)` | 添加资源 |
| `add_action(resource, name, method, ...)` | 添加操作 |
| `add_request(action, ...)` | 添加请求 |
| `add_response(action, ...)` | 添加响应 |
| `build()` | 构建并返回Blueprint字符串 |

### HttpMethod

HTTP方法枚举：
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `PATCH`
- `HEAD`
- `OPTIONS`

### ParameterType

参数类型枚举：
- `STRING`
- `NUMBER`
- `INTEGER`
- `BOOLEAN`
- `ARRAY`
- `OBJECT`

### MockServerGenerator

| 方法 | 描述 |
|------|------|
| `generate_flask_app()` | 生成Flask应用代码 |
| `generate_express_app()` | 生成Express应用代码 |

### OpenAPIToBlueprintConverter

| 方法 | 描述 |
|------|------|
| `convert()` | 将OpenAPI规范转换为API Blueprint |

## 示例：完整的API Blueprint

```python
from main import *

builder = APIBlueprintBuilder(
    name="Pet Store API",
    description="A simple API for managing pets",
    host="https://petstore.example.com"
)

# 元数据
builder.add_metadata("VERSION", "1.0.0")
builder.add_metadata("AUTHOR", "Pet Store Team")

# Pets资源组
pets_group = builder.add_resource_group("Pets", "Everything about pets")

# 列表/创建Pets
pets_resource = builder.add_resource(
    name="Pets",
    uri_template="/pets",
    description="Collection of all pets",
    group=pets_group
)

# GET /pets
list_action = builder.add_action(
    resource=pets_resource,
    name="List Pets",
    method=HttpMethod.GET,
    description="Get a list of all pets"
)

builder.add_request(
    action=list_action,
    parameters=[
        Parameter(name="limit", type_=ParameterType.INTEGER, required=False, description="Maximum results"),
        Parameter(name="status", type_=ParameterType.STRING, required=False, description="Filter by status")
    ]
)

builder.add_response(
    action=list_action,
    status_code=200,
    description="List of pets",
    example='''[
    {"id": 1, "name": "Fluffy", "type": "cat"},
    {"id": 2, "name": "Rex", "type": "dog"}
]'''
)

# POST /pets
create_action = builder.add_action(
    resource=pets_resource,
    name="Create Pet",
    method=HttpMethod.POST,
    description="Create a new pet"
)

builder.add_request(
    action=create_action,
    body='''{
    "name": "Buddy",
    "type": "dog",
    "age": 3
}'''
)

builder.add_response(
    action=create_action,
    status_code=201,
    description="Pet created",
    example='''{"id": 3, "name": "Buddy", "type": "dog", "age": 3}'''
)

# 单个Pet资源
pet_resource = builder.add_resource(
    name="Pet",
    uri_template="/pets/{id}",
    description="A single pet",
    group=pets_group
)

# GET /pets/{id}
get_action = builder.add_action(
    resource=pet_resource,
    name="Get Pet",
    method=HttpMethod.GET,
    description="Get a pet by ID"
)

builder.add_request(
    action=get_action,
    parameters=[Parameter(name="id", type_=ParameterType.INTEGER, required=True, description="Pet ID")]
)

builder.add_response(
    action=get_action,
    status_code=200,
    description="Pet found"
)

builder.add_response(
    action=get_action,
    status_code=404,
    description="Pet not found"
)

# 构建
blueprint = builder.build()

# 导出
export_blueprint(blueprint, "petstore.apib")

# 生成Mock服务器
generator = MockServerGenerator(blueprint)
with open("mock_server.py", "w") as f:
    f.write(generator.generate_flask_app())
```

## 输出示例

生成的API Blueprint格式：

```apib
FORMAT: 1A

VERSION: 1.0.0
AUTHOR: Pet Store Team

# Pet Store API

A simple API for managing pets

HOST: https://petstore.example.com

# Group Pets

Everything about pets

## Pets [/pets]

Collection of all pets

### List Pets [GET /pets]

Get a list of all pets

+ Parameters
    + limit (integer) - Maximum results
    + status (string) - Filter by status

+ Response 200 (application/json)

    List of pets

    + Body

            [
                {"id": 1, "name": "Fluffy", "type": "cat"},
                {"id": 2, "name": "Rex", "type": "dog"}
            ]

### Create Pet [POST /pets]

Create a new pet

+ Request (application/json)

    + Body

            {
                "name": "Buddy",
                "type": "dog",
                "age": 3
            }

+ Response 201 (application/json)

    Pet created

    + Body

            {"id": 3, "name": "Buddy", "type": "dog", "age": 3}
```

## Mock服务器示例

生成的Flask Mock服务器：

```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

mock_data = {}

@app.route('/pets', methods=['GET'])
def get_pets():
    """Get a list of all pets"""
    response = [
        {"id": 1, "name": "Fluffy", "type": "cat"},
        {"id": 2, "name": "Rex", "type": "dog"}
    ]
    return jsonify(response), 200

@app.route('/pets', methods=['POST'])
def create_pet():
    """Create a new pet"""
    response = {"id": 3, "name": "Buddy", "type": "dog", "age": 3}
    return jsonify(response), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 配置选项

在 `skill.json` 中配置默认选项：

```json
{
  "config": {
    "default_format": "apib",
    "include_mock": true,
    "validate_on_build": true
  }
}
```

## 注意事项

1. API Blueprint使用特定的语法格式（基于Markdown）
2. 资源URI模板使用 `{param}` 格式
3. Mock服务器基于解析Blueprint中的定义生成
4. 支持从OpenAPI 3.0规范转换
5. 生成的代码包含基本的路由和处理逻辑

## 参考链接

- [API Blueprint Specification](https://apiblueprint.org/documentation/specification.html)
- [Aglio Renderer](https://github.com/danielgtaylor/aglio)
- [Drafter Parser](https://github.com/apiaryio/drafter)

## 许可证

MIT License
