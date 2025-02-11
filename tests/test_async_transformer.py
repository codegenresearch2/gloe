from typing import TypeVar, Any
from gloe import async_transformer, ensure, UnsupportedTransformerArgException, transformer
from gloe.functional import partial_async_transformer
from gloe.utils import forward
import asyncio
import unittest

_In = TypeVar("_In")
_DATA = {"foo": "bar"}
_URL = "http://my-service"

class InvalidInputType(Exception):
    pass

def validate_string(value: Any) -> None:
    if not isinstance(value, str):
        raise InvalidInputType(f"Expected string, got {type(value).__name__}")

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

class HasNotBarKey(Exception):
    pass

def has_bar_key(dict: dict[str, str]) -> None:
    if "bar" not in dict.keys():
        raise HasNotBarKey()

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
        @ensure(incoming=[validate_string], outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA
        pipeline = ensured_request >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[validate_string], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA
        pipeline = ensured_delayed_request(0.1) >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_async_transformer_wrong_arg(self):
        with self.assertWarns(RuntimeWarning):
            @transformer  # type: ignore
            async def invalid_transformer(arg1: str, arg2: int):
                return arg1, arg2

    async def test_async_transformer_copy(self):
        copied_transformer = request_data.copy()
        self.assertEqual(copied_transformer, request_data)

    async def test_unsupported_argument(self):
        def unsupported_function():
            return None

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {unsupported_function}",
        ):
            _ = request_data >> unsupported_function  # type: ignore

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {unsupported_function}",
        ):
            _ = request_data >> (unsupported_function, forward[str]())  # type: ignore