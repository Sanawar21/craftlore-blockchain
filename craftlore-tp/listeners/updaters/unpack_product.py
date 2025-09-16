from .. import BaseListener, EventContext
from models.classes.assets import Product, Packaging
from models.enums import EventType

class UnpackProduct(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.PRODUCT_UNPACKED],
            priorities=[1000]
        )  # default priority

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})
        uid = fields.get("uid")
        assert uid is not None, "Product 'uid' must be provided."

        product, product_address = self.get_asset(uid, event)
        assert isinstance(product, Product), "Asset is not a product."
        assert product.asset_owner == event.signer_public_key, "Cannot unpack a product you do not own."
        assert not product.is_deleted, "Cannot unpack a deleted product."

        assert product.packaging is not None, "Product has no associated packaging to unpack."

        packaging, packaging_address = self.get_asset(product.packaging, event)
        assert isinstance(packaging, Packaging), "Associated packaging asset not found."
        assert packaging.is_deleted is False, "Cannot unpack from a deleted packaging."
        assert packaging.asset_owner == event.signer_public_key, "Cannot unpack from a packaging you do not own."

        # Unlink product from packaging
        product.packaging = None
        if product.uid in packaging.products:
            packaging.products.remove(product.uid)

        owner, owner_address = self.get_account(event.signer_public_key, event)
        assert owner.is_deleted is False, "Owner account is deleted."


        history_entry = {
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [product.uid, packaging.uid],
            "transaction": event.signature,
            "timestamp": event.timestamp
        }
        product.history.append(history_entry)
        packaging.history.append(history_entry)
        owner.history.append(history_entry)
        event.context.set_state({
            product_address: self.serialize_for_state(product),
            packaging_address: self.serialize_for_state(packaging),
            owner_address: self.serialize_for_state(owner)
        })
        event.add_data({"product": product, "packaging": packaging, "owner": owner})
        
