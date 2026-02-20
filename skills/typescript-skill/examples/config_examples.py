#!/usr/bin/env python3
"""TypeScript Skill - 配置生成示例"""

import sys
sys.path.insert(0, '..')

from main import TypeScriptGenerator
import json

def main():
    generator = TypeScriptGenerator()
    
    print("=" * 70)
    print("TypeScript Skill - 配置生成示例")
    print("=" * 70)
    
    # 示例1: 默认配置
    print("\n1. 默认 tsconfig.json")
    print("-" * 50)
    
    default_config = generator.generate_tsconfig()
    print(json.dumps(default_config, indent=2))
    
    # 示例2: React项目配置
    print("\n2. React项目 tsconfig.json")
    print("-" * 50)
    
    react_config = generator.generate_tsconfig({
        "target": "ES2020",
        "lib": ["ES2020", "DOM", "DOM.Iterable"],
        "jsx": "react-jsx",
        "module": "ESNext",
        "moduleResolution": "bundler",
        "allowJs": True,
        "checkJs": False
    })
    print(json.dumps(react_config, indent=2))
    
    # 示例3: Node.js项目配置
    print("\n3. Node.js项目 tsconfig.json")
    print("-" * 50)
    
    node_config = generator.generate_tsconfig({
        "target": "ES2020",
        "lib": ["ES2020"],
        "module": "commonjs",
        "moduleResolution": "node",
        "outDir": "./dist",
        "rootDir": "./src",
        "resolveJsonModule": True,
        "esModuleInterop": True
    })
    # 更新include和exclude
    node_config["include"] = ["src/**/*"]
    node_config["exclude"] = ["node_modules", "dist", "**/*.test.ts"]
    print(json.dumps(node_config, indent=2))
    
    # 示例4: 严格模式配置
    print("\n4. 严格模式 tsconfig.json")
    print("-" * 50)
    
    strict_config = generator.generate_tsconfig({
        "strict": True,
        "noImplicitAny": True,
        "strictNullChecks": True,
        "strictFunctionTypes": True,
        "strictBindCallApply": True,
        "strictPropertyInitialization": True,
        "noImplicitThis": True,
        "alwaysStrict": True,
        "noUnusedLocals": True,
        "noUnusedParameters": True,
        "noImplicitReturns": True,
        "noFallthroughCasesInSwitch": True
    })
    print(json.dumps(strict_config, indent=2))
    
    # 示例5: 库开发配置
    print("\n5. 库开发 tsconfig.json")
    print("-" * 50)
    
    lib_config = generator.generate_tsconfig({
        "target": "ES2015",
        "module": "ESNext",
        "lib": ["ES2015", "DOM"],
        "declaration": True,
        "declarationMap": True,
        "sourceMap": True,
        "outDir": "./lib",
        "strict": True,
        "esModuleInterop": True,
        "skipLibCheck": True,
        "forceConsistentCasingInFileNames": True
    })
    print(json.dumps(lib_config, indent=2))
    
    # 示例6: Vue类型声明
    print("\n6. Vue类型声明 (vue-shims.d.ts)")
    print("-" * 50)
    
    vue_shims = generator.generate_vue_shims()
    print(vue_shims)
    
    # 示例7: 配置验证
    print("\n7. 类型字符串验证")
    print("-" * 50)
    
    test_types = [
        "string",
        "number",
        "boolean",
        "string[]",
        "Array<number>",
        "{ name: string; age: number }",
        "string | number",
        "User & Timestamp",
        "invalid type @#$",
        "",
    ]
    
    for type_str in test_types:
        valid, error = generator.validate_type_string(type_str)
        status = "✓ Valid" if valid else f"✗ Invalid: {error}"
        display = type_str if type_str else "(empty)"
        print(f"  '{display}' -> {status}")
    
    # 示例8: OpenAPI Schema转换
    print("\n8. OpenAPI Schema 转 TypeScript")
    print("-" * 50)
    
    pet_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "format": "int64"},
            "name": {"type": "string"},
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                }
            },
            "photoUrls": {
                "type": "array",
                "items": {"type": "string"}
            },
            "status": {
                "type": "string",
                "enum": ["available", "pending", "sold"]
            }
        },
        "required": ["name", "photoUrls"]
    }
    
    pet_interface = generator.generate_from_openapi(pet_schema, "Pet")
    print(pet_interface)
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
