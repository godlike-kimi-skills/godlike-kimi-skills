"""
GitLab CI Skill - CI/CD管理

功能：
- .gitlab-ci.yml创建和编辑
- GitLab Runner管理
- Pipeline查看和触发
- CI/CD变量管理
- 调度任务管理
"""

import os
import base64
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

import yaml
import gitlab
from gitlab.exceptions import GitlabError


class GitLabCISkill:
    """GitLab CI/CD管理类"""
    
    def __init__(self, token: Optional[str] = None, 
                 project: Optional[str] = None,
                 url: str = "https://gitlab.com",
                 timeout: int = 30):
        """
        初始化GitLab CI Skill
        
        Args:
            token: GitLab Personal Access Token
            project: 项目路径或ID
            url: GitLab URL
            timeout: 请求超时
        """
        self.token = token or os.environ.get("GITLAB_TOKEN")
        self.project_id = project or os.environ.get("GITLAB_PROJECT")
        self.url = url.rstrip("/")
        self.timeout = timeout
        
        if not self.token:
            raise ValueError("GitLab token is required")
        
        # 初始化GitLab连接
        self.gl = gitlab.Gitlab(self.url, private_token=self.token, timeout=timeout)
        self.gl.auth()
        
        self.project = None
        if self.project_id:
            self.project = self.gl.projects.get(self.project_id)
    
    def _create_response(self, success: bool, data: Any = None,
                         error: Optional[str] = None) -> Dict:
        """创建标准响应对象"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_ci_config(self, ref: str = "main") -> Dict:
        """
        获取CI配置文件内容
        
        Args:
            ref: 分支或标签
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            try:
                file_content = self.project.files.get(file_path=".gitlab-ci.yml", ref=ref)
                content = base64.b64decode(file_content.content).decode('utf-8')
                parsed = yaml.safe_load(content)
                
                return self._create_response(True, data={
                    "content": content,
                    "parsed": parsed,
                    "sha": file_content.sha,
                    "ref": ref
                })
            except GitlabError as e:
                if e.response_code == 404:
                    return self._create_response(False, error=".gitlab-ci.yml not found")
                raise
                
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def create_ci_config(self, stages: List[str],
                         jobs: Dict[str, Dict],
                         variables: Optional[Dict] = None,
                         default: Optional[Dict] = None,
                         ref: str = "main",
                         commit_message: str = "Create .gitlab-ci.yml") -> Dict:
        """
        创建CI配置文件
        
        Args:
            stages: 阶段列表
            jobs: Job配置字典
            variables: CI/CD变量
            default: 默认配置
            ref: 目标分支
            commit_message: 提交信息
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            config = {"stages": stages}
            
            if variables:
                config["variables"] = variables
            if default:
                config["default"] = default
            
            config.update(jobs)
            
            content = yaml.dump(config, default_flow_style=False, 
                               sort_keys=False, allow_unicode=True)
            
            try:
                # 检查文件是否已存在
                existing = self.project.files.get(file_path=".gitlab-ci.yml", ref=ref)
                # 更新文件
                existing.content = content
                existing.save(branch=ref, commit_message=f"Update {commit_message}")
                
                return self._create_response(True, data={
                    "action": "updated",
                    "path": ".gitlab-ci.yml",
                    "commit_id": existing.commit_id
                })
            except GitlabError as e:
                if e.response_code == 404:
                    # 创建新文件
                    new_file = self.project.files.create({
                        'file_path': '.gitlab-ci.yml',
                        'branch': ref,
                        'content': content,
                        'commit_message': commit_message
                    })
                    
                    return self._create_response(True, data={
                        "action": "created",
                        "path": ".gitlab-ci.yml",
                        "commit_id": new_file.commit_id
                    })
                raise
                
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def update_ci_job(self, job_name: str, job_config: Dict,
                      ref: str = "main") -> Dict:
        """
        更新特定Job配置
        
        Args:
            job_name: Job名称
            job_config: Job配置
            ref: 目标分支
            
        Returns:
            标准响应对象
        """
        try:
            result = self.get_ci_config(ref)
            if not result["success"]:
                return result
            
            config = result["data"]["parsed"]
            config[job_name] = job_config
            
            stages = config.get("stages", [])
            variables = config.get("variables")
            default = config.get("default")
            
            # 提取jobs（非保留键）
            reserved = ["stages", "variables", "default", "include", "workflow"]
            jobs = {k: v for k, v in config.items() if k not in reserved}
            
            return self.create_ci_config(
                stages=stages,
                jobs=jobs,
                variables=variables,
                default=default,
                ref=ref,
                commit_message=f"Update CI job: {job_name}"
            )
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def delete_ci_config(self, ref: str = "main") -> Dict:
        """
        删除CI配置文件
        
        Args:
            ref: 目标分支
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            file_content = self.project.files.get(file_path=".gitlab-ci.yml", ref=ref)
            file_content.delete(branch=ref, commit_message="Delete .gitlab-ci.yml")
            
            return self._create_response(True, data={"deleted": ".gitlab-ci.yml"})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def validate_ci_config(self, content: Optional[str] = None,
                           ref: str = "main") -> Dict:
        """
        验证CI配置
        
        Args:
            content: CI配置内容（可选，不提供则获取当前配置）
            ref: 分支
            
        Returns:
            标准响应对象
        """
        try:
            if content is None:
                result = self.get_ci_config(ref)
                if not result["success"]:
                    return result
                content = result["data"]["content"]
            
            # 尝试解析YAML
            parsed = yaml.safe_load(content)
            
            errors = []
            warnings = []
            
            # 基本验证
            if not parsed:
                errors.append("Empty configuration")
            else:
                # 检查stages
                if "stages" in parsed:
                    if not isinstance(parsed["stages"], list):
                        errors.append("'stages' must be a list")
                
                # 检查jobs
                reserved_keys = ["stages", "variables", "default", "include", "workflow", "cache"]
                jobs = {k: v for k, v in parsed.items() if k not in reserved_keys}
                
                for job_name, job_config in jobs.items():
                    if not isinstance(job_config, dict):
                        errors.append(f"Job '{job_name}' must be a dictionary")
                        continue
                    
                    if "script" not in job_config and "trigger" not in job_config:
                        warnings.append(f"Job '{job_name}' has no 'script' or 'trigger'")
            
            return self._create_response(True, data={
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            })
            
        except yaml.YAMLError as e:
            return self._create_response(False, error=f"YAML syntax error: {e}")
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_runners(self, scope: str = "specific") -> Dict:
        """
        列出Runners
        
        Args:
            scope: 范围 (specific, shared, group)
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            runners = self.project.runners.list(all=True)
            
            runner_list = []
            for runner in runners:
                runner_list.append({
                    "id": runner.id,
                    "description": runner.description,
                    "active": runner.active,
                    "online": getattr(runner, 'online', None),
                    "status": getattr(runner, 'status', None),
                    "tags": runner.tag_list if hasattr(runner, 'tag_list') else [],
                    "executor": getattr(runner, 'executor', None)
                })
            
            return self._create_response(True, data=runner_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_runner(self, runner_id: int) -> Dict:
        """
        获取Runner详情
        
        Args:
            runner_id: Runner ID
            
        Returns:
            标准响应对象
        """
        try:
            runner = self.gl.runners.get(runner_id)
            
            return self._create_response(True, data={
                "id": runner.id,
                "description": runner.description,
                "active": runner.active,
                "paused": getattr(runner, 'paused', False),
                "online": getattr(runner, 'online', False),
                "status": getattr(runner, 'status', None),
                "architecture": getattr(runner, 'architecture', None),
                "platform": getattr(runner, 'platform', None),
                "executor": getattr(runner, 'executor', None),
                "tags": runner.tag_list if hasattr(runner, 'tag_list') else [],
                "version": getattr(runner, 'version', None),
                "ip_address": getattr(runner, 'ip_address', None),
                "maximum_timeout": getattr(runner, 'maximum_timeout', None)
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def register_runner(self, token: str, description: str,
                       tags: Optional[List[str]] = None,
                       executor: str = "docker") -> Dict:
        """
        注册Runner（获取注册令牌后）
        
        Args:
            token: 注册令牌
            description: Runner描述
            tags: 标签列表
            executor: 执行器类型
            
        Returns:
            标准响应对象
        """
        try:
            runner = self.gl.runners.create({
                "token": token,
                "description": description,
                "tag_list": tags or [],
                "executor": executor
            })
            
            return self._create_response(True, data={
                "id": runner.id,
                "token": runner.token,
                "description": runner.description
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def unregister_runner(self, runner_id: int) -> Dict:
        """
        注销Runner
        
        Args:
            runner_id: Runner ID
            
        Returns:
            标准响应对象
        """
        try:
            runner = self.gl.runners.get(runner_id)
            runner.delete()
            
            return self._create_response(True, data={"deleted": runner_id})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_pipelines(self, status: Optional[str] = None,
                       ref: Optional[str] = None,
                       limit: int = 20) -> Dict:
        """
        列出Pipelines
        
        Args:
            status: 状态过滤 (created, pending, running, success, failed, canceled)
            ref: 分支过滤
            limit: 返回数量
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            params = {"per_page": limit}
            if status:
                params["status"] = status
            if ref:
                params["ref"] = ref
            
            pipelines = self.project.pipelines.list(**params)
            
            pipeline_list = []
            for pipe in pipelines:
                pipeline_list.append({
                    "id": pipe.id,
                    "sha": pipe.sha,
                    "ref": pipe.ref,
                    "status": pipe.status,
                    "source": getattr(pipe, 'source', None),
                    "created_at": pipe.created_at,
                    "updated_at": pipe.updated_at,
                    "web_url": pipe.web_url
                })
            
            return self._create_response(True, data=pipeline_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_pipeline(self, pipeline_id: int) -> Dict:
        """
        获取Pipeline详情
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            pipeline = self.project.pipelines.get(pipeline_id)
            
            # 获取Jobs
            jobs = pipeline.jobs.list(all=True)
            job_list = []
            for job in jobs:
                job_list.append({
                    "id": job.id,
                    "name": job.name,
                    "stage": job.stage,
                    "status": job.status,
                    "duration": getattr(job, 'duration', None),
                    "queued_duration": getattr(job, 'queued_duration', None),
                    "started_at": getattr(job, 'started_at', None),
                    "finished_at": getattr(job, 'finished_at', None)
                })
            
            return self._create_response(True, data={
                "id": pipeline.id,
                "sha": pipeline.sha,
                "ref": pipeline.ref,
                "status": pipeline.status,
                "before_sha": getattr(pipeline, 'before_sha', None),
                "tag": getattr(pipeline, 'tag', False),
                "yaml_errors": getattr(pipeline, 'yaml_errors', None),
                "created_at": pipeline.created_at,
                "updated_at": pipeline.updated_at,
                "started_at": getattr(pipeline, 'started_at', None),
                "finished_at": getattr(pipeline, 'finished_at', None),
                "committed_at": getattr(pipeline, 'committed_at', None),
                "duration": getattr(pipeline, 'duration', None),
                "queued_duration": getattr(pipeline, 'queued_duration', None),
                "web_url": pipeline.web_url,
                "jobs": job_list
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def trigger_pipeline(self, ref: str = "main",
                         variables: Optional[Dict] = None) -> Dict:
        """
        触发Pipeline
        
        Args:
            ref: 分支或标签
            variables: Pipeline变量
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            params = {"ref": ref}
            if variables:
                params["variables"] = [
                    {"key": k, "value": v} for k, v in variables.items()
                ]
            
            pipeline = self.project.pipelines.create(params)
            
            return self._create_response(True, data={
                "id": pipeline.id,
                "sha": pipeline.sha,
                "ref": pipeline.ref,
                "status": pipeline.status,
                "web_url": pipeline.web_url
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def retry_pipeline(self, pipeline_id: int) -> Dict:
        """
        重试Pipeline
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            pipeline = self.project.pipelines.get(pipeline_id)
            new_pipeline = pipeline.retry()
            
            return self._create_response(True, data={
                "id": new_pipeline.id,
                "ref": new_pipeline.ref,
                "status": new_pipeline.status,
                "web_url": new_pipeline.web_url
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def cancel_pipeline(self, pipeline_id: int) -> Dict:
        """
        取消Pipeline
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            pipeline = self.project.pipelines.get(pipeline_id)
            pipeline.cancel()
            
            return self._create_response(True, data={"cancelled": pipeline_id})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_job_log(self, job_id: int) -> Dict:
        """
        获取Job日志
        
        Args:
            job_id: Job ID
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            job = self.project.jobs.get(job_id)
            log = job.trace()
            
            return self._create_response(True, data={
                "job_id": job_id,
                "job_name": job.name,
                "log": log.decode('utf-8', errors='replace') if log else ""
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_variables(self) -> Dict:
        """
        列出CI/CD变量
        
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            variables = self.project.variables.list(all=True)
            
            var_list = []
            for var in variables:
                var_list.append({
                    "key": var.key,
                    "protected": var.protected,
                    "masked": var.masked,
                    "environment_scope": getattr(var, 'environment_scope', '*')
                })
            
            return self._create_response(True, data=var_list)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def set_variable(self, key: str, value: str,
                    protected: bool = False,
                    masked: bool = False,
                    environment_scope: str = "*") -> Dict:
        """
        设置CI/CD变量
        
        Args:
            key: 变量名
            value: 变量值
            protected: 是否受保护
            masked: 是否掩码
            environment_scope: 环境范围
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            try:
                # 尝试更新现有变量
                var = self.project.variables.get(key)
                var.value = value
                var.protected = protected
                var.masked = masked
                var.environment_scope = environment_scope
                var.save()
                action = "updated"
            except GitlabError:
                # 创建新变量
                var = self.project.variables.create({
                    "key": key,
                    "value": value,
                    "protected": protected,
                    "masked": masked,
                    "environment_scope": environment_scope
                })
                action = "created"
            
            return self._create_response(True, data={
                "key": key,
                "action": action,
                "protected": protected,
                "masked": masked
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def delete_variable(self, key: str) -> Dict:
        """
        删除CI/CD变量
        
        Args:
            key: 变量名
            
        Returns:
            标准响应对象
        """
        try:
            if not self.project:
                return self._create_response(False, error="Project not set")
            
            var = self.project.variables.get(key)
            var.delete()
            
            return self._create_response(True, data={"deleted": key})
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def generate_ci_template(self, template_type: str = "python",
                             stages: Optional[List[str]] = None) -> Dict:
        """
        生成CI配置模板
        
        Args:
            template_type: 模板类型 (python, nodejs, java, docker)
            stages: 自定义stages
            
        Returns:
            标准响应对象
        """
        try:
            templates = {
                "python": self._generate_python_template(stages),
                "nodejs": self._generate_nodejs_template(stages),
                "java": self._generate_java_template(stages),
                "docker": self._generate_docker_template(stages)
            }
            
            template = templates.get(template_type, templates["python"])
            
            return self._create_response(True, data={
                "template_type": template_type,
                "content": template
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _generate_python_template(self, stages: Optional[List[str]]) -> str:
        """生成Python CI模板"""
        stages = stages or ["test", "build", "deploy"]
        
        config = {
            "stages": stages,
            "variables": {
                "PIP_CACHE_DIR": "$CI_PROJECT_DIR/.cache/pip"
            },
            "cache": {
                "paths": [".cache/pip", "venv/"]
            },
            "before_script": [
                "python -V",
                "pip install virtualenv",
                "virtualenv venv",
                "source venv/bin/activate"
            ],
            "test": {
                "stage": "test",
                "script": [
                    "pip install -r requirements.txt",
                    "pip install pytest pytest-cov",
                    "pytest --cov=. --cov-report=xml"
                ],
                "artifacts": {
                    "reports": {
                        "coverage_report": {
                            "coverage_format": "cobertura",
                            "path": "coverage.xml"
                        }
                    }
                }
            },
            "build": {
                "stage": "build",
                "script": [
                    "pip install -r requirements.txt",
                    "python setup.py build"
                ],
                "artifacts": {
                    "paths": ["dist/"]
                }
            }
        }
        
        return yaml.dump(config, default_flow_style=False, 
                        sort_keys=False, allow_unicode=True)
    
    def _generate_nodejs_template(self, stages: Optional[List[str]]) -> str:
        """生成Node.js CI模板"""
        stages = stages or ["install", "test", "build"]
        
        config = {
            "stages": stages,
            "variables": {
                "NODE_VERSION": "20"
            },
            "cache": {
                "paths": ["node_modules/"]
            },
            "install": {
                "stage": "install",
                "image": "node:${NODE_VERSION}",
                "script": ["npm ci"]
            },
            "test": {
                "stage": "test",
                "image": "node:${NODE_VERSION}",
                "script": ["npm test"]
            },
            "build": {
                "stage": "build",
                "image": "node:${NODE_VERSION}",
                "script": ["npm run build"],
                "artifacts": {
                    "paths": ["dist/"]
                }
            }
        }
        
        return yaml.dump(config, default_flow_style=False,
                        sort_keys=False, allow_unicode=True)
    
    def _generate_java_template(self, stages: Optional[List[str]]) -> str:
        """生成Java CI模板"""
        stages = stages or ["build", "test"]
        
        config = {
            "stages": stages,
            "variables": {
                "MAVEN_OPTS": "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"
            },
            "cache": {
                "paths": [".m2/repository"]
            },
            "build": {
                "stage": "build",
                "image": "maven:3.9-eclipse-temurin-17",
                "script": ["mvn compile"]
            },
            "test": {
                "stage": "test",
                "image": "maven:3.9-eclipse-temurin-17",
                "script": ["mvn test"],
                "artifacts": {
                    "reports": {
                        "junit": ["target/surefire-reports/TEST-*.xml"]
                    }
                }
            }
        }
        
        return yaml.dump(config, default_flow_style=False,
                        sort_keys=False, allow_unicode=True)
    
    def _generate_docker_template(self, stages: Optional[List[str]]) -> str:
        """生成Docker CI模板"""
        stages = stages or ["build", "push"]
        
        config = {
            "stages": stages,
            "variables": {
                "DOCKER_IMAGE": "$CI_REGISTRY_IMAGE"
            },
            "build": {
                "stage": "build",
                "image": "docker:latest",
                "services": ["docker:dind"],
                "script": [
                    "docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .",
                    "docker tag $DOCKER_IMAGE:$CI_COMMIT_SHA $DOCKER_IMAGE:latest"
                ]
            },
            "push": {
                "stage": "push",
                "image": "docker:latest",
                "services": ["docker:dind"],
                "before_script": [
                    "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY"
                ],
                "script": [
                    "docker push $DOCKER_IMAGE:$CI_COMMIT_SHA",
                    "docker push $DOCKER_IMAGE:latest"
                ],
                "only": ["main"]
            }
        }
        
        return yaml.dump(config, default_flow_style=False,
                        sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    print("GitLab CI Skill 已加载")
    print("使用方法: from main import GitLabCISkill")
