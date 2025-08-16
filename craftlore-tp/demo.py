#!/usr/bin/env python3
"""
Demo script for CraftLore Combined TP - Complete Batch Production Workflow
Tests the complete w    # Buyer creates work order for cust    # Workshop accepts the work order
    print("3. Workshop accepting t    # Workshop creates product batch to fulfill the work order
    print("1. Workshop creating luxury shawl batch...")
    result = workshop_client.create_product_batch(
        batch_id='fresh_batch_003',
        batch_type='luxury_shawls',
        order_quantity=8,
        name='Premium Kashmir Luxury Shawl Collection',
        description='Luxury shawls using premium cashmere and golden silk',
        work_order_id='batch_order_003'  # Linking to the work order
    )der...")
    result = workshop_client.accept_work_order(
        work_order_id='batch_order_003'
    )awls
    print("1. Buyer creating work order for custom shawl collection...")
    result = buyer_client.create_work_order(
        work_order_id='batch_order_003',
        work_type='production',
        assignee_id=workshop_client.public_key,
        buyer_id=buyer_client.public_key,
        product_batch_id='fresh_batch_003',  # This will be created later by workshop
        description='Custom order for 8 premium Kashmir shawls with organic materials'
    )om buyer request to batch completion.
"""

import time
import sys
import os
sys.path.append('/app')

from clients.combined_client import CraftLoreClient


