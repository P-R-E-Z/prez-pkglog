"""Utility functions for performance monitoring and optimization"""

import time
import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def performance_monitor(func: F) -> Callable[..., Any]:
    """Decorator to monitor function performance"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.debug(f"{func.__name__} took {duration:.4f} seconds")

    return wrapper


def cache_result(max_size: int = 128):
    """Simple LRU cache decorator for expensive operations"""

    def decorator(func: F) -> Callable[..., Any]:
        cache: dict[str, Any] = {}
        cache_keys: list[str] = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str((args, tuple(sorted(kwargs.items()))))

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)

            if "_seen_keys" not in wrapper.__dict__:
                wrapper._seen_keys = set()  # type: ignore[attr-defined]

            seen_keys: set[str] = wrapper._seen_keys  # type: ignore[attr-defined]

            if len(cache) >= max_size and key in seen_keys:
                return result

            if len(cache) >= max_size:
                oldest_key = cache_keys.pop(0)
                del cache[oldest_key]

            cache[key] = result
            cache_keys.append(key)
            seen_keys.add(key)

            return result

        return wrapper

    return decorator


class PerformanceTracker:
    """Context manager for tracking performance of code blocks"""

    def __init__(self, name: str):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            logger.debug(f"{self.name} took {duration:.4f} seconds")


def optimize_file_operations(file_path: str, operation: Callable[[], Any]) -> Any:
    """Optimize file operations with error handling and retries"""
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        try:
            return operation()
        except (OSError, IOError) as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to perform operation on {file_path}: {e}")
                raise
            time.sleep(retry_delay * (2**attempt))
