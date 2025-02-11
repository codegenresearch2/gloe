import asyncio
import unittest
from gloe import partial_async_transformer
from gloe.utils import forward

class TestPartialAsyncTransformer(unittest.IsolatedAsyncioTestCase):

    async def test_partial_async_transformer(self):
        _DATA = {"foo": "bar"}

        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.01) >> forward()
        result = await pipeline(_DATA)
        self.assertDictEqual(result, _DATA)


In the rewritten code, I have removed the unused import statement for `unittest.TestCase` and replaced it with `unittest.IsolatedAsyncioTestCase` as it is required for testing asynchronous code. I have also defined `_DATA` within the test method to minimize redundancy. Finally, I have used `assertDictEqual` instead of `assertEqual` to compare dictionaries, which is a more appropriate method for this use case.