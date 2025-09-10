from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import ProductBatch, RawMaterial
from models.enums import AssetType, SubEventType, EventType, WorkOrderStatus, BatchStatus

class AddToBatch(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ADD_RAW_MATERIAL],
            priorities=[100]
        )  # default priority

    def __load_asset_by_id(self, context: EventContext, asset_id: str, asset_type: AssetType) -> Any:
        asset_address = self.address_generator.generate_asset_address(asset_id)
        entries = context.context.get_state([asset_address])
        if entries:
            asset_data = self.serializer.from_bytes(entries[0].data)
            return asset_data
        else:
            raise InvalidTransaction(f"{asset_type.value.replace('_', ' ').title()} with ID {asset_id} does not exist")

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})
        if "batch" not in fields or "raw_material" not in fields or "usage_quantity" not in fields:
            raise InvalidTransaction("Payload must include 'batch', 'raw_material' and 'usage_quantity' fields")

        batch_id = fields["batch"]
        raw_material_id = fields["raw_material"]

        batch_data = self.__load_asset_by_id(event, batch_id, AssetType.PRODUCT_BATCH)
        raw_material_data = self.__load_asset_by_id(event, raw_material_id, AssetType.RAW_MATERIAL)

        batch: ProductBatch = ProductBatch.model_validate(batch_data)
        raw_material: RawMaterial = RawMaterial.model_validate(raw_material_data)

        batch.raw_materials.append({raw_material.uid: fields["usage_quantity"]})
        raw_material.batches_used_in.append({ batch.uid: fields["usage_quantity"] })

        history_entry = {
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [batch.uid, raw_material.uid],
            "transaction": event.signature,
            "timestamp": event.timestamp
        }

        batch.history.append(history_entry)
        raw_material.history.append(history_entry)

        batch_address = self.address_generator.generate_asset_address(batch.uid)
        raw_material_address = self.address_generator.generate_asset_address(raw_material.uid)

        event.context.set_state({
            batch_address: self.serialize_for_state(batch.model_dump()),
            raw_material_address: self.serialize_for_state(raw_material.model_dump())
        })

        event.add_data({
            "entity": batch,
            "raw_material": raw_material
        })

