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

from tests.type_utils.mypy_test_suite import MypyTestSuite

class TestTransformerTypes(MypyTestSuite):
    mypy_result: str

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