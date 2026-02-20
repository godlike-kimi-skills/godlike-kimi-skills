#!/usr/bin/env python3
"""TypeScript Skill - 测试文件"""

import unittest
import sys
sys.path.insert(0, '.')

from main import TypeScriptGenerator, UtilityTypes, InterfaceProperty


class TestTypeScriptGenerator(unittest.TestCase):
    """测试TypeScriptGenerator类"""
    
    def setUp(self):
        self.generator = TypeScriptGenerator()
    
    def test_infer_type_primitive(self):
        """测试基本类型推断"""
        self.assertEqual(self.generator.infer_type("hello"), "string")
        self.assertEqual(self.generator.infer_type(42), "number")
        self.assertEqual(self.generator.infer_type(3.14), "number")
        self.assertEqual(self.generator.infer_type(True), "boolean")
        self.assertEqual(self.generator.infer_type(None), "null")
    
    def test_infer_type_array(self):
        """测试数组类型推断"""
        self.assertEqual(self.generator.infer_type([1, 2, 3]), "number[]")
        self.assertEqual(self.generator.infer_type(["a", "b"]), "string[]")
        self.assertEqual(self.generator.infer_type([]), "any[]")
    
    def test_infer_type_object(self):
        """测试对象类型推断"""
        obj = {"name": "John", "age": 30}
        result = self.generator.infer_type(obj)
        self.assertIn("name:", result)
        self.assertIn("age:", result)
        self.assertIn("string", result)
        self.assertIn("number", result)
    
    def test_generate_interface(self):
        """测试接口生成"""
        data = {
            "id": 1,
            "name": "Test",
            "active": True
        }
        interface = self.generator.generate_interface("User", data)
        self.assertIn("export interface User", interface)
        self.assertIn("id: number;", interface)
        self.assertIn("name: string;", interface)
        self.assertIn("active: boolean;", interface)
    
    def test_generate_interface_with_extends(self):
        """测试继承接口生成"""
        data = {"email": "test@example.com"}
        interface = self.generator.generate_interface("Admin", data, extends=["User"])
        self.assertIn("extends User", interface)
    
    def test_generate_type_alias(self):
        """测试类型别名生成"""
        type_alias = self.generator.generate_type_alias("ID", "string | number")
        self.assertIn("export type ID", type_alias)
        self.assertIn("= string | number;", type_alias)
    
    def test_generate_type_alias_with_generics(self):
        """测试泛型类型别名生成"""
        type_alias = self.generator.generate_type_alias(
            "Response",
            "{ data: T; success: boolean }",
            generics=["T"]
        )
        self.assertIn("export type Response<T>", type_alias)
    
    def test_generate_enum(self):
        """测试枚举生成"""
        enum_code = self.generator.generate_enum("Status", ["Active", "Inactive", "Pending"])
        self.assertIn("export enum Status", enum_code)
        self.assertIn("Active = \"Active\"", enum_code)
        self.assertIn("Inactive = \"Inactive\"", enum_code)
    
    def test_generate_enum_with_values(self):
        """测试带值的枚举生成"""
        values = {"Low": 1, "Medium": 2, "High": 3}
        enum_code = self.generator.generate_enum("Priority", values)
        self.assertIn("Low = 1", enum_code)
        self.assertIn("Medium = 2", enum_code)
        self.assertIn("High = 3", enum_code)
    
    def test_generate_union_type(self):
        """测试联合类型生成"""
        union = self.generator.generate_union_type("Status", ["'active'", "'inactive'"])
        self.assertIn("'active' | 'inactive'", union)
    
    def test_generate_function_type(self):
        """测试函数类型生成"""
        func_type = self.generator.generate_function_type(
            "Handler",
            [("event", "Event"), ("data", "any")],
            "void"
        )
        self.assertIn("(event: Event, data: any) => void", func_type)
    
    def test_generate_react_props(self):
        """测试React Props生成"""
        props = {
            "label": "string",
            "onClick": {"type": "() => void", "optional": False}
        }
        interface = self.generator.generate_react_props("Button", props)
        self.assertIn("interface ButtonProps", interface)
        self.assertIn("label: string", interface)
        self.assertIn("onClick: () => void", interface)
    
    def test_generate_react_props_with_children(self):
        """测试带children的React Props"""
        interface = self.generator.generate_react_props("Card", {}, with_children=True)
        self.assertIn("children?: React.ReactNode", interface)
    
    def test_generate_tsconfig(self):
        """测试tsconfig生成"""
        config = self.generator.generate_tsconfig()
        self.assertIn("compilerOptions", config)
        self.assertIn("include", config)
        self.assertEqual(config["compilerOptions"]["target"], "ES2020")
    
    def test_generate_tsconfig_with_options(self):
        """测试带选项的tsconfig生成"""
        config = self.generator.generate_tsconfig({"target": "ES2022", "strict": False})
        self.assertEqual(config["compilerOptions"]["target"], "ES2022")
        self.assertEqual(config["compilerOptions"]["strict"], False)
    
    def test_generate_vue_shims(self):
        """测试Vue类型声明生成"""
        shims = self.generator.generate_vue_shims()
        self.assertIn("declare module '*.vue'", shims)
        self.assertIn("DefineComponent", shims)
    
    def test_validate_type_string_valid(self):
        """测试有效类型验证"""
        valid_types = ["string", "number", "boolean", "string[]", "any", "MyType"]
        for type_str in valid_types:
            valid, error = self.generator.validate_type_string(type_str)
            self.assertTrue(valid, f"Type '{type_str}' should be valid")
            self.assertIsNone(error)
    
    def test_validate_type_string_invalid(self):
        """测试无效类型验证"""
        invalid_types = ["", "123", "string|number|", "{invalid}"]
        for type_str in invalid_types:
            if type_str:  # 跳过空字符串
                valid, error = self.generator.validate_type_string(type_str)
                self.assertFalse(valid, f"Type '{type_str}' should be invalid")
    
    def test_parse_interface_from_json(self):
        """测试JSON解析"""
        json_str = '{"name": "John", "age": 30}'
        result = self.generator.parse_interface_from_json(json_str)
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)
    
    def test_parse_interface_from_invalid_json(self):
        """测试无效JSON解析"""
        with self.assertRaises(ValueError):
            self.generator.parse_interface_from_json("{invalid json}")
    
    def test_generate_from_openapi_schema(self):
        """测试OpenAPI Schema转换"""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            "required": ["id"]
        }
        result = self.generator.generate_from_openapi(schema, "User")
        self.assertIn("interface User", result)
        self.assertIn("id: number", result)
        self.assertIn("name: string", result)
    
    def test_openapi_to_ts_type(self):
        """测试OpenAPI类型转换"""
        self.assertEqual(self.generator._openapi_to_ts_type({"type": "string"}), "string")
        self.assertEqual(self.generator._openapi_to_ts_type({"type": "integer"}), "number")
        self.assertEqual(self.generator._openapi_to_ts_type({"enum": ["a", "b"]}), '"a" | "b"')


class TestUtilityTypes(unittest.TestCase):
    """测试UtilityTypes类"""
    
    def test_get_template(self):
        """测试获取模板"""
        template = UtilityTypes.get_template("Partial")
        self.assertIsNotNone(template)
        self.assertIn("Partial<T>", template)
    
    def test_get_template_invalid(self):
        """测试获取无效模板"""
        template = UtilityTypes.get_template("Invalid")
        self.assertIsNone(template)
    
    def test_list_templates(self):
        """测试列出所有模板"""
        templates = UtilityTypes.list_templates()
        self.assertIn("Partial", templates)
        self.assertIn("Required", templates)
        self.assertIn("Pick", templates)
        self.assertIn("Omit", templates)


class TestInterfaceProperty(unittest.TestCase):
    """测试InterfaceProperty数据类"""
    
    def test_create_property(self):
        """测试创建属性"""
        prop = InterfaceProperty(
            name="test",
            type_str="string",
            optional=True,
            readonly=True
        )
        self.assertEqual(prop.name, "test")
        self.assertEqual(prop.type_str, "string")
        self.assertTrue(prop.optional)
        self.assertTrue(prop.readonly)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTypeScriptGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestInterfaceProperty))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
