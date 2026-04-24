import time
import fakeredis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse

app = FastAPI()
r = fakeredis.FakeRedis(decode_responses=True)

CAPACITY = 3.0   
RATE_LIMIT = 0.2  

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path != "/api/login":
        return await call_next(request)

    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    current_time = time.time()
    
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
        return JSONResponse(status_code=429, content={"error": "Too Many Requests. Wait 5 seconds."})

@app.get("/")
def serve_frontend():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Design: Rate Limiting</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin-top: 10vh; background-color: #121212; color: #ffffff;}
            .card { background-color: #1e1e1e; padding: 40px; border-radius: 10px; width: 50%; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            button { padding: 15px 40px; font-size: 18px; font-weight: bold; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; margin-top: 20px;}
            button:active { transform: scale(0.98); }
            #status { margin-top: 30px; font-size: 22px; font-weight: bold; min-height: 30px; }
            .success { color: #00e676; }
            .blocked { color: #ff1744; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Authentication Gateway</h2>
            <p>Limit: 3 attempts. Lockout cooldown: 5 seconds.</p>
            <button onclick="attemptLogin()">Attempt Login</button>
            <div id="status">Ready</div>
        </div>
        <script>
            async function attemptLogin() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = "Authenticating...";
                statusDiv.className = "";
                try {
                    const response = await fetch('/api/login');
                    if (response.status === 200) {
                        statusDiv.innerHTML = "✅ Login Successful! (200 OK)";
                        statusDiv.className = "success";
                    } else if (response.status === 429) {
                        statusDiv.innerHTML = "🚫 Blocked: Too Many Requests! Wait 5 sec.";
                        statusDiv.className = "blocked";
                    }
                } catch (e) {
                    statusDiv.innerHTML = "Network Error";
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/login")
def login():
    return {"message": "Authenticated"}