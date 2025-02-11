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

class _PartialTransformer(Generic[A, P1, S]):
    def __init__(self, func: Callable[Concatenate[A, P1], S]):
        self.func = func

    def __call__(self, *args: P1.args, **kwargs: P1.kwargs) -> Transformer[A, S]:
        func = self.func
        func_signature = inspect.signature(func)

        class LambdaTransformer(Transformer[A, S]):
            """
            Transformer class created from a function with partial application of arguments.
            """
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
    """
    Decorator to create a partial transformer from a function.

    Args:
        func: A callable with one or more arguments. The first argument is of
            type :code:`A`. The subsequent arguments are retained for use during
            transformer instantiation. This callable returns a value of type
            :code:`S`.

    Returns:
        An instance of the :code:`_PartialTransformer`, an internal class utilized within
        Gloe that facilitates partial instantiation of transformers by the user.
    """
    return _PartialTransformer(func)

class _PartialAsyncTransformer(Generic[A, P1, S]):
    def __init__(self, func: Callable[Concatenate[A, P1], Awaitable[S]]):
        self.func = func

    def __call__(self, *args: P1.args, **kwargs: P1.kwargs) -> AsyncTransformer[A, S]:
        func = self.func
        func_signature = inspect.signature(func)

        class LambdaTransformer(AsyncTransformer[A, S]):
            """
            AsyncTransformer class created from a function with partial application of arguments.
            """
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
    """
    Decorator to create a partial async transformer from a function.

    Args:
        func: A callable with one or more arguments, the first of which is of type `A`.
            Remaining arguments are preserved for later use during the instantiation of
            the transformer. This callable must asynchronously return a result of type
            `S`, indicating an operation that produces an output of type `S` upon
            completion.

    Returns:
        An instance of the :code:`_PartialAsyncTransformer`, an internally managed class
        within Gloe designed to facilitate the partial instantiation of asynchronous
        transformers.
    """
    return _PartialAsyncTransformer(func)

def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    """
    Convert a callable to an instance of the Transformer class.

    Args:
        func: A callable that takes a single argument and returns a result. The callable
            should return an instance of the generic type :code:`S` specified.

    Returns:
        An instance of the Transformer class, encapsulating the transformation logic
        defined in the provided callable.
    """
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformers. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning,
        )

    class LambdaTransformer(Transformer[A, S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def signature(self) -> Signature:
            return func_signature

        def transform(self, data):
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    lambda_transformer._label = func.__name__
    return lambda_transformer

def async_transformer(func: Callable[[A], Awaitable[S]]) -> AsyncTransformer[A, S]:
    """
    Convert a callable to an instance of the AsyncTransformer class.

    Args:
        func: A callable that takes a single argument and returns a coroutine.

    Returns:
        Returns an instance of the AsyncTransformer class, representing the built async
        transformer.
    """
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformers. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning,
        )

    class LambdaAsyncTransformer(AsyncTransformer[A, S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def signature(self) -> Signature:
            return func_signature

        async def transform_async(self, data):
            return await func(data)

    lambda_transformer = LambdaAsyncTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    lambda_transformer._label = func.__name__
    return lambda_transformer