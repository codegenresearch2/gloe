from typing import TypeVar, Tuple
from typing_extensions import assert_type
from gloe import Transformer, async_transformer, AsyncTransformer
from gloe.experimental import bridge
from gloe.utils import forward
from tests.lib.transformers import square, square_root, plus1, minus1, to_string, tuple_concatenate
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")

TRANSFORMER_FLOAT_FLOAT = Transformer[float, float]
TRANSFORMER_FLOAT_STR = Transformer[float, str]

class TestBasicTransformerTypes(MypyTestSuite):

    def test_transformer_simple_typing(self):
        """
        Test the most simple transformer typing
        """
        graph = square
        assert_type(graph, TRANSFORMER_FLOAT_FLOAT)

    def test_simple_flow_typing(self):
        """
        Test the simple flow typing
        """
        graph = square >> square_root
        assert_type(graph, TRANSFORMER_FLOAT_FLOAT)

    def test_flow_with_mixed_types(self):
        """
        Test the flow typing with mixed types
        """
        graph = square >> square_root >> to_string
        assert_type(graph, TRANSFORMER_FLOAT_STR)

    def test_divergent_flow_types(self):
        """
        Test the divergent flow typing
        """
        graph2 = square >> square_root >> (to_string, square)
        assert_type(graph2, Transformer[float, tuple[str, float]])

        graph3 = square >> square_root >> (to_string, square, to_string)
        assert_type(graph3, Transformer[float, tuple[str, float, str]])

        # ... rest of the code ...

    def test_bridge(self):
        """
        Test the bridge functionality
        """
        num_bridge = bridge[float]("num")
        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()
        assert_type(graph, Transformer[float, tuple[float, float]])

    def test_async_transformer(self):
        """
        Test the async transformer
        """
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