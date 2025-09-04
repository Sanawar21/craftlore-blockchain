from typing import Any


from .. import BaseListener, EventType, EventContext, InvalidTransaction
from models.enums import AssetType
from models.classes.assets import (RawMaterial,)


class AssetCreationHandler(BaseListener):
    def __init__(self):
        super().__init__([EventType.ASSET_CREATED], priorities=[1000]) # run before every other listener

    def on_event(self, event: EventContext):
        # Handle asset creation event
        transaction = event.transaction
        context = event.context
        signature = event.signature
        payload = event.payload
        signer_public_key = event.signer_public_key

        fields: dict[str, Any] = payload.get("fields")
        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")

        fields = fields.copy() 

        fields["asset_owner"] = signer_public_key

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

