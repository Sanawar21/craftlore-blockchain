from .. import BaseListener, EventType, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount


class EmailIndexUpdater(BaseListener):
    def __init__(self):
        super().__init__([EventType.ACCOUNT_CREATED], priorities=[-1000])  # run in the last

    def on_event(self, event: EventContext):
        account: BaseAccount = event.get_data("entity")

        if not account:
            raise InvalidTransaction("Account data not found in event context for EmailIndexUpdater")

        data = {
            "public_key": account.public_key,
            "email": account.email
        }

        address = self.address_generator.generate_email_index_address(account.email)
        
        if event.context.get_state([address]):
            raise InvalidTransaction(f"{account.email} is already taken")
        
        event.context.set_state({
            address: self.serialize_for_state(data)
        })
