# rate-limiter-service
Distributed Rate Limiter with token bucket and sliding window variants

## 1. Problem statement
high-throughput rate limiter supporting Token Bucket and Sliding Window algorithms. Supports distributed environments using Redis.

## 2. Requirements
- per-user and global rate limiting
- Configurable limits and windows
- Low-latency checks (<5ms local, <15ms distributed)
- Burst handling
- Fault tolerance

## 3. API Design
- Post /check
- Post consume
- Get

## 4. Architecture
(Architecture diagram will be added here)

## 5. Scaling Plan
- Redis for distributed counters
- Lua scripting for atomic operations
- SHarding strategy
- Caching layers
- Failure mechanism

## 6. Load Testing Plan
Tools: k6
Metrics: p95, p99 latency, max RPS, failure thresholds

## 7. Results
(TBA)

## 8. Improvements
(TBA)