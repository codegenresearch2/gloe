from __future__ import annotations
import asyncio
from inspect import Signature
from types import GenericAlias
from typing import TypeVar, Any, cast

from gloe import Transformer, AsyncTransformer, BaseTransformer
from gloe._utils import _match_types, _specify_types
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

def is_transformer(node):
    return isinstance(node, Transformer) if not isinstance(node, (list, tuple)) else all(is_transformer(n) for n in node)

def is_async_transformer(node):
    return isinstance(node, AsyncTransformer)

def has_any_async_transformer(node: list):
    return any(is_async_transformer(n) for n in node)

def _resolve_new_merge_transformers(new_transformer: BaseTransformer, transformer2: BaseTransformer):
    new_transformer.__class__.__name__ = transformer2.__class__.__name__
    new_transformer._label = transformer2.label
    new_transformer._children = transformer2.children
    new_transformer._invisible = transformer2.invisible
    new_transformer._graph_node_props = transformer2.graph_node_props
    new_transformer._set_previous(transformer2.previous)
    return new_transformer

def _resolve_serial_connection_signatures(transformer2: BaseTransformer, generic_vars: dict, signature2: Signature) -> Signature:
    first_param = next(iter(signature2.parameters.values()))
    new_parameter = first_param.replace(annotation=_specify_types(transformer2.input_type, generic_vars))
    return signature2.replace(parameters=[new_parameter], return_annotation=_specify_types(signature2.return_annotation, generic_vars))

def _merge_serial(transformer1, _transformer2):
    transformer1 = transformer1.copy(regenerate_instance_id=True) if transformer1.previous is None else transformer1
    transformer2 = _transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)

    signature1, signature2 = transformer1.signature(), transformer2.signature()
    generic_vars = {**_match_types(transformer2.input_type, signature1.return_annotation), **_match_types(signature1.return_annotation, transformer2.input_type)}
    setattr(transformer1, "signature", lambda _: signature1.replace(return_annotation=_specify_types(signature1.return_annotation, generic_vars)))

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(transformer2, generic_vars, signature2)
        def __len__(self):
            return len(transformer1) + len(transformer2)

    if is_transformer(transformer1) and is_transformer(_transformer2):
        class NewTransformer(BaseNewTransformer, Transformer[_In, _NextOut]):
            def transform(self, data: _In) -> _NextOut:
                return transformer2(transformer1(data))
    elif is_async_transformer(transformer1) and is_transformer(_transformer2):
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return transformer2(await transformer1(data))
    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return await transformer2(await transformer1(data))
    elif is_transformer(transformer1) and is_async_transformer(_transformer2):
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return await transformer2(transformer1(data))
    else:
        raise UnsupportedTransformerArgException(transformer2)

    return _resolve_new_merge_transformers(NewTransformer(), transformer2)

def _merge_diverging(incident_transformer, *receiving_transformers):
    incident_transformer = incident_transformer.copy(regenerate_instance_id=True) if incident_transformer.previous is None else incident_transformer
    receiving_transformers = tuple(receiving_transformer.copy(regenerate_instance_id=True) for receiving_transformer in receiving_transformers)

    for receiving_transformer in receiving_transformers:
        receiving_transformer._set_previous(incident_transformer)

    incident_signature = incident_transformer.signature()
    receiving_signatures = [receiving_transformer.signature().replace(return_annotation=_specify_types(receiving_transformer.signature().return_annotation, _match_types(receiving_transformer.input_type, incident_signature.return_annotation))) for receiving_transformer in receiving_transformers]

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return incident_signature.replace(return_annotation=GenericAlias(tuple, tuple(r.return_annotation for r in receiving_signatures)))
        def __len__(self):
            return sum(len(t) for t in receiving_transformers) + len(incident_transformer)

    if is_transformer(incident_transformer) and is_transformer(receiving_transformers):
        class NewTransformer(BaseNewTransformer, Transformer[_In, tuple[Any, ...]]):
            def transform(self, data: _In) -> tuple[Any, ...]:
                intermediate_result = incident_transformer(data)
                return tuple(receiving_transformer(intermediate_result) for receiving_transformer in receiving_transformers)
    else:
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, tuple[Any, ...]]):
            async def transform_async(self, data: _In) -> tuple[Any, ...]:
                intermediate_result = await incident_transformer(data) if asyncio.iscoroutinefunction(incident_transformer.__call__) else incident_transformer(data)
                return tuple(await receiving_transformer(intermediate_result) if asyncio.iscoroutinefunction(receiving_transformer.__call__) else receiving_transformer(intermediate_result) for receiving_transformer in receiving_transformers)

    new_transformer = NewTransformer()
    new_transformer._previous = cast(Transformer, receiving_transformers)
    new_transformer.__class__.__name__ = "Converge"
    new_transformer._label = ""
    new_transformer._graph_node_props = {"shape": "diamond", "width": 0.5, "height": 0.5}

    return new_transformer

def _compose_nodes(current: BaseTransformer, next_node: tuple | BaseTransformer):
    if isinstance(current, BaseTransformer):
        if isinstance(next_node, BaseTransformer):
            return _merge_serial(current, next_node)
        elif isinstance(next_node, tuple) and all(isinstance(next_transformer, BaseTransformer) for next_transformer in next_node):
            return _merge_diverging(current, *next_node)
        else:
            raise UnsupportedTransformerArgException(next_node)
    else:
        raise UnsupportedTransformerArgException(next_node)