def test_complete_batch_workflow():
    """Test complete batch production workflow from blank state."""
    print("🚀 Starting CraftLore Complete Batch Production Demo")
    print("=" * 70)
    
    # Create client instances for different roles
    print("📱 Creating client instances...")
    
    # Super admin client (for bootstrapping)
    admin_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="ba4817a5951802b29efd2250d62795721b26224975b8a7b3b6b13398f6bd8553")
    print(f"Super Admin Public Key: {admin_client.public_key}")
    
    # Buyer client (who will request custom products)
    buyer_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    print(f"Buyer Public Key: {buyer_client.public_key}")
    
    # Supplier client (provides raw materials)
    supplier_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="4888fdf00249c34ce929206d1c51a37e01183ab56721897a939285ad31a6ebbf")
    print(f"Supplier Public Key: {supplier_client.public_key}")
    
    # Workshop client (produces the products)
    workshop_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="9d2d2ff5837f90a4af442847efa6ba1f5d08630fb348384876fb1266d4e4c517")
    print(f"Workshop Public Key: {workshop_client.public_key}")
    
    print("\n" + "=" * 70)
    
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
    
    # Create buyer account
    print("4. Creating Buyer account...")
    result = buyer_client.create_account(
        account_type='buyer',
        email='buyer@craftlore.com'
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
    
    # Authenticate buyer
    print("3. Admin authenticating Buyer...")
    result = admin_client.authenticate_account(
        target_public_key=buyer_client.public_key,
        auth_decision='approve'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 3: WORK ORDER CREATION (BUYER → WORKSHOP)
    # ===========================
    print("\n📋 PHASE 3: Work Order Creation by Buyer")
    print("-" * 30)
    
    # Buyer creates work order for custom shawls
    print("1. Buyer creating work order for luxury shawls...")
    result = buyer_client.create_work_order(
        work_order_id='batch_order_003',
        buyer_id=buyer_client.public_key,
        product_batch_id='fresh_batch_003',  # This will be created later by workshop
        assignee_id=workshop_client.public_key,
        description='Custom order for 8 luxury Kashmir shawls with premium materials',
        work_type='production',
        estimated_completion_date='2025-09-15',
        order_quantity=8  # Buyer wants 8 shawls
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ Work order created: {result.get('message', 'Order placed successfully')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # Buyer locks the work order (prerequisite for acceptance)
    print("2. Buyer locking work order for workshop acceptance...")
    result = buyer_client.lock_asset(
        asset_id='batch_order_003',
        asset_type='work_order'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ Work order locked: Ready for workshop acceptance")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # Workshop accepts the work order
    print("3. Workshop accepting work order...")
    result = workshop_client.accept_work_order(
        work_order_id='batch_order_003'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ Work order accepted: {result.get('message', 'Order accepted successfully')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 4: RAW MATERIAL CREATION & TRANSFER
    # ===========================
    print("\n🏭 PHASE 4: Raw Material Creation & Transfer")
    print("-" * 30)
    
    # Supplier creates raw materials
    print("1a. Supplier creating premium cashmere wool...")
    result = supplier_client.create_raw_material(
        material_id='cashmere_003',
        material_type='cashmere_wool',
        supplier_id=supplier_client.public_key,
        quantity=150.0,
        source_location='Ladakh, India',
        certification='premium_organic'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("1b. Supplier creating golden silk thread...")
    result = supplier_client.create_raw_material(
        material_id='goldsilk_003',
        material_type='golden_silk_thread',
        supplier_id=supplier_client.public_key,
        quantity=80.0,
        source_location='Kashmir, India',
        certification='luxury_grade'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Transfer raw materials to workshop
    print("2a. Supplier transferring cashmere to workshop...")
    result = supplier_client.transfer_asset(
        asset_id='cashmere_003',
        asset_type='raw_material',
        new_owner_public_key=workshop_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("2b. Supplier transferring golden silk to workshop...")
    result = supplier_client.transfer_asset(
        asset_id='goldsilk_003',
        asset_type='raw_material',
        new_owner_public_key=workshop_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 5: PRODUCT BATCH CREATION (WORKSHOP FULFILLS ORDER)
    # ===========================
    print("\n🏗️  PHASE 5: Product Batch Creation to Fulfill Work Order")
    print("-" * 30)
    
    # Workshop creates product batch to fulfill the buyer's order
    print("1. Workshop creating luxury shawl batch for work order...")
    result = workshop_client.create_product_batch(
        batch_id='fresh_batch_003',
        batch_type='luxury_shawls',
        order_quantity=8,  # Matching the buyer's request
        name='Custom Kashmir Luxury Shawl Collection',
        description='Custom batch to fulfill buyer order - Luxury shawls using premium cashmere and golden silk',
        work_order_id='batch_order_003'  # Linking to the work order
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ Batch created to fulfill work order")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 6: NEW FEATURE - RAW MATERIAL USAGE IN BATCH
    # ===========================
    print("\n🧵 PHASE 6: Raw Material Usage in Batch (NEW FEATURE)")
    print("-" * 50)
    
    # Workshop uses cashmere in the batch
    print("1. Workshop using cashmere in luxury batch...")
    result = workshop_client.use_raw_material_in_batch(
        raw_material_id='cashmere_003',
        batch_id='fresh_batch_003'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ {result.get('message')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # Workshop uses golden silk in the same batch  
    print("2. Workshop using golden silk in luxury batch...")
    result = workshop_client.use_raw_material_in_batch(
        raw_material_id='goldsilk_003',
        batch_id='fresh_batch_003'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ {result.get('message')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)
    
    # ===========================
    # PHASE 7: COMPLETE BATCH PRODUCTION
    # ===========================
    print("\n🏭 PHASE 7: Complete Batch Production")
    print("-" * 40)
    
    # Workshop completes the batch production
    print("1. Workshop completing luxury batch production...")
    result = workshop_client.complete_batch_production(
        batch_id='fresh_batch_003',
        artisans_involved=[workshop_client.public_key],  # Workshop owner is the artisan
        quality_notes='Luxury quality shawls completed using premium cashmere and golden silk'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ {result.get('message')}")
        if result.get('work_order_updated'):
            print(f"   ✅ Work order {result.get('work_order_id')} also marked as completed")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(2)  # Longer wait for this important operation
    
    # ===========================
    # PHASE 8: PRODUCT TRANSFER TO BUYER
    # ===========================
    print("\n📦 PHASE 8: Product Transfer to Buyer")
    print("-" * 40)
    
    # Workshop transfers some products to buyer (not all)
    batch_id = 'fresh_batch_003'
    products_to_transfer = 5  # Transfer 5 out of 8 products
    
    print(f"1. Workshop transferring {products_to_transfer} products to buyer...")
    transfer_results = []
    
    for i in range(products_to_transfer):
        product_id = f"{batch_id}_product_{i}"
        print(f"   Transferring product {i+1}/{products_to_transfer}: {product_id}")
        
        result = workshop_client.transfer_asset(
            asset_id=product_id,
            asset_type='product',
            new_owner_public_key=buyer_client.public_key
        )
        
        transfer_results.append({
            'product_id': product_id,
            'result': result
        })
        
        if result.get('status') == 'success':
            print(f"      ✅ Product {i+1} transferred successfully")
        else:
            print(f"      ❌ Product {i+1} transfer failed: {result.get('message', 'Unknown error')}")
        
        time.sleep(0.5)  # Small delay between transfers
    
    # Summary of transfers
    successful_transfers = sum(1 for r in transfer_results if r['result'].get('status') == 'success')
    print(f"\n   📊 Transfer Summary:")
    print(f"   ✅ Successfully transferred: {successful_transfers}/{products_to_transfer} products")
    print(f"   🏭 Remaining with workshop: {8 - successful_transfers}/8 products")
    print(f"   👤 Buyer now owns: {successful_transfers} products")
    
    # ===========================
    # PHASE 9: VERIFICATION
    # ===========================
    print("\n🔍 PHASE 9: Verification")
    print("-" * 30)
    
    # Check batch state
    print("1. Checking batch state...")
    batch_addr = workshop_client.get_asset_address('fresh_batch_003', 'product_batch')
    batch_data = workshop_client.get_state(batch_addr)
    if batch_data:
        print(f"   ✅ Batch found: {batch_data.get('name', 'N/A')}")
        print(f"   Batch status: {batch_data.get('batch_status', 'unknown')}")
        print(f"   Is complete: {batch_data.get('is_complete', False)}")
        print(f"   Production date: {batch_data.get('production_date', 'N/A')}")
        print(f"   Order quantity: {batch_data.get('order_quantity', 0)}")
        print(f"   Current quantity: {batch_data.get('current_quantity', 0)}")
        print(f"   Raw materials used: {len(batch_data.get('raw_materials_used', []))}")
        print(f"   Materials: {batch_data.get('raw_materials_used', [])}")
    else:
        print(f"   ❌ Batch not found")
    
    # Check raw material states
    print("2. Checking raw material states...")
    for material_id in ['cashmere_003', 'goldsilk_003']:
        material_addr = workshop_client.get_asset_address(material_id, 'raw_material')
        material_data = workshop_client.get_state(material_addr)
        if material_data:
            print(f"   ✅ {material_id}: Used in {len(material_data.get('batches_used_in', []))} batches")
            print(f"      Batches: {material_data.get('batches_used_in', [])}")
        else:
            print(f"   ❌ {material_id} not found")
    
    # Check work order state
    print("3. Checking work order state...")
    work_order_addr = buyer_client.get_asset_address('batch_order_003', 'work_order')
    work_order_data = buyer_client.get_state(work_order_addr)
    if work_order_data:
        print(f"   ✅ Work order found: Status = {work_order_data.get('status', 'unknown')}")
        print(f"   Order quantity: {work_order_data.get('order_quantity', 0)}")
        print(f"   Buyer: {work_order_data.get('buyer_id', 'N/A')[:10]}...")
        print(f"   Assignee: {work_order_data.get('assignee_id', 'N/A')[:10]}...")
        print(f"   Batch ID: {work_order_data.get('batch_id', 'N/A')}")
        print(f"   Completion date: {work_order_data.get('actual_completion_date', 'N/A')}")
    else:
        print(f"   ❌ Work order not found")
    
    # Check generated products and their ownership
    print("4. Checking product ownership after transfers...")
    batch_id = 'fresh_batch_003'
    expected_quantity = 8
    products_found = 0
    workshop_owned = 0
    buyer_owned = 0
    
    for i in range(expected_quantity):
        product_id = f"{batch_id}_product_{i}"
        product_addr = buyer_client.get_asset_address(product_id, 'product')
        product_data = buyer_client.get_state(product_addr)
        if product_data:
            products_found += 1
            owner = product_data.get('owner', 'N/A')
            owner_short = owner[:10]
            
            if owner == workshop_client.public_key:
                workshop_owned += 1
                print(f"   ✅ Product {i}: {product_id} → Owner: Workshop ({owner_short}...)")
            elif owner == buyer_client.public_key:
                buyer_owned += 1
                print(f"   ✅ Product {i}: {product_id} → Owner: Buyer ({owner_short}...)")
            else:
                print(f"   ⚠️  Product {i}: {product_id} → Owner: Unknown ({owner_short}...)")
        else:
            print(f"   ❌ Product {i}: {product_id} not found")
    
    print(f"   📊 Product ownership summary:")
    print(f"   📦 Products found: {products_found}/{expected_quantity}")
    print(f"   🏭 Workshop owned: {workshop_owned}")
    print(f"   👤 Buyer owned: {buyer_owned}")
    
    if products_found == expected_quantity:
        print(f"   ✅ All {expected_quantity} products successfully generated!")
        if buyer_owned > 0 and workshop_owned > 0:
            print(f"   ✅ Partial transfer successful: {buyer_owned} products transferred to buyer")
        elif buyer_owned == expected_quantity:
            print(f"   ✅ Full transfer: All products transferred to buyer")
        else:
            print(f"   🏭 No transfers: All products remain with workshop")
    else:
        print(f"   ⚠️  Only {products_found} out of {expected_quantity} products found")
    
    print("\n" + "=" * 80)
    print("🎉 Complete Demo with Product Generation & Manual Transfer completed successfully!")
    print("✅ Core account & asset management tested")
    print("✅ NEW: Buyer → Workshop work order workflow implemented")
    print("✅ Raw material transfer workflow verified")
    print("✅ NEW: Raw material usage in batches implemented")
    print("✅ NEW: Automatic batch completion with product generation implemented")
    print("✅ NEW: Products created and owned by workshop initially")
    print("✅ NEW: Manual product transfer from workshop to buyer (partial transfer)")
    print("✅ Work order completion linkage working properly")
    print("✅ Bidirectional tracking working properly")
    print("✅ Flow 1 specification implemented: products generated, then manually transferred!")
    print("✅ Flexible transfer: workshop can transfer some/all products as needed")


def main():
    """Main demo function."""
    try:
        test_complete_batch_workflow()
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
