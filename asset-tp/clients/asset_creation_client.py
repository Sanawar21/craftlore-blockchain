#!/usr/bin/env python3
"""
Asset Creation Client for CraftLore Asset TP.
Handles creation of all asset types with proper validation and testing.
"""

import sys
import time
from typing import Dict, List
from datetime import datetime, timedelta
from base_client import AssetClient


class AssetCreationClient(AssetClient):
    """Client for creating various types of assets."""
    
    def create_raw_material(self, asset_id: str, material_type: str, supplier_id: str, 
                          quantity: float, quantity_unit: str, source_location: str,
                          harvested_date: str = None, **kwargs) -> Dict:
        """Create a raw material asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': 'raw_material',
            'material_type': material_type,
            'supplier_id': supplier_id,
            'quantity': quantity,
            'quantity_unit': quantity_unit,
            'source_location': source_location,
            'harvested_date': harvested_date or datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        print(f"Creating raw material: {asset_id}")
        result = self.submit_transaction('create_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Raw material created successfully: {asset_id}")
            asset = self.get_asset(asset_id, 'raw_material')
            if asset:
                self.print_asset(asset)
        else:
            print(f"❌ Failed to create raw material: {result}")
        
        return result
    
    def create_product_batch(self, asset_id: str, name: str, description: str,
                           raw_materials_used: List[str], order_quantity: int,
                           quantity_unit: str, producer_id: str, category: str,
                           work_order_id: str = None, **kwargs) -> Dict:
        """Create a product batch asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': 'product_batch',
            'name': name,
            'description': description,
            'raw_materials_used': raw_materials_used,
            'order_quantity': order_quantity,
            'quantity_unit': quantity_unit,
            'producer_id': producer_id,
            'category': category,
            'work_order_id': work_order_id or f"WO_{asset_id}",
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        print(f"Creating product batch: {asset_id}")
        result = self.submit_transaction('create_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Product batch created successfully: {asset_id}")
            asset = self.get_asset(asset_id, 'product_batch')
            if asset:
                self.print_asset(asset)
        else:
            print(f"❌ Failed to create product batch: {result}")
        
        return result
    
    def create_work_order(self, asset_id: str, batch_id: str, assignee_id: str,
                         work_type: str = 'production', estimated_completion_date: str = None,
                         **kwargs) -> Dict:
        """Create a work order asset."""
        completion_date = estimated_completion_date or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            'asset_id': asset_id,
            'asset_type': 'work_order',
            'batch_id': batch_id,
            'assignee_id': assignee_id,
            'work_type': work_type,
            'estimated_completion_date': completion_date,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        print(f"Creating work order: {asset_id}")
        result = self.submit_transaction('create_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Work order created successfully: {asset_id}")
            asset = self.get_asset(asset_id, 'work_order')
            if asset:
                self.print_asset(asset)
        else:
            print(f"❌ Failed to create work order: {result}")
        
        return result
    
    def create_product(self, asset_id: str, batch_id: str, batch_index: int = 0, **kwargs) -> Dict:
        """Create a standalone product asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': 'product',
            'batch_id': batch_id,
            'batch_index': batch_index,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        print(f"Creating product: {asset_id}")
        result = self.submit_transaction('create_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Product created successfully: {asset_id}")
            asset = self.get_asset(asset_id, 'product')
            if asset:
                self.print_asset(asset)
        else:
            print(f"❌ Failed to create product: {result}")
        
        return result
    
    def create_warranty(self, asset_id: str, product_id: str, buyer_id: str,
                       warranty_period_months: int = 12, warranty_terms: str = None,
                       **kwargs) -> Dict:
        """Create a warranty asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': 'warranty',
            'product_id': product_id,
            'buyer_id': buyer_id,
            'warranty_period_months': warranty_period_months,
            'warranty_terms': warranty_terms or "Standard warranty terms apply",
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        print(f"Creating warranty: {asset_id}")
        result = self.submit_transaction('create_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Warranty created successfully: {asset_id}")
            asset = self.get_asset(asset_id, 'warranty')
            if asset:
                self.print_asset(asset)
        else:
            print(f"❌ Failed to create warranty: {result}")
        
        return result
    
    def create_products_from_batch(self, batch_id: str, product_count: int, buyer_public_key: str) -> Dict:
        """Create multiple products from a batch."""
        data = {
            'batch_id': batch_id,
            'product_count': product_count,
            'buyer_public_key': buyer_public_key,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"Creating {product_count} products from batch: {batch_id}")
        result = self.submit_transaction('create_products_from_batch', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Products created from batch successfully")
            # Try to get the updated batch
            batch = self.get_asset(batch_id, 'product_batch')
            if batch:
                print(f"Updated batch info:")
                self.print_asset(batch)
        else:
            print(f"❌ Failed to create products from batch: {result}")
        
        return result


def main():
    """Main CLI for asset creation testing."""
    if len(sys.argv) < 2:
        print("Usage: python asset_creation_client.py <command> [args...]")
        print("\nCommands:")
        print("  raw_material <id> <type> <supplier_id> <quantity> <unit> <location>")
        print("  product_batch <id> <name> <description> <quantity> <unit> <producer_id> <category>")
        print("  work_order <id> <batch_id> <assignee_id> [work_type]")
        print("  product <id> <batch_id> [batch_index]")
        print("  warranty <id> <product_id> <buyer_id> [period_months]")
        print("  products_from_batch <batch_id> <count> <buyer_key>")
        print("  demo - Run a complete demo scenario")
        return
    
    client = AssetCreationClient(private_key_hex="ee038ca8e172149eb12eac2225ceaebf2e020e6683905684a5763ae1a044789d")
    command = sys.argv[1]
    
    try:
        if command == "raw_material" and len(sys.argv) >= 8:
            client.create_raw_material(
                asset_id=sys.argv[2],
                material_type=sys.argv[3],
                supplier_id=sys.argv[4],
                quantity=float(sys.argv[5]),
                quantity_unit=sys.argv[6],
                source_location=sys.argv[7]
            )
        
        elif command == "product_batch" and len(sys.argv) >= 9:
            client.create_product_batch(
                asset_id=sys.argv[2],
                name=sys.argv[3],
                description=sys.argv[4],
                raw_materials_used=[sys.argv[2].replace('BATCH', 'RM')],  # Simple derivation
                order_quantity=int(sys.argv[5]),
                quantity_unit=sys.argv[6],
                producer_id=sys.argv[7],
                category=sys.argv[8]
            )
        
        elif command == "work_order" and len(sys.argv) >= 5:
            work_type = sys.argv[5] if len(sys.argv) > 5 else 'production'
            client.create_work_order(
                asset_id=sys.argv[2],
                batch_id=sys.argv[3],
                assignee_id=sys.argv[4],
                work_type=work_type
            )
        
        elif command == "product" and len(sys.argv) >= 4:
            batch_index = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            client.create_product(
                asset_id=sys.argv[2],
                batch_id=sys.argv[3],
                batch_index=batch_index
            )
        
        elif command == "warranty" and len(sys.argv) >= 5:
            period = int(sys.argv[5]) if len(sys.argv) > 5 else 12
            client.create_warranty(
                asset_id=sys.argv[2],
                product_id=sys.argv[3],
                buyer_id=sys.argv[4],
                warranty_period_months=period
            )
        
        elif command == "products_from_batch" and len(sys.argv) >= 5:
            client.create_products_from_batch(
                batch_id=sys.argv[2],
                product_count=int(sys.argv[3]),
                buyer_public_key=sys.argv[4]
            )
        
        elif command == "demo":
            run_demo(client)
        
        else:
            print("Invalid command or missing arguments")
    
    except Exception as e:
        print(f"Error: {e}")


def run_demo(client: AssetCreationClient):
    """Run a complete demonstration of asset creation flow."""
    print("🎯 Starting CraftLore Asset Creation Demo")
    print("=" * 50)
    
    # Step 1: Create raw material
    print("\n1️⃣  Creating Raw Material...")
    client.create_raw_material(
        asset_id="RM_PASHMINA_WOOL_001",
        material_type="pashmina_wool",
        supplier_id=client.public_key[:16],
        quantity=10.5,
        quantity_unit="kg",
        source_location="Ladakh, Kashmir"
    )
    
    time.sleep(2)
    
    # # Step 2: Create product batch
    # print("\n2️⃣  Creating Product Batch...")
    # client.create_product_batch(
    #     asset_id="BATCH_KANI_SHAWL_001",
    #     name="Kani Pashmina Shawls",
    #     description="Traditional Kani weave pashmina shawls with intricate patterns",
    #     raw_materials_used=["RM_PASHMINA_WOOL_001"],
    #     order_quantity=5,
    #     quantity_unit="pieces",
    #     producer_id=client.public_key[:16],
    #     category="luxury_textiles"
    # )
    
    # time.sleep(2)
    
    # # Step 3: Create work order
    # print("\n3️⃣  Creating Work Order...")
    # client.create_work_order(
    #     asset_id="WO_KANI_001",
    #     batch_id="BATCH_KANI_SHAWL_001",
    #     assignee_id=client.public_key[:16],
    #     work_type="kani_weaving"
    # )
    
    # time.sleep(2)
    
    # # Step 4: Create individual product
    # print("\n4️⃣  Creating Individual Product...")
    # client.create_product(
    #     asset_id="PRODUCT_KANI_001",
    #     batch_id="BATCH_KANI_SHAWL_001",
    #     batch_index=1
    # )
    
    # time.sleep(2)
    
    # # Step 5: Create warranty
    # print("\n5️⃣  Creating Warranty...")
    # client.create_warranty(
    #     asset_id="WARRANTY_KANI_001",
    #     product_id="PRODUCT_KANI_001",
    #     buyer_id=client.public_key[:16],
    #     warranty_period_months=24,
    #     warranty_terms="2-year warranty against manufacturing defects"
    # )
    
    # print("\n🎉 Demo completed successfully!")
    # print("=" * 50)
    
    # # Show summary
    # print("\n📊 Demo Summary:")
    # assets_created = [
    #     ("Raw Material", "RM_PASHMINA_WOOL_001", "raw_material"),
    #     ("Product Batch", "BATCH_KANI_SHAWL_001", "product_batch"),
    #     ("Work Order", "WO_KANI_001", "work_order"),
    #     ("Product", "PRODUCT_KANI_001", "product"),
    #     ("Warranty", "WARRANTY_KANI_001", "warranty")
    # ]
    
    # for name, asset_id, asset_type in assets_created:
    #     asset = client.get_asset(asset_id, asset_type)
    #     status = "✅ Created" if asset else "❌ Failed"
    #     print(f"  {name}: {asset_id} - {status}")


if __name__ == "__main__":
    main()
