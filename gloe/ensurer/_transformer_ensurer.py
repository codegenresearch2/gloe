from abc import abstractmethod, ABC
from types import FunctionType
from typing import Any, Callable, Generic, ParamSpec, Sequence, TypeVar, cast

from gloe.async_transformer import AsyncTransformer
from gloe.functional import _PartialTransformer, _PartialAsyncTransformer, Transformer

T = TypeVar('T')
S = TypeVar('S')
U = TypeVar('U')
P1 = ParamSpec('P1')

class TransformerEnsurer(Generic[T, S], ABC):
    @abstractmethod
    def validate_input(self, data: T):
        pass

    @abstractmethod
    def validate_output(self, data: T, output: S):
        pass

    def __call__(self, transformer: Transformer[T, S]) -> Transformer[T, S]:
        def transform(this: Transformer, data: T) -> S:
            self.validate_input(data)
            output = transformer.transform(data)
            self.validate_output(data, output)
            return output

        return transformer.copy(transform)

def input_ensurer(func: Callable[[T], Any]) -> TransformerEnsurer[T, Any]:
    class LambdaEnsurer(TransformerEnsurer[T, S]):
        def validate_input(self, data: T):
            func(data)

        def validate_output(self, data: T, output: S):
            pass

    return LambdaEnsurer()

def output_ensurer(func: Callable) -> TransformerEnsurer:
    class LambdaEnsurer(TransformerEnsurer):
        def validate_input(self, data):
            pass

        def validate_output(self, data, output):
            if len(func.__annotations__) == 2:
                func(data, output)
            else:
                func(output)

    return LambdaEnsurer()

class _ensure_base:
    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        if isinstance(arg, AsyncTransformer):
            return self._generate_new_async_transformer(arg)
        if isinstance(arg, _PartialTransformer):
            return self._wrap_partial_transformer(arg)
        if isinstance(arg, _PartialAsyncTransformer):
            return self._wrap_partial_async_transformer(arg)

    @abstractmethod
    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        pass

    @abstractmethod
    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        pass

    def _wrap_partial_transformer(self, transformer_init: _PartialTransformer[T, P1, U]):
        def ensured_transformer_init(*args, **kwargs):
            transformer = transformer_init(*args, **kwargs)
            return self._generate_new_transformer(transformer)

        return ensured_transformer_init

    def _wrap_partial_async_transformer(self, async_transformer_init: _PartialAsyncTransformer[T, P1, U]):
        def ensured_async_transformer_init(*args, **kwargs):
            async_transformer = async_transformer_init(*args, **kwargs)
            return self._generate_new_async_transformer(async_transformer)

        return ensured_async_transformer_init

class _ensure_incoming(Generic[T], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[T], Any]]):
        self.input_ensurers_instances = [input_ensurer(ensurer) for ensurer in incoming]

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            return output

        return transformer.copy(transform)

    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        async def transform_async(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = await transformer.transform_async(data)
            return output

        return transformer.copy(transform_async)

class _ensure_outcome(Generic[S], _ensure_base):
    def __init__(self, outcome: Sequence[Callable[[S], Any]]):
        self.output_ensurers_instances = [output_ensurer(ensurer) for ensurer in outcome]

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            output = transformer.transform(data)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform)

    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        async def transform_async(_, data):
            output = await transformer.transform_async(data)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform_async)

class _ensure_changes(Generic[T, S], _ensure_base):
    def __init__(self, changes: Sequence[Callable[[T, S], Any]]):
        self.changes_ensurers_instances = [output_ensurer(ensurer) for ensurer in changes]

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            output = transformer.transform(data)
            for ensurer in self.changes_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform)

    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        async def transform_async(_, data):
            output = await transformer.transform_async(data)
            for ensurer in self.changes_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform_async)

class _ensure_both(Generic[T, S], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[T], Any]], outcome: Sequence[Callable[[S], Any]], changes: Sequence[Callable[[T, S], Any]]):
        self.input_ensurers_instances = [input_ensurer(ensurer) for ensurer in incoming]
        self.output_ensurers_instances = [output_ensurer(ensurer) for ensurer in outcome]
        self.changes_ensurers_instances = [output_ensurer(ensurer) for ensurer in changes]

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            for ensurer in self.output_ensurers_instances + self.changes_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform)

    def _generate_new_async_transformer(self, transformer: AsyncTransformer) -> AsyncTransformer:
        async def transform_async(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = await transformer.transform_async(data)
            for ensurer in self.output_ensurers_instances + self.changes_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        return transformer.copy(transform_async)

def ensure(*args, **kwargs):
    if len(kwargs) == 1 and 'incoming' in kwargs:
        return _ensure_incoming(kwargs['incoming'])
    if len(kwargs) == 1 and 'outcome' in kwargs:
        return _ensure_outcome(kwargs['outcome'])
    if len(kwargs) == 1 and 'changes' in kwargs:
        return _ensure_changes(kwargs['changes'])
    if len(kwargs) > 1:
        incoming = kwargs.get('incoming', [])
        outcome = kwargs.get('outcome', [])
        changes = kwargs.get('changes', [])
        return _ensure_both(incoming, outcome, changes)