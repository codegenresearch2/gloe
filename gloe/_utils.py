from typing import Callable, TypeVar, ParamSpec, Awaitable, Generic, Union, _GenericAlias\\nimport asyncio\\n\\n_Args = ParamSpec("_Args")\\n_R = TypeVar("_R")\\n\\ndef awaitify(sync_func: Callable[_Args, _R]) -> Callable[_Args, Awaitable[_R]]:\\n    async def async_func(*args, **kwargs):\\n        return sync_func(*args, **kwargs)\\n\\n    return async_func