#!/usr/bin/env python3
"""
Error Tracking Skill 测试套件
"""

import unittest
import tempfile
import os
from datetime import datetime
from main import StackTraceParser, ErrorTracker, ErrorEntry, StackFrame


class TestStackTraceParser(unittest.TestCase):
    """测试堆栈解析器"""
    
    def setUp(self):
        self.parser = StackTraceParser()
    
    def test_parse_python_traceback(self):
        """测试Python Traceback解析"""
        text = '''Traceback (most recent call last):
  File "/app/main.py", line 42, in process_data
    result = calculate(data)
  File "/app/utils.py", line 15, in calculate
    return x / y
ZeroDivisionError: division by zero'''
        
        error = self.parser.parse_python_traceback(text)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.error_type, "ZeroDivisionError")
        self.assertEqual(error.message, "division by zero")
        self.assertEqual(len(error.stack_trace), 2)
        self.assertEqual(error.stack_trace[0].file, "/app/main.py")
        self.assertEqual(error.stack_trace[0].line, 42)
        self.assertEqual(error.stack_trace[0].function, "process_data")
    
    def test_parse_java_stack_trace(self):
        """测试Java Stack Trace解析"""
        text = '''java.lang.NullPointerException: Cannot invoke method
    at com.example.Service.process(Service.java:25)
    at com.example.Controller.handle(Controller.java:40)
    at com.example.Main.main(Main.java:15)'''
        
        error = self.parser.parse_java_stack_trace(text)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.error_type, "java.lang.NullPointerException")
        self.assertEqual(error.message, "Cannot invoke method")
        self.assertEqual(len(error.stack_trace), 3)
        self.assertEqual(error.stack_trace[0].function, "process")
        self.assertEqual(error.stack_trace[0].module, "com.example.Service")
    
    def test_parse_javascript_error(self):
        """测试JavaScript Error解析"""
        text = '''TypeError: Cannot read property 'foo' of undefined
    at Object.myFunction (/app/script.js:10:15)
    at processTicksAndRejections (internal/process/task_queues.js:97:5)'''
        
        error = self.parser.parse_javascript_error(text)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.error_type, "TypeError")
        self.assertEqual(error.message, "Cannot read property 'foo' of undefined")
        self.assertEqual(len(error.stack_trace), 2)
    
    def test_parse_go_panic(self):
        """测试Go Panic解析"""
        text = '''panic: runtime error: index out of range [5] with length 3

goroutine 1 [running]:
main.processArray(0xc0000b4008, 0x3, 0x3, 0x5)
    /app/main.go:15 +0x8f
main.main()
    /app/main.go:10 +0x4d'''
        
        error = self.parser.parse_go_panic(text)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.error_type, "panic")
        self.assertIn("index out of range", error.message)
        self.assertTrue(len(error.stack_trace) > 0)
    
    def test_parse_generic_error(self):
        """测试通用错误解析"""
        text = '''2024-01-01 10:30:00 ERROR DatabaseConnectionException: Failed to connect to database
    at connection pool'''
        
        error = self.parser.parse_generic_error(text)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.error_type, "DatabaseConnectionException")
        self.assertIn("Failed to connect", error.message)
    
    def test_parse_timestamp(self):
        """测试时间戳解析"""
        text1 = '2024-01-15 10:30:45 ERROR something'
        ts1 = self.parser.parse_timestamp(text1)
        self.assertIsNotNone(ts1)
        self.assertEqual(ts1.year, 2024)
        self.assertEqual(ts1.month, 1)
        self.assertEqual(ts1.day, 15)
        
        text2 = 'Jan 15 10:30:45 ERROR something'
        ts2 = self.parser.parse_timestamp(text2)
        self.assertIsNotNone(ts2)
    
    def test_detect_format_python(self):
        """测试Python格式检测"""
        sample = 'Traceback (most recent call last):\n  File "/app.py"'
        fmt = self.parser.detect_format(sample)
        self.assertEqual(fmt, 'python')
    
    def test_detect_format_java(self):
        """测试Java格式检测"""
        sample = 'java.lang.Exception: message\n    at Class.method(File.java:10)'
        fmt = self.parser.detect_format(sample)
        self.assertEqual(fmt, 'java')
    
    def test_detect_format_go(self):
        """测试Go格式检测"""
        sample = 'panic: runtime error\n\ngoroutine 1'
        fmt = self.parser.detect_format(sample)
        self.assertEqual(fmt, 'go')


