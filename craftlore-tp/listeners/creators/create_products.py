from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount, BaseAccount
from models.classes.assets import WorkOrder, ProductBatch, Product
from models.enums import AccountType, SubEventType, EventType, WorkOrderStatus, BatchStatus, AssetType

class ProductsCreationHandler(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.WORK_ORDER_COMPLETED],
            priorities=[-200]
        )  # default priority

    def on_event(self, event: EventContext):
        batch: ProductBatch = event.get_data("batch")
        work_order: WorkOrder = event.get_data("entity")
        producer: BaseAccount = event.get_data("assignee")

        assert isinstance(batch.units_produced, int), "units_produced should be an integer in batch"

        products = []
        for i in range(1, batch.units_produced + 1):
            product_data = {
                "asset_owner": batch.producer,
                "uid": batch.uid + f"-{i}",
                "batch": batch.uid,
                "serial_no": i,
                "price_usd": work_order.total_price_usd / batch.units_produced,  # Default price, can be updated
                "quantity": batch.quantity / batch.units_produced,
                "unit": batch.unit,
                "created_timestamp": event.timestamp,
            }
            product = Product.model_validate(product_data)

            product.history.append({
                "source": self.__class__.__name__,
                "event": event.event_type.value,
                "actor": event.signer_public_key,
                "targets": [product.uid, batch.uid, work_order.uid],
                "transaction": event.signature,
                "timestamp": event.timestamp
            })

            product_address = self.address_generator.generate_asset_address(product.uid)
            
            if event.context.get_state([product_address]):
                raise InvalidTransaction(f"Product with UID {product.uid} already exists")

            event.context.set_state({
                product_address: self.serialize_for_state(product.model_dump())
            })

            products.append(product)
        
        producer.assets.extend([p.uid for p in products])
        producer.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [p.uid for p in products],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })
        producer_address = self.address_generator.generate_account_address(producer.public_key)

        event.context.set_state({
            producer_address: self.serialize_for_state(producer.model_dump())
        })
        event.add_data({
            "products": products
        })
