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
    BOOTSTRAP_PREFIX = '03'
    ASSET_PREFIX = '04'

    


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
       
    def generate_bootstrap_address(self) -> str:
        """Generate address for bootstrap status."""
        return self._generate_address(self.BOOTSTRAP_PREFIX, 'bootstrap_complete')
    
    # ==============================================
    # ASSET ADDRESS GENERATION
    # ==============================================
    
    def generate_asset_address(self, asset_id: str) -> str:
        """Generate address for an asset."""
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + asset_hash[:62]
    

  
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
            self.FAMILY_NAMESPACE + self.BOOTSTRAP_PREFIX
        ]
        
    def is_account_address(self, address: str) -> bool:
        """Check if an address belongs to account data."""
        if len(address) < 8:
            return False
        prefix = address[6:8]
        return prefix in [self.ACCOUNT_PREFIX, self.EMAIL_INDEX_PREFIX]
    
    def is_asset_address(self, address: str) -> bool:
        """Check if an address belongs to asset data."""
        if len(address) < 8:
            return False
        prefix = address[6:8]
        return prefix in [self.ASSET_PREFIX]
    
