#!/usr/bin/env python3
"""
Error Recovery System — Resilient LLM & System Calls

Provides retry logic, exponential backoff, and graceful degradation for:
- LLM API calls (Ollama, OpenAI, etc.)
- System operations (file I/O, network)
- Module calls (evaluator, bandit, memory)

Critical for production stability.
"""

import time
import functools
from typing import Callable, Any, Optional, List, Type
from dataclasses import dataclass
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    exponential_base: float = 2.0  # 1s, 2s, 4s, ...
    max_delay: float = 30.0  # cap at 30 seconds
    exceptions_to_catch: tuple = (Exception,)  # Catch all by default
    exceptions_to_skip: tuple = ()  # Never retry these


class ErrorRecovery:
    """
    Centralized error recovery system.

    Provides decorators and context managers for resilient operations.
    """

    @staticmethod
    def retry_with_backoff(
        max_retries: int = 3,
        base_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 30.0,
        exceptions_to_catch: tuple = (Exception,),
        exceptions_to_skip: tuple = (),
        fallback_value: Any = None,
        on_retry: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        """
        Decorator for retrying function calls with exponential backoff.

        Args:
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            exponential_base: Multiplier for each retry
            max_delay: Maximum delay cap
            exceptions_to_catch: Tuple of exceptions to retry on
            exceptions_to_skip: Tuple of exceptions to never retry
            fallback_value: Value to return if all retries fail
            on_retry: Callback(attempt, exception, delay) called before each retry
            on_failure: Callback(exception) called after all retries fail

        Returns:
            Decorated function with retry logic
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)

                    except exceptions_to_skip as e:
                        # Never retry these exceptions
                        logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                        if on_failure:
                            on_failure(e)
                        raise

                    except exceptions_to_catch as e:
                        last_exception = e

                        if attempt == max_retries:
                            # Final attempt failed
                            logger.error(
                                f"{func.__name__} failed after {max_retries} retries: {e}"
                            )
                            if on_failure:
                                on_failure(e)

                            if fallback_value is not None:
                                logger.info(f"{func.__name__} returning fallback value")
                                return fallback_value
                            else:
                                raise

                        # Calculate delay with exponential backoff
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )

                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        if on_retry:
                            on_retry(attempt + 1, e, delay)

                        time.sleep(delay)

                # Should never reach here, but just in case
                if fallback_value is not None:
                    return fallback_value
                raise last_exception

            return wrapper
        return decorator

    @staticmethod
    def retry_llm_call(
        max_retries: int = 3,
        base_delay: float = 2.0,
        fallback_response: Optional[str] = None
    ):
        """
        Specialized decorator for LLM API calls.

        Handles common LLM errors:
        - Connection timeouts
        - Rate limits (503, 429)
        - Model loading delays
        - Network errors

        Args:
            max_retries: Maximum retry attempts
            base_delay: Initial delay (higher for LLMs)
            fallback_response: Text to return if all retries fail

        Returns:
            Decorated function with LLM-specific retry logic
        """
        def on_retry(attempt, exception, delay):
            logger.info(f"LLM call retry {attempt}: {exception.__class__.__name__}")

        def on_failure(exception):
            logger.error(f"LLM call failed permanently: {exception}")

        return ErrorRecovery.retry_with_backoff(
            max_retries=max_retries,
            base_delay=base_delay,
            exponential_base=2.0,
            max_delay=60.0,  # LLMs can be slow
            exceptions_to_catch=(
                Exception,  # Catch all for now, can specialize later
            ),
            exceptions_to_skip=(
                KeyboardInterrupt,  # Never retry user interrupts
            ),
            fallback_value=fallback_response,
            on_retry=on_retry,
            on_failure=on_failure
        )

    @staticmethod
    def retry_file_operation(max_retries: int = 3):
        """
        Specialized decorator for file I/O operations.

        Handles:
        - File locks
        - Permission errors (transient)
        - Network filesystem delays

        Args:
            max_retries: Maximum retry attempts

        Returns:
            Decorated function with file I/O retry logic
        """
        return ErrorRecovery.retry_with_backoff(
            max_retries=max_retries,
            base_delay=0.5,
            exponential_base=2.0,
            max_delay=5.0,
            exceptions_to_catch=(
                IOError,
                OSError,
            ),
            exceptions_to_skip=(
                PermissionError,  # Permanent permission errors
                FileNotFoundError,  # Missing files won't appear on retry
            )
        )

    @staticmethod
    def safe_call(
        func: Callable,
        *args,
        fallback_value: Any = None,
        error_message: str = "Operation failed",
        **kwargs
    ) -> Any:
        """
        Safely call a function, catching all exceptions.

        Args:
            func: Function to call
            *args: Positional arguments
            fallback_value: Value to return on error
            error_message: Error message to log
            **kwargs: Keyword arguments

        Returns:
            Function result or fallback_value
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return fallback_value


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.

    States:
    - CLOSED: Normal operation (allow all calls)
    - OPEN: Circuit tripped (reject all calls, return fallback)
    - HALF_OPEN: Testing (allow one call to test recovery)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit breaker: Entering HALF_OPEN state")
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker: Recovered, entering CLOSED state")
            self.state = "CLOSED"
            self.failure_count = 0

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold}"
            )

            if self.failure_count >= self.failure_threshold:
                logger.error("Circuit breaker: OPEN - rejecting calls")
                self.state = "OPEN"

            raise


