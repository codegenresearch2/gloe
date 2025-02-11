import asyncio
import unittest
from typing import TypeVar
from gloe import async_transformer, ensure, UnsupportedTransformerArgException
from gloe.functional import partial_async_transformer
from gloe.utils import forward

_In = TypeVar("_In")

_DATA = {"foo": "bar"}
_URL = "http://my-service"

class HasNotBarKey(Exception):
    pass

def is_string(data: str):
    if type(data) is not str:
        raise TypeError("Input data must be a string")

def has_bar_key(dict: dict[str, str]):
    if "bar" not in dict.keys():
        raise HasNotBarKey

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

@async_transformer
async def add_slash(url: str) -> str:
    return url + "/"

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
        @ensure(incoming=[is_string], outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline = ensured_request >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_string], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.1) >> forward()
        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

    async def test_async_transformer_wrong_arg(self):
        with self.assertRaises(UnsupportedTransformerArgException):
            _ = request_data >> 123  # type: ignore

    async def test_pipeline_copying(self):
        pipeline = request_data >> forward()
        copied_pipeline = pipeline.copy()
        result = await copied_pipeline(_URL)
        self.assertDictEqual(result, _DATA)

    async def test_pipeline_copying_with_transformer(self):
        pipeline = add_slash >> forward()
        copied_pipeline = pipeline.copy()
        result = await copied_pipeline(_URL)
        self.assertEqual(result, _URL + "/")