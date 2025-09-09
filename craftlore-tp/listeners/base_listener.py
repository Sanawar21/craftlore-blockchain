from typing import List, Dict, Union

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from utils.address_generator import CraftLoreAddressGenerator
from utils.serialization import SerializationHelper
from abc import ABC, abstractmethod

from models.enums import EventType, AccountType, AssetType, SubEventType
from events import EventContext

from models.classes.accounts import *
from models.classes.assets import *

class BaseListener(ABC):
    """Base class for all event listeners."""

    def __init__(self, event_types: List[Union[EventType, SubEventType]], priorities: List[int]):
        self.address_generator = CraftLoreAddressGenerator()
        self.serializer = SerializationHelper()
        self.event_types = event_types
        self.priorities = priorities
        
        self.account_types: Dict[AccountType, BaseAccount] = {
            AccountType.SUPPLIER: SupplierAccount,
            AccountType.ARTISAN: ArtisanAccount
        }
        self.asset_types: Dict[AssetType, BaseAsset] = {
            AssetType.RAW_MATERIAL: RawMaterial,
            AssetType.WORK_ORDER: WorkOrder,
            AssetType.PRODUCT_BATCH: ProductBatch,
            AssetType.PACKAGING: Packaging,
            # AssetType.PRODUCT: Product
        }


    def serialize_for_state(self, data):
        return self.serializer.to_bytes(data)

    @abstractmethod
    def on_event(self, event: EventContext):
        """Handle an event."""
        pass

