from typing import Any


from .. import BaseListener, EventContext, InvalidTransaction
from models.enums import AssetType, EventType, SubEventType
from models.classes.assets import WorkOrder


class AssetCreationHandler(BaseListener):
    def __init__(self):
        super().__init__([EventType.ASSET_CREATED, SubEventType.BATCH_CREATED, SubEventType.LOGISTICS_CREATED], priorities=[1000, 1000, 0]) # run before every other listener

    def on_event(self, event: EventContext):
        # Handle asset creation event
        context = event.context
        payload = event.payload
        signer_public_key = event.signer_public_key

        fields: dict[str, Any] = payload.get("fields")

        # if event.event_type == SubEventType.BATCH_CREATED:
        #     fields = {"asset_type": AssetType.PRODUCT_BATCH.value}
        # elif not fields:
        #     raise InvalidTransaction("Missing 'fields' key in payload")

        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")

        if event.event_type == SubEventType.BATCH_CREATED:
            fields["asset_type"] = AssetType.PRODUCT_BATCH.value
        elif event.event_type == SubEventType.LOGISTICS_CREATED:
            fields = fields.get("logistics", {})
            fields["asset_type"] = AssetType.LOGISTICS.value

        fields = fields.copy() 

        fields["asset_owner"] = signer_public_key
        fields["created_timestamp"] = event.timestamp

        if fields.get("asset_type") == AssetType.RAW_MATERIAL.value:
            fields["supplier"] = event.signer_public_key
        elif fields.get("asset_type") == AssetType.WORK_ORDER.value:
            fields["assigner"] = event.signer_public_key
        elif fields.get("asset_type") == AssetType.PRODUCT_BATCH.value:
            work_order: WorkOrder = event.get_data("entity")
            fields["producer"] = event.signer_public_key
            fields["quantity"] = work_order.requested_quantity
            fields["unit"] = work_order.requested_quantity_unit
            fields["product_description"] = work_order.product_description
            fields["specifications"] = work_order.specifications
            fields["design_reference"] = work_order.design_reference
            fields["special_instructions"] = work_order.special_instructions
            fields["work_order"] = work_order.uid
        elif fields.get("asset_type") == AssetType.LOGISTICS.value: 
            transfer_fields = payload.get("fields", {})
            if event.event_type == EventType.ASSET_CREATED:
                raise InvalidTransaction("Logistic assets can only be created when transferring assets.")
            fields["assets"] = transfer_fields.get("assets")
            fields["recipient"] = transfer_fields.get("recipient")
            fields["transaction"] = event.signature
        elif fields.get("asset_type") == AssetType.PRODUCT.value:
            raise InvalidTransaction("Direct creation of Product assets is not supported. Create a ProductBatch instead or accept a WorkOrder.")

        # Process the fields as needed
        asset_type_str = fields.get("asset_type")
        asset_type = AssetType(asset_type_str)
        asset_class = self.asset_types.get(asset_type)

        if not asset_class:
            raise InvalidTransaction(f"Unsupported asset type: {asset_type_str}")

        asset = asset_class.model_validate(fields)
        asset_data = asset.model_dump()

        asset_address = self.address_generator.generate_asset_address(asset.uid)

        if context.get_state([asset_address]):
            raise InvalidTransaction("Asset already exists")

        context.set_state({
            asset_address: self.serialize_for_state(asset_data)
        })

        event.add_data({
            "entity_address": asset_address,
            "entity": asset
        })

