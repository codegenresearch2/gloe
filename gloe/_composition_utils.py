import asyncio
import types
from inspect import Signature
from typing import TypeVar, Any, cast

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.transformers import Transformer
from gloe._utils import _match_types, _specify_types, awaitify
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")


def is_transformer(node: Any) -> bool:
    if type(node) == list or type(node) == tuple:
        return all(is_transformer(n) for n in node)
    return isinstance(node, Transformer)


def is_async_transformer(node: Any) -> bool:
    return isinstance(node, AsyncTransformer)


def has_any_async_transformer(node: list) -> bool:
    return any(is_async_transformer(n) for n in node)


def _resolve_new_merge_transformers(
    new_transformer: BaseTransformer, transformer2: BaseTransformer
) -> BaseTransformer:
    new_transformer.__class__.__name__ = transformer2.__class__.__name__
    new_transformer._label = transformer2.label
    new_transformer._children = transformer2.children
    new_transformer._invisible = transformer2.invisible
    new_transformer._graph_node_props = transformer2.graph_node_props
    new_transformer._set_previous(transformer2.previous)
    return new_transformer


def _resolve_serial_connection_signatures(
    transformer2: BaseTransformer, generic_vars: dict, signature2: Signature
) -> Signature:
    first_param = list(signature2.parameters.values())[0]
    new_parameter = first_param.replace(
        annotation=_specify_types(transformer2.input_type, generic_vars)
    )
    new_signature = signature2.replace(
        parameters=[new_parameter],
        return_annotation=_specify_types(signature2.return_annotation, generic_vars),
    )
    return new_signature


def _nerge_serial(transformer1: BaseTransformer, transformer2: BaseTransformer) -> BaseTransformer:
    if transformer1.previous is None:
        transformer1 = transformer1.copy(regenerate_instance_id=True)

    transformer2 = transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)

    signature1: Signature = transformer1.signature()
    signature2: Signature = transformer2.signature()

    input_generic_vars = _match_types(
        transformer2.input_type, signature1.return_annotation
    )
    output_generic_vars = _match_types(
        signature1.return_annotation, transformer2.input_type
    )
    generic_vars = {**input_generic_vars, **output_generic_vars}

    def transformer1_signature(_) -> Signature:
        return signature1.replace(
            return_annotation=_specify_types(signature1.return_annotation, generic_vars)
        )

    setattr(
        transformer1,
        "signature",
        types.MethodType(transformer1_signature, transformer1),
    )

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(
                transformer2, generic_vars, signature2
            )

        def __len__(self):
            return len(transformer1) + len(transformer2)

    new_transformer: BaseTransformer | None = None
    if is_transformer(transformer1) and is_transformer(transformer2):

        class NewTransformer1(BaseNewTransformer, Transformer[_In, _NextOut]):
            def transform(self, data: _In) -> _NextOut:
                transformer2_call = transformer2.__call__
                transformer1_call = transformer1.__call__
                transformed = transformer2_call(transformer1_call(data))
                return transformed

        new_transformer = NewTransformer1()

    elif is_async_transformer(transformer1) and is_transformer(transformer2):

        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = await transformer1(data)
                transformed = transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer2()

    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):

        class NewTransformer3(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = await transformer1(data)
                transformed = await transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer3()

    elif is_transformer(transformer1) and is_async_transformer(transformer2):

        class NewTransformer4(AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = transformer1(data)
                transformed = await transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer4()

    else:
        raise UnsupportedTransformerArgException(transformer2)

    return _resolve_new_merge_transformers(new_transformer, transformer2)