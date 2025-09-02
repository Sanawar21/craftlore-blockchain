from pydantic import BaseModel
from typing import Any, Dict, Callable
from collections import defaultdict
from sawtooth_sdk.processor.context import Context
import json

from models.enums import EventType


class EventContext:
    def __init__(self, event_type: EventType, transaction: Any, context: Context):
        self.event_type = event_type
        self.generated_data = {}
        self.transaction = transaction
        self.context = context
        self.signature: str = transaction.signature
        self.payload: dict[str, Any] = json.loads(transaction.payload.decode('utf-8'))
        self.signer_public_key: str = transaction.header.signer_public_key

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the shared generated_data dictionary."""
        self.generated_data[key] = value

    def get_data(self, key: str) -> Any:
        """Retrieve data from the shared generated_data dictionary."""
        return self.generated_data.get(key)
    

class EventsManager:
    def __init__(self):
        self.listeners: Dict[EventType, list] = defaultdict(list)

    def register(self, event_type: EventType, listener):
        for event_type, priority in zip(listener.event_types, listener.priorities):
            self.listeners[event_type].append((priority, listener))
            self.listeners[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def propagate(self, event_type: EventType, transaction, context: Context):
        context_ = EventContext(event_type=event_type, transaction=transaction, context=context)
        for _, listener in self.listeners[event_type]:
            listener.on_event(context_)  # Pass context; handlers add/get data
        return context_