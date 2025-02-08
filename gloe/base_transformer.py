import copy
import types
import uuid
import inspect
from functools import cached_property
from typing import Any, Callable, Generic, TypeVar, Union, Iterable, get_args, get_origin, TypeAlias, Type
from uuid import UUID
from itertools import groupby

from gloe._utils import _format_return_annotation
import networkx as nx

__all__ = ["BaseTransformer", "TransformerException", "PreviousTransformer"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")
_Self = TypeVar("_Self", bound="BaseTransformer")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")

PreviousTransformer: TypeAlias = Union[
    None,
    _Self,
    tuple[_Self, _Self],
    tuple[_Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self, _Self, _Self],
]

class TransformerException(Exception):
    def __init__(self,
        internal_exception: Union["TransformerException", Exception],
        raiser_transformer: "BaseTransformer",
        message: str | None = None,
    ):
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
        self._previous: PreviousTransformer["BaseTransformer"] = None
        self._children: list["BaseTransformer"] = []
        self._invisible = False
        self.id = uuid.uuid4()
        self.instance_id = uuid.uuid4()
        self._label = self.__class__.__name__
        self._graph_node_props: dict[str, Any] = {"shape": "box"}

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
    def previous(self) -> PreviousTransformer["BaseTransformer"]:
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

    def copy(self,
        transform: Callable[[_Self, _In], _Out] | None = None,
        regenerate_instance_id: bool = False,
    ) -> _Self:
        copied = copy.copy(self)

        if transform is not None:
            setattr(copied, "transform", types.MethodType(transform, copied))

        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        if self.previous is not None:
            copied._previous = self.previous.copy() if isinstance(self.previous, BaseTransformer) else self.previous

        copied._children = [child.copy(regenerate_instance_id=True) for child in self.children]

        return copied

    @cached_property
    def visible_previous(self) -> PreviousTransformer["BaseTransformer"]:
        previous = self.previous

        if isinstance(previous, BaseTransformer):
            if previous.invisible:
                if previous.previous is None:
                    return previous

                if type(previous.previous) == tuple:
                    return previous.previous

                return previous.visible_previous
            else:
                return previous

        return previous

    def _set_previous(self, previous: PreviousTransformer):
        self._previous = previous

    def signature(self) -> Signature:
        return self._signature(type(self))

    def _signature(self, klass: Type) -> Signature:
        orig_bases = getattr(self, "__orig_bases__", [])
        transformer_args = [get_args(base) for base in orig_bases if get_origin(base) == klass]

        orig_class = getattr(self, "__orig_class__", None)

        specific_args = {}
        if len(transformer_args) == 1 and len(get_args(orig_class)) == 1:
            specific_args = {generic: specific for generic, specific in zip(get_args(orig_class)[0], transformer_args[0])}

        signature = inspect.signature(self.transform)
        new_return_annotation = specific_args.get(signature.return_annotation, signature.return_annotation)
        parameters = list(signature.parameters.values())
        if len(parameters) > 0:
            parameter = parameters[0]
            parameter = parameter.replace(annotation=specific_args.get(parameter.annotation, parameter.annotation))
            return signature.replace(return_annotation=new_return_annotation, parameters=[parameter])

        return signature.replace(return_annotation=new_return_annotation)

    @property
    def output_type(self) -> Any:
        return self.signature().return_annotation

    @property
    def output_annotation(self) -> str:
        return _format_return_annotation(self.output_type, None, None)

    @property
    def input_type(self) -> Any:
        parameters = list(self.signature().parameters.items())
        return parameters[0][1].annotation if len(parameters) > 0 else None

    @property
    def input_annotation(self) -> str:
        return self.input_type.__name__

    def _add_net_node(self, net: nx.Graph, custom_data: dict[str, Any] = {}) -> str:
        node_id = self.node_id
        props = {**self.graph_node_props, **custom_data, "label": self.label}
        if node_id not in net.nodes():
            net.add_node(node_id, **props)
        else:
            nx.set_node_attributes(net, {node_id: props})
        return node_id

    def _add_child_node(self, child: "BaseTransformer", child_net: nx.DiGraph, parent_id: str, next_node: "BaseTransformer"):
        child._dag(child_net, next_node, custom_data={"parent_id": parent_id})

    @property
    def node_id(self) -> str:
        return str(self.instance_id)

    def _add_children_subgraph(self, net: nx.DiGraph, next_node: "BaseTransformer"):
        next_node_id = next_node.node_id
        children_nets = [nx.DiGraph() for _ in self.children]

        for child, child_net in zip(self.children, children_nets):
            self._add_child_node(child, child_net, self.node_id, next_node)
            net.add_nodes_from(child_net.nodes.data())
            net.add_edges_from(child_net.edges.data())

            child_root_node = [n for n in child_net.nodes if child_net.in_degree(n) == 0][0]
            child_final_node = [n for n in child_net.nodes if child_net.out_degree(n) == 0][0]

            if child_final_node != next_node_id:
                net.add_edge(child_final_node, next_node_id, label=next_node.input_annotation)

    def _dag(self, net: nx.DiGraph, next_node: Union["BaseTransformer", None] = None, custom_data: dict[str, Any] = {}) -> None:
        in_nodes = [edge[1] for edge in net.in_edges()]

        if self.previous is not None:
            if isinstance(self.previous, BaseTransformer):
                previous_node_id = self.previous.node_id

                if len(self.previous.children) == 0 and (not self.previous.invisible or self.previous.previous is None):
                    previous_node_id = self.previous._add_net_node(net)
                    net.add_edge(previous_node_id, next_node.node_id if next_node else self.node_id, label=self.previous.output_annotation)

                if previous_node_id not in in_nodes:
                    self.previous._dag(net, next_node, custom_data)
            elif isinstance(self.previous, tuple):
                for prev in self.previous:
                    previous_node_id = prev.node_id

                    if not prev.invisible and len(prev.children) == 0:
                        net.add_edge(previous_node_id, next_node.node_id if next_node else self.node_id, label=prev.output_annotation)

                    if previous_node_id not in in_nodes:
                        prev._dag(net, next_node, custom_data)
        else:
            self._add_net_node(net, custom_data)

        if len(self.children) > 0 and next_node is not None:
            self._add_children_subgraph(net, next_node)

    def graph(self) -> nx.DiGraph:
        net = nx.DiGraph()
        net.graph["splines"] = "ortho"
        self._dag(net)
        return net

    def export(self, path: str, with_edge_labels: bool = True):
        net = self.graph()
        boxed_nodes = [
            node
            for node in net.nodes.data()
            if "parent_id" in node[1] and "bounding_box" in node[1]
        ]
        if not with_edge_labels:
            for u, v in net.edges():
                net.edges[u, v]["label"] = ""

        agraph = nx.nx_agraph.to_agraph(net)
        subgraphs: Iterable[tuple] = groupby(boxed_nodes, key=lambda x: x[1]["parent_id"])
        for parent_id, nodes in subgraphs:
            nodes = list(nodes)
            node_ids = [node[0] for node in nodes]
            if len(nodes) > 0:
                label = nodes[0][1]["box_label"]
                agraph.add_subgraph(node_ids, label=label, name=f"cluster_{parent_id}", style="dotted")
        agraph.write(path)

    def __len__(self):
        return 1
