# app/limiter.py

import time 
import asyncio
from typing import Tuple
from prometheus_client import Counter, Histogram, Gauge

from .redis_client import RedisClient

REQUESTS_TOTAL = Counter("app_requests_total", "Total requests")
REQUESTS_ALLOWED = Counter("app_requests_allowed_total", "Total allowed requests")
REQUESTS_BLOCKED = Counter("app_requests_blocked_total", "Total blocked requests")
REDIS_LATENCY = Histogram("app_redis_latency_seconds", "Redis call latency seconds", buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1))
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency seconds", buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1))
TOKENS_REMAINING = Gauge("app_tokens_remaining", "Tokens remaining (sample)")

class LocalTokenBucket:
    def __init__(self, bucket_size: float, refill_rate:float):
        self.tokens = bucket_size
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate
        self.last_ts = time.time()
        self._lock = asyncio.Lock()
        
    async def allow(self, cost: float = 1.0) -> Tuple[bool, float]:
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_ts
            if elapsed > 0:
                refill = elapsed * self.refill_rate
                self.tokens = min(self.bucket_size, self.tokens + refill)
                self.last_ts = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True, self.tokens
            return False, self.tokens
        
class RateLimiter:
    def __init__(self, redis_client: RedisClient, lua_script_str: str):
        self.redis = redis_client
        self.lua = lua_script_str
        self.lua_sha = None
        # conservative local fallback
        self.local_buckets = {} # api_key -> LocalTokenBucket
        self.local_bucket_cfg = (5.0, 1.0) # bucket_size, refill_rate
        self._local_lock = asyncio.Lock()
        
    async def init(self):
        self.lua_sha = await self.redis.load_script(self.lua)
        
    async def _get_local_bucket(self, key):
        async with self._local_lock:
            if key not in self.local_buckets:
                self.local_buckets[key] = LocalTokenBucket(*self.local_bucket_cfg)
            return self.local_buckets[key]
        
    async def allow_request(self, api_key: str, bucket_size: int = 40, refill_rate: float = 10.0, cost: int = 1) -> uple[bool, float, str]:
        """ Return (allowed, tokens_remaining, mode) where mode indicates 'redis' or 'local' """
        REQUEST_TOTAL.inc()
        start = time.time()
        now_ms = int(time.time() * 1000)
        key = f"rl:{api_key}"
        try:
            with REDIS_LATENCY.time():
                res = await self.redis.evalsha(self.lua_sha, [key], [str(bucket_size), str(refill_rate), str(now_ms), str(cost)])
            # redis returns table {allowed, tokens_str}
            allowed = bool(int(res[0]))
            tokens = float(res[1])
            REQUEST_LATENCY.observe(time.time() - start)
            if allowed:
                REQUESTS_ALLOWED.inc()
            else:
                REQUESTS_BLOCKED.inc()
            try:
                TOKENS_REMAINING.set(tokens)
            except Exception:
                pass
            return allowed, tokens, "redis"
        except (TimeoutError, ConnectionError) as e:
            # fallback to local token bucket (degraded mode)
            bucket = await self._get_local_bucket(api_key)
            allowed, tokens = await bucket.allow(cost)
            REQUEST_LATENCY.observe(time.time() - start)
            if allowed:
                REQUESTS_ALLOWED.inc()
            else:
                REQUESTS_BLOCKED.inc()
            return allowed, tokens, "local"