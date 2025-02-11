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

def _format_tuple_annotation(tuple_annotation, generic_input_param, input_annotation) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(_format_return_annotation(annotation, generic_input_param, input_annotation))
    return f"({', '.join(formatted)})"

def _format_union_annotation(union_annotation, generic_input_param, input_annotation) -> str:
    formatted: list[str] = []
    for annotation in union_annotation.__args__:
        formatted.append(_format_return_annotation(annotation, generic_input_param, input_annotation))
    return f"({' | '.join(formatted)})"

def _format_generic_alias_annotation(generic_alias, generic_input_param, input_annotation) -> str:
    alias_name = generic_alias.__origin__.__name__
    formatted: list[str] = []
    for annotation in generic_alias.__args__:
        formatted.append(_format_return_annotation(annotation, generic_input_param, input_annotation))
    return f"{alias_name}[{', '.join(formatted)}]"

def _format_return_annotation(return_annotation, generic_input_param, input_annotation) -> str:
    if type(return_annotation) == str:
        return return_annotation
    if type(return_annotation) == tuple:
        return _format_tuple_annotation(return_annotation, generic_input_param, input_annotation)
    if get_origin(return_annotation) == tuple:
        return _format_tuple_annotation(return_annotation.__args__, generic_input_param, input_annotation)
    if get_origin(return_annotation) == Union:
        return _format_union_annotation(return_annotation, generic_input_param, input_annotation)
    if type(return_annotation) in {GenericAlias, _GenericAlias}:
        return _format_generic_alias_annotation(return_annotation, generic_input_param, input_annotation)
    if return_annotation == generic_input_param:
        return str(input_annotation.__name__)
    return str(return_annotation.__name__)

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
    if specific_args is None and generic_args is None:
        return {}
    if generic_args is None:
        if ignore_mismatches:
            return {}
        raise Exception(f"Type {generic} in generic has no arguments")
    if specific_args is None:
        if ignore_mismatches:
            return {}
        raise Exception(f"Type {specific} in specific has no arguments")
    if len(generic_args) != len(specific_args):
        if ignore_mismatches:
            return {}
        raise Exception(f"Number of arguments of type {generic} is different in specific type")
    matches = {}
    for generic_arg, specific_arg in zip(generic_args, specific_args):
        matched_types = _match_types(generic_arg, specific_arg)
        matches.update(matched_types)
    return matches

def _specify_types(generic, spec):
    if type(generic) == TypeVar:
        tp = spec.get(generic)
        if tp is None:
            return generic
        return tp
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