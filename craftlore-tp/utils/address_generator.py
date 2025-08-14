#!/usr/bin/env python3
"""
Unified address generator for CraftLore Combined TP.
Handles both account and asset addresses in a single namespace.
"""

import hashlib
from typing import Dict, List


class CraftLoreAddressGenerator:
    """Generates blockchain addresses for the unified CraftLore system."""
    
    FAMILY_NAME = 'craftlore'
    FAMILY_NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]
    
    # Account prefixes (starting with 0)
    ACCOUNT_PREFIX = '00'
    EMAIL_INDEX_PREFIX = '01'
    ACCOUNT_TYPE_INDEX_PREFIX = '02'
    BOOTSTRAP_PREFIX = '03'
    
    # Asset prefixes (starting with 1)
    RAW_MATERIAL_PREFIX = '10'
    PRODUCT_PREFIX = '11'
    PRODUCT_BATCH_PREFIX = '12'
    WORK_ORDER_PREFIX = '13'
    WARRANTY_PREFIX = '14'
    
    # Index prefixes (starting with f)
    OWNER_INDEX_PREFIX = 'f0'
    ASSET_TYPE_INDEX_PREFIX = 'f1'
    BATCH_INDEX_PREFIX = 'f2'
    
    # Asset type prefix mapping
    ASSET_TYPE_PREFIXES = {
        'raw_material': RAW_MATERIAL_PREFIX,
        'product': PRODUCT_PREFIX,
        'product_batch': PRODUCT_BATCH_PREFIX,
        'work_order': WORK_ORDER_PREFIX,
        'warranty': WARRANTY_PREFIX
    }
    
    def get_namespace(self) -> str:
        """Get the family namespace."""
        return self.FAMILY_NAMESPACE
    
    # ==============================================
    # ACCOUNT ADDRESS GENERATION
    # ==============================================
    
    def generate_account_address(self, public_key: str) -> str:
        """Generate address for account data."""
        return self._generate_address(self.ACCOUNT_PREFIX, public_key)
    
    def generate_email_index_address(self, email: str) -> str:
        """Generate address for email index."""
        return self._generate_address(self.EMAIL_INDEX_PREFIX, email)
    
    def generate_account_type_index_address(self, account_type: str) -> str:
        """Generate address for account type index."""
        return self._generate_address(self.ACCOUNT_TYPE_INDEX_PREFIX, account_type)
    
    def generate_bootstrap_address(self) -> str:
        """Generate address for bootstrap status."""
        return self._generate_address(self.BOOTSTRAP_PREFIX, 'bootstrap_complete')
    
    # ==============================================
    # ASSET ADDRESS GENERATION
    # ==============================================
    
    def generate_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Generate address for an asset."""
        type_prefix = self.ASSET_TYPE_PREFIXES.get(asset_type, '1f')  # Default fallback
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

    def generate_asset_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        type_hash = hashlib.sha512(asset_type.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + self.ASSET_TYPE_INDEX_PREFIX + type_hash[:62]

    def generate_batch_index_address(self, batch_id: str) -> str:
        """Generate address for batch index (to track products in a batch)."""
        batch_hash = hashlib.sha512(batch_id.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + self.BATCH_INDEX_PREFIX + batch_hash[:62]
    
    # ==============================================
    # UTILITY METHODS
    # ==============================================
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate a blockchain address."""
        identifier_hash = hashlib.sha512(identifier.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + prefix + identifier_hash[:62]
    
    def get_all_account_addresses(self) -> List[str]:
        """Get list of address patterns for all account-related data."""
        return [
            self.FAMILY_NAMESPACE + self.ACCOUNT_PREFIX,
            self.FAMILY_NAMESPACE + self.EMAIL_INDEX_PREFIX,
            self.FAMILY_NAMESPACE + self.ACCOUNT_TYPE_INDEX_PREFIX,
            self.FAMILY_NAMESPACE + self.BOOTSTRAP_PREFIX
        ]
    
    def get_all_asset_addresses(self) -> List[str]:
        """Get list of address patterns for all asset-related data."""
        return [
            self.FAMILY_NAMESPACE + self.RAW_MATERIAL_PREFIX,
            self.FAMILY_NAMESPACE + self.PRODUCT_PREFIX,
            self.FAMILY_NAMESPACE + self.PRODUCT_BATCH_PREFIX,
            self.FAMILY_NAMESPACE + self.WORK_ORDER_PREFIX,
            self.FAMILY_NAMESPACE + self.WARRANTY_PREFIX
        ]
    
    def get_all_index_addresses(self) -> List[str]:
        """Get list of address patterns for all index data."""
        return [
            self.FAMILY_NAMESPACE + self.OWNER_INDEX_PREFIX,
            self.FAMILY_NAMESPACE + self.ASSET_TYPE_INDEX_PREFIX,
            self.FAMILY_NAMESPACE + self.BATCH_INDEX_PREFIX
        ]
    
    def get_all_addresses(self) -> List[str]:
        """Get list of all address patterns this TP handles."""
        return (self.get_all_account_addresses() + 
                self.get_all_asset_addresses() + 
                self.get_all_index_addresses())
    
    def is_account_address(self, address: str) -> bool:
        """Check if an address belongs to account data."""
        if len(address) < 8:
            return False
        prefix = address[6:8]
        return prefix in [self.ACCOUNT_PREFIX, self.EMAIL_INDEX_PREFIX, 
                         self.ACCOUNT_TYPE_INDEX_PREFIX, self.BOOTSTRAP_PREFIX]
    
    def is_asset_address(self, address: str) -> bool:
        """Check if an address belongs to asset data."""
        if len(address) < 8:
            return False
        prefix = address[6:8]
        return prefix in [self.RAW_MATERIAL_PREFIX, self.PRODUCT_PREFIX,
                         self.PRODUCT_BATCH_PREFIX, self.WORK_ORDER_PREFIX,
                         self.WARRANTY_PREFIX]
    
    def get_asset_type_from_address(self, address: str) -> str:
        """Get asset type from address prefix."""
        if len(address) < 8:
            return None
        
        prefix = address[6:8]
        prefix_to_type = {
            self.RAW_MATERIAL_PREFIX: 'raw_material',
            self.PRODUCT_PREFIX: 'product',
            self.PRODUCT_BATCH_PREFIX: 'product_batch',
            self.WORK_ORDER_PREFIX: 'work_order',
            self.WARRANTY_PREFIX: 'warranty'
        }
        return prefix_to_type.get(prefix)
