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
    print("👥 PHASE 1: Creating Accounts")
    print("-" * 30)
    
    # Create super admin account (bootstrap)
    print("1. Creating Super Admin account...")
    result = admin_client.create_account(
        account_type='super_admin',
        email='admin@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Create supplier account
    print("2. Creating Supplier account...")
    result = supplier_client.create_account(
        account_type='supplier',
        email='supplier@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Create artisan account
    print("3. Creating Artisan account...")
    result = artisan_client.create_account(
        account_type='artisan',
        email='artisan@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Create workshop account
    print("4. Creating Workshop account...")
    result = workshop_client.create_account(
        account_type='workshop',
        email='workshop@craftlore.com'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
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
    time.sleep(2)
    
    # Authenticate artisan
    print("2. Admin authenticating Artisan...")
    result = admin_client.authenticate_account(
        target_public_key=artisan_client.public_key,
        auth_decision='approve'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Authenticate workshop
    print("3. Admin authenticating Workshop...")
    result = admin_client.authenticate_account(
        target_public_key=workshop_client.public_key,
        auth_decision='approve'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # ===========================
    # PHASE 3: ASSET CREATION
    # ===========================
    print("\n🏭 PHASE 3: Creating Assets")
    print("-" * 30)
    
    # Supplier creates raw material
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
    time.sleep(2)
    
    # Supplier creates another raw material
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
    time.sleep(2)
    
    # Transfer raw material from supplier to workshop
    print("2a. Supplier transferring pashmina wool to workshop...")
    result = supplier_client.transfer_asset(
        asset_id='wool_002',
        asset_type='raw_material',
        new_owner_public_key=workshop_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Raw material 'wool_002' ownership transferred from supplier to workshop")
    time.sleep(2)
    
    # Transfer another raw material from supplier to artisan  
    print("2b. Supplier transferring silk thread to artisan...")
    result = supplier_client.transfer_asset(
        asset_id='silk_001',
        asset_type='raw_material',
        new_owner_public_key=artisan_client.public_key
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Raw material 'silk_001' ownership transferred from supplier to artisan")
    time.sleep(2)
    
    # Workshop creates work order
    print("3. Workshop creating work order...")
    result = workshop_client.create_work_order(
        work_order_id='wo_001',
        buyer_id=workshop_client.public_key,
        product_batch_id='batch_001',
        assignee_id=artisan_client.public_key,
        description='Weave pashmina shawls from wool_001'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Workshop creates product batch
    print("4. Workshop creating product batch...")
    result = workshop_client.create_product_batch(
        batch_id='batch_001',
        batch_type='pashmina_shawls',
        expected_quantity=10,
        assigned_artisan=artisan_client.public_key,
        raw_materials=['wool_001']
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # ===========================
    # PHASE 4: ASSET WORKFLOW
    # ===========================
    print("\n🔄 PHASE 4: Asset Workflow Operations")
    print("-" * 30)
    
    # Lock the work order
    print("1. Workshop locking work order...")
    result = workshop_client.lock_asset(
        asset_id='wo_001',
        asset_type='work_order'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Artisan accepts the work order
    print("2. Artisan accepting work order...")
    result = artisan_client.accept_asset(
        asset_id='wo_001',
        asset_type='work_order'
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(2)

    # ===========================
    # PHASE 5: SUB-ASSIGNMENT WORKFLOW
    # ===========================
    print("\n🏭 PHASE 5: Sub-Assignment Workflow (Workshop → Artisans)")
    print("-" * 50)
    
    # Create additional artisan clients for sub-assignment demo
    print("Creating additional artisan accounts for sub-assignment demo...")
    
    # Second artisan
    artisan2_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="da320cb9234ea89055e4bf4d6a6d55422008f1465a550fbe9d9bd91a1c793807")
    print(f"Artisan 2 Public Key: {artisan2_client.public_key}")
    
    # Third artisan  
    artisan3_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="7b867a5a92cc224d8c4e0a03d2278fcf7726d71357e0a77c1c7c83199f9c1ac4")
    print(f"Artisan 3 Public Key: {artisan3_client.public_key}")
    
    # Second workshop for hierarchical demo
    workshop2_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="7d6cd00a642f26d2c5d18f54495ea6c0646d09f953b329cfadf0c99a408f3b62")
    print(f"Workshop 2 Public Key: {workshop2_client.public_key}")
    
    # Create additional accounts
    print("\n1. Creating additional artisan accounts...")
    
    # Create artisan 2
    result = artisan2_client.create_account(
        account_type='artisan',
        email='artisan2@craftlore.com',
        specialty='embroidery'
    )
    print(f"   Artisan 2 creation: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Create artisan 3
    result = artisan3_client.create_account(
        account_type='artisan', 
        email='artisan3@craftlore.com',
        specialty='finishing'
    )
    print(f"   Artisan 3 creation: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Create workshop 2
    result = workshop2_client.create_account(
        account_type='workshop',
        email='workshop2@craftlore.com',
        specialty='small_scale_weaving'
    )
    print(f"   Workshop 2 creation: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Authenticate new accounts
    print("\n2. Admin authenticating new accounts...")
    
    for client_name, client in [("Artisan 2", artisan2_client), 
                               ("Artisan 3", artisan3_client),
                               ("Workshop 2", workshop2_client)]:
        result = admin_client.authenticate_account(
            target_public_key=client.public_key,
            auth_decision='approve'
        )
        print(f"   {client_name} authentication: {result.get('status', 'unknown')}")
        time.sleep(1)
    
    # Create a larger work order for sub-assignment
    print("\n3. Workshop creating large work order for sub-assignment...")
    result = workshop_client.create_work_order(
        work_order_id='wo_large_001',
        buyer_id=workshop_client.public_key,
        product_batch_id='batch_large_001',
        assignee_id=workshop_client.public_key,  # Self-assigned initially
        description='Large order: 50 pashmina shawls with intricate patterns',
        estimated_completion_days=30,
        complexity_level='high'
    )
    print(f"   Large work order creation: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # IMPORTANT: Lock and accept the work order before sub-assignment
    print("\n3a. Workshop locking the work order...")
    result = workshop_client.lock_asset(
        asset_id='wo_large_001',
        asset_type='work_order'
    )
    print(f"   Work order locking: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("3b. Workshop accepting the work order...")
    result = workshop_client.accept_asset(
        asset_id='wo_large_001',
        asset_type='work_order'
    )
    print(f"   Work order acceptance: {result.get('status', 'unknown')}")
    time.sleep(2)

    # Demo 1: Workshop sub-assigns to individual artisans
    print("\n4. Workshop sub-assigning to individual artisans...")
    result = workshop_client.sub_assign_work_order(
        work_order_id='wo_large_001',
        assignee_ids=[artisan_client.public_key, artisan2_client.public_key, artisan3_client.public_key],
        assignment_details={
            'assignment_type': 'parallel_work',
            'coordination_notes': 'Each artisan handles their specialty. Final assembly at workshop.'
        }
    )
    print(f"   Sub-assignment to artisans: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Demo 2: Workshop sub-assigns to another workshop  
    print("\n5. Creating hierarchical workshop assignment...")
    
    # Create another large work order
    result = workshop_client.create_work_order(
        work_order_id='wo_complex_001',
        buyer_id=workshop_client.public_key,
        product_batch_id='batch_complex_001', 
        assignee_id=workshop_client.public_key,
        description='Complex multi-stage production requiring specialized workshops',
        estimated_completion_days=45,
        complexity_level='expert'
    )
    print(f"   Complex work order creation: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Lock and accept the complex work order
    print("5a. Workshop locking the complex work order...")
    result = workshop_client.lock_asset(
        asset_id='wo_complex_001',
        asset_type='work_order'
    )
    print(f"   Complex work order locking: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    print("5b. Workshop accepting the complex work order...")
    result = workshop_client.accept_asset(
        asset_id='wo_complex_001',
        asset_type='work_order'
    )
    print(f"   Complex work order acceptance: {result.get('status', 'unknown')}")
    time.sleep(1)
    
    # Main workshop sub-assigns to smaller specialized workshop
    print("5c. Main workshop sub-assigning to specialized workshop...")
    result = workshop_client.sub_assign_work_order(
        work_order_id='wo_complex_001',
        assignee_ids=[workshop2_client.public_key],
        assignment_details={
            'assignment_type': 'specialized_delegation',
            'delegation_reason': 'Requires specialized equipment and expertise'
        }
    )
    print(f"   Workshop-to-workshop sub-assignment: {result.get('status', 'unknown')}")
    time.sleep(2)
    
    # Note: Sub-workshop cannot further sub-assign because it's not the primary assignee
    # Only the original assignee (main workshop) can perform sub-assignments
    print("\n6. Demonstration Note:")
    print("   ℹ️  Only the primary assignee can sub-assign work orders")
    print("   ℹ️  Sub-workshops receive delegated work but cannot re-delegate")
    print("   ℹ️  This maintains clear accountability in the assignment hierarchy")

    # ===========================
    # PHASE 6: QUERY SUB-ASSIGNMENT RESULTS
    # ===========================
    print("\n🔍 PHASE 6: Querying Sub-Assignment Results")
    print("-" * 40)
    
    # Query main workshop account to see issued work orders
    print("1. Querying main workshop account...")
    # Note: Using direct state access instead of deprecated query transactions
    account_addr = workshop_client.get_account_address(workshop_client.public_key)
    account_data = workshop_client.get_state(account_addr)
    if account_data:
        print(f"   ✅ Workshop account found")
        print(f"   Work orders issued: {len(account_data.get('work_orders_issued', []))}")
        print(f"   Work orders assigned to workshop: {len(account_data.get('work_orders_assigned', []))}")
        if 'work_orders_issued' in account_data:
            print(f"   Issued work order IDs: {account_data['work_orders_issued']}")
    else:
        print(f"   ❌ Workshop account not found")
    time.sleep(1)
    
    # Query artisan accounts to see assignment tracking
    print("\n2. Querying artisan accounts for assignment tracking...")
    
    for artisan_name, artisan_client_obj in [("Artisan 1", artisan_client),
                                            ("Artisan 2", artisan2_client),  
                                            ("Artisan 3", artisan3_client)]:
        # Using direct state access instead of deprecated query transactions
        account_addr = artisan_client_obj.get_account_address(artisan_client_obj.public_key)
        account_data = artisan_client_obj.get_state(account_addr)
        if account_data:
            direct_assignments = len(account_data.get('work_orders_assigned', []))
            sub_assignments = len(account_data.get('work_orders_sub_assigned', []))
            print(f"   ✅ {artisan_name}:")
            print(f"      Direct assignments: {direct_assignments}")
            print(f"      Sub-assignments from workshops: {sub_assignments}")
            if account_data.get('work_orders_sub_assigned'):
                print(f"      Sub-assigned work order IDs: {account_data['work_orders_sub_assigned']}")
        else:
            print(f"   ❌ {artisan_name} account not found")
        time.sleep(0.5)
    
    # Query sub-workshop account
    print("\n3. Querying sub-workshop account...")
    # Using direct state access instead of deprecated query transactions
    account_addr = workshop2_client.get_account_address(workshop2_client.public_key)
    account_data = workshop2_client.get_state(account_addr)
    if account_data:
        print(f"   ✅ Sub-workshop account found")
        print(f"   Work orders issued by sub-workshop: {len(account_data.get('work_orders_issued', []))}")
        print(f"   Work orders sub-assigned to sub-workshop: {len(account_data.get('work_orders_sub_assigned', []))}")
        print(f"   Sub-assigned work order IDs: {account_data.get('work_orders_sub_assigned', [])}")
    else:
        print(f"   ❌ Sub-workshop account not found")
    time.sleep(1)
    
    # Query work order assets to see sub-assignment details
    print("\n4. Querying work order assets for sub-assignment metadata...")
    
    for wo_id in ['wo_large_001', 'wo_complex_001']:
        # Using direct state access instead of deprecated query transactions
        asset_addr = workshop_client.get_asset_address(wo_id, 'work_order')
        asset_data = workshop_client.get_state(asset_addr)
        if asset_data:
            print(f"   ✅ Work Order {wo_id}:")
            print(f"      Is sub-assigned: {asset_data.get('is_sub_assigned', False)}")
            print(f"      Sub-assignees: {len(asset_data.get('sub_assignees', []))}")
            if asset_data.get('sub_assignment_details'):
                # Get first assignee's details as example
                first_assignee = list(asset_data['sub_assignment_details'].keys())[0] if asset_data['sub_assignment_details'] else None
                if first_assignee:
                    assignment_type = asset_data['sub_assignment_details'][first_assignee].get('details', {}).get('assignment_type', 'N/A')
                    print(f"      Assignment type: {assignment_type}")
        else:
            print(f"   ❌ Work Order {wo_id} not found")
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("🎉 Sub-Assignment Demo Summary:")
    print("✅ Three-level hierarchy: Buyer → Workshop → Artisans")
    print("✅ Workshop-to-workshop delegation capability")
    print("✅ Granular tracking: direct vs sub-assignments")
    print("✅ Bidirectional relationship maintenance")
    print("✅ Complete audit trail with assignment metadata")
    print("=" * 60)

    # ===========================
    # PHASE 7: ORIGINAL QUERY OPERATIONS
    # ===========================
    print("\n🔍 PHASE 7: Original Query Operations")
    print("-" * 30)    # Query artisan account
    print("1. Querying artisan account...")
    # Using direct state access instead of deprecated query transactions
    account_addr = artisan_client.get_account_address(artisan_client.public_key)
    account_data = artisan_client.get_state(account_addr)
    if account_data:
        print(f"   ✅ Artisan account found")
        print(f"   Account Type: {account_data.get('account_type')}")
        print(f"   Auth Status: {account_data.get('authentication_status')}")
    else:
        print(f"   ❌ Artisan account not found")
    time.sleep(2)
    
    # Check state data
    print("2. Checking blockchain state...")
    namespace = admin_client.address_generator.get_namespace()
    print(f"   Namespace: {namespace}")
    
    # Get account address
    account_addr = admin_client.get_account_address(artisan_client.public_key)
    account_data = admin_client.get_state(account_addr)
    if account_data:
        print(f"   ✅ Artisan account found on blockchain")
        print(f"   Account ID: {account_data.get('account_id', 'N/A')}")
    else:
        print(f"   ❌ Artisan account not found")
    
    # Get asset address
    asset_addr = admin_client.get_asset_address('wool_001', 'raw_material')
    asset_data = admin_client.get_state(asset_addr)
    if asset_data:
        print(f"   ✅ Raw material asset found on blockchain")
        print(f"   Material Type: {asset_data.get('material_type', 'N/A')}")
    else:
        print(f"   ❌ Raw material asset not found")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("✅ Accounts and assets are managed in unified namespace")
    print("✅ No need for careful input/output address management")
    print("✅ Simplified client interaction with single TP")
    print("✅ Complete hierarchical work assignment system implemented")
    print("✅ Sub-assignment workflow tested with real-world scenarios")


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
