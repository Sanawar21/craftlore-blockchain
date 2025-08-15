#!/usr/bin/env python3
"""
Unified Transaction Handler for CraftLore Combined TP.
Handles both account and asset operations in a single transaction processor.
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from utils.address_generator import CraftLoreAddressGenerator
from utils.serialization import SerializationHelper
from handlers import (
    AccountHandler,
    AssetCreationHandler,
    AssetTransferHandler,
    AssetWorkflowHandler,
    AssetCertificationHandler
)


class CraftLoreTransactionHandler(TransactionHandler):
    """Unified transaction handler for CraftLore account and asset operations."""
    
    def __init__(self):
        self._family_name = 'craftlore'
        self._family_versions = ['1.0']
        
        self.address_generator = CraftLoreAddressGenerator()
        self.serializer = SerializationHelper()
        self._namespaces = [self.address_generator.get_namespace()]
        
        # Initialize handlers
        self.account_handler = AccountHandler(self.address_generator, self.serializer)
        self.asset_creation_handler = AssetCreationHandler(self.address_generator, self.serializer)
        self.asset_transfer_handler = AssetTransferHandler(self.address_generator, self.serializer)
        self.asset_workflow_handler = AssetWorkflowHandler(self.address_generator, self.serializer)
        self.asset_certification_handler = AssetCertificationHandler(self.address_generator, self.serializer)
    
    @property
    def family_name(self):
        return self._family_name
    
    @property
    def family_versions(self):
        return self._family_versions
    
    @property
    def namespaces(self):
        return self._namespaces
    
    def apply(self, transaction, context: Context):
        """Apply unified account and asset transactions."""
        print(f"Transaction received: {transaction.signature}")
        try:
            # Parse payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            action = payload.get('action')
            
            if not action:
                raise InvalidTransaction("Transaction must specify an action")
            
            # Add signer public key to payload for permission checks
            payload['signer_public_key'] = transaction.header.signer_public_key
            
            # Route to appropriate handler based on action type
            if action.startswith('account_'):
                return self.account_handler.handle_account_operation(context, action, payload)
            elif action in ['create_asset', 'create_products_from_batch']:
                return self.asset_creation_handler.create_asset(context, payload) if action == 'create_asset' else self.asset_creation_handler.create_products_from_batch(context, payload)
            elif action in ['transfer_asset', 'bulk_transfer', 'accept_asset', 'sub_assign_work_order']:
                if action == 'transfer_asset':
                    return self.asset_transfer_handler.transfer_asset(context, payload)
                elif action == 'bulk_transfer':
                    return self.asset_transfer_handler.bulk_transfer(context, payload)
                elif action == 'accept_asset':
                    return self.asset_transfer_handler.accept_asset(context, payload)
                elif action == 'sub_assign_work_order':
                    return self.asset_transfer_handler.sub_assign_work_order(context, payload)
            elif action in ['lock_asset', 'unlock_asset', 'delete_asset', 'update_asset']:
                if action == 'lock_asset':
                    return self.asset_workflow_handler.lock_asset(context, payload)
                elif action == 'unlock_asset':
                    return self.asset_workflow_handler.unlock_asset(context, payload)
                elif action == 'delete_asset':
                    return self.asset_workflow_handler.delete_asset(context, payload)
                elif action == 'update_asset':
                    return self.asset_workflow_handler.update_asset(context, payload)
            elif action in ['register_warranty', 'update_certification', 'update_sustainability']:
                if action == 'register_warranty':
                    return self.asset_certification_handler.register_warranty(context, payload)
                elif action == 'update_certification':
                    return self.asset_certification_handler.update_certification(context, payload)
                elif action == 'update_sustainability':
                    return self.asset_certification_handler.update_sustainability(context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
    def get_account_by_public_key(self, context: Context, public_key: str) -> Optional[Dict]:
        """Helper method to get account by public key - used by asset operations."""
        return self.account_handler._get_account_by_public_key(context, public_key)
    
    def validate_account_permissions(self, context: Context, signer_public_key: str, required_account_types: List[str]) -> bool:
        """Helper method to validate account permissions for asset operations."""
        account = self.get_account_by_public_key(context, signer_public_key)
        if not account:
            return False
        
        account_type = account.get('account_type')
        authentication_status = account.get('authentication_status')
        
        # Check if account is authenticated
        if authentication_status != 'approved':
            return False
        
        # Check if account type is allowed
        return account_type in required_account_types
    
    def get_all_inputs_outputs(self) -> List[str]:
        """Get all possible input/output addresses for this TP."""
        return [self.address_generator.get_namespace()]  # Just use namespace prefix
    
    def get_account_addresses(self) -> List[str]:
        """Get all account-related address patterns."""
        return self.address_generator.get_all_account_addresses()
    
    def get_asset_addresses(self) -> List[str]:
        """Get all asset-related address patterns."""
        return self.address_generator.get_all_asset_addresses()
    
    def get_index_addresses(self) -> List[str]:
        """Get all index-related address patterns."""
        return self.address_generator.get_all_index_addresses()
