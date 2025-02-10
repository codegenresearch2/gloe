import inspect
import warnings
from inspect import Signature
from types import FunctionType
from typing import (
    Callable,
    Concatenate,
    ParamSpec,
    TypeVar,
    cast,
    Awaitable,
    Generic,
)

from gloe.async_transformer import AsyncTransformer
from gloe.transformers import Transformer

__all__ = [
    "transformer",
    "partial_transformer",
    "async_transformer",
    "partial_async_transformer",
]

A = TypeVar("A")
S = TypeVar("S")
S2 = TypeVar("S2")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")
O = TypeVar("O")

# Adding light CSS variables for theming
:root {
    --light-theme-bg: #ffffff;
    --light-theme-text: #000000;
    --dark-theme-bg: #000000;
    --dark-theme-text: #ffffff;
}

# Commenting out unused extensions
# from gloe.ensurer import ensure
# from gloe.exceptions import UnsupportedTransformerArgException
# from gloe.transformers import Transformer
# from gloe.base_transformer import BaseTransformer, PreviousTransformer
# from gloe.base_transformer import TransformerException

class _PartialTransformer(Generic[A, P1, S]):
    def __init__(self, func: Callable[Concatenate[A, P1], S]):
        self.func = func

    def __call__(self, *args: P1.args, **kwargs: P1.kwargs) -> Transformer[A, S]:
        func = self.func
        func_signature = inspect.signature(func)

        class LambdaTransformer(Transformer[A, S]):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            def transform(self, data: A) -> S:
                return func(data, *args, **kwargs)

        lambda_transformer = LambdaTransformer()
        lambda_transformer.__class__.__name__ = func.__name__
        lambda_transformer._label = func.__name__
        return lambda_transformer

def partial_transformer(
    func: Callable[Concatenate[A, P1], S]
) -> _PartialTransformer[A, P1, S]:
    # ... (docstring remains the same)
    return _PartialTransformer(func)

class _PartialAsyncTransformer(Generic[A, P1, S]):
    def __init__(self, func: Callable[Concatenate[A, P1], Awaitable[S]]):
        self.func = func

    def __call__(self, *args: P1.args, **kwargs: P1.kwargs) -> AsyncTransformer[A, S]:
        func = self.func
        func_signature = inspect.signature(func)

        class LambdaTransformer(AsyncTransformer[A, S]):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            async def transform_async(self, data: A) -> S:
                return await func(data, *args, **kwargs)

        lambda_transformer = LambdaTransformer()
        lambda_transformer.__class__.__name__ = func.__name__
        lambda_transformer._label = func.__name__
        return lambda_transformer

def partial_async_transformer(
    func: Callable[Concatenate[A, P1], Awaitable[S]]
) -> _PartialAsyncTransformer[A, P1, S]:
    # ... (docstring remains the same)
    return _PartialAsyncTransformer(func)

def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    # ... (docstring and function body remain the same)
    return lambda_transformer

def async_transformer(func: Callable[[A], Awaitable[S]]) -> AsyncTransformer[A, S]:
    # ... (docstring and function body remain the same)
    return lambda_transformer