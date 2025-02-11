from typing import Any, Tuple, TypeVar, Generic

from gloe.functional import transformer
from gloe.transformers import Transformer

__all__ = ["forget", "debug", "forward", "forward_incoming"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")

@transformer
def forget(data: Any) -> None:
    """Transform any input data to `None`"""
    # Input validation
    if data is None:
        raise ValueError("Input data cannot be None")
    return None

@transformer
def debug(incoming: _In) -> _In:
    """Transformer that sets a breakpoint for debugging purposes"""
    # Input validation
    if incoming is None:
        raise ValueError("Input data cannot be None")
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
        # Input validation
        if data is None:
            raise ValueError("Input data cannot be None")
        return data

def forward_incoming(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, Tuple[_Out, _In]]:
    """Transformer that applies an inner transformer and returns a tuple of the transformed data and the original data"""
    # Input validation
    if inner_transformer is None:
        raise ValueError("Inner transformer cannot be None")
    try:
        return forward[_In]() >> (inner_transformer, forward())
    except Exception as e:
        raise ValueError("Error in forward_incoming transformer") from e