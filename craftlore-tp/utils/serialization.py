#!/usr/bin/env python3
"""
Serialization utilities for CraftLore Combined TP.
"""

import json
from typing import Dict, Any, Union
from datetime import datetime


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
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_timestamp(timestamp: Union[float, int, str]) -> str:
        """Format timestamp to ISO string."""
        if isinstance(timestamp, str):
            return timestamp
        return datetime.fromtimestamp(timestamp).isoformat()
    
    @staticmethod
    def serialize_enum(enum_value) -> str:
        """Serialize enum value to string."""
        return enum_value.value if hasattr(enum_value, 'value') else str(enum_value)
    
    @staticmethod
    def safe_dict_get(data: Dict, key: str, default=None):
        """Safely get value from dictionary."""
        return data.get(key, default)
