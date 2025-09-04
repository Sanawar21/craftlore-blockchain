from sawtooth_sdk.processor.exceptions import InvalidTransaction
from utils.address_generator import CraftLoreAddressGenerator
from utils.serialization import SerializationHelper
from abc import ABC, abstractmethod

from models.enums import EventType, AccountType, AssetType
from events import EventContext

from models.classes.accounts import *
from models.classes.assets import *

class BaseListener(ABC):
    """Base class for all event listeners."""

    def __init__(self, event_types: list[EventType], priorities: list[int]):
        self.address_generator = CraftLoreAddressGenerator()
        self.serializer = SerializationHelper()
        self.event_types: list[EventType] = event_types
        self.priorities: list[int] = priorities
        
        self.account_types = {
            AccountType.SUPPLIER: SupplierAccount
        }
        self.asset_types = {
            AssetType.RAW_MATERIAL: RawMaterial
        }


    def serialize_for_state(self, data):
        return self.serializer.to_bytes(data)

    @abstractmethod
    def on_event(self, event: EventContext):
        """Handle an event."""
        pass

