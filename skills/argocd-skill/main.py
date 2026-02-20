"""
ArgoCD Skill - GitOps管理

功能：
- Application创建、更新、删除
- Sync操作（同步、强制同步、回滚）
- Git/Helm仓库配置
- Application状态监控
- 资源树查看
- 同步历史管理
"""

import os
import json
import time
import urllib3
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ArgoCDSkill:
    """ArgoCD GitOps管理类"""
    
    def __init__(self, server: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 token: Optional[str] = None,
                 insecure: bool = False):
        """
        初始化ArgoCD Skill
        
        Args:
            server: ArgoCD服务器URL
            username: 用户名
            password: 密码
            token: API Token（可直接提供，或从环境变量获取）
            insecure: 跳过TLS验证
        """
        self.server = (server or os.environ.get("ARGOCD_SERVER", "")).rstrip("/")
        self.username = username or os.environ.get("ARGOCD_USERNAME")
        self.password = password or os.environ.get("ARGOCD_PASSWORD")
        self.token = token or os.environ.get("ARGOCD_TOKEN")
        self.insecure = insecure
        
        if not self.server:
            raise ValueError("ArgoCD server URL is required")
        
        # 创建session
        self.session = requests.Session()
        self.session.verify = not insecure
        
        # 配置重试
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 如果提供了token直接使用，否则尝试登录
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        elif self.username and self.password:
            self._login()
        else:
            raise ValueError("Either token or username/password is required")
    
    def _login(self) -> None:
        """使用用户名密码登录获取token"""
        login_url = f"{self.server}/api/v1/session"
        response = self.session.post(
            login_url,
            json={"username": self.username, "password": self.password}
        )
        response.raise_for_status()
        
        self.token = response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def _request(self, method: str, endpoint: str, 
                 **kwargs) -> Dict:
        """
        发送API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.server}/api/v1{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        if response.content:
            return response.json()
        return {}
    
    def _create_response(self, success: bool, data: Any = None,
                         error: Optional[str] = None) -> Dict:
        """创建标准响应对象"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_server_info(self) -> Dict:
        """
        获取ArgoCD服务器信息
        
        Returns:
            标准响应对象
        """
        try:
            info = self._request("GET", "/settings")
            return self._create_response(True, data={
                "url": self.server,
                "dexEnabled": info.get("dexEnabled", False),
                "disablePassword": info.get("disablePassword", False),
                "googleAnalyticsID": info.get("googleAnalyticsID"),
                "help": info.get("help", {}),
                "oidcConfig": info.get("oidcConfig")
            })
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def create_app(self, name: str, repo_url: str, path: str,
                   dest_server: str = "https://kubernetes.default.svc",
                   dest_namespace: str = "default",
                   project: str = "default",
                   sync_policy: Optional[Dict] = None,
                   helm_values: Optional[Dict] = None,
                   kustomize: Optional[Dict] = None) -> Dict:
        """
        创建ArgoCD Application
        
        Args:
            name: Application名称
            repo_url: Git仓库URL
            path: 资源路径
            dest_server: 目标Kubernetes集群
            dest_namespace: 目标命名空间
            project: ArgoCD项目
            sync_policy: 同步策略
            helm_values: Helm值
            kustomize: Kustomize配置
            
        Returns:
            标准响应对象
        """
        try:
            # 构建source
            source = {
                "repoURL": repo_url,
                "targetRevision": "HEAD",
                "path": path
            }
            
            if helm_values:
                source["helm"] = helm_values
            
            if kustomize:
                source["kustomize"] = kustomize
            
            # 构建application
            app = {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "Application",
                "metadata": {
                    "name": name,
                    "namespace": "argocd"
                },
                "spec": {
                    "project": project,
                    "source": source,
                    "destination": {
                        "server": dest_server,
                        "namespace": dest_namespace
                    }
                }
            }
            
            if sync_policy:
                app["spec"]["syncPolicy"] = sync_policy
            
            response = self._request("POST", "/applications", json=app)
            
            return self._create_response(True, data={
                "name": name,
                "repoURL": repo_url,
                "path": path,
                "destination": f"{dest_server}/{dest_namespace}",
                "status": response.get("status", {}).get("sync", {}).get("status")
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def delete_app(self, name: str, cascade: bool = True) -> Dict:
        """
        删除Application
        
        Args:
            name: Application名称
            cascade: 是否级联删除资源
            
        Returns:
            标准响应对象
        """
        try:
            params = {"cascade": str(cascade).lower()}
            self._request("DELETE", f"/applications/{name}", params=params)
            
            return self._create_response(True, data={"deleted": name})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_app(self, name: str) -> Dict:
        """
        获取Application详情
        
        Args:
            name: Application名称
            
        Returns:
            标准响应对象
        """
        try:
            app = self._request("GET", f"/applications/{name}")
            
            metadata = app.get("metadata", {})
            spec = app.get("spec", {})
            status = app.get("status", {})
            
            return self._create_response(True, data={
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "project": spec.get("project"),
                "source": spec.get("source"),
                "destination": spec.get("destination"),
                "syncPolicy": spec.get("syncPolicy"),
                "syncStatus": status.get("sync", {}).get("status"),
                "healthStatus": status.get("health", {}).get("status"),
                "resources": status.get("resources", []),
                "history": status.get("history", []),
                "reconciledAt": status.get("reconciledAt"),
                "operationState": status.get("operationState")
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_apps(self, project: Optional[str] = None) -> Dict:
        """
        列出Applications
        
        Args:
            project: 项目过滤（可选）
            
        Returns:
            标准响应对象
        """
        try:
            params = {}
            if project:
                params["project"] = project
            
            result = self._request("GET", "/applications", params=params)
            apps = result.get("items", [])
            
            app_list = []
            for app in apps:
                metadata = app.get("metadata", {})
                spec = app.get("spec", {})
                status = app.get("status", {})
                
                app_list.append({
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "project": spec.get("project"),
                    "repoURL": spec.get("source", {}).get("repoURL"),
                    "path": spec.get("source", {}).get("path"),
                    "syncStatus": status.get("sync", {}).get("status"),
                    "healthStatus": status.get("health", {}).get("status"),
                    "destination": spec.get("destination")
                })
            
            return self._create_response(True, data=app_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def sync_app(self, name: str, revision: str = "HEAD",
                 resources: Optional[List[str]] = None,
                 prune: bool = False, dry_run: bool = False,
                 force: bool = False, wait: bool = False,
                 timeout: int = 300) -> Dict:
        """
        同步Application
        
        Args:
            name: Application名称
            revision: 要同步的版本
            resources: 要同步的特定资源
            prune: 是否清理未跟踪资源
            dry_run: 是否仅预览
            force: 是否强制同步
            wait: 是否等待同步完成
            timeout: 等待超时（秒）
            
        Returns:
            标准响应对象
        """
        try:
            sync_request = {
                "revision": revision,
                "prune": prune,
                "dryRun": dry_run,
                "strategy": {
                    "hook": {"force": force}
                }
            }
            
            if resources:
                sync_request["resources"] = [
                    {"group": r.split("/")[0] if "/" in r else "",
                     "kind": r.split("/")[1] if "/" in r else r,
                     "name": r.split("/")[2] if "/" in r and len(r.split("/")) > 2 else ""}
                    for r in resources
                ]
            
            response = self._request("POST", "/applications/{}/sync".format(name),
                                    json=sync_request)
            
            if wait:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    app_info = self.get_app(name)
                    if app_info["success"]:
                        sync_status = app_info["data"].get("syncStatus")
                        if sync_status == "Synced":
                            break
                        elif sync_status == "Failed":
                            return self._create_response(False, 
                                error="Sync failed", data=app_info["data"])
                    time.sleep(2)
            
            return self._create_response(True, data={
                "name": name,
                "revision": revision,
                "synced": True
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def rollback_app(self, name: str, history_id: int) -> Dict:
        """
        回滚Application到指定版本
        
        Args:
            name: Application名称
            history_id: 历史记录ID
            
        Returns:
            标准响应对象
        """
        try:
            rollback_request = {"id": history_id}
            self._request("POST", f"/applications/{name}/rollback",
                         json=rollback_request)
            
            return self._create_response(True, data={
                "name": name,
                "history_id": history_id,
                "rolled_back": True
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_app_resources(self, name: str) -> Dict:
        """
        获取Application的资源树
        
        Args:
            name: Application名称
            
        Returns:
            标准响应对象
        """
        try:
            resources = self._request("GET", "/applications/{}/resource-tree".format(name))
            
            nodes = resources.get("nodes", [])
            resource_list = []
            
            for node in nodes:
                resource_list.append({
                    "group": node.get("group"),
                    "kind": node.get("kind"),
                    "namespace": node.get("namespace"),
                    "name": node.get("name"),
                    "status": node.get("status"),
                    "health": node.get("health", {}).get("status"),
                    "createdAt": node.get("createdAt")
                })
            
            return self._create_response(True, data=resource_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_app_history(self, name: str, limit: int = 10) -> Dict:
        """
        获取Application的同步历史
        
        Args:
            name: Application名称
            limit: 返回数量限制
            
        Returns:
            标准响应对象
        """
        try:
            app = self._request("GET", f"/applications/{name}")
            history = app.get("status", {}).get("history", [])[:limit]
            
            history_list = []
            for item in history:
                history_list.append({
                    "id": item.get("id"),
                    "revision": item.get("revision"),
                    "deployedAt": item.get("deployedAt"),
                    "deployStartedAt": item.get("deployStartedAt"),
                    "source": item.get("source")
                })
            
            return self._create_response(True, data=history_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def add_repo(self, url: str, username: Optional[str] = None,
                 password: Optional[str] = None,
                 ssh_private_key: Optional[str] = None,
                 insecure: bool = False) -> Dict:
        """
        添加Git仓库
        
        Args:
            url: 仓库URL
            username: 用户名
            password: 密码/Token
            ssh_private_key: SSH私钥
            insecure: 是否跳过TLS验证
            
        Returns:
            标准响应对象
        """
        try:
            repo = {
                "repo": url,
                "insecure": insecure,
                "insecureIgnoreHostKey": insecure
            }
            
            if username and password:
                repo["username"] = username
                repo["password"] = password
            
            if ssh_private_key:
                repo["sshPrivateKey"] = ssh_private_key
            
            response = self._request("POST", "/repositories", json=repo)
            
            return self._create_response(True, data={
                "repo": url,
                "connectionState": response.get("connectionState", {}).get("status")
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def delete_repo(self, url: str) -> Dict:
        """
        删除Git仓库
        
        Args:
            url: 仓库URL
            
        Returns:
            标准响应对象
        """
        try:
            # URL编码
            import urllib.parse
            encoded_url = urllib.parse.quote(url, safe="")
            self._request("DELETE", f"/repositories/{encoded_url}")
            
            return self._create_response(True, data={"deleted": url})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_repos(self) -> Dict:
        """
        列出已配置的仓库
        
        Returns:
            标准响应对象
        """
        try:
            result = self._request("GET", "/repositories")
            items = result.get("items", [])
            
            repo_list = []
            for repo in items:
                repo_list.append({
                    "repo": repo.get("repo"),
                    "connectionState": repo.get("connectionState", {}).get("status"),
                    "type": repo.get("type", "git"),
                    "insecure": repo.get("insecure", False)
                })
            
            return self._create_response(True, data=repo_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def add_helm_repo(self, name: str, url: str,
                      username: Optional[str] = None,
                      password: Optional[str] = None) -> Dict:
        """
        添加Helm仓库
        
        Args:
            name: 仓库名称
            url: 仓库URL
            username: 用户名
            password: 密码
            
        Returns:
            标准响应对象
        """
        try:
            repo = {
                "name": name,
                "repo": url,
                "type": "helm"
            }
            
            if username and password:
                repo["username"] = username
                repo["password"] = password
            
            response = self._request("POST", "/repositories", json=repo)
            
            return self._create_response(True, data={
                "name": name,
                "repo": url,
                "type": "helm"
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_projects(self) -> Dict:
        """
        列出ArgoCD项目
        
        Returns:
            标准响应对象
        """
        try:
            result = self._request("GET", "/projects")
            items = result.get("items", [])
            
            project_list = []
            for proj in items:
                metadata = proj.get("metadata", {})
                spec = proj.get("spec", {})
                
                project_list.append({
                    "name": metadata.get("name"),
                    "description": spec.get("description"),
                    "sourceRepos": spec.get("sourceRepos", []),
                    "destinations": spec.get("destinations", [])
                })
            
            return self._create_response(True, data=project_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def generate_app_template(self, app_type: str = "git",
                             **kwargs) -> Dict:
        """
        生成Application模板
        
        Args:
            app_type: 应用类型 (git, helm, kustomize)
            **kwargs: 模板参数
            
        Returns:
            标准响应对象
        """
        try:
            templates = {
                "git": self._generate_git_template,
                "helm": self._generate_helm_template,
                "kustomize": self._generate_kustomize_template
            }
            
            template_func = templates.get(app_type, self._generate_git_template)
            template = template_func(**kwargs)
            
            return self._create_response(True, data={
                "app_type": app_type,
                "template": template
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _generate_git_template(self, name: str = "my-app",
                               repo_url: str = "https://github.com/org/repo.git",
                               path: str = "manifests",
                               namespace: str = "default",
                               auto_sync: bool = True) -> str:
        """生成Git应用模板"""
        app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": name,
                "namespace": "argocd",
                "finalizers": ["resources-finalizer.argocd.argoproj.io"]
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": repo_url,
                    "targetRevision": "HEAD",
                    "path": path
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": namespace
                },
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": auto_sync
                    },
                    "syncOptions": ["CreateNamespace=true"]
                }
            }
        }
        
        return yaml.dump(app, default_flow_style=False, 
                        sort_keys=False, allow_unicode=True)
    
    def _generate_helm_template(self, name: str = "my-helm-app",
                                repo_url: str = "https://charts.helm.sh/stable",
                                chart: str = "my-chart",
                                version: str = "1.0.0",
                                values: Optional[Dict] = None) -> str:
        """生成Helm应用模板"""
        app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": name,
                "namespace": "argocd"
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": repo_url,
                    "targetRevision": version,
                    "chart": chart,
                    "helm": {
                        "releaseName": name
                    }
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": name
                },
                "syncPolicy": {
                    "syncOptions": ["CreateNamespace=true"]
                }
            }
        }
        
        if values:
            app["spec"]["source"]["helm"]["values"] = yaml.dump(values, default_flow_style=False)
        
        return yaml.dump(app, default_flow_style=False,
                        sort_keys=False, allow_unicode=True)
    
    def _generate_kustomize_template(self, name: str = "my-kustomize-app",
                                     repo_url: str = "https://github.com/org/repo.git",
                                     path: str = "overlays/production",
                                     name_prefix: str = "prod-") -> str:
        """生成Kustomize应用模板"""
        app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": name,
                "namespace": "argocd"
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": repo_url,
                    "targetRevision": "HEAD",
                    "path": path,
                    "kustomize": {
                        "namePrefix": name_prefix
                    }
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": "production"
                },
                "syncPolicy": {
                    "syncOptions": ["CreateNamespace=true"]
                }
            }
        }
        
        return yaml.dump(app, default_flow_style=False,
                        sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    print("ArgoCD Skill 已加载")
    print("使用方法: from main import ArgoCDSkill")
