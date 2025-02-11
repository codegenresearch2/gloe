from functools import wraps
from types import GenericAlias
from typing import (
    TypeVar,
    get_origin,
    Generic,
    Union,
    _GenericAlias,
    ParamSpec,
    Callable,
    Awaitable,
)

def _format_annotation(annotation, generic_input_param, input_annotation) -> str:
    if type(annotation) == str:
        return annotation
    if type(annotation) == tuple:
        return f"({', '.join(_format_annotation(a, generic_input_param, input_annotation) for a in annotation)})"
    if get_origin(annotation) in {tuple, Union}:
        return f"({' | '.join(_format_annotation(a, generic_input_param, input_annotation) for a in annotation.__args__)})"
    if type(annotation) in {GenericAlias, _GenericAlias}:
        return f"{annotation.__origin__.__name__}[{', '.join(_format_annotation(a, generic_input_param, input_annotation) for a in annotation.__args__)}]"
    if annotation == generic_input_param:
        return str(input_annotation.__name__)
    return str(annotation.__name__)

def _match_types(generic, specific, ignore_mismatches=True):
    if type(generic) == TypeVar:
        return {generic: specific}
    specific_origin = get_origin(specific)
    generic_origin = get_origin(generic)
    if (specific_origin is None or generic_origin is None) or not issubclass(specific_origin, generic_origin):
        if ignore_mismatches:
            return {}
        raise Exception(f"Type {generic} does not match with {specific}")
    generic_args = getattr(generic, "__args__", None)
    specific_args = getattr(specific, "__args__", None)
    if generic_args is None or specific_args is None:
        if ignore_mismatches:
            return {}
        raise Exception(f"Type {generic} or {specific} has no arguments")
    if len(generic_args) != len(specific_args):
        if ignore_mismatches:
            return {}
        raise Exception(f"Number of arguments of type {generic} is different in specific type")
    return {g: s for arg in zip(generic_args, specific_args) for g, s in _match_types(arg[0], arg[1]).items()}

def _specify_types(generic, spec):
    if type(generic) == TypeVar:
        return spec.get(generic, generic)
    generic_args = getattr(generic, "__args__", None)
    if generic_args is None:
        return generic
    origin = get_origin(generic)
    args = tuple(_specify_types(arg, spec) for arg in generic_args)
    return GenericAlias(origin, args)

_Args = ParamSpec("_Args")
_R = TypeVar("_R")

def awaitify(sync_func: Callable[_Args, _R]) -> Callable[_Args, Awaitable[_R]]:
    async def async_func(*args, **kwargs):
        return sync_func(*args, **kwargs)
    return async_func

# Additional test cases and docstring for function documentation can be added here