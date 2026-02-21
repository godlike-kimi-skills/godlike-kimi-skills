#!/usr/bin/env python3
"""
daily-sync.py - 每日竞品扫描系统
扫描竞品仓库，识别热门 skills 并创建移植任务
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

class CompetitorScanner:
    def __init__(self):
        self.targets = {
            'openclaw': 'https://api.github.com/repos/VoltAgent/awesome-openclaw-skills',
            'claude': 'https://api.github.com/repos/daymade/claude-code-skills',
        }
        self.results = {}
    
    def scan_github_repo(self, repo_url):
        """扫描 GitHub 仓库"""
        try:
            # 获取最新 commits
            commits_url = f"{repo_url}/commits"
            since = (datetime.now() - timedelta(days=1)).isoformat()
            response = requests.get(commits_url, params={'since': since}, timeout=10)
            new_commits = len(response.json()) if response.status_code == 200 else 0
            
            # 获取 README 内容
            readme_url = f"{repo_url}/contents/README.md"
            readme_resp = requests.get(readme_url, timeout=10)
            readme_content = readme_resp.json().get('content', '') if readme_resp.status_code == 200 else ''
            
            return {
                'new_commits': new_commits,
                'readme_content': readme_content[:1000],  # 截断避免过大
                'status': 'success'
            }
        except Exception as e:
            return {
                'new_commits': 0,
                'readme_content': '',
                'status': f'error: {e}'
            }
    
    def generate_report(self):
        """生成扫描报告"""
        report = {
            'date': datetime.now().isoformat(),
            'findings': {}
        }
        
        for name, url in self.targets.items():
            print(f"扫描 {name}...")
            data = self.scan_github_repo(url)
            report['findings'][name] = data
        
        return report
    
    def save_report(self, report):
        """保存报告到文件"""
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = reports_dir / f'scan-report-{date_str}.json'
        
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"报告已保存: {report_file}")
        
        # 同时更新最新报告
        latest_file = reports_dir / 'latest-scan.json'
        latest_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    scanner = CompetitorScanner()
    report = scanner.generate_report()
    scanner.save_report(report)
    
    print("\n=== 扫描完成 ===")
    for name, data in report['findings'].items():
        print(f"{name}: {data['new_commits']} 个新 commits")
