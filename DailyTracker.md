### Day-1 Progress (Token Bucket)
- Project name: rate-limiter-service
- Implemented: local token-bucket (thread-safe) at `rate_limiter/token_bucket.py`
- Tests added: `tests/test_token_bucket.py` (pytest)
- Benchmark script: `scripts/benchmark_token_bucket.py`


### Day - 2 Progress (Sliding Window Counter):
- Implemented sliding window counter rate limiter with prev+current windows.
- Added tests for window shifts, partial sliding, and strict limits.
- Added benchmark script.

### Day - 3 Progress (Sliding Window Log - Exact Sliding Window):
- Implemented Log-based exact sliding window rate limiter.
- Added timestamp pruning logic.
- Added tests for exact expiration and correctness.
- Added benchmark comparing performance to Sliding Counter and Token Bucket.

### Day - 4 Progress ():