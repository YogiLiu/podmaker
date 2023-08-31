from __future__ import annotations

import logging
import sys
import time
from datetime import timedelta
from typing import Callable, Tuple, Type, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


P = ParamSpec('P')
T = TypeVar('T')
_logger = logging.getLogger(__name__)


def retry(
        cnt: int,
        *,
        wait: timedelta = timedelta(seconds=0),
        catch: Type[Exception] | Tuple[Type[Exception], ...] = Exception,
        logger: logging.Logger = _logger,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A decorator to retry the function when exception raised.
    The function will be called at least once and at most cnt + 1 times.

    :param cnt: retry count
    :param wait: wait time between retries
    :param catch: the exception to retry
    :param logger: logger to log retry info
    """
    if cnt <= 0:
        raise ValueError('cnt must be positive')
    wait_seconds = wait.total_seconds()

    def deco(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for _ in range(cnt):
                try:
                    return func(*args, **kwargs)
                except catch:
                    logger.warning('retrying...')
                    if wait_seconds > 0:
                        logger.warning(f'wait {wait_seconds}s before retry')
                        time.sleep(wait_seconds)
            return func(*args, **kwargs)
        return wrapper
    return deco
