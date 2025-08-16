#!/usr/bin/env python3
"""
Asset workflow operations for CraftLore Asset TP.
"""

from typing import Dict, List
from datetime import datetime
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AssetStatus, AssetType
from entities import AssetFactory
from .asset_utils import AssetUtils


class AssetWorkflowHandler:
    """Handler for asset workflow operations."""
    
    def __init__(self, address_generator, serializer):
        self.address_generator = address_generator
        self.serializer = serializer
        self.asset_utils = AssetUtils(address_generator, serializer)
    
    def lock_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Lock asset to prevent modifications."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            reason = transaction_data.get('reason', 'Locked by owner')
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                raise InvalidTransaction("Insufficient permissions to lock asset")
            
            # Check if already locked
            if asset_data.get('is_locked', False):
                raise InvalidTransaction("Asset is already locked")
            
            # Lock the asset without changing its status
            asset_data['is_locked'] = True
            asset_data['lock_reason'] = reason
            asset_data['locked_by'] = signer_public_key
            asset_data['locked_at'] = timestamp
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'locked',
                'reason': reason,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {'status': 'success', 'message': f'Asset {asset_id} locked'}
            
        except Exception as e:
            raise InvalidTransaction(f"Lock failed: {str(e)}")
    
    def unlock_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Unlock asset to allow modifications."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                raise InvalidTransaction("Insufficient permissions to unlock asset")
            
            # Check if locked
            if not asset_data.get('is_locked', False):
                raise InvalidTransaction("Asset is not locked")
            
            # Unlock the asset
            asset_data['is_locked'] = False
            
            # Remove lock-related fields
            asset_data.pop('lock_reason', None)
            asset_data.pop('locked_by', None)
            asset_data.pop('locked_at', None)
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'unlocked',
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {'status': 'success', 'message': f'Asset {asset_id} unlocked'}
            
        except Exception as e:
            raise InvalidTransaction(f"Unlock failed: {str(e)}")
    
    def delete_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Soft delete asset (mark as deleted)."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            reason = transaction_data.get('reason', 'Deleted by owner')
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                raise InvalidTransaction("Insufficient permissions to delete asset")
            
            # Check if already deleted
            if asset_data.get('status') == AssetStatus.DELETED.value:
                raise InvalidTransaction("Asset is already deleted")
            
            # Store previous status
            previous_status = asset_data.get('status', AssetStatus.AVAILABLE.value)
            
            # Soft delete
            asset_data['status'] = AssetStatus.DELETED.value
            asset_data['deleted_at'] = timestamp
            asset_data['deleted_by'] = signer_public_key
            asset_data['deletion_reason'] = reason
            asset_data['previous_status'] = previous_status
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'deleted',
                'reason': reason,
                'previous_status': previous_status,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {'status': 'success', 'message': f'Asset {asset_id} deleted'}
            
        except Exception as e:
            raise InvalidTransaction(f"Delete failed: {str(e)}")
    
    def update_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Update asset with new data."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            updates = transaction_data['updates']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_update_asset(signer_public_key, asset_data, asset_type):
                raise InvalidTransaction("Insufficient permissions to update asset")
            
            # Create asset instance to check editability
            asset_instance = AssetFactory.create_asset(asset_data)
            
            # Check if asset is locked and updates are allowed
            is_locked = asset_data.get('is_locked', False)
            
            # Track changes for history
            changes = {}
            
            # Apply updates
            for field, new_value in updates.items():
                if field in asset_instance.uneditable_fields:
                    raise InvalidTransaction(f"Field '{field}' is not editable")
                
                if is_locked and field not in asset_instance.post_lock_editable_fields:
                    raise InvalidTransaction(f"Field '{field}' cannot be modified when asset is locked")
                
                old_value = asset_data.get(field)
                if old_value != new_value:
                    asset_data[field] = new_value
                    changes[field] = {'old': old_value, 'new': new_value}
            
            if not changes:
                return {'status': 'success', 'message': 'No changes made'}
            
            # Update last modified timestamp
            asset_data['last_modified'] = timestamp
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'updated',
                'changes': changes,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {
                'status': 'success',
                'message': f'Asset {asset_id} updated',
                'changes': changes
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Update failed: {str(e)}")

    def use_raw_material_in_batch(self, context: Context, transaction_data: Dict) -> Dict:
        """Use raw material in a product batch."""
        try:
            raw_material_id = transaction_data['raw_material_id']
            batch_id = transaction_data['batch_id']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get raw material asset
            raw_material_data = self.asset_utils.get_asset(context, raw_material_id, 'raw_material')
            if not raw_material_data:
                raise InvalidTransaction(f"Raw material {raw_material_id} not found")
            
            # Get batch asset
            batch_data = self.asset_utils.get_asset(context, batch_id, 'product_batch')
            if not batch_data:
                raise InvalidTransaction(f"Product batch {batch_id} not found")
            
            # Check if signer owns the raw material
            if raw_material_data['owner'] != signer_public_key:
                raise InvalidTransaction("Only the owner of the raw material can use it in a batch")
            
            # Check if signer owns the batch
            if batch_data['owner'] != signer_public_key:
                raise InvalidTransaction("Only the owner of the batch can add raw materials to it")
            
            # Check if raw material is already used in this batch
            if batch_id in raw_material_data.get('batches_used_in', []):
                raise InvalidTransaction(f"Raw material {raw_material_id} is already used in batch {batch_id}")
            
            # Add batch to raw material's batches_used_in list
            if 'batches_used_in' not in raw_material_data:
                raw_material_data['batches_used_in'] = []
            raw_material_data['batches_used_in'].append(batch_id)
            
            # Add raw material to batch's raw_materials_used list if not already there
            if 'raw_materials_used' not in batch_data:
                batch_data['raw_materials_used'] = []
            if raw_material_id not in batch_data['raw_materials_used']:
                batch_data['raw_materials_used'].append(raw_material_id)
            
            # Add history entry to raw material
            self.asset_utils.add_asset_history(raw_material_data, {
                'action': 'used_in_batch',
                'batch_id': batch_id,
                'actor': signer_public_key
            }, timestamp)
            
            # Add history entry to batch
            self.asset_utils.add_asset_history(batch_data, {
                'action': 'raw_material_added',
                'raw_material_id': raw_material_id,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated assets
            self.asset_utils.store_asset(context, raw_material_data)
            self.asset_utils.store_asset(context, batch_data)
            
            return {
                'status': 'success',
                'message': f'Raw material {raw_material_id} is now used in batch {batch_id}',
                'raw_material_id': raw_material_id,
                'batch_id': batch_id
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Use raw material in batch failed: {str(e)}")

    def complete_batch_production(self, context: Context, transaction_data: Dict) -> Dict:
        """Complete batch production - mark as complete, generate individual products and transfer to buyer."""
        try:
            from core.enums import ProductBatchStatus, WorkOrderStatus
            from entities.assets.product import Product
            
            batch_id = transaction_data['batch_id']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            production_date = transaction_data.get('production_date', timestamp)
            artisans_involved = transaction_data.get('artisans_involved', [])
            quality_notes = transaction_data.get('quality_notes', '')
            
            # Get current batch
            batch_data = self.asset_utils.get_asset(context, batch_id, 'product_batch')
            if not batch_data:
                raise InvalidTransaction(f"Product batch {batch_id} not found")
            
            # Check permissions - only batch owner (artisan/workshop) can complete
            if batch_data.get('owner') != signer_public_key:
                raise InvalidTransaction("Only the batch owner can complete production")
            
            # Validate account type
            account_type = self.asset_utils.get_account_type(context, signer_public_key)
            if account_type not in ['artisan', 'workshop']:
                raise InvalidTransaction("Only artisan or workshop accounts can complete batch production")
            
            # Check if already completed
            if batch_data.get('is_complete', False):
                raise InvalidTransaction("Batch production is already completed")
            
            # Check if batch has required information
            order_quantity = batch_data.get('order_quantity', 0)
            if order_quantity <= 0:
                raise InvalidTransaction("Batch must have valid order_quantity to complete production")
            
            # Lock the batch first (as per flow specification)
            batch_data['is_locked'] = True
            batch_data['locked_by'] = signer_public_key
            batch_data['locked_timestamp'] = timestamp
            
            # Update batch data - mark as complete
            batch_data['is_complete'] = True
            batch_data['batch_status'] = ProductBatchStatus.COMPLETED.value
            batch_data['production_date'] = production_date
            batch_data['current_quantity'] = order_quantity  # Set to full quantity when completed
            batch_data['updated_timestamp'] = timestamp
            
            # Update artisans involved if provided
            if artisans_involved:
                batch_data['artisans_involved'] = artisans_involved
            
            # Add quality notes if provided
            if quality_notes:
                if 'quality_control_reports' not in batch_data:
                    batch_data['quality_control_reports'] = []
                batch_data['quality_control_reports'].append({
                    'timestamp': timestamp,
                    'notes': quality_notes,
                    'inspector': signer_public_key
                })
            
            # Generate individual products (owned by batch creator initially)
            product_ids = self._create_individual_products_from_batch(
                context, batch_id, order_quantity, signer_public_key, timestamp
            )
            
            # Add history entry for production completion and product generation
            self.asset_utils.add_asset_history(batch_data, {
                'action': 'production_completed_with_products_generated',
                'actor': signer_public_key,
                'production_date': production_date,
                'quantity_produced': order_quantity,
                'products_created': len(product_ids),
                'products_owner': signer_public_key,
                'artisans_involved': artisans_involved
            }, timestamp)
            
            # Store updated batch
            self.asset_utils.store_asset(context, batch_data)
            
            result = {
                'status': 'success',
                'message': f'Batch {batch_id} production completed. {order_quantity} products generated (owned by batch creator).',
                'batch_id': batch_id,
                'quantity_produced': order_quantity,
                'products_generated': len(product_ids),
                'product_ids': product_ids,
                'products_owner': signer_public_key,
                'production_date': production_date
            }
            
            # Update work order status if batch is linked to a work order
            work_order_id = batch_data.get('work_order_id')
            if work_order_id:
                try:
                    work_order_data = self.asset_utils.get_asset(context, work_order_id, 'work_order')
                    if work_order_data:
                        work_order_data['status'] = WorkOrderStatus.COMPLETED.value
                        work_order_data['actual_completion_date'] = timestamp
                        work_order_data['updated_timestamp'] = timestamp
                        
                        # Add history entry to work order
                        self.asset_utils.add_asset_history(work_order_data, {
                            'action': 'completed_with_products_ready',
                            'actor': signer_public_key,
                            'batch_id': batch_id,
                            'products_created': len(product_ids),
                            'products_pending_transfer': True,
                            'completion_date': timestamp
                        }, timestamp)
                        
                        # Store updated work order
                        self.asset_utils.store_asset(context, work_order_data)
                        
                        result['work_order_updated'] = True
                        result['work_order_id'] = work_order_id
                        result['transfer_required'] = True
                        result['transfer_message'] = f"Products ready for manual transfer to buyer"
                        
                except Exception as e:
                    print(f"Warning: Could not update work order {work_order_id}: {str(e)}")
                    result['work_order_warning'] = str(e)
            
            return result
            
        except Exception as e:
            raise InvalidTransaction(f"Complete batch production failed: {str(e)}")

    def _create_individual_products_from_batch(self, context: Context, batch_id: str, 
                                              product_count: int, batch_owner_public_key: str, 
                                              timestamp: str) -> List[str]:
        """Create individual products from a completed batch (owned by batch creator initially)."""
        from entities.assets.product import Product
        
        product_ids = []
        
        for i in range(product_count):
            # Generate product ID and address using standard asset addressing
            product_id = f"{batch_id}_product_{i}"
            product_address = self.address_generator.generate_asset_address(product_id, 'product')
            
            # Create product instance
            product = Product(
                asset_id=product_id,
                public_key=batch_owner_public_key,  # Products are created and owned by batch creator
                timestamp=timestamp
            )
            
            # Set product properties
            product.batch_id = batch_id
            product.batch_index = i
            product.owner = batch_owner_public_key  # Products remain with batch owner
            product.purchase_date = ""  # No purchase yet, will be set when transferred
            
            # Add history entry for product creation (no transfer yet)
            product.history = [{
                'action': 'created_from_completed_batch',
                'actor': batch_owner_public_key,
                'batch_id': batch_id,
                'batch_index': i,
                'status': 'ready_for_transfer',
                'timestamp': timestamp
            }]
            
            # Store product on blockchain
            product_data = product.to_dict()
            context.set_state({
                product_address: self.serializer.to_bytes(product_data)
            })
            
            # Update indices for product discovery
            self._update_owner_index(context, product_id, batch_owner_public_key)
            self._update_type_index(context, 'product', product_id)
            
            product_ids.append(product_id)
            
            print(f"   ✅ Created product {product_id} (owned by batch creator)")
        
        return product_ids
    
    def _update_owner_index(self, context: Context, asset_id: str, owner_public_key: str):
        """Update owner index for asset discovery."""
        self.asset_utils.update_owner_index(context, asset_id, owner_public_key)
    
    def _update_type_index(self, context: Context, asset_type: str, asset_id: str):
        """Update asset type index for discovery."""
        self.asset_utils.update_type_index(context, asset_type, asset_id)
