from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uuid
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import requests

app = FastAPI(title="Map Server with Inventory")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for sessions
sessions: Dict[str, Dict[str, Any]] = {}

# Simple in-memory inventory storage
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

# Map-related models
class Coordinate(BaseModel):
    lat: float
    lng: float

class BoundingBox(BaseModel):
    north: float
    east: float
    south: float
    west: float

class GeoJSONPolygon(BaseModel):
    type: str
    coordinates: List[List[List[float]]]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONPolygon
    properties: Optional[Dict[str, Any]] = None

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class PolygonRequest(BaseModel):
    polygon: Optional[Union[GeoJSONPolygon, GeoJSONFeature, GeoJSONFeatureCollection]] = None
    url: Optional[str] = None
    id: Optional[str] = Field(None, description="Optional ID for the polygon")

class ZoomToCoordinateRequest(BaseModel):
    session_id: str
    coordinate: Coordinate
    zoom_level: Optional[int] = 13

class ZoomToGeoJSONRequest(BaseModel):
    session_id: str
    geojson: Union[GeoJSONPolygon, GeoJSONFeature, GeoJSONFeatureCollection]

class ZoomToBoundingBoxRequest(BaseModel):
    session_id: str
    bounding_box: BoundingBox

class PlotPolygonRequest(BaseModel):
    session_id: str
    polygon_data: PolygonRequest

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

# Basic Routes
@app.get("/")
def root():
    return {"message": "Map Server API with Inventory Management"}

@app.get("/health")
def health():
    return {"status": "ok", "features": ["inventory_management", "session_management"]}

# Session Management
@app.post("/session")
def create_session(map_type: MapType = MapType.LEAFLET):
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
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# Inventory Management Routes
@app.get("/session/{session_id}/items")
def get_items(session_id: str):
    """Get all items in a session's inventory"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items:
        inventory_items[session_id] = {}
    
    items = list(inventory_items[session_id].values())
    return {"items": items}

@app.post("/session/{session_id}/items")
def add_item(session_id: str, request: AddItemRequest):
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
    
    # Create event for the map
    event_data = {
        "action": "add",
        "item_id": item["id"],
        "item_type": item["type"],
        "item_name": item["name"],
        "item": item
    }
    create_event(session_id, "inventory_update", event_data)
    
    return {"item": item}

@app.get("/session/{session_id}/items/{item_id}")
def get_item(session_id: str, item_id: str):
    """Get a specific item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = inventory_items[session_id][item_id]
    return {"item": item}

@app.put("/session/{session_id}/items/{item_id}")
def update_item(session_id: str, item_id: str, request: UpdateItemRequest):
    """Update an existing item"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = inventory_items[session_id][item_id]
    
    # Track what fields were updated
    updated_fields = []
    
    # Update fields that were provided
    if request.name is not None:
        item["name"] = request.name
        updated_fields.append("name")
    if request.description is not None:
        item["description"] = request.description
        updated_fields.append("description")
    if request.data is not None:
        item["data"] = request.data
        updated_fields.append("data")
    if request.metadata is not None:
        item["metadata"] = request.metadata
        updated_fields.append("metadata")
    if request.visible is not None:
        item["visible"] = request.visible
        updated_fields.append("visible")
    
    # Update timestamp
    from datetime import datetime
    item["updated_at"] = datetime.utcnow().isoformat()
    
    # Create event for the map
    event_data = {
        "action": "update",
        "item_id": item["id"],
        "item_type": item["type"],
        "item_name": item["name"],
        "updated_fields": updated_fields,
        "item": item
    }
    create_event(session_id, "inventory_update", event_data)
    
    return {"item": item}

@app.delete("/session/{session_id}/items/{item_id}")
def delete_item(session_id: str, item_id: str):
    """Delete an item by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_id not in inventory_items or item_id not in inventory_items[session_id]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get item info before deleting for the event
    item = inventory_items[session_id][item_id]
    item_name = item["name"]
    item_type = item["type"]
    
    # Delete the item
    del inventory_items[session_id][item_id]
    
    # Create event for the map
    event_data = {
        "action": "delete",
        "item_id": item_id,
        "item_type": item_type,
        "item_name": item_name
    }
    create_event(session_id, "inventory_update", event_data)
    
    return {"message": "Item deleted successfully"}

