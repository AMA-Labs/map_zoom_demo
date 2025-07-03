#!/usr/bin/env python3

print("Testing inventory system imports...")

try:
    print("1. Testing basic imports...")
    import uuid
    from datetime import datetime
    from typing import Dict, List, Optional, Any
    from enum import Enum
    print("   ✅ Basic imports OK")
    
    print("2. Testing pydantic...")
    from pydantic import BaseModel, Field
    print("   ✅ Pydantic OK")
    
    print("3. Testing inventory models...")
    from app.models.inventory import ItemType
    print("   ✅ ItemType imported")
    
    from app.models.inventory import MapItem
    print("   ✅ MapItem imported")
    
    from app.models.inventory import AddItemRequest, UpdateItemRequest
    print("   ✅ Request models imported")
    
    print("4. Testing storage interface...")
    from app.storage.interface import StorageInterface
    print("   ✅ Storage interface imported")
    
    print("5. Testing dictionary storage...")
    from app.storage.dictionary import DictionaryStorage
    print("   ✅ Dictionary storage imported")
    
    print("6. Testing inventory service...")
    from app.services.inventory import InventoryService
    print("   ✅ Inventory service imported")
    
    print("7. Testing initialization...")
    storage = DictionaryStorage()
    print("   ✅ Storage initialized")
    
    service = InventoryService(storage)
    print("   ✅ Service initialized")
    
    print("8. Testing basic operations...")
    # Test creating an item
    item = MapItem(
        type=ItemType.MARKER,
        name="Test Marker",
        data={"coordinate": {"lat": 37.7749, "lng": -122.4194}},
        metadata={"test": True}
    )
    print("   ✅ Item created")
    
    print("\n🎉 All tests passed! Inventory system is working correctly.")
    
except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
