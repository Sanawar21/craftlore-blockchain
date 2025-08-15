#!/usr/bin/env python3
"""
Asset transfer operations for CraftLore Asset TP.
"""

from typing import Dict, List
from datetime import datetime
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AssetStatus, AssetType, AccountType
from entities.assets import BaseAsset, Product, ProductBatch, RawMaterial, WorkOrder, Warranty
from .asset_utils import AssetUtils
from .asset_utils import AssetUtils


# Dynamic account class mapping
def _get_account_class_mapping():
    """Get dynamic mapping of account types to their classes."""
    mapping = {}
    
    try:
        from entities.accounts.artisan_account import ArtisanAccount
        mapping[AccountType.ARTISAN] = ArtisanAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.workshop_account import WorkshopAccount
        mapping[AccountType.WORKSHOP] = WorkshopAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.supplier_account import SupplierAccount
        mapping[AccountType.SUPPLIER] = SupplierAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.buyer_account import BuyerAccount
        mapping[AccountType.BUYER] = BuyerAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.seller_account import SellerAccount
        mapping[AccountType.SELLER] = SellerAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.distributor_account import DistributorAccount
        mapping[AccountType.DISTRIBUTOR] = DistributorAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.wholesaler_account import WholesalerAccount
        mapping[AccountType.WHOLESALER] = WholesalerAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.retailer_account import RetailerAccount
        mapping[AccountType.RETAILER] = RetailerAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.verifier_account import VerifierAccount
        mapping[AccountType.VERIFIER] = VerifierAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.admin_account import AdminAccount
        mapping[AccountType.ADMIN] = AdminAccount
    except ImportError:
        pass
    
    try:
        from entities.accounts.super_admin_account import SuperAdminAccount
        mapping[AccountType.SUPER_ADMIN] = SuperAdminAccount
    except ImportError:
        pass
    
    return mapping


