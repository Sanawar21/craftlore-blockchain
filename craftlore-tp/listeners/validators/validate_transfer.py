from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import BaseAsset
from models.enums import BatchStatus, EventType, SubEventType, AssetType

from typing import List

class ValidateTransfer(BaseListener):
    def __init__(self):
        super().__init__([EventType.ASSETS_TRANSFERRED], priorities=[-200])  # run after updating owner history

    def on_event(self, event: EventContext):
        assets: List[BaseAsset] = event.get_data("assets")
        recipient: BaseAccount = event.get_data("recipient")
        old_owner: BaseAccount = event.get_data("old_owner")

        if not assets:
            raise InvalidTransaction("No assets found for validation in ValidateTransfer")
        if not recipient:
            raise InvalidTransaction("New owner account not found for validation in ValidateTransfer")
        if not old_owner:
            raise InvalidTransaction("Old owner account not found for validation in ValidateTransfer")  

        for asset in assets:
            if asset.is_deleted:
                raise InvalidTransaction(f"Asset {asset.uid} is deleted")
            if asset.asset_type == AssetType.RAW_MATERIAL:
                if asset.processor_public_key:
                    raise InvalidTransaction("Processed raw materials cannot be transferred")
            if asset.asset_type == AssetType.WORK_ORDER:
                raise InvalidTransaction("Work orders cannot be transferred")
            if asset.asset_type == AssetType.PRODUCT_BATCH:
                raise InvalidTransaction("Batches cannot be transferred")
            if asset.asset_type == AssetType.LOGISTICS:
                raise InvalidTransaction("Logistics assets cannot be transferred")

        if recipient.is_deleted:
            raise InvalidTransaction("New owner account is deleted")
        if old_owner.is_deleted:
            raise InvalidTransaction("Old owner account is deleted")
        



