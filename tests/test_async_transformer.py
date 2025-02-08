import asyncio
import unittest
from typing import TypeVar, Any
from gloe import async_transformer, ensure
from gloe.functional import partial_async_transformer
from gloe.utils import forward
from gloe import UnsupportedTransformerArgException

_In = TypeVar('_In')

_DATA = {'foo': 'bar'}

class HasNotBarKey(Exception):
    pass

class IsString(Exception):
    pass

def is_string(value: Any) -> None:
    if not isinstance(value, str):
        raise IsString()

def has_bar_key(data: dict[str, str]) -> None:
    if 'bar' not in data:
        raise HasNotBarKey()

_URL = 'http://my-service'

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

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
        test_forward = request_data >> (forward[dict[str, str]](), forward[dict[str, str]]())

        result = await test_forward(_URL)

        self.assertEqual(result, (_DATA, _DATA))

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.1) >> forward()

        result = await pipeline(_DATA)

        self.assertEqual(result, _DATA)

    async def test_ensure_async_transformer(self):
        @ensure(outcome=[has_bar_key], incoming=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(outcome=[has_bar_key], incoming=[has_bar_key])
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

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = square >> just_a_normal_function  # type: ignore

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = square >> (just_a_normal_function, plus1)  # type: ignore

    async def test_transformer_copying(self):
        graph = square >> square_root
        copied_graph = graph.copy()

        self.assertEqual(graph, copied_graph)

    async def test_transformer_equality(self):
        graph = square >> square_root
        self.assertEqual(square, square)
        self.assertEqual(square, square.copy())
        self.assertNotEqual(graph, square_root)
        self.assertNotEqual(square, square_root)

    async def test_transformer_pydoc_keeping(self):
        @transformer
        def to_string(num: int) -> str:
            """
            This transformer receives a number as input and return its representation as a string
            """
            return str(num)

        self.assertEqual(
            to_string.__doc__,
            """
            This transformer receives a number as input and return its representation as a string
            """
        )

    async def test_transformer_signature_representation(self):
        signature = square.signature()

        self.assertEqual(str(signature), '(num: float) -> float')
