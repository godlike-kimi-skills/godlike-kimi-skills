#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Use Skill - 基础测试

测试内容：
- 浏览器配置
- 实例创建和销毁
- 数据模型
- 基础功能

运行方式：
    python -m pytest tests/test_basic.py -v
"""

import pytest
import asyncio
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import BrowserUseSkill, BrowserConfig, ExtractedData


class TestBrowserConfig:
    """测试浏览器配置类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = BrowserConfig()
        assert config.headless is True
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080
        assert config.timeout == 30000
        assert "Mozilla/5.0" in config.user_agent
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = BrowserConfig(
            headless=False,
            viewport_width=1280,
            viewport_height=720,
            timeout=60000
        )
        assert config.headless is False
        assert config.viewport_width == 1280
        assert config.viewport_height == 720
        assert config.timeout == 60000


class TestExtractedData:
    """测试数据模型"""
    
    def test_extracted_data_creation(self):
        """测试提取数据对象创建"""
        data = ExtractedData(
            url="https://example.com",
            title="Example Domain",
            text_content="Hello World",
            links=[{"text": "Link1", "href": "/link1"}],
            images=[{"src": "/img.jpg", "alt": "Image"}]
        )
        assert data.url == "https://example.com"
        assert data.title == "Example Domain"
        assert len(data.links) == 1
        assert len(data.images) == 1
    
    def test_empty_extracted_data(self):
        """测试空数据对象"""
        data = ExtractedData(url="", title="")
        assert data.elements == []
        assert data.links == []
        assert data.images == []


class TestBrowserUseSkill:
    """测试浏览器技能类"""
    
    def test_skill_initialization(self):
        """测试技能初始化"""
        skill = BrowserUseSkill()
        assert skill.config is not None
        assert skill._is_started is False
        assert skill.browser is None
        assert skill.page is None
    
    def test_skill_with_custom_config(self):
        """测试自定义配置初始化"""
        config = BrowserConfig(headless=False, timeout=10000)
        skill = BrowserUseSkill(config)
        assert skill.config.headless is False
        assert skill.config.timeout == 10000
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """测试启动和停止（需要Playwright）"""
        # 注意：此测试需要安装playwright和浏览器
        pytest.importorskip("playwright")
        
        skill = BrowserUseSkill(BrowserConfig(headless=True))
        
        # 启动
        await skill.start()
        assert skill._is_started is True
        assert skill.browser is not None
        assert skill.page is not None
        
        # 停止
        await skill.stop()
        assert skill._is_started is False
    
    @pytest.mark.asyncio
    async def test_navigation_without_start(self):
        """测试未启动时的导航错误"""
        skill = BrowserUseSkill()
        
        with pytest.raises(RuntimeError) as exc_info:
            await skill.navigate("https://example.com")
        
        assert "未启动" in str(exc_info.value)
    
    def test_directories_created(self):
        """测试目录自动创建"""
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            config = BrowserConfig(
                download_dir=f"{temp_dir}/downloads",
                screenshot_dir=f"{temp_dir}/screenshots"
            )
            skill = BrowserUseSkill(config)
            
            assert Path(config.download_dir).exists()
            assert Path(config.screenshot_dir).exists()
        finally:
            shutil.rmtree(temp_dir)


class TestAsyncOperations:
    """测试异步操作"""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """测试异步上下文管理器"""
        pytest.importorskip("playwright")
        
        async with BrowserUseSkill(BrowserConfig(headless=True)) as skill:
            assert skill._is_started is True
            assert skill.page is not None
        
        # 上下文退出后应该已停止
        # 注意：实际停止状态取决于实现


class TestUtilityMethods:
    """测试工具方法"""
    
    @pytest.mark.asyncio
    async def test_get_set_cookies(self):
        """测试Cookie操作"""
        pytest.importorskip("playwright")
        
        async with BrowserUseSkill(BrowserConfig(headless=True)) as skill:
            await skill.navigate("https://example.com")
            
            # 获取cookies
            cookies = await skill.get_cookies()
            assert isinstance(cookies, list)
            
            # 设置cookies（空列表测试）
            await skill.set_cookies([])


# 集成测试示例
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_workflow():
    """
    完整工作流集成测试
    
    注意：此测试需要网络连接和Playwright
    """
    pytest.importorskip("playwright")
    
    config = BrowserConfig(
        headless=True,
        timeout=30000
    )
    
    async with BrowserUseSkill(config) as skill:
        # 导航
        success = await skill.navigate("https://example.com")
        assert success is True
        
        # 提取数据
        data = await skill.extract_data()
        assert data.url is not None
        assert data.title is not None
        
        # 检查链接
        assert isinstance(data.links, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
