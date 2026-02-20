#!/usr/bin/env python3
"""
Prometheus Skill 测试套件
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from main import PrometheusClient, QueryResult


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


class TestPrometheusClient(unittest.TestCase):
    """测试Prometheus客户端"""
    
    def setUp(self):
        self.client = PrometheusClient("http://localhost:9090")
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_query(self, mock_request, mock_urlopen):
        """测试即时查询"""
        mock_response_data = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "up", "job": "prometheus"},
                        "value": [1234567890.123, "1"]
                    }
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.query('up{job="prometheus"}')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['resultType'], 'vector')
        self.assertEqual(len(result['data']['result']), 1)
        self.assertEqual(result['data']['result'][0]['value'][1], "1")
    
    @patch('urllib.request.urlopen')
    def test_query_range(self, mock_urlopen):
        """测试范围查询"""
        mock_response_data = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage"},
                        "values": [
                            [1234567890, "10"],
                            [1234567950, "15"],
                            [1234568010, "20"]
                        ]
                    }
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.query_range(
            'cpu_usage',
            start='-1h',
            end='now',
            step='1m'
        )
        
        self.assertEqual(result['data']['resultType'], 'matrix')
        self.assertEqual(len(result['data']['result'][0]['values']), 3)
    
    @patch('urllib.request.urlopen')
    def test_labels(self, mock_urlopen):
        """测试获取标签"""
        mock_response_data = {
            "status": "success",
            "data": ["job", "instance", "__name__"]
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.labels()
        
        self.assertIn('data', result)
        self.assertIn('job', result['data'])
        self.assertIn('instance', result['data'])
    
    @patch('urllib.request.urlopen')
    def test_label_values(self, mock_urlopen):
        """测试获取标签值"""
        mock_response_data = {
            "status": "success",
            "data": ["prometheus", "node-exporter", "grafana"]
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.label_values('job')
        
        self.assertIn('prometheus', result['data'])
        self.assertIn('node-exporter', result['data'])
    
    @patch('urllib.request.urlopen')
    def test_targets(self, mock_urlopen):
        """测试获取目标"""
        mock_response_data = {
            "status": "success",
            "data": {
                "activeTargets": [
                    {
                        "discoveredLabels": {"__address__": "localhost:9090"},
                        "labels": {"job": "prometheus", "instance": "localhost:9090"},
                        "health": "up",
                        "lastError": "",
                        "lastScrape": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.targets()
        
        self.assertEqual(len(result['data']['activeTargets']), 1)
        self.assertEqual(result['data']['activeTargets'][0]['health'], 'up')
    
    @patch('urllib.request.urlopen')
    def test_alert_rules(self, mock_urlopen):
        """测试获取告警规则"""
        mock_response_data = {
            "status": "success",
            "data": {
                "groups": [
                    {
                        "name": "alert.rules",
                        "file": "/etc/prometheus/alerts.yml",
                        "interval": 15,
                        "rules": [
                            {
                                "name": "HighCPUUsage",
                                "query": "cpu_usage > 80",
                                "duration": 300,
                                "state": "inactive"
                            }
                        ]
                    }
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.alert_rules()
        
        self.assertEqual(len(result['data']['groups']), 1)
        self.assertEqual(result['data']['groups'][0]['rules'][0]['name'], 'HighCPUUsage')
    
    @patch('urllib.request.urlopen')
    def test_active_alerts(self, mock_urlopen):
        """测试获取活动告警"""
        mock_response_data = {
            "status": "success",
            "data": {
                "alerts": [
                    {
                        "labels": {"alertname": "HighMemoryUsage", "severity": "warning"},
                        "annotations": {"summary": "Memory usage is high"},
                        "state": "firing",
                        "activeAt": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        alerts = self.client.active_alerts()
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['state'], 'firing')
    
    @patch('urllib.request.urlopen')
    def test_metadata(self, mock_urlopen):
        """测试获取元数据"""
        mock_response_data = {
            "status": "success",
            "data": {
                "up": [
                    {"type": "gauge", "help": "The up metric", "unit": ""}
                ],
                "cpu_usage": [
                    {"type": "gauge", "help": "CPU usage percentage", "unit": "percent"}
                ]
            }
        }
        mock_urlopen.return_value = MockResponse(mock_response_data)
        
        result = self.client.metadata()
        
        self.assertIn('up', result['data'])
        self.assertIn('cpu_usage', result['data'])
    
    def test_parse_time(self):
        """测试时间解析"""
        # 测试相对时间
        result = self.client._parse_time('now')
        self.assertTrue(result.endswith('Z'))
        
        # 测试负时间
        result = self.client._parse_time('-1h')
        self.assertTrue(result.endswith('Z'))
        
        result = self.client._parse_time('-30m')
        self.assertTrue(result.endswith('Z'))
        
        result = self.client._parse_time('-1d')
        self.assertTrue(result.endswith('Z'))
        
        # 测试绝对时间
        result = self.client._parse_time('2024-01-01T00:00:00Z')
        self.assertEqual(result, '2024-01-01T00:00:00Z')
    
    def test_parse_duration(self):
        """测试持续时间解析"""
        self.assertEqual(self.client._parse_duration('1m'), '1m')
        self.assertEqual(self.client._parse_duration('5m'), '5m')
        self.assertEqual(self.client._parse_duration('1h'), '1h')
        self.assertEqual(self.client._parse_duration('1d'), '1d')
        
        with self.assertRaises(ValueError):
            self.client._parse_duration('invalid')
    
    def test_export_to_csv(self):
        """测试CSV导出"""
        data = {
            "resultType": "vector",
            "result": [
                {"metric": {"job": "test"}, "value": [1234567890, "10"]}
            ]
        }
        csv_output = self.client._to_csv(data)
        self.assertIn('metric,timestamp,value', csv_output)
        self.assertIn('10', csv_output)
    
    def test_export_to_prometheus_format(self):
        """测试Prometheus格式导出"""
        data = {
            "result": [
                {"metric": {"__name__": "cpu", "job": "test"}, "value": [0, "10"]}
            ]
        }
        prom_output = self.client._to_prometheus_format(data)
        self.assertIn('cpu{job="test"} 10', prom_output)
    
    def test_generate_report(self):
        """测试生成报告"""
        with patch.object(self.client, 'query') as mock_query:
            mock_query.return_value = {
                "status": "success",
                "data": {"resultType": "vector", "result": [{"value": [0, "1"]}]}
            }
            
            queries = {
                "cpu": "cpu_usage",
                "memory": "memory_usage"
            }
            
            report = self.client.generate_report(queries, output_format='json')
            report_data = json.loads(report)
            
            self.assertIn('generated_at', report_data)
            self.assertIn('results', report_data)
            self.assertEqual(len(report_data['results']), 2)
    
    def test_find_metrics(self):
        """测试查找指标"""
        with patch.object(self.client, 'metadata') as mock_metadata:
            mock_metadata.return_value = {
                "data": {
                    "cpu_usage": {},
                    "cpu_idle": {},
                    "memory_usage": {},
                    "disk_usage": {}
                }
            }
            
            metrics = self.client.find_metrics('cpu_*')
            self.assertIn('cpu_usage', metrics)
            self.assertIn('cpu_idle', metrics)
            self.assertNotIn('memory_usage', metrics)


class TestQueryResult(unittest.TestCase):
    """测试查询结果类"""
    
    def test_get_value(self):
        """测试获取值"""
        result = QueryResult(
            metric={"job": "test"},
            value=[1234567890, "42.5"]
        )
        self.assertEqual(result.get_value(), 42.5)
    
    def test_get_timestamp(self):
        """测试获取时间戳"""
        result = QueryResult(
            metric={"job": "test"},
            value=[1234567890.5, "1"]
        )
        self.assertEqual(result.get_timestamp(), 1234567890.5)
    
    def test_empty_value(self):
        """测试空值处理"""
        result = QueryResult(metric={"job": "test"})
        self.assertEqual(result.get_value(), 0.0)
        self.assertEqual(result.get_timestamp(), 0.0)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    def setUp(self):
        self.client = PrometheusClient("http://localhost:9090")
    
    @patch('urllib.request.urlopen')
    def test_query_error(self, mock_urlopen):
        """测试查询错误"""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            url='http://localhost:9090/api/v1/query',
            code=400,
            msg='Bad Request',
            hdrs={},
            fp=None
        )
        
        with self.assertRaises(Exception):
            self.client.query('invalid query')
    
    @patch('urllib.request.urlopen')
    def test_connection_error(self, mock_urlopen):
        """测试连接错误"""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")
        
        with self.assertRaises(Exception) as context:
            self.client.query('up')
        
        self.assertIn("Connection failed", str(context.exception))


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPrometheusClient))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryResult))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
