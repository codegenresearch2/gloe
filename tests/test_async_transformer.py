import asyncio\\nimport unittest\\nfrom typing import TypeVar, Any\\nfrom gloe import async_transformer, ensure\\nfrom gloe.functional import partial_async_transformer\\nfrom gloe.utils import forward\\n\\n_In = TypeVar("_In")\\n\\n_DATA = {"foo": "bar"}\\n\\nclass HasNotBarKey(Exception):\\n    pass\\n\\ndef has_bar_key(dict: dict[str, str]):\\n    if "bar" not in dict.keys():\\n        raise HasNotBarKey()\\n\\n_URL = "http://my-service"\\n\\nclass TestAsyncTransformer(unittest.IsolatedAsyncioTestCase):\\n    async def test_basic_case(self):\\n        @async_transformer\\n        async def request_data(url: str) -> dict[str, str]:\\n            await asyncio.sleep(0.1)\\n            return _DATA\\n\\n        test_forward = request_data >> forward()\\n\\n        result = await test_forward(_URL)\\n\\n        self.assertDictEqual(result, _DATA)\\n\\n    async def test_begin_with_transformer(self):\\n        @async_transformer\\n        async def request_data(url: str) -> dict[str, str]:\\n            await asyncio.sleep(0.1)\\n            return _DATA\\n\\n        test_forward = forward[str]() >> request_data\\n\\n        result = await test_forward(_URL)\\n\\n        self.assertDictEqual(result, _DATA)\\n\\n    async def test_async_on_divergent_connection(self):\\n        @async_transformer\\n        async def request_data(url: str) -> dict[str, str]:\\n            await asyncio.sleep(0.1)\\n            return _DATA\\n\\n        test_forward = forward[str]() >> (forward[str](), request_data)\\n\\n        result = await test_forward(_URL)\\n\\n        self.assertEqual(result, (_URL, _DATA))\\n\\n    async def test_divergent_connection_from_async(self):\\n        @async_transformer\\n        async def request_data(url: str) -> dict[str, str]:\\n            await asyncio.sleep(0.1)\\n            return _DATA\\n\\n        test_forward = request_data >> (forward[dict[str, str]](), forward[dict[str, str]]())\\n\\n        result = await test_forward(_URL)\\n\\n        self.assertEqual(result, (_DATA, _DATA))\\n\\n    async def test_partial_async_transformer(self):\\n        @partial_async_transformer\\n        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:\\n            await asyncio.sleep(delay)\\n            return data\\n\\n        pipeline = sleep_and_forward(0.1) >> forward()\\n\\n        result = await pipeline(_DATA)\\n\\n        self.assertEqual(result, _DATA)\\n\\n    async def test_ensure_async_transformer(self):\\n        @ensure(outcome=[has_bar_key])\\n        @async_transformer\\n        async def ensured_request(url: str) -> dict[str, str]:\\n            await asyncio.sleep(0.1)\\n            return _DATA\\n\\n        pipeline = ensured_request >> forward()\\n\\n        with self.assertRaises(HasNotBarKey):\\n            await pipeline(_URL)\\n\\n    async def test_ensure_partial_async_transformer(self):\\n        @ensure(outcome=[has_bar_key])\\n        @partial_async_transformer\\n        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:\\n            await asyncio.sleep(delay)\\n            return _DATA\\n\\n        pipeline = ensured_delayed_request(0.1) >> forward()\\n\\n        with self.assertRaises(HasNotBarKey):\\n            await pipeline(_URL)\\n