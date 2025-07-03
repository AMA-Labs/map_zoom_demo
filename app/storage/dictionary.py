"""
Dictionary-based storage implementation for inventory management
"""

from typing import Dict, List, Optional
from app.storage.interface import StorageInterface
from app.models.inventory import MapItem
from datetime import datetime


class DictionaryStorage(StorageInterface):
    """In-memory dictionary storage for inventory items"""
    
    def __init__(self):
        # Structure: {session_id: {item_id: MapItem}}
        self.items: Dict[str, Dict[str, MapItem]] = {}
    
    async def get_items(self, session_id: str) -> List[MapItem]:
        """Get all items for a session"""
        if session_id not in self.items:
            return []
        return list(self.items[session_id].values())
    
    async def add_item(self, session_id: str, item: MapItem) -> str:
        """Add an item and return its ID"""
        if session_id not in self.items:
            self.items[session_id] = {}
        
        # Ensure the item has an ID
        if not item.id:
            import uuid
            item.id = str(uuid.uuid4())
        
        self.items[session_id][item.id] = item
        return item.id
    
    async def get_item(self, session_id: str, item_id: str) -> Optional[MapItem]:
        """Get a specific item by ID"""
        if session_id not in self.items:
            return None
        return self.items[session_id].get(item_id)
    
    async def update_item(self, session_id: str, item_id: str, item: MapItem) -> bool:
        """Update an existing item"""
        if session_id not in self.items or item_id not in self.items[session_id]:
            return False
        
        # Update the timestamp
        item.updated_at = datetime.utcnow()
        self.items[session_id][item_id] = item
        return True
    
    async def delete_item(self, session_id: str, item_id: str) -> bool:
        """Delete an item by ID"""
        if session_id not in self.items or item_id not in self.items[session_id]:
            return False
        
        del self.items[session_id][item_id]
        return True
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        return session_id in self.items
    
    async def create_session(self, session_id: str) -> None:
        """Create a new session"""
        if session_id not in self.items:
            self.items[session_id] = {}