def _create_account_from_data(account_data):
    """Create account object dynamically based on account type."""
    from entities.accounts.base_account import BaseAccount
    
    account_type = account_data.get('account_type')
    if not account_type:
        return BaseAccount.from_dict(account_data)
    
    # Convert string to enum if needed
    if isinstance(account_type, str):
        try:
            account_type = AccountType(account_type)
        except ValueError:
            # Unknown account type, use base account
            return BaseAccount.from_dict(account_data)
    
    # Get the mapping and create appropriate account object
    account_mapping = _get_account_class_mapping()
    AccountClass = account_mapping.get(account_type, BaseAccount)
    
    return AccountClass.from_dict(account_data)


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
            new_owner = transaction_data['new_owner_public_key']
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
            self._update_account_state_for_asset_transfer(context, old_owner, new_owner, asset_id, timestamp)
            
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
            
            # Update account states consistently (both assignee and issuer)
            self._update_account_state_for_work_order_acceptance(context, work_order_data, signer_public_key, timestamp)
            self._update_work_order_issuer_account(context, work_order_data, timestamp)
            
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
    
    def sub_assign_work_order(self, context: Context, transaction_data: Dict) -> Dict:
        """Allow workshop to sub-assign work order to individual artisans or other workshops."""
        try:
            work_order_id = transaction_data['work_order_id']
            assignee_ids = transaction_data['assignee_ids']  # List of assignee public keys (artisans/workshops)
            assignment_details = transaction_data.get('assignment_details', {})  # Optional details per assignee
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current work order
            work_order_data = self.asset_utils.get_asset(context, work_order_id, 'work_order')
            if not work_order_data:
                raise InvalidTransaction(f"Work order {work_order_id} not found")
            
            # Check if signer is the primary assignee (workshop)
            if work_order_data.get('assignee_id') != signer_public_key:
                raise InvalidTransaction("Only the primary assignee can sub-assign the work order")
            
            # Verify signer is a workshop
            self.asset_utils.validate_workshop_account(context, signer_public_key)
            
            # Check if work order is in progress
            if work_order_data.get('status') != AssetStatus.IN_PROGRESS.value:
                raise InvalidTransaction("Work order must be in progress to sub-assign")
            
            # Validate all assignees exist and are artisan or workshop accounts
            for assignee_id in assignee_ids:
                self.asset_utils.validate_artisan_or_workshop_account(context, assignee_id)
            
            # Update work order with sub-assignments
            work_order_data['sub_assignees'] = list(set(work_order_data.get('sub_assignees', []) + assignee_ids))
            work_order_data['is_sub_assigned'] = True
            
            # Update assignment details
            if 'sub_assignment_details' not in work_order_data:
                work_order_data['sub_assignment_details'] = {}
            
            for assignee_id in assignee_ids:
                work_order_data['sub_assignment_details'][assignee_id] = {
                    'assigned_at': timestamp,
                    'assigned_by': signer_public_key,
                    'details': assignment_details.get(assignee_id, {}),
                    'status': 'assigned'
                }
            
            # Add history entry
            self.asset_utils.add_asset_history(work_order_data, {
                'action': 'sub_assigned',
                'workshop_id': signer_public_key,
                'assignee_ids': assignee_ids,
                'assignment_count': len(assignee_ids)
            }, timestamp)
            
            # Store updated work order
            self.asset_utils.store_asset(context, work_order_data)
            
            # Update account states for all involved parties
            self._update_accounts_for_sub_assignment(context, work_order_data, signer_public_key, assignee_ids, timestamp)
            
            return {
                'status': 'success',
                'message': f'Work order {work_order_id} sub-assigned to {len(assignee_ids)} assignees',
                'sub_assignees': assignee_ids,
                'total_sub_assignees': len(work_order_data['sub_assignees'])
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Sub-assignment failed: {str(e)}")
    
    def _update_account_state_for_work_order_acceptance(self, context: Context, work_order_data: Dict, 
                                                       assignee_public_key: str, timestamp: str):
        """Update account state when work order is accepted."""
        try:
            # Get assignee account
            account_data = self.asset_utils.get_account(context, assignee_public_key)
            if not account_data:
                print(f"Warning: Could not find assignee account for {assignee_public_key}")
                return
            
            # Create account object dynamically based on account type
            account = _create_account_from_data(account_data)
            
            # Add work order to assignee's work order list (bidirectional relationship)
            work_order_id = work_order_data['asset_id']
            account_type = account_data.get('account_type')
            
            if account_type in ['artisan', 'workshop'] and hasattr(account, 'work_orders_assigned'):
                if work_order_id not in account.work_orders_assigned:
                    account.work_orders_assigned.append(work_order_id)
                    print(f"✅ Added work order {work_order_id} to {account_type}'s work_orders_assigned list")
            
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
            serialized_account = self.serializer.to_bytes(account.to_dict())
            
            context.set_state({account_address: serialized_account})
            print(f"✅ Updated assignee account history for work order acceptance: {work_order_data['asset_id']}")
            
        except Exception as e:
            print(f"Warning: Could not update account state for work order acceptance: {str(e)}")
            # Don't fail the transaction, just log the warning
    
    def _update_work_order_issuer_account(self, context: Context, work_order_data: Dict, timestamp: str):
        """Update the work order issuer's account when work order is accepted."""
        try:
            issuer_public_key = work_order_data.get('assigner_id') or work_order_data.get('owner')
            if not issuer_public_key:
                print("Warning: Could not identify work order issuer for account update")
                return
            
            # Get issuer account
            account_data = self.asset_utils.get_account(context, issuer_public_key)
            if not account_data:
                print(f"Warning: Could not find issuer account for {issuer_public_key}")
                return
            
            # Create account object dynamically based on account type
            account = _create_account_from_data(account_data)
            
            # Add history entry for work order acceptance from issuer perspective
            account.add_history_entry({
                'action': 'work_order_accepted_by_assignee',
                'work_order_id': work_order_data['asset_id'],
                'assignee_id': work_order_data['assignee_id'],
                'accepted_at': timestamp
            }, timestamp)
            
            # Update the account data with new history
            account_data['history'] = account.history
            
            # Store updated account
            account_address = self.address_generator.generate_account_address(issuer_public_key)
            serialized_account = self.serializer.to_bytes(account.to_dict())
            
            context.set_state({account_address: serialized_account})
            print(f"✅ Updated issuer account history for work order acceptance: {work_order_data['asset_id']}")
            
        except Exception as e:
            print(f"Warning: Could not update issuer account state for work order acceptance: {str(e)}")
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
                
                # Create account object dynamically based on account type
                account = _create_account_from_data(account_data)
                
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
                serialized_account = self.serializer.to_bytes(account.to_dict())
                
                context.set_state({account_address: serialized_account})
                print(f"✅ Updated account history for {action}: {asset_id}")
            
        except Exception as e:
            print(f"Warning: Could not update account state for asset transfer: {str(e)}")
            # Don't fail the transaction, just log the warning

    def _update_accounts_for_sub_assignment(self, context: Context, work_order_data: Dict, 
                                          workshop_public_key: str, assignee_ids: List[str], timestamp: str):
        """Update account states when work order is sub-assigned to artisans or workshops."""
        try:
            work_order_id = work_order_data['asset_id']
            
            # Update workshop account
            workshop_account_data = self.asset_utils.get_account(context, workshop_public_key)
            if workshop_account_data:
                workshop_account = _create_account_from_data(workshop_account_data)
                
                # Add history entry for sub-assignment
                workshop_account.add_history_entry({
                    'action': 'work_order_sub_assigned',
                    'work_order_id': work_order_id,
                    'assignee_ids': assignee_ids,
                    'sub_assigned_at': timestamp
                }, timestamp)
                
                # Update workshop account
                workshop_account_data['history'] = workshop_account.history
                workshop_address = self.address_generator.generate_account_address(workshop_public_key)
                serialized_workshop = self.serializer.to_bytes(workshop_account.to_dict())
                context.set_state({workshop_address: serialized_workshop})
                print(f"✅ Updated workshop account for sub-assignment: {work_order_id}")
            
            # Update each assignee account (artisan or workshop)
            for assignee_id in assignee_ids:
                assignee_account_data = self.asset_utils.get_account(context, assignee_id)
                if assignee_account_data:
                    assignee_account = _create_account_from_data(assignee_account_data)
                    
                    # Add to work_orders_sub_assigned list (for sub-assignments from workshops)
                    if hasattr(assignee_account, 'work_orders_sub_assigned'):
                        if work_order_id not in assignee_account.work_orders_sub_assigned:
                            assignee_account.work_orders_sub_assigned.append(work_order_id)
                            account_type = assignee_account_data.get('account_type', 'unknown')
                            print(f"✅ Added work order {work_order_id} to {account_type}'s work_orders_sub_assigned list")
                    
                    # Add history entry for sub-assignment
                    assignee_account.add_history_entry({
                        'action': 'work_order_sub_assigned_to_me',
                        'work_order_id': work_order_id,
                        'workshop_id': workshop_public_key,
                        'sub_assigned_at': timestamp
                    }, timestamp)
                    
                    # Update assignee account
                    assignee_account_data['history'] = assignee_account.history
                    assignee_address = self.address_generator.generate_account_address(assignee_id)
                    serialized_assignee = self.serializer.to_bytes(assignee_account.to_dict())
                    context.set_state({assignee_address: serialized_assignee})
                    print(f"✅ Updated assignee account for sub-assignment: {assignee_id}")
                    
        except Exception as e:
            print(f"Warning: Could not update accounts for sub-assignment: {str(e)}")
            # Don't fail the transaction, just log the warning
