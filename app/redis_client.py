# app/redis_client.py

import asyncio
import os
from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class RedisClient:
    def __init__(self):
        self._redis = aioredis.from_url(REDIS_URL, decode_resposes=True)
        self._script_sha = None
        
    async def load_script(self, script_str: str):
        self._script_sha = await self._redis.script_load(script_str)
        return self._script_sha
    
    async def evalsha(self, sha, keys, args, timeout_ms: int = 500):
        # set a timeout for Redis call
        try: 
            coro = self._redis.evalsha(sha, len(keys), *(keys + args))
            return await asyncio.wait_for(coro, timeout=timeout_ms/1000.0)
        except asyncio.TimeoutError:
            raise TimeoutError("Redis script eval timed out")
        except aioredis.exceptions.RedisError as e:
            raise ConnectionError(f"Redis error: {e}")
        
    def client(self):
        return self._redis