#!/usr/bin/env python3
"""
Address generator for CraftLore Asset TP.
"""

import hashlib
from typing import Dict, List


class AssetAddressGenerator:
    """Generates addresses for assets in the CraftLore system."""
    
    FAMILY_NAME = 'craftlore-asset' 
    FAMILY_NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]
    
    # Asset type prefixes (2 characters each)
    ASSET_TYPE_PREFIXES = {
        'raw_material': '01',
        'product': '02',
        'product_batch': '03',
        'work_order': '04',
        'warranty': '05'
    }
    
    # Index prefixes
    OWNER_INDEX_PREFIX = 'ff'
    TYPE_INDEX_PREFIX = 'fe'
    BATCH_INDEX_PREFIX = 'fd'
    
    def generate_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Generate address for an asset."""
        type_prefix = self.ASSET_TYPE_PREFIXES.get(asset_type, '00')
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + type_prefix + asset_hash[:62]
    
    def generate_product_address_from_batch(self, batch_address: str, batch_index: int) -> str:
        """Generate product address from batch address and index."""
        # Use batch address as base and append index hash
        index_hash = hashlib.sha512(str(batch_index).encode()).hexdigest()[:8]
        return batch_address[:62] + index_hash
    
    def generate_owner_index_address(self, owner_public_key: str) -> str:
        """Generate address for owner index (to query assets by owner)."""
        owner_hash = hashlib.sha512(owner_public_key.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + self.OWNER_INDEX_PREFIX + owner_hash[:62]

    def generate_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        type_hash = hashlib.sha512(asset_type.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + self.TYPE_INDEX_PREFIX + type_hash[:62]
    
    def generate_batch_index_address(self, batch_id: str) -> str:
        """Generate address for batch index (to query products by batch)."""
        batch_hash = hashlib.sha512(batch_id.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + self.BATCH_INDEX_PREFIX + batch_hash[:62]
    
    def get_namespace(self) -> str:
        """Get the family namespace."""
        return self.FAMILY_NAMESPACE
