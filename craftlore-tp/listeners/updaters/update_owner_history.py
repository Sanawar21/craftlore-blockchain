from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount, SupplierAccount
from models.classes.assets import BaseAsset, RawMaterial, WorkOrder
from models.enums import AccountType, AssetType, EventType, SubEventType

class OwnerHistoryUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ASSET_CREATED, SubEventType.BATCH_CREATED],
            priorities=[0, 0]
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
        else:
            raise InvalidTransaction("Owner account does not exist for OwnerHistoryUpdater")

        # if event.event_type == EventType.ASSET_CREATED:
        owner_data["assets"].append(entity.uid)
      
        targets = [entity.uid]

        if entity.asset_type == AssetType.RAW_MATERIAL.value and isinstance(entity, RawMaterial):
            owner_data["raw_materials_created"].append(entity.uid)
        elif entity.asset_type == AssetType.WORK_ORDER.value and isinstance(entity, WorkOrder):
            targets.append(entity.assignee)
            owner_data["work_orders_issued"].append(entity.uid)

        owner_data["history"].append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        event.context.set_state({
            owner_address: self.serialize_for_state(owner_data)
        })

        event.add_data({
            "owner_address": owner_address,
            "owner": self.account_types[AccountType(owner_data["account_type"])].model_validate(owner_data)
        })
