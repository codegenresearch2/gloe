import asyncio
import unittest
from typing import TypeVar, Callable, Any
from gloe import async_transformer, ensure
from gloe.functional import partial_async_transformer
from gloe.utils import forward
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")

_DATA = {"foo": "bar"}


def is_string(data: Any) -> bool:
    return isinstance(data, str)


@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA


class HasNotBarKey(Exception):
    pass


def has_bar_key(dict: dict[str, str]):
    if "bar" not in dict.keys():
        raise HasNotBarKey()


def is_dict(data: Any) -> bool:
    return isinstance(data, dict)


_URL = "http://my-service"


class TestAsyncTransformer(unittest.IsolatedAsyncioTestCase):
    async def test_basic_case(self):
        test_forward = request_data >> forward()

        result = await test_forward(_URL)

        self.assertDictEqual(result, _DATA)

    async def test_begin_with_transformer(self):
        test_forward = forward[str]() >> request_data

        result = await test_forward(_URL)

        self.assertDictEqual(result, _DATA)

    async def test_async_on_divergent_connection(self):
        test_forward = forward[str]() >> (forward[str](), request_data)

        result = await test_forward(_URL)

        self.assertEqual(result, (_URL, _DATA))

    async def test_divergent_connection_from_async(self):
        test_forward = request_data >> (
            forward[dict[str, str]](),
            forward[dict[str, str]](),
        )

        result = await test_forward(_URL)

        self.assertEqual(result, (_DATA, _DATA))

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(
            data: dict[str, str], delay: float
        ) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.1) >> forward()

        result = await pipeline(_DATA)

        self.assertEqual(result, _DATA)

    async def test_ensure_async_transformer(self):
        @ensure(outcome=[has_bar_key], incoming=[is_dict])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(outcome=[has_bar_key], incoming=[is_dict])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_unsupported_transformer_argument(self):
        def just_a_normal_function():
            return None

        with self.assertRaises(UnsupportedTransformerArgException):
            _ = request_data >> just_a_normal_function  # type: ignore

        with self.assertRaises(UnsupportedTransformerArgException):
            _ = request_data >> (just_a_normal_function, forward[int]())  # type: ignore

    async def test_transformer_copying(self):
        graph = request_data >> forward()
        copied_graph = graph.copy()

        result1 = await graph(_URL)
        result2 = await copied_graph(_URL)

        self.assertDictEqual(result1, _DATA)
        self.assertDictEqual(result2, _DATA)

    async def test_transformer_signature_representation(self):
        @async_transformer
        async def to_string(num: float) -> str:
            """
            This transformer receives a number as input and return its representation as a string
            """
            return str(num)

        signature = to_string.signature()

        self.assertEqual(str(signature), "(num: float) -> str")