#!/usr/bin/env python3
"""
TypeScript Skill - 类型生成和检查工具
支持接口生成、类型推导、配置优化
"""

import json
import re
import sys
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from colorama import init, Fore, Style

init()


class TypeScriptType(Enum):
    """TypeScript内置类型枚举"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    NULL = "null"
    UNDEFINED = "undefined"
    ANY = "any"
    UNKNOWN = "unknown"
    NEVER = "never"
    VOID = "void"
    OBJECT = "object"
    SYMBOL = "symbol"
    BIGINT = "bigint"


@dataclass
class InterfaceProperty:
    """接口属性定义"""
    name: str
    type_str: str
    optional: bool = False
    readonly: bool = False
    description: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class InterfaceDefinition:
    """接口定义"""
    name: str
    properties: List[InterfaceProperty] = field(default_factory=list)
    extends: Optional[List[str]] = None
    generics: Optional[List[str]] = None
    export: bool = True


class UtilityTypes:
    """TypeScript工具类型库"""
    
    TEMPLATES = {
        "Partial": "type Partial<T> = { [P in keyof T]?: T[P]; }",
        "Required": "type Required<T> = { [P in keyof T]-?: T[P]; }",
        "Readonly": "type Readonly<T> = { readonly [P in keyof T]: T[P]; }",
        "Pick": "type Pick<T, K extends keyof T> = { [P in K]: T[P]; }",
        "Omit": "type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>",
        "Record": "type Record<K extends keyof any, T> = { [P in K]: T; }",
        "Exclude": "type Exclude<T, U> = T extends U ? never : T",
        "Extract": "type Extract<T, U> = T extends U ? T : never",
        "NonNullable": "type NonNullable<T> = T extends null | undefined ? never : T",
        "Parameters": "type Parameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never",
        "ReturnType": "type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any",
        "Awaited": "type Awaited<T> = T extends PromiseLike<infer U> ? Awaited<U> : T",
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[str]:
        """获取工具类型模板"""
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """列出所有可用模板"""
        return list(cls.TEMPLATES.keys())


class TypeScriptGenerator:
    """TypeScript类型生成器"""
    
    # TypeScript修饰符
    ACCESS_MODIFIERS = ["public", "private", "protected", "readonly"]
    
    # 常见类型映射
    PRIMITIVE_TYPES = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
    }
    
    def __init__(self):
        self.indent = "  "
        self.generated_types: Dict[str, str] = {}
    
    def infer_type(self, value: Any) -> str:
        """
        推断Python值的TypeScript类型
        
        Args:
            value: Python值
        
        Returns:
            TypeScript类型字符串
        """
        if value is None:
            return "null"
        
        if isinstance(value, bool):
            return "boolean"
        
        if isinstance(value, int) or isinstance(value, float):
            return "number"
        
        if isinstance(value, str):
            return "string"
        
        if isinstance(value, list):
            if not value:
                return "any[]"
            # 推断数组元素类型
            element_types = {self.infer_type(item) for item in value}
            if len(element_types) == 1:
                return f"{list(element_types)[0]}[]"
            else:
                return f"({ ' | '.join(element_types) })[]"
        
        if isinstance(value, dict):
            if not value:
                return "Record<string, any>"
            # 推断对象类型
            properties = []
            for k, v in value.items():
                prop_type = self.infer_type(v)
                properties.append(f"{k}: {prop_type}")
            return f"{{ {', '.join(properties)} }}"
        
        if isinstance(value, tuple):
            types = [self.infer_type(item) for item in value]
            return f"[{', '.join(types)}]"
        
        return "any"
    
    def generate_interface(
        self,
        name: str,
        data: Union[Dict[str, Any], List[InterfaceProperty]],
        extends: Optional[List[str]] = None,
        export: bool = True,
        description: Optional[str] = None
    ) -> str:
        """
        生成TypeScript接口
        
        Args:
            name: 接口名称
            data: 数据字典或属性列表
            extends: 继承的接口列表
            export: 是否导出
            description: 接口描述
        
        Returns:
            TypeScript接口代码
        """
        lines = []
        
        # 添加描述注释
        if description:
            lines.append(f"/** {description} */")
        
        # 接口声明
        export_str = "export " if export else ""
        extends_str = ""
        if extends:
            extends_str = " extends " + ", ".join(extends)
        
        lines.append(f"{export_str}interface {name}{extends_str} {{")
        
        # 添加属性
        if isinstance(data, dict):
            for key, value in data.items():
                type_str = self.infer_type(value)
                optional = False
                
                # 处理可选属性（值可能为null或undefined）
                if value is None:
                    optional = True
                    type_str = "any"
                
                prop_def = f"{self.indent}{key}"
                if optional:
                    prop_def += "?"
                prop_def += f": {type_str};"
                
                # 添加注释（如果是对象或数组）
                if isinstance(value, (dict, list)) and value:
                    prop_def += f" // {str(value)[:50]}..."
                
                lines.append(prop_def)
        else:
            for prop in data:
                prop_line = self.indent
                if prop.readonly:
                    prop_line += "readonly "
                prop_line += prop.name
                if prop.optional:
                    prop_line += "?"
                prop_line += f": {prop.type_str}"
                if prop.default_value:
                    prop_line += f" = {prop.default_value}"
                prop_line += ";"
                lines.append(prop_line)
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_type_alias(
        self,
        name: str,
        definition: str,
        generics: Optional[List[str]] = None,
        export: bool = True,
        description: Optional[str] = None
    ) -> str:
        """
        生成类型别名
        
        Args:
            name: 类型名称
            definition: 类型定义
            generics: 泛型参数
            export: 是否导出
            description: 类型描述
        
        Returns:
            TypeScript类型别名代码
        """
        lines = []
        
        if description:
            lines.append(f"/** {description} */")
        
        export_str = "export " if export else ""
        generics_str = ""
        if generics:
            generics_str = f"<{', '.join(generics)}>"
        
        lines.append(f"{export_str}type {name}{generics_str} = {definition};")
        
        return "\n".join(lines)
    
    def generate_enum(
        self,
        name: str,
        values: Union[List[str], Dict[str, Union[str, int]]],
        is_const: bool = False,
        export: bool = True
    ) -> str:
        """
        生成枚举类型
        
        Args:
            name: 枚举名称
            values: 枚举值列表或字典
            is_const: 是否为const枚举
            export: 是否导出
        
        Returns:
            TypeScript枚举代码
        """
        export_str = "export " if export else ""
        const_str = "const " if is_const else ""
        
        lines = [f"{export_str}{const_str}enum {name} {{"]
        
        if isinstance(values, list):
            for i, value in enumerate(values):
                lines.append(f"{self.indent}{value} = \"{value}\",")
        else:
            for key, value in values.items():
                if isinstance(value, str):
                    lines.append(f"{self.indent}{key} = \"{value}\",")
                else:
                    lines.append(f"{self.indent}{key} = {value},")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_union_type(
        self,
        name: str,
        types: List[str],
        export: bool = True
    ) -> str:
        """生成联合类型"""
        union = " | ".join(types)
        return self.generate_type_alias(name, union, export=export)
    
    def generate_function_type(
        self,
        name: str,
        params: List[Tuple[str, str]],
        return_type: str,
        generics: Optional[List[str]] = None,
        export: bool = True
    ) -> str:
        """
        生成函数类型
        
        Args:
            name: 类型名称
            params: 参数列表 [(param_name, param_type)]
            return_type: 返回类型
            generics: 泛型参数
            export: 是否导出
        
        Returns:
            TypeScript函数类型代码
        """
        params_str = ", ".join([f"{p}: {t}" for p, t in params])
        definition = f"({params_str}) => {return_type}"
        
        return self.generate_type_alias(name, definition, generics, export)
    
    def generate_react_props(
        self,
        component_name: str,
        props: Dict[str, Any],
        extends: Optional[str] = None,
        with_children: bool = False
    ) -> str:
        """
        生成React组件Props类型
        
        Args:
            component_name: 组件名称
            props: 属性定义
            extends: 继承的基础Props
            with_children: 是否包含children
        
        Returns:
            TypeScript Props接口代码
        """
        interface_name = f"{component_name}Props"
        
        properties = []
        for prop_name, prop_value in props.items():
            if isinstance(prop_value, dict):
                prop_type = prop_value.get("type", "any")
                optional = prop_value.get("optional", False)
            else:
                prop_type = self.infer_type(prop_value)
                optional = prop_value is None
            
            properties.append(InterfaceProperty(
                name=prop_name,
                type_str=prop_type,
                optional=optional
            ))
        
        # 添加children属性
        if with_children:
            properties.append(InterfaceProperty(
                name="children",
                type_str="React.ReactNode",
                optional=True
            ))
        
        extends_list = []
        if extends:
            extends_list.append(extends)
        
        return self.generate_interface(
            interface_name,
            properties,
            extends=extends_list if extends_list else None
        )
    
    def generate_tsconfig(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成tsconfig.json配置
        
        Args:
            options: 自定义选项
        
        Returns:
            tsconfig配置字典
        """
        default_config = {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "forceConsistentCasingInFileNames": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "build"]
        }
        
        if options:
            default_config["compilerOptions"].update(options)
        
        return default_config
    
    def generate_vue_shims(self) -> str:
        """生成Vue类型声明文件"""
        return '''declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
'''
    
    def validate_type_string(self, type_str: str) -> Tuple[bool, Optional[str]]:
        """
        验证类型字符串有效性
        
        Args:
            type_str: 类型字符串
        
        Returns:
            (是否有效, 错误信息)
        """
        # 基本类型检查
        valid_primitives = ["string", "number", "boolean", "null", "undefined", 
                          "any", "unknown", "never", "void", "object", "symbol", "bigint"]
        
        # 去除空白
        clean_type = type_str.strip()
        
        if not clean_type:
            return False, "Empty type string"
        
        # 检查基本类型
        if clean_type in valid_primitives:
            return True, None
        
        # 检查数组类型
        if clean_type.endswith("[]"):
            base_type = clean_type[:-2]
            return self.validate_type_string(base_type)
        
        # 检查泛型
        generic_match = re.match(r'^(\w+)<(.+)>$', clean_type)
        if generic_match:
            return True, None  # 简化处理
        
        # 检查对象字面量
        if clean_type.startswith("{") and clean_type.endswith("}"):
            return True, None
        
        # 检查联合类型
        if "|" in clean_type:
            types = [t.strip() for t in clean_type.split("|")]
            for t in types:
                valid, error = self.validate_type_string(t)
                if not valid:
                    return False, f"Invalid union member: {error}"
            return True, None
        
        # 检查交叉类型
        if "&" in clean_type:
            types = [t.strip() for t in clean_type.split("&")]
            for t in types:
                valid, error = self.validate_type_string(t)
                if not valid:
                    return False, f"Invalid intersection member: {error}"
            return True, None
        
        # 检查是否为有效的标识符
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', clean_type):
            return True, None
        
        return False, f"Invalid type syntax: {type_str}"
    
    def parse_interface_from_json(self, json_str: str) -> Dict[str, Any]:
        """从JSON字符串解析接口数据"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def save_tsconfig(self, config: Dict[str, Any], filepath: str) -> None:
        """保存配置到tsconfig.json文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def generate_from_openapi(
        self,
        schema: Dict[str, Any],
        type_name: Optional[str] = None
    ) -> str:
        """
        从OpenAPI Schema生成TypeScript类型
        
        Args:
            schema: OpenAPI schema对象
            type_name: 类型名称
        
        Returns:
            TypeScript类型定义
        """
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            interface_props = []
            for prop_name, prop_schema in properties.items():
                is_required = prop_name in required
                ts_type = self._openapi_to_ts_type(prop_schema)
                
                interface_props.append(InterfaceProperty(
                    name=prop_name,
                    type_str=ts_type,
                    optional=not is_required
                ))
            
            name = type_name or "GeneratedType"
            return self.generate_interface(name, interface_props)
        
        elif schema_type == "array":
            items = schema.get("items", {})
            item_type = self._openapi_to_ts_type(items)
            return f"{item_type}[]"
        
        return "any"
    
    def _openapi_to_ts_type(self, schema: Dict[str, Any]) -> str:
        """将OpenAPI类型转换为TypeScript类型"""
        schema_type = schema.get("type", "any")
        
        type_mapping = {
            "string": "string",
            "integer": "number",
            "number": "number",
            "boolean": "boolean",
            "array": "any[]",
            "object": "object"
        }
        
        if "enum" in schema:
            return " | ".join([f'"{v}"' for v in schema["enum"]])
        
        if "$ref" in schema:
            # 提取引用名称
            ref = schema["$ref"]
            return ref.split("/")[-1]
        
        if schema_type == "array" and "items" in schema:
            item_type = self._openapi_to_ts_type(schema["items"])
            return f"{item_type}[]"
        
        return type_mapping.get(schema_type, "any")


