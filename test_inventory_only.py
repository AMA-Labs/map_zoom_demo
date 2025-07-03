#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8003"

def test_inventory_endpoints():
    """Test inventory endpoints directly"""
    print("Testing inventory management endpoints...")
    
    try:
        # Test 1: Create a session
        print("1. Creating session...")
        session_response = requests.post(f"{BASE_URL}/session", timeout=5)
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["session_id"]
            print(f"   ✅ Session created: {session_id}")
        else:
            print(f"   ❌ Session creation failed: {session_response.status_code}")
            return
        
        # Test 2: Add a marker
        print("2. Adding marker...")
        marker_data = {
            "type": "marker",
            "name": "Test Marker",
            "data": {"coordinate": {"lat": 37.7749, "lng": -122.4194}},
            "metadata": {"test": True}
        }
        marker_response = requests.post(f"{BASE_URL}/session/{session_id}/items", json=marker_data, timeout=5)
        if marker_response.status_code == 200:
            marker_result = marker_response.json()
            marker_id = marker_result["item"]["id"]
            print(f"   ✅ Marker added: {marker_id}")
        else:
            print(f"   ❌ Marker creation failed: {marker_response.status_code}")
            return
        
        # Test 3: List items
        print("3. Listing items...")
        items_response = requests.get(f"{BASE_URL}/session/{session_id}/items", timeout=5)
        if items_response.status_code == 200:
            items_data = items_response.json()
            print(f"   ✅ Found {len(items_data['items'])} items")
        else:
            print(f"   ❌ List items failed: {items_response.status_code}")
            return
        
        # Test 4: Get specific item
        print("4. Getting specific item...")
        item_response = requests.get(f"{BASE_URL}/session/{session_id}/items/{marker_id}", timeout=5)
        if item_response.status_code == 200:
            item_data = item_response.json()
            print(f"   ✅ Retrieved item: {item_data['item']['name']}")
        else:
            print(f"   ❌ Get item failed: {item_response.status_code}")
            return
        
        # Test 5: Update item
        print("5. Updating item...")
        update_data = {"description": "Updated test marker"}
        update_response = requests.put(f"{BASE_URL}/session/{session_id}/items/{marker_id}", json=update_data, timeout=5)
        if update_response.status_code == 200:
            update_result = update_response.json()
            print(f"   ✅ Item updated: {update_result['item']['description']}")
        else:
            print(f"   ❌ Update item failed: {update_response.status_code}")
            return
        
        # Test 6: Delete item
        print("6. Deleting item...")
        delete_response = requests.delete(f"{BASE_URL}/session/{session_id}/items/{marker_id}", timeout=5)
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            print(f"   ✅ Item deleted: {delete_result['message']}")
        else:
            print(f"   ❌ Delete item failed: {delete_response.status_code}")
            return
        
        print("\n🎉 All inventory tests passed!")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server may be hanging")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_inventory_endpoints()
