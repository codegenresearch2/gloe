from typing import Any, Tuple, TypeVar, Generic

from gloe.functional import transformer
from gloe.transformers import Transformer

__all__ = ["forget", "debug", "forward", "forward_incoming"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@transformer
def forget(data: Any) -> None:
    """Transform any input data to `None`"""
    return None


@transformer
def debug(incoming: _In) -> _In:
    """Pauses the execution and returns the incoming data."""
    breakpoint()
    return incoming


class forward(Generic[_In], Transformer[_In, _In]):
    def __init__(self):
        super().__init__()
        self._invisible = True

    def __repr__(self):
        if self.previous is not None:
            return str(self.previous)

        return super().__repr__()

    def transform(self, data: _In) -> _In:
        return data


def forward_incoming(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, Tuple[_Out, _In]]:
    """Combines the inner transformer with the forward transformer to return a tuple of the transformed data and the original input."""
    return forward[_In]() >> (inner_transformer, forward())