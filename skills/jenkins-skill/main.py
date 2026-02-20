"""
Jenkins Skill - 流水线管理

功能：
- Job创建、配置、删除
- Build触发和状态监控
- Pipeline脚本配置
- 节点管理
- 凭据管理
- Build日志获取
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

import jenkins
import requests
from requests.auth import HTTPBasicAuth


class BuildStatus(Enum):
    """Build状态枚举"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNSTABLE = "UNSTABLE"
    ABORTED = "ABORTED"
    NOT_BUILT = "NOT_BUILT"
    BUILDING = "BUILDING"
    QUEUED = "QUEUED"


class JenkinsSkill:
    """Jenkins流水线管理类"""
    
    def __init__(self, url: Optional[str] = None, 
                 username: Optional[str] = None,
                 token: Optional[str] = None,
                 timeout: int = 30):
        """
        初始化Jenkins Skill
        
        Args:
            url: Jenkins URL
            username: Jenkins用户名
            token: Jenkins API Token
            timeout: 请求超时时间
        """
        self.url = url or os.environ.get("JENKINS_URL", "")
        self.username = username or os.environ.get("JENKINS_USER", "")
        self.token = token or os.environ.get("JENKINS_TOKEN", "")
        self.timeout = timeout
        
        if not all([self.url, self.username, self.token]):
            raise ValueError("Jenkins URL, username and token are required")
        
        # 移除URL末尾的斜杠
        self.url = self.url.rstrip("/")
        
        # 初始化Jenkins服务器连接
        self.server = jenkins.Jenkins(
            self.url, 
            username=self.username, 
            password=self.token,
            timeout=timeout
        )
        
        # 测试连接
        try:
            self.server.get_whoami()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Jenkins: {e}")
    
    def _create_response(self, success: bool, data: Any = None,
                         error: Optional[str] = None) -> Dict:
        """创建标准响应对象"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_version(self) -> Dict:
        """
        获取Jenkins版本信息
        
        Returns:
            标准响应对象
        """
        try:
            version = self.server.get_version()
            return self._create_response(True, data={"version": version})
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def create_job(self, name: str, job_type: str = "pipeline",
                   config: Optional[Dict] = None) -> Dict:
        """
        创建Jenkins Job
        
        Args:
            name: Job名称
            job_type: Job类型 (pipeline, freestyle, multibranch)
            config: Job配置
            
        Returns:
            标准响应对象
        """
        try:
            if config is None:
                config = {}
            
            xml_config = self._generate_job_xml(job_type, config)
            
            self.server.create_job(name, xml_config)
            
            return self._create_response(True, data={
                "name": name,
                "type": job_type,
                "url": f"{self.url}/job/{name}"
            })
            
        except jenkins.JenkinsException as e:
            if "already exists" in str(e):
                return self._create_response(False, error=f"Job '{name}' already exists")
            return self._create_response(False, error=str(e))
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _generate_job_xml(self, job_type: str, config: Dict) -> str:
        """生成Job的XML配置"""
        
        if job_type == "pipeline":
            script = config.get("script", "pipeline { agent any; stages { stage('Build') { steps { echo 'Building...' } } } }")
            return f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{config.get('description', '')}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""
        
        elif job_type == "freestyle":
            return f"""<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>{config.get('description', '')}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>"""
        
        else:
            raise ValueError(f"Unsupported job type: {job_type}")
    
    def delete_job(self, name: str) -> Dict:
        """
        删除Jenkins Job
        
        Args:
            name: Job名称
            
        Returns:
            标准响应对象
        """
        try:
            self.server.delete_job(name)
            return self._create_response(True, data={"deleted": name})
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_job_info(self, name: str) -> Dict:
        """
        获取Job信息
        
        Args:
            name: Job名称
            
        Returns:
            标准响应对象
        """
        try:
            info = self.server.get_job_info(name)
            return self._create_response(True, data={
                "name": info.get("name"),
                "url": info.get("url"),
                "buildable": info.get("buildable"),
                "inQueue": info.get("inQueue"),
                "lastBuild": info.get("lastBuild"),
                "lastSuccessfulBuild": info.get("lastSuccessfulBuild"),
                "lastFailedBuild": info.get("lastFailedBuild"),
                "healthReport": info.get("healthReport", [])
            })
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_jobs(self, folder: Optional[str] = None) -> Dict:
        """
        列出所有Jobs
        
        Args:
            folder: 文件夹路径（可选）
            
        Returns:
            标准响应对象
        """
        try:
            if folder:
                jobs = self.server.get_jobs(folder)
            else:
                jobs = self.server.get_jobs()
            
            job_list = []
            for job in jobs:
                job_list.append({
                    "name": job.get("name"),
                    "url": job.get("url"),
                    "color": job.get("color", "notbuilt")
                })
            
            return self._create_response(True, data=job_list)
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def update_job_config(self, name: str, config: Dict) -> Dict:
        """
        更新Job配置
        
        Args:
            name: Job名称
            config: 新配置
            
        Returns:
            标准响应对象
        """
        try:
            # 获取当前配置
            current_xml = self.server.get_job_config(name)
            
            # 根据config生成新XML
            new_xml = self._generate_job_xml("pipeline", config)
            
            self.server.reconfig_job(name, new_xml)
            
            return self._create_response(True, data={"updated": name})
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def trigger_build(self, name: str, parameters: Optional[Dict] = None,
                     block: bool = False) -> Dict:
        """
        触发Build
        
        Args:
            name: Job名称
            parameters: Build参数
            block: 是否等待Build完成
            
        Returns:
            标准响应对象
        """
        try:
            if parameters:
                # 参数化构建
                queue_item = self.server.build_job(name, parameters)
            else:
                queue_item = self.server.build_job(name)
            
            result = {
                "job": name,
                "queue_item": queue_item,
                "parameters": parameters or {}
            }
            
            if block:
                # 等待Build完成
                build_info = self._wait_for_build_completion(name, queue_item)
                result["build_info"] = build_info
            
            return self._create_response(True, data=result)
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _wait_for_build_completion(self, job_name: str, queue_id: int,
                                   timeout: int = 3600) -> Dict:
        """等待Build完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 获取队列信息
                queue_info = self.server.get_queue_item(queue_id)
                
                if queue_info.get("executable"):
                    build_number = queue_info["executable"]["number"]
                    
                    # 等待Build完成
                    while time.time() - start_time < timeout:
                        build_info = self.server.get_build_info(job_name, build_number)
                        if not build_info.get("building", False):
                            return build_info
                        time.sleep(5)
                    
                    raise TimeoutError("Build timeout")
                
                time.sleep(2)
                
            except Exception:
                time.sleep(2)
        
        raise TimeoutError("Queue timeout")
    
    def get_build_info(self, job_name: str, build_number: int) -> Dict:
        """
        获取Build信息
        
        Args:
            job_name: Job名称
            build_number: Build编号
            
        Returns:
            标准响应对象
        """
        try:
            info = self.server.get_build_info(job_name, build_number)
            return self._create_response(True, data={
                "number": info.get("number"),
                "url": info.get("url"),
                "building": info.get("building"),
                "result": info.get("result"),
                "timestamp": info.get("timestamp"),
                "duration": info.get("duration"),
                "estimatedDuration": info.get("estimatedDuration"),
                "culprits": [c.get("fullName") for c in info.get("culprits", [])]
            })
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_build_logs(self, job_name: str, build_number: int) -> Dict:
        """
        获取Build日志
        
        Args:
            job_name: Job名称
            build_number: Build编号
            
        Returns:
            标准响应对象
        """
        try:
            logs = self.server.get_build_console_output(job_name, build_number)
            return self._create_response(True, data={
                "job": job_name,
                "build_number": build_number,
                "logs": logs
            })
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def stop_build(self, job_name: str, build_number: int) -> Dict:
        """
        停止Build
        
        Args:
            job_name: Job名称
            build_number: Build编号
            
        Returns:
            标准响应对象
        """
        try:
            self.server.stop_build(job_name, build_number)
            return self._create_response(True, data={
                "stopped": True,
                "job": job_name,
                "build_number": build_number
            })
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_builds(self, job_name: str, limit: int = 10) -> Dict:
        """
        列出Build历史
        
        Args:
            job_name: Job名称
            limit: 返回数量限制
            
        Returns:
            标准响应对象
        """
        try:
            job_info = self.server.get_job_info(job_name)
            builds = job_info.get("builds", [])[:limit]
            
            build_list = []
            for build in builds:
                build_info = self.server.get_build_info(job_name, build["number"])
                build_list.append({
                    "number": build_info["number"],
                    "result": build_info.get("result"),
                    "timestamp": build_info.get("timestamp"),
                    "duration": build_info.get("duration"),
                    "building": build_info.get("building")
                })
            
            return self._create_response(True, data=build_list)
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def list_nodes(self) -> Dict:
        """
        列出所有节点
        
        Returns:
            标准响应对象
        """
        try:
            nodes = self.server.get_nodes()
            node_list = []
            
            for node in nodes:
                node_name = node.get("name", "master")
                try:
                    node_info = self.server.get_node_info(node_name)
                    node_list.append({
                        "name": node_name,
                        "offline": node_info.get("offline", False),
                        "numExecutors": node_info.get("numExecutors", 0),
                        "idle": len([e for e in node_info.get("executors", []) if e.get("idle", True)]),
                        "labels": [l.get("name") for l in node_info.get("assignedLabels", [])]
                    })
                except:
                    node_list.append({
                        "name": node_name,
                        "offline": True,
                        "error": "Failed to get info"
                    })
            
            return self._create_response(True, data=node_list)
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def get_queue(self) -> Dict:
        """
        获取构建队列
        
        Returns:
            标准响应对象
        """
        try:
            queue = self.server.get_queue_info()
            queue_list = []
            
            for item in queue:
                queue_list.append({
                    "id": item.get("id"),
                    "inQueueSince": item.get("inQueueSince"),
                    "why": item.get("why"),
                    "task": item.get("task", {}).get("name")
                })
            
            return self._create_response(True, data=queue_list)
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def generate_pipeline_template(self, template_type: str = "ci",
                                   language: str = "python") -> Dict:
        """
        生成Pipeline模板
        
        Args:
            template_type: 模板类型 (ci, cd, test, docker)
            language: 编程语言
            
        Returns:
            标准响应对象
        """
        try:
            templates = {
                "ci": self._generate_ci_pipeline(language),
                "cd": self._generate_cd_pipeline(),
                "test": self._generate_test_pipeline(language),
                "docker": self._generate_docker_pipeline()
            }
            
            template = templates.get(template_type, templates["ci"])
            
            return self._create_response(True, data={
                "template_type": template_type,
                "language": language,
                "script": template
            })
            
        except Exception as e:
            return self._create_response(False, error=str(e))
    
    def _generate_ci_pipeline(self, language: str) -> str:
        """生成CI Pipeline模板"""
        
        setup_steps = {
            "python": """
        stage('Setup') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }""",
            "nodejs": """
        stage('Setup') {
            steps {
                sh 'npm ci'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }""",
            "java": """
        stage('Build') {
            steps {
                sh 'mvn clean compile'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }"""
        }
        
        steps = setup_steps.get(language, setup_steps["python"])
        
        return f"""pipeline {{
    agent any
    
    stages {{{steps}
        stage('Build') {{
            steps {{
                echo 'Building project...'
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
    }}
}}"""
    
    def _generate_cd_pipeline(self) -> str:
        """生成CD Pipeline模板"""
        return """pipeline {
    agent any
    
    environment {
        DEPLOY_ENV = 'production'
    }
    
    stages {
        stage('Deploy') {
            steps {
                echo "Deploying to ${DEPLOY_ENV}"
                sh './deploy.sh'
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}"""
    
    def _generate_test_pipeline(self, language: str) -> str:
        """生成测试Pipeline模板"""
        return self._generate_ci_pipeline(language)
    
    def _generate_docker_pipeline(self) -> str:
        """生成Docker Pipeline模板"""
        return """pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub') {
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                    }
                }
            }
        }
    }
}"""


if __name__ == "__main__":
    print("Jenkins Skill 已加载")
    print("使用方法: from main import JenkinsSkill")
