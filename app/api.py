from fastapi import APIRouter, Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

router = APIRouter()

class Policy(BaseModel):
    api_key: str
    bucket_size: int
    refill_rate: float
    
# simple in-memory policy store for demo
POLICIES = {}

@router.get("/resource")
async def resource():
    # simulated upstream work - trivial
    return {"status": "ok", "data": "resource payload"}

@router.post("/set_policy")
async def set_policy(policy: Policy):
    POLICIES[policy.api_key] = {"bucket_size": policy.bucket_size, "refill_rate": policy.refill_rate}
    return{"status": "ok", "policy": POLICIES[policy.api_key]}

@router.get("/get_policy")
async def get_policy(api_key: str):
    return {"policy": POLICIES.get(api_key)}

@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)