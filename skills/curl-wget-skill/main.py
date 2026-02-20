#!/usr/bin/env python3
"""
cURL/wget Download Skill
========================
HTTP download tool with resume capability, batch downloads, and progress tracking.

Use when scanning networks, managing remote servers, or when user mentions 
'SSH', 'DNS', 'network'.

Author: Kimi Skills Team
License: MIT
"""

import os
import sys
import json
import hashlib
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor
import requests
from tqdm import tqdm
import time


@dataclass
class DownloadResult:
    """Data class to represent download results."""
    url: str
    status: str
    local_path: Optional[str] = None
    file_size: int = 0
    downloaded_size: int = 0
    speed: float = 0.0
    time_elapsed: float = 0.0
    error: Optional[str] = None
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return asdict(self)


class DownloadProgress:
    """Track download progress."""
    
    def __init__(self, total_size: int, desc: str = "Downloading"):
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.pbar = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=desc
        ) if total_size > 0 else None
    
    def update(self, chunk_size: int):
        """Update progress."""
        self.downloaded += chunk_size
        if self.pbar:
            self.pbar.update(chunk_size)
    
    def close(self):
        """Close progress bar."""
        if self.pbar:
            self.pbar.close()
    
    @property
    def speed(self) -> float:
        """Calculate download speed."""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return self.downloaded / elapsed
        return 0.0


