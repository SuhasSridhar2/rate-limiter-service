## Overview
A lightweight rate-limiting service built with FastAPI and Redis using the Token Bucket algorithm.
It enforces request limits for clients, prevents overload during traffic spikes, and provides predictable system behavior under burst workloads.

## Why Rate Limiting Matters:
- Every distributed system has a throughput ceiling; When traffic exceeds that limit, queues grow and tail latency spikes.
- High latency triggers client retries, which results in retry storms that cascade into system-wide failures.
- Without rate limits, a single noisy client can monopolize shared resources and starve other users, breaking fairness guarantees.
- Systems cannot scale instantly-autoscaling, caches, and DB pools require warm-up time; rate limiting smooths bursts into manageable traffic.
- Overload causes cache eviction, lock contention, and even region failover; rate limiting ensures stable and predictable operation under load.

## Constraints and Assumptions
Traffic model:
- Steady load: 500 req/s
- Peak load: 1200 req/s
- Burst duration: 4 seconds

Client Population
- ~12,000 active clients
- Identified via API key

Rate Limit Policy (Taken Bucket)
- Bucket size: 40 tokens
- Refill rate: 10 tokens/second
- Supports short bursts while enforcing a sustained rate

Latency Budget:
- Rate limiter should add < 3 ms p99 latency

Redis Performance Assumptions:
- Local Redis latency: 0.5 - 1 ms
- Token check requires: 1 GET + 1 Lua script
- Max safe throughput assumed: ~50k ops/sec

Key Cardinality:
- 1 Redis key per client
- ~12,000 total keys

Deployment Assumptions:
- Local deployment using Docker
- Single Redis instance
- Horizontally scalable at the app layer
- No multi-region or cluster complexity in this project

## Functional Requirements
1. The system must enforce a rate limit per API key using the Token Bucket algorithm.
2. Each incoming request must check the current token count and allow/block based on availability.
3. The system must return HTTP 200 when allowed and 429 "Too Many Requests when blocked.
4. The system must maintain rate-limit state in Redis to allow horizontal scaling of the FastAPI nodes.
5. The system must maintain rate-limited user endpoint: GET /resource.
6. The system must expose an admin endpoint to configure or update rate-limit policies.
7. The system must expose a /metrics endpoint for Prometheus scraping.
8. The system must log rate-limit violations and internal errors.

## Non-Fuctional Requirements
1. Low latency
2. High availability
3. Horizontal scalability
4. Consistency
5. Predictability
6. Fault tolerance
7. Observability
8. Minimal Redis footprint

## High-Level Architecture
+--------+     +----------------+     +--------+     +-----------+
| Client | --> | FastAPI (app)  | --> | Redis  | --> | Upstream  |
|        |     | (rate limiter) |     | (state)|     | service   |
+--------+     +----------------+     +--------+     +-----------+
                    |   ^
                    v   |
                 /metrics (Prom) |
                    |            |
                  Locust/k6      |

