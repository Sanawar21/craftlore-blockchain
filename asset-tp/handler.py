#!/usr/bin/env python3
"""
AssetTransactionHandler for CraftLore Asset TP.

This handler manages asset-related transactions including:
- Asset creation (raw materials, products, work orders, warranties)
- Asset transfers and ownership changes
- Asset locking/unlocking for workflow control
- Asset updates and modifications
- Warranty registration and management
- Certification tracking
- Bulk operations for efficiency
- Product creation from batches
- Cross-entity relationship management

The handler integrates with the CraftLore ecosystem supporting flows from
raw material sourcing through finished product resale.
"""

import hashlib
import json

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction

# Import CraftLore components
from utils.address_generator import AssetAddressGenerator
from utils.serialization import SerializationHelper

# Import modular handlers
from handlers import (
    AssetCreationHandler,
    AssetTransferHandler,
    AssetWorkflowHandler,
    AssetCertificationHandler
)

# Transaction handler family information
FAMILY_NAME = 'craftlore-asset'
FAMILY_VERSION = '1.0'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]


class AssetTransactionHandler(TransactionHandler):
    """Transaction handler for CraftLore Asset operations."""

    def __init__(self):
        """Initialize handler with utilities and sub-handlers."""
        self.address_generator = AssetAddressGenerator()
        self.serializer = SerializationHelper()
        
        # Initialize modular handlers
        self.creation_handler = AssetCreationHandler(self.address_generator, self.serializer)
        self.transfer_handler = AssetTransferHandler(self.address_generator, self.serializer)
        self.workflow_handler = AssetWorkflowHandler(self.address_generator, self.serializer)
        self.certification_handler = AssetCertificationHandler(self.address_generator, self.serializer)

    @property
    def family_name(self):
        """Return transaction family name."""
        return FAMILY_NAME

    @property
    def family_versions(self):
        """Return list of transaction family versions."""
        return [FAMILY_VERSION]

    @property
    def namespaces(self):
        """Return list of namespaces this handler addresses."""
        return [NAMESPACE]

    def apply(self, transaction, context: Context):
        """Apply the transaction to the state."""
        try:
            # Parse transaction payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            action = payload.get('action')
            
            # Add signer public key to payload for permission checks
            payload['signer_public_key'] = transaction.header.signer_public_key
            
            # Route to appropriate handler method
            if action == 'create_asset':
                return self.creation_handler.create_asset(context, payload)
            elif action == 'create_products_from_batch':
                return self.creation_handler.create_products_from_batch(context, payload)
            elif action == 'transfer_asset':
                return self.transfer_handler.transfer_asset(context, payload)
            elif action == 'bulk_transfer':
                return self.transfer_handler.bulk_transfer(context, payload)
            elif action == 'accept_asset':
                return self.transfer_handler.accept_asset(context, payload)
            elif action == 'lock_asset':
                return self.workflow_handler.lock_asset(context, payload)
            elif action == 'unlock_asset':
                return self.workflow_handler.unlock_asset(context, payload)
            elif action == 'delete_asset':
                return self.workflow_handler.delete_asset(context, payload)
            elif action == 'update_asset':
                return self.workflow_handler.update_asset(context, payload)
            elif action == 'register_warranty':
                return self.certification_handler.register_warranty(context, payload)
            elif action == 'update_certification':
                return self.certification_handler.update_certification(context, payload)
            elif action == 'update_sustainability':
                return self.certification_handler.update_sustainability(context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
                
        except json.JSONDecodeError as e:
            raise InvalidTransaction(f"Invalid payload format: {str(e)}")
        except Exception as e:
            raise InternalError(f"Transaction processing failed: {str(e)}")
