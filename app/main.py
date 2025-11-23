import asyncio
import os
from fastapi import FastAPI
import uvicorn
from .redis_client import RedisClient
from .limiter import RateLimiter
from .middleware import RateLimitMiddleware
from .api import router
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(ROOT /"scripts"/ "token_bucket.lua", "r") as f:
    LUA_SCRIPT = f.read()
    
app = FastAPI(title="Rate Limiter Service")
app.include_router(router)

redis_client = RedisClient()
rate_limiter = RateLimiter(redis_client, LUA_SCRIPT)

@app.on_event("startup")
async def startup_event():
    await rate_limiter.init()
    # attach middleware after init
    app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)
    
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)