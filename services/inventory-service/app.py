import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI(
    title="Inventory Service",
    description="Microservice responsible for managing product inventory and stock levels.",
    version=os.getenv("VERSION", "v1.0.0")
)

SERVICE_NAME = os.getenv("SERVICE_NAME", "inventory-service")
VERSION = os.getenv("VERSION", "v1.0.0")
PORT = int(os.getenv("PORT", "8001"))

# In-memory inventory catalog
ITEMS: Dict[str, dict] = {
    "item-101": {"id": "item-101", "name": "Kubernetes Action Figure", "price": 29.99, "stock": 42},
    "item-102": {"id": "item-102", "name": "Docker Whale Plushie", "price": 19.50, "stock": 15},
    "item-103": {"id": "item-103", "name": "ArgoCD GitOps Octo Hoodie", "price": 49.00, "stock": 8},
    "item-104": {"id": "item-104", "name": "Minikube Local Dev Mug", "price": 14.00, "stock": 60},
}

class Item(BaseModel):
    id: str
    name: str
    price: float
    stock: int

@app.get("/healthz", tags=["Health"])
def health_check():
    """Liveness and readiness probe endpoint."""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": VERSION
    }

@app.get("/api/v1/items", tags=["Inventory"])
def list_items():
    """Retrieve all inventory items."""
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "count": len(ITEMS),
        "items": list(ITEMS.values())
    }

@app.get("/api/v1/items/{item_id}", tags=["Inventory"])
def get_item(item_id: str):
    """Retrieve details and stock for a specific item."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")
    return ITEMS[item_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)
