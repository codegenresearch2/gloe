import asyncio
import copy
import types
import uuid
from inspect import Signature
from typing import Any, Callable, Generic, TypeVar, Union, cast
from uuid import UUID

from networkx import DiGraph, Graph

from gloe._composition_utils import (
    _compose_nodes,
    _match_types,
    _specify_types,
    is_async_transformer,
    is_transformer,
)
from gloe._utils import _format_return_annotation
from gloe.exceptions import UnsupportedTransformerArgException

__all__ = ["BaseTransformer", "TransformerException"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_Self = TypeVar("_Self", bound="BaseTransformer")

PreviousTransformer = Union[None, _Self, tuple[_Self, ...]]

class TransformerException(Exception):
    def __init__(self, internal_exception: Exception, raiser_transformer: "BaseTransformer", message: str | None = None):
        self._internal_exception = internal_exception
        self.raiser_transformer = raiser_transformer
        self._traceback = internal_exception.__traceback__
        internal_exception.__cause__ = self
        super().__init__(message)

    @property
    def internal_exception(self):
        return self._internal_exception.with_traceback(self._traceback)

class BaseTransformer(Generic[_In, _Out, _Self]):
    def __init__(self):
        self._previous: PreviousTransformer = None
        self._children: list["BaseTransformer"] = []
        self._invisible = False
        self.id = uuid.uuid4()
        self.instance_id = uuid.uuid4()
        self._label = self.__class__.__name__
        self._graph_node_props: dict[str, Any] = {"shape": "box"}
        self.events = []

    @property
    def label(self) -> str:
        return self._label

    @property
    def graph_node_props(self) -> dict[str, Any]:
        return self._graph_node_props

    @property
    def children(self) -> list["BaseTransformer"]:
        return self._children

    @property
    def previous(self) -> PreviousTransformer:
        return self._previous

    @property
    def invisible(self) -> bool:
        return self._invisible

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, BaseTransformer):
            return self.id == other.id
        return NotImplemented

    def copy(self, transform: Callable[[_Self, _In], _Out] | None = None, regenerate_instance_id: bool = False) -> _Self:
        copied = copy.copy(self)
        if transform is not None:
            setattr(copied, "transform", types.MethodType(transform, copied))
        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()
        if self.previous is not None:
            if isinstance(self.previous, tuple):
                copied._previous = tuple(prev.copy() for prev in self.previous)
            else:
                copied._previous = self.previous.copy()
        copied._children = [child.copy(regenerate_instance_id=True) for child in self.children]
        return copied

    @property
    def graph_nodes(self) -> dict[UUID, "BaseTransformer"]:
        nodes = {self.instance_id: self}
        if self.previous is not None:
            if isinstance(self.previous, tuple):
                for prev in self.previous:
                    nodes = {**nodes, **prev.graph_nodes}
            else:
                nodes = {**nodes, **self.previous.graph_nodes}
        for child in self.children:
            nodes = {**nodes, **child.graph_nodes}
        return nodes

    def _set_previous(self, previous: PreviousTransformer):
        if self.previous is None:
            self._previous = previous
        elif isinstance(self.previous, tuple):
            for previous_transformer in self.previous:
                previous_transformer._set_previous(previous)
        else:
            self.previous._set_previous(previous)

    def signature(self) -> Signature:
        signature = self._signature(type(self))
        if self.previous is not None:
            if isinstance(self.previous, tuple):
                for prev in self.previous:
                    signature = self._resolve_signature(prev.signature(), signature)
            else:
                signature = self._resolve_signature(self.previous.signature(), signature)
        return signature

    def _resolve_signature(self, prev_signature: Signature, signature: Signature) -> Signature:
        input_generic_vars = _match_types(self.input_type, prev_signature.return_annotation)
        output_generic_vars = _match_types(prev_signature.return_annotation, self.input_type)
        generic_vars = {**input_generic_vars, **output_generic_vars}
        return signature.replace(return_annotation=_specify_types(signature.return_annotation, generic_vars))

    @property
    def output_type(self) -> Any:
        return self.signature().return_annotation

    @property
    def output_annotation(self) -> str:
        return _format_return_annotation(self.output_type, None, None)

    @property
    def input_type(self) -> Any:
        return list(self.signature().parameters.values())[0].annotation

    @property
    def input_annotation(self) -> str:
        return self.input_type.__name__

    def _add_net_node(self, net: Graph, custom_data: dict[str, Any] = {}):
        node_id = self.node_id
        props = {**self.graph_node_props, **custom_data, "label": self.label}
        if node_id not in net.nodes:
            net.add_node(node_id, **props)
        else:
            net.nodes[node_id].update(props)
        return node_id

    def _add_child_node(self, child: "BaseTransformer", child_net: DiGraph, parent_id: str, next_node: "BaseTransformer"):
        child._dag(child_net, next_node, custom_data={"parent_id": parent_id})

    @property
    def node_id(self) -> str:
        return str(self.instance_id)

    @property
    def visible_previous(self) -> PreviousTransformer:
        previous = self.previous
        if isinstance(previous, BaseTransformer):
            if previous.invisible:
                if previous.previous is None:
                    return previous
                if isinstance(previous.previous, tuple):
                    return previous.previous
                return previous.visible_previous
            else:
                return previous
        return previous

    def _add_children_subgraph(self, net: DiGraph, next_node: "BaseTransformer"):
        next_node_id = next_node.node_id
        children_nets = [DiGraph() for _ in self.children]
        visible_previous = self.visible_previous
        for child, child_net in zip(self.children, children_nets):
            self._add_child_node(child, child_net, self.node_id, next_node)
            net.add_nodes_from(child_net.nodes.data())
            net.add_edges_from(child_net.edges.data())
            child_root_node = [n for n in child_net.nodes if child_net.in_degree(n) == 0][0]
            child_final_node = [n for n in child_net.nodes if child_net.out_degree(n) == 0][0]
            if self.invisible:
                if isinstance(visible_previous, tuple):
                    for prev in visible_previous:
                        net.add_edge(prev.node_id, child_root_node, label=prev.output_annotation)
                elif isinstance(visible_previous, BaseTransformer):
                    net.add_edge(visible_previous.node_id, child_root_node, label=visible_previous.output_annotation)
            else:
                node_id = self._add_net_node(net)
                net.add_edge(node_id, child_root_node)
            if child_final_node != next_node_id:
                net.add_edge(child_final_node, next_node_id, label=next_node.input_annotation)

    def _dag(self, net: DiGraph, next_node: Union["BaseTransformer", None] = None, custom_data: dict[str, Any] = {}):
        in_nodes = [edge[1] for edge in net.in_edges()]
        previous = self.previous
        if previous is not None:
            if isinstance(previous, tuple):
                if self.invisible and next_node is not None:
                    next_node_id = next_node._add_net_node(net)
                    _next_node = next_node
                else:
                    next_node_id = self._add_net_node(net, custom_data)
                    _next_node = self
                for prev in previous:
                    previous_node_id = prev.node_id
                    if not prev.invisible and len(prev.children) == 0:
                        net.add_edge(previous_node_id, next_node_id, label=prev.output_annotation)
                    if previous_node_id not in in_nodes:
                        prev._dag(net, _next_node, custom_data)
            elif isinstance(previous, BaseTransformer):
                if self.invisible and next_node is not None:
                    next_node_id = next_node._add_net_node(net)
                    _next_node = next_node
                else:
                    next_node_id = self._add_net_node(net, custom_data)
                    _next_node = self
                previous_node_id = previous.node_id
                if len(previous.children) == 0 and (not previous.invisible or previous.previous is None):
                    previous_node_id = previous._add_net_node(net)
                    net.add_edge(previous_node_id, next_node_id, label=previous.output_annotation)
                if previous_node_id not in in_nodes:
                    previous._dag(net, _next_node, custom_data)
        else:
            self._add_net_node(net, custom_data)
        if len(self.children) > 0 and next_node is not None:
            self._add_children_subgraph(net, next_node)

    def graph(self) -> DiGraph:
        net = DiGraph()
        net.graph["splines"] = "ortho"
        self._dag(net)
        return net

    def __len__(self):
        return 1

    def __call__(self, data: _In) -> _Out:
        if is_async_transformer(self):
            return asyncio.run(self.transform_async(data))
        else:
            return self.transform(data)

    def __rshift__(self, next_node: Union["BaseTransformer", tuple["BaseTransformer", ...]]) -> "BaseTransformer":
        return _compose_nodes(self, next_node)