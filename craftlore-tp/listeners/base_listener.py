from typing import List, Dict, Union, Tuple

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
            AccountType.ARTISAN: ArtisanAccount,
            AccountType.BUYER: BuyerAccount
        }
        self.asset_types: Dict[AssetType, BaseAsset] = {
            AssetType.RAW_MATERIAL: RawMaterial,
            AssetType.WORK_ORDER: WorkOrder,
            AssetType.PRODUCT_BATCH: ProductBatch,
            AssetType.PACKAGING: Packaging,
            AssetType.PRODUCT: Product,
            AssetType.LOGISTICS: Logistics
        }

    def get_asset(self, asset_id: str, context: EventContext) -> Tuple[BaseAsset, str]:
        asset_address = self.address_generator.generate_asset_address(asset_id)
        entries = context.context.get_state([asset_address])
        if entries:
            asset_data = self.serializer.from_bytes(entries[0].data)
            asset = self.asset_types[AssetType(asset_data["asset_type"])].model_validate(asset_data)
            return asset, asset_address
        else:
            raise InvalidTransaction(f"Asset with ID {asset_id} does not exist.")

    def get_account(self, public_key: str, context: EventContext) -> Tuple[BaseAccount, str]:
        account_address = self.address_generator.generate_account_address(public_key)
        entries = context.context.get_state([account_address])
        if entries:
            account_data = self.serializer.from_bytes(entries[0].data)
            account = self.account_types[AccountType(account_data["account_type"])].model_validate(account_data)
            return account, account_address
        else:
            raise InvalidTransaction(f"Account with public key {public_key} does not exist.")

    def serialize_for_state(self, data):
        return self.serializer.to_bytes(data)

    @abstractmethod
    def on_event(self, event: EventContext):
        """Handle an event."""
        pass

