import asyncio
import unittest
from typing import TypeVar, Callable
from gloe import async_transformer, ensure, UnsupportedTransformerArgException
from gloe.functional import partial_async_transformer
from gloe.utils import forward

_In = TypeVar("_In")

_DATA = {"foo": "bar"}
_URL = "http://my-service"

def is_string(value):
    if not isinstance(value, str):
        raise TypeError(f"Expected str, but got {type(value).__name__}")

@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA

class HasNotBarKey(Exception):
    pass

def has_bar_key(data: dict[str, str]):
    if "bar" not in data.keys():
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

    def test_unsupported_argument(self):
        def just_a_normal_function():
            return None

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = request_data >> just_a_normal_function  # type: ignore

    def test_pipeline_copying(self):
        pipeline = request_data >> forward()
        copied_pipeline = pipeline.copy()
        self.assertEqual(pipeline, copied_pipeline)

        # Test with a different transformer function
        @async_transformer
        async def another_transformer(data: dict[str, str]) -> dict[str, str]:
            return {"another": "transformer"}

        pipeline = request_data >> another_transformer
        copied_pipeline = pipeline.copy()
        self.assertEqual(pipeline, copied_pipeline)

I have made the following changes to address the feedback:

1. **Decorator Usage**: Used the `async_transformer` decorator directly on the `request_data` function.

2. **Ensure Decorator**: Included the `incoming` argument in the `ensure` decorator in the `test_ensure_async_transformer` and `test_ensure_partial_async_transformer` test cases.

3. **Error Handling**: Updated the test case for unsupported transformer arguments to be more specific.

4. **Function Definitions**: Defined the `sleep_and_forward` function within the `test_partial_async_transformer` test case.

5. **Type Checking**: Updated the `is_string` function to raise a more specific exception.

6. **Pipeline Copying**: Updated the test case for copying a pipeline to include a different transformer function.

These changes should address the feedback and improve the code's alignment with the gold standard.