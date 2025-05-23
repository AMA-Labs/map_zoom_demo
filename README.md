# Map Server

A FastAPI-based web server for interactive maps with real-time event handling. This server allows you to create map sessions, display interactive maps (Leaflet or deck.gl), and control map behavior through API endpoints.

## Features

- Create and manage map sessions
- Display interactive maps with two rendering options:
  - Leaflet (traditional 2D maps)
  - deck.gl (WebGL-powered 3D maps)
- Animated zoom transitions with smooth fly-to effects
- Real-time event handling through polling
- Zoom to coordinates, bounding boxes, or GeoJSON polygons
- Plot GeoJSON polygons on the map

## Requirements

- Python 3.8+
- Poetry (for dependency management)

## Installation

1. Clone the repository
2. Install dependencies with Poetry:

```bash
cd map_server
poetry install
```

## Running the Server

```bash
cd map_server
poetry run uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000

## API Endpoints

### Session Management

- `POST /session` - Create a new map session
- `GET /session/{session_id}` - Get session information

### Map Display

- `GET /map/{session_id}` - Display an interactive map for the session

### Map Control

- `POST /zoom_to_coordinate` - Zoom to a specific coordinate
- `POST /zoom_to_geojson` - Zoom to fit a GeoJSON polygon
- `POST /zoom_to_bounding_box` - Zoom to a specific bounding box
- `POST /plot_polygon` - Plot a GeoJSON polygon on the map

### Event Handling

- `GET /events/{session_id}` - Poll for new events in the session

## Example Usage

A test script is included to demonstrate the functionality with both map types:

```bash
# Run with Leaflet (default)
cd map_server
poetry run python test_map_server.py

# Run with deck.gl
poetry run python test_map_server.py --map-type deckgl
```

This will:
1. Create a new map session with the specified map type
2. Open the map in your default web browser
3. Demonstrate various map operations:
   - Zoom to San Francisco
   - Zoom to California (bounding box)
   - Zoom to New York (to demonstrate long-distance animation)
   - Plot a triangle polygon in San Francisco
   - Plot a GeoJSON feature for Los Angeles

## Map Types

### Leaflet
- Traditional 2D map with tile layers
- Lightweight and fast
- Excellent compatibility across browsers
- Smooth animated transitions between locations

### deck.gl
- WebGL-powered 3D visualization
- Enhanced polygon rendering with 3D effects
- Improved visual styling for GeoJSON features
- Advanced animation capabilities
- Better for data visualization use cases

## API Request Examples

### Create a Session

```bash
curl -X POST http://localhost:8000/session
```

### Zoom to Coordinate

```bash
curl -X POST http://localhost:8000/zoom_to_coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "coordinate": {
      "lat": 37.7749,
      "lng": -122.4194
    },
    "zoom_level": 12
  }'
```

### Plot a Polygon

```bash
curl -X POST http://localhost:8000/plot_polygon \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "polygon_data": {
      "polygon": {
        "type": "Polygon",
        "coordinates": [
          [
            [-122.4, 37.7],
            [-122.5, 37.8],
            [-122.3, 37.9],
            [-122.4, 37.7]
          ]
        ]
      }
    }
  }'
```

## Architecture

The server uses an event-based architecture:

1. Clients create a map session
2. The map page polls the server for events
3. API endpoints create events (zoom, plot_polygon, etc.)
4. The map reacts to these events in real-time

All session data is stored in memory for simplicity.
