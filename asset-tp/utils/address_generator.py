#!/usr/bin/env python3
"""
Asset generator for CraftLore Account TP.
"""

import hashlib


class AssetAddressGenerator:
    """Generates blockchain addresses for asset-related data."""
    
    FAMILY_NAME = 'craftlore-asset' 
    FAMILY_NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]
    
    # Address prefixes (2 characters each)
    ASSET_PREFIX = '00'
    TYPE_INDEX_PREFIX = '02'

    def generate_asset_address(self, public_key: str) -> str:
        """Generate address for asset data."""
        return self._generate_address(self.ASSET_PREFIX, public_key)

    def generate_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        return self._generate_address(self.TYPE_INDEX_PREFIX, asset_type)

    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate a blockchain address."""
        identifier_hash = hashlib.sha512(identifier.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + prefix + identifier_hash[:62]
    
    def get_namespace(self) -> str:
        """Get the family namespace."""
        return self.FAMILY_NAMESPACE
