#!/usr/bin/env python3
"""
Read client for CraftLore Combined TP.
Demonstrates how to query both accounts and assets from the unified blockchain.
"""

import base64
import hashlib
import requests
import sys
import json
from typing import Optional, List, Dict

# Configuration
REST_API_URL = "http://localhost:8008"
FAMILY_NAME = 'craftlore'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]

# Account prefixes (starting with 0)
ACCOUNT_PREFIX = '00'
EMAIL_INDEX_PREFIX = '01'
ACCOUNT_TYPE_INDEX_PREFIX = '02'
BOOTSTRAP_PREFIX = '03'

# Asset prefixes (starting with 1)
ASSET_TYPE_PREFIXES = {
    'raw_material': '10',
    'product': '11',
    'product_batch': '12',
    'work_order': '13',
    'warranty': '14'
}

# Index prefixes (starting with f)
OWNER_INDEX_PREFIX = 'f0'
ASSET_TYPE_INDEX_PREFIX = 'f1'
BATCH_INDEX_PREFIX = 'f2'


class CraftLoreReadClient:
    """Client for reading both account and asset data from the unified blockchain."""
    
    def __init__(self, rest_api_url: str = REST_API_URL):
        self.rest_api_url = rest_api_url
    
    # =============================================
    # ADDRESS GENERATION
    # =============================================
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate a blockchain address."""
        identifier_hash = hashlib.sha512(identifier.encode()).hexdigest()
        return NAMESPACE + prefix + identifier_hash[:62]
    
    def _make_account_address(self, public_key: str) -> str:
        """Generate address for account data."""
        return self._generate_address(ACCOUNT_PREFIX, public_key)
    
    def _make_email_index_address(self, email: str) -> str:
        """Generate address for email index."""
        return self._generate_address(EMAIL_INDEX_PREFIX, email)
    
    def _make_account_type_index_address(self, account_type: str) -> str:
        """Generate address for account type index."""
        return self._generate_address(ACCOUNT_TYPE_INDEX_PREFIX, account_type)
    
    def _make_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Generate address for a specific asset."""
        type_prefix = ASSET_TYPE_PREFIXES.get(asset_type, '1f')
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        return NAMESPACE + type_prefix + asset_hash[:62]
    
    def _make_owner_index_address(self, owner_public_key: str) -> str:
        """Generate address for owner index."""
        owner_hash = hashlib.sha512(owner_public_key.encode()).hexdigest()
        return NAMESPACE + OWNER_INDEX_PREFIX + owner_hash[:62]
    
    def _make_asset_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        type_hash = hashlib.sha512(asset_type.encode()).hexdigest()
        return NAMESPACE + ASSET_TYPE_INDEX_PREFIX + type_hash[:62]
    
    def _make_batch_index_address(self, batch_id: str) -> str:
        """Generate address for batch index."""
        batch_hash = hashlib.sha512(batch_id.encode()).hexdigest()
        return NAMESPACE + BATCH_INDEX_PREFIX + batch_hash[:62]
    
    # =============================================
    # UTILITY METHODS
    # =============================================
    
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
    
    # =============================================
    # ACCOUNT QUERY METHODS
    # =============================================
    
    def get_account_by_public_key(self, public_key: str) -> Optional[Dict]:
        """
        Get an account by its public key.
        
        Args:
            public_key: The public key of the account
        
        Returns:
            Account data dictionary or None if not found
        """
        address = self._make_account_address(public_key)
        data = self._get_state(address)
        return self._parse_json_data(data)
    
    def get_account_by_email(self, email: str) -> Optional[Dict]:
        """
        Get an account by its email address.
        
        Args:
            email: The email address of the account
        
        Returns:
            Account data dictionary or None if not found
        """
        # First get the email index to find the public key
        email_address = self._make_email_index_address(email)
        data = self._get_state(email_address)
        email_data = self._parse_json_data(data)
        
        if email_data and 'public_key' in email_data:
            return self.get_account_by_public_key(email_data['public_key'])
        
        return None
    
    def get_accounts_by_type(self, account_type: str) -> List[Dict]:
        """
        Get all accounts of a specific type.
        
        Args:
            account_type: Type of account to query
        
        Returns:
            List of account data dictionaries
        """
        address = self._make_account_type_index_address(account_type)
        data = self._get_state(address)
        index_data = self._parse_json_data(data)
        
        if not index_data or 'public_keys' not in index_data:
            return []
        
        accounts = []
        for public_key in index_data['public_keys']:
            account = self.get_account_by_public_key(public_key)
            if account and not account.get('is_deleted', False):
                accounts.append(account)
        
        return accounts
    
    def get_all_artisans(self) -> List[Dict]:
        """Get all artisan accounts."""
        return self.get_accounts_by_type('artisan')
    
    def get_all_workshops(self) -> List[Dict]:
        """Get all workshop accounts."""
        return self.get_accounts_by_type('workshop')
    
    def get_all_suppliers(self) -> List[Dict]:
        """Get all supplier accounts."""
        return self.get_accounts_by_type('supplier')
    
    # =============================================
    # ASSET QUERY METHODS
    # =============================================
    
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
        address = self._make_asset_type_index_address(asset_type)
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
    
    # =============================================
    # COMBINED QUERY METHODS
    # =============================================
    
    def get_artisan_with_products(self, public_key: str) -> Dict:
        """
        Get artisan account data along with their products.
        
        Args:
            public_key: The public key of the artisan
        
        Returns:
            Dictionary with artisan data and their products
        """
        account = self.get_account_by_public_key(public_key)
        assets = self.get_assets_by_owner(public_key)
        
        products = [asset for asset in assets if asset.get('asset_type') == 'product']
        
        return {
            'account': account,
            'products': products,
            'total_products': len(products)
        }
    
    def get_workshop_with_production(self, public_key: str) -> Dict:
        """
        Get workshop account data along with their production assets.
        
        Args:
            public_key: The public key of the workshop
        
        Returns:
            Dictionary with workshop data and their assets
        """
        account = self.get_account_by_public_key(public_key)
        assets = self.get_assets_by_owner(public_key)
        
        products = [asset for asset in assets if asset.get('asset_type') == 'product']
        batches = [asset for asset in assets if asset.get('asset_type') == 'product_batch']
        work_orders = [asset for asset in assets if asset.get('asset_type') == 'work_order']
        
        return {
            'account': account,
            'products': products,
            'batches': batches,
            'work_orders': work_orders,
            'total_assets': len(assets)
        }
    
    def get_supply_chain_for_product(self, product_id: str) -> Dict:
        """
        Get the full supply chain information for a product.
        
        Args:
            product_id: The ID of the product
        
        Returns:
            Dictionary with supply chain information
        """
        product = self.get_product(product_id)
        if not product:
            return {'error': 'Product not found'}
        
        supply_chain = {
            'product': product,
            'creator': None,
            'raw_materials': [],
            'batch': None
        }
        
        # Get creator account
        if 'owner' in product:
            supply_chain['creator'] = self.get_account_by_public_key(product['owner'])
        
        # Get batch information if available
        if 'batch_id' in product:
            batch = self.get_asset_by_id(product['batch_id'], 'product_batch')
            supply_chain['batch'] = batch
            
            # Get raw materials used in the batch
            if batch and 'raw_materials' in batch:
                for rm_id in batch['raw_materials']:
                    raw_material = self.get_asset_by_id(rm_id, 'raw_material')
                    if raw_material:
                        supply_chain['raw_materials'].append(raw_material)
        
        return supply_chain
    
    # =============================================
    # SEARCH METHODS
    # =============================================
    
    def search_accounts(self, filters: Dict) -> List[Dict]:
        """
        Search accounts with various filters.
        
        Args:
            filters: Dictionary of search criteria:
                - account_type: Filter by account type
                - authentication_status: Filter by authentication status
                - region: Filter by region
        
        Returns:
            List of matching account data dictionaries
        """
        accounts = []
        
        # Start with type filter if provided
        if 'account_type' in filters:
            accounts = self.get_accounts_by_type(filters['account_type'])
        else:
            # Get all accounts by querying each type
            account_types = ['buyer', 'seller', 'artisan', 'workshop', 'distributor', 
                           'wholesaler', 'retailer', 'verifier', 'admin', 'super_admin', 'supplier']
            for account_type in account_types:
                accounts.extend(self.get_accounts_by_type(account_type))
        
        # Apply additional filters
        filtered_accounts = []
        for account in accounts:
            match = True
            
            if 'authentication_status' in filters and account.get('authentication_status') != filters['authentication_status']:
                match = False
            
            if 'region' in filters and account.get('region') != filters['region']:
                match = False
            
            if match:
                filtered_accounts.append(account)
        
        return filtered_accounts
    
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
    
    # =============================================
    # PRETTY PRINTING METHODS
    # =============================================
    
    def print_account(self, account: Dict):
        """Pretty print account information."""
        if not account:
            print("Account not found.")
            return
        
        print(f"\n=== {account.get('account_type', 'Unknown').title()} Account ===")
        print(f"Account ID: {account.get('account_id')}")
        print(f"Public Key: {account.get('public_key')}")
        print(f"Email: {account.get('email')}")
        print(f"Authentication Status: {account.get('authentication_status')}")
        print(f"Verification Status: {account.get('verification_status')}")
        print(f"Region: {account.get('region', 'Not specified')}")
        print(f"Created: {account.get('created_timestamp')}")
        
        if 'specialization' in account and account['specialization']:
            print(f"Specialization: {', '.join(account['specialization'])}")
        
        if 'certifications' in account and account['certifications']:
            print("Certifications:")
            for cert in account['certifications']:
                print(f"  - {cert}")
        
        print()
    
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
        if 'batch_id' in asset:
            print(f"Batch ID: {asset['batch_id']}")
        
        if 'certifications' in asset and asset['certifications']:
            print("Certifications:")
            for cert in asset['certifications']:
                print(f"  - {cert.get('certification_type')} by {cert.get('certifying_authority')}")
        
        print()
    
    def print_supply_chain(self, supply_chain: Dict):
        """Pretty print supply chain information."""
        if 'error' in supply_chain:
            print(f"Error: {supply_chain['error']}")
            return
        
        print("\n=== SUPPLY CHAIN INFORMATION ===")
        
        print("\n--- PRODUCT ---")
        self.print_asset(supply_chain['product'])
        
        if supply_chain['creator']:
            print("--- CREATOR/ARTISAN ---")
            self.print_account(supply_chain['creator'])
        
        if supply_chain['batch']:
            print("--- PRODUCTION BATCH ---")
            self.print_asset(supply_chain['batch'])
        
        if supply_chain['raw_materials']:
            print("--- RAW MATERIALS ---")
            for rm in supply_chain['raw_materials']:
                self.print_asset(rm)


