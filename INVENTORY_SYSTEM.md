# Map Inventory Management System

## Overview
This document describes the inventory management system added to the map server application. The system allows tracking and managing items added to map sessions with flexible metadata support.

## Architecture

### Core Components

1. **Models** (`app/models/inventory.py`)
   - `ItemType`: Enum for item types (POLYGON, MARKER, PATH, GEOTIFF)
   - `MapItem`: Core item model with flexible data and metadata
   - `AddItemRequest`: Request model for adding items
   - `UpdateItemRequest`: Request model for updating items

2. **Storage Interface** (`app/storage/interface.py`)
   - Abstract interface for storage backends
   - Supports session-based item management
   - Designed for easy extension to Redis, databases, etc.

3. **Dictionary Storage** (`app/storage/dictionary.py`)
   - In-memory implementation using Python dictionaries
   - Suitable for development and small-scale deployments

4. **Inventory Service** (`app/services/inventory.py`)
   - Business logic layer
   - Handles CRUD operations
   - Integration with existing polygon plotting

## API Endpoints

### Inventory Management
- `GET /session/{session_id}/items` - List all items
- `POST /session/{session_id}/items` - Add new item
- `GET /session/{session_id}/items/{item_id}` - Get specific item
- `PUT /session/{session_id}/items/{item_id}` - Update item
- `DELETE /session/{session_id}/items/{item_id}` - Delete item

### Integration
- `POST /plot_polygon` - Enhanced to automatically add polygons to inventory

## Item Types

### Polygon
```json
{
  "type": "polygon",
  "name": "My Polygon",
  "data": {
    "geojson": { ... }
  },
  "metadata": {
    "area_sqkm": 45.2,
    "source": "user_drawn"
  }
}
```

### Marker
```json
{
  "type": "marker",
  "name": "Golden Gate Bridge",
  "data": {
    "coordinate": {"lat": 37.8199, "lng": -122.4783}
  },
  "metadata": {
    "type": "landmark",
    "year_built": 1937
  }
}
```

### Path
```json
{
  "type": "path",
  "name": "Hiking Trail",
  "data": {
    "coordinates": [[37.7749, -122.4194], [37.7849, -122.4094]]
  },
  "metadata": {
    "difficulty": "easy",
    "length_miles": 2.5
  }
}
```

## Features

### Flexible Metadata
- Open-ended JSON metadata support
- No schema restrictions
- Suitable for any use case

### Storage Abstraction
- Interface-based design
- Easy to swap storage backends
- Future-ready for Redis, PostgreSQL, etc.

### Backward Compatibility
- Existing polygon plotting continues to work
- Automatic inventory integration
- No breaking changes

### Session Isolation
- Each session has its own inventory
- No cross-session data leakage
- Clean separation of concerns

## Testing

The `test_map_server.py` script includes comprehensive inventory testing:
- Adding markers and paths
- Listing inventory items
- Updating item metadata
- Deleting items
- Integration with polygon plotting

## Future Extensions

### Planned Item Types
- **GeoTIFF**: Raster data support
- **Custom**: User-defined item types

### Storage Backends
- Redis for distributed deployments
- PostgreSQL for persistent storage
- S3 for large file storage

### Advanced Features
- Item search and filtering
- Bulk operations
- Item relationships
- Version history

## Usage Example

```python
# Add a marker
marker_data = {
    "type": "marker",
    "name": "Coffee Shop",
    "data": {"coordinate": {"lat": 37.7749, "lng": -122.4194}},
    "metadata": {"rating": 4.5, "price": "$$"}
}
response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=marker_data)

# List all items
items = requests.get(f"{BASE_URL}/session/{session_id}/items").json()

# Delete an item
requests.delete(f"{BASE_URL}/session/{session_id}/items/{item_id}")
