import logging
from functools import wraps
from typing import Callable, Any
from requests.exceptions import RequestException
import aiohttp

def api_error_handler(logger_name: str = "API") -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args) -> Any:
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                logging.error(e, name=logger_name)
                return "Network error"
            except Exception as e:
                logging.error(e, name=logger_name)
                return "Internal server error"
        return async_wrapper
    return decorator