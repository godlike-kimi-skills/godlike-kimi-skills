#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HuggingFace Hub CLI Tool - 简化模型和数据集管理
Author: Kimi Code CLI | Version: 1.0.0 | License: MIT
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from huggingface_hub import (
        HfApi, HfFolder, snapshot_download, list_models, list_datasets,
        model_info, dataset_info, whoami, login as hf_login, logout as hf_logout
    )
    from huggingface_hub.utils import RepositoryNotFoundError
except ImportError:
    print("❌ 请先安装: pip install huggingface_hub>=0.19.0")
    sys.exit(1)

DEFAULT_CACHE = Path.home() / ".cache" / "huggingface"


class HuggingFaceCLI:
    """HuggingFace CLI主类"""
    
    def __init__(self, token: Optional[str] = None, cache_dir: Optional[str] = None):
        self.api = HfApi(token=token)
        self.token = token or self._get_token()
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE
    
    def _get_token(self) -> Optional[str]:
        try:
            return HfFolder.get_token()
        except Exception:
            return None
    
    def _print(self, icon: str, msg: str):
        print(f"{icon} {msg}")
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def _get_dir_size(self, path: str) -> int:
        return sum(os.path.getsize(os.path.join(dp, f)) 
                   for dp, dn, fn in os.walk(path) for f in fn)
    
    # ===== Token管理 =====
    
    def login(self, token: str) -> bool:
        try:
            hf_login(token=token)
            self.token, self.api = token, HfApi(token=token)
            user = whoami(token=token)
            self._print("✅", f"登录成功! 欢迎, {user.get('name', 'User')}")
            return True
        except Exception as e:
            self._print("❌", f"登录失败: {e}")
            return False
    
    def logout(self) -> bool:
        try:
            hf_logout()
            self.token, self.api = None, HfApi()
            self._print("✅", "已登出HuggingFace")
            return True
        except Exception as e:
            self._print("❌", f"登出失败: {e}")
            return False
    
    # ===== 搜索功能 =====
    
    def search_models(self, query: str, limit: int = 10) -> List[Dict]:
        print(f"\n{'='*50}\n  🔍 搜索模型: '{query}'\n{'='*50}\n")
        try:
            models = list(list_models(search=query, limit=limit, fetch_config=False))
            if not models:
                self._print("ℹ️", "未找到匹配的模型")
                return []
            
            results = []
            print(f"找到 {len(models)} 个模型:\n")
            for i, m in enumerate(models, 1):
                info = {"id": m.modelId, "downloads": m.downloads or 0, 
                        "likes": m.likes or 0, "tags": m.tags or [],
                        "task": m.pipeline_tag or "N/A"}
                results.append(info)
                print(f"  {i}. {m.modelId}")
                print(f"     📥 {info['downloads']:,} | ❤️ {info['likes']:,} | 🔧 {info['task']}")
                if info['tags']:
                    print(f"     🏷️ {', '.join(info['tags'][:5])}")
                print()
            return results
        except Exception as e:
            self._print("❌", f"搜索失败: {e}")
            return []
    
    def search_datasets(self, query: str, limit: int = 10) -> List[Dict]:
        print(f"\n{'='*50}\n  🔍 搜索数据集: '{query}'\n{'='*50}\n")
        try:
            datasets = list(list_datasets(search=query, limit=limit))
            if not datasets:
                self._print("ℹ️", "未找到匹配的数据集")
                return []
            
            results = []
            print(f"找到 {len(datasets)} 个数据集:\n")
            for i, d in enumerate(datasets, 1):
                info = {"id": d.id, "downloads": d.downloads or 0, "tags": d.tags or []}
                results.append(info)
                print(f"  {i}. {d.id}")
                print(f"     📥 {info['downloads']:,}")
                if info['tags']:
                    print(f"     🏷️ {', '.join(info['tags'][:5])}")
                print()
            return results
        except Exception as e:
            self._print("❌", f"搜索失败: {e}")
            return []
    
    # ===== 信息查询 =====
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        print(f"\n{'='*50}\n  📋 模型信息: {model_id}\n{'='*50}\n")
        try:
            info = model_info(model_id, token=self.token)
            files = [f.rfilename for f in info.siblings] if info.siblings else []
            result = {"id": info.id, "sha": info.sha[:16] if info.sha else "N/A",
                      "downloads": info.downloads, "likes": info.likes,
                      "task": info.pipeline_tag, "tags": info.tags or [],
                      "files": files, "created": str(info.created_at)[:10],
                      "modified": str(info.last_modified)[:10]}
            
            print(f"  🆔 {result['id']}")
            print(f"  🔢 {result['sha']}...")
            print(f"  📥 {result['downloads']:,} | ❤️ {result['likes']:,}")
            print(f"  🔧 {result['task'] or 'N/A'}")
            print(f"  📅 {result['created']} | 📝 {result['modified']}")
            print(f"\n  🏷️ 标签: {', '.join(result['tags'][:8]) if result['tags'] else 'N/A'}")
            print(f"\n  📁 文件 ({len(files)} 个):")
            for f in files[:15]:
                print(f"     - {f}")
            if len(files) > 15:
                print(f"     ... 还有 {len(files)-15} 个")
            return result
        except RepositoryNotFoundError:
            self._print("❌", f"模型不存在: {model_id}")
            return None
        except Exception as e:
            self._print("❌", f"获取失败: {e}")
            return None
    
    def get_dataset_info(self, dataset_id: str) -> Optional[Dict]:
        print(f"\n{'='*50}\n  📋 数据集信息: {dataset_id}\n{'='*50}\n")
        try:
            info = dataset_info(dataset_id, token=self.token)
            files = [f.rfilename for f in info.siblings] if info.siblings else []
            result = {"id": info.id, "sha": info.sha[:16] if info.sha else "N/A",
                      "downloads": info.downloads, "tags": info.tags or [],
                      "files": files, "modified": str(info.last_modified)[:10]}
            
            print(f"  🆔 {result['id']}")
            print(f"  🔢 {result['sha']}...")
            print(f"  📥 {result['downloads']:,}")
            print(f"  📝 {result['modified']}")
            print(f"\n  🏷️ 标签: {', '.join(result['tags'][:8]) if result['tags'] else 'N/A'}")
            print(f"\n  📁 文件 ({len(files)} 个):")
            for f in files[:15]:
                print(f"     - {f}")
            if len(files) > 15:
                print(f"     ... 还有 {len(files)-15} 个")
            return result
        except RepositoryNotFoundError:
            self._print("❌", f"数据集不存在: {dataset_id}")
            return None
        except Exception as e:
            self._print("❌", f"获取失败: {e}")
            return None
    
    # ===== 下载功能 =====
    
    def download_model(self, model_id: str, local_dir: Optional[str] = None,
                       include: Optional[List[str]] = None, exclude: Optional[List[str]] = None,
                       resume: bool = True) -> Optional[str]:
        print(f"\n{'='*50}\n  ⬇️  下载模型: {model_id}\n{'='*50}\n")
        target = Path(local_dir) if local_dir else self.cache_dir / "hub" / model_id.replace("/", "--")
        
        try:
            self._print("ℹ️", f"目标: {target}")
            path = snapshot_download(repo_id=model_id, repo_type="model",
                                     local_dir=str(target) if local_dir else None,
                                     cache_dir=self.cache_dir if not local_dir else None,
                                     allow_patterns=include, ignore_patterns=exclude,
                                     resume_download=resume, token=self.token)
            self._print("✅", "下载完成!")
            self._print("ℹ️", f"位置: {path}")
            self._print("ℹ️", f"大小: {self._format_size(self._get_dir_size(path))}")
            return path
        except RepositoryNotFoundError:
            self._print("❌", f"模型不存在: {model_id}")
            return None
        except Exception as e:
            self._print("❌", f"下载失败: {e}")
            return None
    
    def download_dataset(self, dataset_id: str, local_dir: Optional[str] = None,
                         include: Optional[List[str]] = None, exclude: Optional[List[str]] = None,
                         resume: bool = True) -> Optional[str]:
        print(f"\n{'='*50}\n  ⬇️  下载数据集: {dataset_id}\n{'='*50}\n")
        target = Path(local_dir) if local_dir else self.cache_dir / "datasets" / dataset_id.replace("/", "--")
        
        try:
            self._print("ℹ️", f"目标: {target}")
            path = snapshot_download(repo_id=dataset_id, repo_type="dataset",
                                     local_dir=str(target) if local_dir else None,
                                     cache_dir=self.cache_dir if not local_dir else None,
                                     allow_patterns=include, ignore_patterns=exclude,
                                     resume_download=resume, token=self.token)
            self._print("✅", "下载完成!")
            self._print("ℹ️", f"位置: {path}")
            self._print("ℹ️", f"大小: {self._format_size(self._get_dir_size(path))}")
            return path
        except RepositoryNotFoundError:
            self._print("❌", f"数据集不存在: {dataset_id}")
            return None
        except Exception as e:
            self._print("❌", f"下载失败: {e}")
            return None
    
    # ===== 缓存管理 =====
    
    def cache_info(self) -> Dict[str, Any]:
        print(f"\n{'='*50}\n  💾 缓存信息\n{'='*50}\n")
        hub_dir = self.cache_dir / "hub"
        ds_dir = self.cache_dir / "datasets"
        
        info = {"cache_dir": str(self.cache_dir), "hub_dir": str(hub_dir),
                "ds_dir": str(ds_dir), "token_exists": (Path.home() / ".huggingface" / "token").exists()}
        
        print(f"  📁 根目录: {info['cache_dir']}")
        print(f"  🤖 模型: {info['hub_dir']}")
        print(f"  📊 数据集: {info['ds_dir']}")
        print(f"  🔑 Token: {'存在' if info['token_exists'] else '不存在'}")
        
        hub_size = self._get_dir_size(str(hub_dir)) if hub_dir.exists() else 0
        ds_size = self._get_dir_size(str(ds_dir)) if ds_dir.exists() else 0
        info.update({"hub_size": hub_size, "ds_size": ds_size, "total": hub_size + ds_size})
        
        print(f"\n  💽 空间使用:")
        print(f"     模型: {self._format_size(hub_size)}")
        print(f"     数据集: {self._format_size(ds_size)}")
        print(f"     总计: {self._format_size(info['total'])}")
        return info
    
    def clean_cache(self, force: bool = False) -> bool:
        print(f"\n{'='*50}\n  🧹 清理缓存\n{'='*50}\n")
        if not force:
            self._print("⚠️", "请使用 --force 确认清理")
            return False
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            self._print("✅", "缓存已清理")
            return True
        except Exception as e:
            self._print("❌", f"清理失败: {e}")
            return False
    
    def list_local(self) -> List[str]:
        print(f"\n{'='*50}\n  📚 本地模型\n{'='*50}\n")
        hub_dir = self.cache_dir / "hub"
        if not hub_dir.exists():
            self._print("ℹ️", "本地没有模型")
            return []
        
        models = [item.name.replace("--", "/") for item in hub_dir.iterdir() if item.is_dir()]
        if models:
            print(f"共 {len(models)} 个模型:\n")
            for i, m in enumerate(sorted(models), 1):
                size = self._get_dir_size(str(hub_dir / m.replace("/", "--")))
                print(f"  {i}. {m} ({self._format_size(size)})")
        else:
            self._print("ℹ️", "本地没有模型")
        return models


