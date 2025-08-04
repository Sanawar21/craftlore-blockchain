from .base import BaseSubHandler, InvalidTransaction, Context
import json

class DeleteValueSubHandler(BaseSubHandler):
    """Subhandler for deleting a value in the account transaction processor."""

    def apply(self, transaction, context: Context, payload: dict):
        """Handle 'delete' action - remove a key-value pair."""
        key = payload.get('key')
        
        if not key:
            raise InvalidTransaction("'delete' action requires 'key'")
        
        # Generate address
        address = self.get_address(key)
        
        # Check if key exists
        entries = context.get_state([address])
        if not entries:
            raise InvalidTransaction(f"Key '{key}' not found")
        
        # Delete by setting to empty data
        context.set_state({address: b''})
        
        print(f"🗑️  Deleted {key}")
        return {'status': 'success', 'key': key, 'action': 'deleted'}
