-- scripts/token_bucket.lua
-- KEYS[1] = rl:{api_key}
-- ARGV[1] = bucket_size (number)
-- ARGV[2] = refill_rate (tokens per second, number)
-- ARGV[3] = now_ms (number)
-- ARGV[4] = cost (tokens to consume, typically 1)

local key = KEYS[1]
local bucket_size = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_ts')
local tokens = tonumber(data[1])
local last_ts = tonumber(data[2])

if tokens == nil then
    tokens = bucket_size
    last_ts = now_ms
end

local elapsed = (now_ms - last_ts) / 1000.0
if elapsed > 0 then
    local refill = elapsed * refill_rate
    tokens = math.min(bucket_size, tokens + refill)
end

local allowed = 0
if tokens >= cost then
    tokens = tokens - cost
    allowed = 1
end

redis.call('HMSET', key, 'tokens', tokens, 'last_ts', now_ms)
redis.call('EXPIRE', key, 3600) -- key expiry to free memory if inactive

return {allowed, tostring(tokens)}