from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

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

# Simple in-memory inventory storage (no async)
inventory_items: Dict[str, Dict[str, Dict[str, Any]]] = {}  # session_id -> item_id -> item

# Models
class MapType(str, Enum):
    LEAFLET = "leaflet"
    DECKGL = "deckgl"

class ItemType(str, Enum):
    POLYGON = "polygon"
    MARKER = "marker"
    PATH = "path"
    GEOTIFF = "geotiff"

class AddItemRequest(BaseModel):
    type: ItemType
    name: str
    description: Optional[str] = None
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    visible: bool = True

class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    visible: Optional[bool] = None

# Helper functions
def create_item_dict(item_type: ItemType, name: str, data: Dict[str, Any], 
                    description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, 
                    visible: bool = True) -> Dict[str, Any]:
    """Create an item dictionary"""
    from datetime import datetime
    return {
        "id": str(uuid.uuid4()),
        "type": item_type,
        "name": name,
        "description": description,
        "data": data,
        "metadata": metadata or {},
        "visible": visible,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }

# Routes
@app.get("/")
async def root():
    return {"message": "Map Server API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/session")
async def create_session(map_type: MapType = MapType.LEAFLET):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "map_type": map_type,
        "events": [],
        "polygons": []
    }
    # Initialize inventory for this session
    inventory_items[session_id] = {}
    return {"session_id": session_id, "map_type": map_type}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# Inventory Management Routes (simplified, no async storage calls)
@app.get("/session/{session_id}/items")
async def get_items(session_id: str):
    """Get all items in a session's inventory"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items:
        inventory_items[session_id] = {}
    
    items = list(inventory_items[session_id].values())
    return {"items": items}

@app.post("/session/{session_id}/items")
async def add_item(session_id: str, request: AddItemRequest):
    """Add a new item to the inventory"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items:
        inventory_items[session_id] = {}
    
    # Create the item
    item = create_item_dict(
        item_type=request.type,
        name=request.name,
        data=request.data,
        description=request.description,
        metadata=request.metadata,
        visible=request.visible
    )
    
    # Store the item
    inventory_items[session_id][item["id"]] = item
    
    return {"item": item}

@app.get("/session/{session_id}/items/{item_id}")
async def get_item(session_id: str, item_id: str):
    """Get a specific item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = inventory_items[session_id][item_id]
    return {"item": item}

@app.put("/session/{session_id}/items/{item_id}")
async def update_item(session_id: str, item_id: str, request: UpdateItemRequest):
    """Update an existing item"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = inventory_items[session_id][item_id]
    
    # Update fields that were provided
    if request.name is not None:
        item["name"] = request.name
    if request.description is not None:
        item["description"] = request.description
    if request.data is not None:
        item["data"] = request.data
    if request.metadata is not None:
        item["metadata"] = request.metadata
    if request.visible is not None:
        item["visible"] = request.visible
    
    # Update timestamp
    from datetime import datetime
    item["updated_at"] = datetime.utcnow().isoformat()
    
    return {"item": item}

@app.delete("/session/{session_id}/items/{item_id}")
async def delete_item(session_id: str, item_id: str):
    """Delete an item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del inventory_items[session_id][item_id]
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_fixed:app", host="0.0.0.0", port=8001, reload=True)
