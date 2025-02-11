from typing import Any, Callable, Generic, ParamSpec, Sequence, TypeVar
from gloe.async_transformer import AsyncTransformer
from gloe.functional import _PartialTransformer, _PartialAsyncTransformer, Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_P1 = ParamSpec("_P1")

class TransformerEnsurer(Generic[_T, _S]):
    def validate_input(self, data: _T):
        pass

    def validate_output(self, data: _T, output: _S):
        pass

    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        return transformer.copy(lambda _, data: self.validate_and_transform(data, transformer))

    def validate_and_transform(self, data: _T, transformer: Transformer[_T, _S]) -> _S:
        self.validate_input(data)
        output = transformer.transform(data)
        self.validate_output(data, output)
        return output

def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    class LambdaEnsurer(TransformerEnsurer[_T, Any]):
        def validate_input(self, data: _T):
            func(data)
    return LambdaEnsurer()

def output_ensurer(func: Callable) -> TransformerEnsurer:
    class LambdaEnsurer(TransformerEnsurer):
        def validate_output(self, data, output):
            func(data, output) if len(func.__annotations__) > 1 else func(output)
    return LambdaEnsurer()

class _ensure_base:
    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        if isinstance(arg, AsyncTransformer):
            return self._generate_new_async_transformer(arg)
        if isinstance(arg, _PartialTransformer):
            return self._generate_new_partial_transformer(arg)
        if isinstance(arg, _PartialAsyncTransformer):
            return self._generate_new_partial_async_transformer(arg)

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        pass

    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        pass

    def _generate_new_partial_transformer(self, transformer_init: _PartialTransformer) -> _PartialTransformer:
        pass

    def _generate_new_partial_async_transformer(self, async_transformer_init: _PartialAsyncTransformer) -> _PartialAsyncTransformer:
        pass

# The rest of the code follows the same structure with similar modifications