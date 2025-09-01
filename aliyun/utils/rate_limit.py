from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

from aiolimiter import AsyncLimiter

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])

# define global limiters
SEC_LIMIT = 5  # requests per second
MIN_LIMIT = 300  # requests per minute
limiter_sec = AsyncLimiter(SEC_LIMIT, 1)
limiter_min = AsyncLimiter(MIN_LIMIT, 60)


def rate_limit() -> Callable[[F], F]:
    """
    Decorator to rate limit the function calls.
    """

    def decorator(func: F) -> F:

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # limit the function calls by second and minute
            async with limiter_sec, limiter_min:
                return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
