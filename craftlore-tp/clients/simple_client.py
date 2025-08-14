#!/usr/bin/env python3
"""
Simple read client module for CraftLore Combined TP.
Can be imported and used in other scripts.
"""

import base64
import hashlib
import requests
import json
from typing import Optional, List, Dict

# Configuration
DEFAULT_REST_API_URL = "http://localhost:8008"
FAMILY_NAME = 'craftlore'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]

# Address prefixes
ACCOUNT_PREFIX = '00'
EMAIL_INDEX_PREFIX = '01'
ACCOUNT_TYPE_INDEX_PREFIX = '02'

ASSET_TYPE_PREFIXES = {
    'raw_material': '10',
    'product': '11',
    'product_batch': '12',
    'work_order': '13',
    'warranty': '14'
}

OWNER_INDEX_PREFIX = 'f0'
ASSET_TYPE_INDEX_PREFIX = 'f1'


class CraftLoreClient:
    """Simple client for reading CraftLore blockchain data."""
    
    def __init__(self, rest_api_url: str = DEFAULT_REST_API_URL):
        self.rest_api_url = rest_api_url
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate a blockchain address."""
        identifier_hash = hashlib.sha512(identifier.encode()).hexdigest()
        return NAMESPACE + prefix + identifier_hash[:62]
    
    def _get_state(self, address: str) -> Optional[Dict]:
        """Get and parse state data from an address."""
        url = f"{self.rest_api_url}/state/{address}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data:
                    raw_data = base64.b64decode(data['data'])
                    return json.loads(raw_data.decode('utf-8'))
        except Exception as e:
            print(f"Error fetching state: {e}")
        return None
    
    # Account methods
    def get_account(self, public_key: str) -> Optional[Dict]:
        """Get account by public key."""
        address = self._generate_address(ACCOUNT_PREFIX, public_key)
        return self._get_state(address)
    
    def get_account_by_email(self, email: str) -> Optional[Dict]:
        """Get account by email."""
        email_address = self._generate_address(EMAIL_INDEX_PREFIX, email)
        email_data = self._get_state(email_address)
        
        if email_data and 'public_key' in email_data:
            return self.get_account(email_data['public_key'])
        return None
    
    def get_accounts_by_type(self, account_type: str) -> List[Dict]:
        """Get all accounts of a specific type."""
        address = self._generate_address(ACCOUNT_TYPE_INDEX_PREFIX, account_type)
        index_data = self._get_state(address)
        
        if not index_data or 'public_keys' not in index_data:
            return []
        
        accounts = []
        for public_key in index_data['public_keys']:
            account = self.get_account(public_key)
            if account and not account.get('is_deleted', False):
                accounts.append(account)
        
        return accounts
    
    # Asset methods
    def get_asset(self, asset_id: str, asset_type: str) -> Optional[Dict]:
        """Get asset by ID and type."""
        type_prefix = ASSET_TYPE_PREFIXES.get(asset_type, '1f')
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        address = NAMESPACE + type_prefix + asset_hash[:62]
        return self._get_state(address)
    
    def get_assets_by_owner(self, owner_public_key: str) -> List[Dict]:
        """Get all assets owned by a public key."""
        address = self._generate_address(OWNER_INDEX_PREFIX, owner_public_key)
        index_data = self._get_state(address)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            for asset_type in ASSET_TYPE_PREFIXES.keys():
                asset = self.get_asset(asset_id, asset_type)
                if asset:
                    assets.append(asset)
                    break
        
        return assets
    
    def get_assets_by_type(self, asset_type: str) -> List[Dict]:
        """Get all assets of a specific type."""
        address = self._generate_address(ASSET_TYPE_INDEX_PREFIX, asset_type)
        index_data = self._get_state(address)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                assets.append(asset)
        
        return assets
    
    # Convenience methods
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get a product by ID."""
        return self.get_asset(product_id, 'product')
    
    def get_all_products(self) -> List[Dict]:
        """Get all products."""
        return self.get_assets_by_type('product')
    
    def get_all_artisans(self) -> List[Dict]:
        """Get all artisan accounts."""
        return self.get_accounts_by_type('artisan')
    
    def get_all_suppliers(self) -> List[Dict]:
        """Get all supplier accounts."""
        return self.get_accounts_by_type('supplier')


# Convenience functions for quick usage
def get_account(public_key: str, rest_api_url: str = DEFAULT_REST_API_URL) -> Optional[Dict]:
    """Quick function to get an account."""
    client = CraftLoreClient(rest_api_url)
    return client.get_account(public_key)


def get_product(product_id: str, rest_api_url: str = DEFAULT_REST_API_URL) -> Optional[Dict]:
    """Quick function to get a product."""
    client = CraftLoreClient(rest_api_url)
    return client.get_product(product_id)


def get_all_artisans(rest_api_url: str = DEFAULT_REST_API_URL) -> List[Dict]:
    """Quick function to get all artisans."""
    client = CraftLoreClient(rest_api_url)
    return client.get_all_artisans()


if __name__ == "__main__":
    # Simple test
    client = CraftLoreClient()
    
    print("Testing CraftLore Client...")
    artisans = client.get_all_artisans()
    print(f"Found {len(artisans)} artisans")
    
    products = client.get_all_products()
    print(f"Found {len(products)} products")
