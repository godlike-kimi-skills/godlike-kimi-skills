#!/usr/bin/env python3
"""TypeScript Skill - 类型生成示例"""

import sys
sys.path.insert(0, '..')

from main import TypeScriptGenerator, UtilityTypes

def main():
    generator = TypeScriptGenerator()
    
    print("=" * 70)
    print("TypeScript Skill - 类型生成示例")
    print("=" * 70)
    
    # 示例1: 基本类型别名
    print("\n1. 基本类型别名")
    print("-" * 50)
    
    types = [
        ("UserID", "string"),
        ("Timestamp", "number"),
        ("JSONValue", "string | number | boolean | null | JSONObject | JSONArray"),
        ("JSONObject", "{ [key: string]: JSONValue }"),
        ("JSONArray", "JSONValue[]"),
    ]
    
    for name, definition in types:
        type_alias = generator.generate_type_alias(name, definition)
        print(type_alias)
    
    # 示例2: 联合类型
    print("\n2. 联合类型")
    print("-" * 50)
    
    union_types = [
        ("Status", ["'pending'", "'active'", "'inactive'", "'deleted'"]),
        ("Theme", ["'light'", "'dark'", "'auto'"]),
        ("Size", ["'xs'", "'sm'", "'md'", "'lg'", "'xl'"]),
    ]
    
    for name, types_list in union_types:
        union = generator.generate_union_type(name, types_list)
        print(union)
    
    # 示例3: 泛型类型
    print("\n3. 泛型类型")
    print("-" * 50)
    
    generics = [
        ("ApiResponse", ["T"], "{ data: T; success: boolean; message?: string }"),
        ("PaginatedResult", ["T"], "{ items: T[]; total: number; page: number; pageSize: number }"),
        ("AsyncState", ["T"], "{ data: T | null; loading: boolean; error: Error | null }"),
    ]
    
    for name, params, definition in generics:
        generic_type = generator.generate_type_alias(name, definition, generics=params)
        print(generic_type)
    
    # 示例4: 函数类型
    print("\n4. 函数类型")
    print("-" * 50)
    
    functions = [
        ("EventHandler", [("event", "Event")], "void"),
        ("Comparator", [("a", "T"), ("b", "T")], "number", ["T"]),
        ("AsyncFunction", [("args", "Parameters<T>")], "Promise<ReturnType<T>>", ["T extends (...args: any) => any"]),
    ]
    
    for name, params, return_type, *generics in functions:
        gen = generics[0] if generics else None
        func_type = generator.generate_function_type(name, params, return_type, gen)
        print(func_type)
    
    # 示例5: 枚举类型
    print("\n5. 枚举类型")
    print("-" * 50)
    
    # 字符串枚举
    status_enum = generator.generate_enum("Status", ["Active", "Inactive", "Pending"])
    print(status_enum)
    print()
    
    # 数值枚举
    priority_enum = generator.generate_enum("Priority", {"Low": 1, "Medium": 2, "High": 3})
    print(priority_enum)
    print()
    
    # const枚举
    direction_enum = generator.generate_enum("Direction", ["Up", "Down", "Left", "Right"], is_const=True)
    print(direction_enum)
    
    # 示例6: 工具类型
    print("\n6. 工具类型模板")
    print("-" * 50)
    
    templates = UtilityTypes.list_templates()
    for template_name in templates[:5]:  # 显示前5个
        template = UtilityTypes.get_template(template_name)
        print(template)
        print()
    
    # 示例7: 类型推断
    print("\n7. 类型推断示例")
    print("-" * 50)
    
    values = [
        "Hello World",
        42,
        True,
        [1, 2, 3],
        ["a", "b", "c"],
        {"name": "John", "age": 30},
        None,
    ]
    
    for value in values:
        inferred = generator.infer_type(value)
        value_str = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
        print(f"  {value_str:<35} -> {inferred}")
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
