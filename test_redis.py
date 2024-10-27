import redis.asyncio as aioredis

async def main():
    redis = aioredis.from_url("redis://localhost:6379")
    await redis.set("test_key", "test_value")
    value = await redis.get("test_key")
    print(value)

import asyncio
asyncio.run(main())
