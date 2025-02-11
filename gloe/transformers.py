import traceback
from abc import ABC, abstractmethod
from inspect import Signature
from typing import (
    TypeVar,
    overload,
    cast,
    Any,
    TypeAlias,
    Union,
)

from gloe.base_transformer import BaseTransformer, TransformerException
from gloe.async_transformer import AsyncTransformer

__all__ = ["Transformer"]

I = TypeVar("I")
O = TypeVar("O")

Tr: TypeAlias = "Transformer"
AT: TypeAlias = AsyncTransformer
BT: TypeAlias = BaseTransformer[I, O, Any]

AsyncNext2 = Union[
    tuple[AT[O, O], BT[O, O]],
    tuple[BT[O, O], AT[O, O]],
]

AsyncNext3 = Union[
    tuple[AT[O, O], BT[O, O], BT[O, O]],
    tuple[BT[O, O], AT[O, O], BT[O, O]],
    tuple[BT[O, O], BT[O, O], AT[O, O]],
]

class Transformer(BaseTransformer[I, O, "Transformer"], ABC):
    """
    A Transformer is the generic block with the responsibility to take an input of type
    `T` and transform it to an output of type `S`.

    See Also:
        Read more about this feature in the page :ref:`creating-a-transformer`.

    Example:
        Typical usage example::

            class Stringifier(Transformer[dict, str]):
                ...
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
            return self.transform(data)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            transformer_frames = [
                frame
                for frame in tb
                if frame.name == self.__class__.__name__ or frame.name == "transform"
            ]

            if len(transformer_frames) == 1:
                transformer_frame = transformer_frames[0]
                exception_message = (
                    f"\n  "
                    f'File "{transformer_frame.filename}", line {transformer_frame.lineno}, '
                    f'in transformer "{self.__class__.__name__}"\n  '
                    f"  >> {transformer_frame.line}"
                )
            else:
                exception_message = (
                    f'An error occurred in transformer "{self.__class__.__name__}"'
                )

            raise TransformerException(
                internal_exception=e,
                raiser_transformer=self,
                message=exception_message,
            )

    @overload
    def __rshift__(self, next_node: "Tr[O, O]") -> "Tr[I, O]":
        pass

    @overload
    def __rshift__(self, next_node: AsyncTransformer[O, O]) -> AsyncTransformer[I, O]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[O, O]", "Tr[O, O]"],
    ) -> "Tr[I, tuple[O, O]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node