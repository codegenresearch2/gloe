import unittest
from typing import TypeVar, Union
from typing_extensions import assert_type

from tests.lib.conditioners import if_not_zero, if_is_even
from tests.lib.transformers import square, square_root, plus1, minus1, to_string, async_plus1
from gloe import Transformer, AsyncTransformer
from gloe.experimental import bridge
from gloe.utils import forward
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")

class TestTransformerTypes(MypyTestSuite):
    def test_conditioned_flow_types(self):
        """Test the typing of a conditional flow."""
        conditioned_graph = square >> square_root >> if_not_zero.Then(plus1).Else(minus1)
        assert_type(conditioned_graph, Transformer[float, float])

        conditioned_graph2 = square >> square_root >> if_not_zero.Then(to_string).Else(square)
        assert_type(conditioned_graph2, Transformer[float, Union[str, float]])

    def test_chained_condition_flow_types(self):
        """Test the typing of a chained conditional flow."""
        chained_conditions_graph = if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
        assert_type(chained_conditions_graph, Transformer[float, Union[float, str, None]])

    def test_async_chained_condition_flow_types(self):
        """Test the typing of an asynchronous chained conditional flow."""
        async_chained_conditions_graph = if_is_even.Then(async_plus1).ElseIf(lambda x: x < 10).Then(to_string).ElseNone()
        assert_type(async_chained_conditions_graph, AsyncTransformer[float, Union[float, str, None]])

        async_chained_conditions_graph = if_is_even.Then(square).ElseIf(lambda x: x < 10).Then(async_plus1).ElseNone()
        assert_type(async_chained_conditions_graph, AsyncTransformer[float, Union[float, None]])