from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.assets import ProductBatch, RawMaterial, UsageRecord
from models.enums import EventType

class AddToBatch(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ADD_RAW_MATERIAL],
            priorities=[100]
        )  # default priority

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})
        if "batch" not in fields or "raw_material" not in fields or "usage_quantity" not in fields:
            raise InvalidTransaction("Payload must include 'batch', 'raw_material' and 'usage_quantity' fields")

        batch_id = fields["batch"]
        raw_material_id = fields["raw_material"]

        batch, batch_address = self.get_asset(batch_id, event)
        raw_material, raw_material_address = self.get_asset(raw_material_id, event)
        assert isinstance(batch, ProductBatch), "Asset must be a ProductBatch"
        assert isinstance(raw_material, RawMaterial), "Asset must be a RawMaterial"

        batch.raw_materials.append(UsageRecord(
            batch=batch.uid,
            usage_quantity=fields["usage_quantity"],
            raw_material=raw_material.uid
        ))
        raw_material.batches_used_in.append(UsageRecord(
            batch=batch.uid,
            usage_quantity=fields["usage_quantity"],
            raw_material=raw_material.uid
        ))
        raw_material.processor_public_key = event.signer_public_key

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

        event.context.set_state({
            batch_address: self.serialize_for_state(batch),
            raw_material_address: self.serialize_for_state(raw_material)
        })

        event.add_data({
            "entity": batch,
            "raw_material": raw_material
        })

