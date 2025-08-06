#!/usr/bin/env python3
"""
Serialization utilities for CraftLore Account TP.
"""

import json
from typing import Dict, Any
from datetime import datetime


class SerializationHelper:
    """Helper class for serializing/deserializing account data."""
    
    @staticmethod
    def to_bytes(data: Dict[str, Any]) -> bytes:
        """Convert dictionary to bytes for blockchain storage."""
        return json.dumps(data, sort_keys=True).encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> Dict[str, Any]:
        """Convert bytes to dictionary from blockchain storage."""
        return json.loads(data.decode('utf-8'))
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format unix timestamp to ISO string."""
        return datetime.fromtimestamp(timestamp).isoformat()
