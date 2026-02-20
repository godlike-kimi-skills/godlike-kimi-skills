#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Use Skill - AI浏览器自动化工具

功能特点：
- 网页自动浏览和导航
- 智能表单填写
- 结构化数据提取
- 页面截图和可视化
- JavaScript执行
- 异步高性能操作

作者: Godlike Kimi Skills
版本: 1.0.0
许可证: MIT
"""

import asyncio
import base64
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle
from bs4 import BeautifulSoup
from PIL import Image

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BrowserConfig:
    """浏览器配置类"""
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0"
    )
    download_dir: str = "./downloads"
    screenshot_dir: str = "./screenshots"


@dataclass
class ExtractedData:
    """提取的数据结构"""
    url: str
    title: str
    elements: List[Dict[str, Any]] = field(default_factory=list)
    text_content: str = ""
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)


class BrowserUseSkill:
    """
    AI浏览器自动化核心类
    
    提供完整的浏览器自动化功能，包括导航、交互、数据提取和截图。
    基于Playwright构建，支持异步高性能操作。
    
    示例用法:
        skill = BrowserUseSkill()
        await skill.start()
        
        # 访问网页
        await skill.navigate("https://example.com")
        
        # 填写表单
        await skill.fill_form({
            "#username": "myuser",
            "#password": "mypass"
        })
        
        # 提取数据
        data = await skill.extract_data()
        
        # 截图
        await skill.screenshot("page.png")
        
        await skill.stop()
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """
        初始化浏览器技能
        
        Args:
            config: 浏览器配置对象，使用默认配置如果未提供
        """
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._is_started = False
        
        # 确保目录存在
        Path(self.config.download_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    async def start(self) -> "BrowserUseSkill":
        """
        启动浏览器实例
        
        Returns:
            self: 支持链式调用
        """
        if self._is_started:
            logger.warning("浏览器已经启动")
            return self
        
        logger.info("正在启动浏览器...")
        self.playwright = await async_playwright().start()
        
        # 启动Chromium浏览器
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--window-size={},{}".format(
                    self.config.viewport_width,
                    self.config.viewport_height
                )
            ]
        )
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            },
            user_agent=self.config.user_agent,
            accept_downloads=True
        )
        
        # 设置下载路径
        self.context.set_default_timeout(self.config.timeout)
        
        # 创建新页面
        self.page = await self.context.new_page()
        
        self._is_started = True
        logger.info("浏览器启动成功")
        return self
    
    async def stop(self) -> None:
        """关闭浏览器并清理资源"""
        if not self._is_started:
            return
        
        logger.info("正在关闭浏览器...")
        
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self._is_started = False
        logger.info("浏览器已关闭")
    
    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        导航到指定URL
        
        Args:
            url: 目标网址
            wait_until: 等待条件 (load/domcontentloaded/networkidle)
        
        Returns:
            bool: 导航是否成功
        """
        if not self._is_started:
            raise RuntimeError("浏览器未启动，请先调用start()")
        
        try:
            logger.info(f"正在访问: {url}")
            response = await self.page.goto(
                url,
                wait_until=wait_until,
                timeout=self.config.timeout
            )
            
            if response:
                status = response.status
                logger.info(f"页面加载完成，状态码: {status}")
                return 200 <= status < 400
            return False
            
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False
    
    async def fill_form(self, data: Dict[str, str], submit: bool = False) -> bool:
        """
        填写表单
        
        Args:
            data: 表单数据，键为选择器，值为输入内容
            submit: 是否自动提交表单
        
        Returns:
            bool: 是否成功
        """
        if not self._is_started:
            raise RuntimeError("浏览器未启动")
        
        try:
            for selector, value in data.items():
                logger.info(f"填写字段 {selector}: {value}")
                
                # 等待元素可见
                await self.page.wait_for_selector(selector, state="visible")
                
                # 清除现有内容
                await self.page.fill(selector, "")
                
                # 输入新值
                await self.page.fill(selector, value)
            
            if submit:
                # 查找提交按钮
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("提交")',
                    'button:has-text("登录")',
                    'button:has-text("Submit")',
                    'button:has-text("Login")'
                ]
                
                for sel in submit_selectors:
                    try:
                        await self.page.click(sel, timeout=2000)
                        logger.info(f"表单已提交 via {sel}")
                        await self.page.wait_for_load_state("networkidle")
                        break
                    except:
                        continue
            
            return True
            
        except Exception as e:
            logger.error(f"表单填写失败: {e}")
            return False
    
    async def click(self, selector: str, wait_for_navigation: bool = False) -> bool:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            wait_for_navigation: 是否等待页面导航
        
        Returns:
            bool: 是否成功
        """
        try:
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await self.page.click(selector)
            else:
                await self.page.click(selector)
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False
    
    async def extract_data(self, selectors: Optional[Dict[str, str]] = None) -> ExtractedData:
        """
        提取页面数据
        
        Args:
            selectors: 自定义提取选择器
        
        Returns:
            ExtractedData: 提取的数据对象
        """
        if not self._is_started:
            raise RuntimeError("浏览器未启动")
        
        try:
            # 获取页面信息
            url = self.page.url
            title = await self.page.title()
            
            # 获取页面内容
            html = await self.page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取文本
            text_content = soup.get_text(separator='\n', strip=True)
            
            # 提取链接
            links = []
            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href'])
                links.append({
                    'text': a.get_text(strip=True),
                    'href': href
                })
            
            # 提取图片
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    images.append({
                        'src': urljoin(url, src),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            # 提取表单
            forms = []
            for form in soup.find_all('form'):
                inputs = []
                for inp in form.find_all(['input', 'textarea', 'select']):
                    inputs.append({
                        'type': inp.get('type', inp.name),
                        'name': inp.get('name', ''),
                        'id': inp.get('id', ''),
                        'required': inp.get('required') is not None
                    })
                forms.append({
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': inputs
                })
            
            # 提取表格
            tables = []
            for table in soup.find_all('table'):
                headers = []
                rows = []
                
                for th in table.find_all('th'):
                    headers.append(th.get_text(strip=True))
                
                for tr in table.find_all('tr'):
                    row = []
                    for td in tr.find_all('td'):
                        row.append(td.get_text(strip=True))
                    if row:
                        rows.append(row)
                
                tables.append({'headers': headers, 'rows': rows})
            
            # 自定义选择器提取
            elements = []
            if selectors:
                for name, selector in selectors.items():
                    try:
                        el = await self.page.query_selector(selector)
                        if el:
                            text = await el.text_content()
                            elements.append({
                                'name': name,
                                'selector': selector,
                                'text': text.strip() if text else ''
                            })
                    except Exception as e:
                        logger.warning(f"提取 {name} 失败: {e}")
            
            return ExtractedData(
                url=url,
                title=title,
                elements=elements,
                text_content=text_content[:10000],  # 限制长度
                links=links[:100],  # 限制数量
                images=images[:50],
                forms=forms,
                tables=tables
            )
            
        except Exception as e:
            logger.error(f"数据提取失败: {e}")
            return ExtractedData(url=self.page.url if self.page else "", title="")
    
    async def screenshot(
        self,
        filename: Optional[str] = None,
        full_page: bool = True,
        selector: Optional[str] = None
    ) -> str:
        """
        截取页面截图
        
        Args:
            filename: 保存文件名，自动生成如果未提供
            full_page: 是否截取完整页面
            selector: 指定元素选择器，只截取该元素
        
        Returns:
            str: 截图文件路径
        """
        if not self._is_started:
            raise RuntimeError("浏览器未启动")
        
        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = Path(self.config.screenshot_dir) / filename
            
            if selector:
                element = await self.page.query_selector(selector)
                if element:
                    await element.screenshot(path=str(filepath))
                else:
                    raise ValueError(f"未找到元素: {selector}")
            else:
                await self.page.screenshot(
                    path=str(filepath),
                    full_page=full_page
                )
            
            logger.info(f"截图已保存: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    async def execute_javascript(self, script: str) -> Any:
        """
        在页面中执行JavaScript
        
        Args:
            script: JavaScript代码
        
        Returns:
            Any: 执行结果
        """
        if not self._is_started:
            raise RuntimeError("浏览器未启动")
        
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"JavaScript执行失败: {e}")
            raise
    
    async def scroll_to_bottom(self) -> None:
        """滚动到页面底部"""
        await self.page.evaluate("""
            () => {
                window.scrollTo(0, document.body.scrollHeight);
            }
        """)
        await asyncio.sleep(0.5)
    
    async def scroll_to_top(self) -> None:
        """滚动到页面顶部"""
        await self.page.evaluate("""
            () => {
                window.scrollTo(0, 0);
            }
        """)
        await asyncio.sleep(0.5)
    
    async def wait_for_element(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> bool:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            state: 等待状态 (attached/detached/visible/hidden)
            timeout: 超时时间(毫秒)
        
        Returns:
            bool: 是否成功
        """
        try:
            await self.page.wait_for_selector(
                selector,
                state=state,
                timeout=timeout or self.config.timeout
            )
            return True
        except Exception as e:
            logger.warning(f"等待元素超时: {e}")
            return False
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """获取当前页面的cookies"""
        return await self.context.cookies()
    
    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """设置cookies"""
        await self.context.add_cookies(cookies)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self._is_started:
            asyncio.run(self.stop())
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()


async def main():
    """
    示例用法
    """
    # 使用配置创建实例
    config = BrowserConfig(
        headless=False,  # 显示浏览器窗口
        viewport_width=1920,
        viewport_height=1080
    )
    
    async with BrowserUseSkill(config) as skill:
        # 访问网页
        success = await skill.navigate("https://example.com")
        
        if success:
            # 提取数据
            data = await skill.extract_data()
            print(f"页面标题: {data.title}")
            print(f"页面链接数: {len(data.links)}")
            
            # 截图
            screenshot_path = await skill.screenshot("example.png")
            print(f"截图保存至: {screenshot_path}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
