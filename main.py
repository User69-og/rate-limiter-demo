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
    
    # Strict 5-Second Penalty Box Logic
    if "penalty_until" in bucket:
        penalty_until = float(bucket["penalty_until"])
        if current_time < penalty_until:
            return JSONResponse(status_code=429, content={"error": "Locked out. Wait."})
        else:
            r.delete(key)
            bucket = {}

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
        r.hset(key, mapping={"penalty_until": current_time + 5.0})
        return JSONResponse(status_code=429, content={"error": "Too Many Requests. Wait 5 seconds."})

@app.get("/")
def serve_frontend():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Design: Rate Limiting</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin-top: 5vh; background-color: #121212; color: #ffffff;}
            .card { background-color: #1e1e1e; padding: 30px; border-radius: 10px; width: 60%; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            .header-info { color: #888; font-size: 13px; margin-top: -15px; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px; }
            button { padding: 15px 40px; font-size: 18px; font-weight: bold; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; margin-top: 10px;}
            button:active { transform: scale(0.98); }
            #status { margin-top: 20px; font-size: 20px; font-weight: bold; min-height: 30px; }
            .success { color: #00e676; }
            .blocked { color: #ff1744; }
            
            /* Table Styles */
            .log-container { margin-top: 30px; max-height: 250px; overflow-y: auto; background-color: #252525; border-radius: 8px; border: 1px solid #333; }
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th, td { padding: 12px 15px; border-bottom: 1px solid #333; }
            th { background-color: #1a1a1a; position: sticky; top: 0; }
            .row-success { border-left: 4px solid #00e676; }
            .row-blocked { border-left: 4px solid #ff1744; color: #ff5252; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Authentication Gateway</h2>
            <div class="header-info">Project by Pujara Nirmit Sumitbhai | 25MCA0216</div>
            <p>Limit: 3 attempts. Lockout cooldown: 5 seconds.</p>
            <button onclick="attemptLogin()">Attempt Login</button>
            <div id="status">Ready</div>
            
            <div class="log-container">
                <table id="logTable">
                    <thead>
                        <tr>
                            <th>Attempt #</th>
                            <th>Timestamp</th>
                            <th>Server Response</th>
                        </tr>
                    </thead>
                    <tbody id="logBody">
                        </tbody>
                </table>
            </div>
        </div>
        <script>
            let attemptCount = 0;
            async function attemptLogin() {
                attemptCount++;
                const statusDiv = document.getElementById('status');
                const tbody = document.getElementById('logBody');
                const now = new Date().toLocaleTimeString();
                const row = document.createElement('tr');
                
                statusDiv.innerHTML = "Authenticating...";
                statusDiv.className = "";
                
                try {
                    const response = await fetch('/api/login');
                    if (response.status === 200) {
                        statusDiv.innerHTML = "✅ Login Successful! (200 OK)";
                        statusDiv.className = "success";
                        row.className = "row-success";
                        row.innerHTML = `<td>${attemptCount}</td><td>${now}</td><td>✅ 200 OK - Allowed</td>`;
                    } else if (response.status === 429) {
                        statusDiv.innerHTML = "🚫 Blocked: Too Many Requests! Wait 5 sec.";
                        statusDiv.className = "blocked";
                        row.className = "row-blocked";
                        row.innerHTML = `<td>${attemptCount}</td><td>${now}</td><td>🚫 429 Too Many Requests</td>`;
                    }
                } catch (e) {
                    statusDiv.innerHTML = "Network Error";
                    row.innerHTML = `<td>${attemptCount}</td><td>${now}</td><td>⚠️ Network Error</td>`;
                }
                
                // Add the new row to the top of the table
                tbody.prepend(row);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/login")
def login():
    return {"message": "Authenticated"}