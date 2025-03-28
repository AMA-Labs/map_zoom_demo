from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uuid
import json
from typing import Dict, List, Optional, Union, Any
import requests
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for sessions
sessions: Dict[str, Dict[str, Any]] = {}

# Models
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

# Routes
@app.get("/")
async def root():
    return {"message": "Map Server API"}

@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "events": [],
        "polygons": []
    }
    return {"session_id": session_id}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.get("/map/{session_id}", response_class=HTMLResponse)
async def get_map(request: Request, session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return templates.TemplateResponse(
        "map.html", 
        {"request": request, "session_id": session_id}
    )

@app.post("/zoom_to_coordinate")
async def zoom_to_coordinate(request: ZoomToCoordinateRequest):
    event_data = {
        "lat": request.coordinate.lat,
        "lng": request.coordinate.lng,
        "zoom": request.zoom_level
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/zoom_to_geojson")
async def zoom_to_geojson(request: ZoomToGeoJSONRequest):
    bounding_box = calculate_bounding_box_from_geojson(request.geojson.dict())
    
    event_data = {
        "bounding_box": bounding_box
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/zoom_to_bounding_box")
async def zoom_to_bounding_box(request: ZoomToBoundingBoxRequest):
    event_data = {
        "bounding_box": request.bounding_box.dict()
    }
    
    event = create_event(request.session_id, "zoom", event_data)
    return event

@app.post("/plot_polygon")
async def plot_polygon(request: PlotPolygonRequest):
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
async def get_events(session_id: str, last_event_index: int = 0):
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
