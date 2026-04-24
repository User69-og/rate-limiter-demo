import time
import fakeredis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Connect to FakeRedis (in-memory, no external server needed!)
r = fakeredis.FakeRedis(decode_responses=True)

RATE_LIMIT = 5.0  # Tokens refilled per second
CAPACITY = 10.0   # Maximum burst capacity

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    current_time = time.time()
    
    # Fetch current bucket state from FakeRedis
    bucket = r.hgetall(key)
    
    if not bucket:
        r.hset(key, mapping={"tokens": CAPACITY - 1, "last_refill": current_time})
        return await call_next(request)
    
    tokens = float(bucket.get("tokens", CAPACITY))
    last_refill = float(bucket.get("last_refill", current_time))
    
    elapsed = current_time - last_refill
    tokens_to_add = elapsed * RATE_LIMIT
    tokens = min(CAPACITY, tokens + tokens_to_add)
    
    if tokens >= 1:
        tokens -= 1
        r.hset(key, mapping={"tokens": tokens, "last_refill": current_time})
        return await call_next(request)
    else:
        r.hset(key, mapping={"tokens": tokens, "last_refill": current_time})
        return JSONResponse(status_code=429, content={"error": "Too Many Requests. Rate limit exceeded."})

@app.get("/api/data")
def get_data():
    return {"message": "Success! You hit the API."}