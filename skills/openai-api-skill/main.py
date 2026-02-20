"""
OpenAI API Skill - API Calling Tool
支持Chat/Completion API、Embedding和图像生成
"""

import os
import json
import logging
import time
from typing import Optional, Union, List, Dict, Any, Tuple, BinaryIO
from pathlib import Path
import base64
import io

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入openai
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. Install with: pip install openai")


class OpenAISkill:
    """OpenAI API调用技能"""
    
    def __init__(self, config_path: Optional[str] = None, api_key: Optional[str] = None):
        """
        初始化OpenAISkill
        
        Args:
            config_path: 配置文件路径
            api_key: API密钥（优先于配置文件）
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
        
        self.config = self._load_config(config_path)
        
        # 获取API密钥
        self.api_key = api_key or self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("API key not found. Set OPENAI_API_KEY environment variable or provide in config.")
        
        # 初始化客户端
        self.client = self._init_client()
        
        # 设置默认参数
        self.default_model = self.config.get("default_model", "gpt-3.5-turbo")
        self.default_temperature = self.config.get("default_temperature", 0.7)
        self.default_max_tokens = self.config.get("default_max_tokens", 2048)
        self.embedding_model = self.config.get("embedding_model", "text-embedding-ada-002")
        self.image_model = self.config.get("image_model", "dall-e-3")
        self.audio_model = self.config.get("audio_model", "whisper-1")
        
        logger.info(f"OpenAISkill initialized with model: {self.default_model}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        default_config = {
            "api_key": None,
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-3.5-turbo",
            "default_temperature": 0.7,
            "default_max_tokens": 2048
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _init_client(self) -> Optional[OpenAI]:
        """初始化OpenAI客户端"""
        if not self.api_key:
            return None
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.config.get("base_url"),
                timeout=self.config.get("timeout", 60.0),
                max_retries=self.config.get("max_retries", 3),
                organization=self.config.get("organization"),
                project=self.config.get("project")
            )
            return client
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        对话接口 (Chat Completions API)
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 采样温度 (0-2)
            max_tokens: 最大生成token数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            stop: 停止序列
            **kwargs: 额外参数
            
        Returns:
            API响应结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        top_p = top_p if top_p is not None else self.config.get("default_top_p", 1.0)
        frequency_penalty = frequency_penalty if frequency_penalty is not None else self.config.get("default_frequency_penalty", 0.0)
        presence_penalty = presence_penalty if presence_penalty is not None else self.config.get("default_presence_penalty", 0.0)
        
        try:
            logger.info(f"Sending chat request to {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                **kwargs
            )
            
            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "id": response.id
            }
            
            logger.info(f"Chat response received. Tokens used: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"Chat API request failed: {e}")
            raise
    
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本补全接口 (Legacy Completions API)
        
        Args:
            prompt: 提示文本
            model: 模型名称
            temperature: 采样温度
            max_tokens: 最大生成token数
            **kwargs: 额外参数
            
        Returns:
            API响应结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or "gpt-3.5-turbo-instruct"
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        try:
            logger.info(f"Sending completion request to {model}")
            
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            result = {
                "text": response.choices[0].text,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
            }
            
            logger.info(f"Completion response received. Tokens used: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"Completion API request failed: {e}")
            raise
    
    def simple_chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简单对话接口
        
        Args:
            message: 用户消息
            system_prompt: 系统提示
            **kwargs: 额外参数
            
        Returns:
            助手回复内容
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        response = self.chat(messages, **kwargs)
        return response["content"]
    
    def create_embedding(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本或文本列表
            model: 嵌入模型名称
            **kwargs: 额外参数
            
        Returns:
            嵌入向量结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or self.embedding_model
        
        # 确保text是列表
        if isinstance(text, str):
            text = [text]
        
        try:
            logger.info(f"Creating embeddings with {model}")
            
            response = self.client.embeddings.create(
                model=model,
                input=text,
                **kwargs
            )
            
            embeddings = [item.embedding for item in response.data]
            
            result = {
                "embeddings": embeddings if len(embeddings) > 1 else embeddings[0],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info(f"Embeddings created. Tokens used: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"Embedding API request failed: {e}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        style: Optional[str] = None,
        model: Optional[str] = None,
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图像 (DALL-E API)
        
        Args:
            prompt: 图像描述
            size: 图像尺寸 (1024x1024/1024x1792/1792x1024)
            quality: 图像质量 (standard/hd)
            style: 图像风格 (vivid/natural)
            model: 模型名称
            n: 生成数量
            **kwargs: 额外参数
            
        Returns:
            图像生成结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or self.image_model
        size = size or self.config.get("image_size", "1024x1024")
        quality = quality or self.config.get("image_quality", "standard")
        style = style or self.config.get("image_style", "vivid")
        
        try:
            logger.info(f"Generating image with {model}")
            
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=n,
                **kwargs
            )
            
            images = []
            for img_data in response.data:
                image_info = {
                    "url": img_data.url,
                    "revised_prompt": img_data.revised_prompt
                }
                images.append(image_info)
            
            result = {
                "images": images if len(images) > 1 else images[0],
                "created": response.created
            }
            
            logger.info(f"Image generation completed. Created: {response.created}")
            return result
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def edit_image(
        self,
        image_path: str,
        mask_path: Optional[str],
        prompt: str,
        size: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        编辑图像
        
        Args:
            image_path: 原图路径
            mask_path: 遮罩路径（可选）
            prompt: 编辑描述
            size: 图像尺寸
            **kwargs: 额外参数
            
        Returns:
            编辑结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        size = size or self.config.get("image_size", "1024x1024")
        
        try:
            with open(image_path, "rb") as image_file:
                mask_file = open(mask_path, "rb") if mask_path else None
                
                response = self.client.images.edit(
                    image=image_file,
                    mask=mask_file,
                    prompt=prompt,
                    size=size,
                    **kwargs
                )
                
                if mask_file:
                    mask_file.close()
            
            result = {
                "url": response.data[0].url,
                "created": response.created
            }
            
            logger.info("Image edit completed")
            return result
            
        except Exception as e:
            logger.error(f"Image edit failed: {e}")
            raise
    
    def transcribe_audio(
        self,
        audio_file: Union[str, BinaryIO],
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        **kwargs
    ) -> Dict[str, Any]:
        """
        语音转文字 (Whisper API)
        
        Args:
            audio_file: 音频文件路径或文件对象
            model: 模型名称
            language: 音频语言
            prompt: 提示文本
            response_format: 响应格式
            **kwargs: 额外参数
            
        Returns:
            转录结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or self.audio_model
        
        try:
            logger.info(f"Transcribing audio with {model}")
            
            # 处理文件路径
            if isinstance(audio_file, str):
                audio_file = open(audio_file, "rb")
                should_close = True
            else:
                should_close = False
            
            response = self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language=language,
                prompt=prompt,
                response_format=response_format,
                **kwargs
            )
            
            if should_close:
                audio_file.close()
            
            result = {
                "text": response.text if hasattr(response, 'text') else str(response),
                "language": language
            }
            
            logger.info("Audio transcription completed")
            return result
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise
    
    def translate_audio(
        self,
        audio_file: Union[str, BinaryIO],
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        语音翻译 (Whisper API)
        
        Args:
            audio_file: 音频文件路径或文件对象
            model: 模型名称
            prompt: 提示文本
            **kwargs: 额外参数
            
        Returns:
            翻译结果
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        model = model or self.audio_model
        
        try:
            logger.info(f"Translating audio with {model}")
            
            if isinstance(audio_file, str):
                audio_file = open(audio_file, "rb")
                should_close = True
            else:
                should_close = False
            
            response = self.client.audio.translations.create(
                model=model,
                file=audio_file,
                prompt=prompt,
                **kwargs
            )
            
            if should_close:
                audio_file.close()
            
            result = {
                "text": response.text if hasattr(response, 'text') else str(response)
            }
            
            logger.info("Audio translation completed")
            return result
            
        except Exception as e:
            logger.error(f"Audio translation failed: {e}")
            raise
    
    def create_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        response_format: str = "mp3",
        speed: float = 1.0,
        **kwargs
    ) -> bytes:
        """
        文本转语音 (TTS API)
        
        Args:
            text: 要转换的文本
            voice: 语音类型 (alloy/echo/fable/onyx/nova/shimmer)
            model: 模型名称
            response_format: 输出格式
            speed: 语速
            **kwargs: 额外参数
            
        Returns:
            音频字节数据
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        try:
            logger.info(f"Creating speech with voice: {voice}")
            
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=response_format,
                speed=speed,
                **kwargs
            )
            
            audio_data = response.content
            logger.info(f"Speech created. Size: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"Speech creation failed: {e}")
            raise
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        计算文本token数量
        
        Args:
            text: 输入文本
            model: 模型名称
            
        Returns:
            Token数量
        """
        try:
            import tiktoken
            model = model or self.default_model
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except ImportError:
            # 简单估算
            return len(text.split()) * 1.3
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(text.split()) * 1.3
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        估算API调用成本
        
        Args:
            prompt_tokens: 提示token数
            completion_tokens: 生成token数
            model: 模型名称
            
        Returns:
            估算成本（美元）
        """
        model = model or self.default_model
        
        # 价格表（每1000 tokens）
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0},
            "dall-e-3": {"standard_1024": 0.04, "hd_1024": 0.08}
        }
        
        # 找到匹配的模型价格
        model_pricing = None
        for key in pricing:
            if key in model:
                model_pricing = pricing[key]
                break
        
        if not model_pricing:
            model_pricing = pricing["gpt-3.5-turbo"]  # 默认价格
        
        input_cost = (prompt_tokens / 1000) * model_pricing.get("input", 0)
        output_cost = (completion_tokens / 1000) * model_pricing.get("output", 0)
        
        return input_cost + output_cost


# 便捷函数接口
def create_skill(config_path: Optional[str] = None, api_key: Optional[str] = None) -> OpenAISkill:
    """创建Skill实例"""
    return OpenAISkill(config_path, api_key)


def quick_chat(message: str, api_key: Optional[str] = None, **kwargs) -> str:
    """快速对话接口"""
    skill = OpenAISkill(api_key=api_key)
    return skill.simple_chat(message, **kwargs)


if __name__ == "__main__":
    skill = OpenAISkill()
    print(f"Default model: {skill.default_model}")
    print("OpenAISkill ready to use!")
