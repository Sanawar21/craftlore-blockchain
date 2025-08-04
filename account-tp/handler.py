#!/usr/bin/env python3

import json
import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from subhandlers import SetValueSubHandler, GetValueSubHandler, DeleteValueSubHandler
from utils import AccountAddressGenerator

class CraftloreAccountTransactionHandler(TransactionHandler):
    """Craftlore Account Transaction Handler"""
    
    def __init__(self):
        self.address_generator = AccountAddressGenerator()
        self._family_name = self.address_generator.FAMILY_NAME
        self._family_versions = ['1.0']
        self._namespace = self.address_generator.get_namespace()
        self.set_value_subhandler = SetValueSubHandler(self._get_address)
        self.get_value_subhandler = GetValueSubHandler(self._get_address)
        self.delete_value_subhandler = DeleteValueSubHandler(self._get_address)

    
    @property
    def family_name(self):
        return self._family_name
    
    @property
    def family_versions(self):
        return self._family_versions
    
    @property
    def namespaces(self):
        return [self._namespace]
    
    def _get_namespace(self):
        """Get the 6-character namespace for this transaction family."""
        return hashlib.sha512('craftlore-account'.encode()).hexdigest()[:6]
    
    def _get_address(self, key):
        """Generate a 70-character address from a key."""
        return self._namespace + hashlib.sha512(key.encode()).hexdigest()[:64]
    
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
            
            if action == 'set':
                return self.set_value_subhandler.apply(transaction, context, payload)
            elif action == 'get':
                return self.get_value_subhandler.apply(transaction, context, payload)
            elif action == 'delete':
                return self.delete_value_subhandler.apply(transaction, context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
        
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
