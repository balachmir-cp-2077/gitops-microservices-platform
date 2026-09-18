import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(
    title="Order Service",
    description="Microservice responsible for placing customer orders and communicating with Inventory Service.",
    version=os.getenv("VERSION", "v1.0.0")
)

SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service")
VERSION = os.getenv("VERSION", "v1.0.0")
PORT = int(os.getenv("PORT", "8000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8001")

# In-memory orders store
ORDERS: List[dict] = [
    {
        "order_id": "ord-init-001",
        "item_id": "item-101",
        "item_name": "Kubernetes Action Figure",
        "quantity": 1,
        "total_price": 29.99,
        "status": "COMPLETED",
        "created_at": "2026-09-19T00:00:00Z"
    }
]

class CreateOrderRequest(BaseModel):
    item_id: str
    quantity: int = 1

@app.get("/healthz", tags=["Health"])
def health_check():
    """Liveness and readiness probe endpoint."""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT
    }

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    """HTML status dashboard displaying service health and inventory connectivity."""
    inventory_status = "UNKNOWN"
    inventory_items_count = 0
    inventory_error = None

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{INVENTORY_SERVICE_URL}/healthz")
            if resp.status_code == 200:
                inventory_status = "CONNECTED (Healthy)"
                items_resp = await client.get(f"{INVENTORY_SERVICE_URL}/api/v1/items")
                if items_resp.status_code == 200:
                    inventory_items_count = items_resp.json().get("count", 0)
            else:
                inventory_status = f"HTTP {resp.status_code}"
    except Exception as e:
        inventory_status = "DISCONNECTED"
        inventory_error = str(e)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitOps Microservices Platform</title>
        <style>
            :root {{
                --bg: #0d1117;
                --card-bg: #161b22;
                --border: #30363d;
                --text: #c9d1d9;
                --text-bright: #f0f6fc;
                --accent: #58a6ff;
                --green: #238636;
                --red: #da3633;
                --tag-bg: #21262d;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .container {{
                max-width: 800px;
                width: 100%;
            }}
            header {{
                margin-bottom: 30px;
                border-bottom: 1px solid var(--border);
                padding-bottom: 20px;
            }}
            h1 {{
                color: var(--text-bright);
                margin: 0 0 10px 0;
                font-size: 28px;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                background: var(--tag-bg);
                border: 1px solid var(--border);
                color: var(--accent);
                margin-right: 8px;
            }}
            .card-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 25px;
            }}
            .card {{
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 20px;
            }}
            .card h3 {{
                margin-top: 0;
                color: var(--text-bright);
                font-size: 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .status-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 6px;
            }}
            .online {{ background: #3fb950; box-shadow: 0 0 8px #3fb950; }}
            .offline {{ background: #f85149; box-shadow: 0 0 8px #f85149; }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                font-size: 14px;
            }}
            .label {{ color: #8b949e; }}
            .value {{ font-family: monospace; font-weight: 600; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                font-size: 14px;
            }}
            th, td {{
                text-align: left;
                padding: 10px 12px;
                border-bottom: 1px solid var(--border);
            }}
            th {{
                background: var(--tag-bg);
                color: var(--text-bright);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>GitOps Microservices Dashboard</h1>
                <div>
                    <span class="badge">Env: {ENVIRONMENT}</span>
                    <span class="badge">Order Service: {VERSION}</span>
                    <span class="badge">Kubernetes & ArgoCD Native</span>
                </div>
            </header>

            <div class="card-grid">
                <div class="card">
                    <h3>
                        <span class="status-indicator online"></span>
                        Order Service
                    </h3>
                    <div class="info-row"><span class="label">Status:</span><span class="value">RUNNING</span></div>
                    <div class="info-row"><span class="label">Version:</span><span class="value">{VERSION}</span></div>
                    <div class="info-row"><span class="label">Port:</span><span class="value">{PORT}</span></div>
                    <div class="info-row"><span class="label">Orders Total:</span><span class="value">{len(ORDERS)}</span></div>
                </div>

                <div class="card">
                    <h3>
                        <span class="status-indicator {'online' if 'CONNECTED' in inventory_status else 'offline'}"></span>
                        Inventory Link
                    </h3>
                    <div class="info-row"><span class="label">Status:</span><span class="value">{inventory_status}</span></div>
                    <div class="info-row"><span class="label">Backend URL:</span><span class="value">{INVENTORY_SERVICE_URL}</span></div>
                    <div class="info-row"><span class="label">Items in Catalog:</span><span class="value">{inventory_items_count}</span></div>
                    {f'<div class="info-row"><span class="label">Error:</span><span class="value" style="color: #f85149">{inventory_error}</span></div>' if inventory_error else ''}
                </div>
            </div>

            <div class="card">
                <h3>Recent Orders</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Item Name</th>
                            <th>Quantity</th>
                            <th>Total Price</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f"<tr><td><code>{o['order_id']}</code></td><td>{o['item_name']}</td><td>{o['quantity']}</td><td>${o['total_price']:.2f}</td><td><span class='badge' style='color:#3fb950;'>{o['status']}</span></td></tr>" for o in ORDERS])}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/api/v1/orders", tags=["Orders"])
def list_orders():
    """Retrieve all placed orders."""
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "count": len(ORDERS),
        "orders": ORDERS
    }

@app.post("/api/v1/orders", tags=["Orders"], status_code=201)
async def create_order(request: CreateOrderRequest):
    """
    Create a new order.
    Calls Inventory Service to verify item availability and retrieve pricing.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{INVENTORY_SERVICE_URL}/api/v1/items/{request.item_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Item '{request.item_id}' not found in inventory.")
            elif resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Failed to query inventory service: {resp.status_code}")
            
            item_data = resp.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Inventory service unreachable at {INVENTORY_SERVICE_URL}: {str(e)}"
        )

    if item_data.get("stock", 0) < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for '{item_data.get('name')}'. Available: {item_data.get('stock')}"
        )

    new_order = {
        "order_id": f"ord-{uuid.uuid4().hex[:8]}",
        "item_id": request.item_id,
        "item_name": item_data.get("name"),
        "quantity": request.quantity,
        "total_price": round(item_data.get("price", 0.0) * request.quantity, 2),
        "status": "COMPLETED",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    ORDERS.append(new_order)
    return new_order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)
