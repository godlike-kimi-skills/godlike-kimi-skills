#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElevenLabs Skill - ElevenLabs TTS语音合成工具
支持文本转语音、声音克隆和多语言
"""

import os
import re
import json
from typing import List, Dict, Optional, BinaryIO, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

try:
    from elevenlabs import ElevenLabs, VoiceSettings
except ImportError:
    ElevenLabs = None
    VoiceSettings = None


@dataclass
class VoiceInfo:
    """声音信息数据类"""
    voice_id: str
    name: str
    category: str = "premade"
    description: str = ""
    labels: Dict[str, str] = None
    preview_url: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


@dataclass
class TTSResult:
    """TTS结果数据类"""
    text: str
    voice_id: str
    voice_name: str
    model: str
    audio_data: bytes = None
    file_path: str = ""
    duration_estimate: float = 0.0
    
    def save(self, path: str) -> str:
        """保存音频到文件"""
        if self.audio_data:
            Path(path).write_bytes(self.audio_data)
            self.file_path = path
            return path
        return ""


class ElevenLabsManager:
    """ElevenLabs TTS管理器"""
    
    def __init__(self, api_key: Optional[str] = None):
        if ElevenLabs is None:
            raise ImportError("请先安装 elevenlabs: pip install elevenlabs")
        
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供ElevenLabs API密钥")
        
        self.client = ElevenLabs(api_key=self.api_key)
        self.default_voice_id = os.getenv("DEFAULT_VOICE_ID", "Rachel")
        self.default_model = os.getenv("DEFAULT_MODEL", "eleven_multilingual_v2")
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./audio_output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_voices(self, show_all: bool = False) -> List[VoiceInfo]:
        """获取可用声音列表"""
        try:
            voices = self.client.voices.get_all()
            voice_list = []
            
            for voice in voices.voices:
                if not show_all and voice.category == "professional":
                    continue
                
                voice_list.append(VoiceInfo(
                    voice_id=voice.voice_id,
                    name=voice.name,
                    category=voice.category,
                    description=getattr(voice, 'description', ''),
                    labels=getattr(voice, 'labels', {}) or {},
                    preview_url=getattr(voice, 'preview_url', '')
                ))
            
            return voice_list
        except Exception as e:
            print(f"获取声音列表失败: {e}")
            return []
    
    def text_to_speech(
        self,
        text: str,
        voice_id: str = None,
        model: str = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        output_format: str = "mp3_44100_128",
        save: bool = True,
        filename: str = None
    ) -> TTSResult:
        """文本转语音"""
        voice_id = voice_id or self.default_voice_id
        model = model or self.default_model
        
        # 限制文本长度（ElevenLabs限制）
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars]
            print(f"警告: 文本已截断至 {max_chars} 字符")
        
        try:
            # 设置声音参数
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            ) if VoiceSettings else None
            
            # 生成音频
            audio_iterator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model,
                voice_settings=voice_settings,
                output_format=output_format
            )
            
            # 收集音频数据
            audio_data = b"".join(chunk for chunk in audio_iterator)
            
            # 获取声音名称
            voice_name = voice_id
            try:
                voices = self.get_voices(show_all=True)
                for v in voices:
                    if v.voice_id == voice_id:
                        voice_name = v.name
                        break
            except:
                pass
            
            result = TTSResult(
                text=text,
                voice_id=voice_id,
                voice_name=voice_name,
                model=model,
                audio_data=audio_data,
                duration_estimate=len(text) * 0.08  # 粗略估计
            )
            
            # 保存文件
            if save:
                if not filename:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_text = re.sub(r'[^\w\u4e00-\u9fff]', '_', text[:30])
                    filename = f"tts_{voice_id}_{timestamp}_{safe_text}.mp3"
                
                output_path = self.output_dir / filename
                result.save(str(output_path))
            
            return result
            
        except Exception as e:
            print(f"TTS生成失败: {e}")
            raise
    
    def stream_text_to_speech(
        self,
        text: str,
        voice_id: str = None,
        model: str = None
    ):
        """流式文本转语音"""
        voice_id = voice_id or self.default_voice_id
        model = model or self.default_model
        
        try:
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=voice_id,
                model_id=model
            )
            return audio_stream
        except Exception as e:
            print(f"流式TTS失败: {e}")
            raise
    
    def clone_voice(
        self,
        name: str,
        description: str,
        audio_files: List[Union[str, bytes, BinaryIO]],
        labels: Dict[str, str] = None
    ) -> str:
        """声音克隆"""
        try:
            # 准备音频文件
            processed_files = []
            for file in audio_files:
                if isinstance(file, str):
                    # 文件路径
                    processed_files.append(open(file, 'rb'))
                elif isinstance(file, bytes):
                    # 字节数据
                    from io import BytesIO
                    processed_files.append(BytesIO(file))
                else:
                    # 文件对象
                    processed_files.append(file)
            
            # 创建声音
            voice = self.client.voices.add(
                name=name,
                description=description,
                files=processed_files,
                labels=labels or {}
            )
            
            # 关闭文件
            for f in processed_files:
                if hasattr(f, 'close') and not isinstance(f, (str, bytes)):
                    f.close()
            
            return voice.voice_id
            
        except Exception as e:
            print(f"声音克隆失败: {e}")
            raise
    
    def edit_voice(
        self,
        voice_id: str,
        name: str = None,
        description: str = None,
        labels: Dict[str, str] = None
    ) -> bool:
        """编辑声音信息"""
        try:
            updates = {}
            if name:
                updates['name'] = name
            if description:
                updates['description'] = description
            if labels:
                updates['labels'] = labels
            
            self.client.voices.edit(voice_id=voice_id, **updates)
            return True
        except Exception as e:
            print(f"编辑声音失败: {e}")
            return False
    
    def delete_voice(self, voice_id: str) -> bool:
        """删除声音"""
        try:
            self.client.voices.delete(voice_id=voice_id)
            return True
        except Exception as e:
            print(f"删除声音失败: {e}")
            return False
    
    def generate_with_timestamps(
        self,
        text: str,
        voice_id: str = None,
        model: str = None
    ) -> Dict:
        """生成带时间戳的语音"""
        voice_id = voice_id or self.default_voice_id
        model = model or self.default_model
        
        try:
            result = self.client.text_to_speech.convert_with_timestamps(
                text=text,
                voice_id=voice_id,
                model_id=model
            )
            return {
                "audio": result.audio_base64,
                "alignment": result.alignment,
                "normalized_alignment": result.normalized_alignment
            }
        except Exception as e:
            print(f"生成带时间戳的语音失败: {e}")
            raise
    
    def get_models(self) -> List[Dict]:
        """获取可用模型列表"""
        try:
            models = self.client.models.get_all()
            return [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "description": m.description,
                    "can_do_text_to_speech": m.can_do_text_to_speech,
                    "can_do_voice_conversion": m.can_do_voice_conversion,
                    "token_cost_factor": m.token_cost_factor
                }
                for m in models
            ]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
    
    def get_user_info(self) -> Dict:
        """获取用户信息"""
        try:
            user = self.client.user.get()
            subscription = self.client.user.get_subscription()
            
            return {
                "user_id": getattr(user, 'user_id', ''),
                "subscription_tier": subscription.tier,
                "character_count": subscription.character_count,
                "character_limit": subscription.character_limit,
                "character_usage_percentage": (
                    subscription.character_count / subscription.character_limit * 100
                    if subscription.character_limit > 0 else 0
                ),
                "voice_slots": getattr(subscription, 'voice_slots', 0),
                "voice_slots_used": getattr(subscription, 'voice_slots_used', 0),
                "professional_voice_slots": getattr(subscription, 'professional_voice_slots', 0),
                "professional_voice_slots_used": getattr(subscription, 'professional_voice_slots_used', 0)
            }
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return {}
    
    def split_long_text(self, text: str, max_length: int = 5000) -> List[str]:
        """分割长文本"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = re.split(r'([。！？.!?]+)', text)
        
        current_chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            
            if len(current_chunk) + len(full_sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = full_sentence
            else:
                current_chunk += full_sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def text_to_speech_long(
        self,
        text: str,
        voice_id: str = None,
        model: str = None,
        **kwargs
    ) -> List[TTSResult]:
        """长文本转语音（自动分割）"""
        chunks = self.split_long_text(text)
        results = []
        
        for i, chunk in enumerate(chunks):
            print(f"处理第 {i+1}/{len(chunks)} 段文本...")
            result = self.text_to_speech(
                text=chunk,
                voice_id=voice_id,
                model=model,
                filename=f"tts_part_{i+1:03d}.mp3",
                **kwargs
            )
            results.append(result)
        
        return results


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ElevenLabs TTS Skill")
    parser.add_argument("--api-key", help="ElevenLabs API密钥")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列出声音
    subparsers.add_parser("voices", help="列出可用声音")
    
    # 列出模型
    subparsers.add_parser("models", help="列出可用模型")
    
    # 用户信息
    subparsers.add_parser("user", help="显示用户信息")
    
    # 文本转语音
    tts_parser = subparsers.add_parser("tts", help="文本转语音")
    tts_parser.add_argument("text", help="要转换的文本")
    tts_parser.add_argument("--voice", "-v", default="Rachel", help="声音ID")
    tts_parser.add_argument("--model", "-m", default="eleven_multilingual_v2", help="模型ID")
    tts_parser.add_argument("--output", "-o", help="输出文件名")
    tts_parser.add_argument("--stability", type=float, default=0.5, help="稳定性 (0.0-1.0)")
    tts_parser.add_argument("--similarity", type=float, default=0.75, help="相似度增强 (0.0-1.0)")
    tts_parser.add_argument("--style", type=float, default=0.0, help="风格 (0.0-1.0)")
    
    # 从文件转换
    file_parser = subparsers.add_parser("file", help="从文件转语音")
    file_parser.add_argument("path", help="文本文件路径")
    file_parser.add_argument("--voice", "-v", default="Rachel", help="声音ID")
    file_parser.add_argument("--model", "-m", default="eleven_multilingual_v2", help="模型ID")
    file_parser.add_argument("--output", "-o", help="输出文件名")
    
    # 克隆声音
    clone_parser = subparsers.add_parser("clone", help="克隆声音")
    clone_parser.add_argument("name", help="新声音名称")
    clone_parser.add_argument("files", nargs="+", help="音频文件路径")
    clone_parser.add_argument("--desc", default="", help="声音描述")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = ElevenLabsManager(api_key=args.api_key)
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 ELEVENLABS_API_KEY 环境变量或使用 --api-key 参数")
        return
    
    if args.command == "voices":
        voices = manager.get_voices(show_all=True)
        print(f"{'ID':<25} {'名称':<25} {'类别':<15}")
        print("-" * 65)
        for v in voices:
            print(f"{v.voice_id:<25} {v.name:<25} {v.category:<15}")
    
    elif args.command == "models":
        models = manager.get_models()
        print(f"{'模型ID':<35} {'名称':<30}")
        print("-" * 65)
        for m in models:
            print(f"{m['model_id']:<35} {m['name']:<30}")
    
    elif args.command == "user":
        info = manager.get_user_info()
        print(f"用户订阅级别: {info.get('subscription_tier', 'N/A')}")
        print(f"字符使用量: {info.get('character_count', 0):,} / {info.get('character_limit', 0):,}")
        print(f"使用比例: {info.get('character_usage_percentage', 0):.1f}%")
        print(f"声音槽位: {info.get('voice_slots_used', 0)} / {info.get('voice_slots', 0)}")
    
    elif args.command == "tts":
        print(f"正在生成语音...")
        print(f"声音: {args.voice}")
        print(f"模型: {args.model}")
        
        result = manager.text_to_speech(
            text=args.text,
            voice_id=args.voice,
            model=args.model,
            stability=args.stability,
            similarity_boost=args.similarity,
            style=args.style,
            filename=args.output
        )
        
        if result.file_path:
            print(f"✓ 已保存: {result.file_path}")
            print(f"  估计时长: {result.duration_estimate:.1f} 秒")
    
    elif args.command == "file":
        text = Path(args.path).read_text(encoding='utf-8')
        print(f"读取文件: {args.path} ({len(text)} 字符)")
        
        results = manager.text_to_speech_long(
            text=text,
            voice_id=args.voice,
            model=args.model
        )
        
        print(f"✓ 已生成 {len(results)} 个音频文件")
        for r in results:
            print(f"  - {r.file_path}")
    
    elif args.command == "clone":
        print(f"正在克隆声音: {args.name}")
        voice_id = manager.clone_voice(
            name=args.name,
            description=args.desc,
            audio_files=args.files
        )
        print(f"✓ 声音已创建，ID: {voice_id}")


if __name__ == "__main__":
    main()
