#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Builder 基础测试
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import MCPBuilder


class TestMCPBuilder(unittest.TestCase):
    """测试MCPBuilder类"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.test_dir = tempfile.mkdtemp(prefix="mcp_test_")
        self.builder = MCPBuilder(self.test_dir)
    
    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init_server_stdio_basic(self):
        """测试基本stdio服务器初始化"""
        result = self.builder.init_server(
            name="test-server",
            transport="stdio",
            force=True
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["transport"], "stdio")
        self.assertIn("hello", result["templates"])
        
        # 检查文件创建
        self.assertTrue(Path(self.test_dir).exists())
        self.assertTrue((Path(self.test_dir) / "server.py").exists())
        self.assertTrue((Path(self.test_dir) / "config.json").exists())
        self.assertTrue((Path(self.test_dir) / "requirements.txt").exists())
    
    def test_init_server_sse(self):
        """测试SSE服务器初始化"""
        result = self.builder.init_server(
            name="sse-server",
            transport="sse",
            port=8080,
            force=True
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["transport"], "sse")
        
        # 检查配置文件
        config_path = Path(self.test_dir) / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["transport"], "sse")
        self.assertEqual(config["port"], 8080)
    
    def test_init_server_with_templates(self):
        """测试带模板的初始化"""
        result = self.builder.init_server(
            name="weather-server",
            transport="stdio",
            templates=["weather", "calculator"],
            force=True
        )
        
        self.assertTrue(result["success"])
        self.assertIn("weather", result["templates"])
        self.assertIn("calculator", result["templates"])
        
        # 检查服务器文件包含工具代码
        server_path = Path(self.test_dir) / "server.py"
        content = server_path.read_text(encoding="utf-8")
        
        self.assertIn("get_current_weather", content)
        self.assertIn("calculate", content)
    
    def test_init_server_without_force(self):
        """测试不强制覆盖时的行为"""
        # 先创建目录
        os.makedirs(self.test_dir, exist_ok=True)
        (Path(self.test_dir) / "existing.txt").write_text("test")
        
        # 不设置force，应该失败
        result = self.builder.init_server(name="test")
        
        self.assertFalse(result["success"])
        self.assertIn("已存在", result["error"])
    
    def test_validate_valid_config(self):
        """测试验证有效配置"""
        # 先创建有效配置
        self.builder.init_server(name="test", force=True)
        
        result = self.builder.validate()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["issues"]), 0)
    
    def test_validate_missing_files(self):
        """测试验证缺少文件"""
        os.makedirs(self.test_dir, exist_ok=True)
        
        result = self.builder.validate()
        
        self.assertFalse(result["valid"])
        self.assertTrue(len(result["issues"]) > 0)
        self.assertTrue(any("缺少" in issue for issue in result["issues"]))
    
    def test_validate_invalid_json(self):
        """测试验证无效JSON"""
        os.makedirs(self.test_dir, exist_ok=True)
        config_path = Path(self.test_dir) / "config.json"
        config_path.write_text("invalid json{", encoding="utf-8")
        
        result = self.builder.validate()
        
        self.assertFalse(result["valid"])
        self.assertTrue(any("JSON" in issue for issue in result["issues"]))
    
    def test_add_tool(self):
        """测试添加工具"""
        # 先初始化服务器
        self.builder.init_server(name="test", force=True)
        
        result = self.builder.add_tool("my_tool", "我的工具描述")
        
        self.assertTrue(result["success"])
        
        # 检查工具文件
        tool_path = Path(self.test_dir) / "tools" / "my_tool.py"
        self.assertTrue(tool_path.exists())
        
        content = tool_path.read_text(encoding="utf-8")
        self.assertIn("my_tool", content)
        self.assertIn("我的工具描述", content)
    
    def test_all_templates(self):
        """测试所有预设模板"""
        all_templates = ["weather", "search", "calculator", "file"]
        
        result = self.builder.init_server(
            name="full-server",
            templates=all_templates,
            force=True
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["templates"]), 4)
        
        # 检查服务器文件
        server_path = Path(self.test_dir) / "server.py"
        content = server_path.read_text(encoding="utf-8")
        
        # 验证各模板的关键字
        self.assertIn("get_current_weather", content)  # weather
        self.assertIn("web_search", content)  # search
        self.assertIn("convert_unit", content)  # calculator
        self.assertIn("read_file", content)  # file


class TestTemplates(unittest.TestCase):
    """测试模板内容"""
    
    def test_weather_template_structure(self):
        """测试天气模板结构"""
        from main import WEATHER_TOOL_TEMPLATE
        
        self.assertIn("get_current_weather", WEATHER_TOOL_TEMPLATE)
        self.assertIn("get_forecast", WEATHER_TOOL_TEMPLATE)
        self.assertIn("location", WEATHER_TOOL_TEMPLATE)
    
    def test_search_template_structure(self):
        """测试搜索模板结构"""
        from main import SEARCH_TOOL_TEMPLATE
        
        self.assertIn("web_search", SEARCH_TOOL_TEMPLATE)
        self.assertIn("local_search", SEARCH_TOOL_TEMPLATE)
        self.assertIn("query", SEARCH_TOOL_TEMPLATE)
    
    def test_calculator_template_structure(self):
        """测试计算器模板结构"""
        from main import CALCULATOR_TOOL_TEMPLATE
        
        self.assertIn("calculate", CALCULATOR_TOOL_TEMPLATE)
        self.assertIn("convert_unit", CALCULATOR_TOOL_TEMPLATE)
        self.assertIn("expression", CALCULATOR_TOOL_TEMPLATE)
    
    def test_file_template_structure(self):
        """测试文件模板结构"""
        from main import FILE_TOOL_TEMPLATE
        
        self.assertIn("read_file", FILE_TOOL_TEMPLATE)
        self.assertIn("write_file", FILE_TOOL_TEMPLATE)
        self.assertIn("list_directory", FILE_TOOL_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
