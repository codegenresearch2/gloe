from typing import TypeVar, Union, Tuple
from typing_extensions import assert_type
from gloe import Transformer, async_transformer, AsyncTransformer
from gloe.utils import forward
from tests.lib.transformers import square, square_root, plus1, minus1, to_string, tuple_concatenate
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")

TRANSFORMER_FLOAT_FLOAT = Transformer[float, float]
TRANSFORMER_FLOAT_STR = Transformer[float, str]

class TestBasicTransformerTypes(MypyTestSuite):

    def test_transformer_simple_typing(self):
        assert_type(square, TRANSFORMER_FLOAT_FLOAT)

    def test_simple_flow_typing(self):
        graph = square >> square_root
        assert_type(graph, TRANSFORMER_FLOAT_FLOAT)

    def test_flow_with_mixed_types(self):
        graph = square >> square_root >> to_string
        assert_type(graph, TRANSFORMER_FLOAT_STR)

    def test_divergent_flow_types(self):
        graph2 = square >> square_root >> (to_string, square)
        assert_type(graph2, Transformer[float, Tuple[str, float]])

        # ... rest of the code ...

    def test_async_transformer(self):
        @async_transformer
        async def _square(num: int) -> float:
            return float(num * num)

        async_pipeline = _square >> to_string
        async_pipeline2 = forward[int]() >> _square >> to_string
        # ... rest of the code ...

        assert_type(_square, AsyncTransformer[int, float])
        assert_type(async_pipeline, AsyncTransformer[int, str])
        assert_type(async_pipeline2, AsyncTransformer[int, str])
        # ... rest of the code ...