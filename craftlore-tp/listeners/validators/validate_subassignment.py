from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import SubAssignment
from models.enums import SubEventType


class ValidateSubAssignment(BaseListener):
    def __init__(self):
        super().__init__([SubEventType.SUB_ASSIGNMENT_CREATED], priorities=[-100])  # run after updating owner history

    def on_event(self, event: EventContext):
        assigner: ArtisanAccount = event.get_data("owner")
        assignment: SubAssignment = event.get_data("entity")

        if assignment.batch not in assigner.assets:
            raise InvalidTransaction("Artisan cannot assign sub-assignment for a batch they do not own")
        

        # if not creator:
        #     raise InvalidTransaction("Account data not found in event context for ValidateCreatorAccount")

        # if creator.account_type not in self.valid_creators:
        #     raise InvalidTransaction(f"Account type {creator.account_type} cannot create any assets")

        # if creator.is_deleted:
        #     raise InvalidTransaction("Deleted accounts cannot create assets")
        
        # if asset.asset_type not in self.valid_creators[creator.account_type]:
        #     raise InvalidTransaction(f"Account type {creator.account_type} cannot create asset type {asset.asset_type}")