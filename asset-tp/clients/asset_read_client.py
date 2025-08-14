#!/usr/bin/env python3
"""
Asset Read Client for CraftLore Asset TP.
Provides comprehensive querying and reading capabilities for all asset types.
"""

import sys
import json
from typing import Dict, List, Optional
from base_client import AssetClient


class AssetReadClient(AssetClient):
    """Client for reading and querying assets."""
    
    def list_all_assets(self, show_details: bool = False) -> Dict[str, List]:
        """List all assets by type."""
        all_assets = {}
        
        for asset_type in self.ASSET_TYPE_PREFIXES.keys():
            assets = self.get_assets_by_type(asset_type)
            all_assets[asset_type] = assets
            
            print(f"\n{asset_type.replace('_', ' ').title()}s ({len(assets)} found):")
            if assets:
                for asset in assets:
                    print(f"  • {asset.get('asset_id')} - Owner: {asset.get('owner', 'Unknown')[:16]}...")
                    if show_details:
                        print(f"    Status: {asset.get('status', 'Unknown')}")
                        if 'name' in asset:
                            print(f"    Name: {asset['name']}")
            else:
                print("  (none found)")
        
        return all_assets
    
    def search_assets(self, filters: Dict) -> List[Dict]:
        """
        Search assets with various filters.
        
        Supported filters:
        - asset_type: Filter by asset type
        - owner: Filter by owner public key  
        - status: Filter by asset status
        - certification_type: Filter by certification type
        - name: Filter by name (partial match)
        - batch_id: Filter by batch ID
        """
        print(f"🔍 Searching assets with filters: {filters}")
        
        assets = []
        
        # Start with type filter if provided
        if 'asset_type' in filters:
            assets = self.get_assets_by_type(filters['asset_type'])
        elif 'owner' in filters:
            assets = self.get_assets_by_owner(filters['owner'])
        else:
            # Get all assets by querying each type
            for asset_type in self.ASSET_TYPE_PREFIXES.keys():
                assets.extend(self.get_assets_by_type(asset_type))
        
        # Apply additional filters
        filtered_assets = []
        for asset in assets:
            match = True
            
            if 'owner' in filters and asset.get('owner') != filters['owner']:
                match = False
            
            if 'status' in filters and asset.get('status') != filters['status']:
                match = False
            
            if 'name' in filters and filters['name'].lower() not in asset.get('name', '').lower():
                match = False
            
            if 'batch_id' in filters and asset.get('batch_id') != filters['batch_id']:
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
        
        print(f"Found {len(filtered_assets)} matching assets")
        return filtered_assets
    
    def get_asset_chain(self, asset_id: str, asset_type: str) -> Dict:
        """Get an asset and its related assets (batch, work order, warranty, etc.)."""
        print(f"🔗 Getting asset chain for: {asset_id} ({asset_type})")
        
        chain = {
            'main_asset': None,
            'batch': None,
            'work_order': None,
            'warranty': None,
            'products': [],
            'raw_materials': []
        }
        
        # Get main asset
        main_asset = self.get_asset(asset_id, asset_type)
        if not main_asset:
            print(f"❌ Asset not found: {asset_id}")
            return chain
        
        chain['main_asset'] = main_asset
        
        # Get related assets based on type
        if asset_type == 'product':
            # Get batch if product has batch_id
            if 'batch_id' in main_asset:
                batch = self.get_asset(main_asset['batch_id'], 'product_batch')
                if batch:
                    chain['batch'] = batch
                    
                    # Get raw materials used in batch
                    if 'raw_materials_used' in batch:
                        for rm_id in batch['raw_materials_used']:
                            rm = self.get_asset(rm_id, 'raw_material')
                            if rm:
                                chain['raw_materials'].append(rm)
                    
                    # Get work order for batch
                    if 'work_order_id' in batch:
                        wo = self.get_asset(batch['work_order_id'], 'work_order')
                        if wo:
                            chain['work_order'] = wo
            
            # Look for warranty
            warranties = self.get_assets_by_type('warranty')
            for warranty in warranties:
                if warranty.get('product_id') == asset_id:
                    chain['warranty'] = warranty
                    break
        
        elif asset_type == 'product_batch':
            # Get raw materials
            if 'raw_materials_used' in main_asset:
                for rm_id in main_asset['raw_materials_used']:
                    rm = self.get_asset(rm_id, 'raw_material')
                    if rm:
                        chain['raw_materials'].append(rm)
            
            # Get work order
            if 'work_order_id' in main_asset:
                wo = self.get_asset(main_asset['work_order_id'], 'work_order')
                if wo:
                    chain['work_order'] = wo
            
            # Find products from this batch
            products = self.get_assets_by_type('product')
            for product in products:
                if product.get('batch_id') == asset_id:
                    chain['products'].append(product)
        
        elif asset_type == 'work_order':
            # Get batch
            if 'batch_id' in main_asset:
                batch = self.get_asset(main_asset['batch_id'], 'product_batch')
                if batch:
                    chain['batch'] = batch
        
        elif asset_type == 'warranty':
            # Get product
            if 'product_id' in main_asset:
                product = self.get_asset(main_asset['product_id'], 'product')
                if product:
                    # Replace main asset with product for chain analysis
                    product_chain = self.get_asset_chain(main_asset['product_id'], 'product')
                    chain.update(product_chain)
                    chain['warranty'] = main_asset  # Keep warranty as main focus
        
        return chain
    
    def print_asset_chain(self, chain: Dict):
        """Pretty print an asset chain."""
        if not chain['main_asset']:
            print("No asset found")
            return
        
        main_asset = chain['main_asset']
        print(f"\n{'='*80}")
        print(f"ASSET CHAIN FOR: {main_asset['asset_id']} ({main_asset['asset_type']})")
        print(f"{'='*80}")
        
        # Main asset
        print(f"\n🎯 MAIN ASSET:")
        self.print_asset(main_asset)
        
        # Raw materials
        if chain['raw_materials']:
            print(f"🌱 RAW MATERIALS ({len(chain['raw_materials'])}):")
            for rm in chain['raw_materials']:
                print(f"  📦 {rm['asset_id']}: {rm.get('material_type', 'Unknown')} - {rm.get('quantity', 0)} {rm.get('quantity_unit', '')}")
                print(f"     From: {rm.get('source_location', 'Unknown')}")
        
        # Batch
        if chain['batch']:
            batch = chain['batch']
            print(f"\n📦 PRODUCT BATCH:")
            print(f"  ID: {batch['asset_id']}")
            print(f"  Name: {batch.get('name', 'Unknown')}")
            print(f"  Quantity: {batch.get('order_quantity', 0)} {batch.get('quantity_unit', '')}")
            print(f"  Producer: {batch.get('producer_id', 'Unknown')[:16]}...")
            print(f"  Status: {batch.get('batch_status', 'Unknown')}")
        
        # Work order
        if chain['work_order']:
            wo = chain['work_order']
            print(f"\n⚒️  WORK ORDER:")
            print(f"  ID: {wo['asset_id']}")
            print(f"  Type: {wo.get('work_type', 'Unknown')}")
            print(f"  Assignee: {wo.get('assignee_id', 'Unknown')[:16]}...")
            print(f"  Status: {wo.get('status', 'Unknown')}")
            print(f"  Est. Completion: {wo.get('estimated_completion_date', 'Unknown')}")
        
        # Products (if batch)
        if chain['products']:
            print(f"\n🏺 PRODUCTS ({len(chain['products'])}):")
            for product in chain['products']:
                print(f"  • {product['asset_id']} - Owner: {product.get('owner', 'Unknown')[:16]}...")
        
        # Warranty
        if chain['warranty']:
            warranty = chain['warranty']
            print(f"\n🛡️  WARRANTY:")
            print(f"  ID: {warranty['asset_id']}")
            print(f"  Period: {warranty.get('warranty_period_months', 'Unknown')} months")
            print(f"  Buyer: {warranty.get('buyer_id', 'Unknown')[:16]}...")
            print(f"  Status: {warranty.get('warranty_status', 'Unknown')}")
        
        print(f"{'='*80}\n")
    
    def analyze_supply_chain(self) -> Dict:
        """Analyze the complete supply chain showing relationships."""
        print("📊 Analyzing Supply Chain...")
        
        analysis = {
            'raw_materials': [],
            'batches': [],
            'work_orders': [],
            'products': [],
            'warranties': [],
            'relationships': []
        }
        
        # Get all assets
        for asset_type in self.ASSET_TYPE_PREFIXES.keys():
            assets = self.get_assets_by_type(asset_type)
            analysis[asset_type.replace('_', 's')] = assets
        
        # Analyze relationships
        relationships = []
        
        # Batch -> Raw Material relationships
        for batch in analysis['product_batches']:
            if 'raw_materials_used' in batch:
                for rm_id in batch['raw_materials_used']:
                    relationships.append({
                        'type': 'uses',
                        'from': batch['asset_id'],
                        'from_type': 'product_batch',
                        'to': rm_id,
                        'to_type': 'raw_material'
                    })
        
        # Work Order -> Batch relationships
        for wo in analysis['work_orders']:
            if 'batch_id' in wo:
                relationships.append({
                    'type': 'produces',
                    'from': wo['asset_id'],
                    'from_type': 'work_order',
                    'to': wo['batch_id'],
                    'to_type': 'product_batch'
                })
        
        # Product -> Batch relationships
        for product in analysis['products']:
            if 'batch_id' in product:
                relationships.append({
                    'type': 'created_from',
                    'from': product['asset_id'],
                    'from_type': 'product',
                    'to': product['batch_id'],
                    'to_type': 'product_batch'
                })
        
        # Warranty -> Product relationships
        for warranty in analysis['warranties']:
            if 'product_id' in warranty:
                relationships.append({
                    'type': 'covers',
                    'from': warranty['asset_id'],
                    'from_type': 'warranty',
                    'to': warranty['product_id'],
                    'to_type': 'product'
                })
        
        analysis['relationships'] = relationships
        
        # Print summary
        print(f"\n📈 Supply Chain Summary:")
        print(f"  Raw Materials: {len(analysis['raw_materials'])}")
        print(f"  Product Batches: {len(analysis['product_batches'])}")
        print(f"  Work Orders: {len(analysis['work_orders'])}")
        print(f"  Products: {len(analysis['products'])}")
        print(f"  Warranties: {len(analysis['warranties'])}")
        print(f"  Relationships: {len(relationships)}")
        
        if relationships:
            print(f"\n🔗 Key Relationships:")
            for rel in relationships[:10]:  # Show first 10
                print(f"  {rel['from']} --({rel['type']})--> {rel['to']}")
        
        return analysis


