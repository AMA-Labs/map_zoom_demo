import requests
import json
import webbrowser
import time
import sys
import argparse
from urllib.parse import urljoin
from enum import Enum

BASE_URL = "http://127.0.0.1:8003"

class MapType(str, Enum):
    LEAFLET = "leaflet"
    DECKGL = "deckgl"
    OPENLAYERS = "openlayers"

class ItemType(str, Enum):
    POLYGON = "polygon"
    MARKER = "marker"
    PATH = "path"
    GEOTIFF = "geotiff"

def create_session(map_type=MapType.LEAFLET):
    """Create a new map session with specified map type"""
    response = requests.post(f"{BASE_URL}/session", params={"map_type": map_type})
    return response.json()["session_id"]

def open_map(session_id):
    """Open the map in a web browser"""
    map_url = f"{BASE_URL}/map/{session_id}"
    webbrowser.open(map_url)

def zoom_to_coordinate(session_id, lat, lng, zoom=13):
    """Zoom to a specific coordinate"""
    data = {
        "session_id": session_id,
        "coordinate": {
            "lat": lat,
            "lng": lng
        },
        "zoom_level": zoom
    }
    response = requests.post(f"{BASE_URL}/zoom_to_coordinate", json=data)
    return response.json()

def zoom_to_bounding_box(session_id, north, east, south, west):
    """Zoom to a bounding box"""
    data = {
        "session_id": session_id,
        "bounding_box": {
            "north": north,
            "east": east,
            "south": south,
            "west": west
        }
    }
    response = requests.post(f"{BASE_URL}/zoom_to_bounding_box", json=data)
    return response.json()

def plot_polygon(session_id, polygon_data):
    """Plot a GeoJSON polygon"""
    data = {
        "session_id": session_id,
        "polygon_data": polygon_data
    }
    response = requests.post(f"{BASE_URL}/plot_polygon", json=data)
    return response.json()

# Inventory Management Functions
def add_item(session_id, item_type, name, data, description=None, metadata=None, visible=True):
    """Add a new item to the inventory"""
    item_data = {
        "type": item_type,
        "name": name,
        "data": data,
        "description": description,
        "metadata": metadata or {},
        "visible": visible
    }
    response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=item_data)
    return response.json()

def get_items(session_id):
    """Get all items in a session's inventory"""
    response = requests.get(f"{BASE_URL}/session/{session_id}/items")
    return response.json()

def get_item(session_id, item_id):
    """Get a specific item by ID"""
    response = requests.get(f"{BASE_URL}/session/{session_id}/items/{item_id}")
    return response.json()

def update_item(session_id, item_id, **updates):
    """Update an existing item"""
    response = requests.put(f"{BASE_URL}/session/{session_id}/items/{item_id}", json=updates)
    return response.json()

def delete_item(session_id, item_id):
    """Delete an item by ID"""
    response = requests.delete(f"{BASE_URL}/session/{session_id}/items/{item_id}")
    return response.json()

def add_marker(session_id, name, lat, lng, description=None, metadata=None):
    """Add a marker to inventory"""
    data = {
        "coordinate": {"lat": lat, "lng": lng}
    }
    return add_item(session_id, ItemType.MARKER, name, data, description, metadata)

def add_path(session_id, name, coordinates, description=None, metadata=None):
    """Add a path to inventory"""
    data = {
        "coordinates": coordinates
    }
    return add_item(session_id, ItemType.PATH, name, data, description, metadata)

