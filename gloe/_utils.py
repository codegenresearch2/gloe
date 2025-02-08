from types import GenericAlias
from typing import TypeVar, get_origin, TypeAlias, TypedDict, Generic, Union, get_args, issubclass

# type: ignore

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
    return f"({' | '.join(formatted)})\