class TestErrorTracker(unittest.TestCase):
    """测试错误追踪器"""
    
    def setUp(self):
        self.tracker = ErrorTracker()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content, filename='test.log'):
        """创建测试日志文件"""
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_analyze_file_python(self):
        """测试分析Python日志文件"""
        content = '''2024-01-01 10:00:00 INFO Starting

Traceback (most recent call last):
  File "/app/main.py", line 10, in <module>
    main()
ValueError: invalid input

2024-01-01 10:01:00 INFO Processing

Traceback (most recent call last):
  File "/app/main.py", line 20, in process
    result = 1/0
ZeroDivisionError: division by zero'''
        
        path = self.create_test_file(content)
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 2)
        self.assertEqual(result['unique_types'], 2)
        self.assertIn('ValueError', result['by_type'])
        self.assertIn('ZeroDivisionError', result['by_type'])
    
    def test_analyze_file_java(self):
        """测试分析Java日志文件"""
        content = '''2024-01-01 10:00:00 ERROR java.lang.NullPointerException: null object
    at com.example.Service.process(Service.java:25)
    at com.example.Main.main(Main.java:10)

2024-01-01 10:01:00 ERROR java.lang.IllegalArgumentException: bad argument
    at com.example.Validator.validate(Validator.java:15)'''
        
        path = self.create_test_file(content)
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 2)
        self.assertIn('java.lang.NullPointerException', result['by_type'])
    
    def test_aggregate_by_type(self):
        """测试按类型聚合"""
        content = '''Traceback (most recent call last):
  File "/app.py", line 10
ValueError: error 1

Traceback (most recent call last):
  File "/app.py", line 20
ValueError: error 2

Traceback (most recent call last):
  File "/app.py", line 30
TypeError: error 3'''
        
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        aggregated = self.tracker.aggregate_by_type()
        
        self.assertEqual(len(aggregated['ValueError']), 2)
        self.assertEqual(len(aggregated['TypeError']), 1)
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        error1 = ErrorEntry(
            error_type="ValueError",
            stack_trace=[
                StackFrame(file="/app.py", line=10, function="func1"),
                StackFrame(file="/app.py", line=20, function="func2")
            ]
        )
        
        error2 = ErrorEntry(
            error_type="ValueError",
            stack_trace=[
                StackFrame(file="/app.py", line=10, function="func1"),
                StackFrame(file="/app.py", line=20, function="func2")
            ]
        )
        
        error3 = ErrorEntry(
            error_type="TypeError",
            stack_trace=[
                StackFrame(file="/other.py", line=5, function="other_func")
            ]
        )
        
        similarity_same = self.tracker._calculate_similarity(error1, error2)
        similarity_diff = self.tracker._calculate_similarity(error1, error3)
        
        self.assertGreater(similarity_same, 0.9)
        self.assertLess(similarity_diff, 0.5)
    
    def test_aggregate_by_stack_similarity(self):
        """测试按堆栈相似度聚合"""
        content = '''Traceback (most recent call last):
  File "/app.py", line 10, in func_a
  File "/app.py", line 20, in func_b
ValueError: error 1

Traceback (most recent call last):
  File "/app.py", line 10, in func_a
  File "/app.py", line 20, in func_b
ValueError: error 2

Traceback (most recent call last):
  File "/other.py", line 5, in other_func
TypeError: different error'''
        
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        groups = self.tracker.aggregate_by_stack_similarity(threshold=0.7)
        
        # 应该有两个组：ValueError组和TypeError组
        self.assertGreaterEqual(len(groups), 1)
        
        # ValueError应该在一起（2个）
        value_error_group = next(
            (g for g in groups if g['representative']['error_type'] == 'ValueError'),
            None
        )
        if value_error_group:
            self.assertEqual(value_error_group['count'], 2)
    
    def test_analyze_trend(self):
        """测试趋势分析"""
        # 创建带时间戳的错误
        content = '''2024-01-01 10:00:00 ERROR Error 1

2024-01-01 10:30:00 ERROR Error 2

2024-01-01 11:00:00 ERROR Error 3'''
        
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        trend = self.tracker.analyze_trend(hours=24, interval='1h')
        
        self.assertEqual(trend['total_errors'], 3)
        self.assertIn('timeline', trend)
        self.assertIn('average_per_interval', trend)
    
    def test_get_top_errors(self):
        """测试获取Top错误"""
        content = '''ERROR TypeA: error
ERROR TypeA: error
ERROR TypeA: error
ERROR TypeB: error
ERROR TypeB: error
ERROR TypeC: error'''
        
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        top = self.tracker.get_top_errors(n=3)
        
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0]['type'], 'TypeA')
        self.assertEqual(top[0]['count'], 3)
        self.assertEqual(top[1]['type'], 'TypeB')
        self.assertEqual(top[1]['count'], 2)
    
    def test_generate_report_json(self):
        """测试生成JSON报告"""
        content = 'ERROR TestError: test message'
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        report = self.tracker.generate_report(format='json')
        data = json.loads(report)
        
        self.assertIn('generated_at', data)
        self.assertIn('summary', data)
        self.assertEqual(data['summary']['total_errors'], 1)
    
    def test_generate_report_markdown(self):
        """测试生成Markdown报告"""
        content = 'ERROR TestError: test message'
        path = self.create_test_file(content)
        self.tracker.analyze_file(path)
        
        report = self.tracker.generate_report(format='markdown')
        
        self.assertIn('# 错误追踪报告', report)
        self.assertIn('TestError', report)
    
    def test_get_stack_signature(self):
        """测试获取堆栈签名"""
        error = ErrorEntry(
            error_type="TestError",
            stack_trace=[
                StackFrame(file="/app.py", line=10, function="func_a", module="app"),
                StackFrame(file="/app.py", line=20, function="func_b", module="app"),
            ]
        )
        
        signature = error.get_stack_signature()
        
        self.assertIn("app.func_a", signature)
        self.assertIn("app.func_b", signature)


