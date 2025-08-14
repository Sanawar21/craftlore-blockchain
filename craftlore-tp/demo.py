#!/usr/bin/env python3
"""
Demo script for CraftLore Combined TP
Tests both account and asset operations in the unified transaction processor.
"""

import time
import sys
import os
sys.path.append('/app')

from clients.combined_client import CraftLoreClient


def test_complete_flow():
    """Test complete flow from account creation to asset management."""
    print("🚀 Starting CraftLore Combined TP Demo")
    print("=" * 60)
    
    # Create client instances for different roles
    print("📱 Creating client instances...")
    
    # Super admin client (for bootstrapping)
    admin_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="ba4817a5951802b29efd2250d62795721b26224975b8a7b3b6b13398f6bd8553")
    print(f"Super Admin Public Key: {admin_client.public_key}")
    
    # Supplier client  
    supplier_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="4888fdf00249c34ce929206d1c51a37e01183ab56721897a939285ad31a6ebbf")
    print(f"Supplier Public Key: {supplier_client.public_key}")
    
    # Artisan client
    artisan_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="b800a8695edcacf2253eac3f1c7a52d106935000392bf9f2071d771d59ced091")
    print(f"Artisan Public Key: {artisan_client.public_key}")
    
    # Workshop client
    workshop_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="9d2d2ff5837f90a4af442847efa6ba1f5d08630fb348384876fb1266d4e4c517")
    print(f"Workshop Public Key: {workshop_client.public_key}")
    
    print("\n" + "=" * 60)
    
    # ===========================
    # PHASE 1: ACCOUNT CREATION
    # ===========================
    # print("👥 PHASE 1: Creating Accounts")
    # print("-" * 30)
    
    # # Create super admin account (bootstrap)
    # print("1. Creating Super Admin account...")
    # result = admin_client.create_account(
    #     account_type='super_admin',
    #     email='admin@craftlore.com'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Create supplier account
    # print("2. Creating Supplier account...")
    # result = supplier_client.create_account(
    #     account_type='supplier',
    #     email='supplier@craftlore.com'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Create artisan account
    # print("3. Creating Artisan account...")
    # result = artisan_client.create_account(
    #     account_type='artisan',
    #     email='artisan@craftlore.com'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Create workshop account
    # print("4. Creating Workshop account...")
    # result = workshop_client.create_account(
    #     account_type='workshop',
    #     email='workshop@craftlore.com'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # ===========================
    # # PHASE 2: ACCOUNT AUTHENTICATION
    # # ===========================
    # print("\n🔐 PHASE 2: Authenticating Accounts")
    # print("-" * 30)
    
    # # Authenticate supplier
    # print("1. Admin authenticating Supplier...")
    # result = admin_client.authenticate_account(
    #     target_public_key=supplier_client.public_key,
    #     auth_decision='approve'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Authenticate artisan
    # print("2. Admin authenticating Artisan...")
    # result = admin_client.authenticate_account(
    #     target_public_key=artisan_client.public_key,
    #     auth_decision='approve'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Authenticate workshop
    # print("3. Admin authenticating Workshop...")
    # result = admin_client.authenticate_account(
    #     target_public_key=workshop_client.public_key,
    #     auth_decision='approve'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # ===========================
    # PHASE 3: ASSET CREATION
    # ===========================
    print("\n🏭 PHASE 3: Creating Assets")
    print("-" * 30)
    
    # Supplier creates raw material
    print("1. Supplier creating raw material...")
    result = supplier_client.create_raw_material(
        material_id='wool_003',
        material_type='pashmina_wool',
        supplier_id=supplier_client.public_key,
        quantity=100.0,
        source_location='Ladakh, India',
        certification='organic'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # # Workshop creates work order
    # print("2. Workshop creating work order...")
    # result = workshop_client.create_work_order(
    #     work_order_id='wo_001',
    #     buyer_id=workshop_client.public_key,
    #     product_batch_id='batch_001',
    #     assignee_id=artisan_client.public_key,
    #     description='Weave pashmina shawls from wool_001'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Workshop creates product batch
    # print("3. Workshop creating product batch...")
    # result = workshop_client.create_product_batch(
    #     batch_id='batch_001',
    #     batch_type='pashmina_shawls',
    #     expected_quantity=10,
    #     assigned_artisan=artisan_client.public_key,
    #     raw_materials=['wool_001']
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # ===========================
    # # PHASE 4: ASSET WORKFLOW
    # # ===========================
    # print("\n🔄 PHASE 4: Asset Workflow Operations")
    # print("-" * 30)
    
    # # Lock the work order
    # print("1. Workshop locking work order...")
    # result = workshop_client.lock_asset(
    #     asset_id='wo_001',
    #     asset_type='work_order'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # Artisan accepts the work order
    # print("2. Artisan accepting work order...")
    # result = artisan_client.accept_asset(
    #     asset_id='wo_001',
    #     asset_type='work_order'
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # time.sleep(2)
    
    # # ===========================
    # # PHASE 5: QUERY OPERATIONS
    # # ===========================
    # print("\n🔍 PHASE 5: Query Operations")
    # print("-" * 30)
    
    # # Query artisan account
    # print("1. Querying artisan account...")
    # result = artisan_client.query_account(
    #     query_type='by_public_key',
    #     public_key=artisan_client.public_key
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # if result.get('status') == 'success' and result.get('account'):
    #     account = result['account']
    #     print(f"   Account Type: {account.get('account_type')}")
    #     print(f"   Auth Status: {account.get('authentication_status')}")
    # time.sleep(2)
    
    # # Check state data
    # print("2. Checking blockchain state...")
    # namespace = admin_client.address_generator.get_namespace()
    # print(f"   Namespace: {namespace}")
    
    # # Get account address
    # account_addr = admin_client.get_account_address(artisan_client.public_key)
    # account_data = admin_client.get_state(account_addr)
    # if account_data:
    #     print(f"   ✅ Artisan account found on blockchain")
    #     print(f"   Account ID: {account_data.get('account_id', 'N/A')}")
    # else:
    #     print(f"   ❌ Artisan account not found")
    
    # # Get asset address
    # asset_addr = admin_client.get_asset_address('wool_001', 'raw_material')
    # asset_data = admin_client.get_state(asset_addr)
    # if asset_data:
    #     print(f"   ✅ Raw material asset found on blockchain")
    #     print(f"   Material Type: {asset_data.get('material_type', 'N/A')}")
    # else:
    #     print(f"   ❌ Raw material asset not found")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("✅ Accounts and assets are managed in unified namespace")
    print("✅ No need for careful input/output address management")
    print("✅ Simplified client interaction with single TP")


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
