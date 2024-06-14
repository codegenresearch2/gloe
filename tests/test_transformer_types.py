import asyncio
import inspect
import os
import re
import unittest
from pathlib import Path
from typing import TypeVar, Iterable, Union
from typing_extensions import assert_type

from tests.lib.conditioners import if_not_zero, if_is_even
from tests.lib.ensurers import is_even, same_value, same_value_int, is_greater_than_10
from tests.lib.transformers import (
    square,
    square_root,
    plus1,
    minus1,
    to_string,
    logarithm,
    repeat,
    format_currency,
    tuple_concatenate,
    async_plus1,
)
from gloe import (
    Transformer,
    transformer,
    partial_transformer,
    partial_async_transformer,
    ensure,
    async_transformer,
    AsyncTransformer,
)
from gloe.utils import forward
from gloe.experimental import bridge
from gloe.collection import Map
from mypy import api


In = TypeVar("In")
Out = TypeVar("Out")


class TestTransformerTypes(unittest.TestCase):
    mypy_result: str

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
            square >> square_root >> (to_string, square, to_string, square, to_string)
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

    def test_conditioned_flow_types(self):
        """
        Test the most simple transformer typing
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
        Test the most simple transformer typing
        """

        chained_conditions_graph = (
            if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
        )

        assert_type(
            chained_conditions_graph, Transformer[float, Union[float, str, None]]
        )

    def test_async_chained_condition_flow_types(self):
        """
        Test the most simple transformer typing
        """

        async_chained_conditions_graph = (
            if_is_even.Then(async_plus1)
            .ElseIf(lambda x: x < 10)
            .Then(to_string)
            .ElseNone()
        )

        assert_type(
            async_chained_conditions_graph,
            AsyncTransformer[float, Union[float, str, None]],
        )

        async_chained_conditions_graph = (
            if_is_even.Then(square)
            .ElseIf(lambda x: x < 10)
            .Then(async_plus1)
            .ElseNone()
        )

        assert_type(
            async_chained_conditions_graph,
            AsyncTransformer[float, Union[float, None]],
        )

    def test_partial_transformer(self):
        """
        Test the curried transformer typing
        """

        log2 = logarithm(base=2)
        assert_type(log2, Transformer[float, float])

        repeater = repeat(n_times=2, linebreak=True)
        assert_type(repeater, Transformer[str, str])

    def test_transformer_init(self):
        """
        Test the transformer initializer typing
        """

        formatter = format_currency(thousands_separator=",")

        assert_type(formatter, Transformer[float, str])

    def test_transformer_map(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[list[float]]() >> Map(
            format_currency(thousands_separator=",")
        )

        assert_type(mapped_logarithm, Transformer[list[float], Iterable[str]])

    def test_transformer_ensurer(self):
        @ensure(incoming=[is_even])
        @transformer
        def t1(n1: int) -> int:
            return n1 * n1

        @ensure(outcome=[is_even])
        @transformer
        def t2(n1: int) -> int:
            return n1 * n1

        @ensure(changes=[same_value_int])
        @transformer
        def t3(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_even])
        @transformer
        def t4(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t5(n1: int) -> float:
            return n1 * n1

        @ensure(outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t6(num: float) -> float:
            return num

        assert_type(t1, Transformer[int, int])
        assert_type(t2, Transformer[int, int])
        assert_type(t3, Transformer[int, int])
        assert_type(t4, Transformer[int, int])
        assert_type(t5, Transformer[int, float])
        assert_type(t6, Transformer[float, float])

    def test_transformer_init_ensurer(self):
        @ensure(incoming=[is_even])
        @partial_transformer
        def ti1(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(outcome=[is_even])
        @partial_transformer
        def ti2(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(changes=[same_value_int])
        @partial_transformer
        def ti3(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], outcome=[is_even])
        @partial_transformer
        def ti4(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], changes=[same_value_int])
        @partial_transformer
        def ti5(n1: int, n2: int) -> int:
            return n1 * n2

        assert_type(ti1(2), Transformer[int, int])
        assert_type(ti2(2), Transformer[int, int])
        assert_type(ti3(2), Transformer[int, int])
        assert_type(ti4(2), Transformer[int, int])
        assert_type(ti5(2), Transformer[int, int])

    def test_bridge(self):
        num_bridge = bridge[float]("num")

        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()

        assert_type(graph, Transformer[float, tuple[float, float]])

    def test_async_transformer(self):
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

    def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: int) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(1) >> forward()

        assert_type(pipeline, AsyncTransformer[dict[str, str], dict[str, str]])

    @classmethod
    def setUpClass(cls):
        file_path = Path(os.path.abspath(__file__))
        config_path = (file_path.parent.parent / "mypy.ini").absolute()
        result = api.run(
            [
                __file__,
                f"--config-file={config_path}",
            ]
        )
        cls.mypy_result = result[0]

    def setUp(self):
        if "Success" in self.mypy_result:
            return

        test_case = self._testMethodName
        lines, start_line = inspect.getsourcelines(getattr(self.__class__, test_case))
        end_line = start_line + len(lines) - 1

        errors = self.mypy_result.split("\n")[:-2]
        for error in errors:
            matches = re.findall(r"^[a-z_]+\.py:(\d+): error: (.+)", error)
            line_number, error = matches[0]
            if start_line <= int(line_number) <= end_line:
                mypy_error = re.sub(r" \[assert-type\]$", "", error)
                raise AssertionError(mypy_error)


if __name__ == "__main__":
    unittest.main()
