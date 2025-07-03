from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uuid
import json
from typing import Dict, List, Optional, Union, Any, Literal
from enum import Enum
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

# Map types
MAP_TYPES = ["leaflet", "deckgl"]

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_simple:app", host="0.0.0.0", port=8002, reload=True)
