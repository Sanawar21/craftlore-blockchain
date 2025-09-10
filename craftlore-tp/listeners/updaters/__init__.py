from .update_email_index import EmailIndexUpdater
from .update_owner_history import OwnerHistoryUpdater
from .update_entity_history import EntityHistoryUpdater
from .update_assignee import AssigneeUpdater
from .update_batch import BatchUpdater
from .package_products import PackageProducts
from .add_raw_material import AddToBatch

listeners = [
    EmailIndexUpdater,
    OwnerHistoryUpdater,
    EntityHistoryUpdater,
    AssigneeUpdater,
    BatchUpdater,
    PackageProducts,
    AddToBatch
]