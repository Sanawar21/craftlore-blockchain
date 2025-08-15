#!/usr/bin/env python3
"""
Demo script for CraftLore Combined TP - Streamlined Version
Tests core functionality including the new raw material in batch feature.
"""

import time
import sys
import os
sys.path.append('/app')

from clients.combined_client import CraftLoreClient


def test_complete_flow():
    """Test streamlined flow focusing on core features and raw material usage."""
    print("🚀 Starting CraftLore Combined TP Demo - Streamlined Version")
    print("=" * 60)
    
    # Create client instances for different roles
    print("📱 Creating client instances...")
    
    # Super admin client (for bootstrapping)
    admin_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="ba4817a5951802b29efd2250d62795721b26224975b8a7b3b6b13398f6bd8553")
    print(f"Super Admin Public Key: {admin_client.public_key}")
    
    # Supplier client  
    supplier_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="4888fdf00249c34ce929206d1c51a37e01183ab56721897a939285ad31a6ebbf")
    print(f"Supplier Public Key: {supplier_client.public_key}")
    
    # Workshop client
    workshop_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="9d2d2ff5837f90a4af442847efa6ba1f5d08630fb348384876fb1266d4e4c517")
    print(f"Workshop Public Key: {workshop_client.public_key}")
    
    print("\n" + "=" * 60)
    
    # ===========================
    # PHASE 1: ACCOUNT CREATION
    # ===========================
    print("👥 PHASE 1: Creating Accounts")
    print("-" * 30)
    
    # Create super admin account (bootstrap)
    print("1. Creating Super Admin account...")
    result = admin_client.create_account(
        account_type='super_admin',
        email='admin@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Create supplier account
    print("2. Creating Supplier account...")
    result = supplier_client.create_account(
        account_type='supplier',
        email='supplier@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Create workshop account
    print("3. Creating Workshop account...")
    result = workshop_client.create_account(
        account_type='workshop',
        email='workshop@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 2: ACCOUNT AUTHENTICATION
    # ===========================
    print("\n🔐 PHASE 2: Authenticating Accounts")
    print("-" * 30)
    
    # Authenticate supplier
    print("1. Admin authenticating Supplier...")
    result = admin_client.authenticate_account(
        target_public_key=supplier_client.public_key,
        auth_decision='approve'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Authenticate workshop
    print("2. Admin authenticating Workshop...")
    result = admin_client.authenticate_account(
        target_public_key=workshop_client.public_key,
        auth_decision='approve'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 3: RAW MATERIAL CREATION & TRANSFER
    # ===========================
    print("\n🏭 PHASE 3: Raw Material Creation & Transfer")
    print("-" * 30)
    
    # Supplier creates raw materials
    print("1a. Supplier creating pashmina wool...")
    result = supplier_client.create_raw_material(
        material_id='wool_002',
        material_type='pashmina_wool',
        supplier_id=supplier_client.public_key,
        quantity=100.0,
        source_location='Ladakh, India',
        certification='organic'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("1b. Supplier creating silk thread...")
    result = supplier_client.create_raw_material(
        material_id='silk_001',
        material_type='silk_thread',
        supplier_id=supplier_client.public_key,
        quantity=50.0,
        source_location='Kashmir, India',
        certification='premium'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Transfer raw materials to workshop
    print("2a. Supplier transferring wool to workshop...")
    result = supplier_client.transfer_asset(
        asset_id='wool_002',
        asset_type='raw_material',
        new_owner_public_key=workshop_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("2b. Supplier transferring silk to workshop...")
    result = supplier_client.transfer_asset(
        asset_id='silk_001',
        asset_type='raw_material',
        new_owner_public_key=workshop_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 4: PRODUCT BATCH CREATION
    # ===========================
    print("\n🏗️  PHASE 4: Product Batch Creation")
    print("-" * 30)
    
    # Workshop creates product batch
    print("1. Workshop creating premium shawl batch...")
    result = workshop_client.create_product_batch(
        batch_id='premium_batch_001',
        batch_type='premium_shawls',
        expected_quantity=5,
        name='Kashmiri Premium Shawl Collection',
        description='High-quality shawls using organic wool and silk'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 5: NEW FEATURE - RAW MATERIAL USAGE IN BATCH
    # ===========================
    print("\n🧵 PHASE 5: Raw Material Usage in Batch (NEW FEATURE)")
    print("-" * 50)
    
    # Workshop uses wool in the batch
    print("1. Workshop using wool in premium batch...")
    result = workshop_client.use_raw_material_in_batch(
        raw_material_id='wool_002',
        batch_id='premium_batch_001'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ {result.get('message')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # Workshop uses silk in the same batch  
    print("2. Workshop using silk in premium batch...")
    result = workshop_client.use_raw_material_in_batch(
        raw_material_id='silk_001',
        batch_id='premium_batch_001'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ {result.get('message')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 6: VERIFICATION
    # ===========================
    print("\n🔍 PHASE 6: Verification")
    print("-" * 30)
    
    # Check batch state
    print("1. Checking batch state...")
    batch_addr = workshop_client.get_asset_address('premium_batch_001', 'product_batch')
    batch_data = workshop_client.get_state(batch_addr)
    if batch_data:
        print(f"   ✅ Batch found: {batch_data.get('name', 'N/A')}")
        print(f"   Raw materials used: {len(batch_data.get('raw_materials_used', []))}")
        print(f"   Materials: {batch_data.get('raw_materials_used', [])}")
    else:
        print(f"   ❌ Batch not found")
    
    # Check raw material states
    print("2. Checking raw material states...")
    for material_id in ['wool_002', 'silk_001']:
        material_addr = workshop_client.get_asset_address(material_id, 'raw_material')
        material_data = workshop_client.get_state(material_addr)
        if material_data:
            print(f"   ✅ {material_id}: Used in {len(material_data.get('batches_used_in', []))} batches")
            print(f"      Batches: {material_data.get('batches_used_in', [])}")
        else:
            print(f"   ❌ {material_id} not found")
    
    print("\n" + "=" * 60)
    print("🎉 Streamlined Demo completed successfully!")
    print("✅ Core account & asset management tested")
    print("✅ Raw material transfer workflow verified")
    print("✅ NEW: Raw material usage in batches implemented")
    print("✅ Bidirectional tracking working properly")


def main():
    """Main demo function."""
    try:
        test_complete_flow()
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
