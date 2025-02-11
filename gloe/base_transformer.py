import copy
import types
import uuid
import inspect
from functools import cached_property
from inspect import Signature
from typing import Any, Callable, Generic, TypeVar, Union, cast, Iterable, get_args, get_origin, TypeAlias
from uuid import UUID
from itertools import groupby
from networkx import DiGraph, Graph

from gloe._utils import _format_return_annotation

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
    def __init__(
        self,
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
        self.events = []

    @property
    def label(self) -> str:
        """
        Label used in visualization.

        When the transformer is created by the `@transformer` decorator, it is the
        name of the function.

        When creating a transformer by extending the `Transformer` class, it is the name of
        the class.
        """
        return self._label

    @property
    def graph_node_props(self) -> dict[str, Any]:
        """
        Properties of the graph node.

        This includes the shape and other visual properties of the node.
        """
        return self._graph_node_props

    @property
    def children(self) -> list["BaseTransformer"]:
        """
        List of child transformers.

        These are the transformers that are directly downstream from this transformer.
        """
        return self._children

    @property
    def previous(self) -> PreviousTransformer["BaseTransformer"]:
        """
        Previous transformers. It can be None, a single transformer, or a tuple of many
        transformers.
        """
        return self._previous

    @property
    def invisible(self) -> bool:
        """
        Indicates whether the transformer is invisible in visualizations.

        Invisible transformers are not displayed in graphs but still participate in the
        transformation process.
        """
        return self._invisible

    def __hash__(self) -> int:
        """
        Returns a hash of the transformer's ID.

        This allows the transformer to be used as a key in dictionaries and sets.
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        Compares the transformer with another object for equality.

        Two transformers are considered equal if they have the same ID.
        """
        if isinstance(other, BaseTransformer):
            return self.id == other.id
        return NotImplemented

    def copy(
        self,
        transform: Callable[[_Self, _In], _Out] | None = None,
        regenerate_instance_id: bool = False,
    ) -> _Self:
        """
        Creates a deep copy of the transformer.

        Args:
            transform (Callable[[_Self, _In], _Out] | None): The transformation function to be used in the copy.
            regenerate_instance_id (bool): Whether to regenerate the instance ID.

        Returns:
            _Self: A deep copy of the transformer.
        """
        copied = copy.deepcopy(self)

        func_type = types.MethodType
        if transform is not None:
            setattr(copied, "transform", func_type(transform, copied))

        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        if self.previous is not None:
            copied._previous = self.previous.copy() if isinstance(self.previous, BaseTransformer) else self.previous

        copied._children = [child.copy(regenerate_instance_id=True) for child in self.children]

        return copied

    @property
    def graph_nodes(self) -> dict[UUID, "BaseTransformer"]:
        """
        Returns a dictionary of all graph nodes associated with this transformer.

        This includes the transformer itself and any previous or child transformers.
        """
        nodes = {self.instance_id: self}

        if self.previous is not None:
            nodes = {**nodes, **self.previous.graph_nodes}

        for child in self.children:
            nodes = {**nodes, **child.graph_nodes}

        return nodes

    def _set_previous(self, previous: PreviousTransformer):
        """
        Sets the previous transformers for this transformer.

        Args:
            previous (PreviousTransformer): The previous transformers.
        """
        self._previous = previous

    def signature(self) -> Signature:
        """
        Returns the signature of the transformer's transform method.

        This includes the input and output types.
        """
        return self._signature(type(self))

    def _signature(self, klass: type) -> Signature:
        """
        Helper method to get the signature of the transformer's transform method.

        Args:
            klass (type): The class type.

        Returns:
            Signature: The signature of the transform method.
        """
        orig_bases = getattr(self, "__orig_bases__", [])
        transformer_args = [
            get_args(base) for base in orig_bases if get_origin(base) == klass
        ]

        orig_class = getattr(self, "__orig_class__", None)

        specific_args = {}
        if orig_class is not None:
            generic_args = get_args(orig_class)
            if len(transformer_args) == 1 and len(generic_args) == 1:
                specific_args = {generic: specific for generic, specific in zip(generic_args, get_args(orig_class)) if generic in transformer_args[0]}

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
        """
        Returns the type of the output of the transformer.

        This is determined by the return type of the transform method.
        """
        return self.signature().return_annotation

    @property
    def output_annotation(self) -> str:
        """
        Returns the string representation of the output type.

        This is formatted using the _format_return_annotation function.
        """
        return _format_return_annotation(self.output_type, None, None)

    @property
    def input_type(self) -> Any:
        """
        Returns the type of the input of the transformer.

        This is determined by the first parameter's type in the transform method.
        """
        parameters = list(self.signature().parameters.items())
        return parameters[0][1].annotation if len(parameters) > 0 else None

    @property
    def input_annotation(self) -> str:
        """
        Returns the string representation of the input type.

        This is the name of the input type.
        """
        input_type = self.input_type
        return input_type.__name__ if input_type else "Unknown"

    def _add_net_node(self, net: DiGraph, custom_data: dict[str, Any] = {}):
        """
        Adds a node to the networkx graph.

        Args:
            net (DiGraph): The networkx graph.
            custom_data (dict[str, Any]): Additional data to be added as node attributes.

        Returns:
            str: The ID of the added node.
        """
        node_id = self.node_id
        props = {**self.graph_node_props, **custom_data, "label": self.label}
        if node_id not in net.nodes:
            net.add_node(node_id, **props)
        else:
            net.nodes[node_id].update(props)
        return node_id

    def _add_child_node(
        self,
        child: "BaseTransformer",
        child_net: DiGraph,
        parent_id: str,
        next_node: "BaseTransformer",
    ):
        """
        Adds a child node to the networkx graph.

        Args:
            child (BaseTransformer): The child transformer.
            child_net (DiGraph): The child's networkx graph.
            parent_id (str): The ID of the parent node.
            next_node (BaseTransformer): The next node in the transformation chain.
        """
        child._dag(child_net, next_node, custom_data={"parent_id": parent_id})

    @property
    def node_id(self) -> str:
        """
        Returns the ID of the transformer as a string.

        This is the string representation of the instance ID.
        """
        return str(self.instance_id)

    @cached_property
    def visible_previous(self) -> PreviousTransformer["BaseTransformer"]:
        """
        Returns the visible previous transformers.

        This excludes invisible previous transformers if they are not the first in the chain.
        """
        previous = self.previous

        if isinstance(previous, BaseTransformer):
            if previous.invisible:
                if previous.previous is None:
                    return previous

                return previous.visible_previous
            else:
                return previous

        return previous

    def _add_children_subgraph(self, net: DiGraph, next_node: "BaseTransformer"):
        """
        Adds a subgraph for the children nodes to the networkx graph.

        Args:
            net (DiGraph): The networkx graph.
            next_node (BaseTransformer): The next node in the transformation chain.
        """
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
                if type(visible_previous) == tuple:
                    for prev in visible_previous:
                        net.add_edge(prev.node_id, child_root_node, label=prev.output_annotation)
                elif isinstance(visible_previous, BaseTransformer):
                    net.add_edge(visible_previous.node_id, child_root_node, label=visible_previous.output_annotation)
            else:
                node_id = self._add_net_node(net)
                net.add_edge(node_id, child_root_node)

            if child_final_node != next_node_id:
                net.add_edge(child_final_node, next_node_id, label=next_node.input_annotation)

    def _dag(
        self,
        net: DiGraph,
        next_node: Union["BaseTransformer", None] = None,
        custom_data: dict[str, Any] = {},
    ):
        """
        Adds nodes and edges to the networkx graph to represent the transformer's position in the transformation chain.

        Args:
            net (DiGraph): The networkx graph.
            next_node (BaseTransformer | None): The next node in the transformation chain.
            custom_data (dict[str, Any]): Additional data to be added as node attributes.
        """
        in_nodes = [edge[1] for edge in net.in_edges()]

        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
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
        """
        Returns a networkx DiGraph representing the transformer's position in the transformation chain.

        This graph includes nodes and edges that visualize the transformer's relationship with its children and previous transformers.
        """
        net = DiGraph()
        net.graph["splines"] = "ortho"
        self._dag(net)
        return net

    def export(self, path: str, with_edge_labels: bool = True):
        """
        Exports the transformer's graph to a file in Graphviz format.

        Args:
            path (str): The path to the output file.
            with_edge_labels (bool): Whether to include edge labels in the exported graph.
        """
        net = self.graph()
        boxed_nodes = [
            node
            for node in net.nodes.data()
            if "parent_id" in node[1] and "bounding_box" in node[1]
        ]
        if not with_edge_labels:
            for u, v in net.edges:
                net.edges[u, v]["label"] = ""

        agraph = nx.nx_agraph.to_agraph(net)
        subgraphs: Iterable[tuple] = groupby(boxed_nodes, key=lambda x: x[1]["parent_id"])
        for parent_id, nodes in subgraphs:
            nodes = list(nodes)
            node_ids = [node[0] for node in nodes]
            if len(nodes) > 0:
                label = nodes[0][1]["box_label"]
                agraph.add_subgraph(
                    node_ids, label=label, name=f"cluster_{parent_id}", style="dotted"
                )
        agraph.write(path)

    def __len__(self):
        """
        Returns the length of the transformer.

        This is a placeholder implementation that always returns 1.
        """
        return 1