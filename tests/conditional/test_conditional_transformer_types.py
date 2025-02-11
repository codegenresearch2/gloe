from typing import TypeVar, Union
from typing_extensions import assert_type

from gloe import Transformer, AsyncTransformer, if_not_zero, if_is_even, async_transformer
from gloe.utils import forward
from tests.lib.transformers import square, square_root, plus1, minus1, to_string, async_plus1
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")

CONDITIONED_GRAPH = square >> square_root >> if_not_zero.Then(plus1).Else(minus1)
CONDITIONED_GRAPH2 = square >> square_root >> if_not_zero.Then(to_string).Else(square)
CHAINED_CONDITIONS_GRAPH = if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
ASYNC_CHAINED_CONDITIONS_GRAPH1 = if_is_even.Then(async_plus1).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
ASYNC_CHAINED_CONDITIONS_GRAPH2 = if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(async_plus1).ElseNone()

class TestTransformerTypes(MypyTestSuite):
    def test_conditioned_flow_types(self):
        assert_type(CONDITIONED_GRAPH, Transformer[float, float])
        assert_type(CONDITIONED_GRAPH2, Transformer[float, Union[str, float]])

    def test_chained_condition_flow_types(self):
        assert_type(CHAINED_CONDITIONS_GRAPH, Transformer[float, Union[float, str, None]])

    def test_async_chained_condition_flow_types(self):
        assert_type(ASYNC_CHAINED_CONDITIONS_GRAPH1, AsyncTransformer[float, Union[float, str, None]])
        assert_type(ASYNC_CHAINED_CONDITIONS_GRAPH2, AsyncTransformer[float, Union[float, None]])