def main():
    """Main CLI for asset reading and querying."""
    if len(sys.argv) < 2:
        print("Usage: python asset_read_client.py <command> [args...]")
        print("\nCommands:")
        print("  get <asset_id> <asset_type>           - Get specific asset")
        print("  chain <asset_id> <asset_type>         - Get asset with related assets")
        print("  owner <public_key>                    - Get assets by owner")
        print("  type <asset_type>                     - Get assets by type")
        print("  search <field>=<value> ...            - Search with filters")
        print("  list [--details]                      - List all assets")
        print("  analyze                               - Analyze supply chain")
        print("\nAsset types: raw_material, product, product_batch, work_order, warranty")
        print("\nSearch fields: asset_type, owner, status, name, batch_id, certification_type")
        return
    
    client = AssetReadClient()
    command = sys.argv[1]
    
    try:
        if command == "get" and len(sys.argv) >= 4:
            asset = client.get_asset(sys.argv[2], sys.argv[3])
            if asset:
                client.print_asset(asset, show_history=True)
            else:
                print(f"Asset not found: {sys.argv[2]}")
        
        elif command == "chain" and len(sys.argv) >= 4:
            chain = client.get_asset_chain(sys.argv[2], sys.argv[3])
            client.print_asset_chain(chain)
        
        elif command == "owner" and len(sys.argv) >= 3:
            assets = client.get_assets_by_owner(sys.argv[2])
            print(f"Found {len(assets)} assets for owner {sys.argv[2][:16]}...")
            for asset in assets:
                client.print_asset(asset)
        
        elif command == "type" and len(sys.argv) >= 3:
            assets = client.get_assets_by_type(sys.argv[2])
            print(f"Found {len(assets)} {sys.argv[2]} assets:")
            for asset in assets:
                client.print_asset(asset)
        
        elif command == "search" and len(sys.argv) >= 3:
            filters = {}
            for arg in sys.argv[2:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    filters[key] = value
            
            assets = client.search_assets(filters)
            for asset in assets:
                client.print_asset(asset)
        
        elif command == "list":
            show_details = "--details" in sys.argv
            client.list_all_assets(show_details)
        
        elif command == "analyze":
            client.analyze_supply_chain()
        
        else:
            print("Invalid command or missing arguments")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
