#!/usr/bin/env python3
"""
Asset transfer operations for CraftLore Asset TP.
"""

from typing import Dict, List
from datetime import datetime
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AssetStatus, AssetType
from entities.assets import BaseAsset, Product, ProductBatch, RawMaterial, WorkOrder, Warranty
from utils.account_validation import AccountValidator
from utils.account_state_updater import AccountStateUpdater
from .asset_utils import AssetUtils


class AssetTransferHandler:
    """Handler for asset transfer operations."""
    
    def __init__(self, address_generator, serializer):
        self.asset_utils = AssetUtils(address_generator, serializer)
        self.account_validator = AccountValidator()
        self.account_updater = AccountStateUpdater()
    
    def transfer_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Transfer asset to new owner."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            new_owner = transaction_data['new_owner']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                raise InvalidTransaction("Insufficient permissions to transfer asset")
            
            # Store old owner for index updates
            old_owner = asset_data['owner']
            
            # Update asset
            asset_data['owner'] = new_owner
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'transferred',
                'from_owner': old_owner,
                'to_owner': new_owner,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            # Update owner indices
            self.asset_utils.update_owner_indices(context, asset_id, old_owner, new_owner)
            
            # Update account states consistently
            self._update_account_state_for_asset_transfer(context, asset_data, old_owner, new_owner, timestamp)
            
            return {'status': 'success', 'message': f'Asset {asset_id} transferred to {new_owner}'}
            
        except Exception as e:
            raise InvalidTransaction(f"Transfer failed: {str(e)}")
    
    def bulk_transfer(self, context: Context, transaction_data: Dict) -> Dict:
        """Transfer multiple assets to new owner."""
        try:
            asset_ids = transaction_data['asset_ids']
            new_owner = transaction_data['new_owner']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            transferred_assets = []
            failed_transfers = []
            
            for asset_info in asset_ids:
                asset_id = asset_info['asset_id']
                asset_type = asset_info['asset_type']
                
                try:
                    # Get current asset
                    asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
                    if not asset_data:
                        failed_transfers.append({'asset_id': asset_id, 'error': 'Asset not found'})
                        continue
                    
                    # Check permissions
                    if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                        failed_transfers.append({'asset_id': asset_id, 'error': 'Insufficient permissions'})
                        continue
                    
                    # Check if asset can be transferred
                    if asset_data.get('status') == AssetStatus.LOCKED.value:
                        failed_transfers.append({'asset_id': asset_id, 'error': 'Asset is locked'})
                        continue
                    
                    # Store old owner for index updates
                    old_owner = asset_data['owner']
                    
                    # Update asset
                    asset_data['owner'] = new_owner
                    
                    # Add history entry
                    self.asset_utils.add_asset_history(asset_data, {
                        'action': 'bulk_transferred',
                        'from_owner': old_owner,
                        'to_owner': new_owner,
                        'actor': signer_public_key
                    }, timestamp)
                    
                    # Store updated asset
                    self.asset_utils.store_asset(context, asset_data)
                    
                    # Update owner indices
                    self.asset_utils.update_owner_indices(context, asset_id, old_owner, new_owner)
                    
                    transferred_assets.append(asset_id)
                    
                except Exception as e:
                    failed_transfers.append({'asset_id': asset_id, 'error': str(e)})
            
            return {
                'status': 'completed',
                'transferred_assets': transferred_assets,
                'failed_transfers': failed_transfers,
                'total_transferred': len(transferred_assets),
                'total_failed': len(failed_transfers)
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Bulk transfer failed: {str(e)}")
    
    def accept_asset(self, context: Context, transaction_data: Dict) -> Dict:
        """Accept work order and transfer associated product batch (Flow 1, step 3)."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Only work orders can be accepted (Flow 1)
            if asset_type != AssetType.WORK_ORDER.value:
                raise InvalidTransaction("Only work orders can be accepted")
            
            # Get current work order
            work_order_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not work_order_data:
                raise InvalidTransaction(f"Work order {asset_id} not found")
            
            # Check if signer is the assignee
            if work_order_data.get('assignee_id') != signer_public_key:
                raise InvalidTransaction("Only the assignee can accept the work order")
            
            # Rule: Only an artisan or workshop can be the assignee of a work order
            self.account_validator.validate_artisan_or_workshop_account(context, signer_public_key)
            
            # Check if work order is locked (Flow 1, step 3)
            if not work_order_data.get('is_locked', False):
                raise InvalidTransaction("Work order must be locked before it can be accepted")
            
            # Check current status
            current_status = work_order_data.get('status')
            if current_status != AssetStatus.PENDING.value:
                raise InvalidTransaction(f"Work order cannot be accepted in status: {current_status}")
            
            # Update work order status to "accepted"
            work_order_data['status'] = AssetStatus.IN_PROGRESS.value
            work_order_data['accepted_timestamp'] = timestamp
            
            # Add history entry for work order
            self.asset_utils.add_asset_history(work_order_data, {
                'action': 'accepted',
                'previous_status': current_status,
                'new_status': AssetStatus.IN_PROGRESS.value,
                'actor': signer_public_key,
                'details': 'Work order accepted by assignee'
            }, timestamp)
            
            # Store updated work order
            self.asset_utils.store_asset(context, work_order_data)
            
            # Update account state consistently
            self._update_account_state_for_work_order_acceptance(context, work_order_data, signer_public_key, timestamp)
            
            # Transfer associated product batch to assignee (Flow 1, step 3)
            batch_id = work_order_data.get('batch_id')
            if batch_id:
                batch_data = self.asset_utils.get_asset(context, batch_id, 'product_batch')
                if batch_data:
                    old_owner = batch_data['owner']
                    batch_data['owner'] = signer_public_key
                    batch_data['transferred_timestamp'] = timestamp
                    
                    # Add history entry for batch transfer
                    self.asset_utils.add_asset_history(batch_data, {
                        'action': 'transferred_on_work_order_acceptance',
                        'from_owner': old_owner,
                        'to_owner': signer_public_key,
                        'work_order_id': asset_id,
                        'actor': signer_public_key
                    }, timestamp)
                    
                    # Store updated batch
                    self.asset_utils.store_asset(context, batch_data)
                    
                    # Update ownership indices for batch
                    self.asset_utils.update_owner_index(context, batch_id, signer_public_key)
            
            return {
                'status': 'success',
                'message': f'Work order {asset_id} accepted and product batch {batch_id} transferred',
                'work_order_status': AssetStatus.IN_PROGRESS.value,
                'batch_transferred': batch_id is not None,
                'new_batch_owner': signer_public_key if batch_id else None
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Accept failed: {str(e)}")
    
    def _update_account_state_for_work_order_acceptance(self, context: Context, work_order_data: Dict, 
                                                       assignee_public_key: str, timestamp: str):
        """Update account state when work order is accepted."""
        try:
            # Update assignee account (artisan or workshop)
            self.account_updater.update_artisan_work_orders(
                context, assignee_public_key, work_order_data['asset_id'], 'accepted', timestamp
            )
            
        except Exception as e:
            print(f"Warning: Could not update account state for work order acceptance: {str(e)}")
            # Don't fail the transaction, just log the warning
    
    def _update_account_state_for_asset_transfer(self, context: Context, asset_data: Dict, 
                                               old_owner: str, new_owner: str, timestamp: str):
        """Update account state when assets are transferred."""
        try:
            asset_type = asset_data.get('asset_type')
            asset_id = asset_data.get('asset_id')
            
            if asset_type == 'raw_material':
                # Update supplier account for raw material transfer
                self.account_updater.update_supplier_raw_materials(
                    context, old_owner, asset_id, 'transferred', timestamp
                )
                
            elif asset_type == 'product':
                # Update old owner (removing product)
                old_account_type = self.account_validator.get_account_type(context, old_owner)
                if old_account_type in ['buyer', 'retailer', 'wholesaler']:
                    self.account_updater.update_buyer_products(
                        context, old_owner, [asset_id], 'transferred', timestamp
                    )
                    if old_account_type == 'retailer':
                        self.account_updater.update_retailer_inventory(
                            context, old_owner, [asset_id], 'sold', timestamp
                        )
                
                # Update new owner (receiving product)
                new_account_type = self.account_validator.get_account_type(context, new_owner)
                if new_account_type in ['buyer', 'retailer', 'wholesaler']:
                    self.account_updater.update_buyer_products(
                        context, new_owner, [asset_id], 'purchased', timestamp
                    )
                    if new_account_type == 'retailer':
                        self.account_updater.update_retailer_inventory(
                            context, new_owner, [asset_id], 'received', timestamp
                        )
                        
        except Exception as e:
            print(f"Warning: Could not update account state for asset transfer: {str(e)}")
            # Don't fail the transaction, just log the warning
