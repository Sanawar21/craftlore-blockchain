#!/usr/bin/env python3
"""
Asset workflow operations for CraftLore Asset TP.
"""

from typing import Dict
from datetime import datetime
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AssetStatus, AssetType
from entities import AssetFactory
from .asset_utils import AssetUtils


class AssetWorkflowHandler:
    """Handler for asset workflow operations."""
    
    def __init__(self, address_generator, serializer):
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
