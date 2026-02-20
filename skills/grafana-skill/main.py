#!/usr/bin/env python3
"""
Grafana Skill - Grafana仪表板管理工具
支持Dashboard创建、数据源配置、面板管理

关键词触发：Grafana、仪表板、dashboard、面板、panel、数据源、datasource、
可视化、visualization、图表、chart
"""

import re
import json
import argparse
import base64
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode, quote
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DashboardInfo:
    """仪表板信息数据类"""
    id: int
    uid: str
    title: str
    url: str
    type: str
    tags: List[str]
    folder_id: int
    folder_title: str


class GrafanaClient:
    """Grafana API客户端"""
    
    # 支持的数据源类型
    DATA_SOURCE_TYPES = {
        'prometheus': {'name': 'Prometheus', 'port': 9090},
        'influxdb': {'name': 'InfluxDB', 'port': 8086},
        'elasticsearch': {'name': 'Elasticsearch', 'port': 9200},
        'mysql': {'name': 'MySQL', 'port': 3306},
        'postgres': {'name': 'PostgreSQL', 'port': 5432},
        'loki': {'name': 'Loki', 'port': 3100},
        'jaeger': {'name': 'Jaeger', 'port': 16686},
        'zipkin': {'name': 'Zipkin', 'port': 9411},
        'cloudwatch': {'name': 'CloudWatch'},
        'azuremonitor': {'name': 'Azure Monitor'},
        'stackdriver': {'name': 'Google Cloud Monitoring'},
    }
    
    # 面板类型映射
    PANEL_TYPES = {
        'timeseries': 'timeseries',
        'graph': 'graph',
        'gauge': 'gauge',
        'stat': 'stat',
        'table': 'table',
        'heatmap': 'heatmap',
        'piechart': 'piechart',
        'bargauge': 'bargauge',
        'logs': 'logs',
        'nodeGraph': 'nodeGraph',
    }
    
    def __init__(self, url: str, api_key: Optional[str] = None,
                 basic_auth: Optional[Tuple[str, str]] = None, timeout: int = 30):
        """
        初始化Grafana客户端
        
        Args:
            url: Grafana服务器URL
            api_key: API密钥（可选）
            basic_auth: (用户名, 密码) 元组（可选）
            timeout: 请求超时时间
        """
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
        elif basic_auth:
            auth_str = base64.b64encode(f'{basic_auth[0]}:{basic_auth[1]}'.encode()).decode()
            self.headers['Authorization'] = f'Basic {auth_str}'
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Dict:
        """发送HTTP请求"""
        url = f"{self.url}/api/{endpoint}"
        if params:
            query_string = urlencode(params, safe=':[]{}"\\/=,')
            url = f"{url}?{query_string}"
        
        request_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(
            url, data=request_data, headers=self.headers, method=method
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                if response_data:
                    return json.loads(response_data)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('message', error_body)
            except:
                error_msg = error_body or str(e)
            raise Exception(f"HTTP Error {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection failed: {e.reason}")
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET请求"""
        return self._request('GET', endpoint, params=params)
    
    def _post(self, endpoint: str, data: Dict) -> Dict:
        """POST请求"""
        return self._request('POST', endpoint, data=data)
    
    def _put(self, endpoint: str, data: Dict) -> Dict:
        """PUT请求"""
        return self._request('PUT', endpoint, data=data)
    
    def _delete(self, endpoint: str) -> Dict:
        """DELETE请求"""
        return self._request('DELETE', endpoint)
    
    def health_check(self) -> Dict:
        """检查Grafana健康状态"""
        try:
            result = self._get('health')
            return {
                "status": "healthy",
                "version": result.get('version', 'unknown'),
                "commit": result.get('commit', 'unknown'),
                "database": result.get('database', 'unknown')
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def get_frontend_settings(self) -> Dict:
        """获取前端设置（包含数据源信息）"""
        return self._get('frontend/settings')
    
    def list_dashboards(self, folder_ids: Optional[List[int]] = None,
                       query: Optional[str] = None, tag: Optional[str] = None,
                       limit: int = 1000) -> List[Dict]:
        """
        列出仪表板
        
        Args:
            folder_ids: 文件夹ID列表（可选）
            query: 搜索查询（可选）
            tag: 标签筛选（可选）
            limit: 返回数量限制
        
        Returns:
            仪表板列表
        """
        params = {'type': 'dash-db', 'limit': limit}
        if folder_ids:
            params['folderIds'] = ','.join(map(str, folder_ids))
        if query:
            params['query'] = query
        if tag:
            params['tag'] = tag
        
        return self._get('search', params)
    
    def get_dashboard(self, uid: str) -> Dict:
        """
        获取仪表板详情
        
        Args:
            uid: 仪表板UID
        
        Returns:
            仪表板完整配置
        """
        return self._get(f'dashboards/uid/{uid}')
    
    def get_dashboard_by_id(self, dashboard_id: int) -> Dict:
        """通过ID获取仪表板（已废弃，建议使用UID）"""
        return self._get(f'dashboards/id/{dashboard_id}')
    
    def create_dashboard(self, title: str, panels: Optional[List[Dict]] = None,
                        folder_id: int = 0, tags: Optional[List[str]] = None,
                        timezone: str = 'browser', **options) -> Dict:
        """
        创建新仪表板
        
        Args:
            title: 仪表板标题
            panels: 面板配置列表
            folder_id: 文件夹ID
            tags: 标签列表
            timezone: 时区设置
            **options: 其他配置选项
        
        Returns:
            创建结果
        """
        dashboard = {
            "id": None,
            "uid": None,
            "title": title,
            "tags": tags or [],
            "timezone": timezone,
            "schemaVersion": 36,
            "refresh": options.get('refresh', '30s'),
            "time": options.get('time', {"from": "now-6h", "to": "now"}),
            "templating": {"list": options.get('variables', [])},
            "annotations": {"list": options.get('annotations', [])},
            "panels": panels or [],
        }
        
        data = {
            "dashboard": dashboard,
            "folderId": folder_id,
            "message": options.get('message', 'Created by Grafana Skill'),
            "overwrite": False
        }
        
        logger.info(f"创建仪表板: {title}")
        return self._post('dashboards/db', data)
    
    def update_dashboard(self, dashboard: Dict, folder_id: Optional[int] = None,
                        message: str = 'Updated by Grafana Skill',
                        overwrite: bool = True) -> Dict:
        """
        更新仪表板
        
        Args:
            dashboard: 仪表板配置
            folder_id: 文件夹ID（可选）
            message: 更新消息
            overwrite: 是否覆盖
        
        Returns:
            更新结果
        """
        data = {
            "dashboard": dashboard,
            "message": message,
            "overwrite": overwrite
        }
        if folder_id is not None:
            data["folderId"] = folder_id
        
        logger.info(f"更新仪表板: {dashboard.get('title', 'Unknown')}")
        return self._post('dashboards/db', data)
    
    def delete_dashboard(self, uid: str) -> Dict:
        """
        删除仪表板
        
        Args:
            uid: 仪表板UID
        
        Returns:
            删除结果
        """
        logger.info(f"删除仪表板: {uid}")
        return self._delete(f'dashboards/uid/{uid}')
    
    def export_dashboard(self, uid: str, pretty: bool = True) -> Dict:
        """
        导出仪表板
        
        Args:
            uid: 仪表板UID
            pretty: 格式化输出
        
        Returns:
            仪表板JSON
        """
        dashboard = self.get_dashboard(uid)
        export_data = dashboard.get('dashboard', {})
        
        # 清理不必要的字段
        export_data.pop('id', None)
        export_data.pop('uid', None)
        export_data.pop('version', None)
        
        return export_data
    
    def import_dashboard(self, dashboard_json: Dict, folder_id: int = 0,
                        folder_uid: Optional[str] = None,
                        overwrite: bool = True) -> Dict:
        """
        导入仪表板
        
        Args:
            dashboard_json: 仪表板配置
            folder_id: 文件夹ID
            folder_uid: 文件夹UID
            overwrite: 是否覆盖
        
        Returns:
            导入结果
        """
        data = {
            "dashboard": dashboard_json,
            "folderId": folder_id,
            "overwrite": overwrite
        }
        if folder_uid:
            data["folderUid"] = folder_uid
        
        title = dashboard_json.get('title', 'Unknown')
        logger.info(f"导入仪表板: {title}")
        return self._post('dashboards/db', data)
    
    def list_data_sources(self) -> List[Dict]:
        """列出所有数据源"""
        return self._get('datasources')
    
    def get_data_source(self, id_or_name: Union[int, str]) -> Dict:
        """
        获取数据源详情
        
        Args:
            id_or_name: 数据源ID或名称
        """
        if isinstance(id_or_name, int):
            return self._get(f'datasources/{id_or_name}')
        else:
            return self._get(f'datasources/name/{quote(id_or_name, safe="")}')
    
    def get_data_source_id_by_name(self, name: str) -> int:
        """通过名称获取数据源ID"""
        ds = self.get_data_source(name)
        return ds.get('id')
    
    def create_data_source(self, name: str, type: str, url: str,
                          database: Optional[str] = None,
                          user: Optional[str] = None,
                          password: Optional[str] = None,
                          json_data: Optional[Dict] = None,
                          secure_json_data: Optional[Dict] = None,
                          **options) -> Dict:
        """
        创建数据源
        
        Args:
            name: 数据源名称
            type: 数据源类型
            url: 连接URL
            database: 数据库名称（可选）
            user: 用户名（可选）
            password: 密码（可选）
            json_data: 额外配置（可选）
            secure_json_data: 安全配置（可选）
        
        Returns:
            创建结果
        """
        data = {
            "name": name,
            "type": type,
            "url": url,
            "access": options.get('access', 'proxy'),
            "isDefault": options.get('is_default', False),
        }
        
        if database:
            data["database"] = database
        if user:
            data["user"] = user
        if password:
            data["password"] = password
        if json_data:
            data["jsonData"] = json_data
        if secure_json_data:
            data["secureJsonData"] = secure_json_data
        
        logger.info(f"创建数据源: {name} (类型: {type})")
        return self._post('datasources', data)
    
    def update_data_source(self, id: int, **kwargs) -> Dict:
        """更新数据源"""
        return self._put(f'datasources/{id}', kwargs)
    
    def delete_data_source(self, id: int) -> Dict:
        """删除数据源"""
        logger.info(f"删除数据源: {id}")
        return self._delete(f'datasources/{id}')
    
    def list_folders(self) -> List[Dict]:
        """列出所有文件夹"""
        return self._get('folders')
    
    def get_folder(self, uid: str) -> Dict:
        """获取文件夹详情"""
        return self._get(f'folders/{uid}')
    
    def get_folder_by_id(self, folder_id: int) -> Dict:
        """通过ID获取文件夹"""
        return self._get(f'folders/id/{folder_id}')
    
    def create_folder(self, title: str, uid: Optional[str] = None) -> Dict:
        """
        创建文件夹
        
        Args:
            title: 文件夹标题
            uid: 自定义UID（可选）
        """
        data = {"title": title}
        if uid:
            data["uid"] = uid
        
        logger.info(f"创建文件夹: {title}")
        return self._post('folders', data)
    
    def update_folder(self, uid: str, title: str, version: int = 0,
                     overwrite: bool = False) -> Dict:
        """更新文件夹"""
        data = {"title": title, "version": version, "overwrite": overwrite}
        return self._put(f'folders/{uid}', data)
    
    def delete_folder(self, uid: str) -> Dict:
        """删除文件夹"""
        logger.info(f"删除文件夹: {uid}")
        return self._delete(f'folders/{uid}')
    
    def search(self, query: str, type: Optional[str] = None,
               folder_ids: Optional[List[int]] = None,
               limit: int = 1000) -> List[Dict]:
        """
        搜索资源
        
        Args:
            query: 搜索关键词
            type: 资源类型（dash-folder/dash-db）
            folder_ids: 文件夹ID列表
            limit: 返回数量限制
        """
        params = {'query': query, 'limit': limit}
        if type:
            params['type'] = type
        if folder_ids:
            params['folderIds'] = ','.join(map(str, folder_ids))
        
        return self._get('search', params)
    
    def get_dashboard_permissions(self, uid: str) -> List[Dict]:
        """获取仪表板权限"""
        return self._get(f'dashboards/uid/{uid}/permissions')
    
    def update_dashboard_permissions(self, uid: str, items: List[Dict]) -> Dict:
        """更新仪表板权限"""
        return self._post(f'dashboards/uid/{uid}/permissions', {"items": items})
    
    def create_panel(self, title: str, panel_type: str = 'timeseries',
                    targets: Optional[List[Dict]] = None,
                    grid_pos: Optional[Dict] = None,
                    **options) -> Dict:
        """
        创建面板配置
        
        Args:
            title: 面板标题
            panel_type: 面板类型
            targets: 查询目标列表
            grid_pos: 网格位置 {'x': 0, 'y': 0, 'w': 12, 'h': 8}
            **options: 其他配置
        
        Returns:
            面板配置字典
        """
        panel = {
            "id": options.get('id', 0),
            "title": title,
            "type": self.PANEL_TYPES.get(panel_type, panel_type),
            "targets": targets or [],
            "gridPos": grid_pos or {"h": 8, "w": 12, "x": 0, "y": 0},
            "datasource": options.get('datasource', None),
            "fieldConfig": {
                "defaults": {
                    "custom": {}
                },
                "overrides": []
            },
            "options": {},
            "pluginVersion": "9.0.0"
        }
        
        # 添加字段配置
        if 'unit' in options:
            panel["fieldConfig"]["defaults"]["unit"] = options['unit']
        if 'min' in options:
            panel["fieldConfig"]["defaults"]["min"] = options['min']
        if 'max' in options:
            panel["fieldConfig"]["defaults"]["max"] = options['max']
        if 'thresholds' in options:
            panel["fieldConfig"]["defaults"]["thresholds"] = options['thresholds']
        if 'color' in options:
            panel["fieldConfig"]["defaults"]["color"] = options['color']
        
        # 添加自定义选项
        if panel_type == 'timeseries':
            panel["options"] = {
                "legend": {"displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "single"}
            }
        elif panel_type == 'gauge':
            panel["options"] = {
                "showThresholdLabels": True,
                "showThresholdMarkers": True
            }
        elif panel_type == 'stat':
            panel["options"] = {
                "graphMode": "area",
                "colorMode": "value"
            }
        
        return panel
    
    def clone_dashboard(self, source_uid: str, new_title: Optional[str] = None,
                       folder_id: int = 0) -> Dict:
        """
        克隆仪表板
        
        Args:
            source_uid: 源仪表板UID
            new_title: 新标题（可选）
            folder_id: 目标文件夹ID
        
        Returns:
            克隆结果
        """
        source = self.get_dashboard(source_uid)
        dashboard = source['dashboard']
        
        # 重置ID和UID
        dashboard['id'] = None
        dashboard['uid'] = None
        
        if new_title:
            dashboard['title'] = new_title
        else:
            dashboard['title'] = f"Copy of {dashboard['title']}"
        
        return self.create_dashboard(
            title=dashboard['title'],
            panels=dashboard.get('panels', []),
            folder_id=folder_id,
            tags=dashboard.get('tags', []),
            refresh=dashboard.get('refresh'),
            time=dashboard.get('time')
        )
    
    def generate_report(self, output_format: str = 'json') -> str:
        """
        生成Grafana资源报告
        
        Args:
            output_format: 输出格式（json/markdown）
        
        Returns:
            报告内容
        """
        dashboards = self.list_dashboards()
        folders = self.list_folders()
        data_sources = self.list_data_sources()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "grafana_url": self.url,
            "summary": {
                "total_dashboards": len(dashboards),
                "total_folders": len(folders),
                "total_data_sources": len(data_sources)
            },
            "folders": folders,
            "data_sources": [{"id": ds['id'], "name": ds['name'], "type": ds['type']} 
                           for ds in data_sources],
            "dashboards": []
        }
        
        for db_summary in dashboards:
            try:
                db = self.get_dashboard(db_summary['uid'])
                info = {
                    "title": db['dashboard']['title'],
                    "uid": db['dashboard']['uid'],
                    "version": db['dashboard'].get('version', 1),
                    "panels": len(db['dashboard'].get('panels', [])),
                    "folder": db['meta'].get('folderTitle', 'General'),
                    "tags": db['dashboard'].get('tags', []),
                    "updated": db['meta'].get('updated', 'Unknown')
                }
                report["dashboards"].append(info)
            except Exception as e:
                logger.warning(f"Failed to get dashboard {db_summary['uid']}: {e}")
        
        if output_format == 'json':
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            return self._format_markdown_report(report)
        else:
            return str(report)
    
    def _format_markdown_report(self, report: Dict) -> str:
        """生成Markdown格式报告"""
        lines = [
            "# Grafana 资源报告",
            f"\n生成时间: {report['generated_at']}",
            f"Grafana地址: {report['grafana_url']}\n",
            "## 摘要\n",
            f"- 仪表板数量: {report['summary']['total_dashboards']}",
            f"- 文件夹数量: {report['summary']['total_folders']}",
            f"- 数据源数量: {report['summary']['total_data_sources']}\n",
            "## 数据源\n",
            "| ID | 名称 | 类型 |",
            "|----|------|------|"
        ]
        
        for ds in report['data_sources']:
            lines.append(f"| {ds['id']} | {ds['name']} | {ds['type']} |")
        
        lines.extend(["\n## 仪表板\n", "| 标题 | 文件夹 | 面板数 | 标签 |", "|------|--------|--------|------|"])
        
        for db in report['dashboards']:
            tags = ', '.join(db['tags']) if db['tags'] else '-'
            lines.append(f"| {db['title']} | {db['folder']} | {db['panels']} | {tags} |")
        
        return '\n'.join(lines)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Grafana仪表板管理工具')
    parser.add_argument('--url', default='http://localhost:3000',
                       help='Grafana服务器URL')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--user', help='用户名（Basic Auth）')
    parser.add_argument('--password', help='密码（Basic Auth）')
    parser.add_argument('--timeout', type=int, default=30, help='超时时间')
    parser.add_argument('--output', '-o', help='输出文件')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list命令
    subparsers.add_parser('list', help='列出仪表板')
    
    # create命令
    create_parser = subparsers.add_parser('create', help='创建仪表板')
    create_parser.add_argument('--title', required=True, help='仪表板标题')
    create_parser.add_argument('--folder', type=int, default=0, help='文件夹ID')
    
    # get命令
    get_parser = subparsers.add_parser('get', help='获取仪表板')
    get_parser.add_argument('--uid', required=True, help='仪表板UID')
    
    # delete命令
    delete_parser = subparsers.add_parser('delete', help='删除仪表板')
    delete_parser.add_argument('--uid', required=True, help='仪表板UID')
    
    # export命令
    export_parser = subparsers.add_parser('export', help='导出仪表板')
    export_parser.add_argument('--uid', required=True, help='仪表板UID')
    export_parser.add_argument('--pretty', action='store_true', default=True, help='格式化输出')
    
    # import命令
    import_parser = subparsers.add_parser('import', help='导入仪表板')
    import_parser.add_argument('--file', required=True, help='JSON文件路径')
    import_parser.add_argument('--folder', type=int, default=0, help='文件夹ID')
    
    # datasources命令
    subparsers.add_parser('datasources', help='列出数据源')
    
    # folders命令
    subparsers.add_parser('folders', help='列出文件夹')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--format', choices=['json', 'markdown'],
                              default='json', help='报告格式')
    
    # health命令
    subparsers.add_parser('health', help='检查健康状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化客户端
    auth = None
    if args.api_key:
        auth = {'api_key': args.api_key}
    elif args.user and args.password:
        auth = {'basic_auth': (args.user, args.password)}
    
    client = GrafanaClient(args.url, timeout=args.timeout, **auth) if auth else \
             GrafanaClient(args.url, timeout=args.timeout)
    
    try:
        if args.command == 'list':
            dashboards = client.list_dashboards()
            output = json.dumps(dashboards, indent=2, ensure_ascii=False)
        
        elif args.command == 'create':
            result = client.create_dashboard(title=args.title, folder_id=args.folder)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'get':
            result = client.get_dashboard(args.uid)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'delete':
            result = client.delete_dashboard(args.uid)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'export':
            result = client.export_dashboard(args.uid, args.pretty)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'import':
            with open(args.file, 'r') as f:
                dashboard_json = json.load(f)
            result = client.import_dashboard(dashboard_json, folder_id=args.folder)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'datasources':
            result = client.list_data_sources()
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'folders':
            result = client.list_folders()
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'report':
            output = client.generate_report(output_format=args.format)
        
        elif args.command == 'health':
            result = client.health_check()
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        else:
            parser.print_help()
            return
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        logger.error(f"操作失败: {e}")
        raise


if __name__ == '__main__':
    main()
