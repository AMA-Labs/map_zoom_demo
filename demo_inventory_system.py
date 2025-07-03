#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8003"

def demo_inventory_system():
    """Comprehensive demo of the inventory management system"""
    print("🚀 Inventory Management System Demo")
    print("=" * 50)
    
    try:
        # 1. Create a session
        print("\n1. Creating a new session...")
        session_response = requests.post(f"{BASE_URL}/session", params={"map_type": "leaflet"})
        session_data = session_response.json()
        session_id = session_data["session_id"]
        print(f"   ✅ Session created: {session_id}")
        print(f"   📍 Map type: {session_data['map_type']}")
        
        # 2. Add various types of items
        print("\n2. Adding different types of items...")
        
        # Add a marker
        marker_data = {
            "type": "marker",
            "name": "Golden Gate Bridge",
            "description": "Famous suspension bridge in San Francisco",
            "data": {"coordinate": {"lat": 37.8199, "lng": -122.4783}},
            "metadata": {
                "type": "landmark",
                "year_built": 1937,
                "height_feet": 746,
                "visitor_rating": 4.8
            }
        }
        marker_response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=marker_data)
        marker_result = marker_response.json()
        marker_id = marker_result["item"]["id"]
        print(f"   ✅ Marker added: {marker_result['item']['name']} (ID: {marker_id[:8]}...)")
        
        # Add a path
        path_data = {
            "type": "path",
            "name": "Hiking Trail",
            "description": "Scenic trail through Golden Gate Park",
            "data": {
                "coordinates": [
                    [37.7749, -122.4194],
                    [37.7849, -122.4094],
                    [37.7949, -122.3994]
                ]
            },
            "metadata": {
                "difficulty": "easy",
                "length_miles": 2.5,
                "surface": "paved"
            }
        }
        path_response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=path_data)
        path_result = path_response.json()
        path_id = path_result["item"]["id"]
        print(f"   ✅ Path added: {path_result['item']['name']} (ID: {path_id[:8]}...)")
        
        # Add a polygon
        polygon_data = {
            "type": "polygon",
            "name": "Protected Area",
            "description": "National park boundary",
            "data": {
                "coordinates": [
                    [
                        [-122.5, 37.7],
                        [-122.4, 37.7],
                        [-122.4, 37.8],
                        [-122.5, 37.8],
                        [-122.5, 37.7]
                    ]
                ]
            },
            "metadata": {
                "area_type": "national_park",
                "established": 1972,
                "area_sq_miles": 15.2
            }
        }
        polygon_response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=polygon_data)
        polygon_result = polygon_response.json()
        polygon_id = polygon_result["item"]["id"]
        print(f"   ✅ Polygon added: {polygon_result['item']['name']} (ID: {polygon_id[:8]}...)")
        
        # 3. List all items
        print("\n3. Listing all items in inventory...")
        items_response = requests.get(f"{BASE_URL}/session/{session_id}/items")
        items_data = items_response.json()
        items = items_data["items"]
        print(f"   📦 Total items: {len(items)}")
        
        for item in items:
            print(f"   • {item['name']} ({item['type']}) - Created: {item['created_at'][:19]}")
            if item['metadata']:
                print(f"     Metadata: {json.dumps(item['metadata'], indent=6)}")
        
        # 4. Update an item
        print("\n4. Updating marker with additional information...")
        update_data = {
            "description": "Iconic suspension bridge connecting San Francisco to Marin County",
            "metadata": {
                **marker_result['item']['metadata'],
                "updated": True,
                "fun_fact": "Painted in International Orange color",
                "daily_visitors": 10000
            }
        }
        update_response = requests.put(f"{BASE_URL}/session/{session_id}/items/{marker_id}", json=update_data)
        updated_item = update_response.json()
        print(f"   ✅ Updated: {updated_item['item']['name']}")
        print(f"   📝 New description: {updated_item['item']['description']}")
        print(f"   🕒 Updated at: {updated_item['item']['updated_at'][:19]}")
        
        # 5. Get specific item details
        print("\n5. Retrieving detailed information for the path...")
        item_response = requests.get(f"{BASE_URL}/session/{session_id}/items/{path_id}")
        item_data = item_response.json()
        item = item_data["item"]
        print(f"   📍 Item: {item['name']}")
        print(f"   📝 Description: {item['description']}")
        print(f"   🗺️  Coordinates: {len(item['data']['coordinates'])} points")
        print(f"   📊 Metadata:")
        for key, value in item['metadata'].items():
            print(f"      • {key}: {value}")
        
        # 6. Demonstrate search/filter capabilities
        print("\n6. Filtering items by type...")
        all_items = items_data["items"]
        markers = [item for item in all_items if item['type'] == 'marker']
        paths = [item for item in all_items if item['type'] == 'path']
        polygons = [item for item in all_items if item['type'] == 'polygon']
        
        print(f"   🔍 Markers: {len(markers)}")
        print(f"   🔍 Paths: {len(paths)}")
        print(f"   🔍 Polygons: {len(polygons)}")
        
        # 7. Delete an item
        print("\n7. Cleaning up - deleting the path...")
        delete_response = requests.delete(f"{BASE_URL}/session/{session_id}/items/{path_id}")
        delete_result = delete_response.json()
        print(f"   ✅ {delete_result['message']}")
        
        # 8. Final inventory count
        print("\n8. Final inventory status...")
        final_items_response = requests.get(f"{BASE_URL}/session/{session_id}/items")
        final_items = final_items_response.json()["items"]
        print(f"   📦 Remaining items: {len(final_items)}")
        for item in final_items:
            print(f"   • {item['name']} ({item['type']})")
        
        print("\n" + "=" * 50)
        print("🎉 Inventory Management System Demo Complete!")
        print("\n📋 Summary:")
        print(f"   • Session ID: {session_id}")
        print(f"   • Items created: 3 (marker, path, polygon)")
        print(f"   • Items updated: 1")
        print(f"   • Items deleted: 1")
        print(f"   • Final count: {len(final_items)}")
        print("\n🔗 API Endpoints demonstrated:")
        print(f"   • POST   {BASE_URL}/session")
        print(f"   • POST   {BASE_URL}/session/{{session_id}}/items")
        print(f"   • GET    {BASE_URL}/session/{{session_id}}/items")
        print(f"   • GET    {BASE_URL}/session/{{session_id}}/items/{{item_id}}")
        print(f"   • PUT    {BASE_URL}/session/{{session_id}}/items/{{item_id}}")
        print(f"   • DELETE {BASE_URL}/session/{{session_id}}/items/{{item_id}}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_inventory_system()
