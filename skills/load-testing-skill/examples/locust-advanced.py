"""
Locust高级使用示例

展示Locust的高级功能：自定义形状、事件处理、数据驱动等
"""

from locust import HttpUser, task, between, events, LoadTestShape
from locust.runners import MasterRunner
import json
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# 自定义负载形状
# ============================================

class StepLoadShape(LoadTestShape):
    """阶梯式负载形状"""
    
    step_time = 30  # 每步持续时间（秒）
    step_load = 10  # 每步增加用户数
    spawn_rate = 10  # 每秒生成用户数
    time_limit = 600  # 总时间限制（秒）
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < self.time_limit:
            current_step = run_time // self.step_time + 1
            user_count = current_step * self.step_load
            return (user_count, self.spawn_rate)
        
        return None


class SpikeLoadShape(LoadTestShape):
    """峰值负载形状"""
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < 60:
            # 正常负载
            return (10, 2)
        elif run_time < 120:
            # 峰值
            return (100, 20)
        elif run_time < 180:
            # 恢复正常
            return (10, 2)
        else:
            return None


class DoubleWaveLoadShape(LoadTestShape):
    """双波负载形状"""
    
    def tick(self):
        run_time = self.get_run_time()
        
        # 两个波峰
        if run_time < 300:
            # 第一波
            user_count = 50 + int(50 * (run_time % 150) / 150)
            return (user_count, 10)
        elif run_time < 600:
            # 第二波
            user_count = 50 + int(50 * ((run_time - 300) % 150) / 150)
            return (user_count, 10)
        else:
            return None


# ============================================
# 数据驱动测试
# ============================================

class TestData:
    """测试数据管理"""
    
    def __init__(self):
        self.users = [
            {"username": f"user_{i}", "password": f"pass_{i}"}
            for i in range(100)
        ]
        self.products = [
            {"id": i, "name": f"Product {i}", "price": random.randint(10, 1000)}
            for i in range(50)
        ]
    
    def get_random_user(self):
        return random.choice(self.users)
    
    def get_random_product(self):
        return random.choice(self.products)


# ============================================
# 用户类定义
# ============================================

class WebsiteUser(HttpUser):
    """网站用户模拟"""
    
    wait_time = between(1, 5)
    host = "https://api.example.com"
    
    def __init__(self, environment):
        super().__init__(environment)
        self.test_data = TestData()
        self.auth_token = None
    
    def on_start(self):
        """用户启动时执行"""
        user = self.test_data.get_random_user()
        
        with self.client.post("/auth/login", json={
            "username": user["username"],
            "password": user["password"]
        }, catch_response=True) as response:
            if response.status_code == 200:
                self.auth_token = response.json().get("token")
                response.success()
            else:
                response.failure("Login failed")
    
    def on_stop(self):
        """用户停止时执行"""
        if self.auth_token:
            self.client.post("/auth/logout", headers={
                "Authorization": f"Bearer {self.auth_token}"
            })
    
    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def browse_products(self):
        """浏览商品"""
        self.client.get("/products", headers=self.get_headers())
    
    @task(5)
    def view_product_detail(self):
        """查看商品详情"""
        product = self.test_data.get_random_product()
        self.client.get(f"/products/{product['id']}", headers=self.get_headers())
    
    @task(3)
    def add_to_cart(self):
        """添加购物车"""
        product = self.test_data.get_random_product()
        self.client.post("/cart/items", json={
            "product_id": product["id"],
            "quantity": random.randint(1, 5)
        }, headers=self.get_headers())
    
    @task(2)
    def checkout(self):
        """结账"""
        self.client.post("/orders", json={
            "payment_method": random.choice(["credit_card", "paypal", "alipay"]),
            "shipping_address": "123 Test St"
        }, headers=self.get_headers())
    
    @task(1)
    def search(self):
        """搜索"""
        keywords = ["laptop", "phone", "headphones", "mouse", "keyboard"]
        self.client.get(f"/search?q={random.choice(keywords)}", headers=self.get_headers())


class MobileUser(HttpUser):
    """移动端用户"""
    
    wait_time = between(2, 8)
    weight = 2  # 权重为网站用户的一半
    
    def __init__(self, environment):
        super().__init__(environment)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
            "Accept": "application/json"
        }
    
    @task(1)
    def mobile_api_call(self):
        """移动端API调用"""
        self.client.get("/api/v2/mobile/home", headers=self.headers)


# ============================================
# 事件处理器
# ============================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始事件"""
    logger.info("Load test starting...")
    
    if isinstance(environment.runner, MasterRunner):
        logger.info(f"Master node: {len(environment.runner.clients)} workers connected")
    
    # 预热环境
    logger.info("Warming up the system...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试停止事件"""
    logger.info("Load test stopping...")
    
    # 生成统计报告
    stats = environment.runner.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Failed requests: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """请求事件"""
    # 记录慢请求
    if response_time > 1000:
        logger.warning(f"Slow request: {name} took {response_time}ms")
    
    # 记录错误
    if exception:
        logger.error(f"Request failed: {name} - {exception}")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """退出事件"""
    logger.info("Locust is quitting...")
    
    # 保存结果到文件
    stats = environment.runner.stats
    report = {
        "timestamp": str(datetime.now()),
        "total_requests": stats.total.num_requests,
        "failed_requests": stats.total.num_failures,
        "avg_response_time": stats.total.avg_response_time,
        "percentiles": {
            "p50": stats.total.get_response_time_percentile(0.5),
            "p95": stats.total.get_response_time_percentile(0.95),
            "p99": stats.total.get_response_time_percentile(0.99)
        }
    }
    
    with open("locust_report.json", "w") as f:
        json.dump(report, f, indent=2)


# ============================================
# 自定义命令
# ============================================

from locust.argument_parser import LocustArgumentParser

class CustomParser(LocustArgumentParser):
    """自定义参数解析器"""
    
    def __init__(self):
        super().__init__()
        self.add_argument(
            "--custom-arg",
            type=str,
            default="default",
            help="Custom argument for testing"
        )


# ============================================
# 使用说明
# ============================================

"""
运行Locust:

1. 单节点模式:
   locust -f locustfile.py --host=https://api.example.com

2. 分布式模式 - Master:
   locust -f locustfile.py --master --master-bind-host=0.0.0.0 --master-bind-port=5557

3. 分布式模式 - Worker:
   locust -f locustfile.py --worker --master-host=localhost --master-port=5557

4. 无Web UI模式:
   locust -f locustfile.py --headless -u 100 -r 10 -t 5m --csv=results

5. 使用自定义负载形状:
   locust -f locustfile.py --class-picker WebsiteUser,StepLoadShape

6. 指定标签运行:
   locust -f locustfile.py --tags browse checkout
"""

from datetime import datetime

if __name__ == "__main__":
    # 直接运行测试（用于调试）
    import os
    os.system("locust -f locustfile.py --host=https://httpbin.org")
