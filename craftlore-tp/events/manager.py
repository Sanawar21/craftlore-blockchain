from typing import Any, Dict
from collections import defaultdict
from sawtooth_sdk.processor.context import Context
import json

from models.enums import EventType, SubEventType


class EventContext:
    def __init__(self, event_type: EventType, transaction: Any, context: Context):
        self.event_type = event_type
        self.transaction = transaction
        self.context = context
        self.signature: str = transaction.signature
        self.payload: dict[str, Any] = json.loads(transaction.payload.decode('utf-8'))
        self.signer_public_key: str = transaction.header.signer_public_key
        self.timestamp = self.payload.get("timestamp", None)  # Assuming timestamp is part of the payload
        self.__generated_data = {}

    def add_data(self, data: dict) -> None:
        """Add data to the shared __generated_data dictionary."""
        self.__generated_data.update(data)


    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve data from the shared __generated_data dictionary."""
        return self.__generated_data.get(key, default)
    

class EventsManager:
    def __init__(self):
        self.listeners: Dict[EventType, list] = defaultdict(list)

    def register(self, listener):
        assert len(listener.event_types) == len(listener.priorities), f"Each event type must have a corresponding priority. Listener: {listener.__class__.__name__}"
        for event_type, priority in zip(listener.event_types, listener.priorities):
            self.listeners[event_type].append((priority, listener))
            
    def __should_propagate(self, event: EventContext, sub_event: SubEventType) -> bool:
        """Check if the conditions for propagating the sub-event are met."""
        if sub_event == SubEventType.BATCH_CREATED:
            return event.event_type == EventType.WORK_ORDER_ACCEPTED
        elif sub_event == SubEventType.WORK_ORDER_CREATED:
            if event.payload.get("fields", {}).get("asset_type") == "work_order":
                return event.event_type == EventType.ASSET_CREATED
        elif sub_event == SubEventType.PACKAGING_CREATED:
            if event.payload.get("fields", {}).get("asset_type") == "packaging":
                return event.event_type == EventType.ASSET_CREATED
        elif sub_event == SubEventType.LOGISTICS_CREATED:
            return event.event_type == EventType.ASSETS_TRANSFERRED
        elif sub_event == SubEventType.SUB_ASSIGNMENT_CREATED:
            if event.payload.get("fields", {}).get("asset_type") == "sub_assignment":
                return event.event_type == EventType.ASSET_CREATED
        return False

    def propagate(self, event_type: EventType, transaction, context: Context):
        events = [event_type]
        context_ = EventContext(event_type=event_type, transaction=transaction, context=context)

        for sub_event in SubEventType:
            if self.__should_propagate(context_, sub_event):
                events.append(sub_event)

        for event in events:
            event_type = event
            context_.event_type = event_type
            self.listeners[event_type].sort(key=lambda x: x[0], reverse=True)
            print(f"Propagating event: {event_type} to {len(self.listeners[event_type])} listeners")
            for _, listener in self.listeners[event_type]: 
                print(f"Executing listener: {listener.__class__.__name__} for event: {event_type}")
                # try:
                listener.on_event(context_)  # Pass context; handlers add/get data
                # except Exception as e:
                #     raise InvalidTransaction(f"Error in listener {listener.__class__.__name__}: {str(e)} Execution order: {[(p, l.__class__.__name__) for p, l in self.listeners[event_type]]}")

        return context_