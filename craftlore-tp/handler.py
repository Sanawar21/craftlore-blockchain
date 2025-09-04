#!/usr/bin/env python3
"""
Unified Transaction Handler for CraftLore Combined TP.
Handles both account and asset operations in a single transaction processor.
"""

import json
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from utils.address_generator import CraftLoreAddressGenerator
from utils.serialization import SerializationHelper
from listeners import registered_listeners
from events import EventsManager


class CraftLoreTransactionHandler(TransactionHandler):
    """Unified transaction handler for CraftLore account and asset operations."""
    
    def __init__(self):
        self._family_name = 'craftlore'
        self._family_versions = ['1.0']
        
        self.address_generator = CraftLoreAddressGenerator()
        self.serializer = SerializationHelper()
        self._namespaces = [self.address_generator.get_namespace()]
        
        self.events_manager = EventsManager()
        for listener in registered_listeners:
            self.events_manager.register(listener)
    
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
        try:
            # Parse payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            event = payload.get('event')
            
            if not event:
                raise InvalidTransaction("Transaction must specify an event from `models.enums.EventType`")

            print(f"Event recieved: {event}")

            self.events_manager.propagate(event, transaction, context)

        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
