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
        transform_exception = None

        transformed: O | None = None
        try:
            transformed = self.transform(data)
        except Exception as exception:
            if isinstance(exception.__cause__, TransformerException):
                transform_exception = exception.__cause__
            else:
                tb = traceback.extract_tb(exception.__traceback__)

                transformer_frames = [
                    frame
                    for frame in tb
                    if frame.name == self.__class__.__name__ or frame.name == "transform"
                ]

                if len(transformer_frames) == 1:
                    transformer_frame = transformer_frames[0]
                    exception_message = (
                        f'\n  File "{transformer_frame.filename}", line {transformer_frame.lineno}, '
                        f'in transformer "{self.__class__.__name__}"\n  '
                        f"  >> {transformer_frame.line}"
                    )
                else:
                    exception_message = (
                        f'An error occurred in transformer "{self.__class__.__name__}"'
                    )

                transform_exception = TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=exception_message,
                )

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if transformed is not None:
            return cast(O, transformed)

        raise NotImplementedError

    def __rshift__(self, next_node):
        if not isinstance(next_node, (BaseTransformer, tuple)):
            raise TypeError(f"Unsupported type for next_node: {type(next_node)}")

        return _compose_nodes(self, next_node)