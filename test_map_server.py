import requests
import json
import webbrowser
import time
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

def create_session():
    """Create a new map session"""
    response = requests.post(f"{BASE_URL}/session")
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
    print("Creating a new map session...")
    session_id = create_session()
    print(f"Session created with ID: {session_id}")
    
    print("Opening map in browser...")
    open_map(session_id)
    
    # Give the browser time to load
    time.sleep(2)
    
    # Example 1: Zoom to San Francisco
    print("Zooming to San Francisco...")
    zoom_to_coordinate(session_id, 37.7749, -122.4194, 12)
    time.sleep(2)
    
    # Example 2: Zoom to a bounding box (roughly California)
    print("Zooming to California...")
    zoom_to_bounding_box(session_id, 42.0, -114.0, 32.5, -124.4)
    time.sleep(2)
    
    # Example 3: Plot a polygon (simple triangle)
    print("Plotting a triangle...")
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
    time.sleep(2)
    
    # Example 4: Plot a GeoJSON feature
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
    print("You can continue to interact with this session using the API.")

if __name__ == "__main__":
    main()
