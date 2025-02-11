from typing import TypeVar
from gloe import async_transformer, ensure
from gloe.functional import partial_async_transformer
from gloe.utils import forward
import asyncio
import unittest

_In = TypeVar("_In")
_DATA = {"foo": "bar"}
_URL = "http://my-service"

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

class HasNotBarKey(Exception):
    pass

def has_bar_key(dict: dict[str, str]):
    if "bar" not in dict.keys():
        raise HasNotBarKey()

class TestAsyncTransformer(unittest.IsolatedAsyncioTestCase):
    async def test_basic_case(self):
        test_forward = request_data >> forward()
        self.assertDictEqual(await test_forward(_URL), _DATA)

    async def test_begin_with_transformer(self):
        test_forward = forward[str]() >> request_data
        self.assertDictEqual(await test_forward(_URL), _DATA)

    async def test_async_on_divergent_connection(self):
        test_forward = forward[str]() >> (forward[str](), request_data)
        self.assertEqual(await test_forward(_URL), (_URL, _DATA))

    async def test_divergent_connection_from_async(self):
        test_forward = request_data >> (forward[dict[str, str]](), forward[dict[str, str]]())
        self.assertEqual(await test_forward(_URL), (_DATA, _DATA))

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data
        pipeline = sleep_and_forward(0.1) >> forward()
        self.assertEqual(await pipeline(_DATA), _DATA)

    async def test_ensure_async_transformer(self):
        @ensure(outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA
        pipeline = ensured_request >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA
        pipeline = ensured_delayed_request(0.1) >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)