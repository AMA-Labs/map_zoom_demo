"""
Inventory models for map items
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class ItemType(str, Enum):
    POLYGON = "polygon"
    MARKER = "marker"
    PATH = "path"
    GEOTIFF = "geotiff"


class MapItem(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ItemType
    name: str
    description: Optional[str] = None
    data: Dict[str, Any]  # Flexible data storage (GeoJSON, coordinates, etc.)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Open-ended metadata
    visible: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def dict(self, **kwargs):
        """Override dict to handle datetime serialization"""
        result = super().dict(**kwargs)
        if 'created_at' in result and isinstance(result['created_at'], datetime):
            result['created_at'] = result['created_at'].isoformat()
        if 'updated_at' in result and isinstance(result['updated_at'], datetime):
            result['updated_at'] = result['updated_at'].isoformat()
        return result


class AddItemRequest(BaseModel):
    type: ItemType
    name: str
    description: Optional[str] = None
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    visible: bool = True


class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    visible: Optional[bool] = None
