from typing import TypeVar\nfrom typing_extensions import assert_type\nfrom gloe import Transformer, AsyncTransformer\nfrom gloe.experimental import bridge\nfrom gloe.utils import forward\nfrom tests.lib.transformers import (\n    square, square_root, plus1, minus1, to_string, tuple_concatenate\n)\nfrom tests.type_utils.mypy_test_suite import MypyTestSuite\n\nIn = TypeVar('In')\nOut = TypeVar('Out')\n\nclass TestBasicTransformerTypes(MypyTestSuite):\n\n    def test_transformer_simple_typing(self):\n        """\n        Test the most simple transformer typing\n        """\n        graph = square\n        assert_type(graph, Transformer[float, float])\n\n    def test_simple_flow_typing(self):\n        """\n        Test the most simple transformer typing\n        """\n        graph = square >> square_root\n        assert_type(graph, Transformer[float, float])\n\n    def test_flow_with_mixed_types(self):\n        """\n        Test the most simple transformer typing\n        """\n        graph = square >> square_root >> to_string\n        assert_type(graph, Transformer[float, str])\n\n    def test_divergent_flow_types(self):\n        """\n        Test the most simple transformer typing\n        """\n        graph2 = square >> square_root >> (to_string, square)\n        assert_type(graph2, Transformer[float, tuple[str, float]])\n\n        graph3 = square >> square_root >> (to_string, square, to_string)\n        assert_type(graph3, Transformer[float, tuple[str, float, str]])\n\n        graph4 = square >> square_root >> (to_string, square, to_string, square)\n        assert_type(graph4, Transformer[float, tuple[str, float, str, float]])\n\n        graph5 = (\n            square >> square_root >> (to_string, square, to_string, square, to_string)\n        )\n        assert_type(graph5, Transformer[float, tuple[str, float, str, float, str]])\n\n        graph6 = (\n            square >> square_root >> (to_string, square, to_string, square, to_string, square)\n        )\n        assert_type(graph6, Transformer[float, tuple[str, float, str, float, str, float]])\n\n        graph7 = (\n            square >> square_root >> (to_string, square, to_string, square, to_string, square, to_string)\n        )\n        assert_type(graph7, Transformer[float, tuple[str, float, str, float, str, float, str]])\n\n    def test_bridge(self):\n        num_bridge = bridge[float]('num')\n        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()\n        assert_type(graph, Transformer[float, tuple[float, float]])\n\n    def test_async_transformer(self):\n        @async_transformer\n        async def _square(num: int) -> float:\n            return float(num * num)\n\n        async_pipeline = _square >> to_string\n        async_pipeline2 = forward[int]() >> _square >> to_string\n        async_pipeline3 = forward[int]() >> (_square, _square >> to_string)\n        async_pipeline4 = _square >> (to_string, forward[float]())\n        async_pipeline5 = _square >> (to_string, forward[float]()) >> tuple_concatenate\n\n        assert_type(_square, AsyncTransformer[int, float])\n        assert_type(async_pipeline, AsyncTransformer[int, str])\n        assert_type(async_pipeline2, AsyncTransformer[int, str])\n        assert_type(async_pipeline3, AsyncTransformer[int, tuple[float, str]])\n        assert_type(async_pipeline4, AsyncTransformer[int, tuple[str, float]])\n        assert_type(async_pipeline5, AsyncTransformer[int, str])\n