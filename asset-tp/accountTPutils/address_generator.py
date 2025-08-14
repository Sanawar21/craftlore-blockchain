#!/usr/bin/env python3
"""
Address generator for CraftLore Account TP.
"""

import hashlib


class AccountAddressGenerator:
    """Generates blockchain addresses for account-related data."""
    
    FAMILY_NAME = 'craftlore-account' 
    FAMILY_NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]
    
    # Address prefixes (2 characters each)
    ACCOUNT_PREFIX = '00'
    EMAIL_INDEX_PREFIX = '01'
    TYPE_INDEX_PREFIX = '02'
    BOOTSTRAP_PREFIX = '03'
    
    def generate_account_address(self, public_key: str) -> str:
        """Generate address for account data."""
        return self._generate_address(self.ACCOUNT_PREFIX, public_key)
    
    def generate_email_index_address(self, email: str) -> str:
        """Generate address for email index."""
        return self._generate_address(self.EMAIL_INDEX_PREFIX, email)
    
    def generate_type_index_address(self, account_type: str) -> str:
        """Generate address for account type index."""
        return self._generate_address(self.TYPE_INDEX_PREFIX, account_type)
    
    def generate_bootstrap_address(self) -> str:
        """Generate address for bootstrap status."""
        return self._generate_address(self.BOOTSTRAP_PREFIX, 'bootstrap_complete')
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate a blockchain address."""
        identifier_hash = hashlib.sha512(identifier.encode()).hexdigest()
        return self.FAMILY_NAMESPACE + prefix + identifier_hash[:62]
    
    def get_namespace(self) -> str:
        """Get the family namespace."""
        return self.FAMILY_NAMESPACE
