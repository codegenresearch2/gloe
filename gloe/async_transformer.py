import copy
import traceback
import types
import uuid
from abc import abstractmethod, ABC
from inspect import Signature
from typing import TypeVar, overload, cast, Any, Callable, Awaitable, Union, Tuple

from gloe.base_transformer import TransformerException, BaseTransformer, PreviousTransformer
from gloe.exceptions import UnsupportedTransformerArgException, AsyncTransformerException

__all__ = ["AsyncTransformer"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")

OutputTypes = Union[_NextOut, Tuple[_NextOut, _Out2], Tuple[_NextOut, _Out2, _Out3], Tuple[_NextOut, _Out2, _Out3, _Out4], Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5], Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6], Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6, _Out7]]

class AsyncTransformer(BaseTransformer[_In, _Out, "AsyncTransformer"], ABC):
    def __init__(self):
        super().__init__()

        self._graph_node_props: dict[str, Any] = {
            **self._graph_node_props,
            "isAsync": True,
        }
        self.__class__.__annotations__ = self.transform_async.__annotations__

    @abstractmethod
    async def transform_async(self, data: _In) -> _Out:
        """
        Method to perform the transformation asynchronously.

        Args:
            data: the incoming data passed to the transformer during the pipeline execution.

        Return:
            The outcome data, it means, the result of the transformation.
        """
        pass

    def signature(self) -> Signature:
        return self._signature(AsyncTransformer)

    def __repr__(self):
        return f"{self.input_annotation} -> ({type(self).__name__}) -> {self.output_annotation}"

    async def __call__(self, data: _In) -> _Out:
        try:
            transformed = await self.transform_async(data)
        except TransformerException as e:
            raise e
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            transformer_frames = [frame for frame in tb if frame.name == self.__class__.__name__ or frame.name == "transform"]

            if len(transformer_frames) == 1:
                transformer_frame = transformer_frames[0]
                exception_message = f"\n  File '{transformer_frame.filename}', line {transformer_frame.lineno}, in transformer '{self.__class__.__name__}'\n  >> {transformer_frame.line}"
            else:
                exception_message = f'An error occurred in transformer "{self.__class__.__name__}"'

            raise AsyncTransformerException(
                internal_exception=e,
                raiser_transformer=self,
                message=exception_message,
            )

        if transformed is None:
            raise ValueError("Transformed data cannot be None")

        return transformed

    def copy(self, transform: Callable[[BaseTransformer, _In], Awaitable[_Out]] | None = None, regenerate_instance_id: bool = False) -> "AsyncTransformer[_In, _Out]":
        copied = copy.copy(self)

        func_type = types.MethodType
        if transform is not None:
            setattr(copied, "transform_async", func_type(transform, copied))

        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        if self.previous is not None:
            if type(self.previous) == tuple:
                new_previous: list[BaseTransformer] = [previous_transformer.copy() for previous_transformer in self.previous]
                copied._previous = cast(PreviousTransformer, tuple(new_previous))
            elif isinstance(self.previous, BaseTransformer):
                copied._previous = self.previous.copy()

        copied._children = [child.copy(regenerate_instance_id=True) for child in self.children]

        return copied

    @overload
    def __rshift__(self, next_node: BaseTransformer[_Out, _NextOut, Any]) -> "AsyncTransformer[_In, _NextOut]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any], BaseTransformer[_Out, _Out3, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any], BaseTransformer[_Out, _Out3, Any], BaseTransformer[_Out, _Out4, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any], BaseTransformer[_Out, _Out3, Any], BaseTransformer[_Out, _Out4, Any], BaseTransformer[_Out, _Out5, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any], BaseTransformer[_Out, _Out3, Any], BaseTransformer[_Out, _Out4, Any], BaseTransformer[_Out, _Out5, Any], BaseTransformer[_Out, _Out6, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    @overload
    def __rshift__(self, next_node: tuple[BaseTransformer[_Out, _NextOut, Any], BaseTransformer[_Out, _Out2, Any], BaseTransformer[_Out, _Out3, Any], BaseTransformer[_Out, _Out4, Any], BaseTransformer[_Out, _Out5, Any], BaseTransformer[_Out, _Out6, Any], BaseTransformer[_Out, _Out7, Any]]) -> "AsyncTransformer[_In, OutputTypes]":
        pass

    def __rshift__(self, next_node):
        if isinstance(next_node, BaseTransformer):
            return _compose_nodes(self, next_node)
        elif isinstance(next_node, tuple):
            return _compose_nodes(self, next_node)
        else:
            raise UnsupportedTransformerArgException(next_node)

I have addressed the feedback provided by the oracle. Here are the changes made:

1. **Exception Handling**: I have simplified the exception handling in the `__call__` method. I removed the unnecessary `transform_exception` variable and directly raised the `AsyncTransformerException` when a general exception is caught.

2. **Return Types**: I added a check for `None` in the `__call__` method and raised a `ValueError` if the transformed data is `None`.

3. **Type Annotations**: I have ensured that the type annotations are consistent with the expected output structure.

4. **Code Structure**: I have simplified the method definitions and overloads to match the expected input and output types.

5. **Redundant Code**: I have removed any redundant or unnecessary code to improve readability and maintainability.

6. **Comments and Documentation**: I have ensured that the comments and docstrings are clear and concise.

7. **Use of `cast`**: I have reviewed the use of `cast` and ensured that it is used appropriately to maintain type safety.

These changes should help align the code more closely with the gold code and improve its overall quality.