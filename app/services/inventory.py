"""
Inventory service layer for business logic
"""

from typing import List, Optional, Dict, Any
from app.models.inventory import MapItem, ItemType, AddItemRequest, UpdateItemRequest
from app.storage.interface import StorageInterface
from datetime import datetime


class InventoryService:
    """Service layer for inventory management"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    async def get_items(self, session_id: str) -> List[MapItem]:
        """Get all items for a session"""
        return await self.storage.get_items(session_id)
    
    async def add_item(self, session_id: str, request: AddItemRequest) -> MapItem:
        """Add a new item to the inventory"""
        # Create the MapItem from the request
        item = MapItem(
            type=request.type,
            name=request.name,
            description=request.description,
            data=request.data,
            metadata=request.metadata,
            visible=request.visible
        )
        
        # Ensure session exists
        if not await self.storage.session_exists(session_id):
            await self.storage.create_session(session_id)
        
        # Add to storage
        item_id = await self.storage.add_item(session_id, item)
        item.id = item_id
        
        return item
    
    async def get_item(self, session_id: str, item_id: str) -> Optional[MapItem]:
        """Get a specific item by ID"""
        return await self.storage.get_item(session_id, item_id)
    
    async def update_item(self, session_id: str, item_id: str, request: UpdateItemRequest) -> Optional[MapItem]:
        """Update an existing item"""
        # Get the existing item
        existing_item = await self.storage.get_item(session_id, item_id)
        if not existing_item:
            return None
        
        # Update fields that were provided
        if request.name is not None:
            existing_item.name = request.name
        if request.description is not None:
            existing_item.description = request.description
        if request.data is not None:
            existing_item.data = request.data
        if request.metadata is not None:
            existing_item.metadata = request.metadata
        if request.visible is not None:
            existing_item.visible = request.visible
        
        # Update timestamp
        existing_item.updated_at = datetime.utcnow()
        
        # Save the updated item
        success = await self.storage.update_item(session_id, item_id, existing_item)
        return existing_item if success else None
    
    async def delete_item(self, session_id: str, item_id: str) -> bool:
        """Delete an item by ID"""
        return await self.storage.delete_item(session_id, item_id)
    
    async def add_polygon_item(self, session_id: str, polygon_data: Dict[str, Any], polygon_id: str = None, name: str = None) -> MapItem:
        """Helper method to add a polygon item (for integration with existing plot_polygon)"""
        # Generate a meaningful name if not provided
        if not name:
            name = f"Polygon {polygon_id or 'Auto-generated'}"
        
        # Create the add request
        request = AddItemRequest(
            type=ItemType.POLYGON,
            name=name,
            data={"geojson": polygon_data},
            metadata={
                "source": "plot_polygon_endpoint",
                "auto_generated": True
            }
        )
        
        # Add the item
        item = await self.add_item(session_id, request)
        
        # If a specific polygon_id was provided, update the item's ID
        if polygon_id:
            item.id = polygon_id
            # Re-save with the specific ID
            await self.storage.delete_item(session_id, item.id)
            item.id = polygon_id
            await self.storage.add_item(session_id, item)
        
        return item
