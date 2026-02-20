#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shadcn-ui Skill 基础测试
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from main import ShadcnUI, ShadcnConfig


class TestShadcnConfig:
    """测试 ShadcnConfig 类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = ShadcnConfig()
        assert config.project_path == "."
        assert config.base_color == "slate"
        assert config.css_framework == "tailwind"
        assert config.base_url == "https://ui.shadcn.com"
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = ShadcnConfig(
            project_path="./test",
            base_color="zinc",
            css_framework="css"
        )
        assert config.project_path == "./test"
        assert config.base_color == "zinc"
        assert config.css_framework == "css"
    
    def test_config_to_dict(self):
        """测试配置转字典"""
        config = ShadcnConfig(base_color="stone")
        data = config.to_dict()
        assert data["base_color"] == "stone"
        assert data["project_path"] == "."
    
    def test_config_from_file(self, tmp_path):
        """测试从文件加载配置"""
        components_json = tmp_path / "components.json"
        components_json.write_text(json.dumps({
            "framework": "next",
            "baseColor": "neutral",
            "aliases": {
                "components": "@/components/ui",
                "utils": "@/lib/utils"
            }
        }))
        
        config = ShadcnConfig.from_file(str(components_json))
        assert config.base_color == "neutral"
        assert config.css_framework == "next"
        assert config.components_path == "@/components/ui"
    
    def test_config_from_file_not_found(self):
        """测试文件不存在时的默认配置"""
        config = ShadcnConfig.from_file("non_existent.json")
        assert config.base_color == "slate"


class TestShadcnUI:
    """测试 ShadcnUI 类"""
    
    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def shadcn(self, temp_project):
        """创建 ShadcnUI 实例"""
        config = ShadcnConfig(project_path=temp_project)
        return ShadcnUI(config)
    
    def test_init(self, shadcn, temp_project):
        """测试初始化"""
        assert shadcn.project_path == Path(temp_project).resolve()
        assert shadcn.components_json == Path(temp_project) / "components.json"
    
    def test_is_shadcn_initialized_false(self, shadcn):
        """测试未初始化状态"""
        assert shadcn._is_shadcn_initialized() is False
    
    def test_is_shadcn_initialized_true(self, shadcn, temp_project):
        """测试已初始化状态"""
        components_json = Path(temp_project) / "components.json"
        components_json.write_text(json.dumps({"test": "value"}))
        assert shadcn._is_shadcn_initialized() is True
    
    def test_get_components_dir(self, shadcn, temp_project):
        """测试获取组件目录"""
        # 默认路径
        comp_dir = shadcn._get_components_dir()
        assert comp_dir == Path(temp_project) / "components" / "ui"
        
        # 创建 app/components/ui 目录
        app_dir = Path(temp_project) / "app" / "components" / "ui"
        app_dir.mkdir(parents=True)
        assert shadcn._get_components_dir() == app_dir
    
    def test_get_installed_components_empty(self, shadcn):
        """测试获取空组件列表"""
        assert shadcn._get_installed_components() == []
    
    def test_get_installed_components_with_files(self, shadcn, temp_project):
        """测试获取已安装组件"""
        comp_dir = Path(temp_project) / "components" / "ui"
        comp_dir.mkdir(parents=True)
        (comp_dir / "button.tsx").write_text("")
        (comp_dir / "card.tsx").write_text("")
        (comp_dir / "custom.tsx").write_text("")  # 非官方组件
        
        installed = shadcn._get_installed_components()
        assert "button" in installed
        assert "card" in installed
        assert "custom" not in installed
    
    def test_popular_components_list(self, shadcn):
        """测试组件列表包含常用组件"""
        assert "button" in shadcn.POPULAR_COMPONENTS
        assert "card" in shadcn.POPULAR_COMPONENTS
        assert "dialog" in shadcn.POPULAR_COMPONENTS
        assert "input" in shadcn.POPULAR_COMPONENTS
        assert len(shadcn.POPULAR_COMPONENTS) >= 40
    
    @patch('main.console')
    def test_search_found(self, mock_console, shadcn):
        """测试搜索找到组件"""
        shadcn.search("button")
        # 验证 console.print 被调用
        assert mock_console.print.called
    
    @patch('main.console')
    def test_search_not_found(self, mock_console, shadcn):
        """测试搜索未找到组件"""
        shadcn.search("xyz_nonexistent")
        assert mock_console.print.called
    
    def test_remove_nonexistent(self, shadcn):
        """测试移除不存在的组件"""
        result = shadcn.remove(["nonexistent"])
        assert result is False
    
    def test_remove_existing(self, shadcn, temp_project):
        """测试移除存在的组件"""
        comp_dir = Path(temp_project) / "components" / "ui"
        comp_dir.mkdir(parents=True)
        (comp_dir / "button.tsx").write_text("")
        
        result = shadcn.remove(["button"])
        assert result is True
        assert not (comp_dir / "button.tsx").exists()
    
    def test_generate_component(self, shadcn, temp_project):
        """测试生成组件"""
        result = shadcn.generate_component("TestComponent")
        assert result is True
        
        comp_file = Path(temp_project) / "components" / "ui" / "TestComponent.tsx"
        assert comp_file.exists()
        
        content = comp_file.read_text()
        assert "TestComponentProps" in content
        assert "TestComponent" in content
    
    def test_generate_component_duplicate(self, shadcn, temp_project):
        """测试生成重复组件"""
        comp_dir = Path(temp_project) / "components" / "ui"
        comp_dir.mkdir(parents=True)
        (comp_dir / "Existing.tsx").write_text("")
        
        result = shadcn.generate_component("Existing")
        assert result is False
    
    def test_theme_without_config(self, shadcn):
        """测试无配置时主题设置"""
        result = shadcn.theme(base_color="zinc")
        assert result is False
    
    def test_theme_with_config(self, shadcn, temp_project):
        """测试有配置时主题设置"""
        components_json = Path(temp_project) / "components.json"
        components_json.write_text(json.dumps({"baseColor": "slate"}))
        
        result = shadcn.theme(base_color="zinc")
        assert result is True
        
        # 验证文件被更新
        data = json.loads(components_json.read_text())
        assert data["baseColor"] == "zinc"


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def temp_project(self):
        """创建完整项目结构"""
        temp_dir = tempfile.mkdtemp()
        
        # 创建模拟项目结构
        (Path(temp_dir) / "package.json").write_text(json.dumps({
            "name": "test-app",
            "dependencies": {
                "react": "^18.0.0"
            }
        }))
        (Path(temp_dir) / "tailwind.config.js").write_text("")
        (Path(temp_dir) / "components.json").write_text(json.dumps({
            "framework": "next",
            "baseColor": "slate",
            "aliases": {
                "components": "@/components/ui",
                "utils": "@/lib/utils"
            }
        }))
        
        comp_dir = Path(temp_dir) / "components" / "ui"
        comp_dir.mkdir(parents=True)
        (comp_dir / "button.tsx").write_text("")
        (comp_dir / "card.tsx").write_text("")
        
        lib_dir = Path(temp_dir) / "lib"
        lib_dir.mkdir()
        (lib_dir / "utils.ts").write_text("")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_doctor_with_valid_project(self, temp_project):
        """测试诊断有效项目"""
        config = ShadcnConfig(project_path=temp_project)
        shadcn = ShadcnUI(config)
        
        result = shadcn.doctor()
        assert result is True
    
    def test_update_with_installed_components(self, temp_project):
        """测试更新已安装组件"""
        config = ShadcnConfig(project_path=temp_project)
        shadcn = ShadcnUI(config)
        
        # mock _run_command 避免实际执行 npx
        with patch.object(shadcn, '_run_command') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = shadcn.update()
            assert result is True
            mock_run.assert_called_once()


class TestCLI:
    """测试命令行接口"""
    
    def test_import_main(self):
        """测试 main 模块导入"""
        from main import main
        assert callable(main)
    
    @patch('sys.argv', ['main.py', '--action', 'list'])
    @patch('main.ShadcnUI.list_components')
    def test_cli_list(self, mock_list):
        """测试 list 命令"""
        mock_list.return_value = None
        try:
            from main import main
            main()
        except SystemExit as e:
            assert e.code == 0
        mock_list.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