def test_inventory_system(session_id):
    """Comprehensive demonstration of inventory management features"""
    print("\n" + "="*60)
    print("🎯 INVENTORY MANAGEMENT SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Phase 1: Add multiple diverse items
    print("\n📦 PHASE 1: Adding diverse items to inventory...")
    
    # Add landmarks
    print("🏛️  Adding famous landmarks...")
    golden_gate = add_marker(
        session_id, "Golden Gate Bridge", 37.8199, -122.4783,
        description="Iconic suspension bridge in San Francisco",
        metadata={"type": "landmark", "year_built": 1937, "height_feet": 746, "visitors_per_year": 15000000}
    )
    
    statue_liberty = add_marker(
        session_id, "Statue of Liberty", 40.6892, -74.0445,
        description="Symbol of freedom and democracy",
        metadata={"type": "monument", "year_built": 1886, "height_feet": 305, "unesco_site": True}
    )
    
    # Add hiking trails
    print("🥾 Adding hiking trails...")
    sf_trail = add_path(
        session_id, "Bay Area Ridge Trail", 
        [[37.7749, -122.4194], [37.7849, -122.4094], [37.7949, -122.3994], [37.8049, -122.3894]],
        description="Scenic ridge trail with bay views",
        metadata={"difficulty": "moderate", "length_miles": 12.5, "elevation_gain": 2400, "surface": "dirt"}
    )
    
    ny_trail = add_path(
        session_id, "Central Park Loop",
        [[40.7829, -73.9654], [40.7689, -73.9441], [40.7648, -73.9731], [40.7829, -73.9654]],
        description="Popular running and walking loop in Central Park",
        metadata={"difficulty": "easy", "length_miles": 6.1, "surface": "paved", "lighting": True}
    )
    
    # Add protected areas
    print("🌲 Adding protected areas...")
    yosemite = add_item(
        session_id, ItemType.POLYGON, "Yosemite National Park",
        data={"coordinates": [[[-119.8, 37.5], [-119.2, 37.5], [-119.2, 38.2], [-119.8, 38.2], [-119.8, 37.5]]]},
        description="Famous national park with granite cliffs and waterfalls",
        metadata={"area_sq_miles": 1168, "established": 1890, "annual_visitors": 4000000, "unesco_site": True}
    )
    
    # Phase 2: Display current inventory
    print(f"\n📋 PHASE 2: Current inventory status...")
    items_result = get_items(session_id)
    items = items_result["items"]
    print(f"   📊 Total items: {len(items)}")
    
    # Group by type
    by_type = {}
    for item in items:
        item_type = item['type']
        if item_type not in by_type:
            by_type[item_type] = []
        by_type[item_type].append(item)
    
    for item_type, type_items in by_type.items():
        print(f"   🔹 {item_type.upper()}: {len(type_items)} items")
        for item in type_items:
            print(f"      • {item['name']} (ID: {item['id'][:8]}...)")
    
    # Phase 3: Detailed item inspection
    print(f"\n🔍 PHASE 3: Detailed item inspection...")
    golden_gate_details = get_item(session_id, golden_gate["item"]["id"])
    item = golden_gate_details["item"]
    print(f"   📍 Inspecting: {item['name']}")
    print(f"   📝 Description: {item['description']}")
    print(f"   📊 Metadata:")
    for key, value in item['metadata'].items():
        print(f"      • {key}: {value}")
    print(f"   🕒 Created: {item['created_at']}")
    
    # Phase 4: Dynamic updates
    print(f"\n✏️  PHASE 4: Dynamic updates...")
    print("   🔄 Updating Golden Gate Bridge with visitor data...")
    update_result = update_item(
        session_id, golden_gate["item"]["id"],
        metadata={
            **item['metadata'],
            "last_inspection": "2025-06-26",
            "condition": "excellent",
            "maintenance_cost_annual": 25000000,
            "updated_by_system": True
        }
    )
    print(f"   ✅ Updated: {update_result['item']['name']}")
    
    # Phase 5: Selective deletion
    print(f"\n🗑️  PHASE 5: Selective cleanup...")
    print("   ❌ Removing Central Park Loop (temporary trail)...")
    delete_result = delete_item(session_id, ny_trail["item"]["id"])
    print(f"   ✅ {delete_result['message']}")
    
    # Add a replacement
    print("   ➕ Adding replacement trail...")
    brooklyn_bridge = add_path(
        session_id, "Brooklyn Bridge Walk",
        [[40.7061, -73.9969], [40.7033, -73.9987], [40.6955, -73.9963]],
        description="Historic bridge walk with skyline views",
        metadata={"difficulty": "easy", "length_miles": 1.1, "historic": True, "year_built": 1883}
    )
    print(f"   ✅ Added: {brooklyn_bridge['item']['name']}")
    
    # Phase 6: Final inventory report
    print(f"\n📈 PHASE 6: Final inventory report...")
    final_items = get_items(session_id)
    final_count = len(final_items["items"])
    print(f"   📊 Final inventory count: {final_count} items")
    
    # Summary by type
    final_by_type = {}
    for item in final_items["items"]:
        item_type = item['type']
        final_by_type[item_type] = final_by_type.get(item_type, 0) + 1
    
    print("   📋 Final breakdown:")
    for item_type, count in final_by_type.items():
        print(f"      🔹 {item_type.upper()}: {count}")
    
    print("\n" + "="*60)
    print("🎉 INVENTORY DEMONSTRATION COMPLETE!")
    print("="*60)
    
    return final_items["items"]

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Map Server with different map types')
    parser.add_argument('--map-type', type=str, choices=['leaflet', 'deckgl', 'openlayers'], default='deckgl',
                        help='Map type to use (leaflet, deckgl, or openlayers)')
    args = parser.parse_args()
    
    if args.map_type == 'leaflet':
        map_type = MapType.LEAFLET
    elif args.map_type == 'deckgl':
        map_type = MapType.DECKGL
    else:
        map_type = MapType.OPENLAYERS
    
    print(f"Creating a new map session with {map_type.value} map...")
    session_id = create_session(map_type)
    print(f"Session created with ID: {session_id}")
    
    print("Opening map in browser...")
    open_map(session_id)
    
    # Give the browser time to load
    time.sleep(3)
    
    # Example 1: Zoom to San Francisco
    print("Zooming to San Francisco...")
    zoom_to_coordinate(session_id, 37.7749, -122.4194, 12)
    time.sleep(4)  # Allow time for the animation to complete
    
    # Example 2: Zoom to a bounding box (roughly California)
    print("Zooming to California...")
    zoom_to_bounding_box(session_id, 42.0, -114.0, 32.5, -124.4)
    time.sleep(4)  # Allow time for the animation to complete
    
    # Example 3: Zoom to New York (to demonstrate long-distance animation)
    print("Zooming to New York...")
    zoom_to_coordinate(session_id, 40.7128, -74.0060, 12)
    time.sleep(4)  # Allow time for the animation to complete
    
    # Example 4: Plot a polygon (simple triangle in San Francisco area)
    print("Plotting a triangle in San Francisco area...")
    triangle = {
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-122.4, 37.7],
                    [-122.5, 37.8],
                    [-122.3, 37.9],
                    [-122.4, 37.7]  # Close the polygon
                ]
            ]
        }
    }
    plot_polygon(session_id, triangle)
    time.sleep(4)  # Allow time for the animation to complete
    
    # Example 5: Plot a GeoJSON feature with properties
    print("Plotting a GeoJSON feature...")
    feature = {
        "polygon": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-118.4, 34.0],
                        [-118.5, 34.1],
                        [-118.3, 34.2],
                        [-118.2, 34.1],
                        [-118.4, 34.0]  # Close the polygon
                    ]
                ]
            },
            "properties": {
                "name": "Los Angeles Area"
            }
        }
    }
    plot_polygon(session_id, feature)
    time.sleep(2)  # Allow time for the polygon to render
    
    # Example 6: Test the inventory management system
    print("\nTesting inventory management system...")
    remaining_items = test_inventory_system(session_id)
    
    print("\nTest completed! The map is open in your browser.")
    print(f"Session ID: {session_id}")
    print(f"Map type: {map_type.value}")
    print(f"Final inventory count: {len(remaining_items)} items")
    print("\nAPI Usage examples:")
    print(f"  - View map: {BASE_URL}/map/{session_id}")
    print(f"  - Get session info: {BASE_URL}/session/{session_id}")
    print(f"  - Get events: {BASE_URL}/events/{session_id}")
    print(f"  - Get inventory items: {BASE_URL}/session/{session_id}/items")
    print("\nInventory Management endpoints:")
    print(f"  - GET    {BASE_URL}/session/{{session_id}}/items")
    print(f"  - POST   {BASE_URL}/session/{{session_id}}/items")
    print(f"  - GET    {BASE_URL}/session/{{session_id}}/items/{{item_id}}")
    print(f"  - PUT    {BASE_URL}/session/{{session_id}}/items/{{item_id}}")
    print(f"  - DELETE {BASE_URL}/session/{{session_id}}/items/{{item_id}}")

if __name__ == "__main__":
    main()
