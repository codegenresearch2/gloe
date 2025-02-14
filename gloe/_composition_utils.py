import asyncio
from inspect import Signature
from typing import TypeVar, Any, cast

from gloe import AsyncTransformer, BaseTransformer, Transformer, UnsupportedTransformerArgException
from gloe._utils import _match_types, _specify_types

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

def _resolve_new_merge_transformers(new_transformer: BaseTransformer, transformer2: BaseTransformer):
    new_transformer.__class__.__name__ = transformer2.__class__.__name__
    new_transformer._label = transformer2.label
    new_transformer._children = transformer2.children
    new_transformer._invisible = transformer2.invisible
    new_transformer._graph_node_props = transformer2.graph_node_props
    new_transformer._set_previous(transformer2.previous)
    return new_transformer

def _resolve_serial_connection_signatures(transformer2: BaseTransformer, generic_vars: dict, signature2: Signature) -> Signature:
    first_param = list(signature2.parameters.values())[0]
    new_parameter = first_param.replace(annotation=_specify_types(transformer2.input_type, generic_vars))
    new_signature = signature2.replace(parameters=[new_parameter], return_annotation=_specify_types(signature2.return_annotation, generic_vars))
    return new_signature

def _merge_serial(transformer1: BaseTransformer, transformer2: BaseTransformer):
    transformer1 = transformer1.copy(regenerate_instance_id=True)
    transformer2 = transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)

    signature1: Signature = transformer1.signature()
    signature2: Signature = transformer2.signature()

    generic_vars = {**_match_types(transformer2.input_type, signature1.return_annotation),
                    **_match_types(signature1.return_annotation, transformer2.input_type)}

    transformer1.signature = lambda: signature1.replace(return_annotation=_specify_types(signature1.return_annotation, generic_vars))

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(transformer2, generic_vars, signature2)
        def __len__(self):
            return len(transformer1) + len(transformer2)

    new_transformer: BaseTransformer | None = None
    if isinstance(transformer1, Transformer) and isinstance(transformer2, Transformer):
        new_transformer = type("NewTransformer", (BaseNewTransformer, Transformer), {"transform": lambda self, data: transformer2(transformer1(data))})()
    elif isinstance(transformer1, AsyncTransformer) and isinstance(transformer2, Transformer):
        new_transformer = type("NewTransformer", (BaseNewTransformer, AsyncTransformer), {"transform_async": lambda self, data: transformer2(await transformer1(data))})()
    elif isinstance(transformer1, AsyncTransformer) and isinstance(transformer2, AsyncTransformer):
        new_transformer = type("NewTransformer", (BaseNewTransformer, AsyncTransformer), {"transform_async": lambda self, data: await transformer2(await transformer1(data))})()
    elif isinstance(transformer1, Transformer) and isinstance(transformer2, AsyncTransformer):
        new_transformer = type("NewTransformer", (AsyncTransformer,), {"transform_async": lambda self, data: await transformer2(transformer1(data))})()
    else:
        raise UnsupportedTransformerArgException(transformer2)

    return _resolve_new_merge_transformers(new_transformer, transformer2)

def _merge_diverging(incident_transformer: BaseTransformer, *receiving_transformers: BaseTransformer):
    incident_transformer = incident_transformer.copy(regenerate_instance_id=True)
    receiving_transformers = tuple(receiving_transformer.copy(regenerate_instance_id=True) for receiving_transformer in receiving_transformers)

    for receiving_transformer in receiving_transformers:
        receiving_transformer._set_previous(incident_transformer)

    incident_signature: Signature = incident_transformer.signature()
    receiving_signatures: list[Signature] = []

    for receiving_transformer in receiving_transformers:
        generic_vars = _match_types(receiving_transformer.input_type, incident_signature.return_annotation)
        receiving_signature = receiving_transformer.signature()
        receiving_transformer.signature = lambda: receiving_signature.replace(return_annotation=_specify_types(receiving_signature.return_annotation, generic_vars))
        receiving_signatures.append(receiving_transformer.signature())

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return incident_signature.replace(return_annotation=tuple(r.return_annotation for r in receiving_signatures))
        def __len__(self):
            return sum(len(t) for t in receiving_transformers) + len(incident_transformer)

    async def split_result_async(data: _In) -> tuple[Any, ...]:
        intermediate_result = await incident_transformer(data) if asyncio.iscoroutinefunction(incident_transformer.__call__) else incident_transformer(data)
        return tuple(await receiving_transformer(intermediate_result) if asyncio.iscoroutinefunction(receiving_transformer.__call__) else receiving_transformer(intermediate_result) for receiving_transformer in receiving_transformers)

    new_transformer = type("NewTransformer", (BaseNewTransformer, AsyncTransformer), {"transform_async": split_result_async})()

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