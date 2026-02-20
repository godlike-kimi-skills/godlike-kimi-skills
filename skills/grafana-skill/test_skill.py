#!/usr/bin/env python3
"""
Grafana Skill 测试套件
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from main import GrafanaClient, DashboardInfo


class MockResponse:
    """模拟HTTP响应"""
    def __init__(self, data, status=200):
        self.data = json.dumps(data).encode('utf-8')
        self.status = status
    
    def read(self):
        return self.data
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass


class TestGrafanaClient(unittest.TestCase):
    """测试Grafana客户端"""
    
    def setUp(self):
        self.client = GrafanaClient("http://localhost:3000")
    
    @patch('urllib.request.urlopen')
    def test_health_check(self, mock_urlopen):
        """测试健康检查"""
        mock_response_data = {
            "commit": "abc123",
            "database": "ok",
            "version": "9.0.0"
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.health_check()
        
        self.assertEqual(result['status'], 'healthy')
        self.assertEqual(result['version'], '9.0.0')
        self.assertEqual(result['database'], 'ok')
    
    @patch('urllib.request.urlopen')
    def test_list_dashboards(self, mock_urlopen):
        """测试列出仪表板"""
        mock_response_data = [
            {"id": 1, "uid": "abc123", "title": "Test Dashboard", "type": "dash-db"},
            {"id": 2, "uid": "def456", "title": "Another Dashboard", "type": "dash-db"}
        ]
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.list_dashboards()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test Dashboard')
        self.assertEqual(result[0]['uid'], 'abc123')
    
    @patch('urllib.request.urlopen')
    def test_get_dashboard(self, mock_urlopen):
        """测试获取仪表板"""
        mock_response_data = {
            "dashboard": {
                "id": 1,
                "uid": "abc123",
                "title": "Test Dashboard",
                "panels": [{"id": 1, "title": "Panel 1"}],
                "tags": ["test", "demo"]
            },
            "meta": {
                "folderId": 0,
                "folderTitle": "General"
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.get_dashboard("abc123")
        
        self.assertEqual(result['dashboard']['title'], 'Test Dashboard')
        self.assertEqual(len(result['dashboard']['panels']), 1)
        self.assertEqual(result['meta']['folderTitle'], 'General')
    
    @patch('urllib.request.urlopen')
    def test_create_dashboard(self, mock_urlopen):
        """测试创建仪表板"""
        mock_response_data = {
            "id": 1,
            "uid": "new-uid",
            "url": "/d/new-uid/test-dashboard",
            "status": "success"
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.create_dashboard(
            title="Test Dashboard",
            panels=[{"id": 1, "title": "Panel 1", "type": "graph"}]
        )
        
        self.assertEqual(result['uid'], 'new-uid')
        self.assertEqual(result['status'], 'success')
    
    @patch('urllib.request.urlopen')
    def test_delete_dashboard(self, mock_urlopen):
        """测试删除仪表板"""
        mock_response_data = {"title": "Test Dashboard", "message": "Dashboard deleted"}
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.delete_dashboard("abc123")
        
        self.assertEqual(result['message'], 'Dashboard deleted')
    
    @patch('urllib.request.urlopen')
    def test_list_data_sources(self, mock_urlopen):
        """测试列出数据源"""
        mock_response_data = [
            {"id": 1, "name": "Prometheus", "type": "prometheus"},
            {"id": 2, "name": "InfluxDB", "type": "influxdb"}
        ]
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.list_data_sources()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Prometheus')
        self.assertEqual(result[1]['type'], 'influxdb')
    
    @patch('urllib.request.urlopen')
    def test_create_data_source(self, mock_urlopen):
        """测试创建数据源"""
        mock_response_data = {
            "id": 3,
            "name": "New Prometheus",
            "type": "prometheus",
            "message": "Datasource added"
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.create_data_source(
            name="New Prometheus",
            type="prometheus",
            url="http://prometheus:9090"
        )
        
        self.assertEqual(result['name'], 'New Prometheus')
        self.assertEqual(result['id'], 3)
    
    @patch('urllib.request.urlopen')
    def test_list_folders(self, mock_urlopen):
        """测试列出文件夹"""
        mock_response_data = [
            {"id": 1, "uid": "abc", "title": "Infrastructure"},
            {"id": 2, "uid": "def", "title": "Applications"}
        ]
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.list_folders()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Infrastructure')
    
    @patch('urllib.request.urlopen')
    def test_create_folder(self, mock_urlopen):
        """测试创建文件夹"""
        mock_response_data = {
            "id": 3,
            "uid": "new-folder",
            "title": "New Folder"
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.create_folder("New Folder")
        
        self.assertEqual(result['title'], 'New Folder')
        self.assertEqual(result['uid'], 'new-folder')
    
    @patch('urllib.request.urlopen')
    def test_search(self, mock_urlopen):
        """测试搜索"""
        mock_response_data = [
            {"id": 1, "uid": "abc", "title": "CPU Dashboard", "type": "dash-db"}
        ]
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.search("CPU")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'CPU Dashboard')
    
    def test_create_panel(self):
        """测试创建面板配置"""
        panel = self.client.create_panel(
            title="CPU Usage",
            panel_type="timeseries",
            targets=[{"expr": "cpu_usage"}],
            grid_pos={"x": 0, "y": 0, "w": 12, "h": 8},
            unit="percent"
        )
        
        self.assertEqual(panel['title'], 'CPU Usage')
        self.assertEqual(panel['type'], 'timeseries')
        self.assertEqual(panel['gridPos']['w'], 12)
        self.assertEqual(panel['fieldConfig']['defaults']['unit'], 'percent')
    
    def test_create_panel_gauge(self):
        """测试创建Gauge面板"""
        panel = self.client.create_panel(
            title="Memory",
            panel_type="gauge",
            unit="percent",
            min=0,
            max=100
        )
        
        self.assertEqual(panel['type'], 'gauge')
        self.assertEqual(panel['options']['showThresholdLabels'], True)
    
    @patch.object(GrafanaClient, 'get_dashboard')
    @patch.object(GrafanaClient, 'create_dashboard')
    def test_clone_dashboard(self, mock_create, mock_get):
        """测试克隆仪表板"""
        mock_get.return_value = {
            "dashboard": {
                "id": 1,
                "uid": "source-uid",
                "title": "Original Dashboard",
                "panels": [{"id": 1}],
                "tags": ["test"]
            }
        }
        mock_create.return_value = {"uid": "new-uid", "url": "/d/new-uid"}
        
        result = self.client.clone_dashboard("source-uid", "Cloned Dashboard")
        
        mock_get.assert_called_once_with("source-uid")
        mock_create.assert_called_once()
        create_call_args = mock_create.call_args
        self.assertEqual(create_call_args[1]['title'], 'Cloned Dashboard')
    
    def test_export_dashboard(self):
        """测试导出仪表板"""
        with patch.object(self.client, 'get_dashboard') as mock_get:
            mock_get.return_value = {
                "dashboard": {
                    "id": 1,
                    "uid": "test-uid",
                    "title": "Test Dashboard",
                    "panels": [],
                    "version": 5
                }
            }
            
            result = self.client.export_dashboard("test-uid")
            
            self.assertEqual(result['title'], 'Test Dashboard')
            self.assertNotIn('id', result)  # 应该被清理
            self.assertNotIn('uid', result)  # 应该被清理
    
    @patch.object(GrafanaClient, 'list_dashboards')
    @patch.object(GrafanaClient, 'list_folders')
    @patch.object(GrafanaClient, 'list_data_sources')
    def test_generate_report(self, mock_ds, mock_folders, mock_dashboards):
        """测试生成报告"""
        mock_ds.return_value = [{"id": 1, "name": "Prometheus", "type": "prometheus"}]
        mock_folders.return_value = [{"id": 1, "title": "Test"}]
        mock_dashboards.return_value = [{"uid": "abc", "title": "Test Dashboard"}]
        
        with patch.object(self.client, 'get_dashboard') as mock_get:
            mock_get.return_value = {
                "dashboard": {"title": "Test", "uid": "abc", "panels": [{}]},
                "meta": {"folderTitle": "General"}
            }
            
            report = self.client.generate_report(output_format='json')
            report_data = json.loads(report)
            
            self.assertIn('generated_at', report_data)
            self.assertEqual(report_data['summary']['total_dashboards'], 1)
            self.assertEqual(report_data['summary']['total_folders'], 1)
    
    def test_format_markdown_report(self):
        """测试Markdown报告格式化"""
        report = {
            "generated_at": "2024-01-01T00:00:00",
            "grafana_url": "http://localhost:3000",
            "summary": {"total_dashboards": 2, "total_folders": 1, "total_data_sources": 1},
            "folders": [{"id": 1, "title": "General"}],
            "data_sources": [{"id": 1, "name": "Prometheus", "type": "prometheus"}],
            "dashboards": [
                {"title": "Dashboard 1", "folder": "General", "panels": 5, "tags": ["test"]},
                {"title": "Dashboard 2", "folder": "General", "panels": 3, "tags": []}
            ]
        }
        
        markdown = self.client._format_markdown_report(report)
        
        self.assertIn('# Grafana 资源报告', markdown)
        self.assertIn('Dashboard 1', markdown)
        self.assertIn('Prometheus', markdown)


class TestAuthentication(unittest.TestCase):
    """测试认证方式"""
    
    def test_api_key_auth(self):
        """测试API Key认证"""
        client = GrafanaClient("http://localhost:3000", api_key="test-key")
        self.assertEqual(client.headers['Authorization'], 'Bearer test-key')
    
    def test_basic_auth(self):
        """测试Basic Auth认证"""
        client = GrafanaClient("http://localhost:3000", basic_auth=("admin", "admin"))
        auth_header = client.headers['Authorization']
        self.assertTrue(auth_header.startswith('Basic '))


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    def setUp(self):
        self.client = GrafanaClient("http://localhost:3000")
    
    @patch('urllib.request.urlopen')
    def test_http_error(self, mock_urlopen):
        """测试HTTP错误"""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            url='http://localhost:3000/api/dashboards/uid/test',
            code=404,
            msg='Not Found',
            hdrs={},
            fp=None
        )
        
        with self.assertRaises(Exception) as context:
            self.client.get_dashboard("test")
        
        self.assertIn("HTTP Error 404", str(context.exception))
    
    @patch('urllib.request.urlopen')
    def test_connection_error(self, mock_urlopen):
        """测试连接错误"""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")
        
        with self.assertRaises(Exception) as context:
            self.client.list_dashboards()
        
        self.assertIn("Connection failed", str(context.exception))


class TestDataSourceTypes(unittest.TestCase):
    """测试数据源类型"""
    
    def test_data_source_types_defined(self):
        """测试数据源类型定义"""
        client = GrafanaClient("http://localhost:3000")
        
        self.assertIn('prometheus', client.DATA_SOURCE_TYPES)
        self.assertIn('influxdb', client.DATA_SOURCE_TYPES)
        self.assertIn('mysql', client.DATA_SOURCE_TYPES)
        self.assertIn('postgres', client.DATA_SOURCE_TYPES)
        self.assertIn('elasticsearch', client.DATA_SOURCE_TYPES)


class TestPanelTypes(unittest.TestCase):
    """测试面板类型"""
    
    def test_panel_types_defined(self):
        """测试面板类型定义"""
        client = GrafanaClient("http://localhost:3000")
        
        self.assertIn('timeseries', client.PANEL_TYPES)
        self.assertIn('graph', client.PANEL_TYPES)
        self.assertIn('gauge', client.PANEL_TYPES)
        self.assertIn('stat', client.PANEL_TYPES)
        self.assertIn('table', client.PANEL_TYPES)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestGrafanaClient))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDataSourceTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestPanelTypes))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
