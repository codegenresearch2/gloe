from abc import abstractmethod, ABC
from typing import Any, Callable, Generic, ParamSpec, Sequence, TypeVar, cast, overload
from inspect import signature
from types import FunctionType
from gloe.async_transformer import AsyncTransformer
from gloe.functional import _PartialTransformer, _PartialAsyncTransformer, Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_P1 = ParamSpec("_P1")

class TransformerEnsurer(Generic[_T, _S], ABC):
    @abstractmethod
    def validate_input(self, data: _T):
        """Perform a validation on incoming data before executing the transformer code"""
        pass

    @abstractmethod
    def validate_output(self, data: _T, output: _S):
        """Perform a validation on outcome data after executing the transformer code"""
        pass

    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(this: Transformer, data: _T) -> _S:
            self.validate_input(data)
            output = transformer.transform(data)
            self.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    class LambdaEnsurer(TransformerEnsurer[_T, Any]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T):
            func(data)

        def validate_output(self, data: _T, output: Any):
            pass

    return LambdaEnsurer()

@overload
def output_ensurer(func: Callable[[_S], Any]) -> TransformerEnsurer[Any, _S]:
    pass

@overload
def output_ensurer(func: Callable[[_T, _S], Any]) -> TransformerEnsurer[_T, _S]:
    pass

def output_ensurer(func: Callable) -> TransformerEnsurer:
    class LambdaEnsurer(TransformerEnsurer):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: Any, output: Any):
            pass

        def validate_output(self, data: Any, output: Any):
            if len(signature(func).parameters) == 1:
                func(output)
            else:
                func(data, output)

    return LambdaEnsurer()

class _ensure_base:
    @overload
    def __call__(self, transformer: Transformer[_U, _S]) -> Transformer[_U, _S]:
        pass

    @overload
    def __call__(self, transformer_init: _PartialTransformer[_T, _P1, _U]) -> _PartialTransformer[_T, _P1, _U]:
        pass

    @overload
    def __call__(self, transformer: AsyncTransformer[_U, _S]) -> AsyncTransformer[_U, _S]:
        pass

    @overload
    def __call__(self, transformer_init: _PartialAsyncTransformer[_T, _P1, _U]) -> _PartialAsyncTransformer[_T, _P1, _U]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        if isinstance(arg, AsyncTransformer):
            return self._generate_new_async_transformer(arg)
        if isinstance(arg, _PartialTransformer):
            return self._generate_new_partial_transformer(arg)
        if isinstance(arg, _PartialAsyncTransformer):
            return self._generate_new_partial_async_transformer(arg)

    @abstractmethod
    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        pass

    @abstractmethod
    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        pass

    def _generate_new_partial_transformer(self, transformer_init: _PartialTransformer) -> _PartialTransformer:
        def ensured_transformer_init(*args, **kwargs):
            transformer = transformer_init(*args, **kwargs)
            return self._generate_new_transformer(transformer)
        return ensured_transformer_init

    def _generate_new_partial_async_transformer(self, async_transformer_init: _PartialAsyncTransformer) -> _PartialAsyncTransformer:
        def ensured_async_transformer_init(*args, **kwargs):
            async_transformer = async_transformer_init(*args, **kwargs)
            return self._generate_new_async_transformer(async_transformer)
        return ensured_async_transformer_init

# The rest of the code follows the same structure with similar modifications