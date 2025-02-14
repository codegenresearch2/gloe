import asyncio
from inspect import Signature
from types import GenericAlias
from typing import TypeVar, Any, cast

from gloe import AsyncTransformer, BaseTransformer, Transformer
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
    new_transformer._set_attributes(transformer2)
    return new_transformer

def _resolve_serial_connection_signatures(transformer2: BaseTransformer, generic_vars: dict, signature2: Signature) -> Signature:
    first_param = next(iter(signature2.parameters.values()))
    return signature2.replace(parameters=[first_param.replace(annotation=_specify_types(transformer2.input_type, generic_vars))], return_annotation=_specify_types(signature2.return_annotation, generic_vars))

def _merge_serial(transformer1, _transformer2):
    transformer1 = transformer1.copy(regenerate_instance_id=True)
    transformer2 = _transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)
    generic_vars = _match_types(transformer2.input_type, transformer1.signature().return_annotation)
    transformer1.signature = lambda: transformer1.signature().replace(return_annotation=_specify_types(transformer1.signature().return_annotation, generic_vars))
    return _resolve_new_merge_transformers(_create_new_transformer(transformer1, transformer2), transformer2)

def _merge_diverging(incident_transformer, *receiving_transformers):
    incident_transformer = incident_transformer.copy(regenerate_instance_id=True)
    receiving_transformers = tuple(receiving_transformer.copy(regenerate_instance_id=True) for receiving_transformer in receiving_transformers)
    for receiving_transformer in receiving_transformers:
        receiving_transformer._set_previous(incident_transformer)
    return _create_new_diverging_transformer(incident_transformer, receiving_transformers)

def _create_new_transformer(transformer1, transformer2):
    if is_transformer(transformer1) and is_transformer(transformer2):
        return Transformer[_In, _NextOut](lambda data: transformer2(transformer1(data)), transformer1.signature(), transformer2.signature())
    elif is_async_transformer(transformer1) and is_transformer(transformer2):
        return AsyncTransformer[_In, _NextOut](lambda data: transformer2(await transformer1(data)), transformer1.signature(), transformer2.signature())
    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):
        return AsyncTransformer[_In, _NextOut](lambda data: await transformer2(await transformer1(data)), transformer1.signature(), transformer2.signature())
    elif is_transformer(transformer1) and is_async_transformer(transformer2):
        return AsyncTransformer[_In, _NextOut](lambda data: await transformer2(transformer1(data)), transformer1.signature(), transformer2.signature())
    else:
        raise UnsupportedTransformerArgException(transformer2)

def _create_new_diverging_transformer(incident_transformer, receiving_transformers):
    if is_transformer(incident_transformer) and is_transformer(receiving_transformers):
        return Transformer[_In, tuple[Any, ...]](lambda data: tuple(receiving_transformer(incident_transformer(data)) for receiving_transformer in receiving_transformers), incident_transformer.signature(), [receiving_transformer.signature() for receiving_transformer in receiving_transformers])
    else:
        return AsyncTransformer[_In, tuple[Any, ...]](lambda data: asyncio.gather(*(receiving_transformer(await incident_transformer(data)) for receiving_transformer in receiving_transformers)), incident_transformer.signature(), [receiving_transformer.signature() for receiving_transformer in receiving_transformers])

def _compose_nodes(current: BaseTransformer, next_node: tuple | BaseTransformer):
    if isinstance(current, BaseTransformer):
        if isinstance(next_node, BaseTransformer):
            return _merge_serial(current, next_node)
        elif isinstance(next_node, tuple):
            return _merge_diverging(current, *next_node) if all(isinstance(next_transformer, BaseTransformer) for next_transformer in next_node) else UnsupportedTransformerArgException(next((elem for elem in next_node if not isinstance(elem, BaseTransformer))))
        else:
            raise UnsupportedTransformerArgException(next_node)
    else:
        raise UnsupportedTransformerArgException(current)