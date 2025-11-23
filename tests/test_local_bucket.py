import asyncio
from app.limiter import LocalTokenBucket 

async def test_local_bucket_allows_and_refills():
    b = LocalTokenBucket(bucket_size = 3, refill_rate = 1)
    allowed, tokens = await b.allow(1)
    assert allowed
    assert tokens <= 2.0
    # deplete
    await b.allow(1)
    await b.allow(1)
    allowed2, _ = await b.allow(1)
    assert not allowed2
    # wait to refill
    await asyncio.sleep(1.2)
    allowed3, _ = await b.allow(1)
    assert allowed3