def main():
    """Main CLI interface for querying the CraftLore blockchain."""
    if len(sys.argv) < 2:
        print("CraftLore Read Client - Query accounts and assets")
        print("\nUsage:")
        print("  ACCOUNT QUERIES:")
        print("    python read_client.py get_account <public_key>")
        print("    python read_client.py get_account_by_email <email>")
        print("    python read_client.py get_accounts_by_type <account_type>")
        print("    python read_client.py get_artisans")
        print("    python read_client.py get_workshops")
        print("    python read_client.py get_suppliers")
        print("\n  ASSET QUERIES:")
        print("    python read_client.py get_asset <asset_id> <asset_type>")
        print("    python read_client.py get_product <product_id>")
        print("    python read_client.py get_assets_by_owner <owner_public_key>")
        print("    python read_client.py get_assets_by_type <asset_type>")
        print("    python read_client.py get_batch_products <batch_id>")
        print("\n  COMBINED QUERIES:")
        print("    python read_client.py get_artisan_products <public_key>")
        print("    python read_client.py get_workshop_production <public_key>")
        print("    python read_client.py get_supply_chain <product_id>")
        print("\n  SEARCH:")
        print("    python read_client.py search_accounts <filter_key>=<filter_value>")
        print("    python read_client.py search_assets <filter_key>=<filter_value>")
        print("\nAccount types: buyer, seller, artisan, workshop, distributor, wholesaler, retailer, verifier, admin, super_admin, supplier")
        print("Asset types: raw_material, product, product_batch, work_order, warranty")
        return
    
    client = CraftLoreReadClient()
    command = sys.argv[1]
    
    # Account queries
    if command == "get_account" and len(sys.argv) >= 3:
        public_key = sys.argv[2]
        account = client.get_account_by_public_key(public_key)
        client.print_account(account)
    
    elif command == "get_account_by_email" and len(sys.argv) >= 3:
        email = sys.argv[2]
        account = client.get_account_by_email(email)
        client.print_account(account)
    
    elif command == "get_accounts_by_type" and len(sys.argv) >= 3:
        account_type = sys.argv[2]
        accounts = client.get_accounts_by_type(account_type)
        print(f"Found {len(accounts)} accounts of type {account_type}:")
        for account in accounts:
            client.print_account(account)
    
    elif command == "get_artisans":
        accounts = client.get_all_artisans()
        print(f"Found {len(accounts)} artisan accounts:")
        for account in accounts:
            client.print_account(account)
    
    elif command == "get_workshops":
        accounts = client.get_all_workshops()
        print(f"Found {len(accounts)} workshop accounts:")
        for account in accounts:
            client.print_account(account)
    
    elif command == "get_suppliers":
        accounts = client.get_all_suppliers()
        print(f"Found {len(accounts)} supplier accounts:")
        for account in accounts:
            client.print_account(account)
    
    # Asset queries
    elif command == "get_asset" and len(sys.argv) >= 4:
        asset_id = sys.argv[2]
        asset_type = sys.argv[3]
        asset = client.get_asset_by_id(asset_id, asset_type)
        client.print_asset(asset)
    
    elif command == "get_product" and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        product = client.get_product(product_id)
        client.print_asset(product)
    
    elif command == "get_assets_by_owner" and len(sys.argv) >= 3:
        owner = sys.argv[2]
        assets = client.get_assets_by_owner(owner)
        print(f"Found {len(assets)} assets for owner {owner}:")
        for asset in assets:
            client.print_asset(asset)
    
    elif command == "get_assets_by_type" and len(sys.argv) >= 3:
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
    
    # Combined queries
    elif command == "get_artisan_products" and len(sys.argv) >= 3:
        public_key = sys.argv[2]
        result = client.get_artisan_with_products(public_key)
        client.print_account(result['account'])
        print(f"Products created by this artisan ({result['total_products']}):")
        for product in result['products']:
            client.print_asset(product)
    
    elif command == "get_workshop_production" and len(sys.argv) >= 3:
        public_key = sys.argv[2]
        result = client.get_workshop_with_production(public_key)
        client.print_account(result['account'])
        print(f"\nWorkshop Production Summary:")
        print(f"  Total Assets: {result['total_assets']}")
        print(f"  Products: {len(result['products'])}")
        print(f"  Batches: {len(result['batches'])}")
        print(f"  Work Orders: {len(result['work_orders'])}")
    
    elif command == "get_supply_chain" and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        supply_chain = client.get_supply_chain_for_product(product_id)
        client.print_supply_chain(supply_chain)
    
    # Search commands
    elif command == "search_accounts" and len(sys.argv) >= 3:
        filter_str = sys.argv[2]
        if '=' in filter_str:
            key, value = filter_str.split('=', 1)
            filters = {key: value}
            accounts = client.search_accounts(filters)
            print(f"Found {len(accounts)} accounts matching filter {key}={value}:")
            for account in accounts:
                client.print_account(account)
        else:
            print("Filter format: key=value")
    
    elif command == "search_assets" and len(sys.argv) >= 3:
        filter_str = sys.argv[2]
        if '=' in filter_str:
            key, value = filter_str.split('=', 1)
            filters = {key: value}
            assets = client.search_assets(filters)
            print(f"Found {len(assets)} assets matching filter {key}={value}:")
            for asset in assets:
                client.print_asset(asset)
        else:
            print("Filter format: key=value")
    
    else:
        print("Invalid command or missing arguments.")


if __name__ == "__main__":
    main()
