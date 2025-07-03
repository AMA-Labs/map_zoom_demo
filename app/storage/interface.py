"""
Storage interface for inventory management
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.inventory import MapItem


class StorageInterface(ABC):
    """Abstract interface for inventory storage backends"""
    
    @abstractmethod
    async def get_items(self, session_id: str) -> List[MapItem]:
        """Get all items for a session"""
        pass
    
    @abstractmethod
    async def add_item(self, session_id: str, item: MapItem) -> str:
        """Add an item and return its ID"""
        pass
    
    @abstractmethod
    async def get_item(self, session_id: str, item_id: str) -> Optional[MapItem]:
        """Get a specific item by ID"""
        pass
    
    @abstractmethod
    async def update_item(self, session_id: str, item_id: str, item: MapItem) -> bool:
        """Update an existing item"""
        pass
    
    @abstractmethod
    async def delete_item(self, session_id: str, item_id: str) -> bool:
        """Delete an item by ID"""
        pass
    
    @abstractmethod
    async def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        pass
    
    @abstractmethod
    async def create_session(self, session_id: str) -> None:
        """Create a new session"""
        pass
