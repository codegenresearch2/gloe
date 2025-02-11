import asyncio
import unittest
from typing import TypeVar
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
        raise HasNotBarKey("The 'bar' key is missing from the data.")

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

    def test_async_transformer_wrong_arg(self):
        def just_a_normal_function():
            return None

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = request_data >> just_a_normal_function  # type: ignore

    def test_async_transformer_wrong_signature(self):
        with self.assertWarns(RuntimeWarning):
            @async_transformer  # type: ignore
            async def many_args(arg1: str, arg2: int):
                return arg1, arg2

    def test_async_transformer_hash(self):
        self.assertEqual(hash(request_data.id), request_data.__hash__())

    def test_async_transformer_previous_property(self):
        pipeline = request_data >> forward()
        self.assertEqual(pipeline.previous, request_data)

    def test_async_transformer_equality(self):
        pipeline = request_data >> forward()
        self.assertEqual(request_data, request_data)
        self.assertEqual(request_data, request_data.copy())
        self.assertNotEqual(pipeline, forward())
        self.assertNotEqual(request_data, forward())

    def test_async_transformer_pydoc_keeping(self):
        @async_transformer
        async def to_string(num: int) -> str:
            """
            This transformer receives a number as input and returns its representation as a string
            """
            return str(num)

        self.assertEqual(
            to_string.__doc__,
            """
            This transformer receives a number as input and returns its representation as a string
            """,
        )

    def test_async_transformer_signature_representation(self):
        signature = request_data.signature()
        self.assertEqual(str(signature), "(url: str) -> dict[str, str]")

    def test_async_transformer_error_forward(self):
        @async_transformer
        async def raise_error(data: dict[str, str]) -> dict[str, str]:
            raise ValueError("An error occurred")

        pipeline = request_data >> raise_error
        with self.assertRaises(ValueError):
            await pipeline(_URL)

    def test_async_transformer_error_handling(self):
        @async_transformer
        async def raise_error(data: dict[str, str]) -> dict[str, str]:
            raise ValueError("An error occurred")

        pipeline = request_data >> raise_error
        try:
            await pipeline(_URL)
        except ValueError as exception:
            self.assertEqual(type(exception.__cause__), TransformerException)
            exception_ctx = cast(TransformerException, exception.__cause__)
            self.assertEqual(raise_error, exception_ctx.raiser_transformer)

    def test_partial_async_transformer(self):
        @partial_async_transformer
        async def delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = delayed_request(0.1) >> forward()
        result = await pipeline(_URL)
        self.assertEqual(result, _DATA)

    def test_async_transformers_on_a_running_event_loop(self):
        async def run_main():
            pipeline = request_data >> forward()
            result = await pipeline(_URL)
            self.assertDictEqual(result, _DATA)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_main())

# Run the tests
if __name__ == "__main__":
    unittest.main()