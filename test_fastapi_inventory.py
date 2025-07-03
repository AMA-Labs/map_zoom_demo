#!/usr/bin/env python3

print("Testing FastAPI with inventory system...")

try:
    print("1. Testing FastAPI imports...")
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    print("   ✅ FastAPI imports OK")
    
    print("2. Testing inventory imports...")
    from app.models.inventory import MapItem, ItemType, AddItemRequest
    from app.storage.dictionary import DictionaryStorage
    from app.services.inventory import InventoryService
    print("   ✅ Inventory imports OK")
    
    print("3. Creating FastAPI app...")
    app = FastAPI(title="Test Server")
    print("   ✅ FastAPI app created")
    
    print("4. Initializing inventory system...")
    storage = DictionaryStorage()
    service = InventoryService(storage)
    print("   ✅ Inventory system initialized")
    
    print("5. Testing async operations...")
    import asyncio
    
    async def test_async():
        # Test session creation
        await service.storage.create_session("test-session")
        print("   ✅ Session created")
        
        # Test adding an item
        request = AddItemRequest(
            type=ItemType.MARKER,
            name="Test Marker",
            data={"coordinate": {"lat": 37.7749, "lng": -122.4194}},
            metadata={"test": True}
        )
        item = await service.add_item("test-session", request)
        print(f"   ✅ Item added with ID: {item.id}")
        
        # Test getting items
        items = await service.get_items("test-session")
        print(f"   ✅ Retrieved {len(items)} items")
        
        return True
    
    # Run the async test
    result = asyncio.run(test_async())
    print("   ✅ Async operations completed")
    
    print("\n🎉 FastAPI + Inventory system test passed!")
    
except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
