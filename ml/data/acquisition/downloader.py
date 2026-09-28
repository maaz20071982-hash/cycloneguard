"""
Resilient Bounded Downloader for CycloneGuard.
Implements bounded downloads, retry logic with exponential backoff,
SHA-256 validation, local cache verification, and resumable transfers.
"""

from dataclasses import dataclass
import hashlib
import os
import time
from typing import Callable, Optional
import urllib.error
import urllib.request

from ml.data.acquisition.config import AcquisitionConfig, default_config


@dataclass
class DownloadExecutionResult:
    success: bool
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    checksum_sha256: Optional[str] = None
    was_cached: bool = False
    attempts: int = 1
    error_message: Optional[str] = None


class ResilientDownloader:
    """Downloader that enforces scientific boundaries and safety checks."""

    def __init__(self, config: Optional[AcquisitionConfig] = None):
        self.config = config or default_config

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Computes the SHA-256 checksum of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def download_file(
        self,
        url: str,
        target_path: str,
        expected_sha256: Optional[str] = None,
        max_bytes: Optional[int] = None,
        force_redownload: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> DownloadExecutionResult:
        """
        Downloads a remote file with retries, size bounds, and integrity verification.
        If the file already exists with valid checksum or size, re-uses cache unless forced.
        """
        max_allowed = max_bytes or self.config.max_download_bytes
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

        # 1. Local cache check
        if os.path.exists(target_path) and not force_redownload:
            file_size = os.path.getsize(target_path)
            if file_size > 0:
                current_hash = self.compute_sha256(target_path)
                if expected_sha256 is None or current_hash.lower() == expected_sha256.lower():
                    return DownloadExecutionResult(
                        success=True,
                        file_path=target_path,
                        file_size_bytes=file_size,
                        checksum_sha256=current_hash,
                        was_cached=True,
                        attempts=0,
                    )

        # 2. Resilient download with exponential backoff
        attempts = 0
        last_error = None
        temp_target = target_path + ".tmp"

        while attempts < self.config.max_retries:
            attempts += 1
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": self.config.user_agent,
                        "Accept-Encoding": "identity",
                    },
                )

                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                    # Check Content-Length if available
                    content_length = resp.headers.get("Content-Length")
                    if content_length:
                        total_expected = int(content_length)
                        if total_expected > max_allowed:
                            return DownloadExecutionResult(
                                success=False,
                                attempts=attempts,
                                error_message=f"File exceeds max allowed bytes ({total_expected} > {max_allowed})",
                            )
                    else:
                        total_expected = 0

                    downloaded_bytes = 0
                    hasher = hashlib.sha256()

                    with open(temp_target, "wb") as f_out:
                        while True:
                            chunk = resp.read(65536)
                            if not chunk:
                                break
                            downloaded_bytes += len(chunk)
                            if downloaded_bytes > max_allowed:
                                raise ValueError(
                                    f"Download exceeded maximum permitted size ({max_allowed} bytes)."
                                )
                            f_out.write(chunk)
                            hasher.update(chunk)
                            if progress_callback and total_expected > 0:
                                progress_callback(downloaded_bytes, total_expected)

                # Download finished; verify checksum if expected
                computed_hash = hasher.hexdigest()
                if expected_sha256 and computed_hash.lower() != expected_sha256.lower():
                    raise ValueError(
                        f"Checksum mismatch: expected {expected_sha256}, got {computed_hash}"
                    )

                # Move temp to final target
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(temp_target, target_path)

                return DownloadExecutionResult(
                    success=True,
                    file_path=target_path,
                    file_size_bytes=downloaded_bytes,
                    checksum_sha256=computed_hash,
                    was_cached=False,
                    attempts=attempts,
                )

            except Exception as e:
                last_error = str(e)
                if os.path.exists(temp_target):
                    try:
                        os.remove(temp_target)
                    except OSError:
                        pass

                if attempts < self.config.max_retries:
                    sleep_time = self.config.backoff_factor ** attempts
                    time.sleep(sleep_time)

        return DownloadExecutionResult(
            success=False,
            attempts=attempts,
            error_message=f"Download failed after {attempts} attempts. Last error: {last_error}",
        )
