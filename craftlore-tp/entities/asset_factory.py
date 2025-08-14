#!/usr/bin/env python3
"""
Asset Factory for creating asset instances from data.
"""

from typing import Dict, Optional, Union
from .assets import BaseAsset, Product, ProductBatch, RawMaterial, WorkOrder, Warranty
from core.enums import AssetType


class AssetFactory:
    """Factory for creating asset instances from dictionaries."""
    
    ASSET_CLASSES = {
        AssetType.RAW_MATERIAL.value: RawMaterial,
        AssetType.PRODUCT.value: Product,
        AssetType.PRODUCT_BATCH.value: ProductBatch,
        AssetType.WORK_ORDER.value: WorkOrder,
        AssetType.WARRANTY.value: Warranty,
        # String aliases
        'raw_material': RawMaterial,
        'product': Product,
        'product_batch': ProductBatch,
        'work_order': WorkOrder,
        'warranty': Warranty,
    }
    
    @classmethod
    def create_asset(cls, asset_data: Dict) -> BaseAsset:
        """
        Create an asset instance from dictionary data.
        
        Args:
            asset_data: Dictionary containing asset data including asset_type
            
        Returns:
            Asset instance of the appropriate type
            
        Raises:
            ValueError: If asset_type is unknown or data is invalid
        """
        if not isinstance(asset_data, dict):
            raise ValueError("Asset data must be a dictionary")
        
        asset_type = asset_data.get('asset_type')
        if not asset_type:
            raise ValueError("Asset data must contain 'asset_type' field")
        
        asset_class = cls.ASSET_CLASSES.get(asset_type)
        if not asset_class:
            raise ValueError(f"Unknown asset type: {asset_type}")
        
        # Create asset instance
        try:
            # Extract basic fields
            asset_id = asset_data.get('asset_id', '')
            public_key = asset_data.get('public_key', asset_data.get('owner', ''))
            timestamp = asset_data.get('timestamp', asset_data.get('created_at', ''))
            
            # Create instance
            asset = asset_class(
                asset_id=asset_id,
                public_key=public_key,
                timestamp=timestamp
            )
            
            # Set all other fields from data
            for key, value in asset_data.items():
                if hasattr(asset, key):
                    setattr(asset, key, value)
            
            return asset
            
        except Exception as e:
            raise ValueError(f"Failed to create asset instance: {str(e)}")
    
    @classmethod
    def get_asset_class(cls, asset_type: str) -> Optional[type]:
        """Get the asset class for a given type."""
        return cls.ASSET_CLASSES.get(asset_type)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Get list of supported asset types."""
        return list(cls.ASSET_CLASSES.keys())
