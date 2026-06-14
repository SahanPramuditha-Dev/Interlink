from fastapi import FastAPI, HTTPException, Query 
# HTTPException: Instantly triggers standard HTTP error status codes (e.g., 400 Bad Request, 404 Not Found).
# Query: Handles validation, engine metadata, and custom descriptions for incoming URL query parameters.

from fastapi.middleware.cors import CORSMiddleware 
# CORS Middleware: Manages Cross-Origin Resource Sharing. Essential for security clearance when frontends 
# hosted on separate local ports/domains attempt to communicate with this API.

from anyio import to_thread 
# to_thread: An AnyIO utility that offloads blocking code to a separate, isolated worker thread pool.
# This prevents synchronous delays from stalling FastAPI's primary asynchronous event loop.

import ipaddress 
# ipaddress: Python standard library used to parse and validate structural IP compliance,
# ensuring malformed strings are intercepted before hitting raw network sockets.

from ping3 import ping 
# ping3: Third-party utility providing an interface for sending ICMP echo requests. 
# It abstracts raw socket bindings into readable Python metric executions.

# Instantiate FastAPI with documentation metadata used by automated OpenAPI/Swagger UIs.
app = FastAPI(
    title="Network Device Monitor",
    description="A fast, non-blocking API to check device latency.",
)

# --- CORS Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Wildcard allows access from any frontend origin during local development.
    allow_credentials=True,  # Enables cookies and authorization headers across cross-origin boundaries.
    allow_methods=["*"],     # Allows all standard HTTP methods (GET, POST, PUT, DELETE).
    allow_headers=["*"],     # Accepts all custom request headers sent by browser clients.
)


def _sync_ping(ip: str) -> dict:
    """
    A private helper function that handles raw synchronous ping execution.
    Designed to run exclusively within an isolated thread pool.
    """
    try:
        # Executes ping packet. Returns float (seconds), False (routing failure), or None (timeout).
        result = ping(ip, timeout=2)

        # Catch dead targets, non-existent routes, or local connectivity drops
        if result is None or result is False:
            return {"ip": ip, "status": "offline", "latency_ms": None}
        
        # Catch successful returns, converting seconds to readable milliseconds
        else:
            return {
                "ip": ip,
                "status": "online",
                "latency_ms": round(result * 1000, 2),
            }
            
    except Exception as e:
        # Safely catch system or permission exceptions (e.g., Linux missing raw socket privileges)
        return {"ip": ip, "status": "error", "error_details": str(e)}


# --- Async Routing Interface ---
@app.get("/check") 
async def check(
    # '...' (Ellipsis) declares this URL parameter strictly required (?ip=x.x.x.x)
    ip: str = Query(..., description="The IP address or hostname to ping")
):
    """
    async def: Declares the route asynchronous, yielding control straight to the event loop.
    """
    # 1. Structural Sanity Validation
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid IP address format."
        )

    # 2. Asynchronous Thread Offloading Execution Flow
    # to_thread.run_sync: Isolates the blocking '_sync_ping' out of the event loop.
    # await: Pauses this isolated context, freeing the server to handle other traffic.
    data = await to_thread.run_sync(_sync_ping, ip)
    
    # 3. Server Response
    return data