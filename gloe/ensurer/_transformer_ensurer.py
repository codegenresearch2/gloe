import inspect
from abc import abstractmethod, ABC
from types import FunctionType
from typing import Any, Callable, Generic, ParamSpec, Sequence, TypeVar, cast, overload

from gloe.async_transformer import AsyncTransformer
from gloe.functional import _PartialTransformer, _PartialAsyncTransformer
from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_P1 = ParamSpec("_P1")

class TransformerEnsurer(Generic[_T, _S], ABC):
    """
    Abstract base class for transformer ensurers.
    """
    @abstractmethod
    def validate_input(self, data: _T) -> None:
        """
        Perform a validation on incoming data before executing the transformer code.
        """
        pass

    @abstractmethod
    def validate_output(self, data: _T, output: _S) -> None:
        """
        Perform a validation on outcome data after executing the transformer code.
        """
        pass

    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(*args: Any, **kwargs: Any) -> _S:
            self.validate_input(args[0])
            output = transformer.transform(*args, **kwargs)
            self.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    class LambdaEnsurer(TransformerEnsurer[_T, _S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T) -> None:
            func(data)

        def validate_output(self, data: _T, output: _S) -> None:
            pass

    return LambdaEnsurer()

@overload
def output_ensurer(func: Callable[[_T, _S], Any]) -> TransformerEnsurer[_T, _S]:
    pass

@overload
def output_ensurer(func: Callable[[_S], Any]) -> TransformerEnsurer[Any, _S]:
    pass

def output_ensurer(func: Callable) -> TransformerEnsurer:
    class LambdaEnsurer(TransformerEnsurer):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: Any) -> None:
            pass

        def validate_output(self, data: Any, output: Any) -> None:
            if len(inspect.signature(func).parameters) == 1:
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

    def __call__(self, arg: Any) -> Any:
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        if isinstance(arg, AsyncTransformer):
            return self._generate_new_async_transformer(arg)
        if isinstance(arg, _PartialTransformer):
            transformer_init = arg

            def ensured_transformer_init(*args: Any, **kwargs: Any) -> Transformer[_T, _S]:
                transformer = transformer_init(*args, **kwargs)
                return self._generate_new_transformer(transformer)

            return ensured_transformer_init
        if isinstance(arg, _PartialAsyncTransformer):
            async_transformer_init = arg

            def ensured_async_transformer_init(*args: Any, **kwargs: Any) -> AsyncTransformer[_T, _S]:
                async_transformer = async_transformer_init(*args, **kwargs)
                return self._generate_new_async_transformer(async_transformer)

            return ensured_async_transformer_init

    @abstractmethod
    def _generate_new_transformer(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        pass

    @abstractmethod
    def _generate_new_async_transformer(self, transformer: AsyncTransformer[_T, _S]) -> AsyncTransformer[_T, _S]:
        pass

class _ensure_incoming(Generic[_T], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[_T], Any]]):
        self.input_ensurers_instances = [input_ensurer(ensurer) for ensurer in incoming]

    def _generate_new_transformer(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(*args: Any, **kwargs: Any) -> _S:
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(args[0])
            output = transformer.transform(*args, **kwargs)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

    def _generate_new_async_transformer(self, transformer: AsyncTransformer[_T, _S]) -> AsyncTransformer[_T, _S]:
        async def transform_async(*args: Any, **kwargs: Any) -> _S:
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(args[0])
            output = await transformer.transform_async(*args, **kwargs)
            return output

        transformer_cp = transformer.copy(transform_async)
        return transformer_cp

class _ensure_outcome(Generic[_S], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[_S], Any]]):
        self.output_ensurers_instances = [output_ensurer(ensurer) for ensurer in incoming]

    def _generate_new_transformer(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(*args: Any, **kwargs: Any) -> _S:
            output = transformer.transform(*args, **kwargs)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

    def _generate_new_async_transformer(self, transformer: AsyncTransformer[_T, _S]) -> AsyncTransformer[_T, _S]:
        async def transform_async(*args: Any, **kwargs: Any) -> _S:
            output = await transformer.transform_async(*args, **kwargs)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform_async)
        return transformer_cp