def main():
    parser = argparse.ArgumentParser(description="HuggingFace Hub CLI", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""示例:
  python main.py search -q bert-base -l 5
  python main.py download -m bert-base-chinese --local-dir ./models
  python main.py info -m bert-base-chinese
  python main.py login -t your_token""")
    
    parser.add_argument("action", choices=["search", "download", "info", "login", "logout", 
                        "cache", "list", "dataset-search", "dataset-download", "dataset-info"],
                        help="操作类型")
    parser.add_argument("-q", "--query", help="搜索关键词")
    parser.add_argument("-l", "--limit", type=int, default=10, help="结果限制")
    parser.add_argument("-m", "--model", help="模型ID")
    parser.add_argument("-d", "--dataset", help="数据集ID")
    parser.add_argument("-t", "--token", help="访问令牌")
    parser.add_argument("--local-dir", help="本地目录")
    parser.add_argument("--cache-dir", help="缓存目录")
    parser.add_argument("--include", nargs="+", help="包含模式")
    parser.add_argument("--exclude", nargs="+", help="排除模式")
    parser.add_argument("--resume", action="store_true", default=True, help="断点续传")
    parser.add_argument("--force", action="store_true", help="强制操作")
    
    args = parser.parse_args()
    cli = HuggingFaceCLI(token=args.token, cache_dir=args.cache_dir)
    
    if args.action == "search":
        if not args.query:
            print("❌ 请提供: --query <关键词>"); sys.exit(1)
        cli.search_models(args.query, args.limit)
    elif args.action == "dataset-search":
        if not args.query:
            print("❌ 请提供: --query <关键词>"); sys.exit(1)
        cli.search_datasets(args.query, args.limit)
    elif args.action == "download":
        if not args.model:
            print("❌ 请提供: --model <模型ID>"); sys.exit(1)
        cli.download_model(args.model, args.local_dir, args.include, args.exclude, args.resume)
    elif args.action == "dataset-download":
        if not args.dataset:
            print("❌ 请提供: --dataset <数据集ID>"); sys.exit(1)
        cli.download_dataset(args.dataset, args.local_dir, args.include, args.exclude, args.resume)
    elif args.action == "info":
        if not args.model:
            print("❌ 请提供: --model <模型ID>"); sys.exit(1)
        cli.get_model_info(args.model)
    elif args.action == "dataset-info":
        if not args.dataset:
            print("❌ 请提供: --dataset <数据集ID>"); sys.exit(1)
        cli.get_dataset_info(args.dataset)
    elif args.action == "login":
        if not args.token:
            print("❌ 请提供: --token <token>"); sys.exit(1)
        cli.login(args.token)
    elif args.action == "logout":
        cli.logout()
    elif args.action == "cache":
        cli.cache_info()
    elif args.action == "list":
        cli.list_local()


if __name__ == "__main__":
    main()
