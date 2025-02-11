import traceback
from abc import ABC, abstractmethod
from inspect import Signature
from typing import TypeVar, overload, cast, Any, TypeAlias, Union

from gloe.base_transformer import BaseTransformer, TransformerException
from gloe.async_transformer import AsyncTransformer
from gloe._composition_utils import _compose_nodes

__all__ = ["Transformer"]

I = TypeVar("I")
O = TypeVar("O")
O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")

Tr: TypeAlias = "Transformer"
AT: TypeAlias = AsyncTransformer
BT: TypeAlias = BaseTransformer[I, O, Any]

class Transformer(BaseTransformer[I, O, "Transformer"], ABC):
    """
    A Transformer is the generic block with the responsibility to take an input of type
    `T` and transform it to an output of type `S`.
    """

    def __init__(self):
        super().__init__()
        self.__class__.__annotations__ = self.transform.__annotations__

    @abstractmethod
    def transform(self, data: I) -> O:
        """Main method to be implemented and responsible to perform the transformer logic"""

    def signature(self) -> Signature:
        return self._signature(Transformer)

    def __repr__(self):
        return f"{self.input_annotation} -> ({type(self).__name__}) -> {self.output_annotation}"

    def __call__(self, data: I) -> O:
        try:
            transformed = self.transform(data)
        except Exception as exception:
            if isinstance(exception.__cause__, TransformerException):
                raise exception.__cause__.internal_exception
            else:
                tb = traceback.extract_tb(exception.__traceback__)
                transformer_frames = [
                    frame
                    for frame in tb
                    if frame.name == self.__class__.__name__ or frame.name == "transform"
                ]
                exception_message = (
                    f'\n  File "{transformer_frames[0].filename}", line {transformer_frames[0].lineno}, '
                    f'in transformer "{self.__class__.__name__}"\n  '
                    f"  >> {transformer_frames[0].line}"
                    if len(transformer_frames) == 1
                    else f'An error occurred in transformer "{self.__class__.__name__}"'
                )
                raise TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=exception_message,
                ).internal_exception

        return cast(O, transformed)

    def __rshift__(self, next_node: Union[BT, tuple[BT, ...]]) -> BT:
        return _compose_nodes(self, next_node)