import asyncio
import functools
from typing import Callable, Any, Type, Tuple
from app.core.logging import logger

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,)
) -> Callable:
    """
    Decorator to retry an asynchronous function using exponential backoff.
    
    :param retries: Maximum number of retry attempts.
    :param delay: Initial delay in seconds.
    :param backoff: Multiplier to adjust delay for subsequent retries.
    :param exceptions: Tuple of exceptions to intercept and retry on.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == retries:
                        logger.error(
                            f"Function '{func.__name__}' failed permanently after {retries} attempts. Error: {e}"
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt}/{retries} for '{func.__name__}' failed: {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
