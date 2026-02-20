#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Transcript Skill - YouTube视频转录提取工具
支持字幕提取、翻译、摘要生成
"""

import re
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter, SRTFormatter, JSONFormatter
except ImportError:
    YouTubeTranscriptApi = None


@dataclass
class VideoInfo:
    """视频信息数据类"""
    video_id: str
    title: str = ""
    author: str = ""
    duration: int = 0
    available_languages: List[Dict] = None
    
    def __post_init__(self):
        if self.available_languages is None:
            self.available_languages = []


@dataclass
class TranscriptSegment:
    """字幕片段数据类"""
    text: str
    start: float
    duration: float
    end: float = 0.0
    
    def __post_init__(self):
        self.end = self.start + self.duration


@dataclass
class TranscriptResult:
    """转录结果数据类"""
    video_id: str
    language: str
    language_name: str
    is_generated: bool
    segments: List[TranscriptSegment]
    full_text: str = ""
    
    def __post_init__(self):
        if not self.full_text and self.segments:
            self.full_text = " ".join([s.text for s in self.segments])


class YouTubeTranscriptExtractor:
    """YouTube字幕提取器"""
    
    def __init__(self, proxy: Optional[str] = None):
        if YouTubeTranscriptApi is None:
            raise ImportError("请先安装 youtube-transcript-api: pip install youtube-transcript-api")
        
        self.proxy = proxy
        self._setup_proxy()
    
    def _setup_proxy(self):
        """设置代理"""
        if self.proxy:
            os.environ["HTTP_PROXY"] = self.proxy
            os.environ["HTTPS_PROXY"] = self.proxy
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从URL中提取视频ID"""
        # 处理不同格式的YouTube URL
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # 直接是视频ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 尝试解析URL
        try:
            parsed = urlparse(url)
            if parsed.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
                return parse_qs(parsed.query).get('v', [None])[0]
            elif parsed.hostname == 'youtu.be':
                return parsed.path.lstrip('/')
        except:
            pass
        
        return None
    
    def get_available_languages(self, video_id: str) -> List[Dict]:
        """获取视频可用的字幕语言"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            languages = []
            
            for transcript in transcript_list:
                languages.append({
                    "language_code": transcript.language_code,
                    "language_name": transcript.language,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable
                })
            
            return languages
        except Exception as e:
            print(f"获取语言列表失败: {e}")
            return []
    
    def extract_transcript(
        self, 
        video_id: str, 
        languages: List[str] = None,
        preserve_formatting: bool = True
    ) -> Optional[TranscriptResult]:
        """提取字幕"""
        # 清理视频ID
        clean_id = self.extract_video_id(video_id) or video_id
        
        try:
            # 获取字幕列表
            transcript_list = YouTubeTranscriptApi.list_transcripts(clean_id)
            
            # 尝试获取首选语言
            transcript = None
            if languages:
                for lang in languages:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        break
                    except:
                        continue
            
            # 如果没有找到首选语言，获取第一个可用的
            if not transcript:
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    # 获取任意可用字幕
                    for t in transcript_list:
                        transcript = t
                        break
            
            if not transcript:
                return None
            
            # 获取字幕数据
            data = transcript.fetch(preserve_formatting=preserve_formatting)
            
            # 转换为TranscriptSegment
            segments = [
                TranscriptSegment(
                    text=item.get('text', ''),
                    start=item.get('start', 0.0),
                    duration=item.get('duration', 0.0)
                )
                for item in data
            ]
            
            return TranscriptResult(
                video_id=clean_id,
                language=transcript.language_code,
                language_name=transcript.language,
                is_generated=transcript.is_generated,
                segments=segments
            )
            
        except Exception as e:
            print(f"提取字幕失败: {e}")
            return None
    
    def translate_transcript(
        self, 
        video_id: str, 
        target_language: str,
        source_language: str = None
    ) -> Optional[TranscriptResult]:
        """翻译字幕"""
        clean_id = self.extract_video_id(video_id) or video_id
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(clean_id)
            
            # 找到源语言字幕
            if source_language:
                try:
                    transcript = transcript_list.find_transcript([source_language])
                except:
                    transcript = list(transcript_list)[0]
            else:
                transcript = list(transcript_list)[0]
            
            # 翻译
            translated = transcript.translate(target_language)
            data = translated.fetch()
            
            segments = [
                TranscriptSegment(
                    text=item.get('text', ''),
                    start=item.get('start', 0.0),
                    duration=item.get('duration', 0.0)
                )
                for item in data
            ]
            
            return TranscriptResult(
                video_id=clean_id,
                language=target_language,
                language_name=f"{transcript.language} -> {target_language}",
                is_generated=True,
                segments=segments
            )
            
        except Exception as e:
            print(f"翻译字幕失败: {e}")
            return None
    
    def format_transcript(self, result: TranscriptResult, format_type: str = "text") -> str:
        """格式化字幕输出"""
        if format_type == "text":
            return result.full_text
        
        elif format_type == "json":
            return json.dumps(asdict(result), ensure_ascii=False, indent=2)
        
        elif format_type == "srt":
            lines = []
            for i, seg in enumerate(result.segments, 1):
                # SRT时间格式: HH:MM:SS,mmm --> HH:MM:SS,mmm
                start = self._format_srt_time(seg.start)
                end = self._format_srt_time(seg.end)
                lines.append(f"{i}")
                lines.append(f"{start} --> {end}")
                lines.append(seg.text)
                lines.append("")
            return "\n".join(lines)
        
        elif format_type == "vtt":
            lines = ["WEBVTT", ""]
            for seg in result.segments:
                start = self._format_vtt_time(seg.start)
                end = self._format_vtt_time(seg.end)
                lines.append(f"{start} --> {end}")
                lines.append(seg.text)
                lines.append("")
            return "\n".join(lines)
        
        elif format_type == "tsv":
            lines = ["start\tend\ttext"]
            for seg in result.segments:
                lines.append(f"{seg.start}\t{seg.end}\t{seg.text}")
            return "\n".join(lines)
        
        else:
            return result.full_text
    
    def _format_srt_time(self, seconds: float) -> str:
        """格式化为SRT时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_vtt_time(self, seconds: float) -> str:
        """格式化为VTT时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def generate_summary(self, result: TranscriptResult, max_sentences: int = 5) -> str:
        """生成字幕摘要（简单实现）"""
        text = result.full_text
        
        # 简单的句子分割
        sentences = re.split(r'[。！？.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # 选择前N个句子作为摘要
        summary_sentences = sentences[:max_sentences]
        
        if not summary_sentences:
            return text[:500] if len(text) > 500 else text
        
        return "。".join(summary_sentences) + "。"
    
    def extract_with_timestamps(
        self, 
        video_id: str, 
        start_time: float = None,
        end_time: float = None
    ) -> Optional[TranscriptResult]:
        """提取特定时间段的字幕"""
        result = self.extract_transcript(video_id)
        if not result:
            return None
        
        filtered_segments = []
        for seg in result.segments:
            if start_time and seg.end < start_time:
                continue
            if end_time and seg.start > end_time:
                continue
            filtered_segments.append(seg)
        
        result.segments = filtered_segments
        result.full_text = " ".join([s.text for s in filtered_segments])
        
        return result
    
    def search_in_transcript(
        self, 
        result: TranscriptResult, 
        keyword: str,
        context_seconds: float = 3.0
    ) -> List[Dict]:
        """在字幕中搜索关键词"""
        matches = []
        
        for i, seg in enumerate(result.segments):
            if keyword.lower() in seg.text.lower():
                # 获取上下文
                context_start = max(0, seg.start - context_seconds)
                context_end = seg.end + context_seconds
                
                context_segments = [
                    s for s in result.segments
                    if s.start >= context_start and s.end <= context_end
                ]
                
                context_text = " ".join([s.text for s in context_segments])
                
                matches.append({
                    "timestamp": seg.start,
                    "formatted_time": self._format_srt_time(seg.start),
                    "text": seg.text,
                    "context": context_text
                })
        
        return matches


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Transcript Skill")
    parser.add_argument("url", help="YouTube视频URL或视频ID")
    parser.add_argument("--proxy", help="代理地址 (如: http://127.0.0.1:7890)")
    parser.add_argument("--lang", nargs="+", default=["zh", "zh-CN", "en"], help="语言优先级")
    parser.add_argument("--format", default="text", choices=["text", "json", "srt", "vtt", "tsv"], help="输出格式")
    parser.add_argument("--translate", help="翻译到目标语言")
    parser.add_argument("--output", "-o", help="输出文件")
    parser.add_argument("--summary", action="store_true", help="生成摘要")
    parser.add_argument("--search", help="搜索关键词")
    parser.add_argument("--start", type=float, help="开始时间(秒)")
    parser.add_argument("--end", type=float, help="结束时间(秒)")
    parser.add_argument("--list-langs", action="store_true", help="列出可用语言")
    
    args = parser.parse_args()
    
    extractor = YouTubeTranscriptExtractor(proxy=args.proxy)
    
    # 提取视频ID
    video_id = extractor.extract_video_id(args.url)
    if not video_id:
        print(f"无法从URL提取视频ID: {args.url}")
        return
    
    print(f"视频ID: {video_id}")
    
    # 列出可用语言
    if args.list_langs:
        languages = extractor.get_available_languages(video_id)
        if languages:
            print("\n可用字幕语言:")
            for lang in languages:
                gen_mark = " (自动生成)" if lang["is_generated"] else ""
                print(f"  {lang['language_code']}: {lang['language_name']}{gen_mark}")
        else:
            print("该视频没有可用的字幕")
        return
    
    # 提取字幕
    if args.translate:
        print(f"正在翻译到 {args.translate}...")
        result = extractor.translate_transcript(video_id, args.translate)
    elif args.start is not None or args.end is not None:
        print(f"提取时间段: {args.start or 0}s - {args.end or 'end'}s")
        result = extractor.extract_with_timestamps(video_id, args.start, args.end)
    else:
        print("正在提取字幕...")
        result = extractor.extract_transcript(video_id, languages=args.lang)
    
    if not result:
        print("提取字幕失败，该视频可能没有字幕")
        return
    
    print(f"语言: {result.language_name} ({result.language})")
    print(f"片段数: {len(result.segments)}")
    
    # 搜索关键词
    if args.search:
        matches = extractor.search_in_transcript(result, args.search)
        print(f"\n找到 {len(matches)} 个匹配:")
        for match in matches:
            print(f"\n[{match['formatted_time']}] {match['text']}")
        return
    
    # 格式化输出
    output = extractor.format_transcript(result, args.format)
    
    # 保存或打印
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n已保存到: {args.output}")
    else:
        print("\n" + "="*50)
        print(output[:2000] if len(output) > 2000 else output)
        if len(output) > 2000:
            print(f"\n... (内容已截断，共 {len(output)} 字符)")
    
    # 生成摘要
    if args.summary:
        summary = extractor.generate_summary(result)
        print("\n" + "="*50)
        print("摘要:")
        print(summary)


if __name__ == "__main__":
    main()