class TestErrorEntry(unittest.TestCase):
    """测试错误条目"""
    
    def test_error_entry_creation(self):
        """测试错误条目创建"""
        entry = ErrorEntry(
            error_type="ValueError",
            message="test message",
            raw_text="raw error text"
        )
        
        self.assertEqual(entry.error_type, "ValueError")
        self.assertEqual(entry.message, "test message")
        self.assertIsNotNone(entry.hash_id)
    
    def test_error_entry_to_dict(self):
        """测试转换为字典"""
        entry = ErrorEntry(
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            error_type="TestError",
            message="test",
            stack_trace=[StackFrame(file="/app.py", line=10, function="test")]
        )
        
        data = entry.to_dict()
        
        self.assertEqual(data['error_type'], "TestError")
        self.assertEqual(data['message'], "test")
        self.assertEqual(len(data['stack_trace']), 1)


class TestStackFrame(unittest.TestCase):
    """测试堆栈帧"""
    
    def test_stack_frame_creation(self):
        """测试堆栈帧创建"""
        frame = StackFrame(
            file="/app/main.py",
            line=42,
            function="process",
            code="x = y + z",
            module="app"
        )
        
        self.assertEqual(frame.file, "/app/main.py")
        self.assertEqual(frame.line, 42)
        self.assertEqual(frame.function, "process")
    
    def test_stack_frame_to_dict(self):
        """测试转换为字典"""
        frame = StackFrame(file="/app.py", line=10, function="test")
        data = frame.to_dict()
        
        self.assertEqual(data['file'], "/app.py")
        self.assertEqual(data['line'], 10)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        self.tracker = ErrorTracker()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content):
        path = os.path.join(self.temp_dir, 'test.log')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_empty_file(self):
        """测试空文件"""
        path = self.create_test_file('')
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 0)
    
    def test_no_errors(self):
        """测试无错误的文件"""
        path = self.create_test_file('INFO: Normal operation\nDEBUG: Debug message')
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 0)
    
    def test_unicode_content(self):
        """测试Unicode内容"""
        content = 'ERROR 中文错误: 错误消息'
        path = self.create_test_file(content)
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 1)
    
    def test_multiline_error_message(self):
        """测试多行错误消息"""
        content = '''ERROR Exception: This is a
multiline error message
that spans several lines'''
        path = self.create_test_file(content)
        result = self.tracker.analyze_file(path)
        
        self.assertEqual(result['total_errors'], 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestStackTraceParser))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorEntry))
    suite.addTests(loader.loadTestsFromTestCase(TestStackFrame))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
