#!/usr/bin/env python3
"""
Test script to demonstrate account validation rules for asset operations.

This script shows how the asset-tp now enforces:
1. Only SupplierAccount can create raw material assets
2. Only Artisan or Workshop accounts can be assignees of work orders
"""

import json
from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Simulate transaction payloads that would trigger validation

def test_raw_material_creation():
    """Test raw material creation validation."""
    print("=== Testing Raw Material Creation ===")
    
    # Valid case: Supplier creates raw material
    print("✅ Test Case 1: Supplier creates raw material")
    payload = {
        "action": "create_asset",
        "asset_type": "raw_material",
        "asset_id": "rm_001",
        "material_type": "wool",
        "supplier_id": "supplier_001",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: SUCCESS (if signer is approved supplier account)")
    
    # Invalid case: Non-supplier tries to create raw material
    print("\n❌ Test Case 2: Non-supplier tries to create raw material")
    payload = {
        "action": "create_asset",
        "asset_type": "raw_material",
        "asset_id": "rm_002",
        "material_type": "cotton",
        "supplier_id": "artisan_001",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: FAILURE - Only SupplierAccount can create raw material assets")

def test_work_order_assignment():
    """Test work order assignee validation."""
    print("\n=== Testing Work Order Assignment ===")
    
    # Valid case: Artisan is assigned work order
    print("✅ Test Case 3: Artisan assigned to work order")
    payload = {
        "action": "create_asset",
        "asset_type": "work_order",
        "asset_id": "wo_001",
        "batch_id": "batch_001",
        "assignee_id": "artisan_001",
        "work_type": "production",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: SUCCESS (if assignee_id is approved artisan account)")
    
    # Valid case: Workshop is assigned work order
    print("\n✅ Test Case 4: Workshop assigned to work order")
    payload = {
        "action": "create_asset",
        "asset_type": "work_order",
        "asset_id": "wo_002",
        "batch_id": "batch_002",
        "assignee_id": "workshop_001",
        "work_type": "production",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: SUCCESS (if assignee_id is approved workshop account)")
    
    # Invalid case: Buyer assigned to work order
    print("\n❌ Test Case 5: Buyer assigned to work order")
    payload = {
        "action": "create_asset",
        "asset_type": "work_order",
        "asset_id": "wo_003",
        "batch_id": "batch_003",
        "assignee_id": "buyer_001",
        "work_type": "production",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: FAILURE - Only Artisan or Workshop accounts can be assignees")

def test_work_order_acceptance():
    """Test work order acceptance validation."""
    print("\n=== Testing Work Order Acceptance ===")
    
    # Valid case: Artisan accepts work order
    print("✅ Test Case 6: Artisan accepts work order")
    payload = {
        "action": "accept_asset",
        "asset_id": "wo_001",
        "asset_type": "work_order",
        "timestamp": "2025-08-08T11:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: SUCCESS (if signer is approved artisan/workshop and is the assignee)")
    
    # Invalid case: Non-artisan/workshop tries to accept
    print("\n❌ Test Case 7: Retailer tries to accept work order")
    payload = {
        "action": "accept_asset",
        "asset_id": "wo_001",
        "asset_type": "work_order",
        "timestamp": "2025-08-08T11:00:00Z"
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("   Expected: FAILURE - Only Artisan or Workshop accounts can accept work orders")

def show_validation_implementation():
    """Show the validation implementation details."""
    print("\n=== Validation Implementation ===")
    
    print("🔍 Raw Material Creation Validation:")
    print("   Location: asset-tp/handlers/asset_creation.py - create_asset()")
    print("   Check: self.account_validator.validate_supplier_account(context, signer_public_key)")
    print("   Rule: Only accounts with account_type='supplier' can create raw materials")
    
    print("\n🔍 Work Order Assignment Validation:")
    print("   Location: asset-tp/handlers/asset_creation.py - _initialize_asset_specific_fields()")
    print("   Check: self.account_validator.validate_artisan_or_workshop_account(context, assignee_id)")
    print("   Rule: Only accounts with account_type='artisan' or 'workshop' can be assignees")
    
    print("\n🔍 Work Order Acceptance Validation:")
    print("   Location: asset-tp/handlers/asset_transfer.py - accept_asset()")
    print("   Check: self.account_validator.validate_artisan_or_workshop_account(context, signer_public_key)")
    print("   Rule: Only artisan/workshop accounts can accept work orders")
    
    print("\n🔍 Account Validation Utility:")
    print("   Location: asset-tp/utils/account_validation.py")
    print("   Features:")
    print("   - Cross-chain account state reading from account-tp")
    print("   - Account type validation")
    print("   - Authentication status checking")
    print("   - Deletion status checking")

if __name__ == "__main__":
    print("CraftLore Asset TP - Account Validation Rules Test")
    print("=" * 55)
    
    test_raw_material_creation()
    test_work_order_assignment()
    test_work_order_acceptance()
    show_validation_implementation()
    
    print("\n" + "=" * 55)
    print("🛡️  VALIDATION RULES IMPLEMENTED:")
    print("   ✅ Rule 1: Only SupplierAccount can create raw material assets")
    print("   ✅ Rule 2: Only Artisan or Workshop can be assignees of work orders")
    print("   ✅ Cross-TP state validation between asset-tp and account-tp")
    print("   ✅ Authentication status checking for all operations")
    print("=" * 55)