# ==============================================================================
# READY-TO-USE WRAPPERS FOR UNITY COMPONENTS
# ==============================================================================

def safe_llm_call(func: Callable, fallback: str = "[LLM Error]") -> Callable:
    """Wrap LLM call with error recovery."""
    return ErrorRecovery.retry_llm_call(
        max_retries=3,
        base_delay=2.0,
        fallback_response=fallback
    )(func)


def safe_evaluator_call(func: Callable, fallback_score: float = 0.0) -> Callable:
    """Wrap evaluator call with error recovery."""
    return ErrorRecovery.retry_with_backoff(
        max_retries=2,
        base_delay=1.0,
        fallback_value={"quality_score": fallback_score, "error": "Evaluation failed"}
    )(func)


def safe_bandit_call(func: Callable, fallback_arm: str = "random_jitter") -> Callable:
    """Wrap bandit call with error recovery."""
    return ErrorRecovery.retry_with_backoff(
        max_retries=2,
        base_delay=0.5,
        fallback_value=fallback_arm
    )(func)


# CLI testing
if __name__ == "__main__":
    print("="*70)
    print("ERROR RECOVERY SYSTEM TEST")
    print("="*70)

    # Test 1: Retry with backoff
    print("\n1. Testing retry with backoff...")

    attempt_count = [0]

    @ErrorRecovery.retry_with_backoff(max_retries=3, base_delay=0.5)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ValueError(f"Attempt {attempt_count[0]} failed")
        return "Success!"

    result = flaky_function()
    print(f"   ✅ Result: {result} (took {attempt_count[0]} attempts)")

    # Test 2: Fallback value
    print("\n2. Testing fallback value...")

    @ErrorRecovery.retry_with_backoff(max_retries=2, base_delay=0.1, fallback_value="FALLBACK")
    def always_fails():
        raise RuntimeError("Always fails")

    result = always_fails()
    print(f"   ✅ Result: {result} (fallback returned)")

    # Test 3: LLM retry
    print("\n3. Testing LLM retry...")

    llm_attempts = [0]

    @ErrorRecovery.retry_llm_call(max_retries=2, base_delay=0.5, fallback_response="[Error]")
    def mock_llm_call(prompt):
        llm_attempts[0] += 1
        if llm_attempts[0] < 2:
            raise ConnectionError("LLM timeout")
        return f"Response to: {prompt}"

    result = mock_llm_call("Test prompt")
    print(f"   ✅ Result: {result} (took {llm_attempts[0]} attempts)")

    # Test 4: Circuit breaker
    print("\n4. Testing circuit breaker...")

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)

    def failing_service():
        raise RuntimeError("Service down")

    # Trip the breaker
    for i in range(3):
        try:
            breaker.call(failing_service)
        except:
            pass

    print(f"   ✅ Circuit breaker state: {breaker.state}")

    # Wait for recovery
    print("   Waiting 2s for recovery...")
    time.sleep(2.1)

    # Should enter HALF_OPEN
    try:
        breaker.call(failing_service)
    except:
        pass

    print(f"   ✅ Circuit breaker state: {breaker.state}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
