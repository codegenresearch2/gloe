from typing import TypeVar, Union, Tuple
from typing_extensions import assert_type

from gloe import Transformer, async_transformer, AsyncTransformer
from gloe.utils import forward
from tests.lib.transformers import square, square_root, to_string, tuple_concatenate

In = TypeVar("In")
Out = TypeVar("Out")

class TestBasicTransformerTypes:
    def test_transformer_simple_typing(self):
        graph = square
        assert_type(graph, Transformer[float, float])

    def test_simple_flow_typing(self):
        graph = square >> square_root
        assert_type(graph, Transformer[float, float])

    def test_flow_with_mixed_types(self):
        graph = square >> square_root >> to_string
        assert_type(graph, Transformer[float, str])

    def test_divergent_flow_types(self):
        graph2 = square >> square_root >> (to_string, square)
        assert_type(graph2, Transformer[float, Tuple[str, float]])

        graph3 = square >> square_root >> (to_string, square, to_string)
        assert_type(graph3, Transformer[float, Tuple[str, float, str]])

        graph4 = square >> square_root >> (to_string, square, to_string, square)
        assert_type(graph4, Transformer[float, Tuple[str, float, str, float]])

        graph5 = square >> square_root >> (to_string, square, to_string, square, to_string)
        assert_type(graph5, Transformer[float, Tuple[str, float, str, float, str]])

        graph6 = square >> square_root >> (to_string, square, to_string, square, to_string, square)
        assert_type(graph6, Transformer[float, Tuple[str, float, str, float, str, float]])

        graph7 = square >> square_root >> (to_string, square, to_string, square, to_string, square, to_string)
        assert_type(graph7, Transformer[float, Tuple[str, float, str, float, str, float, str]])

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
        assert_type(async_pipeline3, AsyncTransformer[int, Tuple[float, str]])
        assert_type(async_pipeline4, AsyncTransformer[int, Tuple[str, float]])
        assert_type(async_pipeline5, AsyncTransformer[int, str])