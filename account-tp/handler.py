#!/usr/bin/env python3

import json
import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from subhandlers import CreateAccountSubHandler
from utils import AccountAddressGenerator

class CraftloreAccountTransactionHandler(TransactionHandler):
    """Craftlore Account Transaction Handler"""
    
    def __init__(self):
        self.address_generator = AccountAddressGenerator()
        self._family_name = self.address_generator.FAMILY_NAME
        self._family_versions = ['1.0']
        self._namespace = self.address_generator.get_namespace()
        self.create_account_subhandler = CreateAccountSubHandler()

    @property
    def family_name(self):
        return self._family_name
    
    @property
    def family_versions(self):
        return self._family_versions
    
    @property
    def namespaces(self):
        return [self._namespace]
    
    def apply(self, transaction, context: Context):
        """Apply the transaction."""
        print(f"📨 Transaction received: {transaction.signature}")
        
        try:
            # Parse the payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            action = payload.get('action')
            
            if not action:
                raise InvalidTransaction("Transaction must specify an action")
            
            print(f"🔄 Processing action: {action}")
            
            if action == 'account_create':
                return self.create_account_subhandler.apply(transaction, context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
        
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
