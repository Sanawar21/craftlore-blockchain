#!/usr/bin/env python3
"""
Utility functions for asset operations in CraftLore Combined TP.
"""

from typing import Dict, Optional
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AccountType


class AssetUtils:
    """Utility class for common asset operations."""
    
    def __init__(self, address_generator, serializer):
        self.address_generator = address_generator
        self.serializer = serializer
    
    # =============================================
    # ACCOUNT VALIDATION METHODS
    # =============================================
    
    def get_account(self, context: Context, public_key: str) -> Optional[Dict]:
        """Get account by public key."""
        try:
            account_address = self.address_generator.generate_account_address(public_key)
            entries = context.get_state([account_address])
            
            if entries:
                account_data = self.serializer.from_bytes(entries[0].data)
                return account_data
            return None
        except Exception as e:
            print(f"Error retrieving account {public_key}: {e}")
            return None
    
    def get_account_type(self, context: Context, public_key: str) -> Optional[str]:
        """Get account type for a public key."""
        account = self.get_account(context, public_key)
        if account and not account.get('is_deleted', False):
            return account.get('account_type')
        return None
    
    def validate_supplier_account(self, context: Context, public_key: str):
        """Validate that the account is a supplier."""
        account_type = self.get_account_type(context, public_key)
        if account_type != AccountType.SUPPLIER.value:
            raise InvalidTransaction(f"Only supplier accounts can create raw materials. Account type: {account_type}")

    def validate_artisan_or_workshop_account(self, context: Context, public_key: str):
        """Validate that the account is an artisan or workshop."""
        account_type = self.get_account_type(context, public_key)
        if account_type not in [AccountType.ARTISAN.value, AccountType.WORKSHOP.value]:
            raise InvalidTransaction("Only artisan or workshop accounts can be assigned work orders")
    
    def validate_account_exists(self, context: Context, public_key: str):
        """Validate that an account exists and is active."""
        account = self.get_account(context, public_key)
        if not account or account.get('is_deleted', False):
            raise InvalidTransaction(f"Account {public_key} does not exist or is inactive")
    
    # =============================================
    # ASSET OPERATIONS
    # =============================================
    
    def get_asset(self, context: Context, asset_id: str, asset_type: str) -> Optional[Dict]:
        """Get asset by ID and type."""
        try:
            asset_address = self.address_generator.generate_asset_address(asset_id, asset_type)
            entries = context.get_state([asset_address])
            
            if entries:
                return self.serializer.from_bytes(entries[0].data)
            return None
        except Exception as e:
            print(f"Error retrieving asset {asset_id}: {e}")
            return None
    
    def store_asset(self, context: Context, asset_data: Dict):
        """Store asset data."""
        asset_id = asset_data['asset_id']
        asset_type = asset_data['asset_type']
        asset_address = self.address_generator.generate_asset_address(asset_id, asset_type)
        
        context.set_state({
            asset_address: self.serializer.to_bytes(asset_data)
        })
    
    def store_asset_with_indices(self, context: Context, asset):
        """Store asset and maintain all necessary indices."""
        # Convert asset to dict for storage
        asset_data = asset.to_dict()
        
        # Store the asset
        self.store_asset(context, asset_data)
        
        # Update owner index
        self.update_owner_index(context, asset.asset_id, asset.owner)
        
        # Update type index
        self.update_type_index(context, asset.asset_type.value, asset.asset_id)
    
    def update_owner_index(self, context: Context, asset_id: str, owner_public_key: str):
        """Update owner index."""
        owner_address = self.address_generator.generate_owner_index_address(owner_public_key)
        
        try:
            entries = context.get_state([owner_address])
            if entries:
                owner_assets = self.serializer.from_bytes(entries[0].data)
            else:
                owner_assets = {'owner': owner_public_key, 'assets': []}
            
            if asset_id not in owner_assets['assets']:
                owner_assets['assets'].append(asset_id)
            
            context.set_state({
                owner_address: self.serializer.to_bytes(owner_assets)
            })
        except Exception as e:
            print(f"Error updating owner index: {e}")
    
    def update_type_index(self, context: Context, asset_type: str, asset_id: str):
        """Update asset type index."""
        type_address = self.address_generator.generate_asset_type_index_address(asset_type)
        
        try:
            entries = context.get_state([type_address])
            if entries:
                type_assets = self.serializer.from_bytes(entries[0].data)
            else:
                type_assets = {'asset_type': asset_type, 'assets': []}
            
            if asset_id not in type_assets['assets']:
                type_assets['assets'].append(asset_id)
            
            context.set_state({
                type_address: self.serializer.to_bytes(type_assets)
            })
        except Exception as e:
            print(f"Error updating type index: {e}")
    
    def update_owner_indices(self, context: Context, asset_id: str, old_owner: str, new_owner: str):
        """Update owner indices when ownership changes."""
        # Remove from old owner's index
        if old_owner:
            self.remove_from_owner_index(context, asset_id, old_owner)
        
        # Add to new owner's index
        if new_owner:
            self.update_owner_index(context, asset_id, new_owner)
    
    def remove_from_owner_index(self, context: Context, asset_id: str, owner_public_key: str):
        """Remove asset from owner's index."""
        try:
            owner_address = self.address_generator.generate_owner_index_address(owner_public_key)
            entries = context.get_state([owner_address])
            
            if entries:
                owner_assets = self.serializer.from_bytes(entries[0].data)
                if asset_id in owner_assets.get('assets', []):
                    owner_assets['assets'].remove(asset_id)
                    context.set_state({
                        owner_address: self.serializer.to_bytes(owner_assets)
                    })
        except Exception as e:
            print(f"Error removing from owner index: {e}")
    
    def add_asset_history(self, asset_data: Dict, history_entry: Dict, timestamp: str):
        """Add history entry to asset."""
        if 'history' not in asset_data:
            asset_data['history'] = []
        
        history_entry['timestamp'] = timestamp
        asset_data['history'].append(history_entry)
    
    def can_modify_asset(self, signer_public_key: str, asset: Dict) -> bool:
        """Check if signer can modify the asset (owner or super admin)."""
        # Owner can always modify
        if asset.get('owner') == signer_public_key:
            return True
        
        # TODO: Check if signer is super admin by querying account-tp
        # For now, allow owner only
        return False
    
    def can_update_asset(self, signer_public_key: str, asset: Dict, asset_type: str) -> bool:
        """Check if signer can update the asset."""
        # For work orders, assignee can update status
        if asset_type == 'work_order':
            if asset.get('assignee_id') == signer_public_key:
                return True
        
        # Owner can update
        if asset.get('owner') == signer_public_key:
            return True
        
        # TODO: Check if signer is super admin
        return False