class _ensure_changes(Generic[_T, _S], _ensure_base):
    def __init__(self, changes: Sequence[Callable[[_T, _S], Any]]):
        self.changes_ensurers_instances = [output_ensurer(ensurer) for ensurer in changes]

    def _generate_new_transformer(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(*args: Any, **kwargs: Any) -> _S:
            output = transformer.transform(*args, **kwargs)
            for ensurer in self.changes_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

    def _generate_new_async_transformer(self, transformer: AsyncTransformer[_T, _S]) -> AsyncTransformer[_T, _S]:
        async def transform_async(*args: Any, **kwargs: Any) -> _S:
            output = await transformer.transform_async(*args, **kwargs)
            for ensurer in self.changes_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform_async)
        return transformer_cp

class _ensure_both(Generic[_T, _S], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[_T], Any]], outcome: Sequence[Callable[[_S], Any]], changes: Sequence[Callable[[_T, _S], Any]]):
        incoming_seq = incoming if type(incoming) == list else [incoming]
        self.input_ensurers_instances = [input_ensurer(ensurer) for ensurer in incoming_seq]

        outcome_seq = outcome if type(outcome) == list else [outcome]
        self.output_ensurers_instances = [output_ensurer(ensurer) for ensurer in outcome_seq]

        changes_seq = changes if type(changes) == list else [changes]
        self.output_ensurers_instances = self.output_ensurers_instances + [output_ensurer(ensurer) for ensurer in changes_seq]

    def _generate_new_transformer(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        def transform(*args: Any, **kwargs: Any) -> _S:
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(args[0])
            output = transformer.transform(*args, **kwargs)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp

    def _generate_new_async_transformer(self, transformer: AsyncTransformer[_T, _S]) -> AsyncTransformer[_T, _S]:
        async def transform_async(*args: Any, **kwargs: Any) -> _S:
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(args[0])
            output = await transformer.transform_async(*args, **kwargs)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(args[0], output)
            return output

        transformer_cp = transformer.copy(transform_async)
        return transformer_cp

@overload
def ensure(incoming: Sequence[Callable[[_T], Any]]) -> _ensure_incoming[_T]:
    pass

@overload
def ensure(outcome: Sequence[Callable[[_S], Any]]) -> _ensure_outcome[_S]:
    pass

@overload
def ensure(changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_changes[_T, _S]:
    pass

@overload
def ensure(incoming: Sequence[Callable[[_T], Any]], outcome: Sequence[Callable[[_S], Any]]) -> _ensure_both[_T, _S]:
    pass

@overload
def ensure(incoming: Sequence[Callable[[_T], Any]], changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_both[_T, _S]:
    pass

@overload
def ensure(outcome: Sequence[Callable[[_T], Any]], changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_both[_T, _S]:
    pass

@overload
def ensure(incoming: Sequence[Callable[[_T], Any]], outcome: Sequence[Callable[[_S], Any]], changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_both[_T, _S]:
    pass

def ensure(*args: Any, **kwargs: Any) -> Any:
    """
    This decorator is used in transformers to ensure some validation based on its incoming
    data, outcome data, or both. These validations are performed by validators. Validators
    are simple callable functions that validate certain aspects of the input, output, or
    the differences between them. If the validation fails, it must raise an exception.

    Args:
        incoming (Sequence[Callable[[_T], Any]]): sequence of validators that will be
            applied to the incoming data. The type :code:`_T` refers to the incoming type.
            Default value: :code:`[]`.
        outcome (Sequence[Callable[[_S], Any]]): sequence of validators that will be
            applied to the outcome data. The type :code:`_S` refers to the outcome type.
            Default value: :code:`[]`.
        changes (Sequence[Callable[[_T, _S], Any]]): sequence of validators that will be
            applied to both incoming and outcome data. The type :code:`_T` refers to the
            incoming type, and type :code:`_S` refers to the outcome type.
            Default value: :code:`[]`.

    Returns:
        An instance of the appropriate _ensure_* class based on the provided arguments.
    """
    if len(kwargs.keys()) == 1 and "incoming" in kwargs:
        return _ensure_incoming(kwargs["incoming"])

    if len(kwargs.keys()) == 1 and "outcome" in kwargs:
        return _ensure_outcome(kwargs["outcome"])

    if len(kwargs.keys()) == 1 and "changes" in kwargs:
        return _ensure_changes(kwargs["changes"])

    if len(kwargs.keys()) > 1:
        incoming = []
        if "incoming" in kwargs:
            incoming = kwargs["incoming"]

        outcome = []
        if "outcome" in kwargs:
            outcome = kwargs["outcome"]

        changes = []
        if "changes" in kwargs:
            changes = kwargs["changes"]

        return _ensure_both(incoming, outcome, changes)