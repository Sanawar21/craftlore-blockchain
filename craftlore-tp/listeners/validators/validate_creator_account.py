from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import BaseAsset
from models.enums import AccountType, AssetType, EventType


class ValidateCreatorAccount(BaseListener):
    def __init__(self):
        super().__init__([EventType.ASSET_CREATED], priorities=[-100])  # run after updating owner history
        self.valid_creators = {
            AccountType.SUPPLIER: [AssetType.RAW_MATERIAL, AssetType.WORK_ORDER],
            AccountType.ARTISAN: [AssetType.WORK_ORDER, AssetType.PRODUCT_BATCH],
            # AccountType.WORKSHOP: [AssetType.WORK_ORDER, AssetType.PRODUCT_BATCH]
        }

    def on_event(self, event: EventContext):
        creator: BaseAccount = event.get_data("owner")
        asset: BaseAsset = event.get_data("entity")

        if not creator:
            raise InvalidTransaction("Account data not found in event context for ValidateCreatorAccount")

        if creator.account_type not in self.valid_creators:
            raise InvalidTransaction(f"Account type {creator.account_type} cannot create any assets")

        if creator.is_deleted:
            raise InvalidTransaction("Deleted accounts cannot create assets")
        
        if asset.asset_type not in self.valid_creators[creator.account_type]:
            raise InvalidTransaction(f"Account type {creator.account_type} cannot create asset type {asset.asset_type}")