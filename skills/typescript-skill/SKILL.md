# TypeScript Skill

TypeScript类型生成和检查工具，提供接口生成、类型推导、配置优化和类型安全验证功能。

## Description

TypeScript类型生成和检查工具。支持接口生成、类型推导、配置优化和类型安全验证。Use when developing frontend applications, working with TypeScript, or when user mentions 'TypeScript', 'types', 'interface', 'React', 'Vue'.

## Features

- **接口生成**：从JSON/对象自动生成TypeScript接口
- **类型推导**：智能类型推断和生成
- **配置优化**：tsconfig.json配置生成和优化
- **类型验证**：类型兼容性和完整性检查
- **泛型支持**：复杂泛型类型生成
- **工具类型**：常用工具类型模板库

## Installation

```bash
# 安装依赖
pip install -r requirements.txt
```

## Usage

### 从JSON生成接口

```python
from main import TypeScriptGenerator

generator = TypeScriptGenerator()

# 从JSON生成接口
json_data = {
    "id": 1,
    "name": "John",
    "email": "john@example.com",
    "isActive": True
}

interface = generator.generate_interface("User", json_data)
print(interface)
```

### 生成类型配置

```python
# 生成tsconfig.json
config = generator.generate_tsconfig({
    "target": "ES2020",
    "module": "ESNext",
    "strict": True
})
generator.save_tsconfig(config, "./tsconfig.json")
```

### 命令行使用

```bash
# 从JSON文件生成接口
python main.py interface User --from-json ./user.json

# 生成React组件Props类型
python main.py props Button --props label:string,onClick:function

# 生成tsconfig.json
python main.py tsconfig --target ES2020 --strict

# 验证类型
python main.py validate "{ name: string, age: number }"
```

## API Reference

### TypeScriptGenerator

主生成器类，提供所有核心功能。

#### Methods

- `generate_interface(name, data, options)` - 从数据生成接口
- `generate_type(name, definition)` - 生成类型别名
- `generate_enum(name, values)` - 生成枚举类型
- `generate_generic(name, params, definition)` - 生成泛型类型
- `generate_tsconfig(options)` - 生成TypeScript配置
- `infer_type(value)` - 推断值类型
- `validate_type(type_str)` - 验证类型字符串
- `merge_interfaces(interfaces)` - 合并接口

### UtilityTypes

常用工具类型库。

#### Available Utilities

- `Partial<T>` - 所有属性变为可选
- `Required<T>` - 所有属性变为必需
- `Readonly<T>` - 所有属性变为只读
- `Pick<T, K>` - 选取指定属性
- `Omit<T, K>` - 省略指定属性
- `Record<K, T>` - 键值对类型

## Examples

查看 `examples/` 目录获取更多使用示例：

- `interface_examples.py` - 接口生成示例
- `type_examples.py` - 类型生成示例
- `config_examples.py` - 配置生成示例

## Testing

```bash
# 运行测试
python test.py
```

## License

MIT License
