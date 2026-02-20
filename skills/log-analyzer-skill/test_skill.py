#!/usr/bin/env python3
"""
Log Analyzer Skill 测试套件
"""

import unittest
import json
import tempfile
import os
from datetime import datetime
from main import LogParser, LogAnalyzer, NginxLogEntry, ApacheLogEntry


class TestLogParser(unittest.TestCase):
    """测试日志解析器"""
    
    def setUp(self):
        self.parser = LogParser()
    
    def test_parse_nginx_line(self):
        """测试Nginx日志解析"""
        line = '192.168.1.1 - - [20/Feb/2026:10:30:00 +0800] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0" 0.023'
        entry = self.parser.parse_nginx_line(line)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.ip, '192.168.1.1')
        self.assertEqual(entry.method, 'GET')
        self.assertEqual(entry.url, '/api/users')
        self.assertEqual(entry.status_code, 200)
        self.assertEqual(entry.response_size, 1234)
        self.assertEqual(entry.response_time, 0.023)
        self.assertIsNotNone(entry.timestamp)
    
    def test_parse_nginx_line_without_response_time(self):
        """测试无响应时间的Nginx日志"""
        line = '192.168.1.1 - - [20/Feb/2026:10:30:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        entry = self.parser.parse_nginx_line(line)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.status_code, 200)
        self.assertEqual(entry.response_time, 0.0)
    
    def test_parse_apache_line(self):
        """测试Apache日志解析"""
        line = '192.168.1.1 - frank [20/Feb/2026:10:30:00 +0800] "GET /apache_pb.gif HTTP/1.0" 200 2326'
        entry = self.parser.parse_apache_line(line)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.ip, '192.168.1.1')
        self.assertEqual(entry.userid, 'frank')
        self.assertEqual(entry.method, 'GET')
        self.assertEqual(entry.url, '/apache_pb.gif')
        self.assertEqual(entry.status_code, 200)
        self.assertEqual(entry.response_size, 2326)
    
    def test_parse_timestamp(self):
        """测试时间戳解析"""
        # Nginx格式
        ts = self.parser.parse_timestamp('20/Feb/2026:10:30:00 +0800')
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)
        self.assertEqual(ts.month, 2)
        self.assertEqual(ts.day, 20)
        
        # ISO格式
        ts = self.parser.parse_timestamp('2026-02-20 10:30:00')
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)
    
    def test_parse_generic_line(self):
        """测试通用日志解析"""
        line = '2026-02-20 10:30:00 ERROR Connection failed to database'
        entry = self.parser.parse_generic_line(line)
        
        self.assertEqual(entry.level, 'ERROR')
        self.assertIn('Connection failed', entry.message)
        self.assertIsNotNone(entry.timestamp)
    
    def test_detect_format_nginx(self):
        """测试Nginx格式检测"""
        lines = [
            '192.168.1.1 - - [20/Feb/2026:10:30:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        ]
        fmt = self.parser.detect_format(lines)
        self.assertEqual(fmt, 'nginx')
    
    def test_detect_format_apache(self):
        """测试Apache格式检测"""
        lines = [
            '192.168.1.1 - - [20/Feb/2026:10:30:00 +0800] "GET / HTTP/1.1" 200 512'
        ]
        fmt = self.parser.detect_format(lines)
        self.assertEqual(fmt, 'apache')
    
    def test_detect_format_json(self):
        """测试JSON格式检测"""
        lines = ['{"timestamp": "2026-02-20", "level": "INFO", "message": "test"}']
        fmt = self.parser.detect_format(lines)
        self.assertEqual(fmt, 'json')


class TestLogAnalyzer(unittest.TestCase):
    """测试日志分析器"""
    
    def setUp(self):
        self.analyzer = LogAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content):
        """创建测试日志文件"""
        path = os.path.join(self.temp_dir, 'test.log')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_analyze_nginx_log(self):
        """测试Nginx日志分析"""
        content = '''192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0" 0.023
192.168.1.2 - - [20/Feb/2026:10:01:00 +0800] "GET /api HTTP/1.1" 200 1024 "-" "Mozilla/5.0" 0.045
192.168.1.1 - - [20/Feb/2026:10:02:00 +0800] "POST /login HTTP/1.1" 404 256 "-" "Mozilla/5.0" 0.012
192.168.1.3 - - [20/Feb/2026:10:03:00 +0800] "GET /error HTTP/1.1" 500 128 "-" "Mozilla/5.0" 0.156'''
        
        path = self.create_test_file(content)
        result = self.analyzer.analyze_nginx_log(path)
        
        self.assertEqual(result['total_requests'], 4)
        self.assertEqual(result['unique_visitors'], 3)
        self.assertEqual(result['error_requests'], 2)  # 404 + 500
        self.assertAlmostEqual(result['error_rate'], 0.5)
        self.assertIn('200', result['status_distribution'])
        self.assertIn('404', result['status_distribution'])
        self.assertIn('500', result['status_distribution'])
    
    def test_analyze_apache_log(self):
        """测试Apache日志分析"""
        content = '''192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 1000
192.168.1.2 - - [20/Feb/2026:10:01:00 +0800] "GET /page HTTP/1.1" 200 2000
192.168.1.1 - - [20/Feb/2026:10:02:00 +0800] "GET /error HTTP/1.1" 500 512'''
        
        path = self.create_test_file(content)
        result = self.analyzer.analyze_apache_log(path)
        
        self.assertEqual(result['total_requests'], 3)
        self.assertEqual(result['unique_visitors'], 2)
        self.assertEqual(result['total_bandwidth'], 3512)
    
    def test_analyze_error_trend(self):
        """测试错误趋势分析"""
        content = '''2026-02-20 09:00:00 INFO Application started
2026-02-20 10:00:00 ERROR Database connection failed
2026-02-20 10:01:00 ERROR TimeoutException: Request timeout
2026-02-20 10:02:00 INFO Request processed
2026-02-20 11:00:00 ERROR NullPointerException
2026-02-20 11:01:00 ERROR Database connection failed'''
        
        path = self.create_test_file(content)
        result = self.analyzer.analyze_error_trend(path, hours=24)
        
        self.assertEqual(result['total_errors_found'], 4)
        self.assertIn('ERROR', result['error_types'])
        self.assertTrue(len(result['hourly_trend']) > 0)
    
    def test_extract_errors(self):
        """测试错误提取"""
        content = '''2026-02-20 10:00:00 INFO Normal operation
2026-02-20 10:01:00 ERROR Critical failure occurred
2026-02-20 10:02:00 DEBUG Debug message
2026-02-20 10:03:00 FATAL System crash
2026-02-20 10:04:00 INFO Recovery started'''
        
        path = self.create_test_file(content)
        result = self.analyzer.extract_errors(path)
        
        self.assertEqual(result['total_errors'], 2)
        self.assertEqual(result['by_level']['ERROR'], 1)
        self.assertEqual(result['by_level']['FATAL'], 1)
    
    def test_generate_report_json(self):
        """测试JSON报告生成"""
        content = '192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        path = self.create_test_file(content)
        
        report = self.analyzer.generate_report([path], output_format='json')
        data = json.loads(report)
        
        self.assertIn('generated_at', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['detected_format'], 'nginx')
    
    def test_generate_report_markdown(self):
        """测试Markdown报告生成"""
        content = '192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        path = self.create_test_file(content)
        
        report = self.analyzer.generate_report([path], output_format='markdown')
        
        self.assertIn('# 日志分析报告', report)
        self.assertIn('test.log', report)
    
    def test_generate_report_html(self):
        """测试HTML报告生成"""
        content = '192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        path = self.create_test_file(content)
        
        report = self.analyzer.generate_report([path], output_format='html')
        
        self.assertIn('<!DOCTYPE html>', report)
        self.assertIn('<title>日志分析报告</title>', report)
    
    def test_empty_log_file(self):
        """测试空日志文件处理"""
        path = self.create_test_file('')
        result = self.analyzer.analyze_nginx_log(path)
        
        self.assertIn('error', result)
        self.assertIn('未解析到有效日志条目', result['error'])
    
    def test_invalid_log_file(self):
        """测试无效日志文件处理"""
        result = self.analyzer.analyze_nginx_log('/nonexistent/path.log')
        self.assertIn('error', result)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        self.analyzer = LogAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content):
        path = os.path.join(self.temp_dir, 'test.log')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_malformed_lines(self):
        """测试损坏的日志行"""
        content = '''192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"
malformed line without proper format
192.168.1.2 - - [20/Feb/2026:10:01:00 +0800] "GET /api HTTP/1.1" 200 1024 "-" "Mozilla/5.0"'''
        
        path = self.create_test_file(content)
        result = self.analyzer.analyze_nginx_log(path)
        
        # 应该成功解析2行有效日志
        self.assertEqual(result['total_requests'], 2)
        self.assertEqual(result['parse_errors'], 1)
    
    def test_unicode_content(self):
        """测试Unicode内容"""
        content = '192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET /中文路径 HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        path = self.create_test_file(content)
        result = self.analyzer.analyze_nginx_log(path)
        
        self.assertEqual(result['total_requests'], 1)
        self.assertIn('/中文路径', [url for url, _ in result['top_urls']])
    
    def test_large_status_code(self):
        """测试各种HTTP状态码"""
        content = '''192.168.1.1 - - [20/Feb/2026:10:00:00 +0800] "GET /1 HTTP/1.1" 200 512 "-" "Mozilla/5.0"
192.168.1.1 - - [20/Feb/2026:10:01:00 +0800] "GET /2 HTTP/1.1" 301 0 "-" "Mozilla/5.0"
192.168.1.1 - - [20/Feb/2026:10:02:00 +0800] "GET /3 HTTP/1.1" 404 512 "-" "Mozilla/5.0"
192.168.1.1 - - [20/Feb/2026:10:03:00 +0800] "GET /4 HTTP/1.1" 500 512 "-" "Mozilla/5.0"
192.168.1.1 - - [20/Feb/2026:10:04:00 +0800] "GET /5 HTTP/1.1" 502 512 "-" "Mozilla/5.0"'''
        
        path = self.create_test_file(content)
        result = self.analyzer.analyze_nginx_log(path)
        
        self.assertEqual(result['total_requests'], 5)
        self.assertEqual(result['error_requests'], 3)  # 404, 500, 502
        
        status_dist = result['status_distribution']
        self.assertIn('200', status_dist)
        self.assertIn('301', status_dist)
        self.assertIn('404', status_dist)
        self.assertIn('500', status_dist)
        self.assertIn('502', status_dist)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLogParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLogAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