class CurlWgetSkill:
    """
    cURL/wget Download Skill class.
    
    Provides comprehensive HTTP download capabilities:
    - Single file downloads
    - Batch downloads
    - Resume interrupted downloads
    - Progress tracking
    - Checksum verification
    - Concurrent downloads
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CurlWgetSkill.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.default_timeout = self.config.get("default_timeout", 30)
        self.chunk_size = self.config.get("chunk_size", 8192)
        self.max_retries = self.config.get("max_retries", 3)
        self.user_agent = self.config.get(
            "user_agent",
            "curl-wget-skill/1.0.0"
        )
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent
        })

    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL."""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = os.path.basename(path)
        if not filename:
            filename = "download"
        return filename

    def _get_filename_from_headers(
        self,
        headers: Dict[str, str]
    ) -> Optional[str]:
        """Extract filename from Content-Disposition header."""
        content_disp = headers.get("Content-Disposition", "")
        if "filename=" in content_disp:
            parts = content_disp.split("filename=")
            if len(parts) > 1:
                filename = parts[1].strip('"\'')
                return unquote(filename)
        return None

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def _calculate_checksum(
        self,
        filepath: str,
        algorithm: str = "sha256"
    ) -> str:
        """Calculate file checksum."""
        hash_obj = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def _get_file_size(self, url: str) -> int:
        """Get remote file size."""
        try:
            response = self.session.head(url, timeout=self.default_timeout)
            return int(response.headers.get("Content-Length", 0))
        except:
            return 0

    def _supports_resume(self, url: str) -> bool:
        """Check if server supports resume."""
        try:
            response = self.session.head(url, timeout=self.default_timeout)
            return "bytes" in response.headers.get("Accept-Ranges", "")
        except:
            return False

    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        resume: bool = True,
        verify_checksum: Optional[str] = None,
        checksum_algorithm: str = "sha256",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> DownloadResult:
        """
        Download a single file.
        
        Args:
            url: URL to download
            output_path: Local save path
            resume: Enable resume capability
            verify_checksum: Expected checksum for verification
            checksum_algorithm: Checksum algorithm
            headers: Additional HTTP headers
            timeout: Request timeout
            
        Returns:
            DownloadResult object
        """
        if not self._validate_url(url):
            return DownloadResult(
                url=url,
                status="error",
                error="Invalid URL"
            )
        
        # Determine output filename
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = Path(self._get_filename_from_url(url))
        
        # Check for existing file for resume
        downloaded_size = 0
        if resume and output_file.exists():
            downloaded_size = output_file.stat().st_size
        
        # Prepare headers
        request_headers = headers or {}
        request_headers["User-Agent"] = self.user_agent
        
        if downloaded_size > 0 and self._supports_resume(url):
            request_headers["Range"] = f"bytes={downloaded_size}-"
        
        start_time = time.time()
        retries = 0
        
        while retries < self.max_retries:
            try:
                response = self.session.get(
                    url,
                    headers=request_headers,
                    stream=True,
                    timeout=timeout or self.default_timeout
                )
                response.raise_for_status()
                
                # Get total size
                total_size = int(response.headers.get("Content-Length", 0))
                if downloaded_size > 0 and response.status_code == 206:
                    total_size += downloaded_size
                
                # Determine mode
                mode = "ab" if downloaded_size > 0 and resume else "wb"
                
                # Create progress tracker
                progress = DownloadProgress(total_size, output_file.name)
                progress.downloaded = downloaded_size
                
                # Download file
                with open(output_file, mode) as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
                
                progress.close()
                
                time_elapsed = time.time() - start_time
                file_size = output_file.stat().st_size
                
                # Verify checksum if provided
                if verify_checksum:
                    actual_checksum = self._calculate_checksum(
                        str(output_file),
                        checksum_algorithm
                    )
                    if actual_checksum != verify_checksum:
                        return DownloadResult(
                            url=url,
                            status="checksum_mismatch",
                            local_path=str(output_file),
                            file_size=file_size,
                            downloaded_size=file_size,
                            speed=progress.speed,
                            time_elapsed=time_elapsed,
                            error="Checksum verification failed"
                        )
                
                return DownloadResult(
                    url=url,
                    status="success",
                    local_path=str(output_file),
                    file_size=file_size,
                    downloaded_size=file_size,
                    speed=progress.speed,
                    time_elapsed=time_elapsed,
                    checksum=self._calculate_checksum(str(output_file))
                        if not verify_checksum else actual_checksum
                )
                
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries >= self.max_retries:
                    return DownloadResult(
                        url=url,
                        status="error",
                        error=f"Download failed after {self.max_retries} retries: {str(e)}"
                    )
                time.sleep(1)
            except Exception as e:
                return DownloadResult(
                    url=url,
                    status="error",
                    error=str(e)
                )
        
        return DownloadResult(
            url=url,
            status="error",
            error="Max retries exceeded"
        )

    def batch_download(
        self,
        urls: List[str],
        output_dir: str = ".",
        max_concurrent: int = 3,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        Download multiple files concurrently.
        
        Args:
            urls: List of URLs to download
            output_dir: Output directory
            max_concurrent: Maximum concurrent downloads
            resume: Enable resume capability
            
        Returns:
            Dictionary with batch results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        success_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = []
            for url in urls:
                filename = self._get_filename_from_url(url)
                filepath = output_path / filename
                future = executor.submit(
                    self.download,
                    url=url,
                    output_path=str(filepath),
                    resume=resume
                )
                futures.append(future)
            
            for future in futures:
                result = future.result()
                results.append(result.to_dict())
                if result.status == "success":
                    success_count += 1
                else:
                    failed_count += 1
        
        return {
            "success": True,
            "total": len(urls),
            "successful": success_count,
            "failed": failed_count,
            "results": results
        }

    async def async_download(
        self,
        url: str,
        output_path: Optional[str] = None,
        resume: bool = True
    ) -> DownloadResult:
        """
        Async download using aiohttp.
        
        Args:
            url: URL to download
            output_path: Local save path
            resume: Enable resume capability
            
        Returns:
            DownloadResult object
        """
        if not output_path:
            output_path = self._get_filename_from_url(url)
        
        output_file = Path(output_path)
        downloaded_size = 0
        
        if resume and output_file.exists():
            downloaded_size = output_file.stat().st_size
        
        headers = {"User-Agent": self.user_agent}
        if downloaded_size > 0:
            headers["Range"] = f"bytes={downloaded_size}-"
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status not in [200, 206]:
                        return DownloadResult(
                            url=url,
                            status="error",
                            error=f"HTTP {response.status}"
                        )
                    
                    mode = "ab" if downloaded_size > 0 and resume else "wb"
                    
                    async with aiofiles.open(output_file, mode) as f:
                        async for chunk in response.content.iter_chunked(
                            self.chunk_size
                        ):
                            await f.write(chunk)
                            downloaded_size += len(chunk)
                    
                    time_elapsed = time.time() - start_time
                    
                    return DownloadResult(
                        url=url,
                        status="success",
                        local_path=str(output_file),
                        file_size=output_file.stat().st_size,
                        downloaded_size=downloaded_size,
                        speed=downloaded_size / time_elapsed if time_elapsed > 0 else 0,
                        time_elapsed=time_elapsed
                    )
                    
        except Exception as e:
            return DownloadResult(
                url=url,
                status="error",
                error=str(e)
            )

    def mirror(
        self,
        url: str,
        output_dir: str,
        depth: int = 1,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Mirror a website (limited depth crawling).
        
        Args:
            url: Starting URL
            output_dir: Output directory
            depth: Crawling depth
            include: URL patterns to include
            exclude: URL patterns to exclude
            
        Returns:
            Mirror results
        """
        # Placeholder for mirroring functionality
        # Full implementation would require web crawling
        return {
            "success": False,
            "error": "Mirror function requires additional dependencies"
        }


# Entry points for Kimi Skills Framework
def download(url: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for single file download.
    
    Args:
        url: URL to download
        **kwargs: Additional parameters
        
    Returns:
        Download result dictionary
    """
    skill = CurlWgetSkill()
    result = skill.download(url, **kwargs)
    return result.to_dict()


def batch_download(urls: List[str], **kwargs) -> Dict[str, Any]:
    """
    Batch download entry point.
    
    Args:
        urls: List of URLs
        **kwargs: Additional parameters
        
    Returns:
        Batch results dictionary
    """
    skill = CurlWgetSkill()
    return skill.batch_download(urls, **kwargs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="cURL/wget Download Skill")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-c", "--continue", dest="resume",
                       action="store_true", help="Resume download")
    parser.add_argument("-b", "--batch", nargs="+",
                       help="Multiple URLs for batch download")
    
    args = parser.parse_args()
    
    if args.batch:
        result = batch_download(args.batch)
    else:
        result = download(args.url, output_path=args.output, resume=args.resume)
    
    print(json.dumps(result, indent=2))
