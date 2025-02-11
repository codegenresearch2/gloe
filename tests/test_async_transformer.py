import asyncio
import unittest
from typing import TypeVar, Any
from gloe import async_transformer, ensure, UnsupportedTransformerArgException, transformer
from gloe.functional import partial_async_transformer
from gloe.utils import forward

_In = TypeVar("_In")

_DATA = {"foo": "bar"}

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

class HasNotBarKey(Exception):
    pass

class HasFooKey(Exception):
    pass

class IsNotInt(Exception):
    pass

def has_bar_key(data: dict[str, str]):
    if "bar" not in data.keys():
        raise HasNotBarKey("The 'bar' key is not present in the dictionary.")

def has_foo_key(data: dict[str, str]):
    if "foo" not in data.keys():
        raise HasNotBarKey("The 'foo' key is not present in the dictionary.")

def foo_key_removed(incoming: dict[str, str], outcome: dict[str, str]):
    if "foo" in incoming.keys() or "foo" in outcome.keys():
        raise HasFooKey("The 'foo' key is still present in the dictionary.")

def is_str(data: Any):
    if type(data) is not str:
        raise TypeError("Data is not a string.")

def is_int(data: Any):
    if type(data) is not int:
        raise IsNotInt("Data is not an integer.")

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
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.1) >> forward()

        result = await pipeline(_DATA)

        self.assertEqual(result, _DATA)

    async def test_ensure_async_transformer(self):
        @ensure(incoming=[is_str], outcome=[has_bar_key], changes=[foo_key_removed])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            data = _DATA.copy()
            data.pop("foo", None)
            return data

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_str], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_async_transformer_int(self):
        @ensure(incoming=[is_int], outcome=[has_bar_key])
        @async_transformer
        async def ensured_request_int(num: int) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline = ensured_request_int >> forward()

        with self.assertRaises(IsNotInt):
            await pipeline("not an int")

    async def test_async_transformer_wrong_arg(self):
        def next_transformer():
            pass

        @ensure(incoming=[is_str], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        with self.assertRaises(UnsupportedTransformerArgException):
            pipeline = ensured_delayed_request(0.1) >> next_transformer

    async def test_async_transformer_copy(self):
        @transformer
        def add_slash(path: str) -> str:
            return path + "/"

        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = add_slash >> ensured_delayed_request(0)

        pipeline = pipeline.copy()
        result = await pipeline(_URL)
        self.assertEqual(result, _DATA)

    async def test_pipeline_with_conditions(self):
        @transformer
        def remove_foo(data: dict[str, str]) -> dict[str, str]:
            if "foo" in data:
                del data["foo"]
            return data

        pipeline = request_data >> remove_foo

        result = await pipeline(_URL)
        self.assertNotIn("foo", result)

        with self.assertRaises(HasFooKey):
            pipeline = request_data >> ensure(outcome=[foo_key_removed]) >> remove_foo
            await pipeline(_URL)