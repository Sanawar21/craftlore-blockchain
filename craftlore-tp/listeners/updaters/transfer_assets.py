from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import RawMaterial, Packaging, BaseAsset
from models.enums import AccountType, AssetType, SubEventType, EventType, WorkOrderStatus, BatchStatus

class AssetsTransferrer(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ASSETS_TRANSFERRED],
            priorities=[1000]
        )  

    def on_event(self, event: EventContext):
        payload = event.payload

        fields = payload.get("fields", {})
        asset_ids = fields.get("assets")
        recipient = fields.get("recipient")
        logistics = fields.get("logistics")

        if not asset_ids or not recipient:
            raise InvalidTransaction("Missing 'assets' or 'recipient' in payload fields")

        assets = []
        for asset_id in asset_ids:
            asset, asset_address = self.get_asset(asset_id, event)
            assets.append((asset, asset_address))
    
        asset_uids = [asset.uid for asset, _ in assets]

        history = {
                "source": self.__class__.__name__,
                "event": event.event_type.value,
                "actor": event.signer_public_key,
                "targets": asset_uids + [recipient, logistics["uid"]],
                "transaction": event.signature,
                "timestamp": event.timestamp
            }
        
        for asset, asset_address in assets.copy():
            if isinstance(asset, Packaging):
                for product_id in asset.products:
                    product_asset, product_address = self.get_asset(product_id, event)
                    assets.append((product_asset, product_address))


        recipient_account, recipient_address = self.get_account(recipient, event)
        old_owner_account, old_owner_address = self.get_account(event.signer_public_key, event)



        asset_objs = []

        for asset, asset_address in assets:
            if asset.asset_owner != event.signer_public_key:
                raise InvalidTransaction("Only the current owner can transfer the asset")
        
            asset.asset_owner = recipient
            asset.previous_owners.append(event.signer_public_key)
            asset.transfer_logistics.append(logistics["uid"])
            recipient_account.assets.append(asset.uid)
            old_owner_account.assets.remove(asset.uid)     

            if old_owner_account.account_type == AccountType.SUPPLIER and asset.asset_type == AssetType.RAW_MATERIAL:
                old_owner_account.raw_materials_supplied.append(asset.uid)

            asset.history.append(history)

            event.context.set_state({
                asset_address: self.serialize_for_state(asset)
            })
            asset_objs.append(asset)

        recipient_account.history.append(history)
        old_owner_account.history.append(history)

        event.add_data({
            "recipient": recipient_account,
            "old_owner": old_owner_account,
            "assets": asset_objs
        })

        event.context.set_state({
            recipient_address: self.serialize_for_state(recipient_account),
            old_owner_address: self.serialize_for_state(old_owner_account)
        })