import asyncio
import unittest

from gloe import partial_async_transformer
from gloe.utils import forward


class TestPartialAsyncTransformer(unittest.TestCase):

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:\n            await asyncio.sleep(delay)\n            return data\n\n        pipeline = sleep_and_forward(0.01) >> forward()\n\n        result = await pipeline(_DATA)\n\n        self.assertEqual(result, _DATA)