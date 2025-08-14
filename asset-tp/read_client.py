#!/usr/bin/env python3
"""
Read client for CraftLore Asset TP.
Demonstrates how any asset (including products) can be easily addressed and queried.
"""

import base64
import hashlib
import requests
import sys
import json
from typing import Optional, List, Dict

# Configuration
REST_API_URL = "http://localhost:8008"
FAMILY_NAME = 'craftlore-asset'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]

# Asset type prefixes (matching the address generator)
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


class AssetReadClient:
    """Client for reading asset data from the blockchain."""
    
    def __init__(self, rest_api_url: str = REST_API_URL):
        self.rest_api_url = rest_api_url
    
    def _make_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Generate address for a specific asset."""
        type_prefix = ASSET_TYPE_PREFIXES.get(asset_type, '00')
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        return NAMESPACE + type_prefix + asset_hash[:62]
    
    def _make_owner_index_address(self, owner_public_key: str) -> str:
        """Generate address for owner index."""
        owner_hash = hashlib.sha512(owner_public_key.encode()).hexdigest()
        return NAMESPACE + OWNER_INDEX_PREFIX + owner_hash[:62]
    
    def _make_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        type_hash = hashlib.sha512(asset_type.encode()).hexdigest()
        return NAMESPACE + TYPE_INDEX_PREFIX + type_hash[:62]
    
    def _make_batch_index_address(self, batch_id: str) -> str:
        """Generate address for batch index."""
        batch_hash = hashlib.sha512(batch_id.encode()).hexdigest()
        return NAMESPACE + BATCH_INDEX_PREFIX + batch_hash[:62]
    
    def _get_state(self, address: str) -> Optional[bytes]:
        """Get state data from a specific address."""
        url = f"{self.rest_api_url}/state/{address}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data:
                    return base64.b64decode(data['data'])
        except Exception as e:
            print(f"Error fetching state: {e}")
        return None
    
    def _parse_json_data(self, data: bytes) -> Optional[Dict]:
        """Parse JSON data from state."""
        if data:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception as e:
                print(f"Error parsing JSON: {e}")
        return None
    
    def get_asset_by_id(self, asset_id: str, asset_type: str) -> Optional[Dict]:
        """
        Get a specific asset by its ID and type.
        
        Args:
            asset_id: The unique identifier of the asset
            asset_type: Type of asset ('raw_material', 'product', 'product_batch', 'work_order', 'warranty')
        
        Returns:
            Asset data dictionary or None if not found
        """
        address = self._make_asset_address(asset_id, asset_type)
        data = self._get_state(address)
        return self._parse_json_data(data)
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get a specific product by ID.
        Convenience method for products.
        
        Args:
            product_id: The unique identifier of the product
        
        Returns:
            Product data dictionary or None if not found
        """
        return self.get_asset_by_id(product_id, 'product')
    
    def get_assets_by_owner(self, owner_public_key: str) -> List[Dict]:
        """
        Get all assets owned by a specific public key.
        
        Args:
            owner_public_key: The public key of the owner
        
        Returns:
            List of asset data dictionaries
        """
        address = self._make_owner_index_address(owner_public_key)
        data = self._get_state(address)
        index_data = self._parse_json_data(data)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            # Try each asset type to find the asset
            for asset_type in ASSET_TYPE_PREFIXES.keys():
                asset = self.get_asset_by_id(asset_id, asset_type)
                if asset:
                    assets.append(asset)
                    break
        
        return assets
    
    def get_assets_by_type(self, asset_type: str) -> List[Dict]:
        """
        Get all assets of a specific type.
        
        Args:
            asset_type: Type of asset to query
        
        Returns:
            List of asset data dictionaries
        """
        address = self._make_type_index_address(asset_type)
        data = self._get_state(address)
        index_data = self._parse_json_data(data)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            asset = self.get_asset_by_id(asset_id, asset_type)
            if asset:
                assets.append(asset)
        
        return assets
    
    def get_products_from_batch(self, batch_id: str) -> List[Dict]:
        """
        Get all products created from a specific batch.
        
        Args:
            batch_id: The ID of the product batch
        
        Returns:
            List of product data dictionaries
        """
        address = self._make_batch_index_address(batch_id)
        data = self._get_state(address)
        index_data = self._parse_json_data(data)
        
        if not index_data or 'products' not in index_data:
            return []
        
        products = []
        for product_id in index_data['products']:
            product = self.get_product(product_id)
            if product:
                products.append(product)
        
        return products
    
    def search_assets(self, filters: Dict) -> List[Dict]:
        """
        Search assets with various filters.
        
        Args:
            filters: Dictionary of search criteria:
                - asset_type: Filter by asset type
                - owner: Filter by owner public key
                - status: Filter by asset status
                - certification_type: Filter by certification type
        
        Returns:
            List of matching asset data dictionaries
        """
        assets = []
        
        # Start with type filter if provided
        if 'asset_type' in filters:
            assets = self.get_assets_by_type(filters['asset_type'])
        elif 'owner' in filters:
            assets = self.get_assets_by_owner(filters['owner'])
        else:
            # Get all assets by querying each type
            for asset_type in ASSET_TYPE_PREFIXES.keys():
                assets.extend(self.get_assets_by_type(asset_type))
        
        # Apply additional filters
        filtered_assets = []
        for asset in assets:
            match = True
            
            if 'owner' in filters and asset.get('owner') != filters['owner']:
                match = False
            
            if 'status' in filters and asset.get('status') != filters['status']:
                match = False
            
            if 'certification_type' in filters:
                certifications = asset.get('certifications', [])
                has_cert = any(
                    cert.get('certification_type') == filters['certification_type']
                    for cert in certifications
                )
                if not has_cert:
                    match = False
            
            if match:
                filtered_assets.append(asset)
        
        return filtered_assets
    
    def print_asset(self, asset: Dict):
        """Pretty print asset information."""
        if not asset:
            print("Asset not found.")
            return
        
        print(f"\n=== {asset.get('asset_type', 'Unknown').title()} Asset ===")
        print(f"Asset ID: {asset.get('asset_id')}")
        print(f"Owner: {asset.get('owner')}")
        print(f"Status: {asset.get('status')}")
        print(f"Created: {asset.get('created_at')}")
        
        if 'name' in asset:
            print(f"Name: {asset['name']}")
        if 'description' in asset:
            print(f"Description: {asset['description']}")
        if 'warranty_id' in asset:
            print(f"Warranty: {asset['warranty_id']}")
        
        if 'certifications' in asset and asset['certifications']:
            print("Certifications:")
            for cert in asset['certifications']:
                print(f"  - {cert.get('certification_type')} by {cert.get('certifying_authority')}")
        
        print()


