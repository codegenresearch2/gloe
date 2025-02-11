import asyncio
import unittest
from typing import TypeVar, Union
from typing_extensions import assert_type

from gloe import Transformer, AsyncTransformer
from gloe.utils import forward
from gloe.experimental import bridge
from tests.lib.transformers import (
    square,
    square_root,
    plus1,
    minus1,
    to_string,
    tuple_concatenate,
    logarithm,
    repeat,
    format_currency,
    async_plus1,
)
from tests.lib.conditioners import if_not_zero, if_is_even
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")


class TestTransformerTypes(MypyTestSuite):
    mypy_result: str = ""

    def test_conditioned_flow_types(self):
        """
        Test conditioned flow types with if_not_zero and if_is_even
        """
        conditioned_graph = (
            square >> square_root >> if_not_zero.Then(plus1).Else(minus1)
        )
        assert_type(conditioned_graph, Transformer[float, float])

        conditioned_graph2 = (
            square >> square_root >> if_not_zero.Then(to_string).Else(square)
        )
        assert_type(conditioned_graph2, Transformer[float, Union[str, float]])

    def test_chained_condition_flow_types(self):
        """
        Test chained conditions in transformer flows
        """
        chained_conditions_graph = (
            if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
        )
        assert_type(chained_conditions_graph, Transformer[float, Union[float, str, None]])

    def test_async_chained_condition_flow_types(self):
        """
        Test async chained conditions in transformer flows
        """
        async_chained_conditions_graph = (
            if_is_even.Then(async_plus1)
            .ElseIf(lambda x: x < 10)
            .Then(to_string)
            .ElseNone()
        )
        assert_type(async_chained_conditions_graph, AsyncTransformer[float, Union[float, str, None]])

        async_chained_conditions_graph = (
            if_is_even.Then(square)
            .ElseIf(lambda x: x < 10)
            .Then(async_plus1)
            .ElseNone()
        )
        assert_type(async_chained_conditions_graph, AsyncTransformer[float, Union[float, None]])

    def test_transformer_simple_typing(self):
        """
        Test the most simple transformer typing
        """
        graph = square
        assert_type(graph, Transformer[float, float])

    def test_simple_flow_typing(self):
        """
        Test the most simple transformer typing
        """
        graph = square >> square_root
        assert_type(graph, Transformer[float, float])

    def test_flow_with_mixed_types(self):
        """
        Test the most simple transformer typing
        """
        graph = square >> square_root >> to_string
        assert_type(graph, Transformer[float, str])

    def test_divergent_flow_types(self):
        """
        Test the most simple transformer typing
        """
        graph2 = square >> square_root >> (to_string, square)
        assert_type(graph2, Transformer[float, tuple[str, float]])

        graph3 = square >> square_root >> (to_string, square, to_string)
        assert_type(graph3, Transformer[float, tuple[str, float, str]])

        graph4 = square >> square_root >> (to_string, square, to_string, square)
        assert_type(graph4, Transformer[float, tuple[str, float, str, float]])

        graph5 = (
            square
            >> square_root
            >> (to_string, square, to_string, square, to_string)
        )
        assert_type(graph5, Transformer[float, tuple[str, float, str, float, str]])

        graph6 = (
            square
            >> square_root
            >> (to_string, square, to_string, square, to_string, square)
        )
        assert_type(
            graph6, Transformer[float, tuple[str, float, str, float, str, float]]
        )

        graph7 = (
            square
            >> square_root
            >> (to_string, square, to_string, square, to_string, square, to_string)
        )
        assert_type(
            graph7, Transformer[float, tuple[str, float, str, float, str, float, str]]
        )

    def test_bridge(self):
        """
        Test bridge functionality
        """
        num_bridge = bridge[float]("num")
        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()
        assert_type(graph, Transformer[float, tuple[float, float]])

    def test_async_transformer(self):
        """
        Test async transformer functionality
        """
        @async_transformer
        async def _square(num: int) -> float:
            return float(num * num)

        async_pipeline = _square >> to_string
        async_pipeline2 = forward[int]() >> _square >> to_string
        async_pipeline3 = forward[int]() >> (_square, _square >> to_string)
        async_pipeline4 = _square >> (to_string, forward[float]())
        async_pipeline5 = _square >> (to_string, forward[float]()) >> tuple_concatenate

        assert_type(_square, AsyncTransformer[int, float])
        assert_type(async_pipeline, AsyncTransformer[int, str])
        assert_type(async_pipeline2, AsyncTransformer[int, str])
        assert_type(async_pipeline3, AsyncTransformer[int, tuple[float, str]])
        assert_type(async_pipeline4, AsyncTransformer[int, tuple[str, float]])
        assert_type(async_pipeline5, AsyncTransformer[int, str])