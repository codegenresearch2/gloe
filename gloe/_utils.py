from types import GenericAlias
from typing import TypeVar, get_origin, TypeAlias, TypedDict, Generic, Union, get_args, issubclass, _GenericAlias


def _format_tuple(
    tuple_annotation: tuple,
    generic_input_param,
    input_annotation,
) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(
            _format_return_annotation(annotation, generic_input_param, input_annotation)
        )
    return f"({', '.join(formatted)})"


def _format_union(
    tuple_annotation: tuple,
    generic_input_param,
    input_annotation,
) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(
            _format_return_annotation(annotation, generic_input_param, input_annotation)
        )
    return f"({' | '.join(formatted)})"


def _format_generic_alias(
    return_annotation: GenericAlias,
    generic_input_param,
    input_annotation,
) -> str:
    alias_name = return_annotation.__name__
    formatted: list[str] = []
    for annotation in return_annotation.__args__:
        formatted.append(
            _format_return_annotation(annotation, generic_input_param, input_annotation)
        )
    return f"{alias_name}[{', '.join(formatted)}]"


def _format_return_annotation(
    return_annotation,
    generic_input_param,
    input_annotation,
) -> str:
    if isinstance(return_annotation, str):
        return return_annotation
    if isinstance(return_annotation, tuple):
        return _format_tuple(return_annotation, generic_input_param, input_annotation)
    if return_annotation.__name__ in {"tuple", "Tuple"}:
        return _format_tuple(
            return_annotation.__args__,
            generic_input_param, input_annotation
        )
    if return_annotation.__name__ in {"Union"}:
        return _format_union(
            return_annotation.__args__,
            generic_input_param, input_annotation
        )
    if isinstance(return_annotation, GenericAlias) or isinstance(return_annotation, _GenericAlias):
        return _format_generic_alias(
            return_annotation,
            generic_input_param, input_annotation
        )

    if return_annotation == generic_input_param:
        return str(input_annotation.__name__)

    return str(return_annotation.__name__)
