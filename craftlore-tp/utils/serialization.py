#!/usr/bin/env python3
"""
Serialization utilities for CraftLore Combined TP.
"""

import json
from typing import Dict, Any, Union
from datetime import datetime, timezone
from uuid import uuid4


class SerializationHelper:
    """Helper class for serializing/deserializing data."""
    
    @staticmethod
    def to_bytes(data: Union[Dict[str, Any], list]) -> bytes:
        """Convert dictionary or list to bytes for blockchain storage."""
        return json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> Union[Dict[str, Any], list]:
        """Convert bytes to dictionary or list from blockchain storage."""
        return json.loads(data.decode('utf-8'))
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current UTC timestamp as ISO string."""
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def create_asset_id() -> str:
        """Create a unique identifier for an asset using UUID4."""
        return str(uuid4())