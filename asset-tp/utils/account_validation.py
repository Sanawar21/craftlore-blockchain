#!/usr/bin/env python3
"""
Account validation utilities for Asset TP.

This module provides functionality to validate account types and permissions
by checking account-tp state from within asset-tp operations.
"""

from typing import Optional, Dict
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Import account-tp utilities
from accountTPutils.address_generator import AccountAddressGenerator
from accountTPutils.serialization import SerializationHelper


class AccountValidator:
    """Validates account types and permissions for asset operations."""
    
    def __init__(self):
        self.account_address_generator = AccountAddressGenerator()
        self.account_serializer = SerializationHelper()
    
    def get_account_by_public_key(self, context: Context, public_key: str) -> Optional[Dict]:
        """Get account information by public key from account-tp state."""
        try:
            account_address = self.account_address_generator.generate_account_address(public_key)
            entries = context.get_state([account_address])
            
            if entries:
                return self.account_serializer.from_bytes(entries[0].data)
            return None
        except Exception as e:
            print(f"Warning: Could not retrieve account for {public_key}: {str(e)}")
            return None
    
    def validate_supplier_account(self, context: Context, public_key: str) -> None:
        """Validate that the account is a SupplierAccount."""
        account = self.get_account_by_public_key(context, public_key)
        
        if not account:
            raise InvalidTransaction(f"Account not found for public key: {public_key}")
        
        account_type = account.get('account_type')
        if account_type != 'supplier':
            raise InvalidTransaction(
                f"Only SupplierAccount can create raw material assets. Found account type: {account_type}"
            )
        
        # Check if account is approved
        auth_status = account.get('authentication_status')
        if auth_status != 'approved':
            raise InvalidTransaction(
                f"Account must be approved to create assets. Current status: {auth_status}"
            )
        
        # Check if account is not deleted
        if account.get('is_deleted', False):
            raise InvalidTransaction("Cannot perform operations with a deleted account")
    
    def validate_artisan_or_workshop_account(self, context: Context, public_key: str) -> None:
        """Validate that the account is an Artisan or Workshop account."""
        account = self.get_account_by_public_key(context, public_key)
        
        if not account:
            raise InvalidTransaction(f"Account not found for public key: {public_key}")
        
        account_type = account.get('account_type')
        if account_type not in ['artisan', 'workshop']:
            raise InvalidTransaction(
                f"Only Artisan or Workshop accounts can be assignees of work orders. Found account type: {account_type}"
            )
        
        # Check if account is approved
        auth_status = account.get('authentication_status')
        if auth_status != 'approved':
            raise InvalidTransaction(
                f"Account must be approved to be assigned work orders. Current status: {auth_status}"
            )
        
        # Check if account is not deleted
        if account.get('is_deleted', False):
            raise InvalidTransaction("Cannot assign work orders to a deleted account")
    
    def get_account_type(self, context: Context, public_key: str) -> Optional[str]:
        """Get the account type for a public key."""
        account = self.get_account_by_public_key(context, public_key)
        return account.get('account_type') if account else None
    
    def is_account_approved(self, context: Context, public_key: str) -> bool:
        """Check if an account is approved."""
        account = self.get_account_by_public_key(context, public_key)
        if not account:
            return False
        
        return (account.get('authentication_status') == 'approved' and 
                not account.get('is_deleted', False))
