import asyncio
import unittest
from typing import TypeVar, Any, cast
from gloe import async_transformer, ensure, UnsupportedTransformerArgException, transformer, AsyncTransformer, TransformerException
from gloe.async_transformer import _execute_async_flow
from gloe.functional import partial_async_transformer
from gloe.utils import forward
from tests.lib.ensurers import is_odd
from tests.lib.exceptions import LnOfNegativeNumber, NumbersEqual, NumberIsEven
from tests.lib.transformers import async_plus1, async_natural_logarithm, minus1

# Define constants
_In = TypeVar("_In")
_DATA = {"foo": "bar"}
_URL = "http://my-service"

# Define custom exceptions
class DataValidationError(Exception):
    """Exception raised for data validation errors."""
    pass

# Define helper functions
def validate_data(data: dict[str, str], key: str, should_have: bool):
    """Validate if the data has a specific key."""
    if should_have and key not in data.keys():
        raise DataValidationError(f"Data does not have '{key}' key.")
    if not should_have and key in data.keys():
        raise DataValidationError(f"Data should not have '{key}' key.")

# Define async transformers
@async_transformer
async def request_data(url: str) -> dict[str, str]:
    """Async transformer that requests data from a given URL."""
    await asyncio.sleep(0.01)
    return _DATA

class RequestData(AsyncTransformer[str, dict[str, str]]):
    """Async transformer class that requests data from a given URL."""
    async def transform_async(self, url: str) -> dict[str, str]:
        await asyncio.sleep(0.01)
        return _DATA

# Define test cases
class TestAsyncTransformer(unittest.IsolatedAsyncioTestCase):
    """Test cases for async transformers."""

    async def test_basic_case(self):
        """Test the basic case of an async transformer."""
        test_forward = request_data >> forward()
        result = await test_forward(_URL)
        self.assertDictEqual(_DATA, result)

    async def test_begin_with_transformer(self):
        """Test beginning a pipeline with a transformer."""
        test_forward = forward[str]() >> request_data
        result = await test_forward(_URL)
        self.assertDictEqual(_DATA, result)

    async def test_async_on_divergent_connection(self):
        """Test an async transformer on a divergent connection."""
        test_forward = forward[str]() >> (forward[str](), request_data)
        result = await test_forward(_URL)
        self.assertEqual((_URL, _DATA), result)

    async def test_divergent_connection_from_async(self):
        """Test a divergent connection from an async transformer."""
        test_forward = request_data >> (forward[dict[str, str]](), forward[dict[str, str]]())
        result = await test_forward(_URL)
        self.assertEqual((_DATA, _DATA), result)

    async def test_async_transformer_wrong_arg(self):
        """Test an async transformer with an unsupported argument."""
        def next_transformer():
            pass

        @ensure(outcome=[lambda data: validate_data(data, 'bar', True)])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        with self.assertRaises(UnsupportedTransformerArgException):
            ensured_delayed_request(0.01) >> next_transformer  # type: ignore

    async def test_async_transformer_copy(self):
        """Test copying an async transformer."""
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
        self.assertEqual(_DATA, result)

    def test_async_transformer_wrong_signature(self):
        """Test an async transformer with an incorrect signature."""
        with self.assertWarns(RuntimeWarning):
            @async_transformer  # type: ignore
            async def many_args(arg1: str, arg2: int):
                await asyncio.sleep(1)
                return arg1, arg2

    def test_async_transformer_signature_representation(self):
        """Test the representation of an async transformer's signature."""
        signature = request_data.signature()
        self.assertEqual(str(signature), "(url: str) -> dict[str, str]")

    def test_async_transformer_representation(self):
        """Test the representation of an async transformer."""
        self.assertEqual(repr(request_data), "str -> (request_data) -> dict[str, str]")
        class_request_data = RequestData()
        self.assertEqual(repr(class_request_data), "str -> (RequestData) -> dict[str, str]")

        @transformer
        def dict_to_str(_dict: dict) -> str:
            return str(_dict)

        request_and_serialize = request_data >> dict_to_str
        self.assertEqual(repr(request_and_serialize), "dict -> (2 transformers omitted) -> str")

    async def test_exhausting_large_flow(self):
        """Test the instantiation of a large graph."""
        graph = async_plus1
        max_iters = 1500
        for _ in range(max_iters):
            graph = graph >> async_plus1
        result = await graph(0)
        self.assertEqual(result, max_iters + 1)

    async def test_async_transformer_error_handling(self):
        """Test if a raised error stores the correct TransformerException as its cause."""
        async_graph = async_plus1 >> async_natural_logarithm
        try:
            await async_graph(-2)
        except LnOfNegativeNumber as exception:
            self.assertEqual(type(exception.__cause__), TransformerException)
            exception_ctx = cast(TransformerException, exception.__cause__)
            self.assertEqual(async_natural_logarithm, exception_ctx.raiser_transformer)

    async def test_execute_async_wrong_flow(self):
        """Test executing an async flow with an incorrect argument."""
        flow = [2]
        with self.assertRaises(NotImplementedError):
            await _execute_async_flow(flow, 1)  # type: ignore

    async def test_composition_transform_method(self):
        """Test the transform_async method of a composed transformer."""
        test3 = forward[float]() >> async_plus1
        result = await test3.transform_async(5)
        self.assertIsNone(result)
        test2 = forward[float]() >> (async_plus1, async_plus1)
        result2 = await test2.transform_async(5)
        self.assertIsNone(result2)

async def raise_an_error():
    """Async function that raises a NotImplementedError."""
    await asyncio.sleep(0.1)
    raise NotImplementedError()