def main():
    """命令行入口"""
    generator = TypeScriptGenerator()
    
    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}TypeScript Skill v1.0.0{Style.RESET_ALL}")
        print("\nUsage:")
        print("  python main.py interface <name> --from-json <file>  - Generate interface from JSON")
        print("  python main.py type <name> <definition>             - Generate type alias")
        print("  python main.py enum <name> <values...>              - Generate enum")
        print("  python main.py tsconfig [options]                   - Generate tsconfig.json")
        print("  python main.py validate <type>                      - Validate type string")
        print("\nExamples:")
        print('  python main.py interface User --from-json user.json')
        print('  python main.py type ID string | number')
        print('  python main.py enum Status active inactive pending')
        print('  python main.py tsconfig --target ES2020 --strict')
        return
    
    command = sys.argv[1]
    
    if command == "interface":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Interface name required{Style.RESET_ALL}")
            return
        
        name = sys.argv[2]
        
        # 检查是否有--from-json参数
        if "--from-json" in sys.argv:
            json_idx = sys.argv.index("--from-json")
            if json_idx + 1 < len(sys.argv):
                json_file = sys.argv[json_idx + 1]
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except FileNotFoundError:
                    print(f"{Fore.RED}Error: File not found: {json_file}{Style.RESET_ALL}")
                    return
            else:
                print(f"{Fore.RED}Error: JSON file path required{Style.RESET_ALL}")
                return
        else:
            # 使用示例数据
            data = {"id": 1, "name": "example", "active": True}
        
        interface = generator.generate_interface(name, data)
        print(f"{Fore.GREEN}{interface}{Style.RESET_ALL}")
    
    elif command == "type":
        if len(sys.argv) < 4:
            print(f"{Fore.RED}Error: Type name and definition required{Style.RESET_ALL}")
            return
        name = sys.argv[2]
        definition = " ".join(sys.argv[3:])
        type_alias = generator.generate_type_alias(name, definition)
        print(f"{Fore.GREEN}{type_alias}{Style.RESET_ALL}")
    
    elif command == "enum":
        if len(sys.argv) < 4:
            print(f"{Fore.RED}Error: Enum name and values required{Style.RESET_ALL}")
            return
        name = sys.argv[2]
        values = sys.argv[3:]
        enum_code = generator.generate_enum(name, values)
        print(f"{Fore.GREEN}{enum_code}{Style.RESET_ALL}")
    
    elif command == "tsconfig":
        options = {}
        if "--target" in sys.argv:
            idx = sys.argv.index("--target")
            if idx + 1 < len(sys.argv):
                options["target"] = sys.argv[idx + 1]
        if "--strict" in sys.argv:
            options["strict"] = True
        
        config = generator.generate_tsconfig(options)
        print(f"{Fore.GREEN}{json.dumps(config, indent=2)}{Style.RESET_ALL}")
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Type string required{Style.RESET_ALL}")
            return
        type_str = " ".join(sys.argv[2:])
        valid, error = generator.validate_type_string(type_str)
        if valid:
            print(f"{Fore.GREEN}✓ Valid type: {type_str}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Invalid type: {error}{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
