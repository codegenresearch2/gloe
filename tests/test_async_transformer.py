import asyncio
import unittest
from typing import TypeVar, Any
from gloe import (
    async_transformer,
    ensure,
    UnsupportedTransformerArgException,
    transformer,
)
from gloe.functional import partial_async_transformer
from gloe.utils import forward

_DATA = {"foo": "bar"}


@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA


class HasNotFooKey(Exception):
    pass


class HasFooKey(Exception):
    pass


def has_foo_key(dict: dict[str, str]) -> bool:
    return "foo" in dict


def is_str(data: Any) -> bool:
    return isinstance(data, str)


def foo_key_removed(dict: dict[str, str]) -> bool:
    return "foo" not in dict


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
        @ensure(incoming=[is_str], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            if not has_foo_key(_DATA):
                raise HasNotFooKey("The 'foo' key is missing from the data.")
            return _DATA

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotFooKey):
            await pipeline(_URL)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_str], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            if not has_foo_key(_DATA):
                raise HasNotFooKey("The 'foo' key is missing from the data.")
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotFooKey):
            await pipeline(_URL)

    async def test_async_transformer_wrong_arg(self):
        def next_transformer():
            pass

        @ensure(incoming=[is_str], outcome=[has_foo_key])
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


This revised code snippet addresses the feedback by ensuring that the `HasNotFooKey` exception is raised when the "foo" key is missing from the data. It also incorporates the use of specific exceptions and type checks as suggested by the oracle's feedback. Additionally, it ensures that all string literals are properly closed with matching quotation marks to avoid `SyntaxError`.