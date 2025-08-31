#!/usr/bin/env python3
"""
Asset creation and management operations for CraftLore Asset TP.
"""

import hashlib
from typing import Dict, List, Optional
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from entities.assets import Product, ProductBatch, RawMaterial, WorkOrder, Warranty, Logistics, Packaging
from core.enums import AssetType, WorkOrderStatus, ProductBatchStatus
from .asset_utils import AssetUtils


class AssetCreationHandler:
    """Handles asset creation operations."""
    
    def __init__(self, address_generator, serializer):
        self.address_generator = address_generator
        self.serializer = serializer
        self.asset_utils = AssetUtils(address_generator, serializer)
        
        # Asset type mapping
        self.ASSET_CLASSES = {
            AssetType.RAW_MATERIAL: RawMaterial,
            AssetType.PRODUCT: Product,
            AssetType.PRODUCT_BATCH: ProductBatch,
            AssetType.WORK_ORDER: WorkOrder,
            AssetType.WARRANTY: Warranty,
            AssetType.LOGISTICS: Logistics,
            AssetType.PACKAGING: Packaging
        }
    
    def create_asset(self, context: Context, payload: Dict):
        """Handle asset creation according to flows."""
        # Validate required fields
        required_fields = ['asset_type', 'asset_id', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")
        
        asset_type_str = payload['asset_type']
        asset_id = payload['asset_id']
        timestamp = payload['timestamp']
        
        # Validate asset type
        try:
            asset_type = AssetType(asset_type_str)
        except ValueError:
            raise InvalidTransaction(f"Invalid asset type: {asset_type_str}")
        
        # Get signer information
        signer_public_key = payload.get('signer_public_key')
        
        # Validate account permissions based on asset type (Flow rules)
        if asset_type == AssetType.RAW_MATERIAL:
            # Rule: Only a SupplierAccount can create raw material assets
            self.asset_utils.validate_supplier_account(context, signer_public_key)
        
        # Check if asset already exists
        self._check_asset_not_exists(context, asset_id, asset_type_str)
        
        # Create asset instance
        asset_class = self.ASSET_CLASSES.get(asset_type)
        if not asset_class:
            raise InvalidTransaction(f"Unsupported asset type: {asset_type_str}")

        # asset = asset_class(
        #     asset_id=asset_id,
        #     owner=signer_public_key,
        #     timestamp=timestamp
        # )
        
        # # Set initial owner
        # asset.owner = signer_public_key
        
        # Handle asset-type-specific initialization
        # self._initialize_asset_specific_fields(context, asset, payload, asset_type)
        if asset_type == AssetType.PRODUCT_BATCH:
            creator_account_type = self.asset_utils.get_account_type(context, signer_public_key)
            if creator_account_type not in ['artisan', 'workshop']:
                raise InvalidTransaction("Only artisan or workshop accounts can create product batches directly. Other accounts should create work orders.")
            
            # Validate that order_quantity is provided and greater than 0
            order_quantity = payload.get('order_quantity', 0)
            if order_quantity <= 0:
                raise InvalidTransaction("order_quantity must be specified and greater than 0 when creating a product batch")
        
        elif asset_type == AssetType.WORK_ORDER:
            # Rule: Only an artisan or workshop can be the assignee of a work order
            assignee_id = payload.get('assignee_id', '')
            if assignee_id:
                assignee_account_type = self.asset_utils.get_account_type(context, assignee_id)
                if assignee_account_type not in ['artisan', 'workshop']:
                    raise InvalidTransaction("Only artisan or workshop accounts can be assigned to a work order.")

        payload['owner'] = signer_public_key
        asset = asset_class.from_dict(payload)

        # Store asset with all necessary indices
        self._store_asset_with_indices(context, asset)
        
        # Update account state consistently
        self._update_account_state_for_asset_creation(context, asset, asset_type, timestamp)
        
        print(f"✅ Asset created: {asset_id} ({asset_type_str})")
        
        return {
            'status': 'success',
            'asset_id': asset_id,
            'asset_type': asset_type_str,
            'owner': signer_public_key,
            'timestamp': timestamp
        }
    
    # Helper methods (imported from asset_utils)
    def _check_asset_not_exists(self, context: Context, asset_id: str, asset_type: str):
        """Check that asset does not already exist."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        existing_asset = utils.get_asset(context, asset_id, asset_type)
        if existing_asset and not existing_asset.get('is_deleted', False):
            raise InvalidTransaction(f"Asset already exists: {asset_id}")
    
    def _get_asset(self, context: Context, asset_id: str, asset_type: str) -> Optional[Dict]:
        """Get asset by ID and type."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        return utils.get_asset(context, asset_id, asset_type)
    
    def _store_asset_with_indices(self, context: Context, asset):
        """Store asset and maintain all necessary indices."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        utils.store_asset_with_indices(context, asset)
    
    def _store_asset(self, context: Context, asset_data: Dict):
        """Store asset data."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        utils.store_asset(context, asset_data)
    
    def _update_owner_index(self, context: Context, asset_id: str, owner_public_key: str):
        """Update owner index."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        utils.update_owner_index(context, asset_id, owner_public_key)
    
    def _update_type_index(self, context: Context, asset_type: str, asset_id: str):
        """Update asset type index."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        utils.update_type_index(context, asset_type, asset_id)
    
    def _add_asset_history(self, asset_data: Dict, history_entry: Dict, timestamp: str):
        """Add history entry to asset."""
        from .asset_utils import AssetUtils
        utils = AssetUtils(self.address_generator, self.serializer)
        utils.add_asset_history(asset_data, history_entry, timestamp)
    
    def _update_account_state_for_asset_creation(self, context: Context, asset, asset_type: AssetType, timestamp: str):
        """Update account state consistently when assets are created."""
        try:
            if asset_type == AssetType.RAW_MATERIAL:
                # Update supplier account by adding the raw material to their created list
                self._update_supplier_account_for_raw_material(context, asset.owner, asset.asset_id, timestamp)
                
            elif asset_type == AssetType.WORK_ORDER:
                # Update work order issuer's work_orders_issued list
                self._update_work_order_issuer_account_on_creation(context, asset, timestamp)
                
                # Update assignee account if work order has an assignee
                if hasattr(asset, 'assignee_id') and asset.assignee_id:
                    # Note: Account state updates can be added here if needed
                    pass
                        
            elif asset_type == AssetType.PRODUCT_BATCH:
                # Update creator account
                creator_account_type = self.asset_utils.get_account_type(context, asset.owner)
                # Note: Account state updates can be added here if needed
                if creator_account_type in ['artisan', 'workshop']:
                    # Will be updated when production is completed
                    pass
                    
        except Exception as e:
            print(f"Warning: Could not update account state for asset creation: {str(e)}")
            # Don't fail the transaction, just log the warning

    def _update_supplier_account_for_raw_material(self, context: Context, supplier_public_key: str, raw_material_id: str, timestamp: str):
        """Update supplier account when they create a raw material."""
        try:
            # Get supplier account
            account_data = self.asset_utils.get_account(context, supplier_public_key)
            if not account_data:
                print(f"Warning: Could not find supplier account for {supplier_public_key}")
                return
            
            # Import the supplier account class
            from entities.accounts.supplier_account import SupplierAccount
            from core.enums import AccountType
            
            # Create supplier account instance from stored data
            supplier_account = SupplierAccount.from_dict(account_data)

            
            # Add the raw material to the created list
            supplier_account.add_raw_material_created(raw_material_id, timestamp)
            
            # Store updated account
            account_address = self.address_generator.generate_account_address(supplier_public_key)
            serialized_account = self.serializer.to_bytes(supplier_account.to_dict())
            
            context.set_state({account_address: serialized_account})
            print(f"✅ Updated supplier account with new raw material: {raw_material_id}")
            
        except Exception as e:
            print(f"Warning: Could not update supplier account: {str(e)}")
            # Don't fail the transaction, just log the warning

    def _update_work_order_issuer_account_on_creation(self, context: Context, work_order_asset, timestamp: str):
        """Update work order issuer's account when a work order is created."""
        try:
            # Get the issuer public key (could be assigner_id or owner)
            issuer_public_key = getattr(work_order_asset, 'assigner_id', None) or work_order_asset.owner
            
            if not issuer_public_key:
                print("Warning: Could not identify work order issuer for account update")
                return
                
            # Get issuer account data
            account_data = self.asset_utils.get_account(context, issuer_public_key)
            if not account_data:
                print(f"Warning: Could not find issuer account for {issuer_public_key}")
                return
                
            # Import account creation function from asset_transfer
            from handlers.asset_transfer import _create_account_from_data
            
            # Create account object dynamically based on account type
            account = _create_account_from_data(account_data)
            
            # Add work order to issuer's work_orders_issued list (bidirectional relationship)
            work_order_id = work_order_asset.asset_id
            if hasattr(account, 'work_orders_issued'):
                if work_order_id not in account.work_orders_issued:
                    account.work_orders_issued.append(work_order_id)
                    print(f"✅ Added work order {work_order_id} to issuer's work_orders_issued list")
            
            # Add history entry for work order creation
            account.add_history_entry({
                'action': 'work_order_created',
                'work_order_id': work_order_id,
                'assignee_id': getattr(work_order_asset, 'assignee_id', ''),
                'created_at': timestamp
            }, timestamp)
            
            # Update the account data with new history
            account_data['history'] = account.history
            
            # Store updated account
            account_address = self.address_generator.generate_account_address(issuer_public_key)
            serialized_account = self.serializer.to_bytes(account.to_dict())
            
            context.set_state({account_address: serialized_account})
            print(f"✅ Updated issuer account for work order creation: {work_order_id}")
            
        except Exception as e:
            print(f"Warning: Could not update work order issuer account: {str(e)}")
            # Don't fail the transaction, just log the warning