# Helper functions for map operations
def create_event(session_id: str, event_type: str, data: Any):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "events" not in sessions[session_id]:
        sessions[session_id]["events"] = []
    
    event = {
        "type": event_type,
        "data": data
    }
    
    sessions[session_id]["events"].append(event)
    return event

def calculate_bounding_box_from_geojson(geojson):
    """Calculate a bounding box from GeoJSON data"""
    coordinates = []
    
    if isinstance(geojson, dict):
        if geojson.get("type") == "FeatureCollection":
            for feature in geojson.get("features", []):
                if feature.get("geometry", {}).get("type") == "Polygon":
                    coordinates.extend(feature["geometry"]["coordinates"][0])
        elif geojson.get("type") == "Feature":
            if geojson.get("geometry", {}).get("type") == "Polygon":
                coordinates.extend(geojson["geometry"]["coordinates"][0])
        elif geojson.get("type") == "Polygon":
            coordinates.extend(geojson["coordinates"][0])
    
    if not coordinates:
        raise HTTPException(status_code=400, detail="Invalid GeoJSON format or no polygon found")
    
    lngs = [coord[0] for coord in coordinates]
    lats = [coord[1] for coord in coordinates]
    
    return {
        "north": max(lats),
        "south": min(lats),
        "east": max(lngs),
        "west": min(lngs)
    }

# Map Routes
@app.get("/map/{session_id}", response_class=HTMLResponse)
def get_map(request: Request, session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get the map type from the session
    map_type = sessions[session_id].get("map_type", MapType.LEAFLET)
    
    # Select the appropriate template based on map type
    template_name = "map.html" if map_type == MapType.LEAFLET else "deckgl_map.html"
    
    # For demo purposes, we'll use a public Mapbox token or empty string
    # In production, you would get this from environment variables
    mapbox_api_key = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"
    
    return templates.TemplateResponse(
        template_name, 
        {
            "request": request, 
            "session_id": session_id,
            "mapbox_api_key": mapbox_api_key
        }
    )

@app.post("/zoom_to_coordinate")
def zoom_to_coordinate(request: ZoomToCoordinateRequest):
    event_data = {
        "lat": request.coordinate.lat,
        "lng": request.coordinate.lng,
        "zoom": request.zoom_level
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/zoom_to_geojson")
def zoom_to_geojson(request: ZoomToGeoJSONRequest):
    bounding_box = calculate_bounding_box_from_geojson(request.geojson.dict())
    
    event_data = {
        "bounding_box": bounding_box
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/zoom_to_bounding_box")
def zoom_to_bounding_box(request: ZoomToBoundingBoxRequest):
    event_data = {
        "bounding_box": request.bounding_box.dict()
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/plot_polygon")
def plot_polygon(request: PlotPolygonRequest):
    polygon_data = None
    
    if request.polygon_data.polygon:
        polygon_data = request.polygon_data.polygon
    elif request.polygon_data.url:
        try:
            response = requests.get(request.polygon_data.url)
            response.raise_for_status()
            polygon_data = response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch GeoJSON from URL: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Either polygon or URL must be provided")
    
    polygon_id = request.polygon_data.id or str(uuid.uuid4())
    
    # Maintain backward compatibility with existing polygons storage
    if "polygons" not in sessions[request.session_id]:
        sessions[request.session_id]["polygons"] = []
    
    sessions[request.session_id]["polygons"].append({
        "id": polygon_id,
        "data": polygon_data
    })
    
    event_data = {
        "polygon_id": polygon_id,
        "polygon": polygon_data
    }
    
    event = create_event(request.session_id, "plot_polygon", event_data)
    return event

@app.get("/events/{session_id}")
def get_events(session_id: str, last_event_index: int = 0):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    events = sessions[session_id].get("events", [])
    new_events = events[last_event_index:] if last_event_index < len(events) else []
    
    return {
        "events": new_events,
        "last_event_index": len(events)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
