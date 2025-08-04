#!/usr/bin/env python3
"""
Simple Transaction Handler
A minimal working transaction handler for testing.
"""

import json
import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction


class SimpleTransactionHandler(TransactionHandler):
    """Simple transaction handler for testing."""
    
    def __init__(self):
        self._family_name = 'simple'
        self._family_versions = ['1.0']
        self._namespace = self._get_namespace()
    
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
        return hashlib.sha512('simple'.encode()).hexdigest()[:6]
    
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
                return self._handle_set(transaction, context, payload)
            elif action == 'get':
                return self._handle_get(transaction, context, payload)
            elif action == 'delete':
                return self._handle_delete(transaction, context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
        
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
    def _handle_set(self, transaction, context: Context, payload):
        """Handle 'set' action - store a key-value pair."""
        key = payload.get('key')
        value = payload.get('value')
        
        if not key:
            raise InvalidTransaction("'set' action requires 'key'")
        if not value:
            raise InvalidTransaction("'set' action requires 'value'")
        
        # Generate address
        address = self._get_address(key)
        
        # Create data to store
        data = {
            'key': key,
            'value': value,
            'signer': transaction.header.signer_public_key,
            'action': 'set'
        }
        
        # Store the data
        context.set_state({
            address: json.dumps(data).encode('utf-8')
        })
        
        print(f"✅ Set {key} = {value}")
        return {'status': 'success', 'key': key, 'value': value}
    
    def _handle_get(self, transaction, context: Context, payload):
        """Handle 'get' action - retrieve a value by key."""
        key = payload.get('key')
        
        if not key:
            raise InvalidTransaction("'get' action requires 'key'")
        
        # Generate address
        address = self._get_address(key)
        
        # Get the data
        entries = context.get_state([address])
        
        if entries:
            stored_data = json.loads(entries[0].data.decode('utf-8'))
            value = stored_data.get('value')
            print(f"📖 Retrieved {key} = {value}")
            return {'status': 'success', 'key': key, 'value': value}
        else:
            print(f"❌ Key '{key}' not found")
            raise InvalidTransaction(f"Key '{key}' not found")
    
    def _handle_delete(self, transaction, context: Context, payload):
        """Handle 'delete' action - remove a key-value pair."""
        key = payload.get('key')
        
        if not key:
            raise InvalidTransaction("'delete' action requires 'key'")
        
        # Generate address
        address = self._get_address(key)
        
        # Check if key exists
        entries = context.get_state([address])
        if not entries:
            raise InvalidTransaction(f"Key '{key}' not found")
        
        # Delete by setting to empty data
        context.set_state({address: b''})
        
        print(f"🗑️  Deleted {key}")
        return {'status': 'success', 'key': key, 'action': 'deleted'}
