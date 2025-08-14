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
            if asset_data.get('status') == AssetStatus.LOCKED.value:
                raise InvalidTransaction("Asset is already locked")
            
            # Store previous status
            previous_status = asset_data.get('status', AssetStatus.AVAILABLE.value)
            
            # Update asset status
            asset_data['status'] = AssetStatus.LOCKED.value
            asset_data['lock_reason'] = reason
            asset_data['locked_by'] = signer_public_key
            asset_data['locked_at'] = timestamp
            asset_data['previous_status'] = previous_status
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'locked',
                'reason': reason,
                'previous_status': previous_status,
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
            if asset_data.get('status') != AssetStatus.LOCKED.value:
                raise InvalidTransaction("Asset is not locked")
            
            # Restore previous status
            previous_status = asset_data.get('previous_status', AssetStatus.AVAILABLE.value)
            asset_data['status'] = previous_status
            
            # Remove lock-related fields
            asset_data.pop('lock_reason', None)
            asset_data.pop('locked_by', None)
            asset_data.pop('locked_at', None)
            asset_data.pop('previous_status', None)
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'unlocked',
                'restored_status': previous_status,
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
            is_locked = asset_data.get('status') == AssetStatus.LOCKED.value
            
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
