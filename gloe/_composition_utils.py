import asyncio
import types
from inspect import Signature
from typing import TypeVar, Any, cast, Tuple, List

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.transformers import Transformer
from gloe._utils import _match_types, _specify_types, awaitify
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")


def is_transformer(node):
    return isinstance(node, (list, tuple)) and all(is_transformer(n) for n in node) if isinstance(node, (list, tuple)) else isinstance(node, Transformer)


def is_async_transformer(node):
    return isinstance(node, AsyncTransformer)


def has_any_async_transformer(node: List):
    return any(is_async_transformer(n) for n in node)


def _resolve_new_merge_transformers(
    new_transformer: BaseTransformer, _transformer2: BaseTransformer
):
    new_transformer.__class__.__name__ = _transformer2.__class__.__name__
    new_transformer._label = _transformer2.label
    new_transformer._children = _transformer2.children
    new_transformer._invisible = _transformer2.invisible
    new_transformer._graph_node_props = _transformer2.graph_node_props
    new_transformer._set_previous(_transformer2.previous)
    return new_transformer


def _resolve_serial_connection_signatures(
    _transformer2: BaseTransformer, generic_vars: dict, signature2: Signature
) -> Signature:
    first_param = list(signature2.parameters.values())[0]
    new_parameter = first_param.replace(
        annotation=_specify_types(_transformer2.input_type, generic_vars)
    )
    new_signature = signature2.replace(
        parameters=[new_parameter],
        return_annotation=_specify_types(signature2.return_annotation, generic_vars),
    )
    return new_signature


def _nerge_serial(transformer1, _transformer2):
    if transformer1.previous is None:
        transformer1 = transformer1.copy(regenerate_instance_id=True)

    _transformer2 = _transformer2.copy(regenerate_instance_id=True)
    _transformer2._set_previous(transformer1)

    signature1: Signature = transformer1.signature()
    signature2: Signature = _transformer2.signature()

    input_generic_vars = _match_types(
        _transformer2.input_type, signature1.return_annotation
    )
    output_generic_vars = _match_types(
        signature1.return_annotation, _transformer2.input_type
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
                _transformer2, generic_vars, signature2
            )

        def __len__(self):
            return len(transformer1) + len(