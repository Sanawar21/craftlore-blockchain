from .. import BaseListener, EventType, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount, SupplierAccount
from models.classes.assets import BaseAsset, RawMaterial
from models.enums import AccountType, AssetType

class OwnerHistoryUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ASSET_CREATED],
            priorities=[0]
        )  # default priority

    def on_event(self, event: EventContext):
        entity: BaseAsset = event.get_data("entity")
        entity_address = event.get_data("entity_address")

        if not entity or not entity_address:
            raise InvalidTransaction("Entity data or address not found in event context for OwnerHistoryUpdater")

        owner_address = self.address_generator.generate_account_address(entity.asset_owner)
        entries = event.context.get_state([owner_address])  # Ensure owner account exists

        if entries:
            owner_data = self.serializer.from_bytes(entries[0].data)

        if event.event_type == EventType.ASSET_CREATED:
            owner_data["assets"].append(entity.uid)
      
        owner_data["history"].append({
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [entity.uid],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        event.context.set_state({
            entity_address: self.serialize_for_state(owner_data)
        })

        event.add_data({
            "owner_address": owner_address,
            "owner": self.account_types[owner_data["account_type"]].model_validate(owner_data)
        })
