from typing import TypeVar, Any, cast
from inspect import Signature
from types import GenericAlias
import asyncio
import types

from gloe import BaseTransformer, Transformer, AsyncTransformer, UnsupportedTransformerArgException
from gloe._utils import _match_types, _specify_types

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

def is_transformer(node):
    return isinstance(node, Transformer)

def is_async_transformer(node):
    return isinstance(node, AsyncTransformer)

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

def _merge_serial(transformer1, transformer2):
    if transformer1.previous is None:
        transformer1 = transformer1.copy(regenerate_instance_id=True)

    transformer2 = transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)

    signature1: Signature = transformer1.signature()
    signature2: Signature = transformer2.signature()

    input_generic_vars = _match_types(transformer2.input_type, signature1.return_annotation)
    output_generic_vars = _match_types(signature1.return_annotation, transformer2.input_type)
    generic_vars = {**input_generic_vars, **output_generic_vars}

    def transformer1_signature(_) -> Signature:
        return signature1.replace(return_annotation=_specify_types(signature1.return_annotation, generic_vars))

    setattr(transformer1, "signature", types.MethodType(transformer1_signature, transformer1))

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(transformer2, generic_vars, signature2)

        def __len__(self):
            return len(transformer1) + len(transformer2)

    if is_transformer(transformer1) and is_transformer(transformer2):
        class NewTransformer(BaseNewTransformer, Transformer[_In, _NextOut]):
            def transform(self, data: _In) -> _NextOut:
                return transformer2(transformer1(data))

    elif is_async_transformer(transformer1) and is_transformer(transformer2):
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return transformer2(await transformer1(data))

    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):
        class NewTransformer(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return await transformer2(await transformer1(data))

    elif is_transformer(transformer1) and is_async_transformer(transformer2):
        class NewTransformer(AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                return await transformer2(transformer1(data))

    else:
        raise UnsupportedTransformerArgException(transformer2)

    return _resolve_new_merge_transformers(NewTransformer(), transformer2)

def _merge_diverging(incident_transformer, *receiving_transformers):
    if incident_transformer.previous is None:
        incident_transformer = incident_transformer.copy(regenerate_instance_id=True)

    receiving_transformers = tuple(receiving_transformer.copy(regenerate_instance_id=True) for receiving_transformer in receiving_transformers)

    for receiving_transformer in receiving_transformers:
        receiving_transformer._set_previous(incident_transformer)

    incident_signature: Signature = incident_transformer.signature()
    receiving_signatures: list[Signature] = []

    for receiving_transformer in receiving_transformers:
        generic_vars = _match_types(receiving_transformer.input_type, incident_signature.return_annotation)
        receiving_signature = receiving_transformer.signature()
        new_return_annotation = _specify_types(receiving_signature.return_annotation, generic_vars)
        receiving_signatures.append(receiving_signature.replace(return_annotation=new_return_annotation))

        def _signature(_) -> Signature:
            return new_return_annotation

        if receiving_transformer._previous == incident_transformer:
            setattr(receiving_transformer, "signature", types.MethodType(_signature, receiving_transformer))

    class BaseNewTransformer:
        def signature(self) -> Signature:
            receiving_signature_returns = [r.return_annotation for r in receiving_signatures]
            new_signature = incident_signature.replace(return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns)))
            return new_signature

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
                outputs = []
                for receiving_transformer in receiving_transformers:
                    output = await receiving_transformer(intermediate_result) if asyncio.iscoroutinefunction(receiving_transformer.__call__) else receiving_transformer(intermediate_result)
                    outputs.append(output)
                return tuple(outputs)

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