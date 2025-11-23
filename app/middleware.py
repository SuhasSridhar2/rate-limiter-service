from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from .limiter import RateLimiter

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter
        
    async def dispatch(self, request: Request, call_next):
        # extract API key
        api_key = requestheaders.get("X-API-Key", "anonymous")
        allowed, tokens, mode = await self.limiter.allow_request(api_key)
        if not allowed:
            # Retry-After in seconds (estimate)
            retry_after = 1.0 # simple heuristic, could compute from tokens/refill
            return Response(status_code=429, content='{"error":"rate_limited", "retry_after":' + str(retry_after) + '}', media_type="application/json")
        response = await call_next(request)
        return response