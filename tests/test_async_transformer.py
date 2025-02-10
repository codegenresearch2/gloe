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

_In = TypeVar("_In")

_DATA = {"foo": "bar"}


@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA


class HasNotFooKey(Exception):
    pass


class HasFooKey(Exception):
    pass


class IsNotInt(Exception):
    pass


class HasNotBarKey(Exception):
    pass


def has_foo_key(data: dict[str, str]):
    if "foo" not in data.keys():
        raise HasNotFooKey()


def is_int(data: Any):
    if not isinstance(data, int):
        raise IsNotInt()


def has_bar_key(data: dict[str, str]):
    if "bar" not in data.keys():
        raise HasNotBarKey()


def remove_foo_key(data: dict[str, str]):
    if "foo" in data:
        del data["foo"]
    return data


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
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = _DATA
            has_foo_key(result)
            return result

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotFooKey):
            await pipeline(123)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = _DATA
            has_foo_key(result)
            return result

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotFooKey):
            await pipeline(123)

    async def test_async_transformer_wrong_arg(self):
        def next_transformer():
            pass

        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = _DATA
            has_foo_key(result)
            return result

        with self.assertRaises(UnsupportedTransformerArgException):
            pipeline = ensured_delayed_request(0.1) >> next_transformer

    async def test_async_transformer_copy(self):
        @transformer
        def add_slash(path: str) -> str:
            return path + "/"

        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = _DATA
            has_foo_key(result)
            return result

        pipeline = add_slash >> ensured_delayed_request(0)

        pipeline = pipeline.copy()
        result = await pipeline(_URL)
        self.assertEqual(result, _DATA)

    async def test_ensure_async_transformer_with_bar_key(self):
        @ensure(incoming=[is_int], outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = _DATA
            has_bar_key(result)
            return result

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(123)

    async def test_ensure_partial_async_transformer_with_bar_key(self):
        @ensure(incoming=[is_int], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = _DATA
            has_bar_key(result)
            return result

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(123)

    async def test_async_transformer_with_string_arg(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = _DATA
            has_foo_key(result)
            return result

        with self.assertRaises(IsNotInt):
            await ensured_request("http://my-service")

    async def test_ensure_async_transformer_with_string_arg(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = _DATA
            has_foo_key(result)
            return result

        with self.assertRaises(IsNotInt):
            await ensured_request("http://my-service")

    async def test_ensure_partial_async_transformer_with_string_arg(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = _DATA
            has_foo_key(result)
            return result

        with self.assertRaises(IsNotInt):
            await ensured_delayed_request("http://my-service", 0.1)

    async def test_async_transformer_with_remove_foo_key(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = remove_foo_key(_DATA)
            has_foo_key(result)
            return result

        await ensured_request(123)

    async def test_ensure_async_transformer_with_remove_foo_key(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            result = remove_foo_key(_DATA)
            has_foo_key(result)
            return result

        await ensured_request(123)

    async def test_ensure_partial_async_transformer_with_remove_foo_key(self):
        @ensure(incoming=[is_int], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            result = remove_foo_key(_DATA)
            has_foo_key(result)
            return result

        await ensured_delayed_request(123, 0.1)