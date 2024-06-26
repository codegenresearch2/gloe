import asyncio
from typing import Any, TypeVar, Union

from typing_extensions import TypeAlias

from gloe.async_transformer import AsyncTransformer, _execute_async_flow
from gloe.base_transformer import BaseTransformer
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _gateway_factory
from gloe.transformers import Transformer, _execute_flow

_In = TypeVar("_In")


Trf: TypeAlias = Transformer
BTrf: TypeAlias = BaseTransformer
ATrf: TypeAlias = AsyncTransformer


class _Parallel(_base_gateway[_In], Transformer[_In, tuple[Any, ...]]):
    def transform(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            result = _execute_flow(transformer._flow, data)
            results.append(result)
        return tuple(results)


class _ParallelAsync(_base_gateway[_In], AsyncTransformer[_In, tuple[Any, ...]]):
    async def transform_async(self, data: _In) -> tuple[Any, ...]:
        results = [None] * len(self._children)
        indexed_children = list(enumerate(self._children))

        async_children = [
            (i, child)
            for i, child in indexed_children
            if isinstance(child, AsyncTransformer)
        ]
        sync_children = [
            (i, child)
            for i, child in indexed_children
            if isinstance(child, Transformer)
        ]

        async_results = await asyncio.gather(
            *[_execute_async_flow(child._flow, data) for _, child in async_children]
        )
        sync_results = [_execute_flow(child._flow, data) for _, child in sync_children]

        for (i, _), result in zip(async_children, async_results):
            results[i] = result

        for (i, _), result in zip(sync_children, sync_results):
            results[i] = result

        return tuple(results)


@_gateway_factory
def parallel(*transformers: BaseTransformer) -> Union[Transformer, AsyncTransformer]:
    """
    Currently, the parallelism of transformers is supported only by executing async
    transformers concurrently.

    Args:
        *transformers (Sequence[Transformer | AsyncTransformer]): the list of
            transformers what will receive the same input.

    Returns:
        Union[Transformer, AsyncTransformer]: a transformer that will execute all the
            transformers in parallel and return a tuple with the results. If at least
            one of the transformers passed is an AsyncTransformer, the returned
            transformer is also an AsyncTransformer. Otherwise, the returned transformer
            is sync.
    """
    if any(isinstance(t, AsyncTransformer) for t in transformers):
        return _ParallelAsync(*transformers)
    return _Parallel(*transformers)
