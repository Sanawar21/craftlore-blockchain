from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import ProductBatch
from models.enums import EventType, BatchStatus

class ProducerUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.BATCH_COMPLETED],
            priorities=[1000]
        )  # default priority

    def on_event(self, event: EventContext):
            context = event.context
            payload = event.payload
            signer_public_key = event.signer_public_key

            fields = payload.get("fields")
            if not fields:
                raise InvalidTransaction("Missing 'fields' key in payload for ProducerUpdater")

            batch_id = fields.get("batch")
            if not batch_id:
                raise InvalidTransaction("Missing 'batch' in fields for ProducerUpdater")

            batch, batch_address = self.get_asset(batch_id, event)
            producer, producer_address = self.get_account(signer_public_key, event)        

            assert isinstance(batch, ProductBatch), "Asset must be a ProductBatch"
            assert isinstance(producer, ArtisanAccount), "Producer must be an ArtisanAccount"

            
            if batch.status != BatchStatus.IN_PROGRESS:
                raise InvalidTransaction(f"Batch status must be 'in_progress' to complete, current status: {batch.status}")
            

            history_entry = {
                "source": self.__class__.__name__,
                "event": event.event_type.value,
                "actor": event.signer_public_key,
                "targets": [batch.uid],
                "transaction": event.signature,
                "timestamp": event.timestamp
            }                
        
            batch.history.append(history_entry)
            producer.history.append(history_entry)

            context.set_state({
                batch_address: self.serialize_for_state(batch),
                producer_address: self.serialize_for_state(producer)
            })


            event.add_data({
                "entity": batch,
                "assignee": producer # Not really assignee but to keep consistent with other updaters
            })