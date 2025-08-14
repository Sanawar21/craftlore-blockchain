#!/usr/bin/env python3
"""
Asset creation and management operations for CraftLore Asset TP.
"""

import hashlib
from typing import Dict, List, Optional
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from entities.assets import Product, ProductBatch, RawMaterial, WorkOrder, Warranty
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
            AssetType.WARRANTY: Warranty
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
        
        asset = asset_class(
            asset_id=asset_id,
            public_key=signer_public_key,
            timestamp=timestamp
        )
        
        # Set initial owner
        asset.owner = signer_public_key
        
        # Handle asset-type-specific initialization
        self._initialize_asset_specific_fields(context, asset, payload, asset_type)
        
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
    
    def create_products_from_batch(self, context: Context, payload: Dict):
        """Handle creation of individual products from a batch."""
        required_fields = ['batch_id', 'product_count', 'buyer_public_key', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")
        
        batch_id = payload['batch_id']
        product_count = payload['product_count']
        buyer_public_key = payload['buyer_public_key']
        timestamp = payload['timestamp']
        signer_public_key = payload.get('signer_public_key')
        
        # Load batch
        batch = self._get_asset(context, batch_id, 'product_batch')
        if not batch:
            raise InvalidTransaction(f"Product batch not found: {batch_id}")
        
        # Check if signer is the batch owner (assignee who completed production)
        if batch.get('owner') != signer_public_key:
            raise InvalidTransaction("Only the batch owner can create products from batch")
        
        # Check if batch is locked and complete
        if not batch.get('is_locked', False):
            raise InvalidTransaction("Batch must be locked before creating products")
        
        if not batch.get('is_complete', False):
            raise InvalidTransaction("Batch must be complete before creating products")
        
        # Validate product count
        max_quantity = batch.get('order_quantity', 0)
        if product_count > max_quantity:
            raise InvalidTransaction(f"Cannot create more products ({product_count}) than batch quantity ({max_quantity})")
        
        # Create individual products
        product_ids = self._create_products_from_batch(context, batch_id, product_count, buyer_public_key, timestamp)
        
        # Update batch current quantity
        batch['current_quantity'] = max(0, batch.get('current_quantity', max_quantity) - product_count)
        batch['updated_timestamp'] = timestamp
        
        # Add history entry
        self._add_asset_history(batch, {
            'action': 'products_created_from_batch',
            'actor_public_key': signer_public_key,
            'details': f'{product_count} products created and transferred to {buyer_public_key}'
        }, timestamp)
        
        # Store updated batch
        self._store_asset(context, batch)
        
        # Update account states consistently
        self._update_account_state_for_product_creation(context, product_ids, buyer_public_key, signer_public_key, timestamp)
        
        print(f"✅ Created {product_count} products from batch {batch_id}")
        
        return {
            'status': 'success',
            'batch_id': batch_id,
            'product_count': product_count,
            'product_ids': product_ids,
            'buyer_public_key': buyer_public_key
        }
    
    def _initialize_asset_specific_fields(self, context: Context, asset, payload: Dict, asset_type: AssetType):
        """Initialize asset-specific fields based on type."""
        if asset_type == AssetType.RAW_MATERIAL:
            asset.material_type = payload.get('material_type', '')
            asset.supplier_id = payload.get('supplier_id', '')
            asset.quantity = payload.get('quantity', 0)
            asset.quantity_unit = payload.get('quantity_unit', '')
            asset.harvested_date = payload.get('harvested_date', '')
            asset.source_location = payload.get('source_location', '')
            asset.transaction_date = payload.get('timestamp', '')
            
        elif asset_type == AssetType.PRODUCT_BATCH:
            asset.raw_materials_used = payload.get('raw_materials_used', [])
            asset.order_quantity = payload.get('order_quantity', 0)
            asset.quantity_unit = payload.get('quantity_unit', '')
            asset.producer_id = payload.get('producer_id', '')
            asset.category = payload.get('category', '')
            asset.name = payload.get('name', '')
            asset.description = payload.get('description', '')
            asset.work_order_id = payload.get('work_order_id', '')
            asset.batch_status = ProductBatchStatus.PENDING
            
        elif asset_type == AssetType.PRODUCT:
            asset.batch_id = payload.get('batch_id', '')
            asset.batch_index = payload.get('batch_index', 0)
            asset.purchase_date = payload.get('timestamp', '')
            
        elif asset_type == AssetType.WORK_ORDER:
            asset.batch_id = payload.get('batch_id', '')
            asset.assigner_id = payload.get('assigner_id', asset.public_key)
            assignee_id = payload.get('assignee_id', '')
            
            # Rule: Only an artisan or workshop can be the assignee of a work order
            if assignee_id:
                self.asset_utils.validate_artisan_or_workshop_account(context, assignee_id)
            
            asset.assignee_id = assignee_id
            asset.work_type = payload.get('work_type', 'production')
            asset.estimated_completion_date = payload.get('estimated_completion_date', '')
            
        elif asset_type == AssetType.WARRANTY:
            asset.product_id = payload.get('product_id', '')
            asset.buyer_id = payload.get('buyer_id', asset.public_key)
            asset.warranty_period_months = payload.get('warranty_period_months', 12)
            asset.warranty_terms = payload.get('warranty_terms', '')
    
    def _create_products_from_batch(self, context: Context, batch_id: str, product_count: int, buyer_public_key: str, timestamp: str) -> List[str]:
        """Create individual products from a batch (Flow 1, step 7)."""
        product_ids = []
        
        # Get batch address for generating product addresses
        batch_address = self.address_generator.generate_asset_address(batch_id, 'product_batch')
        
        for i in range(product_count):
            # Generate product ID and address from batch
            product_id = f"{batch_id}_product_{i}"
            product_address = self.address_generator.generate_product_address_from_batch(batch_address, i)
            
            # Create product
            product = Product(
                asset_id=product_id,
                public_key=buyer_public_key,  # Initial creator
                timestamp=timestamp
            )
            
            product.batch_id = batch_id
            product.batch_index = i
            product.owner = buyer_public_key
            product.purchase_date = timestamp
            
            # Store product
            product_data = product.to_dict()
            context.set_state({
                product_address: self.serializer.to_bytes(product_data)
            })
            
            # Update indices
            self._update_owner_index(context, product_id, buyer_public_key)
            self._update_type_index(context, 'product', product_id)
            
            product_ids.append(product_id)
        
        return product_ids
    
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
                # Update assignee account if work order has an assignee
                if hasattr(asset, 'assignee_id') and asset.assignee_id:
                    # Note: Account state updates can be added here if needed
                    pass
                
                # Update assigner account if it's a workshop
                if hasattr(asset, 'assigner_id') and asset.assigner_id:
                    assigner_account_type = self.asset_utils.get_account_type(context, asset.assigner_id)
                    # Note: Account state updates can be added here if needed
                        
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
    
    def _update_account_state_for_product_creation(self, context: Context, product_ids: List[str], 
                                                  buyer_public_key: str, creator_public_key: str, timestamp: str):
        """Update account state when products are created and transferred to buyer."""
        try:
            # Update buyer account - they now own these products
            # Note: Account state updates can be added here if needed
            
            # Update creator account based on their type
            creator_account_type = self.asset_utils.get_account_type(context, creator_public_key)
            # Note: Account state updates can be added here if needed
            
            print(f"✅ Created {len(product_ids)} products from batch")
                    
        except Exception as e:
            print(f"Warning: Could not update account state for product creation: {str(e)}")
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
