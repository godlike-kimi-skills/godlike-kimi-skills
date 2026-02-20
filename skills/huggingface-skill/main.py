"""
Hugging Face Skill - Model Management Tool
支持模型下载、Pipeline使用和数据集加载
"""

import os
import json
import logging
from typing import Optional, Union, List, Dict, Any, Callable
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HuggingFaceSkill:
    """Hugging Face模型管理技能"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化HuggingFaceSkill
        
        Args:
            config_path: 配置文件路径，默认使用同级目录的config.json
        """
        self.config = self._load_config(config_path)
        self.cache_dir = self.config.get("cache_dir", "./hf_cache")
        self.device = self._get_device()
        self._pipelines = {}
        self._models = {}
        self._tokenizers = {}
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"HuggingFaceSkill initialized with device: {self.device}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        default_config = {
            "cache_dir": "./hf_cache",
            "default_model": "bert-base-chinese",
            "device": "auto"
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _get_device(self) -> str:
        """获取计算设备"""
        device_config = self.config.get("device", "auto")
        if device_config != "auto":
            return device_config
        
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"
    
    def download_model(self, model_name: str, cache_dir: Optional[str] = None) -> str:
        """
        下载模型到本地缓存
        
        Args:
            model_name: Hugging Face模型名称
            cache_dir: 自定义缓存目录
            
        Returns:
            模型本地路径
        """
        from huggingface_hub import snapshot_download
        
        cache = cache_dir or self.cache_dir
        logger.info(f"Downloading model: {model_name}")
        
        try:
            local_path = snapshot_download(
                repo_id=model_name,
                cache_dir=cache,
                resume_download=self.config.get("resume_download", True),
                local_files_only=self.config.get("local_files_only", False),
                proxies=self.config.get("proxies"),
                use_auth_token=self.config.get("use_auth_token")
            )
            logger.info(f"Model downloaded to: {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            raise
    
    def pipeline_infer(
        self,
        task: str,
        inputs: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        使用Pipeline进行推理
        
        Args:
            task: 任务类型，如 "sentiment-analysis", "ner", "question-answering"
            inputs: 输入文本或列表
            model: 指定模型名称，默认使用config中的默认模型
            **kwargs: 额外参数
            
        Returns:
            推理结果
        """
        from transformers import pipeline
        
        model_name = model or self.config.get("default_model")
        cache_key = f"{task}_{model_name}"
        
        # 缓存pipeline实例
        if cache_key not in self._pipelines:
            logger.info(f"Creating pipeline for task: {task}, model: {model_name}")
            self._pipelines[cache_key] = pipeline(
                task=task,
                model=model_name,
                device=self.device if self.device != "cpu" else -1,
                cache_dir=self.cache_dir,
                trust_remote_code=self.config.get("trust_remote_code", False),
                torch_dtype=self._get_torch_dtype()
            )
        
        pipe = self._pipelines[cache_key]
        
        try:
            result = pipe(inputs, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Pipeline inference failed: {e}")
            raise
    
    def _get_torch_dtype(self):
        """获取torch数据类型"""
        dtype_config = self.config.get("torch_dtype", "auto")
        if dtype_config == "auto":
            return "auto"
        try:
            import torch
            dtype_map = {
                "float16": torch.float16,
                "bfloat16": torch.bfloat16,
                "float32": torch.float32
            }
            return dtype_map.get(dtype_config, "auto")
        except ImportError:
            return "auto"
    
    def load_dataset(
        self,
        dataset_name: str,
        split: Optional[str] = "train",
        subset: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        加载Hugging Face数据集
        
        Args:
            dataset_name: 数据集名称
            split: 数据分割，如 "train", "test", "validation"
            subset: 数据子集名称
            **kwargs: 额外参数
            
        Returns:
            数据集对象
        """
        from datasets import load_dataset as hf_load_dataset
        
        logger.info(f"Loading dataset: {dataset_name}, split: {split}")
        
        try:
            dataset = hf_load_dataset(
                dataset_name,
                subset,
                split=split,
                cache_dir=self.cache_dir,
                trust_remote_code=self.config.get("trust_remote_code", False),
                **kwargs
            )
            logger.info(f"Dataset loaded: {len(dataset)} samples")
            return dataset
        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_name}: {e}")
            raise
    
    def encode_text(
        self,
        tokenizer_name: str,
        text: Union[str, List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Tokenizer编码文本
        
        Args:
            tokenizer_name: Tokenizer名称或路径
            text: 输入文本
            **kwargs: 编码参数
            
        Returns:
            编码后的token字典
        """
        from transformers import AutoTokenizer
        
        if tokenizer_name not in self._tokenizers:
            logger.info(f"Loading tokenizer: {tokenizer_name}")
            self._tokenizers[tokenizer_name] = AutoTokenizer.from_pretrained(
                tokenizer_name,
                cache_dir=self.cache_dir,
                trust_remote_code=self.config.get("trust_remote_code", False)
            )
        
        tokenizer = self._tokenizers[tokenizer_name]
        
        # 设置默认参数
        default_kwargs = {
            "padding": True,
            "truncation": True,
            "return_tensors": "pt",
            "max_length": 512
        }
        default_kwargs.update(kwargs)
        
        try:
            encoded = tokenizer(text, **default_kwargs)
            return encoded
        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            raise
    
    def decode_tokens(
        self,
        tokenizer_name: str,
        tokens: Any,
        **kwargs
    ) -> Union[str, List[str]]:
        """
        解码Token为文本
        
        Args:
            tokenizer_name: Tokenizer名称或路径
            tokens: Token IDs或tensor
            **kwargs: 解码参数
            
        Returns:
            解码后的文本
        """
        from transformers import AutoTokenizer
        
        if tokenizer_name not in self._tokenizers:
            self._tokenizers[tokenizer_name] = AutoTokenizer.from_pretrained(
                tokenizer_name,
                cache_dir=self.cache_dir
            )
        
        tokenizer = self._tokenizers[tokenizer_name]
        
        try:
            decoded = tokenizer.batch_decode(tokens, **kwargs)
            return decoded[0] if len(decoded) == 1 else decoded
        except Exception as e:
            logger.error(f"Token decoding failed: {e}")
            raise
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息字典
        """
        from huggingface_hub import model_info
        
        try:
            info = model_info(model_name)
            return {
                "modelId": info.modelId,
                "author": info.author,
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "pipeline_tag": info.pipeline_tag,
                "siblings": [s.rfilename for s in info.siblings]
            }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            raise
    
    def search_models(
        self,
        query: str,
        limit: int = 10,
        filter_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索模型
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量
            filter_tags: 过滤标签
            
        Returns:
            模型列表
        """
        from huggingface_hub import list_models
        
        try:
            models = list_models(
                search=query,
                limit=limit,
                filter=filter_tags
            )
            return [
                {
                    "modelId": m.modelId,
                    "downloads": m.downloads,
                    "likes": m.likes,
                    "tags": m.tags
                }
                for m in models
            ]
        except Exception as e:
            logger.error(f"Model search failed: {e}")
            raise
    
    def clear_cache(self) -> None:
        """清理缓存"""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info("Cache cleared")
    
    def list_cached_models(self) -> List[str]:
        """
        列出已缓存的模型
        
        Returns:
            模型名称列表
        """
        models = []
        if os.path.exists(self.cache_dir):
            for item in os.listdir(self.cache_dir):
                if item.startswith("models--"):
                    # 解析模型名称
                    model_name = item.replace("models--", "").replace("--", "/")
                    models.append(model_name)
        return models


# 便捷函数接口
def create_skill(config_path: Optional[str] = None) -> HuggingFaceSkill:
    """创建Skill实例"""
    return HuggingFaceSkill(config_path)


def quick_infer(task: str, text: str, model: Optional[str] = None) -> Any:
    """快速推理接口"""
    skill = HuggingFaceSkill()
    return skill.pipeline_infer(task, text, model)


if __name__ == "__main__":
    # 简单测试
    skill = HuggingFaceSkill()
    print(f"Device: {skill.device}")
    print(f"Cache dir: {skill.cache_dir}")
    print("HuggingFaceSkill ready to use!")
