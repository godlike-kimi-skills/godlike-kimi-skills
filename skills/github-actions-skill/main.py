"""
GitHub Actions Skill - CI/CD工作流管理

功能：
- Workflow创建、编辑、删除
- 触发器配置（push, PR, schedule, manual）
- Secrets和环境变量管理
- 工作流运行状态监控
- Self-hosted Runner管理
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

import yaml
from github import Github
from github.GithubException import GithubException


class GitHubActionsSkill:
    """GitHub Actions工作流管理类"""
    
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None, 
                 base_url: str = "https://api.github.com"):
        """
        初始化GitHub Actions Skill
        
        Args:
            token: GitHub Personal Access Token
            repo: 仓库名 (格式: owner/repo)
            base_url: GitHub API基础URL
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_name = repo or os.environ.get("GITHUB_REPO")
        self.base_url = base_url
        
        if not self.token:
            raise ValueError("GitHub token is required")
        
        self.github = Github(self.token, base_url=base_url)
        self.repo = None
        
        if self.repo_name:
            self.repo = self.github.get_repo(self.repo_name)
    
    def _create_response(self, success: bool, data: Any = None, 
                         error: Optional[str] = None) -> Dict:
        """创建标准响应对象"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_workflow(self, name: str, content: Optional[str] = None,
                        triggers: Optional[List[str]] = None,
                        jobs: Optional[List[Dict]] = None,
                        on_branch: str = "main") -> Dict:
        """
        创建新的GitHub Actions工作流
        
        Args:
            name: 工作流名称（不含.yml后缀）
            content: 完整的YAML内容（可选）
            triggers: 触发器列表，如["push", "pull_request"]
            jobs: Job配置列表
            on_branch: 目标分支
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            workflow_path = f".github/workflows/{name}.yml"
            
            if content:
                yaml_content = content
            else:
                workflow_def = self._build_workflow(name, triggers, jobs)
                yaml_content = yaml.dump(workflow_def, default_flow_style=False, 
                                        sort_keys=False, allow_unicode=True)
            
            try:
                existing = self.repo.get_contents(workflow_path, ref=on_branch)
                # 更新现有文件
                result = self.repo.update_file(
                    path=workflow_path,
                    message=f"Update workflow: {name}",
                    content=yaml_content,
                    sha=existing.sha,
                    branch=on_branch
                )
            except GithubException as e:
                if e.status == 404:
                    # 创建新文件
                    result = self.repo.create_file(
                        path=workflow_path,
                        message=f"Create workflow: {name}",
                        content=yaml_content,
                        branch=on_branch
                    )
                else:
                    raise
            
            return self._create_response(True, data={
                "workflow_name": name,
                "path": workflow_path,
                "commit_sha": result.get("commit", {}).sha if isinstance(result, dict) else result.sha
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _build_workflow(self, name: str, triggers: Optional[List[str]], 
                        jobs: Optional[List[Dict]]) -> Dict:
        """构建工作流定义字典"""
        workflow = {"name": name}
        
        on_config = {}
        if triggers:
            for trigger in triggers:
                if trigger == "push":
                    on_config["push"] = {"branches": ["main"]}
                elif trigger == "pull_request":
                    on_config["pull_request"] = {"branches": ["main"]}
                elif trigger == "workflow_dispatch":
                    on_config["workflow_dispatch"] = {}
                else:
                    on_config[trigger] = {}
        else:
            on_config = {"push": {"branches": ["main"]}}
        
        workflow["on"] = on_config
        
        workflow["jobs"] = {}
        if jobs:
            for i, job in enumerate(jobs):
                job_name = job.get("name", f"job-{i+1}")
                workflow["jobs"][job_name] = {
                    "runs-on": job.get("runs_on", "ubuntu-latest"),
                    "steps": job.get("steps", [
                        {"uses": "actions/checkout@v4"}
                    ])
                }
        else:
            workflow["jobs"]["build"] = {
                "runs-on": "ubuntu-latest",
                "steps": [{"uses": "actions/checkout@v4"}]
            }
        
        return workflow
    
    def delete_workflow(self, name: str, on_branch: str = "main") -> Dict:
        """
        删除工作流文件
        
        Args:
            name: 工作流名称（不含.yml后缀）
            on_branch: 目标分支
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            workflow_path = f".github/workflows/{name}.yml"
            file_content = self.repo.get_contents(workflow_path, ref=on_branch)
            
            self.repo.delete_file(
                path=workflow_path,
                message=f"Delete workflow: {name}",
                sha=file_content.sha,
                branch=on_branch
            )
            
            return self._create_response(True, data={"deleted": name})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_workflow(self, name: str, on_branch: str = "main") -> Dict:
        """
        获取工作流内容
        
        Args:
            name: 工作流名称
            on_branch: 分支名称
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            workflow_path = f".github/workflows/{name}.yml"
            file_content = self.repo.get_contents(workflow_path, ref=on_branch)
            content = base64.b64decode(file_content.content).decode('utf-8')
            
            return self._create_response(True, data={
                "name": name,
                "path": workflow_path,
                "content": content,
                "sha": file_content.sha
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_workflows(self) -> Dict:
        """
        列出仓库中所有工作流
        
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            workflows = self.repo.get_workflows()
            workflow_list = []
            
            for wf in workflows:
                workflow_list.append({
                    "id": wf.id,
                    "name": wf.name,
                    "path": wf.path,
                    "state": wf.state,
                    "created_at": wf.created_at.isoformat() if wf.created_at else None,
                    "updated_at": wf.updated_at.isoformat() if wf.updated_at else None
                })
            
            return self._create_response(True, data=workflow_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def configure_triggers(self, workflow_name: str, 
                          triggers: Dict[str, Any],
                          on_branch: str = "main") -> Dict:
        """
        配置工作流触发器
        
        Args:
            workflow_name: 工作流名称
            triggers: 触发器配置字典
            on_branch: 目标分支
            
        Returns:
            标准响应对象
        """
        try:
            result = self.get_workflow(workflow_name, on_branch)
            if not result["success"]:
                return result
            
            workflow_def = yaml.safe_load(result["data"]["content"])
            workflow_def["on"] = triggers
            
            new_content = yaml.dump(workflow_def, default_flow_style=False, 
                                   sort_keys=False, allow_unicode=True)
            
            workflow_path = f".github/workflows/{workflow_name}.yml"
            file_content = self.repo.get_contents(workflow_path, ref=on_branch)
            
            update_result = self.repo.update_file(
                path=workflow_path,
                message=f"Update triggers for {workflow_name}",
                content=new_content,
                sha=file_content.sha,
                branch=on_branch
            )
            
            return self._create_response(True, data={
                "workflow": workflow_name,
                "triggers": triggers,
                "commit_sha": update_result["commit"].sha
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def set_secret(self, name: str, value: str) -> Dict:
        """
        设置仓库Secret
        
        Args:
            name: Secret名称
            value: Secret值
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            self.repo.create_secret(name, value)
            
            return self._create_response(True, data={
                "secret_name": name,
                "status": "created"
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def delete_secret(self, name: str) -> Dict:
        """
        删除仓库Secret
        
        Args:
            name: Secret名称
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            self.repo.delete_secret(name)
            
            return self._create_response(True, data={"deleted_secret": name})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_secrets(self) -> Dict:
        """
        列出仓库所有Secrets
        
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            secrets = self.repo.get_secrets()
            secret_list = [{"name": s.name, "created_at": s.created_at} for s in secrets]
            
            return self._create_response(True, data=secret_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_workflow_runs(self, workflow_name: Optional[str] = None,
                          branch: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: int = 30) -> Dict:
        """
        获取工作流运行记录
        
        Args:
            workflow_name: 工作流名称（可选）
            branch: 分支过滤（可选）
            status: 状态过滤（可选）
            limit: 返回数量限制
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            if workflow_name:
                workflow = self.repo.get_workflow(f".github/workflows/{workflow_name}.yml")
                runs = workflow.get_runs()
            else:
                runs = self.repo.get_workflow_runs()
            
            if branch:
                runs = [r for r in runs if r.head_branch == branch]
            if status:
                runs = [r for r in runs if r.status == status]
            
            run_list = []
            for run in list(runs)[:limit]:
                run_list.append({
                    "id": run.id,
                    "name": run.name,
                    "head_branch": run.head_branch,
                    "head_sha": run.head_sha[:8],
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "created_at": run.created_at.isoformat() if run.created_at else None,
                    "run_number": run.run_number,
                    "html_url": run.html_url
                })
            
            return self._create_response(True, data=run_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_run_logs(self, run_id: int) -> Dict:
        """
        获取工作流运行日志
        
        Args:
            run_id: 运行ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            run = self.repo.get_workflow_run(run_id)
            logs_url = run.logs_url
            
            return self._create_response(True, data={
                "run_id": run_id,
                "status": run.status,
                "conclusion": run.conclusion,
                "logs_url": logs_url,
                "html_url": run.html_url
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def rerun_workflow(self, run_id: int) -> Dict:
        """
        重新运行工作流
        
        Args:
            run_id: 运行ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            run = self.repo.get_workflow_run(run_id)
            run.rerun()
            
            return self._create_response(True, data={"rerun": run_id})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def cancel_workflow(self, run_id: int) -> Dict:
        """
        取消工作流运行
        
        Args:
            run_id: 运行ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            run = self.repo.get_workflow_run(run_id)
            run.cancel()
            
            return self._create_response(True, data={"cancelled": run_id})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_runners(self) -> Dict:
        """
        列出Self-hosted runners
        
        Returns:
            标准响应对象
        """
        try:
            if not self.repo:
                return self._create_response(False, error="Repository not set")
            
            runners = self.repo.get_self_hosted_runners()
            runner_list = []
            
            for runner in runners:
                runner_list.append({
                    "id": runner.id,
                    "name": runner.name,
                    "os": runner.os,
                    "status": runner.status,
                    "busy": runner.busy,
                    "labels": [l.name for l in runner.labels()]
                })
            
            return self._create_response(True, data=runner_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def generate_template(self, template_type: str = "ci",
                          language: str = "python") -> Dict:
        """
        生成工作流模板
        
        Args:
            template_type: 模板类型 (ci, cd, test, deploy)
            language: 编程语言
            
        Returns:
            标准响应对象
        """
        try:
            templates = {
                "ci": self._generate_ci_template(language),
                "cd": self._generate_cd_template(),
                "test": self._generate_test_template(language),
                "deploy": self._generate_deploy_template()
            }
            
            template = templates.get(template_type, templates["ci"])
            
            return self._create_response(True, data={
                "template_type": template_type,
                "language": language,
                "content": template
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _generate_ci_template(self, language: str) -> str:
        """生成CI模板"""
        setup_steps = {
            "python": [
                {"uses": "actions/checkout@v4"},
                {"uses": "actions/setup-python@v5", "with": {"python-version": "3.11"}},
                {"run": "pip install -r requirements.txt"},
                {"run": "pytest"}
            ],
            "nodejs": [
                {"uses": "actions/checkout@v4"},
                {"uses": "actions/setup-node@v4", "with": {"node-version": "20"}},
                {"run": "npm ci"},
                {"run": "npm test"}
            ],
            "go": [
                {"uses": "actions/checkout@v4"},
                {"uses": "actions/setup-go@v5", "with": {"go-version": "1.21"}},
                {"run": "go build -v ./..."},
                {"run": "go test -v ./..."}
            ]
        }
        
        steps = setup_steps.get(language, setup_steps["python"])
        
        template = {
            "name": "CI",
            "on": {"push": {"branches": ["main"]}, "pull_request": {"branches": ["main"]}},
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": steps
                }
            }
        }
        
        return yaml.dump(template, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _generate_cd_template(self) -> str:
        """生成CD模板"""
        template = {
            "name": "CD",
            "on": {"push": {"tags": ["v*"]}},
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {"name": "Deploy to Production", "run": "echo 'Deploying...'"}
                    ]
                }
            }
        }
        return yaml.dump(template, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _generate_test_template(self, language: str) -> str:
        """生成测试模板"""
        return self._generate_ci_template(language)
    
    def _generate_deploy_template(self) -> str:
        """生成部署模板"""
        return self._generate_cd_template()


if __name__ == "__main__":
    # 简单测试
    print("GitHub Actions Skill 已加载")
    print("使用方法: from main import GitHubActionsSkill")