def main():
    """Main CLI interface for asset querying."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python read_client.py get_asset <asset_id> <asset_type>")
        print("  python read_client.py get_product <product_id>")
        print("  python read_client.py get_by_owner <owner_public_key>")
        print("  python read_client.py get_by_type <asset_type>")
        print("  python read_client.py get_batch_products <batch_id>")
        print("  python read_client.py search_certified <certification_type>")
        print("\nAsset types: raw_material, product, product_batch, work_order, warranty")
        return
    
    client = AssetReadClient()
    command = sys.argv[1]
    
    if command == "get_asset" and len(sys.argv) >= 4:
        asset_id = sys.argv[2]
        asset_type = sys.argv[3]
        asset = client.get_asset_by_id(asset_id, asset_type)
        client.print_asset(asset)
    
    elif command == "get_product" and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        product = client.get_product(product_id)
        client.print_asset(product)
    
    elif command == "get_by_owner" and len(sys.argv) >= 3:
        owner = sys.argv[2]
        assets = client.get_assets_by_owner(owner)
        print(f"Found {len(assets)} assets for owner {owner}:")
        for asset in assets:
            client.print_asset(asset)
    
    elif command == "get_by_type" and len(sys.argv) >= 3:
        asset_type = sys.argv[2]
        assets = client.get_assets_by_type(asset_type)
        print(f"Found {len(assets)} assets of type {asset_type}:")
        for asset in assets:
            client.print_asset(asset)
    
    elif command == "get_batch_products" and len(sys.argv) >= 3:
        batch_id = sys.argv[2]
        products = client.get_products_from_batch(batch_id)
        print(f"Found {len(products)} products from batch {batch_id}:")
        for product in products:
            client.print_asset(product)
    
    elif command == "search_certified" and len(sys.argv) >= 3:
        cert_type = sys.argv[2]
        assets = client.search_assets({'certification_type': cert_type})
        print(f"Found {len(assets)} assets with {cert_type} certification:")
        for asset in assets:
            client.print_asset(asset)
    
    else:
        print("Invalid command or missing arguments.")


if __name__ == "__main__":
    main()
