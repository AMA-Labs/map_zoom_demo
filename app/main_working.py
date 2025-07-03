from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

# Import inventory system
from app.models.inventory import MapItem, ItemType, AddItemRequest, UpdateItemRequest
from app.storage.dictionary import DictionaryStorage
from app.services.inventory import InventoryService

app = FastAPI(title="Map Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for sessions
sessions: Dict[str, Dict[str, Any]] = {}

# Initialize inventory system
inventory_storage = DictionaryStorage()
inventory_service = InventoryService(inventory_storage)

# Models
class MapType(str, Enum):
    LEAFLET = "leaflet"
    DECKGL = "deckgl"

class Coordinate(BaseModel):
    lat: float
    lng: float

# Routes
@app.get("/")
async def root():
    return {"message": "Map Server API"}

@app.post("/session")
async def create_session(map_type: MapType = MapType.LEAFLET):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "map_type": map_type,
        "events": [],
        "polygons": []
    }
    return {"session_id": session_id, "map_type": map_type}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# Inventory Management Routes
@app.get("/session/{session_id}/items")
async def get_items(session_id: str):
    """Get all items in a session's inventory"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    items = await inventory_service.get_items(session_id)
    return {"items": [item.dict() for item in items]}

@app.post("/session/{session_id}/items")
async def add_item(session_id: str, request: AddItemRequest):
    """Add a new item to the inventory"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        item = await inventory_service.add_item(session_id, request)
        return {"item": item.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/session/{session_id}/items/{item_id}")
async def get_item(session_id: str, item_id: str):
    """Get a specific item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    item = await inventory_service.get_item(session_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"item": item.dict()}

@app.put("/session/{session_id}/items/{item_id}")
async def update_item(session_id: str, item_id: str, request: UpdateItemRequest):
    """Update an existing item"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    item = await inventory_service.update_item(session_id, item_id, request)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"item": item.dict()}

@app.delete("/session/{session_id}/items/{item_id}")
async def delete_item(session_id: str, item_id: str):
    """Delete an item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    success = await inventory_service.delete_item(session_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_working:app", host="0.0.0.0", port=8000, reload=True)
