from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import Packaging, Product
from models.enums import SubEventType

class PackageProducts(BaseListener):
    def __init__(self):
        super().__init__(
            [SubEventType.PACKAGING_CREATED],
            priorities=[0]
        )  # default priority

    def on_event(self, event: EventContext):
        packaging: Packaging = event.get_data("entity")
        owner: BaseAccount = event.get_data("owner")

        if not packaging:
            raise InvalidTransaction("Packaging entity not found in event data")
        if not owner:
            raise InvalidTransaction("Owner entity not found in event data")

        for product in packaging.products:
            product, product_address = self.get_asset(product, event)
            assert isinstance(product, Product), "Asset must be a Product"
            if product.is_deleted:
                raise InvalidTransaction(f"Cannot include deleted product {product.uid} in packaging")
            if product.packaging:
                raise InvalidTransaction(f"Product {product.uid} is already included in packaging {product.packaging}")
            if product.asset_owner != event.signer_public_key:
                raise InvalidTransaction(f"Product {product.uid} is owned by {product.asset_owner}, cannot be packaged by {owner.public_key}")

            product.packaging = packaging.uid

            product.history.append({
              "source": self.__class__.__name__,
              "event": event.event_type.value,
              "actor": event.signer_public_key,
              "targets": [product.uid, packaging.uid],
              "transaction": event.signature,
              "timestamp": event.timestamp
            })

            event.context.set_state({
                product_address: self.serialize_for_state(product)
            })
            

