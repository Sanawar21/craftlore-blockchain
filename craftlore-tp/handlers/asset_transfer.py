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
from .asset_utils import AssetUtils
from .asset_utils import AssetUtils


class AssetTransferHandler:
    """Handler for asset transfer operations."""
    
    def __init__(self, address_generator, serializer):
        self.address_generator = address_generator
        self.serializer = serializer
        self.asset_utils = AssetUtils(address_generator, serializer)
    
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
            self.asset_utils.validate_artisan_or_workshop_account(context, signer_public_key)
            
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
            # Get assignee account
            account_data = self.asset_utils.get_account(context, assignee_public_key)
            if not account_data:
                print(f"Warning: Could not find assignee account for {assignee_public_key}")
                return
            
            # Add work order acceptance to account history
            from entities.accounts.base_account import BaseAccount
            
            # Create a base account instance to use the add_history_entry method
            account = BaseAccount(
                account_id=account_data['account_id'],
                public_key=account_data['public_key'],
                email=account_data['email'],
                account_type=account_data['account_type'],
                timestamp=account_data['created_at']
            )
            
            # Load existing history
            account.history = account_data.get('history', [])
            
            # Add history entry for work order acceptance
            account.add_history_entry({
                'action': 'work_order_accepted',
                'work_order_id': work_order_data['asset_id'],
                'accepted_at': timestamp
            }, timestamp)
            
            # Update the account data with new history
            account_data['history'] = account.history
            
            # Store updated account
            account_address = self.address_generator.generate_account_address(assignee_public_key)
            serialized_account = self.serializer.serialize(account_data)
            
            context.set_state({account_address: serialized_account})
            print(f"✅ Updated assignee account history for work order acceptance: {work_order_data['asset_id']}")
            
        except Exception as e:
            print(f"Warning: Could not update account state for work order acceptance: {str(e)}")
            # Don't fail the transaction, just log the warning
    
    def _update_account_state_for_asset_transfer(self, context: Context, from_public_key: str, 
                                                to_public_key: str, asset_id: str, timestamp: str):
        """Update account states for asset transfer."""
        try:
            # Update both sender and receiver accounts
            for public_key, action in [(from_public_key, 'asset_sent'), (to_public_key, 'asset_received')]:
                account_data = self.asset_utils.get_account(context, public_key)
                if not account_data:
                    print(f"Warning: Could not find account for {public_key}")
                    continue
                
                # Add transfer to account history
                from entities.accounts.base_account import BaseAccount
                
                # Create a base account instance to use the add_history_entry method
                account = BaseAccount(
                    account_id=account_data['account_id'],
                    public_key=account_data['public_key'],
                    email=account_data['email'],
                    account_type=account_data['account_type'],
                    timestamp=account_data['created_at']
                )
                
                # Load existing history
                account.history = account_data.get('history', [])
                
                # Add history entry for asset transfer
                account.add_history_entry({
                    'action': action,
                    'asset_id': asset_id,
                    'other_party': to_public_key if action == 'asset_sent' else from_public_key,
                    'transferred_at': timestamp
                }, timestamp)
                
                # Update the account data with new history
                account_data['history'] = account.history
                
                # Store updated account
                account_address = self.address_generator.generate_account_address(public_key)
                serialized_account = self.serializer.serialize(account_data)
                
                context.set_state({account_address: serialized_account})
                print(f"✅ Updated account history for {action}: {asset_id}")
            
        except Exception as e:
            print(f"Warning: Could not update account state for asset transfer: {str(e)}")
            # Don't fail the transaction, just log the warning
