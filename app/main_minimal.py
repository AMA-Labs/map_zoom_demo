from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

# Models
class MapType(str, Enum):
    LEAFLET = "leaflet"
    DECKGL = "deckgl"

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
    uvicorn.run("app.main_minimal:app", host="0.0.0.0", port=8003, reload=True)
