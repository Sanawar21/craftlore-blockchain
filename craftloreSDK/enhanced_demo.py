#!/usr/bin/env python3
"""
Demo of the enhanced CraftLore object system with authentication, authorization, 
and history tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object import CraftloreObject, AuthenticationStatus, AccountType
from accounts import SuperAdminAccount, ArtisanAdminAccount, ArtisanAccount
import time

# Create a simple product class for demonstration
class Product(CraftloreObject):
    """Example product implementation"""
    
    def __init__(self, **kwargs):
        # Product-specific attributes (before calling super().__init__)
        self.product_id = kwargs.get('product_id', self.generate_unique_identifier())
        self.product_name = kwargs.get('product_name', '')
        self.artisan_id = kwargs.get('artisan_id', '')
        self.price = kwargs.get('price', 0.0)
        
        # Remove these from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        for key in ['product_id', 'product_name', 'artisan_id', 'price']:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.product_id
    
    @property
    def creator(self):
        return self.artisan_id
    
    @property
    def type(self):
        return 'product'
    
    @property
    def owner(self):
        return getattr(self, 'owner_id', self.artisan_id)

def demo_enhanced_craftlore_system():
    """Demonstrate the enhanced CraftLore system capabilities."""
    
    print("🎨 === Enhanced CraftLore System Demo ===\n")
    
    # ===============================
    # 1. CREATE ACCOUNTS
    # ===============================
    print("1. Creating accounts...\n")
    
    # Create Super Admin
    super_admin = SuperAdminAccount.new(
        account_id="super_admin_001",
        email="admin@craftlore.com",
        created_by="system"
    )
    print(f"✅ Super Admin: {super_admin.identifier} ({super_admin.account_type.value})")
    
    # Create Artisan Admin
    artisan_admin = ArtisanAdminAccount.new(
        account_id="artisan_admin_001",
        email="artisan.admin@craftlore.com",
        region="Kashmir",
        craft_specialization="carpet_weaving",
        created_by=super_admin.identifier
    )
    print(f"✅ Artisan Admin: {artisan_admin.identifier} ({artisan_admin.account_type.value})")
    
    # Create Artisan
    artisan = ArtisanAccount.new(
        account_id="artisan_001",
        artisan_name="Master Weaver Ali",
        specialization="Carpet Weaving",
        years_experience=25,
        location="Srinagar, Kashmir",
        email="ali.weaver@craftlore.com",
        created_by=artisan_admin.identifier
    )
    print(f"✅ Artisan: {artisan.identifier} ({artisan.account_type.value})")
    print()
    
    # ===============================
    # 2. DEMONSTRATE AUTHENTICATION HIERARCHY
    # ===============================
    print("2. Testing authentication hierarchy...\n")
    
    # Super admin approves artisan admin
    print("Super Admin approving Artisan Admin...")
    artisan_admin.authenticate(
        approver_id=super_admin.identifier,
        account_type=super_admin.account_type,
        status=AuthenticationStatus.APPROVED,
        reason="Initial admin setup",
        block_number=1001,
        transaction_id="tx_001"
    )
    print(f"✅ Artisan Admin status: {artisan_admin.authentication_status.value}")
    
    # Artisan admin approves artisan
    print("Artisan Admin approving Artisan...")
    artisan.authenticate(
        approver_id=artisan_admin.identifier,
        account_type=artisan_admin.account_type,
        status=AuthenticationStatus.APPROVED,
        reason="Verified credentials and skills",
        block_number=1002,
        transaction_id="tx_002"
    )
    print(f"✅ Artisan status: {artisan.authentication_status.value}")
    print()
    
    # ===============================
    # 3. CREATE AND MANAGE PRODUCTS
    # ===============================
    print("3. Creating and managing products...\n")
    
    # Create a product
    carpet = Product.new(
        product_name="Traditional Kashmiri Carpet",
        artisan_id=artisan.identifier,
        price=500.0,
        description="Handwoven carpet with traditional patterns",
        required_signatures=1,
        creator_id=artisan.identifier
    )
    print(f"✅ Product created: {carpet.identifier}")
    print(f"   Product type: {carpet.type}")
    print(f"   Authentication status: {carpet.authentication_status.value}")
    print(f"   Object address: {carpet.get_object_address()}")
    print(f"   History address: {carpet.get_history_address()}")
    print()
    
    # ===============================
    # 4. DEMONSTRATE AUTHORIZATION RULES
    # ===============================
    print("4. Testing authorization rules...\n")
    
    # Test who can authenticate the product
    print("Who can authenticate the carpet?")
    print(f"   Super Admin: {carpet.can_authenticate(super_admin.identifier, super_admin.account_type)}")
    print(f"   Artisan Admin: {carpet.can_authenticate(artisan_admin.identifier, artisan_admin.account_type)}")
    print(f"   Artisan (owner): {carpet.can_authenticate(artisan.identifier, artisan.account_type)}")
    print()
    
    # Test who can modify the product
    print("Who can modify the carpet?")
    print(f"   Super Admin: {carpet.can_modify(super_admin.identifier, super_admin.account_type)}")
    print(f"   Artisan Admin: {carpet.can_modify(artisan_admin.identifier, artisan_admin.account_type)}")
    print(f"   Artisan (owner): {carpet.can_modify(artisan.identifier, artisan.account_type)}")
    print()
    
    # ===============================
    # 5. DEMONSTRATE PRODUCT AUTHENTICATION
    # ===============================
    print("5. Authenticating product...\n")
    
    # Artisan admin authenticates the product
    carpet.authenticate(
        approver_id=artisan_admin.identifier,
        account_type=artisan_admin.account_type,
        status=AuthenticationStatus.APPROVED,
        reason="Quality verified, traditional techniques confirmed",
        block_number=1003,
        transaction_id="tx_003"
    )
    print(f"✅ Carpet authenticated: {carpet.authentication_status.value}")
    print()
    
    # ===============================
    # 6. DEMONSTRATE OBJECT UPDATES
    # ===============================
    print("6. Updating product...\n")
    
    # Update product details
    updates = {
        'price': 750.0,
        'description': 'Premium handwoven carpet with intricate traditional patterns'
    }
    
    carpet.update_object(
        updated_by=artisan.identifier,
        account_type=artisan.account_type,
        updates=updates,
        block_number=1004,
        transaction_id="tx_004"
    )
    print(f"✅ Carpet updated - New price: ${carpet.price}")
    print(f"   Version: {carpet.version}")
    print()
    
    # ===============================
    # 7. DEMONSTRATE MULTI-SIGNATURE AUTHENTICATION
    # ===============================
    print("7. Testing multi-signature authentication...\n")
    
    # Create a high-value product requiring multiple signatures
    premium_carpet = Product.new(
        product_name="Master Artisan Premium Carpet",
        artisan_id=artisan.identifier,
        price=2000.0,
        required_signatures=2,  # Requires 2 signatures
        creator_id=artisan.identifier
    )
    
    print(f"Premium carpet created (requires {premium_carpet.required_signatures} signatures)")
    
    # First signature from artisan admin
    premium_carpet.authenticate(
        approver_id=artisan_admin.identifier,
        account_type=artisan_admin.account_type,
        status=AuthenticationStatus.APPROVED,
        reason="Initial quality check passed",
        block_number=1005,
        transaction_id="tx_005"
    )
    print(f"   After 1st signature: {premium_carpet.authentication_status.value}")
    
    # Second signature from super admin
    premium_carpet.authenticate(
        approver_id=super_admin.identifier,
        account_type=super_admin.account_type,
        status=AuthenticationStatus.APPROVED,
        reason="Final approval for premium product",
        block_number=1006,
        transaction_id="tx_006"
    )
    print(f"   After 2nd signature: {premium_carpet.authentication_status.value}")
    print()
    
    # ===============================
    # 8. DEMONSTRATE HISTORY TRACKING
    # ===============================
    print("8. History tracking...\n")
    
    print(f"Carpet history ({len(carpet.history)} entries):")
    for i, entry in enumerate(carpet.history, 1):
        print(f"   {i}. Block {entry.block_number} - {entry.action} by {entry.actor_id}")
        print(f"      Transaction: {entry.transaction_id}")
        if entry.action == "update":
            print(f"      Changes: price changed from {entry.previous_state.get('price')} to {entry.current_state.get('price')}")
        print()
    
    # ===============================
    # 9. DEMONSTRATE OWNERSHIP TRANSFER
    # ===============================
    print("9. Ownership transfer...\n")
    
    # Create a buyer account
    buyer = ArtisanAccount.new(
        account_id="buyer_001",
        artisan_name="Collector Smith",
        account_type=AccountType.BUYER
    )
    
    # Transfer ownership
    carpet.transfer_ownership(
        new_owner_id=buyer.identifier,
        authorized_by=artisan.identifier,
        account_type=artisan.account_type,
        block_number=1007,
        transaction_id="tx_007"
    )
    print(f"✅ Ownership transferred to: {carpet.owner_id}")
    print()
    
    # ===============================
    # 10. DEMONSTRATE SOFT DELETE
    # ===============================
    print("10. Soft delete...\n")
    
    # Create a test product for deletion
    test_product = Product.new(
        product_name="Test Product",
        artisan_id=artisan.identifier,
        creator_id=artisan.identifier
    )
    
    print(f"Test product created: {test_product.identifier}")
    print(f"Is deleted: {test_product.is_deleted}")
    
    # Soft delete the product
    test_product.soft_delete(
        deleted_by=artisan.identifier,
        account_type=artisan.account_type,
        block_number=1008,
        transaction_id="tx_008"
    )
    
    print(f"After soft delete:")
    print(f"   Is deleted: {test_product.is_deleted}")
    print(f"   Deleted by: {test_product.deleted_by}")
    print(f"   Deleted at: {test_product.deleted_at}")
    print()
    
    # ===============================
    # 11. SERIALIZATION DEMO
    # ===============================
    print("11. Serialization demo...\n")
    
    # Convert to JSON
    carpet_json = carpet.to_json()
    print("Carpet serialized to JSON (first 200 chars):")
    print(carpet_json[:200] + "...")
    print()
    
    # Convert back from JSON
    carpet_restored = Product.from_json(carpet_json)
    print(f"Restored carpet ID: {carpet_restored.identifier}")
    print(f"Restored carpet price: ${carpet_restored.price}")
    print(f"History entries preserved: {len(carpet_restored.history)}")
    print()
    
    print("🎉 Demo completed successfully!")

if __name__ == '__main__':
    demo_enhanced_craftlore_system()
