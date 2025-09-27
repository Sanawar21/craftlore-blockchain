from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import RawMaterial, ProductBatch
from models.enums import BatchStatus, EventType


class ValidateRawMaterialAddition(BaseListener):
    def __init__(self):
        super().__init__([EventType.ADD_RAW_MATERIAL], priorities=[-100])  # run after updating owner history

    def on_event(self, event: EventContext):
        raw_material: RawMaterial = event.get_data("raw_material")
        batch: ProductBatch = event.get_data("entity")
        owner: BaseAccount = event.get_data("owner")
        usage_quantity = event.payload.get("fields", {}).get("usage_quantity")

        if raw_material.is_deleted:
            raise InvalidTransaction("Raw material is deleted")
        if batch.is_deleted:
            raise InvalidTransaction("Batch is deleted")
        if owner.is_deleted:
            raise InvalidTransaction("Owner account is deleted")
        if raw_material.asset_owner != owner.public_key:
            raise InvalidTransaction("Owner account does not own the raw material")
        if batch.asset_owner != owner.public_key:
            raise InvalidTransaction("Owner account does not own the batch")
        if batch.status != BatchStatus.IN_PROGRESS:
            raise InvalidTransaction("Can only add raw materials to batches that are 'in progress'")
        if usage_quantity <= 0:
            raise InvalidTransaction("Usage quantity must be a positive number")
        if usage_quantity > raw_material.quantity:
            raise InvalidTransaction("Usage quantity cannot exceed available raw material quantity")
        