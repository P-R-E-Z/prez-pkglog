"""Unit tests for the utils module"""

import time
import tempfile
from pathlib import Path
from unittest.mock import patch, call
import pytest

from src.prez_pkglog.utils import (
    performance_monitor,
    cache_result,
    PerformanceTracker,
    optimize_file_operations,
)


class TestPerformanceMonitor:
    """Test the performance_monitor decorator."""

    def test_performance_monitor_decorator(self):
        """Test that performance_monitor decorator works correctly."""

        @performance_monitor
        def test_function():
            time.sleep(0.01)
            return "test_result"

        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            result = test_function()

            assert result == "test_result"
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "test_function took" in call_args
            assert "seconds" in call_args

    def test_performance_monitor_with_exception(self):
        """Test performance_monitor decorator when function raises exception."""

        @performance_monitor
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test error"):
                failing_function()

            # Should still log performance even when exception occurs
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "failing_function took" in call_args

    def test_performance_monitor_with_args(self):
        """Test performance_monitor decorator with function arguments."""

        @performance_monitor
        def function_with_args(a, b, c=None):
            return f"{a}-{b}-{c}"

        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            result = function_with_args("arg1", "arg2", c="kwarg")

            assert result == "arg1-arg2-kwarg"
            mock_logger.debug.assert_called_once()

    def test_performance_monitor_preserves_function_metadata(self):
        """Test that performance_monitor preserves function metadata."""

        @performance_monitor
        def documented_function():
            """This is a test function."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function."


class TestCacheResult:
    """Test the cache_result decorator."""

    def test_cache_result_basic_functionality(self):
        """Test basic caching functionality."""
        call_count = 0

        @cache_result(max_size=2)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute the function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same args should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

        # Call with different args should execute function
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2

    def test_cache_result_with_kwargs(self):
        """Test caching with keyword arguments."""
        call_count = 0

        @cache_result(max_size=3)
        def function_with_kwargs(a, b=None, c=None):
            nonlocal call_count
            call_count += 1
            return f"{a}-{b}-{c}"

        # Test with different combinations
        result1 = function_with_kwargs("test", b="value")
        assert result1 == "test-value-None"
        assert call_count == 1

        # Same call should use cache
        result2 = function_with_kwargs("test", b="value")
        assert result2 == "test-value-None"
        assert call_count == 1

        # Different kwargs should execute function
        result3 = function_with_kwargs("test", c="other")
        assert result3 == "test-None-other"
        assert call_count == 2

    def test_cache_result_lru_eviction(self):
        """Test LRU cache eviction when max_size is exceeded."""
        call_count = 0

        @cache_result(max_size=2)
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3

        # Fill cache to max size
        cached_function(1)  # call_count = 1
        cached_function(2)  # call_count = 2

        # Add third item, should evict first
        cached_function(3)  # call_count = 3

        # First item should be evicted, so calling it again should execute
        cached_function(1)  # call_count = 4
        assert call_count == 4

        # Second and third items should still be cached
        cached_function(2)  # call_count = 4 (no change)
        cached_function(3)  # call_count = 4 (no change)
        assert call_count == 4

    def test_cache_result_default_max_size(self):
        """Test cache_result with default max_size."""
        call_count = 0

        @cache_result()  # Uses default max_size=128
        def default_cached_function(x):
            nonlocal call_count
            call_count += 1
            return x

        # Should work with default settings
        result = default_cached_function(42)
        assert result == 42
        assert call_count == 1

        # Second call should use cache
        result = default_cached_function(42)
        assert result == 42
        assert call_count == 1

    def test_cache_result_preserves_function_metadata(self):
        """Test that cache_result preserves function metadata."""

        @cache_result(max_size=10)
        def cached_documented_function():
            """This function has documentation."""
            return "cached_result"

        assert cached_documented_function.__name__ == "cached_documented_function"
        assert cached_documented_function.__doc__ == "This function has documentation."


class TestPerformanceTracker:
    """Test the PerformanceTracker context manager."""

    def test_performance_tracker_basic_usage(self):
        """Test basic PerformanceTracker usage."""
        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            with PerformanceTracker("test_operation"):
                time.sleep(0.01)

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "test_operation took" in call_args
            assert "seconds" in call_args

    def test_performance_tracker_with_exception(self):
        """Test PerformanceTracker when exception occurs in context."""
        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test error"):
                with PerformanceTracker("failing_operation"):
                    time.sleep(0.01)
                    raise ValueError("Test error")

            # Should still log performance even when exception occurs
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "failing_operation took" in call_args

    def test_performance_tracker_initialization(self):
        """Test PerformanceTracker initialization."""
        tracker = PerformanceTracker("test_name")
        assert tracker.name == "test_name"
        assert tracker.start_time is None

    def test_performance_tracker_enter_exit(self):
        """Test PerformanceTracker __enter__ and __exit__ methods."""
        tracker = PerformanceTracker("test_operation")

        # Test __enter__
        result = tracker.__enter__()
        assert result is tracker
        assert tracker.start_time is not None

        # Test __exit__
        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            tracker.__exit__(None, None, None)
            mock_logger.debug.assert_called_once()

    def test_performance_tracker_multiple_operations(self):
        """Test multiple PerformanceTracker operations."""
        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            with PerformanceTracker("operation1"):
                time.sleep(0.005)

            with PerformanceTracker("operation2"):
                time.sleep(0.005)

            assert mock_logger.debug.call_count == 2

            # Check that both operations were logged
            calls = mock_logger.debug.call_args_list
            assert "operation1 took" in calls[0][0][0]
            assert "operation2 took" in calls[1][0][0]


class TestOptimizeFileOperations:
    """Test the optimize_file_operations function."""

    def test_optimize_file_operations_success(self):
        """Test optimize_file_operations with successful operation."""

        def successful_operation():
            return "success"

        result = optimize_file_operations("/test/path", successful_operation)
        assert result == "success"

    def test_optimize_file_operations_retry_on_failure(self):
        """Test optimize_file_operations retries on failure."""
        call_count = 0

        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OSError("File operation failed")
            return "success_after_retries"

        with patch("time.sleep") as mock_sleep:
            result = optimize_file_operations("/test/path", failing_operation)

            assert result == "success_after_retries"
            assert call_count == 3

            # Check exponential backoff
            expected_calls = [call(0.1), call(0.2)]
            mock_sleep.assert_has_calls(expected_calls)

    def test_optimize_file_operations_max_retries_exceeded(self):
        """Test optimize_file_operations when max retries are exceeded."""
        call_count = 0

        def always_failing_operation():
            nonlocal call_count
            call_count += 1
            raise IOError("Persistent file error")

        with patch("src.prez_pkglog.utils.logger") as mock_logger:
            with pytest.raises(IOError, match="Persistent file error"):
                optimize_file_operations("/test/path", always_failing_operation)

            assert call_count == 3  # Should try 3 times
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Failed to perform operation on /test/path" in error_call

    def test_optimize_file_operations_with_different_exceptions(self):
        """Test optimize_file_operations with different exception types."""

        # Test with OSError
        def os_error_operation():
            raise OSError("OS error")

        with pytest.raises(OSError):
            optimize_file_operations("/test/path", os_error_operation)

        # Test with IOError
        def io_error_operation():
            raise IOError("IO error")

        with pytest.raises(IOError):
            optimize_file_operations("/test/path", io_error_operation)

    def test_optimize_file_operations_non_file_exception(self):
        """Test optimize_file_operations with non-file-related exceptions."""

        def non_file_error_operation():
            raise ValueError("Not a file error")

        # Should not retry for non-file errors
        with pytest.raises(ValueError, match="Not a file error"):
            optimize_file_operations("/test/path", non_file_error_operation)

    def test_optimize_file_operations_with_real_file(self):
        """Test optimize_file_operations with real file operations."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("test content")

        try:

            def read_file_operation():
                return Path(temp_path).read_text()

            result = optimize_file_operations(temp_path, read_file_operation)
            assert result == "test content"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_optimize_file_operations_exponential_backoff(self):
        """Test that exponential backoff works correctly."""
        call_count = 0

        def operation_with_retries():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OSError("Temporary failure")
            return "success"

        with patch("time.sleep") as mock_sleep:
            result = optimize_file_operations("/test/path", operation_with_retries)

            assert result == "success"
            # Check exponential backoff: 0.1, 0.2
            expected_calls = [call(0.1), call(0.2)]
            mock_sleep.assert_has_calls(expected_calls)
            assert mock_sleep.call_count == 2
