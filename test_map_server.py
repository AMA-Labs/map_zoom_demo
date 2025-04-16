import requests
import json
import webbrowser
import time
import sys
import argparse
from urllib.parse import urljoin
from enum import Enum

BASE_URL = "http://localhost:8000"

class MapType(str, Enum):
    LEAFLET = "leaflet"
    DECKGL = "deckgl"

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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Map Server with different map types')
    parser.add_argument('--map-type', type=str, choices=['leaflet', 'deckgl'], default='leaflet',
                        help='Map type to use (leaflet or deckgl)')
    args = parser.parse_args()
    
    map_type = MapType.LEAFLET if args.map_type == 'leaflet' else MapType.DECKGL
    
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
    
    print("\nTest completed! The map is open in your browser.")
    print(f"Session ID: {session_id}")
    print(f"Map type: {map_type.value}")
    print("\nUsage examples:")
    print(f"  - View map: {BASE_URL}/map/{session_id}")
    print(f"  - Get session info: {BASE_URL}/session/{session_id}")
    print(f"  - Get events: {BASE_URL}/events/{session_id}")

if __name__ == "__main__":
    main()
