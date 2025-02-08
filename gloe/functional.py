from gloe.functional import transformer, partial_transformer, partial_async_transformer, async_transformer
from gloe.conditional import If, condition
from gloe.ensurer import ensure
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.transformers import Transformer
from gloe.base_transformer import BaseTransformer, PreviousTransformer
from gloe.base_transformer import TransformerException
from gloe.async_transformer import AsyncTransformer

__all__ = [
    'transformer',
    'partial_transformer',
    'partial_async_transformer',
    'async_transformer',
    'If',
    'condition',
    'ensure',
    'UnsupportedTransformerArgException',
    'BaseTransformer',
    'PreviousTransformer',
    'Transformer',
    'TransformerException',
    'AsyncTransformer',
]

setattr(Transformer, '__rshift__', _compose_nodes)
setattr(AsyncTransformer, '__rshift__', _compose_nodes)

# Ensure string literals are properly terminated
# Fixed the unterminated string literal in the first line of functional.py

# New code snippet starts here

import inspect
import warnings
from inspect import Signature
from types import FunctionType
from typing import (Callable, Concatenate, ParamSpec, TypeVar, cast, Awaitable, Generic)

from gloe.async_transformer import AsyncTransformer
from gloe.transformers import Transformer

__all__ = [
    'transformer',
    'partial_transformer',
    'async_transformer',
    'partial_async_transformer',
]

A = TypeVar('A')
S = TypeVar('S')
S2 = TypeVar('S2')
P1 = ParamSpec('P1')
P2 = ParamSpec('P2')
O = TypeVar('O')

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


def partial_transformer(func: Callable[Concatenate[A, P1], S]) -> _PartialTransformer[A, P1, S]:
    """
    This decorator lets us create partial transformers, which are transformers that allow for partial application of their arguments.
    This capability is particularly useful for creating configurable transformer instances where some arguments are preset, enhancing modularity and reusability in data processing pipelines.
    """
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


def partial_async_transformer(func: Callable[Concatenate[A, P1], Awaitable[S]]) -> _PartialAsyncTransformer[A, P1, S]:
    """
    This decorator enables the creation of partial asynchronous transformers, which are transformers capable of partial argument application.
    Such functionality is invaluable for crafting reusable asynchronous transformer instances where certain arguments are predetermined, enhancing both modularity and reusability within asynchronous data processing flows.
    """
    return _PartialAsyncTransformer(func)


def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    """
    Convert a callable to an instance of the Transformer class.
    """
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) > 1:
        warnings.warn(
            f"Only one parameter is allowed on Transformers. Function '{func.__name__}' has the following signature: {func_signature}. "
            'To pass a complex data, use a complex type like named tuples, typed dicts, dataclasses or anything else.',
            category=RuntimeWarning,
        )

    class LambdaTransformer(Transformer[A, S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def signature(self) -> Signature:
            return func_signature

        def transform(self, data: A) -> S:
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    lambda_transformer._label = func.__name__
    return lambda_transformer


def async_transformer(func: Callable[[A], Awaitable[S]]) -> AsyncTransformer[A, S]:
    """
    Convert a callable to an instance of the AsyncTransformer class.
    """
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) > 1:
        warnings.warn(
            f"Only one parameter is allowed on Transformers. Function '{func.__name__}' has the following signature: {func_signature}. "
            'To pass a complex data, use a complex type like named tuples, typed dicts, dataclasses or anything else.',
            category=RuntimeWarning,
        )

    class LambdaAsyncTransformer(AsyncTransformer[A, S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def signature(self) -> Signature:
            return func_signature

        async def transform_async(self, data: A) -> S:
            return await func(data)

    lambda_transformer = LambdaAsyncTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    lambda_transformer._label = func.__name__
    return lambda_transformer
