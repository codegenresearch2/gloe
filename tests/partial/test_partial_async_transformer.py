import asyncio
import unittest
from gloe import partial_async_transformer
from gloe.utils import forward

class TestPartialAsyncTransformer(unittest.IsolatedAsyncioTestCase):

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.01) >> forward()

        result = await pipeline({"foo": "bar"})

        self.assertDictEqual(result, {"foo": "bar"})


In the rewritten code, I have removed the unused import for `unittest.TestCase` and replaced it with `unittest.IsolatedAsyncioTestCase` since we are using asynchronous tests. I have also updated the assertion to use `self.assertDictEqual` to compare dictionaries. Additionally, I have provided a dictionary to the `pipeline` function call as it was not defined in the original code.