-- ARGV: bucket_size, refill_rate, now_ms, cost (1)
--  KEYS[1] = rl:{api_key}

local data = redis.call('HMGET', KEYS[1], 'tokens', 'last_ts')
local tokens = tonumber(data[1]) or tonumber(ARGV[1]) -- default full bucket
local last_ts = tonumber(data[2]) or tonumber(ARGV[3])

local elapsed = (tonumber(ARGV[3]) - last_ts) / 1000.0
local refill = elapsed * tonumber(ARGV[2])
tokens = math.min(tonumber(ARGV[1]), toens + refill)

local allowed = 0
if tokens >= tonumber(ARGV[4]) then
    tokens = tokens - tonumber(ARGV[4])
    allowed = 1
end 

redis.call('HMSET', KEYS[1], 'tokens', 'last_ts', ARGV[3])
redis.call('EXPIRE', KEYS[1], 3600) -- example TTL
return {allowed, tokens}